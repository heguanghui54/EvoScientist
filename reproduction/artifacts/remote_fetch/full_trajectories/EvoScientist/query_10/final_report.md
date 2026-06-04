# Research Proposal: Semantically Decomposed Text-to-SQL with Skeleton-Based Compositional Generalization

---

## 1. Title

**Schema-Aware Skeleton Decomposition with Constraint-Guided Slot Filling for Compositional Text-to-SQL**

---

## 2. Problem Statement

Current LLM-based Text-to-SQL systems achieve ~86-88% execution accuracy on standard benchmarks like Spider. However, this masks a critical weakness: **compositional generalization**. When a natural language question requires combining multiple known SQL operations — e.g., a nested subquery inside a `UNION` with a `GROUP BY` and `HAVING` clause — performance drops sharply. In-distribution accuracy on Spider's easy questions exceeds 90%, but on hard and extra-hard questions requiring complex compositional structure, it falls below 65% (DIN-SQL, 2024). On adversarial evaluations like Spider-Syn (with paraphrased schema) and Spider-Realistic, SOTA methods drop by 8-15 points.

**Why this matters**: Real-world text-to-SQL applications require users to ask arbitrarily complex questions. A system that handles simple queries but fails on multi-constraint compositional ones is not deployable.

**Root cause identified**: Current methods treat Text-to-SQL as an end-to-end generation problem, conflating two fundamentally different cognitive sub-tasks:

1. **Structural reasoning**: Deciding the SQL skeleton — which operators (`SELECT`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`), set operations (`UNION`, `INTERSECT`, `EXCEPT`), join topology, and nesting structure are needed.
2. **Schema grounding**: Mapping natural language spans to specific schema elements (tables, columns, data types) and literal values.

When these are coupled in a single autoregressive pass, errors in structural planning cascade into schema grounding and vice versa. Small earlier errors (e.g., predicting an unnecessary `JOIN`) corrupt the entire subsequent generation.

---

## 3. Hypothesis

**Central hypothesis**: Decoupling Text-to-SQL into (a) skeleton prediction, (b) schema-aware slot filling, and (c) symbolic constraint verification significantly improves compositional generalization compared to end-to-end generation, particularly on queries requiring multiple nested operations and complex join topologies.

**Sub-hypotheses**:

1. **H1 (Skeleton Transferability)**: SQL skeletons (abstract structures stripped of schema identifiers) transfer across domains more effectively than full SQL, because structural patterns (e.g., "find the maximum X grouped by Y") are domain-independent.

2. **H2 (Slot Filling Simplicity)**: Schema-aware slot filling from a correctly predicted skeleton is a simpler learning problem than full SQL generation, resulting in higher accuracy for the same model capacity.

3. **H3 (Verifier Effectiveness)**: A lightweight symbolic constraint verifier (operating on schema metadata without requiring database execution) can detect and repair 70%+ of slot-filling errors, providing a correctness guarantee that end-to-end methods lack.

---

## 4. Method

We propose a **three-stage Text-to-SQL pipeline**:

### Stage A: Skeleton Prediction

**Input**: Natural language question + condensed schema (table and column names with types, foreign key relationships).

**Output**: A SQL *skeleton* — the structural query with schema-specific identifiers replaced by typed placeholders.

*Structure placeholders*:
- `{TABLE: <domain-hint>}` — a table reference
- `{COLUMN: <domain-hint> <type>}` — a column reference with data type
- `{VALUE: <type> <entity-hint>}` — a literal value
- `{AGG: <operation>}` — aggregation function (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`)
- `{COND_OP: <logical>}` — comparison operator (`=`, `>`, `<`, `LIKE`, `IN`, etc.)
- `{SUBQUERY: <skeleton>}` — a nested subquery skeleton

**Example**:

> *Question*: "Find departments where the average salary is greater than the company-wide average salary."

> *Skeleton*:
> ```sql
> SELECT {COLUMN: department name}
> FROM {TABLE: employees}
> JOIN {TABLE: departments} ON {COLUMN: dept_id = dept_id}
> GROUP BY {COLUMN: department name}
> HAVING {AGG: AVG}({COLUMN: salary integer}) > (
>   SELECT {AGG: AVG}({COLUMN: salary integer})
>   FROM {TABLE: employees}
> )
> ```

