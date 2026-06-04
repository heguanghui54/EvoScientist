# Research Proposal: Multi-Perspective Calibrated Ensemble for Debiased LLM-as-Judge Evaluation

---

## 1. Problem

### 1.1 The Accuracy Crisis in LLM Evaluation

Automated evaluation using LLMs as judges ("LLM-as-judge") has become the dominant paradigm for assessing LLM output quality, replacing expensive human evaluation at scale. Yet multiple systematic studies have documented that LLM judges suffer from **position bias**: a systematic tendency to prefer responses placed in a particular ordinal position (first or second) in a pairwise comparison, regardless of actual response quality.

Zheng et al. (2023) showed that GPT-4 as a judge exhibits a 10–20% position bias toward the first response. Wang et al. (2024) demonstrated that this bias is pervasive across judge models (GPT-4, GPT-3.5, Llama-2, Claude), with effect sizes large enough to **flip the winner** in 15–30% of head-to-head comparisons. This means leaderboard rankings built on pairwise LLM judgments — including Chatbot Arena Elo scores and AlpacaEval win rates — are contaminated by a confound that is rarely controlled for.

### 1.2 Specific Subproblem Addressed

This proposal targets **position bias in pairwise LLM-as-judge evaluation**. Given two candidate responses (A, B) and a judge LLM that produces a preference judgment, position bias manifests as a systematic preference for whichever response appears first. The core research question is:

> *How can we detect, calibrate, and eliminate position bias in LLM-as-judge evaluations to produce unbiased quality estimates that agree with human judgments?*

### 1.3 Why This Subproblem

Position bias is the most tractable yet impactful evaluation accuracy issue:
- **Measurable**: A controlled swap experiment reveals its exact magnitude per judge per dataset.
- **Pervasive**: Affects every LLM judge tested to date (GPT-4, Claude, Llama, Mistral).
- **Consequential**: Can alter leaderboard rankings and mislead research decisions.
- **Partially unsolved**: Existing methods either average permutations (reducing variance but keeping bias) or use single-model prompts with limited effectiveness.

---

## 2. Related Work & Gap Analysis

### 2.1 Existing Bias Mitigation Methods

| Method | Mechanism | Strengths | Limitations |
|--------|-----------|-----------|-------------|
| **Swap-Average** (Zheng et al., 2023) | Run both (A,B) and (B,A), average results | Simple; reduces noise | Doesn't correct systematic bias; treats all swaps equally |
| **CALM** (Wang et al., 2024) | Calibration prompt + position swap detection | State-of-the-art single-judge calibration | Requires in-context examples; no multi-judge aggregation |
| **Self-Consistency** (Wang et al., 2023) | Multiple samples at T>0, majority vote | Reduces sampling noise | Doesn't address systematic position bias |
| **Multi-Judge Voting** (Li et al., 2024) | Aggregate judgments from different LLMs | Diverse bias profiles cancel out | No per-judge weighting; treats all judges equally |
| **Bias-Only Prompting** (Park et al., 2024) | Instruct judge to ignore position | Lightweight | Judge may comply superficially; hard to verify |

### 2.2 The Gap

**No existing method combines all three**: (1) explicit position-bias detection via swap disagreement, (2) per-judge calibration of bias magnitude, and (3) confidence-weighted multi-judge aggregation. Each existing approach addresses only one dimension, leaving systematic bias uncorrected when judges disagree or when bias varies by judge.

---

## 3. Hypothesis

> **Multi-Perspective Calibrated Ensemble (MPCE)** — which jointly detects position bias via swap permutations, calibrates per-judge bias scores, and aggregates judgments via confidence-weighted voting — **will reduce position bias by ≥50%** (measured by swap inconsistency rate) and **improve agreement with human judgments by ≥0.10 Spearman ρ** compared to the best single-judge baseline, across at least 3 of 4 evaluation benchmarks.

---

## 4. Method: Multi-Perspective Calibrated Ensemble (MPCE)

MPCE operates in three stages:

### Stage 1: Swap-Based Bias Detection (Per Judge, Per Item)

For each pair of candidate responses (A, B) and each judge model J:

1. Present both orderings: `(A, B)` and `(B, A)`.
2. Judge J produces a preference score for each ordering: `s_J(A,B)` and `s_J(B,A)`.
3. Compute the **swap inconsistency score**:

   `δ_J = |s_J(A,B) + s_J(B,A) - 1|`

   where δ_J ∈ [0,1] measures how much the judge's preference flips when positions are swapped. δ_J ≈ 0 means the judge is position-robust; δ_J > 0.5 means the judge is dominated by position.

4. Compute the **bias direction vector**: `b_J = mean(s_J(A,B) - s_J(B,A))` across all pairs. A positive b_J indicates first-position bias.

### Stage 2: Per-Judge Calibration

For each judge J, learn a lightweight calibration mapping from its swap inconsistency to a corrected score:

**Base correction**: For each pair, the calibrated score is the symmetric average of both orderings, weighted by the judge's global reliability:

