# Research Proposal: CodeSemEval — A Deep Semantic Evaluation Framework for Code LLMs

## Subproblem Choice

The query "deep evaluation framework for code LLMs" is broad. I narrow to one critical and under-explored subproblem: **evaluating whether code LLMs understand program semantics rather than merely synthesizing syntactically plausible code that passes weak functional tests.** This addresses the gap between pass@k scores and genuine reasoning about program behavior.

---

## 1. Title

**CodeSemEval: Measuring Semantic Grounding in Code Large Language Models**

---

## 2. Problem

### 2.1 The gap

Current code LLM evaluation relies almost exclusively on *functional correctness* benchmarks (HumanEval, MBPP, CodeContests, SWE-bench Verified). A model scores well if its generated code passes a held-out set of test cases. This conflates at least three distinct capabilities:

- **Memorization** — the model has seen the solution or a close variant in training.
- **Pattern matching** — the model produces code that *looks* like valid solutions without understanding its semantics.
- **Genuine semantic understanding** — the model can reason about what code does, why it works, and how it behaves under transformation.

**Evidence this is a real problem:** Prior work (Biderman et al., 2024; Golchin & Surdeanu, 2024) shows that LLMs score well on HumanEval even when the training data is contaminated with test-set solutions. Moreover, models perform poorly on semantic perturbation tasks — e.g., predicting output for a given input (Iv et al., 2023; Liu et al., 2024) — suggesting they lack robust execution models.

### 2.2 Problem statement

> Existing code LLM benchmarks evaluate *whether generated code passes tests* but not *whether the model understands what the code does*. This leaves a blind spot: a model could ace pass@k by memorizing solution patterns while being unable to reason about program behavior under novel transformations, identify subtle bugs, or verify semantic equivalence.

We need a framework that decomposes "code understanding" into specific, measurable semantic competencies and evaluates them independently of code generation ability.

---

## 3. Hypothesis

> **H1:** Code LLMs that achieve comparable pass@k on existing benchmarks exhibit significantly different performance on semantic reasoning tasks (output prediction, equivalence judgment, bug localization, invariant inference), revealing that pass@k is an insufficient proxy for semantic understanding.

> **H2:** Semantic reasoning performance correlates weakly (r < 0.4) with model size and stronger with training data composition (e.g., proportion of execution-traced examples), suggesting that current training pipelines do not efficiently induce semantic grounding.

> **H3:** A composite score across these semantic tasks predicts model performance on downstream trust-critical tasks (e.g., code review, automated repair, safety-constrained generation) better than pass@k alone (ΔR² > 0.15).

---

## 4. Method: CodeSemEval Framework

The framework comprises five evaluation axes, each implemented as a separate task with automatically verifiable ground truth. All tasks are *execution-based* — answers are derived by running code, not by LLM-as-judge — ensuring objective, reproducible scoring.

### Axis 1: Execution Prediction (EP)

Given a snippet `S` and an input `I`, predict the output `O = execute(S, I)`.

- **Formulation:** Multi-choice (5 options, one correct, 4 plausible distractors derived from common execution errors + one adversarial from a different valid execution path).
- **Why it tests semantic grounding:** Requires the model to simulate the program's state transformations step by step. Distractors test for off-by-one, early return misinterpretation, mutability errors, and scope confusion.
- **Difficulty levels:** Single-function (easy), nested calls with non-trivial data structures (medium), recursive/iterative with side effects (hard).

### Axis 2: Semantic Equivalence (SE)

Given two programs `P` and `Q`, determine whether they are functionally identical under all deterministic inputs.

- **Formulation:** Binary classification (equivalent / not equivalent) for pairs of programs from an oracle-generated pool.
- **Data generation:** Take a reference program, generate semantically equivalent variants (loop unrolling, tail-recursion conversion, map vs. explicit loop, expression rewriting) using verified rewrite rules. Generate non-equivalent variants by introducing subtle mutations (off-by-one, swapped conditionals, wrong operator) that are *not* detectable by simple syntax comparison.
- **Key design:** Equivalent pairs share no tokens verbatim >60% of the time (controlled), forcing semantic rather than surface-form reasoning.

