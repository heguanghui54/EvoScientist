# Research Proposal: DACS — Dynamic Alignment-based Curriculum Selection for Self-Supervised Domain-Specific Data Filtering

---

## 1. Problem

**Setting**: Continued pretraining of a foundation LLM on an uncurated domain corpus (medical texts, legal documents, code, financial reports, etc.).

**Core challenge**: Raw web-crawled domain corpora contain a long tail of low-quality, off-domain, and redundant content. Filtering this data is critical — naive training on unfiltered data degrades downstream task performance (Curió-Edu 7B, Almeida et al., 2025; CoLoR-Filter, Brandfonbrener et al., 2024). Yet existing filtering methods face a trilemma:

| Approach | Representative Work | Limitation |
|---|---|---|
| **Static heuristics** (perplexity, n-gram features) | RefinedWeb (Penedo et al., 2023) | Brittle across domains; ignores model's learning state |
| **Classifier-based** (trained on human labels) | 3DS (Ding et al., 2024, EMNLP) | Requires expensive domain-specific annotations per new domain |
| **Two-model loss comparison** | CoLoR-Filter (Brandfonbrener et al., 2024, NeurIPS); PDPC (Zhang et al., 2025, ACL); DavIR (Zhou et al., 2025) | Requires training/loading a second reference model; doubles compute |
| **External teacher** | SIEVE (Zhang & Nowak, 2024) — GPT-4o as judge; DataChef (Chen et al., 2026) — 32B proxy | API costs; closed models; no adaptation to target model |
| **Influence-based** | MATES (Yu et al., 2024) | O(N × parameters) per step; infeasible for 7B+ models |
| **Compression-based** | ZIP-FIT (Obbad et al., 2024) | Static; single-shot scoring with no online adaptation |

**Subproblem selected (narrowed from the broad query)**: *Dynamic, self-supervised, online data filtering for domain-specific continued pretraining that uses only signals from the model being trained — no auxiliary models, no human labels, no expensive per-sample influence computation.*

## 2. Hypothesis

> **H₁**: During domain-specific continued pretraining, the trajectory of per-example loss reduction combined with the model's internal representation alignment to a small domain seed set provides sufficient signal to dynamically identify and prioritize training examples that yield the largest downstream performance gains — without any auxiliary model or human annotation.

> **H₂**: A curriculum that schedules training data by increasing the domain-relevance and learnability thresholds over time (easy/canonical content first, periphery content later) outperforms static filtering baselines on domain-specific benchmarks.

## 3. Proposed Method: DACS

DACS operates entirely from the model being trained. It has three components that run online during continued pretraining with minimal overhead.

### 3.1 Self-Supervised Domain Relevance Scoring

**Input**: A small seed set of ~200 high-confidence domain documents (e.g., 200 PubMed abstracts for medicine; 200 court rulings for law). These are the only human-provided input and are trivial to obtain (one domain keyword search + 5 minutes of curation).

**Procedure**: At each logging interval (every K optimization steps), we:
1. Run the seed documents through the model and extract the mean hidden state at the final layer's last token position. Denote this as $h_{\text{seed}} \in \mathbb{R}^d$.
2. For each candidate training example $x_i$ in the current batch, extract its final-layer last-token hidden state $h_i$.
3. Compute **domain relevance score** $R(x_i) = \cos(h_i, h_{\text{seed}})$ — cosine similarity to the domain centroid.

**Why this works**: As the model undergoes domain-specific continued pretraining, its hidden representations increasingly align with the target domain (domain adaptation via feature shift). The cosine similarity to seed documents naturally captures how "in-domain" a candidate example is, and this signal *improves* as training progresses — no static classifier needed.

**Computational cost**: One forward pass of 200 seed examples every K steps (~1% of training FLOPs). The per-example hidden state is already computed during the normal forward pass.

### 3.2 Learnability Tracking via Loss Trajectory

**Key insight from prior work**: DavIR (Zhou et al., 2025) showed that the *reducible holdout loss* — how much a training example's loss decreases during training — correlates with data quality. However, DavIR requires a separate holdout set and two training runs. We propose an online approximation.

**Procedure**:
1. Maintain a running per-example loss history $L_i^{(t)}$ for the last $W$ encounters of example $x_i$ (using a hash table keyed by a hash of the text).
2. Compute the **loss reduction rate**: $\Delta_i^{(t)} = L_i^{(t-W)} - L_i^{(t)}$ over the last $W$ times the model saw $x_i$ or a similar example (measured by embedding proximity).
3. Compute the **learnability score**: $S(x_i) = \sigma(\Delta_i^{(t)} - \tau)$ where $\sigma$ is a sigmoid squash and $\tau$ is a running mean of $\Delta$ across all recent examples.

**Intuition**: Examples the model is still learning from (loss decreasing) are valuable. Examples with flat or increasing loss are either already learned (redundant) or noisy (not learnable).

**Computational cost**: O(1) per example with a lightweight hash table. No additional forward passes.

### 3.3 Combined Filtering and Curriculum Scheduling

At each training step $t$, the **DACS weight** for example $x_i$ is:

