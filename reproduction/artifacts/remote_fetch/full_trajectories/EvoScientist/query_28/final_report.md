# Preference Bias Amplification: Measuring and Mitigating Western Cultural Bias in DPO-Based LLM Alignment

---

## 1. Problem

Large language models are aligned to human preferences via methods like Direct Preference Optimization (DPO) and Reinforcement Learning from Human Feedback (RLHF). The standard preference datasets used for this — **UltraFeedback**, **HH-RLHF**, **Anthropic Helpfulness/Harmlessness** — are English-only and crowdsourced predominantly from Western (primarily US) annotators. This means the notion of a "helpful" or "harmless" response baked into the most consequential layer of LLM post-training encodes **WEIRD** (Western, Educated, Industrialized, Rich, Democratic) cultural assumptions.

**The gap:** While prior work has examined cultural bias in SFT data (CultureLLM, 2024), in prompting (Luther & Brown, 2025), and in evaluation benchmarks (CValues, MENAValues, CQ-Bench), **no published work systematically measures the specific contribution of preference optimization (DPO/RLHF) to cultural bias amplification**. The central question is: does DPO training on standard Western preference data *increase* the cultural bias of a model relative to its base checkpoint?

**Subproblem selected (from the broader cross-cultural alignment space):** Western cultural bias in preference optimization data and its downstream effect on model outputs across four culturally distinct regions.

---

## 2. Hypothesis

*Standard preference optimization (DPO) on English-only, Western-crowdsourced preference data amplifies the measured Western cultural bias in LLM outputs, and this amplification can be substantially reduced by training on culturally balanced preference data without sacrificing response quality on standard benchmarks.*

**Formal predictions:**
- **H1**: A model fine-tuned with DPO on UltraFeedback will show higher cultural similarity to US/WEIRD populations (measured by WVS-based probes) than its base or SFT-only checkpoint.
- **H2**: A model fine-tuned with DPO on a culturally balanced preference dataset (equal representation of US, Chinese, Indian, and Saudi Arabian value preferences) will show lower measured Western cultural bias than the UltraFeedback-DPO model, while maintaining competitive performance on standard helpfulness/harmlessness benchmarks.
- **H3**: The bias amplification effect is not reducible to linguistic factors — it persists when evaluation is conducted in the target culture's language.

---

## 3. Method

### 3.1 CulturPref-4K: A Culturally Stratified Preference Evaluation Dataset

We construct **CulturPref-4K**, a diagnostic dataset of 4,000 culturally-contrastive preference pairs spanning 4 regions:

| Region | Rationale | Cultural Distinctiveness |
|--------|-----------|------------------------|
| **United States** | Default culture in preference data | Individualist, low power distance, liberal |
| **China** | Collectivist, distinct value system | Collectivist, high power distance, harmony-focused |
| **India** | Large English-speaking but non-Western | Hierarchical, religiously-grounded moral frameworks |
| **Saudi Arabia** | Arab-Muslim cultural context | High power distance, traditional/religious values |

**Construction protocol:**
1. **Prompt sourcing (1,000 prompts):** Sample 250 prompts per region from culturally relevant social media and QA forums (Zhihu for China, Quora India, Arab Twitter/X for Saudi Arabia, Reddit US). Each prompt is a realistic scenario with cultural value implications (e.g., family obligations, authority respect, religious practice, gender roles).
2. **Response pair generation:** For each prompt, generate two responses via GPT-4o with cultural personas — one encoding a Western-liberal value judgment, one encoding a non-Western value judgment aligned with the target culture.
3. **Expert validation:** For each pair, 2 annotators from the target culture label which response better reflects their culture's prevailing values. Only pairs with ≥75% inter-annotator agreement are retained.

### 3.2 Culture-Balanced Training Dataset (CulturPref-Train-6K)

We augment the existing UltraFeedback dataset (63k pairs) by adding **6,000 additional preference pairs** — 1,500 from each of the three non-Western regions (China, India, Saudi Arabia). Each pair contrasts a Western-default response with a culturally adapted response, with the non-Western response labeled as preferred.

Three training conditions are compared:

| Condition | Preference Data | Size |
|-----------|----------------|------|
| **W-DPO** (Western DPO) | UltraFeedback only (standard) | ~63k pairs |
| **B-DPO** (Balanced DPO) | UltraFeedback + 6k non-Western pairs | ~69k pairs |
| **N-DPO** (Non-Western DPO) | 6k non-Western pairs only | ~6k pairs |

### 3.3 Evaluation Framework

We evaluate all model variants across four dimensions:

| Dimension | Metric | Source Instrument |
|-----------|--------|-----------------|
| **Cultural value similarity** | Top-1 agreement with regional majority + Jensen-Shannon Divergence (JSD) over WVS item distributions | World Values Survey (20 items selected per region for relevance) |
| **WEIRD bias score** | % of responses matching US-majority opinion vs. target-culture majority | Adapted from Rystrøm et al. (2025) |
| **Semantic invariance** | Variance across 5 semantically equivalent rephrasings of each probe | Following Khan et al. (2025) critique |
| **Response quality** | Helpfulness rating (GPT-4 evaluator) + Harmlessness rating | Standard MT-Bench / SafetyBench |

### 3.4 Model & Training Details

- **Base model:** Llama-3.1-8B-Instruct (SFT checkpoint)
- **Alignment method:** DPO (β=0.1, learning rate=5e-7, batch size=64, 1 epoch)
- **All training runs** are repeated with 3 seeds; all metrics reported with 95% CIs.
- **Compute estimate:** 3 seeds × 3 conditions = 9 DPO runs × ~2 hours on 1×A100-80GB ≈ 18 GPU-hours.

---

## 4. Dataset / Benchmark

| Name | Type | Size | Source / Construction |
|------|------|------|----------------------|
| **CulturPref-4K** | Evaluation (diagnostic) | 4,000 culturally-contrastive preference pairs | Newly constructed (Sec 3.1) |
| **CulturPref-Train-6K** | Training (augmentation) | 6,000 non-Western preference pairs | Newly constructed (Sec 3.2) |
| **WVS Cultural Probe** | Evaluation (values) | 20 items × 4 regions = 80 multi-choice probes | Sampled from World Values Survey wave 7 |
| **MT-Bench** | Evaluation (quality) | 80 multi-turn questions | Standard benchmark |
| **SafetyBench** | Evaluation (safety) | 11,475 test questions | Standard benchmark (Chinese + English subsets) |

---

## 5. Evaluation Metrics

| Metric | Target | Interpretation | Reported As |
|--------|--------|---------------|-------------|
| **Cultural Agreement (%)** | WVS probes | % of model answers matching target-culture majority | Mean ± std across 20 items, per region |
| **WEIRD Shift (Δ)** | WVS probes | (DPO agreement with US) − (DPO agreement with target culture) | Positive = Western bias amplification |
| **JSD** | WVS response distribution | Distance between model's value distribution and target culture's | Per-region JSD, averaged |
| **Prompt Variance Score** | WVS probes | Variance in agreement across 5 rephrasings | Lower = more robust (0–1 normalized) |
| **MT-Bench Score** | MT-Bench | Average GPT-4 rating (1–10) | Mean ± std |
| **Safety Score** | SafetyBench | % safe responses | Per-category breakdown |

**Primary metric:** WEIRD Shift (Δ) — the difference between US agreement rate and target-culture agreement rate, before vs. after DPO. A positive Δ after DPO confirms H1 (bias amplification). A smaller Δ under B-DPO vs. W-DPO confirms H2.

---

## 6. Baselines

| Baseline | What It Measures | Why It's Needed |
|----------|-----------------|-----------------|
| **Base model** (no alignment) | Cultural bias in pre-trained / SFT model | Reference point for measuring *additional* bias from DPO |
| **W-DPO** (UltraFeedback only) | Standard DPO pipeline | Represents status quo — the current practice in LLM alignment |
| **N-DPO** (non-Western pairs only) | Upper bound of cultural adaptation | Shows what pure non-Western alignment looks like |
| **B-DPO** (balanced) | Our proposed mitigation | Main intervention |
| **CultureLLM-style SFT** (SFT on culture-specific data) | Existing best practice for cultural adaptation | Shows whether preference-level intervention adds value beyond SFT-level intervention |

