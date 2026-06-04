# UniAudio-MoE: Modality-Aware Mixture-of-Experts for General-Purpose Audio Representation Learning

## Research Proposal

---

## 1. Title

**UniAudio-MoE: Modality-Aware Mixture-of-Experts for General-Purpose Audio Foundation Models**

---

## 2. Problem

General-purpose audio foundation models aim to learn transferable representations from diverse audio — speech, music, and environmental sounds — using a single architecture and training procedure. Despite significant progress, existing approaches fall into two categories, each with a critical limitation:

**Category A — Single-modality specialists.** BEATs (Chen et al., ICML 2022; 596 citations), Whisper (Radford et al., NeurIPS 2023), and MERT (Li et al., ICASSP 2024) each achieve state-of-the-art results within one audio domain but do not generalize to others. Deploying separate models for each domain is costly and misses cross-modal synergies.

**Category B — Uniform-all-audio models.** AST (Gong et al., Interspeech 2021; 1,316 citations), AudioMAE/MAE-AST (Baade et al., Interspeech 2022; 131 citations), and CLAP (Elizalde et al., 2023; 118 citations) process all audio types through identical weights. This forces the model to learn a single set of filters that must simultaneously capture harmonic structure (music), formant transitions (speech), and transient patterns (environmental sounds). Whisper-AT (Gong et al., 2023; 120 citations) demonstrated that a speech-pretrained Whisper can handle sound event tagging, but suffers a 7.6 mAP gap compared to audio-specialist models — confirming that uniform architectures underperform on at least one modality.

**The core problem**: How can a single audio foundation model learn representations that match specialist-level performance *simultaneously* across speech, music, and environmental sound tasks, without requiring separate models, modality-specific heads, or knowledge distillation from multiple teachers?

---

## 3. Hypothesis

A Mixture-of-Experts (MoE) architecture with **modality-aware routing**, trained via a **modality-balanced masked autoencoding** objective, enables a single audio foundation model to match or exceed specialist-level performance across speech, music, and environmental sound.

**Key insight**: Audio modalities differ fundamentally in their signal structure:
- **Speech**: narrowband (0–8 kHz), formant-structured, high temporal resolution needed.
- **Music**: wideband, polyphonic, harmonic stack, long-range periodic dependencies.
- **Environmental**: sparse, transient-heavy, diverse event durations, often non-stationary.

A uniform transformer forces one set of FFN weights to handle all three. MoE allows different "expert" sub-networks to specialize on different modal structures, while **modality-aware routing** ensures the right experts are activated by the right input type — rather than relying on a learned router that may be dominated by a single modality during training.

**Secondary hypothesis**: Explicit modality routing (via a lightweight pre-classifier) outperforms both (a) naive MoE with learned token-level routing and (b) the all-uniform baseline, because it prevents mode collapse where one modality hogs the expert capacity.

---

## 4. Method

### 4.1 Architecture

**Backbone**: Audio Spectrogram Transformer (AST) encoder with ViT-B/16 configuration (12 transformer blocks, 768 hidden dim, 12 heads). Input: log-Mel spectrogram patches (16×16, 1 s window, 160 ms hop). We insert MoE layers in the feed-forward network (FFN) of selected transformer blocks.

**MoE modification** (Figure 1 conceptual sketch):
- Replace the single MLP in every 4th transformer block (blocks 4, 8, 12) with an MoE layer containing **E = 8 experts**, each an independent 2-layer FFN (768 → 2048 → 768, GELU).
- Each expert has the same capacity as a standard AST FFN (≈4.7M params per expert; total MoE ≈37.5M additional params).
- During each forward pass, each token is routed to **top-2 experts** (sparse MoE with k=2), keeping FLOPs comparable to a dense model despite the larger total parameter count.

**Modality-aware router**: Instead of a learned router (which can collapse to using few experts), we use a **two-level routing strategy**:

1. **Global modality classifier**: A lightweight ConvNet (3× Conv2D + GAP + linear, <500K params) takes the raw log-Mel spectrogram and predicts a soft distribution over 3 modalities: {speech, music, environmental}. This classifier is trained jointly from the start with soft labels derived from dataset provenance (e.g., LibriSpeech → speech, FMA → music, AudioSet → environmental).
2. **Modality-grouped experts**: Experts are partitioned into 3 groups — 2 speech experts, 2 music experts, 2 environmental experts, and 2 **shared** experts for cross-modal features.
3. **Token-level routing**: Each token is routed only within the group predicted by the global classifier plus the shared experts. This ensures (a) capacity is reserved for each modality, (b) cross-modal transfer happens through shared experts, and (c) one modality cannot dominate expert allocation.

**Auxiliary load-balancing loss**: A small auxiliary loss (weight α = 0.01) encourages uniform usage across experts within each group, adapted from switch transformer (Fedus et al., 2022).

