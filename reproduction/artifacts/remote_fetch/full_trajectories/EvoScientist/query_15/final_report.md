# Research Proposal: Context-Adaptive Gender Debiasing (CAGED) for Neural Machine Translation

---

## Choice of subproblem

The query asks about "debiasing in machine translation" — a broad area covering gender, political, religious, and dialect bias. I focus on **gender bias in neural machine translation (NMT)**, the most documented and benchmarked debiasing problem in MT. Within that, I target a specific gap: **existing methods treat all sentences uniformly, applying debiasing pressure regardless of whether the source context actually resolves a person's gender.**

---

## 1. Problem

Neural machine translation systems produce stereotyped gender translations even when the source context disambiguates gender. For example:

| Source (English) | Correct (resolved from context) | NMT output (stereotyped) |
|---|---|---|
| *"My sister, the doctor, arrived."* | "Ma sœur, la docteure, est arrivée." | "Ma sœur, le docteur, est arrivé." |
| *"The nurse — he was exhausted — sat down."* | "L'infirmier, épuisé, s'est assis." | "L'infirmière, épuisée, s'est assise." |

Conversely, when the source is genuinely ambiguous (e.g., *"The doctor arrived"* with no prior context), current debiasing methods often **force a binary gender choice**, introducing information absent in the source and degrading translation quality by ~1–2 BLEU points (Saunders & Byrne, 2020).

**Core tension**: Stronger debiasing reduces stereotyped errors on disambiguated cases but increases over-correction errors on genuinely ambiguous cases. Weaker debiasing has the opposite problem. Current approaches apply a single, uniform debiasing strength globally, creating an unavoidable trade-off.

**Key insight**: The optimal debiasing strength at inference depends on whether the source context *actually resolves* the entity's gender — information that the MT model itself has but current debiasing methods do not exploit.

---

## 2. Hypothesis

> **We can improve both bias reduction *and* translation quality by conditioning debiasing strength on a per-entity ambiguity score derived from document-level context, instead of applying uniform debiasing pressure across all sentences.**

Concretely:
- **H₁**: A model fine-tuned with ambiguity-adaptive regularization will achieve lower gender bias (measured on WinoMT) than both an unregularized baseline and a uniformly-regularized baseline, at the same BLEU.
- **H₂**: On genuinely ambiguous sentences, the adaptive model will preserve higher translation quality than a uniformly-regularized model, because it does not force stereotyped gender choices when context is insufficient.
- **H₃**: The ambiguity estimator can be a lightweight classifier (≤200M parameters) that does not require expensive coreference annotations at inference — only the source text with document boundaries.

---

## 3. Method: Context-Adaptive Gender Debiasing (CAGED)

CAGED has two components:

### 3.1 Ambiguity Estimator

A lightweight, language-agnostic classifier that outputs a **per-entity ambiguity score** *a ∈ [0, 1]* for each gender-ambiguous slot in the source sentence.

**Input**: Source sentence *s* with *N* preceding sentences of document context *d* (truncated at 512 BPE tokens).
**Output**: For each entity mention *e* in *s* that maps to a gender-inflected slot in the target language (identified via a target-side morphological analyzer), a score *a(e) ∈ [0,1]*.

**Architecture**: mBERT-based sentence-pair classifier (sequence length ≤ 512). The [CLS] representation is fed to a 2-layer MLP with a sigmoid output. Training data is automatically generated from existing parallel corpora with gold coreference annotations (OntoNotes, WikiCoref) by:

1. Identifying gender-resolvable entities (pronoun links, kinship terms + gender-stereotyped occupations where coreference resolves to a gendered antecedent)
2. Labeling them *a=0* (resolved)
3. Sampling synthetic ambiguous cases by stripping gendered antecedents — label *a=1* (ambiguous)

**Inference cost**: ~5ms per sentence on a single GPU — negligible relative to MT decoding.

### 3.2 Gender-Adaptive Fine-Tuning

Fine-tune a pretrained NMT model with an augmented loss:

```
L_total = L_NLL + λ · L_gender

L_gender = Σ_{e ∈ entities(s)} (1 - a(e)) · CE(p_gender(e), g_target(e))
```

Where:
- **L_NLL**: Standard cross-entropy loss (next-token prediction on target side).
- **λ**: A scalar controlling overall regularization strength (tuned on a validation set).
- **a(e)**: Ambiguity score from §3.1. When *a(e) ≈ 0* (gender fully resolved from context), the gender loss fires strongly. When *a(e) ≈ 1* (fully ambiguous), the gender loss is suppressed to near-zero.
- **CE(p_gender(e), g_target(e))**: Cross-entropy between the model's predicted distribution over gender-marked tokens for entity *e* and the correct gender form *g_target*. The gender target is extracted from the reference translation's morphological analysis — automatically obtained without additional annotation.