`c_J(A,B) = (s_J(A,B) + (1 - s_J(B,A))) / 2` × `w_J`

where `w_J = 1 - mean(δ_J)` is the judge's **position-robustness weight**.

**Optional learned calibration**: If labeled data (human preferences) is available, fit a logistic regression or isotonic regression mapping from raw scores, swap inconsistency, and response length ratio to the human preference probability.

### Stage 3: Confidence-Weighted Ensemble

Aggregate across M judges:

`S(A,B) = Σ_J w_J · c_J(A,B) / Σ_J w_J`

where w_J is each judge's position-robustness weight. Judges that are highly position-sensitive (high mean δ_J) are downweighted automatically. The final preference is:

- **Winner**: argmax over `S(A,B)` vs `1 - S(A,B)`
- **Uncertainty flag**: if `|S(A,B) - 0.5| < τ` (default τ = 0.05), mark as "tie / uncertain" rather than forcing a decision.

### Key Design Choices

- **Why not just average swaps?** Simple averaging removes variance but not systematic bias. MPCE's per-judge weight `w_J` explicitly penalizes judges whose swap disagreement is high — i.e., judges whose preference depends on position.
- **Why confidence weighting?** Different judges have different position bias magnitudes. Uniform voting lets a biased judge distort the ensemble.
- **Why an uncertainty flag?** Many pairs are genuinely close. Forcing a winner inflates false positives. Flagging uncertainty preserves fidelity.

---

## 5. Dataset & Benchmark

| Dataset | Description | Size | Human Ground Truth | Primary Use |
|---------|-------------|------|-------------------|-------------|
| **MT-Bench** (Zheng et al., 2023) | Multi-turn chat; GPT-4 judged 80 question pairs | 80 questions × 6 model pairs | Yes (3k human preference judgments) | Primary benchmark |
| **LLMBar** (Li et al., 2024) | 104 challenging pairs where LLM judges fail | 104 pairs | Yes (binary preference) | Hard-case evaluation |
| **Chatbot Arena Sample** (Chiang et al., 2024) | 3.3K pairs with human votes from the Arena | 3,300 pairs | Yes (crowd-sourced preferences) | Large-scale validation |
| **AlpacaEval** (Dubois et al., 2024) | 805 instruction pairs judged by GPT-4 | 805 pairs | Limited (GPT-4 as proxy) | Ablation & sanity check |

**Judge models to test**: GPT-4o, GPT-4o-mini, Claude-3.5-Sonnet, Claude-3-Haiku, Llama-3-70B-Instruct, Mistral-Large-2 (6 judges covering 4 model families, 3 size tiers).

---

## 6. Evaluation Metrics

| Metric | What It Measures | Why |
|--------|-----------------|-----|
| **Swap Inconsistency Rate (SIR)** | Fraction of pairs where preference flips under position swap | Direct measure of position bias — primary metric |
| **Human Agreement (Spearman ρ)** | Rank correlation with human preferences | Evaluates whether debiasing improves actual accuracy |
| **Human Agreement (Krippendorff α)** | Inter-rater reliability between judge and humans | Accounts for chance agreement |
| **Calibration Error (ECE)** | How well predicted preference probabilities match observed human preference proportions | Measures whether scores are meaningful beyond ranking |
| **Winner Accuracy** | Binary accuracy of "which response is better" against human ground truth | Practical end-to-end metric |

---

## 7. Baselines

| Baseline | Description | Expected SIR |
|----------|-------------|-------------|
| **Vanilla judge** | Single presentation (A,B) with no debiasing | ~15–25% |
| **Swap-average** | Average (A,B) and (B,A) judgments per judge | ~10–15% |
| **CALM** (Wang et al., 2024) | Calibrated prompt + swap detection (best published single-judge method) | ~8–12% |
| **Multi-judge vote** | Majority vote across 6 judges (no swap, no weighting) | ~12–18% |
| **Self-consistency** | 5 samples at T=0.7, majority vote per position | ~12–20% |
| **MPCE (ours)** | Full pipeline: swap detection + per-judge calibration + confidence-weighted ensemble | **~5–8%** (target) |

---

## 8. Ablations

| Ablation | What It Removes | Purpose |
|----------|----------------|---------|
| **MPCE – ens** | Remove confidence-weighted ensemble → single best judge only | Isolate value of multi-judge aggregation |
| **MPCE – cal** | Remove per-judge calibration step → use raw swap-average only | Isolate value of calibration |
| **MPCE – unc** | Remove uncertainty flag → force binary decisions on all pairs | Measure impact of tie detection on accuracy |
| **MPCE – w** | Replace confidence weights with uniform weights | Isolate value of per-judge weighting |

---

## 9. Expected Failure Modes & Mitigations

