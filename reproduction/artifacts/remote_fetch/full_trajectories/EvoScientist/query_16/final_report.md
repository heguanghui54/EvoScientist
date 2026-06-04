# Structured vs. Unstructured Knowledge Injection in Biomedical LLMs:
# A Controlled Study of Adaptation Architecture and Catastrophic Forgetting

---

## 1. Problem Statement

Domain-specific Large Language Models (e.g., BioMistral, Clinical Camel, Med-PaLM) are typically adapted by fine-tuning a general-purpose base model on biomedical corpora. However, this process faces a fundamental tension: **injecting new domain knowledge risks catastrophic forgetting of the general capabilities that made the base model useful**. Prior work documents this trade-off empirically (Luo et al., 2023; Ovadia et al., 2023), but three critical gaps remain:

1. **No controlled comparison of knowledge formats.** Structured knowledge (knowledge graph triples, ontological relations) and unstructured knowledge (raw biomedical text) differ in density, redundancy, and format. It is unknown which causes less forgetting per unit of injected knowledge, because prior studies compare unequal data quantities and sources.

2. **No consensus on adapter placement.** LoRA-based adaptation is the standard PEFT method, but contradictory findings report that middle layers (Cong et al., 2025), all layers (Hu et al., 2023), only 5% of layers (Bafghi et al., 2025), or gated mixtures (Han et al., 2024) perform best. No study has tested whether the optimal placement interacts with knowledge format.

3. **Biomedical LLMs rarely report general capability retention.** Most biomedical LLM papers report only domain benchmarks (MedQA, PubMedQA) and omit MMLU, GSM8K, or HellaSwag — making the forgetting dimension invisible.

**This proposal addresses all three gaps in a single controlled design.**

---

## 2. Hypothesis

**Primary hypothesis (H1):** Structured knowledge injection (training on text derived from biomedical knowledge graph triples) achieves higher domain knowledge gain per unit of catastrophic forgetting compared to matched-volume unstructured corpus fine-tuning, because structured data presents knowledge in a disentangled, high-signal format that requires fewer parameter updates.

**Secondary hypothesis (H2):** The optimal adapter placement strategy depends on knowledge format — specifically, middle-layer-only adaptation is sufficient for structured knowledge (which encodes compact relational patterns), while unstructured knowledge requires broader adaptation (all-layers or gated mixture) because its patterns are more diffuse.

**Tertiary hypothesis (H3):** Structured injection with optimal adapter placement matches or exceeds a RAG baseline on domain QA while retaining more general capability, demonstrating that fine-tuning and retrieval are complementary rather than competing strategies.

---

## 3. Method

### 3.1 Design: 2 × 3 Factorial + Reference Baselines

| Factor | Levels |
|--------|--------|
| **Knowledge Format** (A) | A1: Structured (KG-derived text) · A2: Unstructured (raw biomedical corpus) |
| **Adapter Strategy** (B) | B1: Middle-only · B2: All-layers · B3: Selective gating (SLIM) |

Each of the 6 conditions is run with 3 random seeds = **18 fine-tuning runs**.

**Reference baselines:** (1) Untuned base model, (2) Full fine-tune on unstructured corpus, (3) RAG-only (no fine-tuning).

### 3.2 Base Model

**Mistral-7B-v0.3** — chosen because:
- It is the base of BioMistral-7B, enabling direct comparison
- 7B is the most studied scale in PEFT literature (majority of prior work)
- It has strong general capabilities (MMLU ~64%), leaving room to measure forgetting

### 3.3 Knowledge Sources (Matched for Content and Volume)

**Both conditions receive the same underlying biomedical knowledge encoded in two formats, matched to within 5% token count:**

**Condition A1 — Structured (KG → Text):**
- Source: **UMLS** (Unified Medical Language System) and **BIOSSES** biomedical KG
- Process: Extract (subject, relation, object) triples from UMLS (e.g., *Metformin, TREATS, Diabetes Mellitus Type 2*)
- Convert each triple to natural language sentences via 3 templates (e.g., *"Metformin is used to treat type 2 diabetes mellitus."*, *"For type 2 diabetes mellitus, one treatment option is metformin."*)
- Filter to the ~500K most clinically relevant triples (ranked by relation frequency in PubMed)
- Final dataset: ~3M sentences, ~50M tokens

**Condition A2 — Unstructured (Raw Corpus):**
- Source: **PubMed Central** open-access subset (same time window as UMLS release)
- Process: Sample biomedical abstracts and article snippets whose entity coverage matches the UMLS triple set (ensured via entity-linking with SciSpacy)
- Filter to sentences containing at least one UMLS entity from the structured set
- Target: ~50M tokens (matched to A1)

