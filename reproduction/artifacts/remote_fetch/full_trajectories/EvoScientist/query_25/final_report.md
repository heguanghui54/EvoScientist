# Research Proposal: Conflict-Aware Multi-Hop Reasoning (CAMHR)

## Explicitly Resolving Inter-Document Conflicts in Multi-Source Question Answering

---

## 1. Problem

**Generative language models deployed with retrieval-augmented generation (RAG) must reason across multiple retrieved documents to answer complex questions. Current systems assume these documents complement each other, but real-world information sources routinely conflict — different pages report different dates, different studies report different effect sizes, and different eyewitnesses give different accounts.**

When documents disagree, today's models behave unpredictably: they silently pick one source (usually the one that appears earlier or has higher lexical overlap with the question), hallucinate a compromise answer that matches neither source, or produce inconsistent answers when re-queried with different document subsets. This is not a corner case — conflicting information is pervasive in news, medical guidelines, legal documents, and encyclopedic knowledge.

**The core problem** is that multi-hop reasoning architectures have no explicit mechanism for handling inter-document conflict. Conflict resolution is left as an implicit emergent behavior of the pretrained transformer, and it fails reliably.

**Specific subproblem addressed in this proposal**: When a multi-hop question requires synthesizing information from multiple documents that contain contradictory or inconsistent facts, how can we architect an explicit conflict detection and resolution stage that improves answer accuracy, consistency, and calibration?

---

## 2. Hypothesis

**Primary hypothesis**: Explicitly modeling inter-document conflict as a discrete reasoning stage — **detect → resolve → answer** — improves answer accuracy by at least 10% (absolute F1) on multi-hop questions with conflicting sources, compared to standard end-to-end multi-hop QA architectures that process documents implicitly.