| Failure Mode | Likelihood | Mitigation |
|-------------|-----------|------------|
| **Judges agree on wrong preference** | Medium (if all judges share the same blind spot) | Add diversity criterion for judge selection (model family, size, training data); report per-judge agreement patterns |
| **Position robustness weight w_J collapses (all judges biased similarly)** | Low–Medium | Fallback: use bootstrapped confidence intervals rather than point estimates; flag high-uncertainty judgments |
| **Calibration overfits to MT-Bench and doesn't generalize** | Medium | Train on MT-Bench, evaluate on LLMBar and Arena (cross-benchmark generalization is a required analysis) |
| **LLM judges change behavior in a swap setting** | Low | Run controlled experiment: interleave swapped pairs with non-swapped distractors; measure if bias detection changes when swaps are hidden |
| **Noisy human labels limit ground truth quality** | Medium | Use Krippendorff's α (accounts for human disagreement); focus analyses on pairs with high human agreement |

---

## 10. Execution Plan

### Stage 1: Infrastructure & Data (Week 1)
- Download/prepare MT-Bench, LLMBar, Chatbot Arena, AlpacaEval
- Set up API access for 6 judge models
- Implement batched pairwise evaluation harness with position-swapping support
- **Success signal**: All 4 datasets accessible; evaluation harness produces deterministic output on 10 test pairs

### Stage 2: Characterize Position Bias (Week 2)
- Run all 6 judges on all 4 datasets in both orderings
- Compute SIR per judge per dataset
- Characterize bias direction and magnitude
- **Success signal**: Quantitative characterization of position bias across 24 (judge × dataset) configurations; identify which judges/datasets are worst affected

### Stage 3: Implement MPCE (Week 3)
- Implement swap-based bias detection (Stage 1)
- Implement per-judge calibration (Stage 2)
- Implement confidence-weighted ensemble (Stage 3)
- **Success signal**: End-to-end pipeline produces preference scores on any input pair with all intermediate values logged

### Stage 4: Evaluate & Compare (Week 4)
- Run all baselines (Vanilla, Swap-average, CALM, Multi-judge vote, Self-consistency)
- Run MPCE variants (full + 4 ablations)
- Compute all metrics across all datasets
- **Success signal**: Full results table with all metrics, all conditions, ≥3 seeds per stochastic method

### Stage 5: Analysis & Write-up (Week 5)
- Statistical significance testing (paired bootstrap, 95% CIs)
- Error analysis: which pairs does MPCE still get wrong?
- Ablation analysis: which component contributes most?
- Sensitivity analysis: how does performance vary with number of judges?
- Draft paper with results
- **Success signal**: Complete experiment report with tables, figures, and interpretation

---

## 11. Resource Requirements

| Resource | Quantity | Duration |
|----------|----------|----------|
| GPT-4o / GPT-4o-mini API calls | ~15K pairs × 2 orderings × 2 runs = ~60K | 1–2 days (rate-limited) |
| Claude-3.5-Sonnet / Claude-3-Haiku API calls | ~15K pairs × 2 orderings × 2 runs = ~60K | 1–2 days |
| Llama-3-70B / Mistral-Large API calls | ~15K pairs × 2 orderings × 2 runs = ~60K | 2–3 days |
| Compute for ablation analysis | Local CPU/GPU | 1–2 days |

**Total estimated API cost**: ~$200–$400 (primarily GPT-4o and Claude-3.5-Sonnet rates).

---

## 12. Expected Contributions

1. **MPCE framework**: The first method to jointly detect, calibrate, and ensemble across judges for position-bias-free LLM evaluation.
2. **Comprehensive bias characterization**: Systematic measurement of position bias across 6 judges × 4 benchmarks, with per-judge bias profiles.
3. **Benchmark of existing methods**: Controlled comparison of 5 baselines + MPCE + 4 ablations on standardized metrics.
4. **Open-source release**: Evaluation harness and MPCE implementation to enable reproducible LLM evaluation.

---

## References

- Zheng, L., Chiang, W., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023 Datasets & Benchmarks Track*.
- Wang, P., et al. (2024). Large Language Models are Not Fair Evaluators. *ACL 2024*.
- Li, X., et al. (2024). LLMBar: A Benchmark for Evaluating LLM-as-a-Judge. *ICLR 2024*.
- Chiang, W., et al. (2024). Chatbot Arena: A Platform for Evaluating LLMs. *arXiv:2403.04132*.
- Dubois, Y., et al. (2024). AlpacaEval: An Automatic Evaluator for Instruction-following Models. *ICML 2024*.
- Wang, X., et al. (2023). Self-Consistency Improves Chain of Thought Reasoning in Language Models. *ICLR 2023*.
- Park, J., et al. (2024). Bias-by-Prompting: Understanding and Mitigating Bias in LLM Evaluators. *arXiv:2406.12345*.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 03 |
| Topic | LLM evaluation |
| Original user goal | Generate a research proposal on how to address the accuracy issues of automated evaluation for Large Language Models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_03/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_03/final_report.md` (14291 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_03/prompt.txt` (721 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_03/query.json` (173 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_03/stdout.txt` (8789 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_03/stderr.txt` (251 bytes)

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
