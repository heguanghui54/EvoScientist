# Fairness-Aware Stylometric Ensemble (FASE): Reducing Demographic False-Positive Disparities in AI-Generated Text Detection

## 1. Title

**Fairness-Aware Stylometric Ensemble (FASE): Reducing False-Positive Disparities in AI-Generated Text Detection Across Writer Populations**

---

## 2. Problem

**False-positive rates in AI-generated text detection are catastrophically unequal across writer populations.** Liang et al. (2023) demonstrated that seven widely-used GPT detectors misclassify 61.22% of non-native English TOEFL essays as AI-generated, while achieving near-perfect accuracy on native U.S. student essays. Individual detectors showed FPRs ranging from 48–76% on non-native writing. This disparity has real-world consequences: students are falsely accused of academic dishonesty, job applicants are unfairly screened, and the tools are unfit for high-stakes educational and hiring contexts.

**The core technical problem** is that existing detectors rely on features (perplexity, probability curvature, n-gram statistics) that correlate with *both* AI-generation *and* non-native or formulaic writing. Low lexical diversity, high repetitiveness, and simple syntactic structures — hallmarks of non-native English — overlap heavily with LLM output. No existing method explicitly disentangles these confounded signals.

**A gap exists in the literature.** State-of-the-art zero-shot detectors (Binoculars, Fast-DetectGPT) report excellent aggregate metrics (0.01% FPR at >90% TPR; 0.9887 AUROC) but do not report stratified results by writer demographics, language background, or writing proficiency. No published method proposes an explicit debiasing objective for AI-text detection, and no standardized fairness benchmark exists for the task.

---

## 3. Hypothesis

**Primary hypothesis (H1):** A detection framework that explicitly models stylometric features of *human writing proficiency* (vocabulary diversity, syntactic complexity, lexical sophistication) as separate dimensions from *AI-generation signals* (perplexity curvature, contrastive LLM scores) can significantly reduce false-positive disparities across writer populations while maintaining high overall accuracy.

**Secondary hypothesis (H2):** A post-hoc calibration procedure with a *group-aware Platt scaling* that learns separate temperature parameters for detected writing-proficiency clusters can equalize FPR across populations at a small cost to overall AUROC.

**Tertiary hypothesis (H3):** An uncertainty-aware rejection mechanism that abstains on low-confidence predictions (where the stylometric and AI-signal dimensions conflict) can reduce the remaining disparity to near-zero, at the cost of coverage.

---

## 4. Method: Fairness-Aware Stylometric Ensemble (FASE)

We propose a three-component architecture:

### Component A: Multi-Signal Feature Extraction

For each input text, we extract four feature groups:

| Feature Group | Signals | Source |
|---|---|---|
| **A1: Contrastive LLM Score** | Binoculars score (log-perplexity / cross-perplexity ratio) | Falcon-7B observer/performer pair |
| **A2: Conditional Curvature** | Fast-DetectGPT conditional probability curvature | LLaMA-2-7B surrogate model |
| **A3: Perplexity Profile** | Per-token log-probability mean, variance, skew, quantiles | LLaMA-2-7B |
| **A4: Stylometric Fingerprint** | 15 features: TTR (type-token ratio), HDD (lexical diversity via hypergeometric distribution), MTLD (Measure of Textual Lexical Diversity), Yule's K, sentence length mean/variance, clause density, coordination/subordination ratios, nominalization rate, passive voice rate, discourse marker density, POS entropy, average word length, hapax legomena percentage | SpaCy / custom scripts |

**Rationale for A4:** Features like TTR, MTLD, and HDD are established in the NLP literature as robust measures of lexical diversity that correlate with writing proficiency. LLMs generating new text typically exhibit higher lexical diversity than non-native human writers (they sample from a broad vocabulary), so A4 provides a disentangling signal that existing detectors ignore.

### Component B: Fairness-Aware Calibrated Classifier

We train a lightweight classifier (gradient-boosted trees, LightGBM) on the concatenated feature vector [A1; A2; A3; A4]. The training objective augments standard log-loss with a **fairness penalty**:

```
L = L_CE + λ · Φ(group_FPRs)
```

where `Φ` is the variance of false-positive rates across detected writing-proficiency clusters, and λ is a hyperparameter controlling the fairness–accuracy tradeoff. Writing-proficiency clusters are derived from the A4 stylometric features using unsupervised Gaussian mixture modeling (GMM; 3–5 components), without requiring explicit demographic labels at inference time.

### Component C: Uncertainty-Aware Rejection

We train a confidence estimator (a separate LightGBM regressor on out-of-bag validation predictions) that predicts whether the classifier's output is reliable. When confidence falls below a threshold τ, the system **abstains** — returning "uncertain" instead of a binary human/AI prediction. This prevents false accusations on borderline cases.

**Inference pipeline:**