### Axis 3: Bug Localization & Categorization (BL)

Given a program `P` that fails a provided test `T`, identify the line(s) containing the bug and the error type (off-by-one, null/undefined access, logic inversion, type confusion, resource leak).

- **Formulation:** Multi-label classification over line numbers + error categories. Partial credit via token-level F1.
- **Why it tests semantic grounding:** Requires the model to align the **execution trace** of `P` with its mental model of the intended behavior, then isolate the discrepancy.
- **Data:** Borrow from Defects4J (Java), CodeFlaws (C/C++), and introduce systematically seeded bugs into the CodeSemEval program pool (one mutation per program, with verified failing tests).

### Axis 4: Invariant Inference (II)

Given a program `P`, identify a likely loop invariant or postcondition that holds at a specified program point.

- **Formulation:** Free-form natural language or formal (e.g., assertions in Python `assert` syntax). Evaluation via automatic assertion checking: generate the assertion, insert it, and run all test cases. If no test fails, the invariant is valid.
- **Difficulty levels:** Simple arithmetic invariants (easy), data structure invariants (sortedness, distinctness — medium), relational invariants across multiple variables with non-linear constraints (hard).

### Axis 5: Transformation Verification (TV)

Given a program `P` and a transformation description `T` (e.g., "refactor this loop into a recursive function"), verify whether a candidate output `P'` is a correct implementation of `T`.

- **Formulation:** Binary yes/no (is the transformation correct?) with optional free-text explanation. Ground truth established by formal equivalence checking or exhaustive testing on bounded inputs.
- **Why it tests semantic grounding:** Requires compositional reasoning — the model must understand both the source semantics and the transformation's intent.

### Pipeline for construction

```
Source program pool (10,000 curated Python + Java programs)
    │
    ├─→ [Exec. traces] → Axis 1: Execution Prediction items
    ├─→ [Verified rewrites + mutations] → Axis 2: Semantic Equivalence items
    ├─→ [Seed & verify bugs] → Axis 3: Bug Localization items
    ├─→ [Daikon + manual verification] → Axis 4: Invariant Inference items
    └─→ [Paired transformations] → Axis 5: Transformation Verification items
```

All items go through a validation stage: 3 human annotators (per item) confirm the ground truth is correct. Minimum inter-annotator agreement of Fleiss' κ > 0.8 for an item to be retained.

---

## 5. Dataset / Benchmark

### Source programs
- **Python:** 6,000 programs drawn from CodeNet (Project Euler subset), AtCoder, and the MBPP training set. Filter to exclude programs that appear in the test splits of popular benchmarks (contamination control).
- **Java:** 4,000 programs drawn from CodeNet and Defects4J.
- **Length distribution:** 8–80 lines (median 20), 1–3 functions.

### Derived items

| Axis | Task | Items | Languages |
|------|------|-------|-----------|
| EP | Execution Prediction | 3,000 | Python, Java |
| SE | Semantic Equivalence | 2,000 pairs | Python, Java |
| BL | Bug Localization | 2,000 | Python, Java |
| II | Invariant Inference | 500 | Python only |
| TV | Transformation Verification | 500 | Python only |
| **Total** | | **8,000** | |

### Contamination control
- Exact and near-exact n-gram matching (Jaccard > 0.8) against HumanEval, MBPP, APPS, CodeContests, SWE-bench. Flagged items are removed or rewritten.
- All items released with a **canonical form** (normalized variable names, formatting) and a **contamination test script**.
- For every model evaluated, report the per-item containment score as a covariate in results.

### Public release
- MIT license. HuggingFace Datasets + GitHub. Includes: item data, grading scripts, leaderboard, and contamination check tools.

---

## 6. Evaluation Metrics