This matching ensures that **differences between A1 and A2 are attributable to knowledge format, not knowledge content or volume**.

### 3.4 Adapter Strategies

All three use rank-16 LoRA (α=32, dropout=0.1) on query and value projections.

| Strategy | Implementation | Modules Adapted | Rationale |
|----------|---------------|-----------------|-----------|
| **B1: Middle-only** | LoRA on layers 8–20 of 32 | 13 layers | Middle layers are hypothesized to encode domain-specific patterns (Cong et al., 2025) |
| **B2: All-layers** | LoRA on all 32 layers | 32 layers | Standard practice; maximum capacity (Hu et al., 2023) |
| **B3: Selective gating** | SLIM (Soft LoRA + Identity Mixture) per layer | Gated, ~5-40% active | Learns which layers to adapt; balances capacity and regularization (Han et al., 2024) |

Training: 3 epochs, batch size 16, learning rate 2e-4 (cosine schedule), sequence length 1024, BF16 mixed precision. Single A100-80GB per run (~2-4 hours per condition).

---

## 4. Dataset / Benchmark

### 4.1 Domain Knowledge Evaluation (3 benchmarks)

| Benchmark | Type | Size | Metric | Used By |
|-----------|------|------|--------|---------|
| **MedQA (USMLE)** | Multi-choice QA | 12,723 | Accuracy | Standard medical LLM eval |
| **PubMedQA** | Binary QA (yes/no/maybe) | 1,000 | F1, accuracy | De facto biomedical QA |
| **BioASQ 12b** | Factoid QA | ~500 | F1, SOTA F1 | Biomedical semantic QA |

### 4.2 General Capability Retention (4 benchmarks)

| Benchmark | Capability | Metric | Rationale |
|-----------|-----------|--------|-----------|
| **MMLU** | Broad knowledge + reasoning | Accuracy (5-shot) | De facto standard for general knowledge retention |
| **HellaSwag** | Commonsense reasoning | Accuracy | Tests world knowledge not present in biomedical data |
| **GSM8K** | Math reasoning | Accuracy | Tests whether mathematical reasoning degrades |
| **ARC-Challenge** | Science reasoning | Accuracy | Tests grade-school science (overlap check with biomedical) |

### 4.3 Forgetting Metrics

- **Capability Retention Rate (CRR):** (post-adaptation score / base score) × 100 for each general benchmark
- **Domain Transfer Efficiency (DTE):** Δ domain accuracy / Δ forgetting (↓MMLU) — knowledge per unit forgetting
- **Composite Score:** 0.5 × (mean domain accuracy) + 0.5 × (mean CRR) — balances both objectives

---

## 5. Baselines

| Baseline | Description | Purpose |
|----------|-------------|---------|
| **Untuned Mistral-7B** | Base model, no adaptation | Lower bound for domain, upper bound for general |
| **Full fine-tune** | All parameters, unstructured corpus | Upper bound for domain, lower bound for general |
| **RAG-only** | No fine-tuning; retrieve from PubMed abstracts via Contriever-MSB | Practical alternative; no forgetting by design |
| **BioMistral-7B** | Published biomedical Mistral (Labrak et al., 2024) | External reference point |
| **DoRA (all-layers)** | DoRA adapter on all layers (SOTA LoRA variant) | SOTA adapter comparison |

---

## 6. Ablations

| Ablation | What Is Changed | Why |
|----------|----------------|-----|
| **Ablation 1: Rank scaling** | r = 8, 16, 32 for best condition | Tests sensitivity to adapter capacity |
| **Ablation 2: Template diversity** | 1 template vs. 3 templates for A1 | Tests whether structured format diversity matters |
| **Ablation 3: Data volume** | 25%, 50%, 100% of training data | Tests whether format effects scale with data |
| **Ablation 4: Model scale** | Swap Mistral-7B for Llama-3-8B | Tests generalization to different base architectures |
| **Ablation 5: Sequential FT** | First adapt on structured, then on unstructured | Tests if order of formats matters |

---