**Secondary hypotheses**:
1. **H₂ₐ**: Conflict-aware reasoning improves consistency: answers become more stable across different subsets of retrieved documents (measured by Krippendorff's α ≥ 0.80 vs. ≤ 0.55 for baselines).
2. **H₂ₓ**: Explicit conflict detection + resolution improves calibration between model confidence and answer correctness on conflict cases (expected calibration error reduced by ≥ 0.15).
3. **H₂ₓ**: Different conflict resolution strategies (source credibility, majority vote, explicit abstention) trade off differently by domain — no single strategy dominates across all conflict types.

---

## 3. Method: Conflict-Aware Multi-Hop Reasoning (CAMHR)

CAMHR adds a dedicated **Conflict Resolution Module** between document retrieval and answer generation, structured as three stages:

### Stage 1: Conflict Detection

Given a question *q* and a set of retrieved documents *D = {d₁, d₂, ..., dₙ}*, extract all factual claims from each document using a lightweight NLI-based claim decomposition. Then compute pairwise contradiction scores between claims that are relevant to *q* using a fine-tuned NLI model (DeBERTa-v3-large-MNLI).

Output: A **conflict graph** where nodes are documents, edges exist if they contain contradictory claims relevant to *q*, and edge weights represent contradiction strength (1 - NLI entailment probability for contradictory pairs).

Documents with no conflict edges → proceed directly to answer generation (standard path).
Documents with conflict edges → proceed to Stage 2.

### Stage 2: Conflict Resolution

Three resolution strategies are implemented and compared:

| Strategy | Mechanism | When It Helps |
|----------|-----------|---------------|
| **Source Credibility Weighting** | Each document gets a credibility score (based on source metadata, recency, authoritativeness). Weight vote by credibility. | News, medical guidelines with known source quality. |
| **Majority Consensus** | When ≥3 sources are available, take the majority-supported fact. Report confidence as proportion. | Encyclopedia-style facts with many independent sources. |
| **Explicit Abstention** | If contradiction strength exceeds threshold *τ* AND no resolution strategy produces a confident answer, output "Sources conflict — answer uncertain" + present conflicting claims. | High-stakes domains (medical, legal) where hallucinating is worse than abstaining. |

A **conflict classifier** (trained on synthetic conflict data, see §4) selects which resolution strategy to apply given the conflict graph properties (density, strength distribution, number of documents, domain).

### Stage 3: Answer Generation with Attribution

The resolved facts are fed into the generator alongside conflict metadata:
- The resolved answer
- Which documents were in conflict
- Which resolution strategy was used
- Confidence score for the resolved answer

The generator is instructed to produce the answer and cite supporting documents. When abstention is triggered, the generator must produce the abstention template rather than hallucinating.

### Full Pipeline

```
Question → Retrieve → Decompose Claims → Conflict Detection
                                            ↓
                              ┌──────────── NO (no conflict)
                              ↓                ↓
                     Conflict Resolution   Standard Generation
                              ↓
                     Answer Generation (with conflict trace)
```

---

## 4. Dataset & Benchmark

No existing dataset explicitly tests multi-hop reasoning under inter-document conflict. We construct two evaluation sets:

### Primary: Conflicting-MuSiQue (Synthetic Controlled)

**Base**: MuSiQue (Multi-hop Sequential Question-answering) — 25K multi-hop questions with supporting documents.

**Conflict injection protocol**:
1. For each multi-hop question, identify the two supporting documents.
2. Make a copy of one supporting document.
3. Edit the copy to inject a controlled contradiction relevant to the answer: change a numerical value (date, count, measurement), replace an entity name, or flip a relational fact.
4. Replace the original document with the edited version.
5. The question now has one supporting document with the correct fact and one with the contradictory fact.

**Controlled variables**:
- **Conflict type**: numerical (dates, counts), entity (names, locations), relational (causal, temporal)
- **Severity**: direct contradiction vs. subtle inconsistency (requires inference to detect conflict)
- **Position**: contradictory document appears first vs. second (to control for position bias)
- **Number of sources**: 2 conflicting, 3 (2-conflict vs. 1-supporting), 4 (3-conflict vs. 1-supporting)

**Size**: 5,000 test questions × 3 severity levels × 3 conflict types = 15,000 evaluation instances (plus 10,000 training instances for the conflict classifier).

### Secondary: HotpotQA-Conflict (Natural)

Take HotpotQA and use an NLI model to automatically identify questions whose supporting documents contain naturally-occurring contradictions. This yields a small real-world benchmark (~200-500 questions). Used for validation of synthetic findings, not for training.

**Expected size**: ~5-10% of HotpotQA has detectable contradictions between supporting docs.

---

## 5. Evaluation Metrics

### Primary Metrics

| Metric | What It Captures | Target |
|--------|-----------------|--------|
| **Answer F1** (token-level) | Factual correctness of generated answer | ≥ 10 pt improvement over FiD |
| **Exact Match** | Complete answer correctness | ≥ 8 pt improvement over FiD |
| **Conflict Detection F1** | Can the model correctly identify when documents conflict? | ≥ 0.85 |

### Consistency & Calibration

| Metric | What It Captures | Target |
|--------|-----------------|--------|
| **Krippendorff's α** | Answer stability across different document subsets | ≥ 0.80 |
| **Expected Calibration Error (ECE)** | Does confidence track accuracy on conflict cases? | ≤ 0.10 |
| **Abstention Rate** | How often does the model correctly decline to answer? | Tuned to maximize a cost-weighted score |

### Diagnostic Metrics

| Metric | What It Captures |
|--------|-----------------|
| **Position bias** | Accuracy by position of contradictory document |
| **Conflict-type accuracy** | Accuracy breakdown by numerical/entity/relational conflicts |
| **Severity sensitivity** | Accuracy by subtle vs. direct contradiction |

---

## 6. Baselines

| Baseline | Description | Why Chosen |
|----------|-------------|------------|
| **Fusion-in-Decoder (FiD)** | State-of-the-art multi-hop QA: encode + fuse + decode | Gold standard multi-hop architecture |
| **FiD + CoT prompting** | FiD with chain-of-thought before answer | Tests whether reasoning chains help implicitly |
| **Standard RAG (retrieve-then-read)** | Retrieve top-5, concatenate, prompt GPT-4/Claude | Industry practice baseline |
| **Self-Consistency RAG** | RAG × 5 samples, majority vote answer | Popularized by Wang et al. (2023) |
| **FiD + Self-Ask** | FiD with intermediate question decomposition | Tests whether decomposition helps resolve conflicts |

All baselines evaluated on both standard MuSiQue (verify no regression) and Conflicting-MuSiQue (primary comparison).

---

## 7. Ablations

| Ablation | What It Tests | Expected Insight |
|----------|--------------|-----------------|
| **No conflict detection** (always route to resolution) | Is detection necessary, or can we always resolve? | Detection prevents unnecessary computation but missing a conflict is costly |
| **No resolution** (detect but just concatenate documents) | Does explicit resolution add value over just flagging? | Unclear — flagging alone may change model behavior |
| **Single resolution strategy** (use only one of 3 strategies) | Is a learned classifier better than any single fixed strategy? | Likely: majority vote works for numerical conflicts, credibility for entity conflicts |
| **No conflict graph** (use linearized conflict features instead) | Is the graph structure important? | Graph structure matters for ≥3 documents |
| **Training-free resolution** (prompt-based, no classifier training) | Can an LLM resolve conflicts from instructions alone? | Measures value of the specialized classifier |
| **Conflict severity sweep** | Accuracy as a function of how subtle the conflict is | Identifies the difficulty boundary |

---

## 8. Expected Failure Modes & Mitigations

| Failure Mode | Likelihood | Impact | Mitigation |
|-------------|-----------|--------|------------|
| **Conflict detector over-flags** (high recall, low precision) | Medium | High — routes to resolution needlessly, adds latency | Adjust NLI contradiction threshold on validation set; report precision-recall curve |
| **Conflict detector under-flags** (high precision, low recall) | Medium | High — misses real conflicts, degrades primary metric | Use recall-oriented detection + separate NLI model for missed conflict analysis |
| **Model learns to ignore conflict metadata** | Low | Critical — entire pipeline becomes a no-op | Debug: probe classifier's attention to conflict signal; if ignored, increase signal through special tokens or architectural gating |
| **Resolution strategy fails on subtle/indirect contradictions** | High | Medium — degrades performance on hardest cases | Analyze per-severity results; consider adding a second-pass deliberation for low-confidence resolved cases |
| **Training-inference mismatch** (synthetic conflicts ≠ natural conflicts) | Medium | High — synthetic gains don't transfer to HotpotQA-Conflict | Proactive validation on HotpotQA-Conflict; if transfer fails, augment synthetic data with natural conflict patterns |
| **Abstention strategy over-used** (models abstain on easy cases) | Low | Medium — reduces useful answers | Set conservative abstention threshold; evaluate abstention as a function of answer confidence |
| **Position bias persists** (resolution favors first document regardless of content) | Medium | High — undermines purpose of explicit resolution | Counterbalancing during construction; measure and report position-conditional accuracy as a diagnostic |

---

## 9. Execution Plan

### Phase 0: Infrastructure & Data Construction (2 weeks)

| Week | Tasks |
|------|-------|
| 1a | Build Conflicting-MuSiQue construction pipeline: MuSiQue download, document editing script for numerical/entity/relational conflicts, validation of injected contradictions via NLI |
| 1b | Implement NLI-based claim decomposition + pairwise contradiction scoring (DeBERTa-v3-large-MNLI) |
| 1c | Identify HotpotQA-Conflict subset using same NLI pipeline |
| 2a | Verify data quality: sample 100 examples, manually audit conflict injection |
| 2b | Write conflict detection evaluation harness |
| 2c | Train conflict classifier on synthetic data (3,000 examples) |

**Deliverables**: Conflicting-MuSiQue dataset (train/dev/test splits), HotpotQA-Conflict benchmark, conflict detection pipeline.

### Phase 1: Baseline Implementations (2 weeks)

| Week | Tasks |
|------|-------|
| 3a | Implement FiD for MuSiQue (reproduce published numbers on standard MuSiQue) |
| 3b | Implement Standard RAG baseline (retrieve-then-generate with GPT-4 / Claude API) |
| 3c | Implement CoT and Self-Ask variants on FiD |
| 4a | Evaluate all baselines on Conflicting-MuSiQue → establish reference scores |
| 4b | Evaluate all baselines on standard MuSiQue → verify no regression |
| 4c | Measure position bias and consistency for each baseline |

**Deliverables**: All five baselines benchmarked on both datasets. Position bias and consistency diagnostics.

### Phase 2: CAMHR Implementation (3 weeks)

| Week | Tasks |
|------|-------|
| 5a | Implement conflict detection → conflict graph construction pipeline |
| 5b | Implement Stage 1 integration with FiD encoder (conflict graph as side input) |
| 5c | Implement Stage 2: three resolution strategy modules (credibility, majority, abstention) |
| 6a | Implement conflict classifier (which strategy to use) |
| 6b | Implement Stage 3: answer generation with conflict metadata |
| 6c | Integrate full CAMHR pipeline, end-to-end |
| 7a | Debug integration issues on small dev set |
| 7b | Tune conflict detection threshold on validation set |
| 7c | Set up evaluation harness end-to-end |

**Deliverables**: Full CAMHR pipeline, end-to-end on dev set.

### Phase 3: Evaluation & Ablations (2 weeks)

| Week | Tasks |
|------|-------|
| 8a | Full CAMHR evaluation on Conflicting-MuSiQue (all severity × type combinations) |
| 8b | Full CAMHR evaluation on MuSiQue (verify no regression on non-conflicting data) |
| 8c | Run all 6 ablations |
| 9a | Full evaluation on HotpotQA-Conflict (transfer check) |
| 9b | Calibration analysis (ECE) for CAMHR vs. baselines |
| 9c | Consistency analysis (Krippendorff's α) |
| 9d | Compile results tables and figures |

**Deliverables**: Complete results with confidence intervals (5 seeds), ablation results, calibration curves.

### Phase 4: Analysis & Write-up (2 weeks)

| Week | Tasks |
|------|-------|
| 10a | Failure analysis: categorize and count failure modes |
| 10b | Error trees: what types of conflict cause CAMHR to fail? |
| 10c | Sensitivity analysis: conflict threshold, number of documents, position |
| 11a | Write paper: Related Work, Method, Experiments, Analysis |
| 11b | Internal review and revision |
| 11c | Release dataset and code |

**Deliverables**: Paper draft (target: ACL/EMNLP/NeurIPS), dataset release, code release.

**Total estimated timeline**: 11 weeks (single researcher, one GPU node).

---

## 10. Prior Work & Positioning

This proposal builds on and differentiates from:

- **Multi-hop QA architectures**: FiD (Izacard & Grave, 2021), REALM (Guu et al., 2020), and RAG (Lewis et al., 2020) all assume complementary information — no conflict handling.
- **Multi-document QA with contradictions**: Chen et al. (2022) study LLM behavior on conflicting information but only analyze, not propose a method. Cohen et al. (2023) propose prompting strategies but no architectural change.
- **NLI for verification**: DAG-NLI (Schuster et al., 2022) and related work use NLI for claim verification but not as a conflict detection stage within a QA pipeline.
- **Abstention in QA**: Kadavath et al. (2022) and Yin et al. (2023) study when models should abstain, but not in the multi-source conflict setting.

**Novelty**: CAMHR is the first architecture that explicitly detects inter-document conflicts via a lightweight NLI module, resolves them through a learned strategy selector, and generates answers with conflict traceability — all within a multi-hop QA pipeline evaluated on a controlled benchmark.

---

## 11. Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU | 1× RTX 3090 (24GB) | 1× A100 (40GB) |
| Storage | 50GB | 100GB |
| API budget (GPT-4/Claude for RAG baselines) | — | ~$500 |
| Key libraries | transformers, torch, NLI models (DeBERTa-v3), MuSiQue/HotpotQA datasets | |
| Stored per run | seeds, configs, checkpoints, logs, predictions | |

All code will use deterministic seeds and logged configs for reproducibility.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 25 |
| Topic | Multi-source reasoning |
| Original user goal | Generate a research proposal on complex reasoning with multi-source information. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_25/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_25/final_report.md` (17318 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_25/prompt.txt` (684 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_25/query.json` (145 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_25/stdout.txt` (8164 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_25/stderr.txt` (251 bytes)

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
