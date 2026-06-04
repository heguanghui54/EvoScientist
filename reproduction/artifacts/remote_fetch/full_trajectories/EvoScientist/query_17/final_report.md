# Schema-Constrained Document-Level Event Extraction via Context-Grounded LLM Decoding

## 1. Problem

**Automated information extraction** (IE) aims to transform unstructured text into structured representations. Within IE, **event extraction** — identifying occurrences of typed events and mapping each event to its participants (agent, object, time, location, etc.) — is a core task with applications in news monitoring, biomedical literature mining, financial analysis, and intelligence.

The problem currently has three unresolved challenges that this proposal targets directly:

1. **Document-level scope.** Most event extraction research operates at the sentence level, yet real events naturally span multiple sentences: an attack is described across several paragraphs, a clinical outcome is scattered across a discharge summary, and a corporate acquisition is reported across a news article. Sentence-level methods fail to capture long-range entity-role dependencies.

2. **Structural faithfulness.** Large language models (LLMs) achieve strong results on IE when prompted in zero/few-shot settings, but they are prone to hallucination — extracting events or arguments that are fluent but not present in the source text. In safety-critical domains (clinical, legal, financial), unfaithful extractions are more harmful than missed extractions.

3. **Schema generalization.** Existing methods require either expensive annotation for each new event schema or brittle prompt engineering. A method that generalizes to arbitrary schemas without task-specific training is needed for practical deployment.

**Concrete scenario:** Given a news article describing a "vehicle crash" event, the system must identify the crash trigger (e.g., "collided"), the vehicles involved, casualties, location, date, and cause — even when these arguments are spread across 3–5 sentences and the event schema is provided at inference time as a structured specification.

---

## 2. Hypothesis

**Central hypothesis:** Constraining the decoding of a frozen LLM with a type-aware, context-grounded automaton — derived from both the provided event schema and the source document — will significantly improve extraction faithfulness and F1 for document-level event extraction across novel schemas, compared to unconstrained prompting, fine-tuned seq2seq baselines, and post-hoc verification approaches.

**Sub-hypotheses:**
- **H1:** Schema-informed hard constraints (e.g., "location must be a span in the document, not a generated phrase") reduce argument hallucination by ≥40% relative.
- **H2:** Document-level cross-sentence argument aggregation via a lightweight span-graph interaction layer outperforms sentence-level greedy extraction when events span >2 sentences.
- **H3:** A schema-conditioned prefix that enumerates roles and type constraints in a structured grammar improves zero-shot transfer to unseen schemas by ≥15% F1 over natural-language prompting.

---

## 3. Method: Constrained Schema Extraction (CSE)

The proposed system has three components:

### 3.1 Schema-Aware Constrained Decoding Grammars

Given an event schema S containing event types E and, for each event type e, a set of role types R_e with their expected entity types (e.g., "agent: PERSON", "target: ORGANIZATION", "place: LOCATION"), we compile S into a formal grammar G_S.

The grammar is a **token-level deterministic finite automaton** (DFA) built on the LLM's vocabulary, where:
- At each decoding step, only tokens that lead to a valid (syntactically correct, schema-conforming) completion are allowed.
- Role slots are typed: if role `place` expects a LOCATION entity, the grammar enforces that the generated token sequence for that slot corresponds to a document span (tokens drawn from the source document via a pointer mechanism) rather than freely generated text.
- The grammar is constructed once per schema at inference time (no training) and is agnostic to the source document content.

### 3.2 Context-Grounded Span Pointer

To prevent hallucination of entity names not present in the source document, the decoder does not generate entity names from its vocabulary freely. Instead, we modify the LLM's output layer to support **span pointer copying** from the source document:

- The source document D is encoded once.
- For each role slot, the decoder selects a span from D via a learned linear projection over the document encoder's hidden states (a small, trainable pointing head with <5M parameters). The LLM's own hidden states at the slot-filling position condition the pointing distribution.
- The role-filling text is forced to be a contiguous span from D, eliminating the possibility of generating names, dates, or locations that do not appear in the source.

This pointer mechanism is the **only trainable component** of the system beyond the frozen LLM. The LLM's weights are never updated.

### 3.3 Cross-Sentence Argument Aggregation

Event arguments can appear across multiple sentences. We construct a **document-level entity graph** where:
- Nodes are entity mentions (from an off-the-shelf NER tagger run on D).
- Edges connect coreferent mentions and sentences adjacent in the document.
- A lightweight graph attention network (GAT, 2 layers, hidden dim=128) propagates contextual information across sentence boundaries.
- The GAT's output representations are fed as additional context to the pointer mechanism, enabling the decoder to select an argument from sentence S_i even when the event trigger is in sentence S_j.

This module is also trained end-to-end with the pointer head, but its weights are small (≈50K parameters).

### 3.4 Overall Architecture Flow

