# CrossLingual-RAG: Cross-Lingual Retrieval-Augmented Generation for Extremely Low-Resource Machine Translation

**Research proposal · June 2026**

---

## 1. Summary & Goals

### Problem Statement

Despite the success of multilingual NMT models covering 200+ languages (NLLB, Costa-jussà et al., 2024), over 40 of those languages still achieve fewer than 10 spBLEU — output that is often unintelligible to native speakers. The core bottleneck is parallel data scarcity: languages with <100K parallel sentences cannot train fluent models, and for most of the world's 7,000+ languages, no significant parallel data exists at all.

A pervasive but underexploited fact is that **extremely low-resource languages almost always have a genetically related higher-resource language**. Quechua is related to Aymara; Mam is related to K'iche'; Wolof is related to Fula; and many more. While cross-lingual transfer learning has been studied for NMT (Lin et al., ACL 2021; Pfeiffer et al., EMNLP 2021), prior work uses transfer only during training — it has not been applied at **inference time** through retrieval augmentation.

### Core Idea

We propose **CrossLingual-RAG**, a retrieval-augmented NMT framework that, when translating from an extremely low-resource source language $L_x$ into English, retrieves $k$-nearest neighbors from a **related higher-resource language $L_y$** parallel datastore. A cross-lingual sentence encoder (SONAR / LASER3) maps both $L_x$ and $L_y$ sentences into a shared embedding space, and a gated adapter module in the decoder selectively attends to retrieved $L_y$→English examples. When the cross-lingual signal is weak (distant languages), a learned gating mechanism falls back to standard decoding.

### Research Questions

1. **RQ1**: Can retrieving from a related language's parallel datastore (rather than the same language's) improve translation quality for extremely low-resource languages?
2. **RQ2**: What is the relationship between language distance (genetic, typological) and the effectiveness of cross-lingual retrieval?
3. **RQ3**: How does cross-lingual RAG compare with, and complement, standard same-language RAG and transfer learning?
4. **RQ4**: Can a lightweight adapter-based architecture enable effective cross-lingual retrieval without full model fine-tuning?

### Success Criteria

- **Primary**: ≥+3 spBLEU improvement over a strong mBART-50/NLLB-600M baseline on held-out extremely low-resource FLORES-200 languages (those with <100K parallel sentences)
- **Secondary**: A quantitative **language distance threshold** beyond which cross-lingual retrieval degrades performance
- **Ablations**: Component contributions (retrieval source language, $k$ value, adapter architecture, gating mechanism) measured independently

---

## 2. Related Work & Gaps

### Retrieval-Augmented NMT (kNN-MT)

Khandelwal et al. (NeurIPS 2021) introduced kNN-MT: at each decoding step, retrieve $k$ nearest neighbors from a parallel datastore and interpolate the NMT output distribution with a nearest-neighbor distribution. Consistent gains of +2–8 BLEU across language pairs. Subsequent work extends kNN-MT with adaptive interpolation (Zheng et al., ACL 2023), efficient datastore pruning (Wang et al., EMNLP 2023), and domain adaptation (Jiang et al., ACL 2022).

**Critical gap**: All kNN-MT variants retrieve from the **same language pair** as the translation direction. For extremely low-resource languages with tiny datastores, nearest neighbors are poor or non-existent — the very condition where RAG could help most.

### Cross-Lingual Transfer for NMT

Lin et al. (ACL 2021) showed that choosing auxiliary languages by **genetic distance** significantly affects transfer quality. MAD-X (Pfeiffer et al., EMNLP 2021) demonstrated parameter-efficient cross-lingual transfer via adapters, training only ~5% new parameters per language pair. Alves et al. (ACL 2023) showed that mBART-50 + 5K fine-tuning sentences yields 10–15 BLEU vs. 0–5 zero-shot.

**Gap**: All these methods transfer at training time. No work has explored **inference-time transfer via retrieval** — i.e., leveraging a related language's datastore at test time.

### Cross-Lingual Sentence Encoders

LASER (Artetxe & Schwenk, ACL 2019), LASER3 (Heffernan et al., ACL 2022), and SONAR (Duquenne et al., EMNLP 2023) provide multilingual sentence embeddings aligned across languages. SONAR supports 200 languages with strong cross-lingual retrieval performance on mining tasks.

**Relevance**: These encoders provide the shared representation space needed for cross-lingual retrieval — but none have been combined with kNN-MT.

### Summary of the Gap

