# Decoding the Capability Graph: Causal Decomposition of Knowledge, Reasoning, and Code Generation in LLMs

---

## 1. Title

**Decoding the Capability Graph: Causal Decomposition of Knowledge, Reasoning, and Code Generation in Large Language Models**

---

## 2. Problem

Large language models exhibit a wide range of capabilities — factual knowledge recall, compositional reasoning, code generation, instruction following, and more — within a single set of weights. This raises a fundamental scientific question:

> **To what degree are these capabilities supported by shared vs. independent mechanisms?**

The question has high practical stakes: if capabilities are deeply entangled, then improving one (e.g., reasoning via chain-of-thought fine-tuning) will unavoidably degrade others (the "alignment tax" problem). If they are dissociable, we can build modular systems, perform surgical capability editing, and design training pipelines that avoid interference.

Despite extensive study of individual capabilities in isolation, we lack a **unified, causal framework** for measuring capability (in)dependence in LLMs. Existing work falls into separate silos: task arithmetic shows that fine-tuning updates for different tasks can be added/subtracted (Ilharco et al., 2022), causal tracing localizes factual recall to specific layers (Meng et al., 2022; Geva et al., 2023), skill neurons suggest sparse functional specialization (Wang et al., 2022), and the superficial alignment hypothesis posits a deep dissociation between pretrained capabilities and alignment-induced behaviors (Zhou et al., 2023). No study has systematically triangulated these perspectives to produce a quantitative "capability decomposition" of a single model.

**Specific subproblem**: We narrow the broad question of "capability decoupling" to three well-defined, high-impact capabilities:
- **Factual Knowledge** — retrieving world facts from parametric memory
- **Compositional Reasoning** — multi-step deduction and mathematical problem-solving
- **Code Generation** — producing syntactically and semantically correct programs

These three are selected because (a) they are ecologically important for deployed LLMs, (b) prior work suggests they may have distinct mechanistic substrates (knowledge in mid-layer MLPs, reasoning across attention+MLP circuits, code in pattern-matching structures), and (c) they can be cleanly benchmarked.

---

## 3. Hypothesis

We propose three converging hypotheses:

- **H1 (Parameter-Level Dissociability)**: Fine-tuning for each capability produces task vectors $\Delta\theta_A$ that are approximately orthogonal (low cosine similarity) to those for other capabilities. Task vector addition preserves individual capabilities, while subtraction selectively removes the target capability with minimal collateral degradation.

- **H2 (Circuit-Level Dissociability)**: The causally important layers for each capability are partially disjoint. Cross-capability activation patching (running the model on task A while injecting hidden states from task B at critical layers) will disrupt performance only when the injected activation originates from overlapping circuit regions.

- **H3 (Asymmetric Entanglement)**: Certain capability pairs are more entangled than others. Specifically, compositional reasoning and code generation share more mechanistic overlap (both involve formal rule-following and structured output generation) than either shares with factual knowledge retrieval.

The null hypothesis for each is complete entanglement: all capabilities rely on substantially the same parameters and circuits, such that any intervention targeting one capability non-selectively affects all others.

---

## 4. Method

We propose three converging experimental blocks, designed so that each provides independent evidence and the three together triangulate on the same ground truth.

### Block A: Task Vector Orthogonality and Merging Analysis

**Rationale**: If fine-tuning for capability A and B produces task vectors $\Delta\theta_A$ and $\Delta\theta_B$ that are near-orthogonal and additively composable, this provides strong evidence for parameter-level dissociability.

**Procedure**:
1. Starting from a single base model (Llama-3-8B), train separate LoRA adapters (rank=32) for each of three capability domains:
   - **Knowledge**: MMLU subset (all categories), PopQA, TruthfulQA training set
   - **Reasoning**: GSM8K training set, LogiQA, BIG-Bench Hard subtasks
   - **Code**: MBPP training set, CodeContests, APPS introductory