**Implementation**: We fine-tune a CodeLlama-7B model on Spider/Bird training data with a custom skeletonization procedure:
1. Parse each gold SQL into an AST
2. Replace leaf schema elements with typed placeholders
3. Keep SQL keywords, operators, and structural tokens intact
4. Train with standard cross-entropy loss on skeleton sequences

The same model can also be used in few-shot mode for GPT-4/Claude as an alternative instantiation.

### Stage B: Schema-Aware Slot Filling

**Input**: Skeleton + full database schema (all tables, columns, types, primary/foreign keys, indexes, sample values).

**Output**: A complete SQL query with all placeholders resolved to concrete schema elements and literal values.

**Slot filling strategy**: For each placeholder, we use a **hybrid linking module**:

1. **Embedding-based retrieval**: Compute cosine similarity between the placeholder's domain hint (and surrounding NL context) vs. each candidate column's name, comments, and sample values using a cross-lingual sentence encoder (LaBSE or sentence-T5).

2. **Graph-based propagation**: Use the schema's foreign-key graph to propagate relevance scores. If a column is relevant, its connected columns (via FK relationships) get a bonus, since joins often co-occur.

3. **Type constraint filtering**: Filter candidates to match the placeholder's declared type (integer, text, date, boolean).

4. **LLM-based disambiguation**: For ambiguous slots (top-3 candidates have confidence within 0.1), query a small LLM (e.g., Llama-3-8B) with the question + skeleton + candidates to make a final selection.

5. **Value extraction**: For `{VALUE}` placeholders, use a span extraction model (fine-tuned BERT) conditioned on the question and the target column's type.

### Stage C: Symbolic Constraint Verifier

**Input**: Completed SQL query + database schema metadata.

**Output**: A set of constraint violations (if any) + a repaired SQL query or a re-ranking among top-k candidates.

**Verification rules** (no database execution required):

| Rule | Check | Repair Action |
|------|-------|---------------|
| R1: Column-Table Membership | Every column in SELECT/WHERE/GROUP BY/ORDER BY/Having/JOIN belongs to a table in FROM/JOIN | Add missing table or correct column reference |
| R2: Column-Table Consistency | Columns in the same SELECT clause that come from different tables must have a join path | Add missing JOIN or correct table alias |
| R3: Type Compatibility | WHERE/HAVING comparison operators match column types (e.g., `>` not on text) | Replace operator or suggest correct column |
| R4: Aggregation Consistency | GROUP BY columns must appear in SELECT unless aggregated | Add aggregation or add to GROUP BY |
| R5: FK-Join Validity | JOIN conditions should reference valid foreign-key relationships | Correct join column references |
| R6: Schema Completeness | All tables in FROM clause are correct for the question | Flag potentially missing/extra tables |

**Repair mechanism**: For each violation, the verifier proposes a minimal repair (e.g., adding a missing table to FROM, swapping a column reference). If multiple violations exist, it selects the repair with the highest total confidence across slot-filling scores. If the repair confidence falls below a threshold, the system returns the top-k candidate SQLs for manual review or execution-guided re-ranking.

**Training data for verifier**: Automatically generated by taking gold SQL queries, introducing targeted corruptions (swap column, drop table, change operator), and labeling violations. We generate ~50K synthetic examples from Spider/Bird training schemas.

---

## 5. Dataset & Benchmark

