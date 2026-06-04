# AToMP-Edge: Adaptive Token-Level Mixed-Precision Quantization for W4A4 LLM Inference on Edge Devices

## 1. Problem

Deploying large language models (LLMs) on edge devices (Jetson Orin, mobile NPUs, Raspberry Pi) requires aggressive quantization to fit within 4–16 GB of memory and meet real-time latency constraints. Weight-only INT4 quantization (W4A16) is the current edge standard — it reduces memory by 4× but gains no compute acceleration because activations remain FP16. To realize both memory and compute savings, **W4A4 quantization (4-bit weights + 4-bit activations)** is needed.

**The core challenge**: Activation outliers — a small fraction of channels with 10–100× larger magnitudes than the median — cause catastrophic accuracy loss at 4-bit activation precision. Existing solutions (QuaRot, InfoQuant, OmniQuant) solve this on server GPUs using Hadamard rotations or learned transformations, but (a) they assume INT4 tensor cores absent from edge hardware, and (b) they apply uniform precision to every token, ignoring that outliers are sparse and token-dependent.

**Key gap**: No prior work has evaluated or optimized W4A4 quantization for real edge hardware, and no method exploits the token-level sparsity of activation outliers to reduce compute cost.

## 2. Hypothesis

Token-level mixed-precision for activations — where a lightweight runtime detector routes outlier tokens to INT8 and typical tokens to INT4 — can match the accuracy of uniform W4A4 methods while maintaining the compute and memory benefits on edge hardware. This is feasible because outlier tokens constitute <1% of all tokens [validated on LLaMA-2/3, Qwen, Gemma in prior work] and are detectable with sub-5μs overhead.

## 3. Method: AToMP-Edge

AToMP-Edge has three components operating at inference time:

### 3.1 Weight Pre-Processing (offline)

Apply AWQ-style activation-aware weight quantization: per-channel INT4 quantization with 1% salient channel protection, using group size g=128. This reduces weight memory by 4× with negligible accuracy loss (validated by Lin et al., MLSys 2024). The weights are stored as INT4 and block-decompressed to INT8 at runtime for computation (since edge hardware lacks native INT4 compute units).

### 3.2 Outlier Detector (lightweight, per-token)

A two-layer MLP (hidden dim 64, ReLU activation, ~2K parameters) that takes as input per-token activation statistics: mean, max, min, and top-5 channel magnitudes of the current token's hidden state (d_model floats, aggregated). It outputs a binary decision: INT4 or INT8 for this token's activations.

**Training**: Calibrate on 128 sequences from WikiText-2. Ground-truth labels are tokens whose INT4 activation error (cosine distance to FP16 activation) exceeds a threshold τ. Train to minimize binary cross-entropy with class-weighting (10:1 for outlier class).

**Inference cost**: ~3–5 μs per token on Jetson Orin CPU core (measured estimate from 2K-param MLP). Adds negligible overhead to the ~1–10 ms per-token decoding time.

### 3.3 Activation Quantization (runtime)

- **INT4 path** (typical tokens, ~99%): Per-token min-max INT4 quantization with per-channel scaling factors. Compute: decompress INT4 weights to INT8 → INT8 × INT4 (via lookup or INT8 widening).
- **INT8 path** (outlier tokens, ~1%): Per-token dynamic INT8 quantization with per-channel scaling. Standard INT8 × INT8 GEMM.
- **Fallback**: If detector confidence is low (<0.6), route to INT8 as a safety margin.

### 3.4 Edge-Optimized Compute Kernel

INT4 weights are block-decompressed (g=128) to INT8 on-the-fly per layer. The INT4-activation path uses a custom kernel that avoids materializing full INT4 tensors: it reads per-token scale factors, scales the weights, and performs INT8 × FP32 widening multiply-accumulate. This is implementable in TensorRT or CoreML custom ops.

## 4. Dataset / Benchmark

### Models (2.6B–8B parameter range, covering small→medium edge-deployable LLMs)

| Model | Parameters | Notes |
|-------|------------|-------|
| LLaMA-3.1-8B | 8B | Strong general-purpose baseline |
| Qwen2.5-7B | 7B | Strong multilingual + reasoning |
| Phi-3-mini-4K | 3.8B | Small, edge-oriented design |
| Gemma-2-2.6B | 2.6B | Lightweight, mobile-friendly |

### Benchmarks