## 7. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Mitigation |
|-------------|-----------|------------|
| **No significant difference between A1 and A2** | Moderate | Post-hoc analysis: compute per-entity knowledge density; the format effect may be concentrated in rare entities |
| **All adapter strategies perform similarly** | Moderate | Check whether the biomedical domain is "easy" (high base-model overlap); if so, switch to a more distant domain (e.g., legal) in a follow-up |
| **Forgetting is negligible across all conditions** | Low (contradicts Luo et al.) | If observed, test with longer training (6 epochs) and higher rank (r=64) to force saturation |
| **SLIM collapses to all-layers (no gating)** | Low | Add L1 regularization on gating weights; evaluate entropy of gate distribution |
| **Template-based structured data is unnatural** | Low | Run human evaluation (N=3 clinicians) on naturalness of A1 sentences; compare perplexity vs. A2 |
| **KG triple coverage is sparse** | Moderate | Augment with LLM-generated paraphrases of triple sentences (using GPT-4o with strict factual constraints) |

---

## 8. Execution Plan

### Stage 1: Data Curation (1-2 weeks)
1. Download UMLS and extract clinically relevant triples → filter by relation frequency
2. Download PubMed Central subset; entity-link with SciSpacy to match UMLS coverage
3. Generate structured dataset (3 templates per triple) → verify token count match
4. Validate: sample 200 sentences per condition, check by human annotator for factual correctness

### Stage 2: Implementation & Infrastructure (1 week)
1. Implement adapter strategies using HuggingFace PEFT library
2. Implement SLIM gating module for B3
3. Set up evaluation pipeline: 7 benchmarks × 3 seeds = 21 eval runs per condition
4. Verify reproducibility: run 1 condition with 2 seeds, check variance < 2%

### Stage 3: Main Experiment (1-2 weeks on 4× A100)
1. Run all 6 factorial conditions + 3 baselines (Table 1)
2. Run 5 ablations (rank scaling, template diversity, data volume, model scale, sequential FT)
3. Track: training loss curves, validation perplexity, and 7 benchmark scores per checkpoint

### Stage 4: Analysis (1 week)
1. Compute CRR, DTE, composite score for each condition
2. Two-way ANOVA: Knowledge Format × Adapter Strategy on composite score
3. Post-hoc: Tukey HSD for pairwise comparisons
4. For SLIM: analyze gating distribution per layer — do certain layers consistently gate?
5. Failure mode analysis: on which MedQA sub-topics does each condition fail?

### Stage 5: Reporting (1 week)
1. Produce main results table (6 + 3 conditions × 7 benchmarks)
2. Generate 4 figures: (i) domain vs. general trade-off scatter, (ii) DTE bar chart, (iii) SLIM gate distribution heatmap, (iv) per-topic error analysis
3. Write findings to paper draft (target: ACL Rolling Review or EMNLP 2026)

### Total expected compute: ~50 A100-hours (main) + ~30 A100-hours (ablations)

---

## 9. Expected Contributions

1. **First controlled comparison** of structured vs. unstructured knowledge injection with matched content and volume, answering whether format alone affects the forgetting trade-off.

2. **Empirical test of adapter placement × knowledge format interaction** — providing guidance for practitioners choosing PEFT strategies for domain adaptation.

3. **New evaluation protocol** requiring joint reporting of domain gain AND general capability retention for all domain-specific LLMs (potentially establishable as a standard).

4. **Open-source release** of the matched structured/unstructured biomedical datasets (~50M tokens each) and the evaluation harness.

---

## 10. Related Work (Condensed)

| Work | What It Found | Our Difference |
|------|--------------|----------------|
| Luo et al. (2023) — CF benchmark | CF increases with model scale; 15-task eval protocol | We add the **format** variable and **adapter placement** variable |
| Ovadia et al. (2023) — FT vs. RAG | FT causes more forgetting than RAG | We control for **matched knowledge content** and test **hybrid hypotheses** |
| Bafghi et al. (2025) — Selective LoRA | 5% layers sufficient for downstream tasks | We test whether this holds for **dense domain knowledge** and whether it **interacts with format** |
| Han et al. (2024) — SLIM | Gated layer selection improves PEFT | We test SLIM for **domain adaptation with forgetting constraints** |
| Zhu et al. (2026) — Bio-LoRA | LoRA vs. full FT in biomedical; LoRA preserves 3-8× more MMLU | We test **format × architecture interaction**, not just method vs. method |
| Hong et al. (2025) — SDFT | Structured dialogue for FT improves clinical QA | We compare **structured vs. unstructured at the representation level**, not dialogue format |

---

*Proposal generated: 2026-06-04.*

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 16 |
| Topic | Knowledge injection |
| Original user goal | Generate a research proposal on addressing the challenges of knowledge injection in domain-specific Large Language Models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_16/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_16/final_report.md` (13228 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_16/prompt.txt` (726 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_16/query.json` (184 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_16/stdout.txt` (8560 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_16/stderr.txt` (251 bytes)

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