2. Extract task vectors: $\Delta\theta_A = \theta_{A} - \theta_{base}$, $\Delta\theta_B = \theta_{B} - \theta_{base}$
3. Compute pairwise cosine similarities: $\text{sim}(\Delta\theta_A, \Delta\theta_B)$ for each pair
4. Test additive composition: evaluate $\theta_{base} + \Delta\theta_A + \Delta\theta_B$ on both capabilities
5. Test selective removal: evaluate $\theta_{base} + \Delta\theta_A - \Delta\theta_B$ and verify that capability B degrades while capability A is preserved
6. Apply DARE pruning (randomly drop 90% of delta parameters and rescale) to measure sparsity of the "capability signal" in each task vector

**Outputs**: Cosine similarity matrix (3×3), per-capability accuracy under addition/subtraction, sparsity curves.

### Block B: Cross-Capability Causal Tracing

**Rationale**: While Block A operates at the parameter level, Block B localizes *where information for each capability flows* through the model during inference.

**Procedure**:
1. For each capability domain, construct 200 prompts that test that capability:
   - **Knowledge**: "The capital of [country] is" (clean factual recall)
   - **Reasoning**: "If [premise], then [conclusion]?" (multi-step deduction)
   - **Code**: "Write a function to [specification]" (code synthesis)
2. Apply mean-corrupted causal tracing (following Meng et al., 2022):
   - Corrupt the input (mask subject tokens / shuffle)
   - Restore hidden states from the clean run at each (layer, token position) individually
   - Measure how much restoration recovers the correct output probability
3. For each capability, produce a **causal importance map**: a matrix $C \in \mathbb{R}^{L \times T}$ where $C_{l,t}$ is the probability gain from restoring layer $l$ at position $t$
4. Compute **pairwise map overlap**:
   - Jaccard similarity of top-$k$ critical layers ($k=5, 10, 20$)
   - Pearson correlation of flattened importance vectors
5. **Activation patching experiment**: For capability pairs (A, B), run the model on a prompt for A but patch in hidden states from the B inference at the top-3 most important layers for B. Measure whether A's performance degrades.

**Outputs**: Causal importance maps (3 capabilities × 32 layers), pairwise Jaccard overlap scores, activation patching interference table.

### Block C: Surgical Capability Ablation via Negated Task Vectors

**Rationale**: The most stringent test of independence: can we remove one capability while leaving others intact?

**Procedure**:
1. Construct ablated models: $\theta_{\text{abolished}_A} = \theta_{base} - \alpha \cdot \Delta\theta_A$ for $\alpha \in \{0.5, 1.0, 1.5, 2.0\}$
2. Evaluate all ablated models on the full benchmark suite (all 10+ benchmarks spanning all three capabilities plus the control tasks)
3. Compute an **Asymmetric Interference Index** for each pair:
   $$ I_{A \to B} = \frac{\text{Δperf}_B}{\text{Δperf}_A} $$
   where Δperf is the change relative to base model. If $I_{A \to B} \approx 0$, capability A can be ablated without affecting B.
4. Repeat for all 3 capabilities at the target ablation strength

**Outputs**: Ablation curves for each capability, full interference matrix, asymmetric interference indices.

---

## 5. Dataset / Benchmark

We construct a unified evaluation suite covering three capability domains plus control tasks:

| Domain | Benchmark | Metric | # Examples | Source |
|--------|-----------|--------|------------|--------|
| **Knowledge** | MMLU (all 57 subjects) | Accuracy | 14,042 | Hendrycks et al., 2021 |
| **Knowledge** | PopQA | Accuracy (F1) | 14,267 | Mallen et al., 2023 |
| **Knowledge** | TruthfulQA | MC1 accuracy | 817 | Lin et al., 2022 |
| **Reasoning** | GSM8K | Exact match | 1,319 | Cobbe et al., 2021 |
| **Reasoning** | LogiQA | Accuracy | 651 | Liu et al., 2020 |
| **Reasoning** | BIG-Bench Hard (selected reasoning tasks) | Accuracy | ~2,500 | Suzgun et al., 2022 |
| **Code** | HumanEval | Pass@1 | 164 | Chen et al., 2021 |
| **Code** | MBPP | Pass@1 | 500 | Austin et al., 2021 |
| **Control** | HellaSwag | Accuracy | 10,042 | Zellers et al., 2019 |
| **Control** | BBH (selected non-reasoning tasks) | Accuracy | ~2,000 | Suzgun et al., 2022 |