```
Input text
    ↓
[Feature extraction: A1 × A2 × A3 × A4]
    ↓
[LightGBM classifier → score s ∈ [0, 1]]
    ↓
[Confidence estimator → confidence c ∈ [0, 1]]
    ↓
if c < τ → return ABSTAIN
else → return HUMAN (s < threshold) or AI (s ≥ threshold)
```

---

## 5. Datasets / Benchmark

We construct an evaluation benchmark with four components:

| Dataset | Role | Size | Human Source | AI Source(s) |
|---|---|---|---|---|
| **M4** | In-domain training + eval | ~300K samples | arXiv, Wikipedia, Reddit, News | ChatGPT, davinci-003, Cohere, LLaMA |
| **HC3** | In-domain eval | ~37K QA pairs | WikiQA, FiQA experts | ChatGPT |
| **RAID** | Adversarial robustness eval | 6M generations | News, essays, creative writing | 11 LLMs + 11 attacks |
| **Non-Native Benchmark (NEW)** | Fairness eval | ~2K essays | TOEFL (91), Lang8 (1K), TOEFL 11 (1.1K) | ChatGPT, GPT-4 (matched-prompt) |

**Non-Native Benchmark construction:** We collect existing non-native English essay datasets (TOEFL essays from Liang et al. corpus, Lang8 learner essays, TOEFL 11) and generate matched-pair AI text by feeding the same essay prompts to ChatGPT and GPT-4. This ensures the evaluation measures detection of *AI text written on the same topics* as the human non-native essays, avoiding topic confounds.

**Proficiency clustering:** We annotate each sample with its GMM-derived proficiency cluster (from A4 features) and also with its ground-truth nativeness (native / non-native) for evaluation purposes only. The classifier never sees ground-truth nativeness during training.

---

## 6. Evaluation Metrics

### Primary Metrics

| Metric | Rationale |
|---|---|
| **FPR@95%TPR (overall)** | Standard metric for low-FPR regime; matches Binoculars evaluation |
| **FPR@95%TPR (per-proficiency cluster)** | Measures FPR disparity across populations |
| **Max-min FPR disparity** | Primary fairness metric: difference between highest and lowest cluster FPR |
| **AUROC (overall)** | Aggregate discriminability (for comparison with prior work) |

### Secondary Metrics

| Metric | Rationale |
|---|---|
| **Abstention rate** | Fraction of predictions the system declines to make |
| **FPR@95%TPR after abstention** | FPR on non-abstained predictions |
| **Coverage-FPR curve** | Area under the coverage-FPR tradeoff |
| **T@1%F (True Positive Rate at 1% FPR)** | Additional low-FPR operating point per prior work |

### Fairness Metrics

| Metric | Rationale |
|---|---|
| **Demographic parity difference** | Max-min FPR across clusters (primary) |
| **Equalized odds gap** | Difference in FNR across clusters (secondary) |
| **FPR ratio (max/min)** | Factor disparity (secondary) |

---

## 7. Baselines

We compare against five detection methods spanning three paradigms:

| Method | Paradigm | Public Code | Relevant FPR |
|---|---|---|---|
| **Binoculars** (Hans et al., 2024) | Zero-shot (contrastive LLM) | Yes | 0.01% FPR @ >90% TPR (overall; demographics not reported) |
| **Fast-DetectGPT** (Bao et al., 2024) | Zero-shot (curvature) | Yes | ~87% TPR @ 1% FPR (ChatGPT; demographics not reported) |
| **Ghostbuster** (Verma et al., 2023) | Classifier (weak LM features) | Yes | 99.0 F1 in-domain |
| **DNA-GPT** (Yang et al., 2023) | Zero-shot (n-gram divergence) | Yes | Outperforms OpenAI classifier |
| **LightGBM (A1+A2+A3 only)** | Ablation control (no stylometrics) | — | Internal ablation |

**All baselines will be re-evaluated on our unified benchmark** with the same metrics, including per-cluster FPR. This is critical because none of the original papers reported demographic-stratified results.

---

## 8. Ablations

We isolate the contribution of each component:

| Ablation | What changes | What it tells us |
|---|---|---|
| **Ablation 1: No A4** | Remove stylometric features (only A1–A3) | Value of writing-proficiency disentanglement |
| **Ablation 2: No fairness penalty** | λ = 0 in training objective | Value of explicit fairness regularization |
| **Ablation 3: No rejection** | Remove Component C (always predict) | Value of uncertainty-aware abstention |
| **Ablation 4: Linear classifier** | Replace LightGBM with logistic regression | Whether non-linear interactions are necessary |
| **Ablation 5: λ sweep** | λ ∈ {0, 0.01, 0.1, 0.5, 1.0, 5.0} | Pareto frontier of accuracy vs. fairness |

---

## 9. Expected Failure Modes

