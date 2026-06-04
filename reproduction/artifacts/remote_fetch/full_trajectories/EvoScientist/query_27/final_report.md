# Position-Decontaminated Attention (PDA): Training-Free Mitigation of Position Bias in Long-Context LLMs

**Subproblem selection note**: The query "enhance long-context understanding of Large Language Models" is broad. I have selected one high-impact subproblem — the **positional attention bias** that causes the "lost in the middle" phenomenon — and developed a complete proposal around it.

---

## 1. Problem

Modern LLMs (GPT-4, Claude, Llama 3.1, Mistral) support context windows of 32K–200K tokens, yet their effective utilization of long contexts remains poor. The well-documented **"lost in the middle" phenomenon** (Liu et al., 2023; Shi et al., 2023) shows a U-shaped performance curve: models reliably use information at the beginning and end of long contexts but systematically fail on information placed in the middle. This is not a capacity limitation — it is a **positional bias in the attention mechanism** that causes content-independent over-attention to early and late positions.

### Why this is unsolved
- **Extending context length** (via RoPE scaling, YaRN, NTK-aware) does not fix the per-token utilization problem — it only makes the window *available*, not *usable*.
- **Architectural modifications** (Longformer, BigBird, Sparse Transformers, HAT) require full retraining, which is infeasible for large-scale models.
- **Fine-tuning approaches** (position interpolation, continued pretraining on long sequences) are expensive and model-specific.
- **No existing method** provides a training-free, inference-time correction for this positional attention bias that works across pretrained models.

### Impact
A training-free method that improves mid-context retrieval accuracy by 10–20% on existing models would immediately benefit every downstream application of long-context LLMs — document analysis, code repository understanding, multi-hop reasoning over long passages, and conversational agents with extended history.

---

## 2. Hypothesis

**Primary hypothesis**: The attention distribution in transformer LLMs has a systematic, content-independent positional bias that can be estimated as a per-layer, per-head function of relative position and then **subtracted from attention logits at inference time** to produce a position-decontaminated attention distribution. This correction will improve the model's ability to attend to relevant content regardless of its position in the context.

**Secondary hypothesis**: After position decontamination, the corrected attention scores more accurately reflect content relevance, enabling a lightweight **adaptive context windowing** strategy that allocates fine-grained processing only to context regions with high content-based relevance scores.

---

## 3. Method: Position-Decontaminated Attention (PDA)

PDA is a two-component inference-time system that requires no training or fine-tuning.

### Component A: Position Bias Estimation (offline, one-time)

For a given model with $L$ layers and $H$ heads, we estimate the position bias as follows:

1. **Prepare calibration set**: Collect $N=500$–$1{,}000$ examples where each example is a long document ($\geq$ 8K tokens) followed by a query with the answer embedded at a known position. Answers are placed at uniformly sampled positions across the context. Each example is designed so that content relevance is *independent* of position.

2. **Forward pass collection**: For each calibration example, record the attention weights $a^{(l,h)}_i$ at each layer $l$, head $h$, and source position $i$ (averaged over query token positions and over all calibration examples at that relative position).

3. **Build bias lookup table**: For each $(l, h)$, compute $\hat{b}^{(l,h)}[p]$ = the average attention weight assigned to source position $p$ (normalized for relative positioning). This forms an $L \times H \times C$ table, where $C$ is the calibration context length.

4. **Convert to logit space**: Convert the bias table to logit offsets: $\beta^{(l,h)}[p] = \log(\hat{b}^{(l,h)}[p] / (1 - \hat{b}^{(l,h)}[p]))$ (logit of the bias probability). A smoothing factor handles zero masses.

**Calibration cost**: One forward pass over 1K examples at 8K context length. For Llama 3.1 8B, this takes approximately 1–2 hours on a single A100. Calibration is done once and the table is reused.

### Component B: Inference-Time Logit Adjustment

At inference time, for each attention computation:

1. Compute standard attention logits $s_{ij} = \frac{q_i k_j}{\sqrt{d_k}} + M_{ij}$ (with causal mask $M$).
2. Look up the logit offset $\beta^{(l,h)}[j - i]$ for source position $j$ relative to query $i$ (or absolute position for decoder-only architectures).
3. Compute **position-decontaminated logits**: $s'_{ij} = s_{ij} - \lambda \cdot \beta^{(l,h)}[j - i]$, where $\lambda$ is a scaling hyperparameter controlling correction strength.
4. Apply softmax: $a_{ij} = \exp(s'_{ij}) / \sum_k \exp(s'_{ik})$.

The subtraction removes the content-independent position bias, allowing content-based relevance to dominate the attention distribution.

### Component C: Adaptive Context Window (optional extension)

Using the decontaminated attention scores, we compute a per-region relevance score for each context window by aggregating attention mass in each window region. Regions with low content-based relevance (after bias correction) receive coarser attention (every K-th token), while high-relevance regions receive fine-grained attention. This reduces compute by roughly $2\times$ for long contexts while maintaining or improving performance.