**Training data** for LoRA fine-tuning (Block A and C): subsets of the training splits of MMLU, GSM8K, and MBPP — filtered to 10K examples per capability to ensure equal training budget.

**Why these benchmarks**: MMLU tests broad factual knowledge, GSM8K tests multi-step mathematical reasoning (which requires compositional thinking), HumanEval tests code correctness in a zero-shot setting, and HellaSwag serves as a control (commonsense inference) that does not cleanly belong to any of the three target capabilities.

---

## 6. Evaluation Metrics

| Category | Metric | What It Measures |
|----------|--------|-----------------|
| **Behavioral** | Per-benchmark accuracy / Pass@1 | Standard capability measurement |
| **Parameter-level** | Cosine similarity of task vectors | How aligned are fine-tuning updates? |
| **Parameter-level** | Task vector norm ratio ($\|\Delta\theta_A\| / \|\theta_{base}\|$) | How much does fine-tuning change the model? |
| **Parameter-level** | Composition accuracy = accuracy($\theta_{base}+\Delta\theta_A+\Delta\theta_B$) | Do task vectors compose additively? |
| **Causal** | Jaccard($top_k$ critical layers) | Do the same layers drive both capabilities? |
| **Causal** | Activation patching disruption (Δprob when patching B into A) | Do B's critical regions interfere with A? |
| **Ablation** | $I_{A \to B}$ (asymmetric interference index) | How much does ablating A harm B? |
| **Ablation** | Ablation dose-response curve | Is the effect of ablation monotonic? |

**Statistical rigor**: All metrics reported with 95% confidence intervals (bootstrapped, 1000 resamples). All fine-tuning runs repeated with 3 random seeds. Multiple-testing correction (Bonferroni) applied when comparing across all capability pairs.

---

## 7. Baselines

| Baseline | Rationale | Expected Behavior Under Null (Full Entanglement) |
|----------|-----------|--------------------------------------------------|
| **Random perturbation** | Apply random parameter perturbation with norm matched to $\|\Delta\theta_A\|$. Controls for the possibility that any perturbation degrades performance non-selectively. | All capabilities degrade equally. |
| **Multi-task fine-tuning** | Fine-tune on all three capability domains jointly. Tests whether joint training produces interference dynamics different from composition of independent vectors. | Joint performance is the sum of individual performances (no interference). |
| **SFT-only checkpoint** | Evaluate the SFT checkpoint before any capability-specific fine-tuning. Tests the superficial alignment hypothesis prediction that SFT teaches format, not content. | No difference between base and SFT on capability benchmarks. |
| **Layer-randomized ablation** | Instead of subtracting $\Delta\theta_A$, subtract a random set of parameters with same norm. Controls for the specificity of the task vector direction. | Same degradation pattern as $\theta_{base} - \Delta\theta_A$. |

---

## 8. Ablations

| Ablation | Variable | Levels | Purpose |
|----------|----------|--------|---------|
| **Model scale** | Base model size | Llama-3.2-1B, Llama-3-8B, Llama-3-70B | Test whether capability dissociability changes with scale (does interference increase or decrease?) |
| **LoRA rank** | LoRA rank for task vectors | 8, 32, 128 | Test whether task vector structure depends on expressivity of the adapter |
| **Training data size** | Examples per capability | 1K, 10K, 50K | Test whether capability-specific fine-tuning becomes more or less selective with more data |
| **Capability pairing** | Which pairs are compared | knowledge vs reasoning, reasoning vs code, knowledge vs code, all vs control (HellaSwag) | Test H3 (asymmetric entanglement — code and reasoning may be more entangled than knowledge and reasoning) |
| **Ablation coefficient α** | Strength of ablation | 0.5, 1.0, 1.5, 2.0 | Test whether capability removal is dose-response or threshold-based |