1. **A4 features may not fully disentangle AI generation from low-proficiency writing.** If LLMs are prompted to produce simpler text (e.g., "write at a middle-school reading level"), the stylometric distributions may overlap. **Mitigation**: We test this explicitly by prompting LLMs at various reading levels and measuring A4 overlap.

2. **Fairness penalty may degrade overall AUROC.** This is a known fairness–accuracy tradeoff. **Mitigation**: We map the full Pareto frontier via λ sweep (Ablation 5) and report the achievable operating points. A modest AUROC drop (e.g., 0.005) that halves FPR disparity is a positive result.

3. **Proficiency clusters from GMM may not align with meaningful writer groups.** The unsupervised clustering may split along topic or genre rather than proficiency. **Mitigation**: We evaluate with ground-truth nativeness labels (which exist for our benchmark) as a secondary grouping. We also use manually-curated TOEFL/Lang8 labels as held-out validation of cluster quality.

4. **Confidence estimator may be poorly calibrated on out-of-distribution data.** **Mitigation**: We evaluate abstention performance on the RAID adversarial splits, which include paraphrasing and perturbation attacks that are distributionally different from training data.

5. **Adversarial paraphrasing may collapse the A4 signal.** Recent work (Cheng et al., 2025) shows that guided adversarial paraphrasing reduces Fast-DetectGPT T@1%F by 98.96%. **Mitigation**: We evaluate against the same adversarial paraphrasing attack and report whether the ensemble (A1–A4) is more robust than any single signal.

6. **Non-native AI-generated text may be indistinguishable from non-native human text.** This is a fundamental limit: if an LLM is prompted to mimic a non-native writer, the writing may be truly indistinguishable. **Mitigation**: The abstention mechanism is designed for exactly this regime — the system declines to classify rather than making a false accusation.

---

## 10. Execution Plan

### Phase 1: Infrastructure and Benchmark (Weeks 1–2)

- **Week 1**: Download and preprocess M4, HC3, RAID, TOEFL, Lang8, TOEFL 11. Implement the Non-Native Benchmark construction (matched-pair generation with ChatGPT/GPT-4). Define train/val/test splits. Implement the evaluation harness (all metrics).
- **Week 2**: Implement Feature Group A4 (stylometric fingerprint) using spaCy + custom scripts. Validate feature distributions across datasets. Run GMM clustering; sanity-check cluster interpretability.

### Phase 2: Baseline Reproduction (Weeks 3–4)

- **Week 3**: Reproduce Binoculars and Fast-DetectGPT on our benchmark. Verify that published aggregate metrics are replicated on our splits.
- **Week 4**: Reproduce Ghostbuster and DNA-GPT. Run all baselines through the full metric suite including per-cluster FPR. **First checkpoint**: measure the magnitude of FPR disparities in existing methods.

### Phase 3: Proposed Method (Weeks 5–6)

- **Week 5**: Implement Components A–C. Train LightGBM with λ = 0 (no fairness penalty first). Compare against baseline + A1–A3 baseline (Ablation 1).
- **Week 6**: Add fairness penalty (Component B). Sweep λ values (Ablation 5). Train confidence estimator (Component C). Sweep rejection threshold τ.

### Phase 4: Ablations and Adversarial Robustness (Weeks 7–8)

- **Week 7**: Run Ablations 2–5. Run adversarial robustness evaluation against guided paraphrasing (Cheng et al., 2025).
- **Week 8**: Compile results. Analyze failure cases. Run statistical significance tests (bootstrapped confidence intervals on all metrics, 1,000 resamples). **Second checkpoint**: complete results ready for paper.

### Phase 5: Paper Writing (Week 9–10)

Draft, review, refine. Target venue: ACL Rolling Review or Findings of EMNLP.

---

## 11. Summary

FASE addresses a critical, well-documented gap in AI-generated text detection: the systematic false-positive bias against non-native English writers. By explicitly disentangling writing-proficiency signals from AI-generation signals through a multi-component stylometric ensemble with fairness-regularized training and uncertainty-aware abstention, we expect to substantially reduce FPR disparities while maintaining competitive overall detection accuracy. The proposal includes a comprehensive evaluation benchmark with demographic stratification, five baselines, five ablations, and adversarial robustness testing against state-of-the-art paraphrasing attacks.

**Success criteria:** FASE achieves (i) FPR disparity (max-min across proficiency clusters) ≤ 5 percentage points (vs. 20+ points expected for existing methods), (ii) overall FPR@95%TPR ≤ 1% (competitive with Binoculars), and (iii) abstention rate ≤ 15% at that operating point.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 21 |
| Topic | Content detection |
| Original user goal | Generate a research proposal on how to address false positives in AI-generated content detection. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_21/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_21/final_report.md` (14376 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_21/prompt.txt` (701 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_21/query.json` (157 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_21/stdout.txt` (9631 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_21/stderr.txt` (251 bytes)

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