### Per-axis metrics
- **EP:** Accuracy@1, Accuracy@5 (correct answer in top 5 log-prob tokens), and Expected Calibration Error (ECE) over confidence.
- **SE:** Accuracy, precision, recall, F1. Also report *symmetric accuracy* — accuracy on equivalent + non-equivalent pairs separately.
- **BL:** Token-level F1 (bug line identification), macro-F1 over error categories. Report precision at rank 1, 3, 5.
- **II:** Acceptance rate (assertions that pass all tests), mean number of redundant assertions (indicating specificity).
- **TV:** Accuracy, F1. For free-text explanations: BERTScore between model explanation and gold explanation (annotated subset of 200 items).

### Composite score: CodeSem Score
Weighted average across axes:
```
CodeSem Score = 0.25·EP_acc + 0.25·SE_F1 + 0.20·BL_F1 + 0.15·II_acc + 0.15·TV_acc
```
Weights are justified by a factor analysis on a pilot study (N=100 items, 5 models) — each axis contributes significant unique variance.

### Reporting standards
- All metrics with 95% bootstrap confidence intervals (1,000 resamples).
- Per-model contamination-adjusted scores (logistic regression residual after controlling for item-level containment).
- Statistical significance testing: McNemar's test for per-item comparisons between models.
- Multiple-testing correction: Benjamini-Hochberg across all model comparisons.

---

## 7. Baselines

### Model families (6+ models to ensure coverage)
| Model | Size | Access | Rationale |
|-------|------|--------|-----------|
| GPT-4o | API | Proprietary SOTA | Upper bound reference |
| Claude 3.5 Sonnet | API | Proprietary SOTA | Upper bound reference |
| DeepSeek-Coder-V2 | Open 236B | Open weights | Best open model |
| CodeLlama-34B | Open 34B | Open weights | Representative mid-size |
| DeepSeek-Coder-6.7B | Open 6.7B | Open weights | Representative small |
| StarCoder2-15B | Open 15B | Open weights | Another mid-size |
| GPT-3.5 (legacy) | API | Prior-gen SOTA | Ablation of scale alone |

### Comparison baselines
- **Random performance** on each axis (chance level, empirically estimated by random-sampled answers).
- **N-gram pattern matcher** (max Jaccard similarity to training set) — to quantify surface-form shortcut ceiling.
- **Human performance** (3 CS graduate students per axis, 200 items each) — to calibrate human-level semantic understanding.