| Benchmark | Metric | What it measures |
|-----------|--------|------------------|
| WikiText-2 | Perplexity (PPL) | Language modeling quality |
| ARC-Challenge | Accuracy | Scientific reasoning |
| MMLU (5-shot) | Accuracy | Multi-task knowledge |
| GSM8K (8-shot) | Accuracy | Math reasoning |
| HellaSwag | Accuracy | Commonsense reasoning |

### Edge Hardware

| Device | Compute | Memory | INT8 Support | Target Use-Case |
|--------|---------|--------|-------------|-----------------|
| Jetson Orin NX 16GB | 1024-core Ampere GPU + 8-core CPU | 16 GB | Yes (TensorRT) | Robotics, drone, local AI |
| Apple M2 (Mac Mini) | 10-core GPU + 16-core Neural Engine | 16–24 GB | Yes (CoreML ANE) | Desktop-edge, local AI apps |
| Raspberry Pi 5 | Broadcom VideoCore VII GPU + 4-core Cortex-A76 | 8 GB | Partial (CPU only) | Low-cost edge, IoT |

## 5. Evaluation Metrics

1. **Accuracy retention**: Perplexity degradation (ΔPPL ≤ 0.5) and task accuracy drop (≤ 2%) vs FP16 baseline.
2. **Latency**: Tokens/second on each edge device. Target: ≥ 80% of W4A16 throughput for AToMP-Edge, ≥ 120% for the INT4-activation-only subset.
3. **Memory**: Peak memory usage during 4K-token generation. Target: ≤ W4A16 memory + 10 MB for detector.
4. **Outlier token ratio**: Percentage of tokens routed to INT8. Success if ≤ 2% across all benchmarks.
5. **Compute-accuracy Pareto frontier**: (tokens/sec) / (accuracy degradation %) — higher is better.

## 6. Baselines

| Baseline | Description | Why it matters |
|----------|-------------|----------------|
| FP16 | Full precision, no quantization | Upper bound on accuracy, lower bound on speed |
| W4A16 (AWQ / GGUF Q4_K_M) | Current edge standard | Compute floor to beat |
| W8A8 (SmoothQuant) | Compute-accelerated baseline | Activation quantization without mixed-precision |
| Uniform W4A8 (OmniQuant) | Fixed W4A8 precision | Ablates the mixed-precision benefit |
| Uniform W4A4 (QuaRot) | Server SOTA W4A4, adapted for edge | Accuracy ceiling for uniform W4A4 |

## 7. Ablations

| Ablation | What it tests | Variants |
|----------|---------------|----------|
| 1. Outlier threshold τ | Sensitivity of detector to classification threshold | τ ∈ {0.01, 0.05, 0.1, 0.5, 1.0} (cosine distance) |
| 2. Detection method | Complexity vs accuracy trade-off | Threshold-based (top-k channel magnitude) vs MLP vs static (no detection, always INT4) |
| 3. Weight quantization | Impact of weight quality | AWQ (g=128) vs GPTQ (g=128) vs RTN (round-to-nearest) |
| 4. Weight group size | Memory / accuracy trade-off | g ∈ {32, 64, 128, 256, 512} |
| 5. Activation quantizer | Non-outlier activation quality | Min-max vs percentile (99.9%) vs BFP4 (block floating point) |

## 8. Expected Failure Modes

1. **Detector overhead exceeds savings**. If outlier token ratio > 5% on some benchmarks (e.g., math reasoning where precise tokens cluster), the detection + INT8 routing overhead may negate compute savings from INT4. *Mitigation*: evaluate outlier ratio per-benchmark; fall back to uniform INT8 mode for outlier-heavy workloads.

2. **Cross-model detector transfer fails**. The detector trained on LLaMA-3.1 may not generalize to Phi-3 or Gemma. *Mitigation*: train per-model detectors; evaluate zero-shot transfer as a bonus experiment.

3. **Worst-case latency spikes**. A burst of consecutive outlier tokens (e.g., during arithmetic) causes intermittent latency spikes. *Mitigation*: measure 95th and 99th percentile latency, not just mean.

4. **INT4 activation error accumulates over long contexts**. Per-token INT4 quantization noise may compound across 4K+ token sequences. *Mitigation*: measure PPL on 8K-context sequences; compare cumulative error drift vs FP16.

5. **Hardware compatibility limits**. Raspberry Pi 5 has no native INT8 GEMM — all compute runs on Cortex-A76 with NEON. *Mitigation*: lower priority for RPi; primary evaluation on Jetson and M2 with INT8 support.

