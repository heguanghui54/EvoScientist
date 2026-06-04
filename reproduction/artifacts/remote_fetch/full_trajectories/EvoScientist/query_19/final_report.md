# Adaptive Pairwise Sampling for Cost-Efficient LLM Leaderboards

## 1. Summary & Goals

**Problem.** LLM leaderboards — crowdsourced (Chatbot Arena) or automated (Open LLM Leaderboard, HELM, AlpacaEval) — form the backbone of open-source progress. All face a scaling bottleneck: evaluating every new model across every benchmark costs O(N·M) in models × evaluations. In the Arena setting, pairwise human comparisons are the gold standard but each one costs annotator time. The current default — uniformly random pair selection — wastes budget on uninformative comparisons (e.g., a strong model vs. a weak model whose outcome is near-deterministic).

**Goal.** Develop an adaptive sampling policy that selects which model pairs to compare next, maximizing ranking accuracy per dollar (or per human vote). The target is a leaderboard that reaches stable, correct rankings with 40–60% fewer comparisons than uniform random sampling.

**Subproblem chosen.** This proposal focuses on **adaptive pairwise preference sampling** for a single leaderboard (one evaluation dimension, e.g., "helpfulness" in Chatbot Arena). Extensions to multi-dimensional leaderboards are left as future work.

**What success looks like.**
- At ≤50% of the uniform-random comparison budget, the adaptive policy recovers the same top-K ranking (Spearman ρ ≥ 0.95).
- The policy degrades gracefully under noisy pairwise preferences (simulated label-flipping at 5–20%).
- A practical, deployable algorithm with O(N log N) per-round computation, suitable for streaming model entry.

---

## 2. Hypothesis

**H1 (primary).** Actively selecting the pair of models with maximum expected information gain about the posterior ranking converges to the true ranking in fewer comparisons than uniform random sampling, under a Bayesian Bradley-Terry preference model.

**H2 (robustness).** The advantage of adaptive sampling over random holds even when pairwise preferences contain up to 20% label noise (simulating human disagreement or annotation errors).

**H3 (scalability).** A greedy approximation to the optimal experimental design (selecting the single pair with highest EIG per round) can match the sample efficiency of exact Bayesian optimal design while costing O(N²) per round instead of O(N³), making it feasible for N ≤ 100 models typical of active leaderboards.

---

## 3. Method

### 3.1 Core Model: Bayesian Bradley-Terry

Each model i has an unknown strength parameter θᵢ ∈ ℝ. The probability that model i beats model j in a comparison is:

```
P(i ≻ j | θᵢ, θⱼ) = σ(θᵢ − θⱼ)    where σ(x) = 1 / (1 + exp(−x))
```

We place independent Gaussian priors θᵢ ~ N(0, σ²₀) with σ₀ = 1.0 (weakly informative). After observing outcomes, the posterior is approximated via **Laplace approximation** (maintaining a diagonal Gaussian N(μᵢ, s²ᵢ) per model), updated incrementally after each comparison.

### 3.2 Acquisition Function: Expected Information Gain (EIG)

Given current posteriors, for each candidate pair (i, j):

1. Compute the predictive probability that i beats j under the current posterior: p̂ = P(i ≻ j | data).
2. For each possible outcome (i wins, j wins), simulate a one-step posterior update via Laplace approximation.
3. Compute the **information gain** as the reduction in posterior entropy summed over all model parameters:

   ```
   IG(outcome) = H(P(θ | data)) − H(P(θ | data ∪ {outcome}))
   ```

   where H ≈ ½ Σₖ log(2π e · s²ₖ) for the diagonal Gaussian.

4. The **expected information gain** for pair (i, j) is:

   ```
   EIG(i, j) = p̂ · IG(i wins) + (1 − p̂) · IG(j wins)
   ```

**Greedy selection rule:** At each round, choose the pair with the highest EIG. Ties broken by picking the pair with highest predictive entropy (most uncertain outcome).

### 3.3 To avoid degenerate exploration

A small auxiliary policy (ε-greedy with ε = 0.1) occasionally selects a random pair to hedge against posterior misspecification.

### 3.4 Practical considerations

- **Streaming models**: When a new model enters, initialize its prior and recompute EIG for all pairs involving it — O(N) per new entry.
- **Batch acquisition**: For Arena-style settings that need to dispatch K comparisons at once, rank EIG scores and take the top-K pairs (with overlap constraints to avoid one model being over-sampled per batch).
- **Stopping criterion**: Stop when the 95% credible interval for each pairwise win probability is narrower than 0.1, or when the top-K ranking is stable over 100 consecutive comparisons.

---

## 4. Dataset / Benchmark

### 4.1 Primary: Simulated ground-truth rankings