---

## 9. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Severity | Mitigation |
|-------------|------------|----------|------------|
| **Task vectors are near-random (high cosine similarity across all pairs)** | Medium | High | If all task vectors point in similar directions, the fine-tuning may not be capability-specific. Mitigation: use stronger training signals (more data, higher LoRA rank, contrastive fine-tuning that explicitly penalizes cross-capability interference). |
| **Causal importance maps are identical across capabilities** | Low-Medium | High | If all capabilities depend on the same layers (e.g., late layers for output generation), the maps will have high overlap from output projection alone. Mitigation: subtract the output-projection baseline from importance maps; report both raw and baseline-subtracted overlaps. |
| **Negated task vectors produce degenerate models (loss diverges)** | Medium | Medium | Subtracting a large task vector may push the model into a pathological region of parameter space. Mitigation: sweep α from 0 to 2.0; report the maximum α before degeneration (unstable loss or gibberish output as detected by perplexity > 3× baseline). |
| **Benchmarks are insufficiently capability-pure (e.g., GSM8K tests both knowledge and reasoning)** | High | Medium | No benchmark is perfectly pure. Mitigation: compute pairwise benchmark correlation matrices; use factor analysis to identify latent capability dimensions; report results both at the "raw benchmark" level and the "latent factor" level. |
| **LoRA fine-tuning is too small to produce measurable capability improvement** | Low-Medium | High | 10K examples may be insufficient for some capabilities. Mitigation: if Block A training produces <5% improvement on the target benchmark, increase to 50K examples or switch to full fine-tuning with LoRA as a fallback analysis. |
| **Activation patching shows widespread effects (patching anything degrades everything)** | Medium | Medium | If model components are highly interconnected, any intervention may have global effects. Mitigation: use correlated ablation (patch entire contiguous layer blocks) to see if degradation is layer-specific; compare to a "sham patching" baseline (patch in activations from a different random input on the same task). |
| **Large model (70B) is too expensive for full causal tracing** | Certain | Low | Causal tracing on 70B requires 2-3 forward passes per prompt × 32 layers × 200 prompts ≈ 12,800 passes. Mitigation: for 70B, reduce to 100 prompts and 16 sampled layers; confirm that conclusions at 8B and 70B are consistent. |

---

## 10. Execution Plan

### Phase 0: Setup (Week 1)

| Task | Artifact |
|------|----------|
| Select and download base models (Llama-3.2-1B, Llama-3-8B, Llama-3-70B) | `/models/` |
| Curate training subsets (10K per capability, deduplicated from train splits) | `/data/knowledge_train.json`, `/data/reasoning_train.json`, `/data/code_train.json` |
| Curate evaluation suite (all 10 benchmarks, validation/test splits) | `/data/eval_suite.json` |
| Set up evaluation harness (lm-eval-harness or custom framework) | `/scripts/evaluate.py` |
| Run initial baseline evaluations on all base models | `/results/baselines.json` |

### Phase 1: Task Vector Analysis (Weeks 2-3)

| Task | Artifact |
|------|----------|
| Train 3 LoRA adapters per model (knowledge, reasoning, code) × 3 seeds | `/adapters/{model}/{capability}/seed_{n}/` |
| Compute task vectors and pairwise cosine similarities | `/results/task_vectors/` |
| Compute composition and ablation evaluations | `/results/composition/` |
| Run DARE pruning at sparsity levels 50%, 90%, 99% | `/results/dare/` |

