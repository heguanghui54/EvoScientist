# Research Proposal: Selective Pseudo-Labeling with Adapter-Based Fine-Tuning for Extremely Low-Resource ASR

**Subproblem choice**: Low-resource ASR with <2 hours of transcribed speech is a practically important regime (hundreds of endangered and under-documented languages). Current large multilingual models (Whisper, XLS-R) provide strong priors but degrade sharply when available transcribed data is extremely scarce and acoustically or orthographically distant from the training distribution. I focus on the interaction between **parameter-efficient fine-tuning** and **iterative self-training with pseudo-label filtering** — a specific, under-studied regime where the two techniques may interfere or synergize.

---

## 1. Problem

Adapting a large multilingual ASR model (Whisper large-v3) to an extremely low-resource target language — defined as ≤2 hours of transcribed speech. Two issues dominate:

- **Full fine-tuning** collapses on tiny seed data (overfitting, catastrophic forgetting of the multilingual prior).
- **Pseudo-labeling** (self-training on untranscribed target-language audio) generates noisy targets. With extremely limited seed data, errors compound across iterations — standard confidence thresholds fail because the model is confidently wrong on OOD acoustic patterns.

**Gap in the literature**: Adapter-based fine-tuning (LoRA, bottleneck adapters) and pseudo-labeling are each studied separately for low-resource ASR. Their **interaction** is not characterized: Do adapters regularize pseudo-label noise, or do they lack the capacity to learn from self-training? Is there an optimal point where adapter rank and pseudo-label confidence threshold trade off?

## 2. Hypothesis

**Primary hypothesis**: For extremely low-resource ASR (≤2h transcribed), combining **LoRA adaptation** with **length- and confidence-aware pseudo-label filtering** produces lower WER than either full fine-tuning or LoRA alone, because adapters preserve the multilingual prior while the proposed filtering mitigates confirmation bias in self-training.

**Secondary hypothesis**: An optimal LoRA rank exists as a function of seed data size — too low a rank underfits the target language, too high a rank overfits noisy pseudo-labels — and this optimum shifts as pseudo-labeled data accumulates across self-training iterations.

## 3. Method

### 3.1 Base Model

Whisper large-v3 (~1.5B params). Frozen encoder + LoRA-decoder fine-tuning. Rationale: Whisper's encoder is already strong on universal acoustic representations; the decoder maps to the target token set, which is the primary source of language-specific errors.

### 3.2 LoRA Configuration

- **Target modules**: All attention query/value projections in the decoder.
- **Rank sweep**: r ∈ {2, 4, 8, 16, 32} across experiments.
- **α = 2× r**, dropout = 0.1, no bias tuning.

### 3.3 Iterative Self-Training (IST) Pipeline

```
Seed: D_labeled (1-2h)
Pool: D_unlabeled (50-100h target-language audio)
For t = 1..T (T ≤ 5):
  1. Train LoRA model on D_labeled ∪ D_pseudo (t-1)
  2. Generate transcriptions for D_unlabeled (beam=5)
  3. Filter pseudo-labels
  4. Add filtered pseudo-labels to D_pseudo(t)
  5. Evaluate on held-out D_dev
```

### 3.4 Pseudo-Label Filtering (Novel Component)

Standard confidence filtering uses model-assigned log-probability. In extremely low-resource settings, this is unreliable. We propose **Length-Adjusted Confidence with Duration Outlier Detection (LAC-DOD)**:

1. **Length-ratio check**: Compute `len(predicted_text) / len(reference_audio_duration)`. Discard utterances outside [0.5, 3.0] characters/second (a phonetically motivated range).
2. **Duration-aware confidence**: Weight the average log-probability of the predicted tokens by the inverse of the utterance duration: `score = (1/L) Σ log p(y_i|x) · (τ / dur)`, where τ is a reference duration (5s). This penalizes short, easy utterances and rewards correct recognition of longer, harder ones.
3. **Top-k% selection**: Select utterances in the top 30% by LAC-DOD score.

This will be ablated against naive confidence filtering (threshold at 0.8 log-prob) and no filtering (all pseudo-labels accepted).

## 4. Dataset / Benchmark

We target two evaluation scenarios:

| Language | Family | Script | Seed (labeled) | Unlabeled pool | Dev/Test |
|----------|--------|--------|-----------------|----------------|----------|
| **Fongbe** (fon) | Niger-Congo | Latin | 2h (Common Voice) | 80h (Mozilla + YouTube) | 1h each |
| **Uyghur** (uig) | Turkic | Arabic | 1.5h (Common Voice) | 60h (Common Voice unused) | 1h each |

Both are genuinely low-resource with existing open data, have non-English phonotactics, and use different scripts — testing generalization beyond the Indo-European-heavy Whisper training set. Fongbe is tonally contrastive; Uyghur features vowel harmony — both stress Whisper's decoder in different ways.

**Public datasets**: Common Voice 17.0 (for both languages, split into seed/unlabeled pools), supplemented by YouTube audio (Fongbe news broadcasts, preprocessed with Silero VAD at 16 kHz).

## 5. Evaluation Metrics

| Metric | Usage |
|--------|-------|
| **Word Error Rate (WER)** | Primary metric on dev/test |
| **Character Error Rate (CER)** | Secondary metric (handles tonal diacritics more granularly) |
| **Oracle WER** | WER on pseudo-labels vs ground-truth (computed on a 1h held-out subset of the unlabeled pool) — measures pseudo-label quality directly |
| **Confidence-Calibration Gap** | ECE = Σ |accuracy(bin) - confidence(bin)| — measures whether model confidence is trustworthy for filtering |
| **Tone Error Rate (TER)** | For Fongbe: proportion of tonal diacritics misassigned (specific diagnostic) |