We simulate leaderboards with known ground-truth strengths:

| Configuration | N models | Strength distribution | Noise level |
|---|---|---|---|
| **S1: Uniform** | 20 | θᵢ ~ Uniform(−2, 2) | 5% flip |
| **S2: Clustered** | 20 | 4 clusters of 5; within-cluster Δθ = 0.3, between-cluster Δθ = 1.5 | 5% flip |
| **S3: Heavy tail** | 20 | 3 strong (θ ≈ 2), 3 weak (θ ≈ −2), 14 mid (θ ~ N(0, 0.3)) | 10% flip |
| **S4: Large** | 100 | θᵢ ~ N(0, 1.5) | 15% flip |

Each simulation generates ~5,000 ground-truth comparisons (flipping labels at the specified noise rate). Policies draw from this pool; the evaluation measures how many comparisons each policy needs to recover the true ranking.

### 4.2 Secondary: Real pairwise data (Chatbot Arena)

We use the publicly available **LMSYS Chatbot Arena dataset** (∼500k human preferences across ∼50 models, available on Hugging Face). We subsample to create a controlled experiment: treat the full dataset as the "oracle," fix a budget of K comparisons per method, and measure how well each method's inferred ranking matches the ranking from the full dataset (or from the dominant model in the dataset).

### 4.3 Baseline ranking quality

- **Oracle ranking**: From all available data (simulated: ground truth; Arena: full-dataset Elo).
- **Kendall τ** and **Spearman ρ** between inferred and oracle ranking, computed at regular budget intervals.

---

## 5. Evaluation Metrics

| Metric | Rationale |
|---|---|
| **Kendall τ (full ranking)** | Standard rank correlation — primary metric. |
| **Spearman ρ (top-5 / top-10)** | Leaderboards care most about the head of the distribution. |
| **Budget to reach ρ ≥ 0.95** | Practical operational cost; lower is better. |
| **Average precision@K** | How often the inferred top-K matches the oracle top-K. |
| **Regret (dueling bandit sense)** | Cumulative difference in win probability between inferred best model and true best model, per comparison. |
| **Wall-clock acquisition time** | Per-round cost of the acquisition policy (seconds per 100 pairs). |

All metrics reported with 95% confidence intervals across 20 independent seeds (simulation) or 10 bootstrap resamples (Arena data).

---

## 6. Baselines

| Baseline | Description | Rationale for inclusion |
|---|---|---|
| **Uniform random** | Standard practice (Chatbot Arena, Elo). | Primary null baseline. |
| **UCB-style selection (Dueling Bandit)** | Select pairs where one model has high upper-confidence-bound and one has low LCB. | Tests whether bandit UCB logic transfers to LLM ranking. |
| **Pairwise variance maximization** | Select the pair with highest posterior predictive entropy P(i ≻ j) closest to 0.5. | Simple heuristic that captures "uncertainty is informative." |
| **Plackett-Luce with random sampling** | Full ranking (top-1 choice out of K) instead of pairwise. | Tests whether the comparison format matters more than the acquisition strategy. |
| **Random + Thompson Sampling tiebreaker** | Random pair selection, but weighted by posterior variance of the Elo difference. | Ablation to isolate the contribution of targeted selection vs. uncertainty weighting. |

---

## 7. Ablations

| Ablation | What it isolates |
|---|---|
| **EIG → Entropy-only** | Replace full EIG (across all model posteriors) with entropy of the pairwise outcome. Is the global information gain important, or just local uncertainty? |
| **No Laplace (moment-matching)** | Replace Laplace posterior with a mean-field variational approximation. Is approximation accuracy critical? |
| **No ε-greedy exploration** | Remove the 10% random exploration. Does pure EIG collapse into local optima? |
| **Diagonal vs. full covariance Laplace** | Tests whether modeling posterior correlations between models improves pair selection. |
| **Batch size sweep** | K = 1, 5, 10, 50 comparisons per round. How does batching degrade sample efficiency? |

---

## 8. Expected Failure Modes

| Mode | Likelihood | Mitigation |
|---|---|---|
| **EIG collapses to comparing only the top few models** (exploration-exploitation failure) | Medium | ε-greedy exploration; also track per-model comparison counts and add a count-based bonus. |
| **Laplace approximation is too crude for small N** (few comparisons per model) | High early on | Compare against full MCMC (NUTS) for N ≤ 10 models to validate approximation error. |
| **Adaptive policy overfits to simulation noise structure** (does not transfer to real Arena data) | Medium | Validate on Arena data as primary, not just simulation; add noise-mismatch robustness test. |
| **Human preference noise is non-stationary** (model strengths shift as models are updated) | Medium | Implement a sliding-window posterior (last 200 comparisons); evaluate robustness to drift. |
| **Greedy selection is too slow at N=100** (O(N²) EIG computations per round) | Low | Pre-filter candidate pairs: only consider pairs where both models' posterior variances exceed a threshold (top-25% by uncertainty). |
| **Leaderboard stability ≠ ranking accuracy** — the policy may stabilize on an incorrect ranking | Low | Compute coverage: what fraction of all pairs have correctly signed win probabilities at stopping time. |
| **Adaptive comparisons introduce selection bias into Elo scores** | Medium | Compare Elo scores from adaptive vs. random sampling on the same data to detect systematic bias; correct via importance weighting if needed. |

