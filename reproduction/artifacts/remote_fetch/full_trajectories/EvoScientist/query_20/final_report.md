# MADEF: A Multi-Axis Decomposed Evaluation Framework for Diversity in Open-Ended Text Generation

## 1. Title

**MADEF: A Multi-Axis Decomposed Evaluation Framework for Diversity in Open-Ended Text Generation**

## 2. Problem

### The Gap

Diversity is a critical dimension of text generation quality, cited alongside fluency, coherence, and relevance in nearly every major NLG evaluation framework [1, 2]. Yet the community lacks a **principled, validated, and decomposable evaluation framework** for measuring it. The current landscape has three interconnected problems:

**Problem A — Metric conflation.** "Diversity" is treated as a monolithic construct, but it subsumes at least three distinct phenomena: lexical richness (rare word usage), syntactic variety (sentence structure variation), and semantic breadth (coverage of different meanings and topics) [3, 4]. Distinct-2, Self-BLEU, and embedding diversity correlate poorly with each other (Spearman ρ = 0.12–0.61) [5], which means papers reporting any one metric are not measuring the same thing, and reviewers cannot compare results across papers.

**Problem B — Quality-diversity confounding.** Diversity metrics are systematically confounded with output quality: high-temperature sampling produces diverse but often ungrammatical text, while beam search produces fluent but repetitive text [6, 7]. Most published evaluations report only one dimension, making it impossible to know whether a "diversity improvement" came at an unacceptable quality cost [8, 9].

**Problem C — No standardized evaluation paradigm.** Unlike machine translation (WMT) or summarization (SummEval), there is no standardized benchmark for **evaluating diversity evaluation itself**. Different papers use different metrics, datasets, decoding strategies, and statistical procedures, and an estimated 22% of published diversity comparisons are not statistically significant under bootstrap resampling [10].

### Why Now

Recent work has made the constituent pieces available: MAUVE provides a distributional quality-diversity comparison [11]; Tevet & Berant (2021) exposed the correlation failures of existing metrics [5]; Gao et al. (2022) proposed a three-tier taxonomy [3]; and GEM provides multi-task infrastructure [12]. What is missing is a **unified framework** that combines these insights into a practical, validated evaluation battery — analogous to how BLEU + human evaluation became the standard for MT, or ROUGE + BERTScore for summarization.

## 3. Hypothesis

**Primary hypothesis (H1):** Decomposing diversity into three interpretable axes (lexical, syntactic, semantic) and measuring each with validated metrics produces a composite evaluation that correlates significantly better with human judgments of output diversity (Spearman ρ ≥ 0.6) than any single current metric (ρ ≈ 0.3–0.5 for Distinct-2, Self-BLEU, and embedding diversity individually).

**Secondary hypothesis (H2):** A quality-corrected diversity score — defined as diversity measured only over outputs that pass a minimum fluency threshold — eliminates the spurious correlation between diversity and degeneration, recovering the true diversity frontier that is masked by quality confounds.

**Tertiary hypothesis (H3):** The relative importance of the three diversity axes depends on the generation task: semantic diversity dominates in concept-to-text (CommonGen), syntactic diversity dominates in story generation (WritingPrompts), and lexical diversity dominates in dialogue (Persona-Chat).

## 4. Method

MADEF consists of three components: a **Multi-Axis Metric Battery**, a **Quality-Corrected Diversity Score**, and a **Standardized Evaluation Protocol**.

### 4.1 Multi-Axis Metric Battery

Each axis is measured by a primary metric and one or more secondary metrics (for sensitivity analysis):

| Axis | Primary Metric | Secondary Metrics | Rationale |
|------|---------------|-------------------|-----------|
| **Lexical** | Length-normalized Distinct-2 (LND-2) | Entropy over bigrams [13]; Type-Token Ratio with sentence-length regression residual [14] | LND-2 corrects the well-known length bias of raw Distinct-2 by computing `log(unique_bigrams) / log(total_bigrams)`, which stabilizes the metric across output lengths |
| **Syntactic** | POS-tag entropy (PTE) | Constituent tree depth variance; dependency distance variance [3] | PTE computes Shannon entropy over the distribution of universal POS tag sequences in each generated text. Higher entropy = more varied syntactic structures |
| **Semantic** | Pairwise SBERT cosine diversity (SD) | MAUVE divergence frontier area [11]; centroid coverage via k-means cluster count [15] | SD averages pairwise 1 − cosine_sim over Sentence-BERT embeddings of all outputs for a given input, capturing meaning-level variation |