---

## 4. Datasets / Benchmarks

| Benchmark | Task | Context Length | Metric |
|-----------|------|----------------|--------|
| **LongBench** (Bai et al., 2023) | Single-doc QA, multi-doc QA, summarization, few-shot learning | 3K–70K | F1 / ROUGE-L / accuracy |
| **RULER** (Hsieh et al., 2024) | Multi-needle retrieval, variable tracking, chunk finding | 4K–128K | Accuracy per task |
| **L-Eval** (An et al., 2023) | QA, summarization, cloze over long docs | 3K–200K | F1 / ROUGE-L |
| **NarrativeQA** (Kočiský et al., 2018) | QA over full-length books | 50K–200K | F1 |
| **SCROLLS** (Shaham et al., 2022) | QMSum, GovReport, SummScreenFD | 5K–200K | ROUGE / F1 |

**Primary benchmark**: We use the **RULER** multi-needle retrieval task as our primary metric because it directly measures position-dependent retrieval accuracy across the full context window and is the most controlled test of positional bias.

**Secondary benchmark**: LongBench for general long-context understanding across diverse tasks, and L-Eval for stress-testing at maximum context lengths.

---

## 5. Evaluation Metrics

| Metric | Description | Why |
|--------|-------------|-----|
| **Position-stratified accuracy** | Accuracy binned by answer position (start 0–10%, middle 45–55%, end 90–100%) | Directly measures mitigation of "lost in the middle" |
| **Δ(acc_middle − acc_overall)** | Gap between middle-position accuracy and overall accuracy | A single number for position bias strength; lower is better |
| **AUPRC across positions** | Area under the precision-recall curve for retrieval success across all positions | Summarizes performance holistically by position |
| **Task-level F1 / ROUGE-L** | Standard metrics on LongBench and L-Eval | Measures general long-context understanding |
| **Perplexity on long documents** | PPL on held-out long-document test set | Checks for degradation introduced by bias correction |
| **Inference throughput** | Tokens/second (with and without adaptive windowing) | Measures efficiency cost of the method |

---

## 6. Baselines

| Baseline | Description | Why this baseline |
|----------|-------------|-------------------|
| **Unmodified model (Llama 3.1 8B)** | Default inference with no modification | Establishes the untreated position bias |
| **Random position shuffling** | Randomize document order at test time | Upper bound on position-independent performance |
| **Parallel Context Windows (PCW)** (Ratner et al., 2023) | Split context into chunks, attend separately, fuse | Training-free competitor with different tradeoffs |
| **Self-Contrastive Attention** (Sun et al., 2024) | Contrastive attention objective at inference | Recent training- and fine-tuning-free baseline |
| **Positional Interpolation** (PI) (Chen et al., 2023) | Scale RoPE frequencies | Tests whether better position encoding fixes bias |
| **Fine-tuned model (LongLoRA)** | Fine-tune with long-context data via LoRA | Upper bound from the most practical tuning approach |

**Primary baseline**: The unmodified Llama 3.1 8B model run on the same benchmarks. Our target is to close ≥60% of the gap between the unmodified model and the position-shuffled upper bound.

---

## 7. Ablations

| Ablation | What is tested | Expected insight |
|----------|----------------|------------------|
| **No bias correction (only adaptive window)** | Component C alone, without Component B | Whether the windowing alone has any benefit |
| **No adaptive window (only bias correction)** | Component B alone | Is bias correction sufficient for the primary effect? |
| **λ scaling sweep** | Vary correction strength λ ∈ {0.01, 0.05, 0.1, 0.5, 1.0, 2.0} | Optimal correction strength and robustness |
| **Calibration set size** | Vary N ∈ {50, 100, 500, 1000} | How much calibration data is needed? |
| **Head-wise vs layer-wise vs uniform bias** | Apply bias correction at different granularities | Where does position bias originate? |
| **Different base models** | Llama 3.1 8B, Mistral 7B, Qwen2 7B | Model-agnostic vs model-specific |
| **Single-pass vs. chunked inference** | Full context vs chunked with position calibration | Can we trade off latency for accuracy? |

---