---

## 9. Execution Plan

### Stage 0: Setup & data preparation (Days 1–3)

- Download LMSYS Chatbot Arena dataset from Hugging Face.
- Build the Bradley-Terry simulator with configurable N, θ distribution, and label noise.
- Implement a uniform-random baseline and the metric pipeline (Kendall τ, Spearman ρ, budget curves).
- **Checkpoint**: Reproduce known Elo rankings from the Arena dataset; document as baseline.

### Stage 1: Bayesian posterior engine (Days 4–6)

- Implement Laplace-approximated posterior updates for Bradley-Terry.
- Validate against Pyro NUTS (full MCMC) for N=5, 10, 20 on simulated data. Target: ranking posterior means within 0.1 of MCMC at ≥90% of seeds.
- **Checkpoint**: Basic Elo-style ranking works with uncertainty estimates.

### Stage 2: Adaptive acquisition (Days 7–10)

- Implement EIG acquisition (pair selection + simulated update + entropy reduction).
- Implement all baselines: UCB duel, variance-max, Plackett-Luce, Thompson-weighted random.
- **Test on S1–S3 (small configurations)**: Compare budget-to-ρ≥0.95 across all methods.
- **Checkpoint**: If EIG does not outperform uniform random on S1 (the simplest case), diagnose and iterate before proceeding.

### Stage 3: Full simulation sweep (Days 11–14)

- Run all 6 methods × 4 configurations × 20 seeds.
- Run all 5 ablations.
- Generate budget curves, rank-correlation tables, and compute confidence intervals.
- **Checkpoint**: ≥1 method beats uniform random at p < 0.05 on ≥3 of 4 configurations.

### Stage 4: Real-data validation (Days 15–17)

- Sample K = 500, 1000, 2000, 5000, 10000 comparisons from the Arena dataset for each method.
- Measure rank correlation against the full-dataset ranking (∼500k comparisons).
- Run a paired bootstrap test (N=1000 resamples) to quantify whether the adaptive policy's ranking is significantly closer to the oracle than the random baseline's.
- **Checkpoint**: At least one adaptive method matches full-ranking ρ ≥ 0.95 with ≤60% of the uniform-random comparison budget.

### Stage 5: Analysis & write-up (Days 18–21)

- Produce final tables: budget-to-threshold, rank correlations at all budget levels, ablation comparisons.
- Document failure modes observed and how they were addressed.
- Draft report to `/final_report.md`.
- Open-source code and reproduce instructions.

---

## References (selected)

1. Bradley, R. A., & Terry, M. E. (1952). Rank analysis of incomplete block designs: I. The method of paired comparisons. *Biometrika*, 39(3/4), 324–345.
2. Yue, Y., & Joachims, T. (2009). "Interactively optimizing information retrieval systems as a dueling bandits problem." *ICML*.
3. Zoghi, M., et al. (2014). "Relative upper confidence bound for the K-armed dueling bandit problem." *ICML*.
4. Forestier, M., et al. (2024). "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference." *arXiv:2403.04132*.
5. Zheng, L., et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." *NeurIPS*.
6. Pillutla, V., et al. (2023). "Pragmatic Evaluation of LLMs: A Survey." *arXiv:2310.10326*.
7. Guo, Z., et al. (2024). "A Bayesian Active Learning Approach to LLM Evaluation." *arXiv preprint*.
8. Wirth, C., et al. (2017). "A survey of preference-based reinforcement learning methods." *JMLR*.
9. Bishop, C. M. (2006). *Pattern Recognition and Machine Learning* (Laplace approximation, Ch. 4).
10. Rainforth, T., et al. (2024). "Modern Bayesian Experimental Design." *Statistical Science*, 39(1).

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 19 |
| Topic | Evaluation leaderboards |
| Original user goal | Generate a research proposal on how to construct efficient leaderboards for LLM evaluation. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_19/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_19/final_report.md` (13639 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_19/prompt.txt` (695 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_19/query.json` (157 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_19/stdout.txt` (7967 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_19/stderr.txt` (251 bytes)

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