### 4.2 Pre-Training Objective: Modality-Balanced Masked Autoencoding

We use the MAE objective from AudioMAE (Baade et al., 2022): 75% of spectrogram patches are masked; the encoder processes only visible patches; a lightweight decoder reconstructs the full spectrogram in the time-frequency domain (L2 loss on masked patches).

**Modality balancing**: We construct each training mini-batch to contain **equal numbers of examples from speech, music, and environmental domains** (stratified sampling). This prevents the dominant modality (typically environmental on AudioSet scale) from dictating gradient updates.

**Multi-resolution reconstruction**: To account for different temporal resolutions needed by each modality, we apply the reconstruction loss at 3 spectrogram resolutions (64 mel bins × 128 time, 64×256, 64×512) through lightweight learned down-/up-sampling, borrowed from the multi-resolution loss used in HTS-AT (Chen et al., ICASSP 2022).

### 4.3 Fine-Tuning Protocol

After pre-training, we remove the decoder and attach task-specific linear heads for downstream evaluation. Heads are linear projections of the [CLS] token (or mean-pooling for detection tasks). We follow the standard protocol from AST/BEATs: fine-tune all parameters for 30 epochs with AdamW, cosine LR decay, and early stopping.

---

## 5. Dataset / Benchmark

### 5.1 Pre-Training Data

We construct a **modality-balanced pre-training corpus** by combining three large-scale datasets:

| Modality | Dataset | Size | Sampling | Duration |
|----------|---------|------|----------|----------|
| Speech | LibriSpeech (clean + other) | 2,815 h | Balanced by speaker | 10–30 s utterances |
| Music | FMA-large + MTG-Jamendo | ≈2,200 h | Balanced by genre | 30–60 s clips |
| Environmental | AudioSet (strong + weak) | ≈5,500 h | Balanced by event class | 10–30 s clips |

**Subsampling strategy**: AudioSet's 5,500 h is 2× larger than the other two combined. We randomly subsample AudioSet to match the smallest modality (music, ≈2,200 h) for each epoch, so each epoch has ≈6,600 h total (2,200 h per modality). This prevents the training from being dominated by environmental sounds.

### 5.2 Evaluation Benchmarks

We evaluate on 8 downstream tasks spanning all three modalities:

**Speech tasks:**
1. **Speech Commands V2** (35k, 35-class keyword classification) — accuracy
2. **LibriSpeech test-clean** (automatic speech recognition via CTC head) — WER
3. **VoxCeleb1** (speaker identification, 1,251 classes) — accuracy

**Music tasks:**
4. **GTZAN** (1k, 10-genre classification) — accuracy
5. **MagnaTagATune** (25k, 50-tag multi-label tagging) — ROC-AUC
6. **Music Auto-Tagging on MTG-Jamendo** (55k, 195 tags) — ROC-AUC

**Environmental tasks:**
7. **AudioSet-20K** (20k balanced subset, 527-class tagging) — mAP
8. **ESC-50** (2k, 50-class classification) — accuracy

---

## 6. Evaluation Metrics

| Domain | Task | Primary Metric | Secondary Metric |
|--------|------|----------------|------------------|
| Speech | SCv2 | Top-1 accuracy | — |
| Speech | LibriSpeech | Word Error Rate (WER) | — |
| Speech | VoxCeleb1 | Top-1 accuracy | — |
| Music | GTZAN | Top-1 accuracy | Macro F1 |
| Music | MagnaTagATune | ROC-AUC | mAP |
| Music | MTG-Jamendo | ROC-AUC | mAP |
| Environmental | AudioSet-20K | mAP | d-prime |
| Environmental | ESC-50 | Top-1 accuracy | Macro F1 |

**Aggregate metric**: We compute the **geometric mean of (metric / specialist-baseline)** across all 8 tasks, where specialist-baseline is the best reported single-model score from BEATs (env.), Whisper-base (speech), and MERT (music). A geomean > 1.0 means UniAudio-MoE outperforms specialists on average.

---

## 7. Baselines

We compare against 3 classes of baselines:

### Class 1: Single-modality specialists
- **BEATs** (Chen et al., ICML 2022) — best self-supervised model for general audio tasks.
- **Whisper-base** (Radford et al., NeurIPS 2023) — speech recognition foundation model.
- **MERT** (Li et al., ICASSP 2024) — music understanding foundation model.

### Class 2: Uniform audio foundation models
- **AST** (Gong et al., Interspeech 2021) — pioneer convolution-free audio transformer.
- **AudioMAE / MAE-AST** (Baade et al., Interspeech 2022) — MAE-based audio pre-training.
- **CLAP** (Elizalde et al., 2023) — contrastive language-audio pretraining (zero-shot).
- **HTS-AT** (Chen et al., ICASSP 2022) — hierarchical token-semantic transformer.

