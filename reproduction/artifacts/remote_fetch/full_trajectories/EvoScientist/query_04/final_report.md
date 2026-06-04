# TrialMatch-Agents: A Multi-Agent Framework for Explainable Clinical Trial Eligibility Matching via Specialized Criterion Decomposition

**Subproblem chosen:** Clinical trial eligibility screening and patient-trial matching in oncology — specifically, the automated determination of whether a patient meets a trial's eligibility criteria given unstructured clinical text.

---

## 1. Problem

**Clinical trial recruitment is the single largest bottleneck in drug development.** Fewer than 5% of adult cancer patients enroll in clinical trials, and roughly 80% of trials fail to meet their enrollment targets on time (Getz et al., 2023). The primary barrier is not patient awareness but the labor-intensive screening process: clinical research coordinators manually review each patient's electronic health records (EHRs) against each trial's eligibility criteria — a process that takes 20–40 minutes per patient-trial pair and does not scale to the ~500,000 trials listed on ClinicalTrials.gov.

**Formally, the patient-trial matching problem is:** Given a patient record *P* (unstructured clinical notes, lab reports, pathology, medication lists) and a clinical trial *T* with eligibility criteria *C* (a set of inclusion/exclusion criteria expressed in natural language), determine whether *P* is eligible for *T*. Each criterion *c ∈ C* requires a binary (or graded) eligibility judgment, and the trial-level judgment is a logical function over the criterion-level judgments.

**Why this is hard for current AI agents:** Eligibility criteria span highly heterogeneous knowledge dimensions — demographics, disease histology, genomic biomarkers, prior treatment history, comorbidities, lab values, and concurrent medications. A single LLM must reason across all these dimensions simultaneously, leading to context confusion (the model loses track of which criteria apply), hallucinated patient facts, and opaque decisions with no traceable evidence. Current state-of-the-art systems (TrialGPT, LLM-Match) treat this as a monolithic classification or retrieval task, producing no structured decomposition per criterion dimension and offering minimal explainability.

---

## 2. Hypothesis

**Central hypothesis:** Decomposing clinical trial eligibility matching into a multi-agent system with specialized agents for distinct criterion dimensions — each equipped with dimension-specific retrieval and reasoning capabilities — improves matching accuracy, enables traceable evidence per judgment, and provides calibrated confidence that allows effective human-AI triage, compared to monolithic single-LLM approaches.

**Sub-hypotheses:**

- **H1 (Accuracy):** A multi-agent decomposition yields higher patient-trial matching accuracy (NDCG@10, F1) than single-LLM baselines (TrialGPT, zero-shot GPT-4, LLM-Match) on TREC Clinical Tracks benchmarks, because each agent reasons over a focused subset of criteria without cross-dimension interference.

- **H2 (Explainability):** Multi-agent architectures naturally produce structured, criterion-level evidence traces that enable clinicians to verify individual judgments, achieving higher factuality and lower hallucination rates (measured by expert annotation of a random sample of 200 patient-criterion pairs).

- **H3 (Triage):** Agent-level confidence calibration enables a reliable human-triage policy: cases where all agents agree with high confidence can be fully automated, while low-confidence cases can be escalated, maintaining overall accuracy comparable to full manual review while reducing human workload by ≥50%.

- **H4 (Modularity):** Individual agents can be independently upgraded (e.g., integrating a specialized genomic reasoning tool or a fine-tuned biomedical LLM) without retraining the full system, enabling continuous improvement.

---

## 3. Method: TrialMatch-Agents

TrialMatch-Agents decomposes the eligibility matching task into a **coordinated multi-agent architecture** with five specialized agent types and a coordinator agent.

### 3.1 Architecture

```
Patient Record (unstructured clinical text)
                      │
                      ▼
┌──────────────────────────────────────────┐
│           Criterion Decomposer            │
│   (Parses trial criteria → dimensions)    │
└──────────────────────────────────────────┘
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
┌──────────┐   ┌──────────┐      ┌──────────┐
│Demographic│   │  Disease │ ...  │Comorbidity│
│  Agent    │   │  Agent   │      │  Agent    │
│           │   │          │      │           │
│·Age/gender│   │·Histology│      │·Conditions│
│·Location  │   │·Stage    │      │·Severity  │
│·ECOG      │   │·Subtype  │      │·Exclusion │
└──────────┘   └──────────┘      └──────────┘
      │              │                  │
      └──────────────┼──────────────────┘
                     ▼
┌──────────────────────────────────────────┐
│           Coordinator Agent               │
│   (Aggregates → confidence → verdict)     │
└──────────────────────────────────────────┘
                     │
                     ▼
         Trial-Level Judgment + Evidence Trace
```