| Approach | Transfer Timing | Datastore Language | Limitation |
|----------|----------------|-------------------|------------|
| Multilingual NMT | Training | All languages | Bulk update; negative transfer |
| Adapter transfer | Training | N/A | Same as above |
| kNN-MT | Inference | Same language pair | No help for extremely low-resource |
| **CrossLingual-RAG (ours)** | **Inference** | **Related language** | Requires aligned embeddings |

---

## 3. Proposed Method

### 3.1 Architecture

CrossLingual-RAG consists of four components:

1. **Base NMT model**: A pre-trained multilingual encoder-decoder (mBART-50 or NLLB-600M) fine-tuned on the target low-resource language pair $L_x$→En.
2. **Cross-lingual datastore**: A key-value store where keys are SONAR embeddings of sentences in a **related higher-resource language** $L_y$, and values are the corresponding English translations.
3. **Retrieval module**: At each decoding step $t$, queries the datastore with the current decoder hidden state $h_t$, retrieves $k$ nearest neighbors from $L_y$ sources, and constructs a $k$-nearest-neighbors distribution $p_{\text{kNN}}(y_t \mid x, y_{<t})$.
4. **Gated adapter**: A learned gate $g_t = \sigma(W_g h_t + b_g)$ that interpolates between the base NMT distribution $p_{\text{NMT}}$ and the cross-lingual kNN distribution:

   $$p(y_t) = (1 - g_t) \cdot p_{\text{NMT}}(y_t) + g_t \cdot p_{\text{kNN}}(y_t)$$

### 3.2 Cross-Lingual Retrieval Mechanism

**Key challenge**: The decoder state $h_t$ is generated from $L_x$ input, but we are retrieving from $L_y$ keys. We propose two variants:

- **Variant A — Shared-Encoder Retrieval**: Embed all $L_y$ sentences with SONAR to build the datastore. At inference, embed the $L_x$ source sentence with the same SONAR encoder, and retrieve $k$ nearest $L_y$ sentences. This is a **sentence-level** retrieval (one retrieval per sentence) — simpler but less expressive.

- **Variant B — Decoder-State Retrieval**: Project decoder hidden states $h_t$ into the SONAR embedding space via a learned projection layer $P$, then retrieve token-level neighbors. This is a **token-level** retrieval matching the original kNN-MT formulation but with cross-lingual keys.

**Initial design choice**: Start with Variant A (sentence-level retrieval) for simplicity and address token-level retrieval in an ablation.

### 3.3 Gating Mechanism

The gate $g_t$ serves a critical role: when the retrieved $L_y$ neighbors are semantically distant from the $L_x$ source (e.g., distantly related languages), the gate should down-weight the kNN distribution to avoid noise. The gate is trained end-to-end on the fine-tuning data.

We hypothesize that the gate learns to encode **language distance implicitly** — languages that are closely related will yield higher $g_t$ values on average, while distant languages will yield lower values.

### 3.4 Language Selection for Cross-Lingual Retrieval

For each target low-resource language $L_x$, we select a related language $L_y$ using genetic language family trees (Glottolog) and typological features (WALS, URIEL):

| Low-Resource Language $L_x$ | Related Language $L_y$ | Family | $L_y$ Parallel Data Size |
|----------------------------|----------------------|--------|------------------------|
| Quechua (S Bolivia) | Quechua (Cusco) / Aymara | Quechuan / Aymaran | ~500K / ~100K |
| Mam | K'iche' | Mayan | ~200K |
| Wolof | Fula / Hausa | Atlantic / Chadic | ~500K / ~5M |
| Kamba | Swahili | Bantu | ~10M |
| Yiddish | German | Germanic | ~20M |
| Uyghur | Turkish | Turkic | ~3M |
| Amharic | Arabic | Semitic | ~10M |
| Inuktitut | Greenlandic | Eskimo-Aleut | ~500K |
| Ilocano | Tagalog | Austronesian | ~5M |
| Sinhala | Tamil | Indo-Aryan / Dravidian | ~3M |

We also compare against a **control condition**: retrieving from an unrelated language (e.g., English or Chinese) to verify that language relatedness, not just any extra data, drives improvement.

---

## 4. Experimental Design

### 4.1 Benchmarks