```
Input: Document D + Schema S
   │
   ├─ Encode D with frozen LLM (e.g., Llama-3-8B) → hidden states H_D
   ├─ Compile S into DFA grammar G_S (symbolic, no learned params)
   │
   ├─ Run NER on D → entity spans E_D
   ├─ Build entity graph → GAT → context vectors C_D
   │
   └─ Decode event structures:
        For each event type e in S:
          For each role r in R_e:
            - Constrain vocabulary via G_S (only valid role-filling tokens)
            - Condition pointer on H_D + C_D → select span from D
        Output: structured JSON with event triggers + arguments
```

**Training:** Only the span pointer head and GAT module are trained (≈5M parameters total). Training uses annotated event datasets (see §5) with standard cross-entropy loss on span boundaries. The LLM and NER tagger remain frozen.

**Inference:** Given a new schema S' unseen during training, we compile a new grammar G_{S'} automatically. The pointer head and GAT generalize via the shared span-selection and aggregation mechanism, without any fine-tuning on S'.

---

## 4. Dataset & Benchmark

We evaluate on three datasets covering diverse domains and document lengths:

| Dataset | Domain | Documents | Event Types | Avg Doc Length | Standard Split |
|---------|--------|-----------|-------------|----------------|----------------|
| **RAMS** | News (Wikinews) | 9,124 | 139 | 4.2 sentences | 7,329/874/921 |
| **WikiEvents** | News (Wikipedia) | 246 articles | 50 | 15+ sentences | 172/28/46 |
| **MLEE** | Biomedical (literature) | 1,413 abstracts | 19 | 5–10 sentences | 989/198/226 |

**Why these three:**
- RAMS: The standard document-level EE benchmark. Each event has arguments distributed across the document.
- WikiEvents: Longer documents with more complex event structures and hierarchical schemas.
- MLEE: Biomedical domain — tests schema generalization to specialized ontology-driven schemas different from news events.

**Zero-shot schema evaluation:** We also construct a zero-shot benchmark by holding out 25% of event types from each dataset during training. At test time, the system must extract events with these held-out schemas using only the grammar compiled from the schema definition (no training examples seen). This directly tests H3.

---

## 5. Evaluation Metrics

| Metric | Definition | Primary? |
|--------|------------|----------|
| **Trigger F1** | Exact-match F1 on event trigger identification + classification | Yes |
| **Argument F1** | Exact-match F1 on argument role-filling (span boundaries must match) | Yes |
| **Argument Head F1** | Head-word F1 (lenient span match, less strict than exact) | Secondary |
| **Hallucination Rate** | % of extracted arguments whose span does not appear verbatim in the source document | Critical |
| **Schema Transfer F1** | Argument F1 evaluated only on held-out event schemas (zero-shot) | Yes |
| **Inference Latency** | Wall-clock time per document (sec) | Monitoring |

**Statistical rigor:** For all F1 metrics, report mean ± 1.96 × SEM over 5 independent seeds. For hallucination rate, report bootstrapped 95% confidence intervals.

---

## 6. Baselines

| Baseline | Category | Description |
|----------|----------|-------------|
| **BART-EE** | Fine-tuned seq2seq | BART-large fine-tuned on RAMS/WikiEvents/MLEE (published state-of-the-art for document-level EE) |
| **LLM-Prompt** | Zero-shot LLM | GPT-4 / Llama-3-8B prompted with schema description + in-context examples (2-shot), free-form generation |
| **LLM-Prompt + Verif.** | Prompt + verification | Same as above, but a second LLM call verifies extractions against source text |
| **OneIE** | Graph-based | Published graph-based event extraction with BERT encoding (pre-LLM SOTA) |
| **CSE-NoConstraints** | Ablation variant | Our method without DFA grammar constraints (free decoding, pointer still active) |
| **CSE-NoPointer** | Ablation variant | Our method without span-pointer (free generation, grammar still active) |

All LLM baselines use the same frozen LLM (Llama-3-8B) for fair comparison. GPT-4 is included as a computational upper bound for zero-shot performance.

---

## 7. Ablations

| Ablation | Component Removed | What It Tests |
|----------|-------------------|---------------|
| A1: No grammar constraint | Remove DFA grammar (free LM generation) | Tests H1 — contribution of hard schema constraints to faithfulness |
| A2: No span pointer | Allow free token generation for arguments | Tests the hallucination prevention mechanism |
| A3: Sentence-local only | Restrict argument search to trigger's sentence | Tests H2 — value of document-level aggregation |
| A4: No entity graph (GAT) | Replace GAT with linear context weighting | Tests the GAT cross-sentence propagation |
| A5: Grammar-only, no pointer | Use DFA grammar but free generation for spans | Isolates pointer vs grammar contributions |
| A6: Larger LLM backbone | Replace Llama-3-8B with Llama-3-70B (frozen) | Tests scaling: does a larger backbone compensate for smaller constrained components? |