### Key comparison
For each model, compute: (a) pass@k on HumanEval+ and (b) CodeSem Score. Report the rank correlation (Spearman's ρ) and pairwise comparisons. If two models have indistinguishable pass@k but significantly different CodeSem Scores, the hypothesis is supported.

---

## 8. Ablations

### A1: Contamination sensitivity
Evaluate all models on the full CodeSemEval set vs. the contamination-filtered subset. If scores drop significantly on the filtered set for closed models, this quantifies memorization reliance.

### A2: Prompt format
Test three prompt formats for each axis:
- **Direct** (no few-shot)
- **Few-shot** (3 exemplars, same axis, different programs)
- **Chain-of-thought** ("Let's think step by step" + execution trace logging)

Report whether CoT narrows the gap between open and closed models.

### A3: Language transfer
Evaluate Python-trained models on Java items and vice versa (for axes 1, 2, 3 that have both languages). If the gap is large (>20% accuracy difference), it suggests the model learned language-specific surface patterns rather than language-agnostic semantic reasoning.

### A4: Axis-wise information gain
Compute the incremental R² of adding each axis to a logistic regression predicting human-judged "code understanding quality" (5-point Likert) on a held-out set of 500 programs. This tests whether the axes measure different facets.

### A5: Pass@k vs. CodeSem Score as predictors
On a held-out set of 50 GitHub pull requests (known to contain bugs), compare how well pass@k vs. CodeSem Score predicts whether a model can correctly identify the bug (binary outcome). Use logistic regression and report ΔAIC and ΔAUC.

---

## 9. Expected Failure Modes and Mitigations

| Failure mode | Risk | Mitigation |
|-------------|------|------------|
| **Iteration-to-death on item construction** the benchmark is too hard to build at scale | Medium | Start with a 500-item pilot (100 per axis). Validate item quality and inter-annotator agreement before scaling. Use program synthesis + verification to generate SE and TV items automatically. |
| **Contamination from pretraining data** models have seen CodeNet/AtCoder solutions | High | Aggressive n-gram deduplication. Release a contamination test script. Report adjusted scores. If contamination is pervasive, construct a synthetic program generator (grammar + random semantics). |
| **Ceiling effects** GPT-4o/Claude score >90% on all axes | Low-Medium | If ceiling is observed, introduce adversarial item construction (e.g., obfuscated control flow, recursive reasoning depth). Design items to be hard for humans too (target human accuracy: 75–85%). |
| **Floor effects** all open models score near chance | Medium | If floor is observed on specific axes (e.g., II, TV), simplify those items first. The goal is discriminative power, not difficulty per se. |
| **LLM-judge contamination** if models are evaluated on their own generated content | Low | All ground truth is execution-verified or human-annotated. No LLM-as-judge in the evaluation loop. |
| **Overfitting to the benchmark** once released, the benchmark becomes a fine-tuning target | Medium | Keep a held-out secret test set (20% of items). Rotate items every 12 months. Design a program generator so new items can be minted perpetually. |
| **Human annotation quality** low inter-annotator agreement on II and SE items | Medium | Train annotators with a calibration phase (50 practice items with gold answers). Use software engineering PhD students, not crowdworkers. Pay for quality. |

---

## 10. Short Execution Plan

**Phase 0 — Infrastructure (Weeks 1–2)**
- Set up program pool (filter CodeNet, AtCoder, MBPP train).
- Build execution sandbox (Docker, time-bounded, crash-safe).
- Write the contamination checker (n-gram + MinHash dedup).
- Deliverable: Program pool (10k programs) + execution infrastructure.

**Phase 1 — Pilot (Weeks 3–5)**
- Generate 500 pilot items (100 per axis).
- Hire 3 annotators; run calibration and annotation for pilot items.
- Compute Fleiss' κ; revise item templates with poor agreement.
- Run 3 baseline models (GPT-4o, CodeLlama-34B, DeepSeek-Coder-6.7B) on the pilot.
- Compute factor analysis to validate axis weights.
- Deliverable: Pilot results + revised item templates. Decision: proceed to full scale if CodeSem Score separates models by >2σ.

**Phase 2 — Full benchmark construction (Weeks 6–10)**
- Scale item generation to 8,000 items.
- Full annotation pass (3 annotators per item).
- Contamination filtering.
- Deliverable: Full CodeSemEval dataset (v1.0) on HuggingFace Datasets.

**Phase 3 — Full evaluation (Weeks 11–13)**
- Run all 7 baseline models on all 8,000 items.
- Run 5 random seeds per model for EP axis (where randomness matters).
- Run human baseline (3 graduate students, 200 items per axis).
- Deliverable: Full results table with confidence intervals.

**Phase 4 — Analysis and ablations (Weeks 14–16)**
- Run ablations A1–A5.
- Compute correlation analysis (pass@k vs. CodeSem Score).
- Write up failure cases and qualitative analysis (50 misclassified items analyzed by axis).
- Deliverable: Analysis notebooks + all figures.

**Phase 5 — Paper writing and release (Weeks 17–18)**
- Write paper (target: NeurIPS or ICLR datasets & benchmarks track).
- Release: dataset, code, leaderboard, contamination checker, and model outputs.
- Deliverable: Paper draft + public release.

### Total timeline: 18 weeks for one PhD student + one research engineer.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 23 |
| Topic | Code LLM evaluation |
| Original user goal | Generate a research proposal on how to build a deep evaluation framework for code LLMs. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_23/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_23/final_report.md` (16680 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_23/prompt.txt` (691 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_23/query.json` (149 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_23/stdout.txt` (8998 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_23/stderr.txt` (251 bytes)

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