| Dataset | Domain(s) | # Examples | Use | Compositional Complexity |
|---------|-----------|------------|-----|-------------------------|
| **Spider** (Yu et al., 2018) | 200 databases, 138 domains | 8,659 training / 1,034 dev / 2,147 test | Primary training + in-distribution eval | 4 difficulty levels (easy/medium/hard/extra-hard) |
| **Spider-Syn** (Gan et al., 2021) | Same as Spider | 1,034 | **Adversarial generalization**: schema synonyms | Same structure as Spider, harder linking |
| **Spider-Realistic** (Deng et al., 2021) | Same as Spider | 508 | **Adversarial generalization**: removed explicit schema mentions | Same structure, harder NL ambiguity |
| **Dr.Spider** (Chang et al., 2023) | Perturbed Spider schemas | 15K | **Robustness**: schema perturbations | Systematic perturbations |
| **BIRD** (Li et al., 2024) | 95 databases, 37 domains | 12,751 training / 1,534 dev / 1,714 test | **Real-world**: larger, more values, dirty data | Higher value extraction demands |
| **SParC** (Yu et al., 2019) | Same as Spider (cross-domain conversational) | 4,298 sessions | **Compositional**: multi-turn context builds complexity | Incremental compositionality |
| **CSpider** (Min et al., 2019) | Chinese Spider | 8,659 | **Cross-lingual generalization** | Same structure, different language |

**Custom: Compositional Stress Test Set**. We construct a small diagnostic set (200 examples) specifically targeting known compositional failure modes:
- Queries requiring ≥3 nested subqueries
- Queries combining 2+ set operations (UNION + EXCEPT)
- Queries with aggregation chains (nested aggregations)
- Queries requiring implicit join paths (3+ FK hops)
- Queries with ambiguous group-by targets

This set is derived by filtering and augmenting existing datasets and will be released with the paper.

---

## 6. Evaluation Metrics

| Metric | Definition | Primary/Secondary |
|--------|-----------|------------------|
| **Exact Set Match (EM)** | Exact SQL structure match (ignoring alias differences) | Primary |
| **Execution Accuracy (EX)** | SQL execution produces identical result set as gold | Primary |
| **Test Suite Accuracy (TS)** | Multi-database test suite execution match (Zhong et al., 2020) | Primary |
| **Breakdown by Difficulty** | EM/EX/TS per Spider difficulty level | Secondary |
| **Compositional Accuracy** | EM/EX on our compositional stress test set | Secondary |
| **Schema Linking F1** | Precision/recall of table and column selection | Diagnostic |
| **Skeleton Accuracy** | EM of predicted vs. gold skeleton (ignoring slot values) | Diagnostic |
| **Slot Filling Accuracy** | % of correctly filled placeholders (given gold skeleton) | Diagnostic |
| **Verifier Precision/Recall** | Correctly identified/repaired constraint violations | Diagnostic |

All metrics reported with **95% confidence intervals** across 3 random seeds.

---

## 7. Baselines

We compare against the following systems, spanning the major methodological families:

| Baseline | Method Family | Key Reference |
|----------|--------------|---------------|
| **GPT-4 + DAIL-SQL** | Few-shot prompting with demonstration retrieval + schema linking | Gao et al., 2024 |
| **CodeLlama-13B-SQL** | Fine-tuned LLM (end-to-end) | CodeS (Li et al., 2024) |
| **DIN-SQL** | Decomposition into sub-questions + schema linking | Pourreza & Rafiei, 2024 |
| **MAC-SQL** | Multi-agent collaboration (selector, decomposer, verifier) | Hong et al., 2024 |
| **RESDSQL** | Ranking-based decoding + skeleton-aware ranking | Li et al., 2024 |
| **TAE-BERT + RoBERTa** | Pre-trained encoder with schema linking | Semantic parsing baselines |
| **Our System (A-only)** | Skeleton prediction only → then gold skeleton → slot filling | Ablation to measure skeleton quality |
| **Our System (A+B)** | Skeleton + slot filling, no verifier | Ablation to measure verifier contribution |
| **Our System (A+B+C, full)** | Full pipeline | Proposed method |

---

## 8. Ablations