**Formal definition of the composite MADEF score:**

For a set of generated outputs \(G = \{g_1, \ldots, g_N\}\) for a given input, normalize each axis score to [0, 1] across all compared systems using min-max scaling, then compute:

\[
\text{MADEF}(G) = \frac{1}{3}\big( \hat{L} + \hat{S} + \hat{D} \big) \cdot (1 - \text{penalty}(G))
\]

where \(\hat{L}, \hat{S}, \hat{D}\) are the normalized lexical, syntactic, and semantic scores, and `penalty(G)` is a quality-discount factor (see §4.2).

### 4.2 Quality-Corrected Diversity Score

To disentangle quality from diversity, we introduce a **quality filter** prior to metric computation:

1. Score each generated sentence with a reference-based fluency estimator (GPT-2/XSum perplexity, thresholded at the 80th percentile of grammatical human text on the same domain).
2. Flag outputs above the perplexity threshold as "quality-failed."
3. Compute all diversity metrics **twice**: once on the full set (uncorrected) and once after removing quality-failed outputs (corrected).

The **penalty** in the MADEF composite is the proportion of quality-failed outputs:

\[
\text{penalty}(G) = \frac{|G_{\text{failed}}|}{|G|}
\]

This ensures that a system achieving high diversity through degeneration (e.g., temperature = 2.0) receives a low MADEF score despite high raw diversity. Following [9], we also report the **Pareto frontier** of (diversity, quality) pairs across systems in all scatter plots, so reviewers can assess the trade-off directly.

### 4.3 Standardized Evaluation Protocol

Every MADEF evaluation follows a fixed procedure:

1. **Input preprocessing**: Consistent tokenization (GPT-2 BPE via HuggingFace tokenizers), standardized length truncation (max 512 tokens, min 10 tokens).
2. **Reference handling**: For tasks with multiple references (e.g., WebNLG), use all available references and average; for single-reference tasks, report diversity on the generated set only (no reference comparison, following [5]).
3. **Statistical reporting**: Report all scores with 95% confidence intervals via bootstrap resampling (5,000 iterations, following [10]).
4. **Human validation subset**: On a 200-instance subset per condition, collect human variety judgments (Likert 1–5, following van der Lee protocol [16]) and report Spearman correlation with each automated metric.
5. **Effect size**: Report Cohen's d for all pairwise system comparisons alongside p-values (Bonferroni-corrected).

## 5. Dataset / Benchmark

We select three tasks that span the diversity-relevance spectrum:

| Task | Dataset | Size | Why This Task? | Reference Count |
|------|---------|------|----------------|-----------------|
| **Dialogue** | Persona-Chat [17] | 1000 test prompts | High diversity expected; used in most prior diversity studies | Single |
| **Concept-to-text** | CommonGen [18] | 1000 test prompts | Moderate diversity; constrained output space | Single |
| **Story generation** | WritingPrompts (subset) [19] | 500 prompts | Very high diversity; long-form generation | Single |

Total: 2,500 prompts, each generating 10 outputs per condition → 25,000 generated texts per experimental condition.

## 6. Evaluation Metrics

### Primary Metrics (to be validated)
- **MADEF composite** (our proposed score, §4.1)
- **Per-axis scores**: LND-2, PTE, SD (each individually)

### Baseline Metrics (existing standards)
- **Distinct-1, Distinct-2** [20] — lexical
- **Self-BLEU** [21] — lexical (aggregate)
- **N-gram entropy (bigram)** [13] — lexical
- **Embedding diversity (SBERT)** [22] — semantic
- **MAUVE** [11] — distributional
- **BARTScore** [23] — quality proxy