### 3.2 Agent Design

Each specialized agent follows a **perceive → retrieve → reason → judge** loop:

| Step | Operation |
|------|-----------|
| **Perceive** | Receive the subset of eligibility criteria relevant to this dimension (from Criterion Decomposer) |
| **Retrieve** | Use RAG to extract relevant text spans from the patient record (structured queries per dimension) |
| **Reason** | Apply dimension-specific reasoning (e.g., biomarker agent uses a gene-variant lookup tool; lab agent uses reference-range calculator) |
| **Judge** | Output a structured verdict: `{criterion_id, status: (eligible/ineligible/uncertain), evidence: [text spans], confidence: [0-1]}` |

**Agent specializations:**

1. **Demographic Agent:** Age, sex, ECOG performance status, geographic restrictions. Retrieves structured EHR fields.
2. **Disease Histology Agent:** Cancer type, histologic subtype, TNM stage, grade. Uses oncology knowledge base for histology classification.
3. **Biomarker/Genomic Agent:** Mutation status (EGFR, KRAS, etc.), IHC markers (PD-L1, HER2), fusion genes. Integrates structured molecular pathology reports.
4. **Prior Treatment Agent:** Prior lines of therapy, response status, washout periods, prior radiation fields. Extracts from medication and treatment timelines.
5. **Comorbidity & Organ Function Agent:** Comorbid conditions (CKD, CHF, etc.), organ function (creatinine, LVEF). Maps lab values to organ function categories.
6. **Concurrent Medication Agent:** Prohibited medications, required supportive care. Extracts from medication lists.
7. **Coordinator Agent:** Aggregates all agent verdicts, applies logical combination (AND/OR/NOT criteria structure), produces final trial-level judgment with overall confidence and a human-readable evidence summary.

### 3.3 Key Technical Components

- **Criterion Decomposer:** Uses structured prompting of an LLM (GPT-4o or Llama-3 70B) to parse each eligibility criterion into a dimension label + structured condition. Validated against the human-annotated TREC criteria.
- **Retrieval:** Each agent uses a dimension-specific retriever (BM25 + bi-encoder reranking) over the patient text, with dimension-tailored query expansion (e.g., biomarker agent expands "EGFR mutation" to synonyms and related test names).
- **Confidence Calibration:** Each agent reports confidence based on: (a) proportion of criteria with unambiguous evidence, (b) retrieval relevance scores, (c) self-consistency across N=5 Monte Carlo sampling of the LLM reasoning path.
- **Deliberation Round (optional):** For high-confidence disagreements, agents can exchange rationale in a single round of structured deliberation before the coordinator makes the final call.

### 3.4 Open-Source Variant

To address the reliance on proprietary models noted in the literature (Ghosh et al., 2025 survey), we implement a fully open-source variant using Llama-3 70B / Meditron-70B + open retrievers (BM25, Contriever, E5-mistral).

---

## 4. Dataset / Benchmark

We evaluate on four publicly available benchmarks, following the standard evaluation protocols:

| Benchmark | Year | Description | Size | Metric |
|-----------|------|-------------|------|--------|
| **TREC Clinical Trials Track 2021** | 2021 | Patient descriptions (synthetic) + clinical trial topics | ~75 topics, ~75K trials | NDCG@10, P@10 |
| **TREC Clinical Trials Track 2022** | 2022 | Extended topics, graded relevance | ~50 topics | NDCG@10, P@10 |
| **TREC Clinical Trials Track 2023** | 2023 | Real patient records from MIMIC-III | ~50 topics | NDCG@10, P@10, R-prec |
| **n2c2 Cohort Selection** | 2018 | Patient records + trial eligibility criteria (structured criteria) | 288 patients, 13 tasks | micro-F1, macro-F1 |

**Primary benchmark:** TREC Clinical Trials 2022 (for comparability with TrialGPT, Controlled Reasoning, and LLM-Match which all report on this split).

**Secondary dataset for generalizability:** n2c2 2018 Cohort Selection for criterion-level F1 evaluation.

**Supplementary evaluation on real clinical data:** A set of 100 de-identified patient-trial pairs from an academic medical center (pending IRB exemption — retrospective, de-identified, no human subjects).

---

## 5. Evaluation Metrics

### Primary Metrics (TREC benchmarks)

- **NDCG@10** — primary ranking metric, graded relevance. Expected SOTA: ~0.693 (Jullien et al., 2024). Target: **≥0.75**.
- **Precision@10** — precision of top-10 trial recommendations. Expected SOTA: ~0.73. Target: **≥0.78**.
- **R-prec** — precision at the number of relevant trials.