| Ablation | Variant | Question Answered |
|----------|---------|-------------------|
| **A1: Skeleton granularity** | Fine-grained vs. coarse-grained placeholders | How much structure must the skeleton encode? |
| **A2: Slot filling method** | Embedding-only vs. graph-only vs. hybrid | Which linking strategy is most effective? |
| **A3: Verifier ablation** | Full pipeline (A+B+C) vs. (A+B) no verifier | Does the verifier add significant value? |
| **A4: Execution vs. symbolic verifier** | Our symbolic verifier vs. execution-guided decoding | Can symbolic verification substitute for execution? |
| **A5: Backbone model** | CodeLlama-7B vs. CodeLlama-13B vs. GPT-4 (few-shot) | How does skeleton prediction scale with model size? |
| **A6: Training data size** | 25%/50%/75%/100% of Spider training | How much data is needed for skeleton prediction? |
| **A7: Cross-domain transfer** | Train on Spider, test on BIRD directly (no fine-tuning) | Does the skeleton approach generalize out-of-the-box? |

---

## 9. Expected Failure Modes

1. **Skeleton under-specification**: If the skeleton is too coarse (e.g., one placeholder for an entire WHERE clause), the slot filler must reconstruct complex structure, collapsing the benefit of decomposition. **Mitigation**: Use fine-grained AST-based skeletonization with explicit placeholders for each structural component.

2. **Compound slot ambiguity**: When a single placeholder could map to multiple plausible schema elements (e.g., "salary" could reference `employees.salary` or `salaries.base_salary`), the slot filler may select incorrectly. **Mitigation**: Include FK-graph context and sample values; if confidence is low, enumerate top-k and let the verifier pick.

3. **Verifier false positives**: A valid SQL query may violate a rule due to schema nuance (e.g., a non-FK join is valid but not captured in the schema metadata). **Mitigation**: Flag but don't reject; allow confidence-based override with lower threshold for warnings vs. actual rejections.

4. **Value extraction fragility**: Extracting literal values (dates, names, numbers) from NL remains hard. **Mitigation**: Use a dedicated span extraction model and fall back to LIKE pattern matching for partial matches.

5. **Error cascades**: An error in Stage A (skeleton) cannot be recovered by Stages B or C — the skeleton must be correct. **Mitigation**: Generate top-3 skeletons and run the full pipeline on each, selecting the final output by verifier score.

6. **OOD SQL patterns**: Rare SQL constructs not seen in training (e.g., window functions, recursive CTEs) won't appear in skeletons. **Mitigation**: Release as a known limitation; window functions can be added in future work.

7. **Computational overhead**: Three-stage pipeline increases latency vs. single-pass generation. **Mitigation**: Design for parallel slot filling (independent placeholders filled concurrently); target <2× end-to-end overhead vs. GPT-4 single-pass.

---

## 10. Execution Plan

| Phase | Duration | Activities | Deliverables |
|-------|----------|-----------|-------------|
| **Phase 1: Data Preparation** | Weeks 1-2 | Install Spider/BIRD/SParC; build skeletonization script (AST parser + placeholder replacement); generate training skeletons; construct compositional stress test set; generate 50K verifier training examples | Skeletonization script, stress test set, verifier training data |
| **Phase 2: Stage A — Skeleton Model** | Weeks 3-4 | Fine-tune CodeLlama-7B on skeleton prediction; evaluate on gold skeleton accuracy; train on 25/50/75/100% data splits; test GPT-4 few-shot skeleton prediction | Trained skeleton model, skeleton accuracy baselines |
| **Phase 3: Stage B — Slot Filling** | Weeks 5-6 | Implement hybrid linking module (embedding + graph + type filtering); implement LLM disambiguation; implement value extraction (BERT span model); evaluate slot filling accuracy given gold skeletons vs. predicted skeletons | Slot filling module, per-slot accuracy metrics |
| **Phase 4: Stage C — Verifier** | Week 7 | Implement 6 verification rules; build repair mechanism; train/evaluate on synthetic corruption data; compare against execution-guided decoding | Verifier module, precision/recall statistics |
| **Phase 5: Full Pipeline Evaluation** | Weeks 8-9 | Run full pipeline on Spider dev + test, Spider-Syn, Spider-Realistic, BIRD dev, Sparch; run all 7 ablations; compute all metrics with confidence intervals | Full results table, ablation results |
| **Phase 6: Analysis & Paper** | Weeks 10-11 | Error analysis on compositional stress test set; analyze failure patterns; write up (method, experiments, analysis, related work) | Paper manuscript, error analysis |
| **Phase 7: Release** | Week 12 | Code release (model + scripts), data release (stress test set), model weights | GitHub repo, HuggingFace model, stress test dataset |