| Benchmark | Languages | Metric | Rationale |
|-----------|-----------|--------|-----------|
| FLORES-200 devtest | All 40+ low-resource languages | spBLEU, CHRF, COMET-22 | Standardized evaluation; many related-language pairs |
| AmericasNLP 2023 | 10 indigenous → Spanish | spBLEU, CHRF | Indigenous languages with clear language relatives |
| IWSLT 2023 Amharic→English | Amharic→En | spBLEU, CHRF | Contested low-resource track with known baselines |

### 4.2 Baselines

| Baseline | Description |
|----------|-------------|
| **NLLB-600M (frozen)** | Off-the-shelf NLLB, no fine-tuning |
| **NLLB-600M (fine-tuned)** | Fine-tuned on $L_x$→En parallel data |
| **mBART-50 (fine-tuned)** | Fine-tuned on $L_x$→En parallel data |
| **kNN-MT (same-language)** | Standard kNN-MT with $L_x$ datastore |
| **CrossLingual-RAG (ours)** | Our method with $L_y$ datastore |
| **GPT-4 / Llama-3 (few-shot)** | LLM prompting with 5 in-context examples |

### 4.3 Experimental Stages

#### Stage 1: Datastore Construction & Encoding (Week 1–2)
- Extract parallel data for related language pairs from NLLB-Seed, CCMatrix, and WikiMatrix
- Encode all $L_y$ source sentences with SONAR (2048-dim embeddings) — store as FAISS index
- **Success signal**: Mean reciprocal rank (MRR) at 10 for cross-lingual retrieval ≥ 0.5

#### Stage 2: Baseline Fine-Tuning (Week 2–3)
- Fine-tune NLLB-600M on each target language $L_x$'s available parallel data
- Train NLLB-600M + same-language kNN-MT (following Khandelwal et al., 2021)
- **Success signal**: Fine-tuned model achieves ≥2 spBLEU over frozen baseline

#### Stage 3: CrossLingual-RAG Training (Week 3–5)
- Implement gated adapter module (Variant A: sentence-level retrieval)
- Fine-tune on $L_x$ data with cross-lingual retrievals from $L_y$
- Train gate parameters end-to-end with standard NMT loss
- **Success signal**: CrossLingual-RAG ≥+3 spBLEU over fine-tuned baseline on development set

#### Stage 4: Ablations & Analysis (Week 5–7)
- Ablate retrieval source language ($L_y$ choice)
- Ablate $k$ (number of neighbors: 1, 4, 8, 16, 32)
- Ablate adapter design (Variant A vs B, projection dimension)
- Ablate gating (with vs. without learned gate; fixed vs. learned interpolation)
- **Success signal**: Each component shows statistically significant contribution

#### Stage 5: Language Distance Analysis (Week 7–8)
- Plot $\Delta$BLEU against language distance metrics:
  - Genetic distance (from Glottolog phylogeny)
  - Typological distance (URIEL feature cosine similarity)
  - Embedding distance (SONAR cosine between language centroids)
- Identify threshold beyond which cross-lingual retrieval is detrimental
- **Success signal**: Clear monotonic or threshold relationship identified

#### Stage 6: Comparison with LLM Baselines (Week 8–9)
- Evaluate GPT-4 and Llama-3-70B with 5-shot prompting on same test sets
- Compare CrossLingual-RAG against LLM outputs using COMET and human evaluation (fluency + adequacy)
- **Success signal**: CrossLingual-RAG matches or exceeds GPT-4 on target languages

### 4.4 Expected Artifacts

- CrossLingual-RAG adapter module implementation (Fairseq2 / HuggingFace)
- FAISS datastores for 10 related-language pairs
- Fine-tuned model checkpoints with adapter weights
- Full evaluation results (spBLEU, CHRF, COMET) on FLORES-200 and AmericasNLP
- Language distance vs. $\Delta$BLEU analysis with figures
- Ablation tables for all architectural choices
- Human evaluation results (fluency + adequacy, 100 sentences per language)

---

## 5. Evaluation Protocol

### Metrics
- **spBLEU**: Using the FLORES-200 tokenizer (sentencepiece BPE); report 95% confidence intervals via bootstrap resampling
- **CHRF**: Character n-gram F-score (Popović, 2015); required for morphologically rich languages
- **COMET-22**: Reference-based neural metric (Rei et al., ACL 2022); covers semantic adequacy
- **Human evaluation**: For top-3 languages, 100 sentences rated by 2 native speakers each on 1–5 fluency and 1–5 adequacy (following WMT guidelines)

### Statistical Rigor
- Each condition run with 3 random seeds
- Paired bootstrap resampling for significance ($p < 0.05$)
- Multiple-testing correction (Bonferroni) across language pairs