**Go/no-go**: If $\max(\cos(\Delta\theta_A, \Delta\theta_B)) > 0.95$ across all pairs, the task vectors are degenerate. Switch to full fine-tuning or contrastive training. Otherwise proceed.

### Phase 2: Causal Tracing (Weeks 4-5)

| Task | Artifact |
|------|----------|
| Implement causal tracing with mean corruption | `/scripts/causal_trace.py` |
| Generate 200 capability-specific prompts per domain | `/data/causal_prompts/` |
| Run causal tracing for each capability (Batch: 8B first, then 1B, skip 70B) | `/results/causal_maps/` |
| Compute pairwise Jaccard overlaps and correlation | `/results/causal_overlap.json` |
| Run activation patching experiments for top-3 layers per pair | `/results/patching/` |

### Phase 3: Surgical Ablation (Week 6)

| Task | Artifact |
|------|----------|
| Compute ablated model evals for α ∈ {0.5, 1.0, 1.5, 2.0} | `/results/ablation/` |
| Compute Asymmetric Interference Index for all pairs | `/results/interference_matrix.json` |
| Run baselines (random perturbation, multi-task, layer-randomized) | `/results/baselines_ablation.json` |

### Phase 4: Ablations and Robustness (Weeks 7-8)

| Task | Artifact |
|------|----------|
| Scale ablation: repeat Blocks 1-3 on Llama-3.2-1B | `/results/scale_ablation/` |
| Rank ablation: repeat Block 1 with LoRA rank 8 and 128 on 8B | `/results/rank_ablation/` |
| Data size ablation: repeat Block 1 with 1K and 50K examples | `/results/data_ablation/` |
| Stability: verify all conclusions on Llama-3-8B across 3 seeds | `/results/stability/` |

### Phase 5: Analysis and Write-up (Weeks 9-10)

| Task | Artifact |
|------|----------|
| Synthesize findings across all three blocks | `/results/synthesis.pdf` |
| Generate figures: task vector similarity heatmap, causal importance maps, ablation curves | `/figures/` |
| Draft paper (NeurIPS / ICML / ICLR format) | `/paper/` |
| Run final statistical checks (bootstrapped CIs, multiple testing correction) | `/paper/supplement/` |

### Resource Requirements

- **Compute**: ~25 A100-80GB GPU-hours for 8B (3 LoRAs × 3 seeds + causal tracing + ablations), ~200 GPU-hours for 70B. Total: ~50-300 GPU-hours depending on 70B scope.
- **Storage**: ~100 GB for model weights and adapters, ~10 GB for results.
- **All models and data are open-source** (Llama-3, Pile, MMLU, GSM8K, MBPP, HumanEval).

---

## 11. Expected Contributions

1. **First systematic capability decomposition of an LLM** using three converging causal methodologies (task vector analysis, causal tracing, surgical ablation) rather than any single approach.

2. **Quantitative capability (in)dependence metrics**: cosine similarity of task vectors, Jaccard overlap of causal maps, asymmetric interference index — a reusable toolkit for the field.

3. **Test of the "capability modularity" hypothesis**: if confirmed, this supports the feasibility of modular model design, targeted capability editing, and interference-free multi-task fine-tuning. If rejected, it suggests fundamental limits on how independently we can manipulate LLM capabilities.

4. **Empirical map of which capability pairs are most entangled**, enabling informed decisions about which combinations can be safely fine-tuned together vs. require isolation.

5. **Ablation experiments across model scale** (1B, 8B, 70B) testing whether larger models exhibit more or less capability decoupling — a question with direct implications for how we train and modify frontier models.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 11 |
| Topic | LLM capabilities |
| Original user goal | Generate a research proposal on the decoupling of Large Language Model capabilities. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_11/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_11/final_report.md` (19843 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_11/prompt.txt` (688 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_11/query.json` (143 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_11/stdout.txt` (10446 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_11/stderr.txt` (251 bytes)

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