## 8. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Mitigation |
|--------------|------------|------------|
| **Bias table captures content covariate, not pure position bias** | Medium | Design calibration set where content is truly position-independent (randomize document order, use synthetic documents) |
| **Correction overly suppresses valid early-position attention** | Medium-High | Use head-specific λ scaling; some heads may genuinely need to attend to early positions for certain tasks |
| **Calibration set does not generalize to different tasks** | Medium | Evaluate cross-task generalization; test on L-Eval tasks never seen in calibration set |
| **Logit subtraction causes numerical instability** | Low | Clamp bias offsets to [-10, 10]; apply softplus normalization |
| **Method benefits RULER (needle tasks) but hurts open-ended generation** | Medium-High | Closely monitor perplexity and open-ended generation quality on LongBench summarization tasks |
| **Adaptive windowing introduces latency overhead** | Low-Medium | Implement as a fused CUDA kernel; the scoring pass is O(n) with a small constant |
| **Position bias patterns differ across context lengths** | Medium | Build separate bias tables for different context length ranges (4K, 8K, 16K, 32K, 64K) and interpolate |
| **Other pre-existing biases (e.g., recency in training data) dominate** | High | PDA only addresses position-induced bias in attention; recency bias from training data distribution needs separate treatment |

---

## 9. Execution Plan

### Stage 1: Calibration Pipeline (Week 1)

1. Select Llama 3.1 8B and Mistral 7B v0.3 as target models (accessible with ~24 GB GPU memory)
2. Build calibration set: 1,000 synthetic long documents (8K tokens each) with queries and answers at uniformly sampled positions
3. Write the forward-pass collection script that records attention weights per layer/head/position
4. Construct the bias lookup tables in logit space
5. **Success signal**: Bias table shows clear U-shape pattern (high weights at position 0–10% and 90–100%, low at 45–55%) that is statistically significant (p < 0.01, permutation test against uniform distribution)

### Stage 2: Core PDA Implementation (Week 2)

1. Implement the inference-time logit adjustment: modify the attention forward pass in HuggingFace `transformers` to read the bias table and apply subtraction
2. Validate on the RULER multi-needle task (controlling for all other variables)
3. Tune λ on a held-out subset of the calibration set
4. **Success signal**: Position-stratified accuracy shows >30% reduction in Δ(acc_middle − acc_overall) vs unmodified model on RULER 8K

### Stage 3: Full Benchmark Suite (Weeks 3–4)

1. Run all baselines on all benchmarks
2. Run the full ablation suite
3. Run with all three models (Llama 3.1 8B, Mistral 7B, Qwen2 7B)
4. **Success signal**: Consistent improvement (p < 0.05 across 3 seeds) on position-stratified accuracy for all models on RULER and LongBench, with <2% perplexity degradation on held-out test

### Stage 4: Adaptive Context Windowing (Week 5)

1. Implement threshold-based adaptive windowing using decontaminated attention scores
2. Measure throughput vs accuracy tradeoff
3. Compare against PCW (Parallel Context Windows) baseline
4. **Success signal**: Adaptive windowing achieves ≥1.5× speedup on contexts ≥32K tokens with <5% relative accuracy drop vs full PDA

### Stage 5: Analysis and Robustness (Week 6)

1. Error analysis: categorize remaining failure cases (position bias vs content complexity vs query ambiguity)
2. Test cross-task generalization (calibrated on RULER, evaluated on L-Eval)
3. Test with different calibration set sizes
4. Write the findings and analysis
5. **Success signal**: Cross-task generalization within <5% of in-task performance; calibration size N=200 achieves >90% of N=1000 benefit

---

## 10. Related Work (References)

- Liu, N. F., et al. (2023). "Lost in the Middle: How Language Models Use Long Contexts." *TMLR*. — Documents the U-shaped performance curve.
- Shi, W., et al. (2023). "Patterns of Position Bias in Transformer Attention." *ACL 2023*. — Analyzes attention-based origin of position bias.
- Hsieh, C.-Y., et al. (2024). "RULER: What Is the Real Context Length of Your LLM?" — Multi-needle benchmark for position-dependent retrieval.
- Ratner, N., et al. (2023). "Parallel Context Windows for Large Language Models." *ACL 2023*. — Training-free context splitting baseline.
- Sun, J., et al. (2024). "Self-Contrastive Attention for Long-Context Understanding." — Contrastive inference-time baseline.
- Chen, S., et al. (2023). "Extending Context Window of Large Language Models via Positional Interpolation." — Position encoding fix baseline.
- Bai, Y., et al. (2023). "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding." — Comprehensive benchmark.
- Xiao, G., et al. (2024). "Efficient Streaming Language Models with Attention Sinks." — Related phenomenon of attention concentration on early tokens.
- An, C., et al. (2023). "L-Eval: Instituting Standardized Evaluation for Long Context Language Models." — Long-context benchmark.
- Kočiský, T., et al. (2018). "The NarrativeQA Reading Comprehension Challenge." — Full-length book QA.
- Shaham, U., et al. (2022). "SCROLLS: Standardized CompaRison Over Long Language Sequences." — Multi-task long-document benchmark.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 27 |
| Topic | Long-context understanding |
| Original user goal | Generate a research proposal on how to enhance the long-context understanding of Large Language Models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_27/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_27/final_report.md` (15229 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_27/prompt.txt` (707 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_27/query.json` (172 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_27/stdout.txt` (9127 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_27/stderr.txt` (251 bytes)

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