### Data Splits
- If FLORES dev and devtest: use devtest for evaluation, dev for validation
- Otherwise: 80/10/10 stratified split; ensure no document overlap

---

## 6. Potential Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Cross-lingual embeddings are too noisy for token-level retrieval | Medium | Start with sentence-level retrieval (Variant A); only attempt Variant B if A succeeds |
| Gate collapses to always-on or always-off | Low | Add gate regularization ($L2$ on $g_t$) and visualize gate values per language |
| Nearest neighbors from $L_y$ are unrelated to $L_x$ source | Medium | Use genetic distance as prior filter — only languages within threshold family |
| Base NMT model (NLLB-600M) already saturates | Low | Target languages with <10 spBLEU in NLLB eval results |
| LLMs (GPT-4) outperform our method | Low-Medium | Frame contribution as efficiency + specialized quality; LLMs are 100-1000× costlier |

---

## 7. Timeline (9 Weeks)

```
Week 1-2    Stage 1: Datastore construction & encoding
Week 2-3    Stage 2: Baseline fine-tuning
Week 3-5    Stage 3: CrossLingual-RAG training
Week 5-7    Stage 4: Ablations
Week 7-8    Stage 5: Language distance analysis + LLM comparison
Week 8-9    Stage 6: Human evaluation + paper writing
```

---

## 8. Contributions & Expected Impact

### Contributions

1. **First cross-lingual retrieval-augmented NMT framework**: We show that retrieving from a related language's parallel datastore at inference time improves translation for extremely low-resource languages — a novel direction bridging cross-lingual transfer and RAG.

2. **Language distance threshold for cross-lingual RAG**: A quantitative analysis establishing when cross-lingual retrieval helps, when it hurts, and how to select optimal retrieval languages automatically.

3. **Gated cross-lingual adapter**: A lightweight, parameter-efficient architecture that integrates cross-lingual retrieval with a learned gating mechanism, requiring <5% new parameters.

4. **Comprehensive evaluation on 10+ languages**: Including FLORES-200, AmericasNLP, and IWSLT benchmarks, with both automatic and human evaluation.

5. **Open-source release**: Model adapter, datastore construction scripts, and evaluation pipeline.

### Expected Venues

- **Primary**: ACL Rolling Review (ARR) → ACL/EMNLP/NAACL 2027
- **Alternative**: EACL 2027 or IWSLT (if more systems-oriented)

---

## 9. Prior Work & References

- Costa-jussà, M. R., et al. (2024). No Language Left Behind: Scaling Human-Centered Machine Translation. *Nature*.
- Fan, A., et al. (2021). Beyond English-Centric Multilingual Machine Translation. *ICLR 2021*.
- Khandelwal, U., et al. (2021). Nearest Neighbor Machine Translation. *NeurIPS 2021*.
- Lin, Z., et al. (2021). Choosing Transfer Languages for Cross-Lingual Learning. *ACL 2021*.
- Pfeiffer, J., et al. (2021). MAD-X: An Adapter-Based Framework for Multi-Task Cross-Lingual Transfer. *EMNLP 2021*.
- Artetxe, M. & Schwenk, H. (2019). Massively Multilingual Sentence Embeddings for Zero-Shot Cross-Lingual Transfer and Beyond. *ACL 2019*.
- Heffernan, K., et al. (2022). Bitext Mining Using Distilled Sentence Representations for Low-Resource Languages. *ACL 2022*.
- Duquenne, P. A., et al. (2023). SONAR: Sentence-Level Multimodal and Language-Agnostic Representations. *EMNLP 2023*.
- Robinson, N., et al. (2023). Large Language Models are not Zero-Shot Translators for Low-Resource Languages. *EMNLP 2023 Findings*.
- Alves, D. M., et al. (2023). Low-Resource Machine Translation with Large Language Models. *ACL 2024*.
- Zheng, Z., et al. (2023). Adaptive Nearest Neighbor Machine Translation. *ACL 2023*.

---

*Proposal generated June 2026. Citations should be verified against Semantic Scholar before submission.*

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 01 |
| Topic | Machine translation |
| Original user goal | Generate a research proposal on low-resource machine translation. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_01/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_01/final_report.md` (16755 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_01/prompt.txt` (66 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_01/query.json` (126 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_01/stdout.txt` (10847 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_01/stderr.txt` (251 bytes)

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