Each ablation is run on the full test sets of all three datasets. Effect size (Cohen's d) is reported for the primary metrics.

---

## 8. Expected Failure Modes

| Failure Mode | Likelihood | Mitigation |
|-------------|-----------|------------|
| **NER cascading errors.** If the off-the-shelf NER misses entity mentions, the pointer mechanism cannot select them, causing false negatives. | High | Use a high-recall NER at lowered confidence threshold; incorporate an "entity proposal" fine-tuning step if needed. |
| **Grammar compilation too restrictive.** Complex schemas with optional roles, nested event structures may require grammar features that are expensive to compile at inference time. | Medium | Implement grammar relaxation fallback: when the DFA blocks all tokens, fall back to unconstrained decoding for that slot with a penalty. |
| **Pointer head fails to generalize to new schemas.** The training distribution of entity types may not cover types in held-out schemas (e.g., drug names → gene names). | Medium | Train pointer on a diverse corpus of document-span selection tasks (SQuAD 2.0, DROP) before domain-specific fine-tuning. |
| **GAT oversmoothing on long documents.** Documents with >20 sentences may cause entity representations to converge to indistinguishable vectors. | Low | Use identity skip-connections and early stopping on the number of propagation steps. |
| **Hallucination rate floor > 0.** Some valid extractions require inference beyond span copying (e.g., "his wife" → resolve to a named entity from earlier in the text). | Medium | Add a coreference resolution pass before pointer selection; document which errors are recoverable vs inherent. |
| **OOM on long documents.** Llama-3-8B inference on 15+ sentence documents may exceed GPU memory for batch decoding. | Low | Implement sliding-window encoding with overlap; document batch size per dataset. |

---

## 9. Short Execution Plan

### Phase 1: Infrastructure (Weeks 1–2)
- [ ] Set up document-level EE evaluation framework (RAMS, WikiEvents, MLEE).
- [ ] Implement schema-to-DFA compiler (Python + context-free grammar parser).
- [ ] Load frozen Llama-3-8B; verify baseline LLM-Prompt results.

### Phase 2: Implementation (Weeks 3–5)
- [ ] Implement span pointer head on top of LLM hidden states.
- [ ] Implement entity-graph GAT aggregator.
- [ ] Integrate constrained decoding with HuggingFace's `generate()` via custom logits processor.
- [ ] Build zero-shot schema hold-out splits.

### Phase 3: Training & Validation (Weeks 6–8)
- [ ] Train pointer + GAT on RAMS train set (2 epochs, batch size 8, A100 40GB).
- [ ] Validate on RAMS dev; check hallucination rate.
- [ ] Debug grammar failures; tune fallback threshold.
- [ ] Full training on all three datasets.

### Phase 4: Evaluation & Ablations (Weeks 9–11)
- [ ] Run all baselines (BART-EE, OneIE, LLM baselines).
- [ ] Run 6 ablations (A1–A6) on all datasets.
- [ ] Run zero-shot schema evaluation.
- [ ] Statistical analysis (confidence intervals, effect sizes).

### Phase 5: Analysis & Write-up (Weeks 12–14)
- [ ] Error analysis: categorize false positives/negatives by failure type.
- [ ] Document failure modes with examples.
- [ ] Write paper (target: ACL Rolling Review / EMNLP / NAACL).
- [ ] Release code + grammar compiler as open-source library.

### Resource Requirements
- GPU: 1× A100 40GB (training), 1× A100 (inference / baselines).
- Storage: <100 GB (datasets + model checkpoints).
- Personnel: 1 researcher + 1 advisor.

---

## 10. Expected Outcomes & Impact

**If successful**, this proposal would deliver:
1. An open-source schema-to-constrained-decoding compiler that works with any HuggingFace LLM.
2. State-of-the-art document-level event extraction results on RAMS, WikiEvents, and MLEE, with hallucination rates near zero.
3. Demonstrated zero-shot schema transfer, enabling event extraction for new domains with zero annotation cost.
4. A clear decomposition of where value comes from: grammar constraints (hallucination reduction) vs. span pointers (faithfulness) vs. graph aggregation (cross-sentence coverage).

**Fallback plan:** If the constrained decoding approach proves too restrictive (e.g., grammar compilation is intractable for complex schemas), we fall back to a softer variant: schema-guided reranking of top-K beam hypotheses, trading some faithfulness guarantees for schema coverage.

**Target venue:** EMNLP 2026 or ACL Rolling Review (ARR) 2026 cycle.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 17 |
| Topic | Information extraction |
| Original user goal | Generate a research proposal on automated information extraction. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_17/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_17/final_report.md` (15237 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_17/prompt.txt` (669 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_17/query.json` (130 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_17/stdout.txt` (8878 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_17/stderr.txt` (251 bytes)

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