### Secondary Metrics

- **Patient-level accuracy** — proportion of patient-trial pairs correctly classified (eligible/ineligible). Evaluate on n2c2.
- **Macro-F1 per criterion dimension** — performance breakdown by criterion type (demographic, biomarker, etc.).
- **Explainability score** — measured by clinician raters evaluating 200 randomly sampled patient-criterion judgments for: evidence correctness (is the cited text span relevant?), judgment correctness (is the eligibility label correct given the text?), completeness (were all relevant evidence spans considered?).
- **Human triage efficiency** — proportion of cases confidently resolved by agents vs. escalated for human review.
- **Confidence calibration (ECE)** — Expected Calibration Error between predicted confidence and actual accuracy.

---

## 6. Baselines

| Baseline | Description | Reference |
|----------|-------------|-----------|
| **TrialGPT** | Three-module zero-shot LLM pipeline: retrieval → criterion matching → ranking | Jin et al., 2023 (arXiv:2307.15051) |
| **LLM-Match** | Fine-tuned Llama + RAG for patient matching | Li et al., 2025 (arXiv:2503.13281) |
| **Zero-shot GPT-4o** | Single LLM prompt for eligibility classification | Common baseline |
| **Set-Guided Reasoning** | Controlled LLM reasoning with structured criterion sets | Jullien et al., 2024 (arXiv:2409.18998) |
| **BM25 + Neural Reranker** | Standard IR pipeline (no LLM reasoning) | Kusa et al., 2023 (arXiv:2307.00381) |

All baselines evaluated on identical TREC train/test splits with identical document collections.

---

## 7. Ablations

| Ablation | Purpose | Expected Finding |
|----------|---------|------------------|
| **A1: Single-agent vs. multi-agent** | Remove agent decomposition; route all criteria to one LLM with same total parameter count | Multi-agent outperforms single-agent, especially on criteria-rich trials (≥10 criteria) |
| **A2: With vs. without RAG** | Disable dimension-specific retrieval; agents reason from full patient text | RAG improves precision on biomarker/lab criteria; minimal effect on demographics |
| **A3: With vs. without confidence calibration** | Remove confidence scores; use raw LLM logits | Calibration reduces false positives in the "fully automated" regime |
| **A4: Open-source vs. proprietary backbone** | Compare Llama-3 70B vs. GPT-4o as agent backbone | GPT-4o outperforms on complex reasoning; gap is smaller for structured criteria |
| **A5: With vs. without deliberation** | Remove inter-agent deliberation round | Deliberation helps on conflicting-evidence cases (e.g., patient eligible for inclusion but also meets exclusion) |
| **A6: Criterion decomposer quality** | Compare rule-based decomposition vs. LLM-based vs. human-annotated | LLM-based decomp is nearly as good as human; rule-based fails on complex criteria |

---

## 8. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Mitigation |
|-------------|------------|------------|
| **Agent over-specialization** — agent misses cross-dimensional interactions (e.g., a comorbidity affects treatment eligibility indirectly) | Medium | Coordinator agent explicitly prompts agents to flag "cross-dimension concerns" during deliberation |
| **RAG retrieval misses critical evidence** — patient fact not captured in retrieved spans | Medium | Expand retriever to use query expansion + multi-hop retrieval; report "evidence gap" as a signal in confidence |
| **Criterion decomposition errors** — complex criteria (e.g., "no history of autoimmune disease unless well-controlled") mis-parsed | Medium-High | Evaluate decomposition quality separately; add an "uncertain decomposition" flag that escalates to human |
| **Confidence miscalibration** — agents report high confidence but are wrong | High (common in LLMs) | Use temperature scaling + Monte Carlo self-consistency (N=5); evaluate ECE explicitly and reject poorly-calibrated agents |
| **Benchmark saturation** — TREC benchmarks may not reflect real clinical complexity | Low-Medium | Add real-world evaluation on 100 de-identified patient-trial pairs from academic medical center |
| **LLM hallucination of patient facts** — agent invents lab values or diagnoses | Medium | Strict evidence grounding: each judgment must cite specific text spans; coordinator verifies span existence |

---

## 9. Short Execution Plan

### Phase 0: Infrastructure & Data (Weeks 1–3)
- Set up TREC Clinical Trials 2021/2022/2023 and n2c2 datasets
- Implement Criterion Decomposer (rule-based + LLM variants)
- Implement BM25 + bi-encoder retrieval index over patient text
- Establish evaluation pipeline with TREC metrics (NDCG, P@10, R-prec)