**Training recipe**:
- Start from a pretrained NMT checkpoint (e.g., M2M-100 418M or NLLB-600M)
- Fine-tune for 10K steps on a subset of WMT training data (English→German + English→French, ~5M sentence pairs with ≥2-sentence documents)
- Use AdamW (lr=5e-6, β₁=0.9, β₂=0.98), batch size 4096 tokens
- Early stopping based on validation BLEU + bias reduction composite

**Inference**: The Ambiguity Estimator runs on the source side (in parallel with MT encoding). Its outputs are used *only during training* to weight the gender loss — at inference, the MT model runs identically to the baseline, with no additional latency.

---

## 4. Dataset and Benchmark

| Dataset | Use | Size | Languages |
|---|---|---|---|
| **WMT News Commentary** + **Europarl v10** | Training (document-level, long enough for coreference) | ~5M sentence pairs | En→De, En→Fr |
| **OntoNotes 5.0** + **WikiCoref** | Training data for Ambiguity Estimator | ~3K documents | English only |
| **WinoMT** (Stanovsky et al., 2019) | Primary bias evaluation (anti-stereotyped pro-stereotyped pairs) | 3,888 sentences | En→De, En→Fr |
| **MuST-SHE** (Bentivogli et al., 2020) | Secondary bias eval — professionally corrected gender annotations | ~1,200 sentences | En→De, En→Fr, En→It, En→Es |
| **new: CAGED-Ambiguous subset** | Ambiguity-specific quality eval — sentences where gender is NOT resolvable from context | ~500 sentences (constructed) | En→De, En→Fr |

**CAGED-Ambiguous construction**: Sentences with profession nouns (*doctor, nurse, engineer, assistant*) whose antecedents in document context provide no gender signal (first-mention, no pronoun, no honorific, no kinship term). Each sentence is paired with a *both correct* label — both masculine and feminine target forms are acceptable.

---

## 5. Evaluation Metrics

| Metric | What it measures | Source |
|---|---|---|
| **Bias Score (ΔS)** | Difference in accuracy between pro-stereotyped and anti-stereotyped WinoMT subsets. Lower is better. | Stanovsky et al., 2019 |
| **Gender Accuracy (GA)** | % of gendered entity translations that match the (context-resolved) correct gender form. Higher is better. | MuST-SHE |
| **Ambiguity Preservation (AP)** | On the CAGED-Ambiguous subset: % of sentences where the model outputs a gender-neutral strategy OR both genders are equally valid. Higher is better. | New metric |
| **sBLEU / COMET** | Overall translation quality. SacreBLEU (BLEU, ChrF) + COMET-22. | Standard |
| **ΔQuality** | BLEU drop from the unfine-tuned base model. Lower drop = better preservation of quality. | — |

**Primary success signal**: ΔS ≤ 5pp (from a baseline of ~35pp) *and* ΔQuality ≥ -1.5 BLEU (baseline → CAGED). The key test is whether CAGED beats uniform debiasing at any λ setting on *both* axes simultaneously.

---

## 6. Baselines

| Baseline | Description | Expected ΔS (En→De) | Expected ΔBLEU |
|---|---|---|---|
| **Unregularized NMT** | Pretrained M2M-100 finetuned with L_NLL only | ~35pp | 0.0 (reference) |
| **Uniform debiasing (λ=0.1)** | Same model, L_total with uniform gender loss (a=0 for all) | ~10–15pp | -1.5 to -2.5 |
| **Uniform debiasing (λ=0.5)** | Stronger uniform gender loss | ~5–10pp | -3.0 to -5.0 |
| **Counterfactual Data Augmentation (CDA)** | Training data augmented with flipped-gender variants (Zmigrod et al., 2019) | ~10–15pp | -1.0 to -2.0 |
| **Post-hoc embedding debiasing** | Hard-debiased embeddings (Bolukbasi-style, Escudé Font & Costa-jussà, 2019) | ~20–25pp | -0.5 to -1.0 |
| **CAGED (ours)** | Ambiguity-adaptive gender loss | **Target: ≥10pp ΔS** | **Target: ≥ -1.0 BLEU** |

---

## 7. Ablations

| Ablation | Purpose | Conditions tested |
|---|---|---|
| **No Ambiguity Estimator (a=0 for all)** | Isolates the contribution of adaptive weighting vs. the gender loss itself | Same as "Uniform debiasing" — if CAGED beats this, the adaptation matters |
| **Oracle ambiguity (perfect coreference)** | Upper bound — how well could CAGED work with perfect gender resolution? | Human-annotated coreference from OntoNotes used as 0/1 oracle |
| **Context window size** | How much context does the Ambiguity Estimator need? | 0 sentences (sentence-only), 1, 3, 5 sentences of context |
| **Ambiguity threshold binarization** | Is a continuous score better than discrete (resolved/ambiguous)? | Binary threshold at 0.5 vs. continuous weighting |
| **λ sensitivity** | How sensitive is CAGED to the regularization strength? | λ ∈ {0.01, 0.05, 0.1, 0.5, 1.0} |