6. **Memory overhead of detector + scaling factors**. Per-token scaling adds ~2 bytes per activation channel. For d_model=4096, that's ~8 KB per token — negligible for batch=1, but could matter for larger batches. *Mitigation*: measure total memory overhead in the 4K-context setting.

## 9. Execution Plan

### Phase 1: Baselines & Infrastructure (Weeks 1–2)

- Set up evaluation harness on Jetson Orin + M2 + RPi 5.
- Implement FP16, W4A16 (AWQ), W8A8 (SmoothQuant) baselines.
- Reproduce QuaRot on server GPU; measure uniform W4A4 accuracy.
- **Success signal**: All baselines running on all 3 edge devices, metrics match published numbers within 5%.

### Phase 2: Outlier Analysis & Detector Training (Weeks 3–4)

- Profile activation outlier distributions across 4 models (WikiText-2 + MMLU subset).
- Train per-model outlier detectors on 128 sequences.
- Measure detector inference latency on each device's CPU.
- **Success signal**: Detector achieves ≥95% precision/recall on held-out calibration set; runs in <5 μs.

### Phase 3: AToMP-Edge Implementation (Weeks 5–6)

- Implement INT4 weight storage + block-decompression kernel.
- Implement INT4 activation path + INT8 activation path with runtime routing.
- Integrate detector into generation loop.
- Benchmark end-to-end latency on Jetson Orin (primary target).
- **Success signal**: End-to-end inference with AToMP-Edge produces correct outputs; latency is ≤ 1.2× W4A16 baseline.

### Phase 4: Full Evaluation (Weeks 7–8)

- Run all benchmarks on all 4 models × 3 edge devices.
- Run all 5 ablations.
- Document failure modes and cross-model generalization.
- Write paper draft with results tables and Pareto plots.
- **Success signal**: At least one model achieves ΔPPL ≤ 1.0 and task accuracy drop ≤ 3% on all benchmarks while using ≤ 2% outlier tokens.

### Contingency: If W4A4 activation quality collapses

If per-token INT4 activation quantization is fundamentally too lossy (even for non-outlier tokens), pivot to **W4A8 with token-level precision reduction** — where typical tokens use INT8 activations and outlier tokens use FP16. This sacrifices compute acceleration but preserves the weight memory savings and provides a controlled comparison of the detection framework.

## 10. Relationship to Prior Work

| Prior Work | What it does | What AToMP-Edge adds |
|------------|-------------|---------------------|
| **SmoothQuant** (Xiao et al., ICML 2023) | W8A8 via activation→weight smoothing | Extends to W4A4 with mixed-precision handling of residual outliers |
| **AWQ** (Lin et al., MLSys 2024) | W4A16 via salient channel protection | Composable: AWQ weight pre-processing + AToMP activation quantization |
| **QuaRot** (Ashkboos et al., NeurIPS 2024) | W4A4KV4 via Hadamard rotation | Removes per-token adaptivity; AToMP exploits outlier sparsity |
| **OmniQuant** (Shao et al., ICLR 2024) | W2-4A4 via learnable clipping + eq. transform | Static per-layer; AToMP is per-token dynamic |
| **Atom** (Zhao et al., MLSys 2024) | W4A4 with mixed-precision + fine-grained groups | Server-focused; AToMP targets real edge hardware |
| **MoBiQuant** (2026) | Recursive residual quantization + token router | Similar spirit but no edge deployment; AToMP focuses on INT4 compute path |
| **MELT-ing point** (Laskaridis et al., 2024) | Systematic edge LLM study (W4A16 only) | Extends to W4A4 + activation quantization on same hardware |

---

*Proposal prepared from: SmoothQuant (ICML 2023), AWQ (MLSys 2024), OmniQuant (ICLR 2024), QuaRot (NeurIPS 2024), Atom (MLSys 2024), MoBiQuant (2026), MELT-ing point (2024), Outlier-Safe Pre-Training (ACL 2025).*

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 09 |
| Topic | Model deployment |
| Original user goal | Generate a research proposal on solving quantization challenges for LLM deployment on edge devices. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_09/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_09/final_report.md` (11892 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_09/prompt.txt` (703 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_09/query.json` (157 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_09/stdout.txt` (8015 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_09/stderr.txt` (251 bytes)

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