---

## 7. Ablations

| Ablation | Manipulation | What It Tests |
|----------|-------------|---------------|
| **A1: Language control** | Evaluate all models in English-only (no native-language evaluation) | Isolates language confound — if bias persists, it's cultural, not linguistic (H3) |
| **A2: Prompt-only intervention** | Add cultural context prompt ("Answer as someone from X") to W-DPO model without retraining | Tests whether prompting can undo DPO-level bias |
| **A3: Data scale** | B-DPO with 2K, 4K, 6K non-Western pairs | Tests whether more culture data monotonically reduces bias |
| **A4: Single-region DPO** | B-DPO with only one non-Western region added at a time | Tests whether bias reduction is uniform across cultures or region-specific |
| **A5: Model size** | Repeat W-DPO and B-DPO on Llama-3.1-70B if compute allows | Tests whether findings scale with model capacity |

---

## 8. Expected Failure Modes

| Failure Mode | Mitigation / Alternative |
|-------------|------------------------|
| **H1 not supported** (DPO does not amplify cultural bias) | Still publishable — would show preference data is less biased than assumed. Report effect sizes and CIs transparently. |
| **H2 not supported** (B-DPO does not reduce bias) | Could mean Western bias is embedded in the base model (pre-training data), not just preference data. Analysis would pivot to pre-training data cultural composition. |
| **H3 not supported** (bias is just a language effect) | Would validate the "multilingual ≠ multicultural" framing and suggest simpler language-based interventions (translate evaluation, not retrain). |
| **Low annotator agreement** (>25% of pairs fail 75% threshold) | Switch to a smaller, higher-quality set of 1,000 pairs with expert (PhD-level) annotators only. Report agreement rates transparently. |
| **Khan et al. (2025) reliability critique** (survey probes are unreliable) | Address directly — compute and report prompt variance scores for every probe. Only include items with low variance. Acknowledge limitation. |
| **MT-Bench quality degradation under B-DPO** | If B-DPO reduces helpfulness because non-Western values produce less "helpful" (as judged by Western evaluators) responses, use human evaluators from each target culture instead of GPT-4. |
| **B-DPO and W-DPO converge** (small effect, overlapping CIs) | Increase sample size for WVS probes (more items). Report Bayes factors as complementary evidence. |

---

## 9. Short Execution Plan

```
Phase 1: Dataset Construction (3 weeks)
├── Week 1: Prompt collection — 1,000 prompts across 4 regions
├── Week 2: Response generation + expert annotation (4 cultures)
├── Week 3: Validation, filtering, finalizing CulturPref-4K + CulturPref-Train-6K
│   Deliverable: culturpref_v1/ (train + eval splits)

Phase 2: Baseline & Train (2 weeks)
├── Week 4: Run base + W-DPO baselines (3 seeds each)
│   Evaluate on WVS probes + MT-Bench + SafetyBench
├── Week 5: Run B-DPO + N-DPO + CultureLLM-SFT (3 seeds each)
│   Deliverable: All 9 checkpoints + raw metric tables

Phase 3: Evaluation & Ablations (2 weeks)
├── Week 6: Full evaluation suite across all conditions
│   Compute WEIRD Shift, JSD, Prompt Variance
├── Week 7: Run ablations A1–A4 (language control, prompting, data scale, single-region)
│   Deliverable: ablation_analysis.csv + figures/

Phase 4: Analysis & Writing (2 weeks)
├── Week 8: Statistical analysis — effect sizes, CIs, sensitivity analysis
│   Produce final tables and figures
├── Week 9: Paper writing + review iteration
│   Deliverable: paper draft + rebuttal prep + reproducibility package

Total: ~9 weeks (with 1×A100-80GB GPU, < $2,000 compute cost at standard cloud rates)
```

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 28 |
| Topic | Alignment |
| Original user goal | Generate a research proposal on cross-cultural alignment for Large Language Models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_28/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_28/final_report.md` (12259 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_28/prompt.txt` (687 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_28/query.json` (135 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_28/stdout.txt` (8042 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_28/stderr.txt` (251 bytes)

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
