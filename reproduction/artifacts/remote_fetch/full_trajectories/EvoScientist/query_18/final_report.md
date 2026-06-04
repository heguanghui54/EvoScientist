# How Uncertainty Communication Format Interacts with User Expertise to Shape Appropriate Reliance on LLMs

## A Research Proposal on User Experience Evaluation for Large Language Models

---

## 1. Subproblem Selection and Motivation

**Broad query:** User experience evaluation for Large Language Models.

**Specific subproblem chosen (author's decision):** How does the *format* of LLM uncertainty communication interact with *user domain expertise* to affect appropriate reliance, trust calibration, and task performance in factual question-answering?

**Why this subproblem:** The literature on LLM trust and overreliance has grown rapidly (Kim et al. 2024, 2025; Zhou et al. 2024; Bo et al. 2024; Steyvers et al. 2024), producing a clear result: users systematically over-rely on confidently wrong LLM outputs. Several interventions have been proposed — verbalized uncertainty, numerical confidence scores, and behavioral uncertainty displays (e.g., showing multiple sampled answers). However, a critical gap remains: **existing work treats users as a homogeneous population.** No study has systematically examined whether the *optimal* uncertainty communication format depends on the user's domain expertise. An expert fact-checker and a novice searching for quick answers may need fundamentally different signals to calibrate their trust appropriately. This proposal addresses that gap directly.

---

## 2. Problem Statement

When LLMs provide factual answers with some expression of uncertainty — a verbal hedge ("I'm not certain, but..."), a numerical confidence score ("I'm 75% confident"), or behavioral inconsistency ("Three out of five sampled answers agree with this") — do these formats *differentially* affect appropriate reliance depending on the user's prior expertise in the domain?

**Null hypothesis (H₀):** Uncertainty communication format and user expertise independently affect appropriate reliance, with no interaction.

**Alternative hypothesis (H₁):** The effectiveness of uncertainty communication format on appropriate reliance is moderated by user domain expertise. Specifically:
- **H₁a:** Novice users benefit more from verbal hedges (simple, intuitive) than from numerical confidence or behavioral uncertainty.
- **H₁b:** Expert users benefit more from numerical confidence scores (precise, calibratable against their own knowledge) than from verbal hedges or behavioral uncertainty.
- **H₁c:** Behavioral uncertainty displays (showing sampled-answer disagreement) produce the most robust improvements across *all* expertise levels, because they convey information about the model's epistemic state without requiring the user to interpret a numeric or verbal format.

These sub-hypotheses are grounded in prior findings: verbal hedges reduced overreliance but also reduced appropriate reliance (Kim et al. 2024); numerical confidence can be misinterpreted (Steyvers et al. 2024); behavioral inconsistency was the most effective single intervention (Kim et al. 2025).

---

## 3. Method

### 3.1 Design

**3 (Uncertainty format) × 2 (User expertise) mixed design.**

- **Between-subjects factor (random assignment):** Uncertainty communication format.
  1. **Verbal hedge:** LLM prefaces its answer with a calibrated natural-language uncertainty expression (e.g., "I'm not entirely sure, but I think the answer is..."). Wording is dynamically selected from a validated set (Zhou et al. 2024 taxonomy).
  2. **Numerical confidence:** LLM appends a confidence percentage based on its token-level probability (e.g., "Answer: Paris. Confidence: 82%"). Displayed alongside the answer in a standardized format.
  3. **Behavioral uncertainty:** LLM shows a summary of 5 independent sampling runs (e.g., "3 out of 5 sampled responses agree with this answer"). This is the inconsistency-display format from Kim et al. (2025).

- **Measured between-subjects factor (blocked post-hoc):** User domain expertise, measured via a pre-task quiz of 10 questions spanning the same domains as the main task, with self-rated confidence for each answer. Users are divided into terciles (low / medium / high expertise).

- **Within-subjects factor:** Question difficulty (easy / hard), validated via a pilot (see Section 7). Each user sees 30 easy and 30 hard questions.

### 3.2 Dependent Variables (Primary and Secondary)

| Variable | Type | Definition | Measurement |
|---|---|---|---|
| **Appropriate reliance score (primary)** | Behavioral | Agreement rate with correct answers minus agreement rate with incorrect answers. Range: [−1, +1]. Higher = better calibrated trust. | Computed from user responses (accept/reject LLM answer). |
| **Task accuracy** | Behavioral | Proportion of questions where the user's final answer (after seeing LLM output) is correct. | Ground-truth labels from the dataset. |
| **Verification rate** | Behavioral | Proportion of trials where the user performs an explicit verification action (clicks a "verify with source" button). | Logged clicks. |
| **Trust score** | Subjective | Post-task 7-item Likert scale adapted from Bach et al. (2023) trust dimensions: perceived competence, benevolence, transparency, and reliance intention. | Mean of 7 items (Cronbach's α expected > 0.80 based on prior use). |
| **Calibration error** | Calibration | |perceived accuracy − actual accuracy|, where perceived accuracy is the user's estimate of how many LLM answers were correct. | User self-report after each block (10 questions). |
| **Decision time** | Behavioral | Time from LLM answer display to user decision. | Logged in milliseconds. |

### 3.3 Data Collection

- **Sample:** N = 600 participants recruited via Prolific (stratified by education level to ensure variance in domain expertise), paid £9/hr for ~30 min session. This sample size is powered to detect a small-to-medium interaction effect (f = 0.15, α = 0.05, power = 0.90 for a 3×2 ANOVA with 100 per cell).
- **Attention checks:** 5 catch trials interspersed where the LLM-provided answer is clearly absurd (e.g., "What is the capital of France?" → "Tokyo"). Participants failing ≥2 are excluded.
- **Exclusion criteria:** Completion time < 10 min, ≥2 failed attention checks, or self-report of not taking the task seriously (single debrief item).

---

## 4. Dataset and Benchmark

### 4.1 Primary Dataset: TruthfulQA (Lin et al. 2021)

- **Size:** 817 questions across 38 categories.
- **Selection:** 60 questions will be sampled, stratified by category, with 30 easy and 30 hard (validated in pilot, see Section 7).
- **Why TruthfulQA:** Designed to probe LLM truthfulness; questions have verifiable ground truth with known common misconceptions. Widely used in prior overreliance studies (Kim et al. 2024, 2025; Zhou et al. 2024). Covers diverse domains (health, law, science, pop culture), enabling meaningful expertise measurement.

### 4.2 Supplementary Dataset: TriviaQA (Joshi et al. 2017)

- **Size:** 95k QA pairs from trivia web sources.
- **Selection:** 20 additional questions per participant (cold-start buffer, not analyzed), used to familiarize users with the interface and format.
- **Why TriviaQA:** Used in Kim et al. (2025) for large-scale overreliance experiments. Clean ground truth, controlled difficulty.

### 4.3 Controlled LLM Outputs (Stimulus Construction)

For each question, the LLM (GPT-4o) generates answers that are:
- **Correct (30 questions):** LLM provides the verified correct answer. Uncertainty communication is calibrated to reflect genuine model confidence (i.e., high-confidence questions get high numeric/hedge/consistency signals).
- **Incorrect (30 questions):** LLM provides a plausible-sounding *incorrect* answer. Uncertainty communication is *systematically miscalibrated* (overconfident) on 20 of these (to mimic the real-world overconfidence documented by Zhou et al. 2024) and *well-calibrated* on 10 (for comparison). This mirrors the 50/50 split used in prior work (Kim et al. 2024).

All stimuli are validated for plausibility by 3 independent raters before the main experiment.

---

## 5. Evaluation Metrics

### 5.1 Primary Analysis

**3 × 2 between-subjects ANOVA** on the primary appropriate-reliace score.
- Main effect of uncertainty format.
- Main effect of expertise tercile.
- **Interaction: format × expertise (the key test of H₁).**

### 5.2 Secondary Analyses

- **ANCOVA** with decision time as a covariate (to control for effort).
- **Post-hoc pairwise comparisons** (Tukey HSD) on significant interactions.
- **Mixed-effects logistic regression** on per-trial agreement (random intercepts for participant and question). Predictors: format, expertise, difficulty, correctness × {format, expertise} interactions.
- **Calibration curves:** Plot perceived accuracy vs. actual accuracy per format × expertise cell.

### 5.3 Effect Size Targets

| Metric | Minimum practically meaningful effect | Interpretation |
|---|---|---|
| Appropriate reliance (Δ between best and worst format within expertise group) | ≥ 0.08 | Equivalent to ~1.5 fewer overreliance errors out of 20 hard+incorrect trials |
| Trust calibration error reduction | ≥ 0.10 | 10 percentage points improvement in accuracy estimation |
| Verification rate increase on incorrect trials | ≥ 10 pp | 10 percentage point increase in verification behavior |

---

## 6. Baselines

### 6.1 No-Uncertainty Baseline (Control)

A fourth condition (n = 150, separate between-subjects) where the LLM presents its answer with no uncertainty expression. This mirrors the default behavior of most deployed LLMs.

### 6.2 Literature Benchmark Comparisons

Expected ranges from prior work (reported on analogous tasks):

| Condition | Appropriate Reliance (Kim et al. 2024) | Overreliance Rate (Kim et al. 2025) |
|---|---|---|
| No uncertainty | ~0.30 | ~72% |
| Verbal hedge | ~0.38 | ~58% |
| Behavioral uncertainty | — | ~45% (from inconsistency condition) |

Our study adds the **expertise × format interaction** analysis that these prior studies did not report.

### 6.3 Ablation: Effect of Question-Specific Confidence Calibration

Within the numerical condition, confidence scores are either:
- **Well-calibrated:** Confidence ≈ model accuracy on that question type (estimated from held-out validation set).
- **Overconfident:** Confidence overstates accuracy by 20–30 pp.

This within-condition ablation tests whether the benefit of numerical confidence depends on its calibration quality — a factor that prior work has not isolated.

---

## 7. Ablations

| Ablation | Description | What It Tests |
|---|---|---|
| **A1 — Format × difficulty** | Re-run analysis with question difficulty as the moderator instead of user expertise. | Is the effect driven by task properties rather than user properties? |
| **A2 — Format × correctness** | Separate appropriate reliance into agreement-with-correct vs. agreement-with-incorrect. | Does a format reduce overreliance (good) at the cost of reducing appropriate reliance on correct answers (bad)? |
| **A3 — No uncertainty baseline only** | Compare each format against the no-uncertainty control, collapsing expertise. | Replicate prior work findings in our setup. |
| **A4 — Self-reported vs. measured expertise** | Compare results using self-reported expertise (single Likert item) vs. measured expertise (quiz score). | Tests whether simple self-report is sufficient for expertise stratification. |
| **A5 — Verification rate decomposition** | Split verification rate by correctness of LLM answer. | Does a format help users verify selectively — more verification on incorrect answers, less on correct ones? |

---

## 8. Expected Failure Modes

| Failure Mode | Likelihood | Mitigation |
|---|---|---|
| **F1 — No interaction effect** (format × expertise is not significant) | Medium | Pre-registered analysis plan; the main effects of format and expertise are still informative. Report Bayes factor for the interaction. |
| **F2 — Task is too easy (ceiling effects)** | Medium | Validate easy/hard split in pilot (Section 7). If ceiling occurs, re-run with harder questions from MMLU or GPQA subsets. |
| **F3 — Expertise measurement is noisy** | Medium | Use the quiz score (continuous) rather than terciles in the primary analysis as a robustness check. Also record domain-specific self-efficacy. |
| **F4 — Participants ignore uncertainty signals** | Low | Include comprehension checks after training phase (e.g., "What did the LLM say about its confidence on the last question?"). Exclude if < 70% accuracy. |
| **F5 — Numerical confidence is interpreted as a probability of correctness by experts but as a general "quality score" by novices** | Medium | Post-task debrief interview (n = 20 per format) to probe qualitative understanding of the uncertainty signal. Include as qualitative supplement. |
| **F6 — Fatigue or order effects** | Low | Randomize question order per participant. Include block-level position as a covariate. |

---

## 9. Execution Plan

### Stage 1: Stimulus Construction (est. 5 days)

1. Select 60 TruthfulQA questions + 20 TriviaQA warm-up questions, stratified by category and difficulty.
2. Generate GPT-4o answers in correct and incorrect variants (3 raters validate plausibility).
3. Construct all three uncertainty-format renderings per question.
4. Implement and pretest the web-based experimental interface (React + Firebase for data collection).

**Success signal:** All 60 × 3 × 2 = 360 stimulus variants reviewed and approved. Interface passes 5 pilot participants with no technical issues.

### Stage 2: Expertise and Difficulty Pilot (est. 3 days)

1. Recruit n = 30 pilot participants (10 per expertise level) via Prolific.
2. Administer 20-question domain quiz + 30-item self-report battery.
3. Validate: (a) quiz score correlates with self-report at r > 0.40; (b) easy/hard split has ≥15 pp accuracy difference; (c) time per trial < 45 seconds.

**Success signal:** All three validation checks pass. If not, adjust question selection or difficulty thresholds.

### Stage 3: Main Experiment (est. 7 days)

1. Recruit N = 600 participants across 4 conditions (3 formats + control, n = 150 each).
2. Run experiment with random assignment, counterbalanced within-subject factors.
3. Real-time monitoring of attention check pass rates and completion times.

**Success signal:** ≥ 500 valid participants after exclusions. Balanced demographics across conditions.

### Stage 4: Analysis (est. 3 days)

1. Pre-registered primary analysis (3×2 ANOVA, ANCOVA, mixed-effects models).
2. All ablations (A1–A5).
3. Qualitative analysis of debrief interviews.

**Success signal:** All analysis scripts produce reproducible outputs. A `renv` or `conda` lockfile is committed.

### Stage 5: Reporting (est. 3 days)

1. Write full paper (Introduction, Related Work, Method, Results, Discussion, Limitations).
2. Create figures: interaction plots, calibration curves, verification-rate bar charts.
3. Release pre-registration, data, and analysis code.

**Success signal:** Paper draft ready for submission to CHI 2027 or IUI 2027.

---

## 10. Timeline Summary

| Stage | Duration | Key Deliverable |
|---|---|---|
| 1. Stimulus construction | 5 days | 360 validated stimuli + working web interface |
| 2. Pilot | 3 days | Difficulty/expertise validation report |
| 3. Main experiment | 7 days | Raw data (≥500 valid participants) |
| 4. Analysis | 3 days | Reproducible notebooks + figures |
| 5. Reporting | 3 days | Paper draft + public release |
| **Total** | **~21 days** | |

---

## 11. Contributions (Summary)

1. **First systematic test of the interaction** between uncertainty communication format and user expertise for appropriate LLM reliance.
2. **Practical design guidance:** Which uncertainty format should LLM interfaces use for expert vs. novice users?
3. **Open dataset + analysis code:** 600-participant behavioral experiment with full stimuli, responses, and reproducible analysis pipeline.

---

### References

- Bach, T. A., et al. (2023). A Systematic Literature Review of User Trust in AI-Enabled Systems. arXiv:2304.08795.
- Bo, J. Y., Wan, S., & Anderson, A. (2024). To Rely or Not to Rely? Evaluating Interventions for Appropriate Reliance on LLMs. arXiv:2412.15584.
- Joshi, M., et al. (2017). TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension. ACL.
- Kim, S. S. Y., et al. (2024). "I'm Not Sure, But...": Examining the Impact of LLMs' Uncertainty Expression on User Reliance and Trust. arXiv:2405.00623.
- Kim, S. S. Y., et al. (2025). Fostering Appropriate Reliance on LLMs: The Role of Explanations, Sources, and Inconsistencies. arXiv:2502.08554.
- Lin, S., Hilton, J., & Evans, O. (2021). TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL.
- Steyvers, M., et al. (2024). What Large Language Models Know and What People Think They Know. arXiv:2401.13835.
- Villavicencio, M., et al. (2026). Not All Uncertainty Is Equal: How Uncertainty Granularity Shapes Human Verification in LLM-Assisted Decision Making. arXiv:2605.28571.
- Zhou, K., et al. (2024). Relying on the Unreliable: The Impact of Language Models' Reluctance to Express Uncertainty. arXiv:2401.06730.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 18 |
| Topic | UX evaluation |
| Original user goal | Generate a research proposal on user experience evaluation for Large Language Models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_18/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_18/final_report.md` (17254 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_18/prompt.txt` (689 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_18/query.json` (141 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_18/stdout.txt` (9771 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_18/stderr.txt` (251 bytes)

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