### Phase 1: Baselines (Weeks 4–6)
- Reproduce TrialGPT (retrieval + matching + ranking modules) from published code
- Reproduce LLM-Match (fine-tuning pipeline)
- Implement zero-shot GPT-4o and Set-Guided Reasoning baselines
- Record all baseline metrics on all four benchmarks

### Phase 2: Single-Agent System (Weeks 7–8)
- Implement TrialMatch-Agents without decomposition (full patient context → single LLM) as a controlled ablation
- Establish single-agent upper/lower bounds

### Phase 3: Multi-Agent System (Weeks 9–14)
- Implement each specialized agent with dimension-specific RAG
- Implement Coordinator Agent with aggregation logic
- Implement confidence calibration (Monte Carlo self-consistency)
- Implement deliberation round
- Run full evaluation across all benchmarks

### Phase 4: Ablations & Analysis (Weeks 15–17)
- Run all 6 ablations (A1–A6)
- Compute per-dimension metrics
- Compute explainability scores via clinician rating of 200 samples
- Compute confidence calibration (ECE)
- Error analysis: categorize failure modes across 100 incorrectly-predicted cases

### Phase 5: Real-World Validation & Writing (Weeks 18–20)
- Evaluate on 100 real patient-trial pairs from academic medical center
- Write paper with full results tables, ablation analysis, and case studies
- Release open-source code and model weights

**Total: ~20 weeks** (5 months) for a single-GPU setup (1× A100 or 4× RTX 4090).

---

## 10. Related Work (Condensed)

This proposal builds on and extends the following lines of work, identified via literature search (paper-navigator, arXiv, Semantic Scholar):

- **TrialGPT** (Jin et al., 2023, *Nature Communications*): Three-module zero-shot LLM pipeline for patient-trial matching. Our work extends this by replacing the monolithic matching module with a multi-agent decomposition.
- **LLM-Match** (Li et al., 2025): Fine-tuned open-source LLM with RAG for patient matching. Strong benchmark results; we adopt their RAG approach but add agent specialization.
- **ClinicalAgent** (Yue et al., 2024): Multi-agent system for clinical trial *outcome prediction*, not patient-trial matching. We repurpose the multi-agent paradigm for the matching task.
- **MSK-MATCH** (Rosenthal et al., 2025): Production multi-agent trial matching system at MSK, but uses single LLM + RAG without criterion-dimension decomposition. Achieves 98.6% accuracy on breast cancer trials. We generalize this to multi-cancer types and introduce explicit dimension specialization.
- **Controlled LLM Reasoning** (Jullien et al., 2024): Set-guided reasoning for clinical trial retrieval (NDCG@10=0.693). Our method replaces set-guided prompting with explicit agent decomposition.
- **Scaling CT Matching** (Wong et al., 2023): Systematic study identifying context limitation and accuracy as key challenges. Our agent decomposition directly addresses context limitation.
- **Survey on LLM-Assisted Trial Recruitment** (Ghosh et al., 2025): Identifies weak benchmarks, proprietary model reliance, and lack of explainability as gaps. Our work addresses all three: (a) rigorous evaluation across 4 benchmarks, (b) open-source Llama variant, (c) structured evidence tracing.

---

## 11. Resource Requirements

| Resource | Specification | Purpose |
|----------|--------------|---------|
| GPU | 1× A100 80GB (or 4× RTX 4090) | LLM inference (GPT-4o API + Llama-3 70B local) |
| Storage | 200 GB | Dataset storage, retrieval indices, model checkpoints |
| API access | OpenAI API (GPT-4o, ~$500) | Proprietary backbone for comparison |
| Software | Python, PyTorch, HuggingFace, LangChain/LlamaIndex, TREC eval scripts | Implementation stack |

---

## 12. Anticipated Contributions

1. **Architecture:** TrialMatch-Agents — the first systematic multi-agent decomposition of clinical trial eligibility matching by criterion dimension, with specialized reasoning and retrieval per agent.

2. **Benchmark results:** Comprehensive evaluation across 4 benchmarks (TREC 2021/2022/2023, n2c2) with 6 ablations, comparing multi-agent vs. single-agent vs. SOTA baselines.

3. **Explainability framework:** Structured evidence tracing with per-criterion, per-dimension judgments and confidence calibration — enabling verifiable human-AI collaboration.

4. **Open-source release:** Fully reproducible codebase with open-weight model variant (Llama-3 70B), enabling community extension.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 04 |
| Topic | Healthcare agents |
| Original user goal | Help me generate a research proposal on AI agents in healthcare. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_04/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_04/final_report.md` (19644 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_04/prompt.txt` (668 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_04/query.json` (123 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_04/stdout.txt` (15076 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_04/stderr.txt` (251 bytes)

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