### Class 3: Unified audio approaches
- **Whisper-AT** (Gong et al., 2023) — Whisper fine-tuned for joint ASR + tagging.
- **USAD** (Chang et al., 2025) — universal speech and audio via distillation.
- **U-SAM** (Wang et al., 2025) — unified audio LLM via text generation.

**Note on fair comparison**: All baselines are evaluated on exactly the same downstream tasks using the same evaluation scripts. For specialists, we only evaluate on their target domain tasks (e.g., BEATs on ESC-50/AudioSet, not on SCv2). For uniform models, we evaluate on all 8 tasks.

---

## 8. Ablations

### Ablation 1: Routing mechanism
| Variant | Description | Expected gap |
|---------|-------------|-------------|
| UniAudio-MoE (proposed) | Modality-aware routing (global classifier + grouped experts) | — |
| UniAudio-MoE-Learned | Same architecture but learned token-level routing (no modality classifier) | Expect degradation on smaller-modality tasks due to capacity capture |
| UniAudio-MoE-Shared | 8 shared experts, no grouping, learned routing | Expect unbalanced expert utilization |

### Ablation 2: Modality balancing
| Variant | Description | Expected gap |
|---------|-------------|-------------|
| Balanced (proposed) | Stratified batch sampling, 1:1:1 ratio | — |
| Unbalanced-natural | Natural proportions (AudioSet ≈55%, speech ≈28%, music ≈17%) | Expect speech/music degradation |
| Unbalanced-speech | 70% speech, 15% music, 15% env. | Expect music/env degradation |
| Unbalanced-music | 70% music, 15% speech, 15% env. | Expect speech/env degradation |

### Ablation 3: Number of experts
- E = 4 (2 per domain + 1 shared) → insufficient capacity per modality.
- E = 8 (2 per domain + 2 shared, as proposed).
- E = 12 (3 per domain + 3 shared) → diminishing returns expected.

### Ablation 4: MoE layer placement
- Early layers only (blocks 1–4) → may not develop distinct representations.
- Late layers only (blocks 8–12) → may miss opportunity for early specialization.
- All layers (blocks 1–12, every FFN replaced with MoE) → compute cost 3× higher.
- Every 4th layer (proposed: blocks 4, 8, 12) → best trade-off.

### Ablation 5: Pre-training objective
- MAE reconstruction (proposed).
- Contrastive learning (as in CLAP, on paired audio-text data).
- Joint MAE + contrastive (as in CAV-MAE).
- Knowledge distillation (as in USAD, distilling BEATs + MERT + Whisper into one).

---

## 9. Expected Failure Modes

| Failure Mode | Likelihood | Mitigation | Contingency |
|-------------|-----------|------------|-------------|
| **Modality classifier is too easy** (spectrogram features trivially separate speech from music) | Low | Not a problem — classification accuracy simply measures how distinct the modalities are, which is expected | If accuracy is >99%, that's fine — it means the router is reliable |
| **Modality classifier is too hard** (environmental sounds confused with speech/music) | Medium | Use soft routing (weighted combination of modality groups instead of hard assignment) | If soft routing doesn't help, switch to learned token-level routing with a strong load-balancing loss |
| **Shared experts dominate** (all tokens route to shared experts, modality-specific experts underutilized) | Medium | Increase auxiliary load-balancing loss weight (α from 0.01 to 0.1) | Add expert dropout during training to force use of diverse experts |
| **Worse than specialists on all domains** (overall loss in expressivity) | Low | Check whether pre-training was too short (modality-balanced batches are smaller per modality) | Train longer (300 → 600 epochs) with cosine restart |
| **Beats uniform models but not specialists** | Medium (expected on music and speech) | Investigate if expert groups need more capacity (E=12) or domain-specific positional encodings | Add lightweight domain adapters (AdaLoRA) per modality group |
| **Catastrophic forgetting during fine-tuning** (model loses general capabilities when fine-tuned on one task) | Low | Keep the MoE backbone frozen and only fine-tune task-specific heads | Use LoRA fine-tuning on all linear projections |
| **Computing budget is prohibitive** | Medium | Start with a smaller variant (ViT-S, E=4) and demonstrate the same trends before scaling up | Report scaling results from small → base → large to show the trend holds |

---

## 10. Execution Plan

### Phase 0: Infrastructure & Data (Est. 1 week)
- Set up data pipeline: download LibriSpeech, FMA-large, AudioSet (balanced subset), and all evaluation datasets.
- Implement stratified batch sampler for 1:1:1 modality balancing.
- Precompute log-Mel spectrograms (fixed config: 64 mel bands, hop 160, window 1024) for all pre-training data.
- Establish evaluation harness: reproduce AST and BEATs baselines on all 8 tasks.