---

## 8. Expected Failure Modes and Mitigations

| Failure mode | Likelihood | Mitigation |
|---|---|---|
| **Ambiguity Estimator is inaccurate on MT inputs** | Medium | Train on a mix of coreference-annotated text *and* pseudo-labeled MT source sentences; evaluate AE accuracy on a held-out set before NMT fine-tuning |
| **Gender loss hurts BLEU more than expected** | Medium | Reduce λ; consider scheduled annealing (warm up L_gender over 2K steps) |
| **Coreference fails cross-linguistically (En→De/Fr only, not extensible)** | Low for this proposal (En→De, En→Fr are well-studied), high for generalization | Explicitly scope to En→De + En→Fr; note extensibility as future work |
| **Model learns to exploit AE weakness rather than actually debiasing** | Low-Medium | Check: does gender accuracy on high-confidence resolved cases (a < 0.2) improve more than on boundary cases? If not, re-train AE |
| **No meaningful improvement over uniform debiasing** | Medium | If results are equal, the paper becomes a negative result: "Adaptive weighting doesn't help — the trade-off is fundamental." Still publishable with proper analysis |

---

## 9. Short Execution Plan

| Stage | Steps | Duration (est.) | Deliverable |
|---|---|---|---|
| **Stage 1: Ambiguity Estimator** | Extract coreference-resolved entities from OntoNotes/WikiCoref; train mBERT-based AE; evaluate accuracy on held-out coreference data | 3 days | `/models/ambiguity_estimator/` + eval results |
| **Stage 2: Baseline runs** | Fine-tune M2M-100 418M on WMT En→De and En→Fr with L_NLL only; evaluate ΔS + BLEU on WinoMT/MuST-SHE | 2 days | Baseline metrics table |
| **Stage 3: Uniform debiasing** | Fine-tune with uniform gender loss at λ ∈ {0.05, 0.1, 0.5, 1.0}; find Pareto frontier | 2 days | Uniform debiasing Pareto plot |
| **Stage 4: CAGED** | Fine-tune with adaptive gender loss at same λ values; evaluate AE + MT jointly | 2 days | CAGED metrics table |
| **Stage 5: Ablations** | Run all 5 ablations (§7); construct CAGED-Ambiguous set | 4 days | Ablation tables + analysis |
| **Stage 6: Analysis & write-up** | Compile results, error analysis on failure cases; draft paper | 3 days | `/final_report.md` + paper draft |

**Total estimated compute**: ~2 weeks on a single A100 (or equivalent). Key expense is MT fine-tuning (Stages 2–4, ~3× the cost of a single fine-tuning run).

---

## References

- Stanovsky, G., Smith, N.A., & Zettlemoyer, L. (2019). Evaluating Gender Bias in Machine Translation. *ACL 2019*. https://aclanthology.org/P19-1164/
- Saunders, D., & Byrne, B. (2020). Reducing Gender Bias in Neural Machine Translation as a Domain Adaptation Problem. *ACL 2020*. https://aclanthology.org/2020.acl-main.690/
- Zmigrod, R., Mielke, S.J., Wallach, H., & Cotterell, R. (2019). Counterfactual Data Augmentation for Mitigating Gender Stereotypes in Languages with Rich Morphology. *ACL 2019*. https://aclanthology.org/P19-1161/
- Bentivogli, L., Savoldi, B., Negri, M., Di Gangi, M.A., & Turchi, M. (2020). Gender in Danger? Evaluating Speech Translation Technology on the MuST-SHE Corpus. *ACL 2020*. https://aclanthology.org/2020.acl-main.702/
- Escudé Font, J., & Costa-jussà, M.R. (2019). Equalizing Gender Bias in Neural Machine Translation with Word Embeddings. *NAACL 2019 Workshop*. https://aclanthology.org/W19-3821/
- Costa-jussà, M.R., et al. (2020). GeBioM: Gender Bias in Machine Translation. https://github.com/mt-upc/GeBioM
- Fan, A., et al. (2021). Beyond English-Centric Multilingual Machine Translation (M2M-100). *JMLR*. https://arxiv.org/abs/2010.11125
- NLLB Team (2022). No Language Left Behind: Scaling Human-Centered Machine Translation. *arXiv*. https://arxiv.org/abs/2207.04672
- Pradhan, S., et al. (2013). Towards Robust Linguistic Analysis using OntoNotes. *CoNLL 2013*. https://aclanthology.org/W13-3516/

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 15 |
| Topic | Machine translation |
| Original user goal | Generate a research proposal on debiasing in machine translation. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_15/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_15/final_report.md` (13452 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_15/prompt.txt` (669 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_15/query.json` (127 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_15/stdout.txt` (6617 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_15/stderr.txt` (354 bytes)

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