$$w_i^{(t)} = R(x_i) \cdot S(x_i)$$

where $R$ is domain relevance and $S$ is learnability.

The curriculum scheduler adjusts the acceptance threshold over time:

$$p_{\text{keep}}^{(t)} = \min\left(1.0, \frac{t}{T_{\text{warmup}}} \cdot \alpha_{\text{max}}\right)$$

where $\alpha_{\text{max}}$ is the maximum keep fraction (e.g., 0.5). At each step:
1. Compute $w_i$ for all examples in the current batch.
2. Sort by $w_i$ descending.
3. Keep the top-$p_{\text{keep}}^{(t)}$ fraction.
4. Replace dropped examples with fresh samples from the domain corpus (online resampling).

This creates a natural curriculum:
- **Early stage** (warmup): Wide filtering — keep most data while the model learns basic domain patterns.
- **Middle stage**: Narrower filtering as the model matures; prioritize examples both domain-relevant and still informative.
- **Late stage**: Tight focus on the hardest, most domain-relevant examples.

### 3.4 Addressing Expected Failure Modes

| Failure Mode | Mitigation |
|---|---|
| Seed set is too narrow | Use multiple seed clusters (k-means on seed set) rather than a single centroid |
| Cosine similarity collapses | Normalize by running variance of similarities; use a rank-based score instead of raw cosine |
| Loss trajectory stale (example seen only once) | Cluster examples into semantic buckets; track loss per-bucket |
| Early-stage noise | Warmup period where filtering is wide (high $p_{\text{keep}}$) |
| Domain shift over training (representations drift) | Recompute seed centroid every K steps |

## 4. Datasets and Benchmarks

We evaluate across three domains to demonstrate generality:

| Domain | Dataset | Seed Set | Downstream Benchmarks | Domain Size |
|---|---|---|---|---|
| **Medicine** | PubMed Central + MIMIC-III clinical notes | 200 PubMed abstracts | MedMCQA, PubMedQA, MedQA (USMLE) | ~20B tokens |
| **Legal** | Case law from Caselaw Access Project + Pile legal subset | 200 US Supreme Court opinions | LegalBench subset (17 tasks), CaseHOLD | ~10B tokens |
| **Code** | The Stack (v1.1, filtered) | 200 Python docstrings from stdlib | HumanEval, MBPP, CodeQA | ~15B tokens |

## 5. Baselines

| Baseline | Category | Why this baseline |
|---|---|---|
| **Full corpus** (no filtering) | Lower bound | Shows the cost of unfiltered data |
| **Perplexity filter** (top-50% by PPL) | Static heuristic | Most common real-world baseline |
| **Classifier-based** (tf-idf + logistic regression on seed) | Supervised | Tests benefit of any learning-based filter |
| **ZIP-FIT** (Obbad et al., 2024) | Compression-based static | Strongest static unsupervised baseline |
| **CoLoR-Filter** (Brandfonbrener et al., 2024) | Two-model loss-based | Strongest weak-supervised baseline (uses reference model) |
| **Random subset** (matched token count) | Ablation control | Ensures results aren't from data quantity alone |

## 6. Evaluation Metrics

| Category | Metric | When |
|---|---|---|
| **Primary** | Average downstream task accuracy (averaged across domain tasks) | After continued pretraining |
| **Secondary** | Perplexity on held-out domain text | At checkpoints |
| **Secondary** | Perplexity on general-domain text (WikiText-103) | Monitor for catastrophic forgetting |
| **Efficiency** | Tokens processed to reach target downstream score | Training cost |
| **Ablation** | Agreement rate between DACS scores and human quality ratings (on 500 labeled examples per domain) | Post-hoc analysis |

All downstream metrics reported as mean ± std over 3 random seeds.

## 7. Ablations

| Ablation | What it isolates |
|---|---|
| DACS w/o domain relevance (only learnability $S$) | Value of the representation-based signal |
| DACS w/o learnability (only domain relevance $R$) | Value of the loss-trajectory signal |
| DACS with static threshold (no curriculum) | Value of curriculum scheduling |
| DACS with random seed set (200 random docs) | Sensitivity to seed quality |
| DACS with $p_{\text{keep}} \in \{0.3, 0.5, 0.7\}$ | Sensitivity to keep fraction |

## 8. Expected Failure Modes and Risk Mitigation

| Risk | Likelihood | Mitigation | Fallback |
|---|---|---|---|
| Representation similarity collapses to a narrow cluster | Medium | Use multi-centroid seed representation + diversity penalty | Fall back to PDPC-style perplexity difference without extra model |
| Loss trajectory too noisy for per-example tracking | Medium | Use per-bucket (semantic cluster) tracking instead of per-example | Aggregate into 100 buckets via k-means on embeddings |
| Domain seed set introduces bias | Low-Medium | Report sensitivity to seed set (ablation) and use multi-source seed | Use 3 seed sets from different domain sub-areas |
| DACS underperforms CoLoR-Filter | Medium | If 2-model gap is <1%, the practical advantage (no second model) still justifies DACS. If >2%, analyze whether a lightweight proxy model is needed only at initialization | Warm-start with a single mini-batch per-step loss comparison to calibrate |