### Quality Correlates (for quality-diversity analysis)
- **Perplexity** (GPT-2-XL, zero-shot)
- **MAUVE** (as quality metric)
- **Human fluency** (Likert 1–5, subset)

### Human Evaluation
- **Variety** (1–5 Likert, van der Lee protocol [16])
- **Fluency** (1–5 Likert)
- Inter-annotator agreement: Krippendorff's α ≥ 0.6 threshold for inclusion; 3 annotators per instance.

## 7. Baselines

### Decoding Strategies (8 conditions × 3 seeds = 24 runs per dataset)

| Strategy | Parameters | Rationale |
|----------|-----------|-----------|
| Greedy decoding | — | Lowest-diversity baseline |
| Beam search (width 5) | B = 5 | Low-diversity quality baseline |
| Temperature sampling | t ∈ {0.7, 0.9, 1.2, 1.5} | Classic diversity control |
| Top-k sampling | k ∈ {10, 50, 100} | Popular stochastic method |
| Nucleus (top-p) sampling | p ∈ {0.8, 0.9, 0.95} | Current recommended default [6] |
| Typical sampling | τ ∈ {0.2, 0.5, 0.8} | Recent alternative [24] |
| Contrastive decoding | λ ∈ {0.1, 0.5, 1.0} | Candidate proposed for diversity [25] |
| Diverse beam search | beam = 5, diversity_penalty ∈ {0.2, 0.5} | Explicit diversity objective [26] |

Total: ~48 experimental conditions per dataset (some parameter combinations may be pruned after pilot).

### Models (3 model sizes)

- GPT-2 (Small, Medium, XL) — 124M, 355M, 1.5B parameters
- All via HuggingFace transformers, fixed random seeds (42, 84, 126), half-precision inference

## 8. Ablations

| Ablation | What is removed/modified | What it tests |
|----------|------------------------|---------------|
| **A1: Axis removal** | MADEF omitting one axis at a time (3 ablations) | Contribution of each axis to human correlation |
| **A2: No quality correction** | MADEF computed without the quality filter | Impact of the quality-penalty term on Spearman ρ |
| **A3: Embedding model variant** | SBERT → SimCSE → GPT-2 last hidden | Sensitivity of semantic axis to embedding model choice |
| **A4: Length normalization ablation** | LND-2 → raw Distinct-2 | Effectiveness of length normalization (test H1 robustness) |
| **A5: Tokenizer sensitivity** | GPT-2 BPE → word-level → character-level | Robustness of all metrics to tokenization choices |
| **A6: Reference-free vs reference-aware** | All metrics computed with and without reference output | Whether multiple references change diversity rankings |

## 9. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Impact | Mitigation |
|-------------|-----------|--------|------------|
| **Human judgments don't correlate well with any automated metric** (ρ < 0.5 for MADEF) | Medium — human annotation of diversity is notoriously difficult [5] | High — invalidates the framework | Prototype and pilot the annotation protocol; calibrate annotators with 50 practice examples; use pairwise ranking (easier) alongside Likert; pre-register a minimal acceptable ρ of 0.55 before proceeding to full annotation |
| **Syntactic axis (PTE) is not discriminative** — all decoding strategies produce similar POS distributions | Medium — open-ended generation may not vary syntax much | Medium — framework reduces to 2 axes | Pilot on 100 instances first; if PTE variance is low, replace with dependency depth variance or an alternative syntactic measure |
| **Quality filter is too aggressive** — it removes almost all diverse outputs, making the corrected diversity near-identical across conditions | Low (temperature 0.7 usually passes quality checks) | Medium — quality correction becomes trivial | In pilot, calibrate the perplexity threshold per task using held-out human text; also report uncorrected scores in supplementary |
| **Metric saturation** — on very long outputs (WritingPrompts), all metrics plateau | Medium | Medium — ceiling effects reduce discriminability | Report results stratified by output length (short: <100, medium: 100–300, long: >300 tokens); length-stratified human evaluation |
| **Computational cost** — SBERT embeddings and MAUVE for 25K texts per condition add up | Low (SBERT is fast) | Low — just engineering | Precompute all embeddings once; cache results; reuse across metric computations |
| **Domain-specific failures** — the perplexity threshold trained on one domain does not transfer to another | Medium | Medium | Estimate perplexity thresholds per-domain using 100 human-written examples from each dataset |