**Milestone**: All 8 downstream evaluation pipelines run reproducibly. AST/BEATs scores match published results within ±1%.

### Phase 1: Baselines (Est. 1 week)
- Train/reproduce: AST (ViT-B), AudioMAE, HTS-AT from scratch on the balanced pre-training corpus.
- Evaluate all baselines on all 8 tasks.
- Record specialist scores from BEATs, Whisper-base, MERT (published results).

**Milestone**: Baseline performance table with 95% confidence intervals (3 seeds each).

### Phase 2: UniAudio-MoE Construction (Est. 2 weeks)
- Implement MoE transformer blocks (top-2 routing, grouped experts, load-balancing loss).
- Implement lightweight modality classifier (ConvNet) + integrate into routing.
- Train UniAudio-MoE (ViT-B, E=8) with modality-balanced MAE for 300 epochs.

**Milestone**: Pre-training converges with reconstruction loss comparable to AudioMAE baseline. Expert utilization is balanced (Gini coefficient < 0.3 across experts).

### Phase 3: Fine-tuning & Evaluation (Est. 1 week)
- Fine-tune on all 8 downstream tasks (3 seeds each).
- Run all 5 ablation experiments (variants of routing, balancing, E, layer placement, objective).
- Compute aggregate scores and geomean metric.

**Milestone**: Full evaluation table with ablations.

### Phase 4: Analysis & Failure Mode Checks (Est. 1 week)
- Expert specialization analysis: measure which experts fire most on which modalities.
- t-SNE/UMAP visualization of [CLS] tokens per modality (ours vs. AudioMAE).
- Check failure modes: does modality classifier degrade on out-of-distribution audio? Does shared expert collapse happen at higher expert counts?
- Statistical significance tests (paired bootstrap, p < 0.05) for all primary metrics.

**Milestone**: Complete analysis document with figures and statistical tests.

### Phase 5: Writing & Release (Est. 1 week)
- Write paper (8–9 pages, conference format — target ICASSP 2026 or NeurIPS 2026).
- Release code, pre-trained weights, and evaluation scripts.
- Write technical blog post.

**Milestone**: Paper submission.

**Total estimated timeline: 6–7 weeks for a single researcher with 1 GPU (A100 80GB).**

---

## References

1. Gong, Y., Chung, Y-A., Glass, J. (2021). *AST: Audio Spectrogram Transformer*. Interspeech. 1,316 citations.
2. Chen, S., et al. (2022). *BEATs: Audio Pre-Training with Acoustic Tokenizers*. ICML. 596 citations.
3. Chen, K., et al. (2022). *HTS-AT: A Hierarchical Token-Semantic Audio Transformer for Sound Classification and Detection*. ICASSP. 413 citations.
4. Baade, A., Peng, P., Harwath, D. (2022). *MAE-AST: Masked Autoencoding Audio Spectrogram Transformer*. Interspeech. 131 citations.
5. Gong, Y., et al. (2022). *Contrastive Audio-Visual Masked Autoencoder*. ICLR. 187 citations.
6. Gong, Y., Khurana, S., Karlinsky, L., Glass, J. (2023). *Whisper-AT: Noise-Robust ASR Models are also Strong General Audio Event Taggers*. 120 citations.
7. Elizalde, B., Deshmukh, S., Wang, H. (2023). *Natural Language Supervision for General-Purpose Audio Representations*. 118 citations.
8. Chang, H-J., Bhati, S., Glass, J., Liu, A. H. (2025). *USAD: Universal Speech and Audio Representation via Distillation*.
9. Wang, Z., et al. (2025). *U-SAM: An Audio Language Model for Unified Speech, Audio, and Music Understanding*.
10. Lou, Y., Yang, K., You, Y. (2026). *MoST: Mixing Speech and Text with Modality-Aware Mixture of Experts*.
11. Cappellazzo, U., Falavigna, D., Brutti, A. (2024). *Efficient Fine-tuning of Audio Spectrogram Transformers via Soft Mixture of Adapters*.
12. Feng, R., et al. (2025). *Steer-MoE: Efficient Audio-Language Alignment with a Mixture-of-Experts Steering Module*.
13. Fedus, W., Zoph, B., Shazeer, N. (2022). *Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity*. JMLR.
14. Radford, A., et al. (2023). *Robust Speech Recognition via Large-Scale Weak Supervision*. NeurIPS.
15. Li, Y., et al. (2024). *MERT: Acoustic Music Understanding Model with Large-Scale Self-Supervised Training*. ICLR.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 30 |
| Topic | Audio foundation models |
| Original user goal | Help me generate a research proposal on general-purpose audio foundation models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_30/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_30/final_report.md` (18630 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_30/prompt.txt` (684 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_30/query.json` (146 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_30/stdout.txt` (7820 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_30/stderr.txt` (251 bytes)

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