All metrics reported with **bootstrapped 95% confidence intervals** (1,000 resamples) and **across 3 seeds**.

## 6. Baselines

| Baseline | Description |
|----------|-------------|
| **B0**: Zero-shot | Whisper large-v3, no fine-tuning |
| **B1**: Full fine-tune | Full Whisper fine-tune on D_labeled |
| **B2**: LoRA only | LoRA (r=8) on D_labeled, no self-training |
| **B3**: Full + naive IST | Full fine-tune + iterative self-training with confidence threshold (0.8) |
| **B4**: LoRA + naive IST | LoRA (r=8) + iterative self-training with confidence threshold (0.8) |
| **B5**: XLS-R + LoRA | wav2vec 2.0 XLS-R (300M) with LoRA decoder + CTC head (model-family ablation) |

Our proposed method (LoRA + LAC-DOD filtering) is compared against all. The strongest incidental baselines are B4 (isolates the filtering contribution) and B5 (tests whether the finding transfers to a different architecture family).

## 7. Ablations

| Ablation | Question Answered |
|----------|-------------------|
| A1: LAC-DOD vs confidence-threshold only vs no filtering | Does the novel filter add value over simpler alternatives? |
| A2: LoRA rank sweep (r=2,4,8,16,32) at fixed seed size | Is there an optimal rank for extremely low resource? |
| A3: Seed size sweep (0.5, 1, 2, 5h) | How does the advantage scale with more seed data? |
| A4: Self-training iterations (T=1,3,5) | When does pseudo-labeling plateau or degrade? |
| A5: LoRA target modules (QKV only vs all linear layers) | Is targeting QKV in the decoder sufficient? |
| A6: Language mismatch — apply same pipeline to Fongbe → Uyghur cross-eval | How much of the result is language-specific vs general? |

Ablations A1 and A2 are the most critical — they directly test the primary and secondary hypotheses.

## 8. Expected Failure Modes

| Failure Mode | Likelihood | Mitigation |
|-------------|------------|------------|
| **Pseudo-labels too noisy even with LAC-DOD** | Medium | Fall back to no self-training; the experiment still produces a valuable comparison of LoRA vs full fine-tune at varying seed sizes |
| **Whisper tokenizer (byte-level BPE) maps tonal diacritics poorly** | Medium-High (Fongbe) | Report CER and tone-specific TER; switch to character-level CTC head as an alternative in the XLS-R baseline (B5) |
| **LoRA adapters underfit target-language phonotactics** | Medium | Sweep higher ranks; if r=32 also underfits, the conclusion is that extremely low-resource ASR requires full fine-tuning with heavy regularization (still publishable) |
| **Results differ between Fongbe and Uyghur** | High (expected) | This is informative — script (Latin vs Arabic) and tonal contrast likely interact differently with Whisper's tokenizer. We treat each as a case study rather than averaging. |
| **Model collapses on first IST iteration (confirmation bias)** | Medium | The LAC-DOD filter is designed specifically to mitigate this. If it fails, the first iteration becomes a data point showing that IST is harmful below a data threshold. |
| **Compute constraints** | Low | LoRA keeps training memory at ~24 GB (single A10G or RTX 3090). Each training run is ~2h on one GPU. Full experiment sweep requires ~60 runs (≈120 GPU-hours). |

## 9. Execution Plan

### Stage 0: Data Preparation (Week 1)
- Download Common Voice 17.0 for Fongbe and Uyghur; partition into seed (2h), dev (1h), test (1h), unlabeled pool (remainder).
- Download/prescreen YouTube audio for Fongbe; run VAD, resample to 16 kHz.
- Verify Whisper tokenizer coverage on both languages (report OOV rate for each).

### Stage 1: Baselines (Week 2)
- Run B0 (zero-shot), B1 (full fine-tune), B2 (LoRA only).
- Tune learning rate, batch size, epochs on D_dev (grid search).
- **Success signal**: All baselines produce stable, reproducible WERs with <5% relative variance across seeds.

### Stage 2: LoRA Rank Sweep (Week 2-3)
- Run A2: r ∈ {2,4,8,16,32} for both languages.
- Identify optimal rank per language.
- **Success signal**: Non-monotonic WER as r increases (i.e., clear optimal rank exists).

### Stage 3: Self-Training Pipeline (Weeks 3-4)
- Implement IST loop + LAC-DOD filter.
- Run B3, B4 (naive IST baselines) and proposed method on both languages.
- Run A1 (filtering ablation), A4 (iteration ablation).
- **Success signal**: Proposed method improves over B4 at T≥2 for at least one language.

### Stage 4: Ablations & Analysis (Week 4-5)
- Run A3 (seed sweep), A5 (target module), A6 (cross-eval).
- Compute calibration gaps, oracle pseudo-label quality.
- **Success signal**: Ablations produce clean monotonic or interpretable patterns.

### Stage 5: Write-Up (Week 5-6)
- Full paper draft with tables, calibration plots, and failure analysis.
- Target venue: Interspeech or ACL (workshop track) — 4–6 page paper.

---

**Total estimated compute**: ~120 GPU-hours (single GPU). All code, configs, and processed data splits will be released as a reproducible benchmark for extremely low-resource ASR adaptation.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 06 |
| Topic | Speech recognition |
| Original user goal | Generate a research proposal on low-resource speech recognition. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_06/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_06/final_report.md` (10720 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_06/prompt.txt` (668 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_06/query.json` (124 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_06/stdout.txt` (7729 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_06/stderr.txt` (251 bytes)

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