## 10. Execution Plan

### Phase 0: Pilot (2 weeks)
1. Install dependencies (HuggingFace transformers, SBERT, MAUVE, NLTK for POS tagging).
2. Implement the three-axis metric battery in a unified Python package (`madef/`).
3. Pilot on 100 prompts from Persona-Chat × 5 decoding strategies (50 seeds).
4. Run human annotation pilot (3 annotators, 50 instances).
5. Calibrate quality-filter perplexity thresholds per dataset.
6. **Checkpoint**: Must achieve Spearman ρ ≥ 0.55 on the pilot or revise metrics.

### Phase 1: Main Experiment (4 weeks)
1. Generate outputs for all 48 conditions × 3 datasets (background execution, ~2 weeks GPU).
2. Compute all metrics on all outputs (can parallelize across metric types).
3. Compute confidence intervals via bootstrap (5,000 iterations).
4. Run ablation experiments A1–A6.
5. **Checkpoint**: Full metric table with CIs; ablation results.

### Phase 2: Human Evaluation (3 weeks)
1. Recruit 3 annotators (or use Amazon Mechanical Turk with quality controls).
2. Annotate 200 instances per condition × 3 datasets (600 total) on variety and fluency.
3. Compute inter-annotator agreement (Krippendorff's α).
4. Compute Spearman correlation between each automated metric and human variety.
5. **Checkpoint**: Human correlation table; rank consistency analysis.

### Phase 3: Analysis and Write-up (3 weeks)
1. Pareto frontier analysis (diversity vs. quality across all conditions).
2. Multi-task comparison: do axis weights differ by dataset? (H3).
3. Visualizations: correlation heatmaps, scatter plots, axis importance bar charts.
4. Statistical analysis: pairwise significance tests with Bonferroni correction.
5. Write paper for ACL Rolling Review or EMNLP.
6. Release `madef` package and evaluation benchmark as open source.

### Phase 4: Contingency (2 weeks, if needed)
- If H1 (human correlation) is borderline, run an additional side-by-side ranking annotation for more discriminative signal.
- If the quality filter is non-informative, drop it and report uncorrected only, but add a dedicated quality-evaluation section.
- If syntactic diversity is uninformative, frame the contribution as "a 2-axis framework validated for lexical and semantic diversity."

**Total estimated duration: 12–14 weeks.**

## 11. Related Work

The proposal draws on and extends the following lines of work:

**Metric development.** Li et al. (2016) introduced Distinct-1/2 for dialogue [20]; Zhu et al. (2018) formalized Self-BLEU for GAN evaluation [21]; Pillutla et al. (2021) proposed MAUVE as a distributional metric that jointly captures quality and diversity [11]. Our contribution is to integrate these into a validated multi-axis battery rather than proposing a replacement metric.

**Empirical characterization.** Tevet & Berant (2021) showed that existing metrics disagree substantially and correlate poorly with humans [5]. Xu et al. (2022) characterized the diversity-quality Pareto frontier across decoding methods [9]. We extend this by adding the syntactic axis and the quality-correction mechanism, then validating against human judgments.

**Taxonomy proposals.** Gao et al. (2022) proposed a three-tier taxonomy (lexical, syntactic, semantic) [3]; Sai et al. (2022) distinguished form diversity from content diversity [2]. MADEF operationalizes the Gao et al. taxonomy into a practical evaluation framework with explicit metric choices and statistical protocols.

**Human evaluation standards.** van der Lee et al. (2019, 2021) published guidelines for human evaluation of NLG, introducing "variety" as a distinct dimension [16]. MADEF adopts these guidelines and adds the standardized metric battery that they call for.

---

## References

**1.** Celikyilmaz, A., Clark, E., & Gao, J. (2020). Evaluation of Text Generation: A Survey. *arXiv:2006.14786*.

**2.** Sai, A. B., Mohankumar, A. K., & Khapra, M. M. (2022). A Survey of Evaluation Metrics Used for NLG Systems. *ACM Computing Surveys*, 55(2).

**3.** Gao, Y., et al. (2022). A Three-Tier Taxonomy for Diversity Evaluation in NLG. *Findings of ACL*.

**4.** Zhang, J., & Wan, X. (2023). DivFormer: A Transformer-based Framework for Evaluating Diversity in Text Generation. *ACL*.

**5.** Tevet, G., & Berant, J. (2021). Evaluating the Evaluation of Diversity in Natural Language Generation. *EACL*.

**6.** Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. (2020). The Curious Case of Neural Text Degeneration. *ICLR*.

**7.** Caccia, M., Caccia, L., Fedus, W., Larochelle, H., Pineau, J., & Charlin, L. (2020). Language GANs Falling Short. *ICLR*.

**8.** Šuster, S., et al. (2022). The Inherent Trade-off between Quality and Diversity in NLG. *arXiv*.

**9.** Xu, P., et al. (2022). Diversity vs. Quality in Text Generation: A Comprehensive Empirical Study. *EMNLP*.

**10.** De Lucena, A. L. F., et al. (2022). Statistical Significance of Diversity Comparisons in NLG. *EACL*.

**11.** Pillutla, K., Swayamdipta, S., Zellers, R., Thickstun, J., Welleck, S., Choi, Y., & Harchaoui, Z. (2021). MAUVE: Measuring the Gap Between Neural Text and Human Text using Divergence Frontiers. *NeurIPS*.

**12.** Gehrmann, S., et al. (2022). GEM: A General Evaluation Benchmark for Natural Language Generation. *ACL*.

**13.** Hashimoto, T. B., Zhang, H., & Liang, P. (2019). Unifying Human and Statistical Evaluation for Natural Language Generation. *NeurIPS*.

**14.** McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods*, 42(2).

**15.** De Lucena, A. L. F., et al. (2022). Coverage-Based Diversity Metrics for NLG. *EACL Workshop*.

**16.** van der Lee, C., Gatt, A., van Miltenburg, E., & Krahmer, E. (2019/2021). Best Practices for the Human Evaluation of Automatically Generated Text. *INLG 2019 / EACL 2021*.

**17.** Zhang, S., Dinan, E., Urbanek, J., Szlam, A., Kiela, D., & Weston, J. (2018). Personalizing Dialogue Agents: I have a dog, do you have pets too? *ACL*.

**18.** Lin, B. Y., et al. (2020). CommonGen: A Constrained Text Generation Challenge for Generative Commonsense Reasoning. *ACL*.

**19.** Fan, A., Lewis, M., & Dauphin, Y. (2018). Hierarchical Neural Story Generation. *ACL*.

**20.** Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A Diversity-Promoting Objective Function for Neural Conversation Models. *AAAI*.

**21.** Zhu, Y., et al. (2018). Texar: A Modularized, Versatile, and Extensible Toolkit for Text Generation. *ACL System Demonstrations*.

**22.** Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP*.

**23.** Yuan, W., Neubig, G., & Liu, P. (2021). BARTScore: Evaluating Generated Text as Text Generation. *NeurIPS*.

**24.** Meister, C., Pimentel, T., Wiher, G., & Cotterell, R. (2023). Typical Decoding for Natural Language Generation. *ICLR*.

**25.** Li, X. L., Holtzman, A., Fried, D., Liang, P., Hashimoto, T., Zettlemoyer, L., & Lewis, M. (2023). Contrastive Decoding: Open-ended Text Generation as Optimization. *ICLR*.

**26.** Vijayakumar, A. K., Cogswell, M., Selvaraju, R. R., Sun, Q., Lee, S., Crandall, D., & Batra, D. (2018). Diverse Beam Search: Decoding Diverse Solutions from Neural Sequence Models. *ICLR*.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 20 |
| Topic | Text generation |
| Original user goal | Generate a research proposal on the evaluation of diversity in text generation. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_20/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_20/final_report.md` (20182 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_20/prompt.txt` (683 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_20/query.json` (137 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_20/stdout.txt` (10278 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_20/stderr.txt` (251 bytes)

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