**Resource requirements**:
- 1× A100-80GB GPU for CodeLlama fine-tuning (or 4× A10G)
- ~2-3 GPU-days total across all phases
- Storage: ~50GB for datasets, ~30GB for checkpoints

---

## 11. Related Work (Condensed)

- **End-to-end LLM Text-to-SQL**: DAIL-SQL (Gao et al., 2024), CodeS (Li et al., 2024), SQL-PaLM (Sun et al., 2023), SFT CodeLlama (Pourreza et al., 2024)
- **Decomposition approaches**: DIN-SQL (Pourreza & Rafiei, 2024), MAC-SQL (Hong et al., 2024), C3 (Dong et al., 2023)
- **Schema linking**: Graph-based (Wang et al., 2020), embedding-based (Guo et al., 2019), hybrid (Qi et al., 2022), NL-augmented (Deng et al., 2021)
- **Execution-guided decoding**: SQLNet (Xu et al., 2017), IRNet (Guo et al., 2019), RAT-SQL + execution-guided (Wang et al., 2020)
- **Compositional generalization in semantic parsing**: COGS (Kim & Linzen, 2020), CFQ (Keysers et al., 2020), Compositional splits of Spider (Finegan-Dollak et al., 2018)
- **Constraint-based verification**: TreeSQL (Sun et al., 2018), grammar-based decoding (Yin & Neubig, 2017), PICARD (Scholak et al., 2021)

**Novelty**: To our knowledge, no prior work combines (a) explicit typed ASTM-level skeleton decomposition, (b) hybrid schema grounding with FK-graph propagation, and (c) symbolic constraint verification (without execution) into a single pipeline. Most decomposition methods (DIN-SQL, MAC-SQL) decompose the *question* into sub-questions, not the *SQL structure* into skeleton + slots. The symbolic verifier without execution is particularly novel — it provides correctness guarantees without needing a running database, making it deployable in read-only or security-restricted environments.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 10 |
| Topic | Text-to-SQL |
| Original user goal | Help me generate a research proposal on Text-to-SQL. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_10/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_10/final_report.md` (18447 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_10/prompt.txt` (656 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_10/query.json` (106 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_10/stdout.txt` (8746 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_10/stderr.txt` (251 bytes)

The browsable HTML preview for this report is generated from the Markdown source by `reproduction/build_all_paper_previews.py`. The all-report index is `reproduction/artifacts/paper_previews/all_evoscientist_reports/index.html`.

### C. Evaluation Protocol Used in This Reproduction

The local reproduction package evaluates the EvoScientist public final reports against replacement or proxy baseline outputs where direct paper-exact baseline outputs were not publicly available. The user-scoped Table 1 replacement uses 30 queries, 7 baseline systems, and 2 swapped comparison orders, yielding 420 Monica/Gemini judge records. The judged dimensions are Clarity, Novelty, Feasibility, and Relevance.

For the Table 2 style check, this reproduction uses Monica/Gemini surrogate labels over 120 inputs and 1,440 dimension-level labels. Formal PhD human labels were intentionally left outside the current user scope. The resulting evidence should therefore be read as a reproduction-oriented proxy, not as a paper-exact human evaluation.

### D. Limits and Non-Claims

- This appendix is local documentation for reproducibility; it is not a new EvoScientist generation step.
- The pass does not add new experimental evidence beyond artifacts already present in the reproduction directory.
- Paper-exact reproduction remains blocked by missing author-side raw baseline outputs, original Gemini judge transcripts, and formal human-label artifacts.
- Claims in the main generated proposal remain those of the generated report; this appendix only records how the local reproduction package stores and evaluates it.

### E. Verification Commands

```bash
.venv/bin/python reproduction/verify_user_scope_reproduction.py --strict
.venv/bin/python reproduction/verify_reproduction_assets.py
bash reproduction/run_preflight.sh
```