## 9. Execution Plan

### Stage 1: Infrastructure and Data Preparation (Week 1-2)
- Download/cache domain corpora (PubMed, Legal, The Stack)
- Construct seed sets (200 docs each)
- Build preprocessing pipeline: tokenization, dedup, hash tables for loss tracking
- Verify data quality with EDA (token distributions, n-gram coverage, domain keyword frequency)

### Stage 2: Baseline Implementation (Week 3-4)
- Implement full-corpus training loop for a 1.3B parameter model (e.g., TinyLlama or Pythia 1.4B)
- Implement all baselines: perplexity filter, classifier-based, ZIP-FIT, CoLoR-Filter, random subset
- Run all baselines on medical domain (smallest dataset for speed)
- **Success signal**: All baselines produce sensible, non-divergent training curves

### Stage 3: DACS Implementation (Week 5-6)
- Implement domain relevance scorer (seed centroid + cosine similarity)
- Implement learnability tracker (hash table + loss trajectory)
- Implement combined filter with curriculum scheduler
- Unit test each component on a 100K-token synthetic corpus
- **Success signal**: DACS produces different per-example rankings than random or PPL-based filters

### Stage 4: Main Experiments (Week 7-10)
- Run DACS vs. all baselines on **medical** domain at 1.3B scale
- Run DACS vs. top-2 baselines on **legal** and **code** domains
- Run DACS at 7B scale (one domain, medical) to test scaling
- **Success signal**: DACS matches or exceeds CoLoR-Filter on average downstream accuracy while using 50% less compute (no second model). DACS outperforms all static baselines.

### Stage 5: Ablations and Analysis (Week 11-12)
- Run all 5 ablations listed in Section 7
- Analyze: which domain examples does DACS select vs. reject vs. baselines?
- Compute agreement with human quality ratings (500 labeled examples)
- Measure forgetting on WikiText-103
- **Success signal**: Ablations confirm that both $R$ and $S$ components contribute. Curriculum scheduling provides >2% improvement over static threshold.

### Stage 6: Analysis, Write-up, and Release (Week 13-14)
- Statistical testing (paired bootstrap across seeds)
- Write paper: introduction → method → experiments → analysis → related work
- Release code and filtered datasets
- **Success signal**: Paper ready for submission to ACL Rolling Review or NeurIPS 2026 Datasets & Benchmarks track.

## 10. Statement of Contribution

If successful, this work would make the following contributions:

1. **Method**: DACS, the first fully self-supervised, online data filtering method for domain-specific continued pretraining that requires no auxiliary model or human annotation beyond a trivial seed set.
2. **Empirical finding**: The first systematic comparison of loss-trajectory vs. representation-alignment vs. combined signals for domain data filtering at scale.
3. **Benchmark**: Open-source, reproducible evaluation of 6 filtering strategies across 3 domains at 1.3B and 7B scales.
4. **Practical impact**: An off-the-shelf data curation pipeline deployable on any domain corpus in under 1 hour (the time to gather 200 seed documents).

## 11. Related Work (Condensed)

- **Data selection surveys**: Albalak et al. (2024) — "A Survey on Data Selection for Language Models"; Wang et al. (2023) — "Data Management for Training Large Language Models"
- **Loss-based selection**: CoLoR-Filter (Brandfonbrener et al., 2024, NeurIPS); PDPC / Preference Curriculum (Zhang et al., 2025, ACL); DavIR (Zhou et al., 2025, ACL); Reducible Holdout Loss (Mindermann et al., 2022)
- **Model-centric difficulty selection**: 3DS (Ding et al., 2024, EMNLP) — for domain-specific SFT, not continued pretraining
- **Compression-based data selection**: ZIP-FIT (Obbad et al., 2024)
- **Curriculum learning for domain adaptation**: Zhang et al. (2019) — curriculum learning for NMT domain adaptation; Iter & Grangier (2021) — complementarity of selection and fine-tuning
- **Domain adaptive pretraining**: Gururangan et al. (2020) — DAPT; Kerner (2024) — domain-specific pretraining comparisons; Almeida et al. (2025) — data selection impacts in continued pretraining
- **Quality-diversity balancing**: QuaDMix (Liu et al., 2025); SampleMix (Xi et al., 2025); GRAPE (Fan et al., 2025)
- **Influence-based selection**: MATES (Yu et al., 2024); Li et al. (2024) — do influence functions work on LLMs?; Bao et al. (2025) — scalable multi-stage influence
- **Optimal control approaches**: PDS (Gu et al., 2024, ICLR)
- **Distilled teacher filtering**: SIEVE (Zhang & Nowak, 2024); DataChef (Chen et al., 2026)

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 26 |
| Topic | Data filtering |
| Original user goal | Generate a research proposal on solving data filtering challenges for domain-specific models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_26/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_26/final_report.md` (14949 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_26/prompt.txt` (697 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_26/query.json` (150 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_26/stdout.txt` (11011 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_26/stderr.txt` (251 bytes)

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
