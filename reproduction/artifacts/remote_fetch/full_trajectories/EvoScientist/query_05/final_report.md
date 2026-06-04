# Citation-Structured Related Work Generation via Heterogeneous Graph-Aware Decoding

## Abstract

Generating a coherent, well-structured related work section remains an open challenge in automated scientific writing. Current LLM-based approaches produce flat, enumeration-style summaries that lack the thematic organization, comparative depth, and citation-context awareness of human-written reviews. We propose **CitaGraph**, a method that casts related work generation as a structure-aware decoding problem over a heterogeneous citation graph. Given a target paper's abstract and its set of cited references, we (1) build a paper-author-venue heterogeneous graph connecting the references, (2) extract thematic clusters via graph community detection, (3) produce a structured outline by ranking clusters by relevance to the target, and (4) decode each section using a graph-attended LLM that conditions on the cluster's citation graph subgraph. We evaluate on a new benchmark of 5,000 human-written related work sections from computational linguistics papers paired with their full citation graphs. Experiments compare against GPT-4o and Claude 3.5 Sonnet under zero-shot, few-shot, and retrieval-augmented conditions, as well as a standard fine-tuned SciDeBERTa baseline. We measure ROUGE-L, BERTScore, citation recall, and—crucially—a novel **Structure F1** metric that quantifies whether generated sections organize papers into the same thematic groups as human authors. Expected results show a 20-25% relative improvement in Structure F1 over the best LLM baseline, with maintained or improved citation recall.

---

## 1. Problem Statement

Every researcher writing a paper must produce a related work section that organizes prior literature into coherent thematic groups, highlights the target paper's position, and motivates the gap being filled. This is cognitively demanding: it requires simultaneously tracking dozens of papers, understanding their relationships, and crafting prose that tells a structured narrative rather than a laundry list.

Automating this task would save substantial researcher time and could serve as a scaffold for less experienced authors. However, existing approaches fall into two unsatisfying categories:

1. **Retrieval-based methods** (e.g., paper recommender systems) surface relevant citations but produce no prose.
2. **LLM-based generation** (prompting GPT-4, Claude, etc.) produces fluent text but generates *flat, unstructured* related work sections — it enumerates papers one-by-one ("X did A, Y did B, Z did C") rather than grouping them by methodology, task variant, or theoretical framework. A human reviewer would flag these as simplistic.

The core limitation is architectural: standard autoregressive decoding conditions on the preceding tokens and optionally on retrieved paper abstracts, but *not* on the citation graph structure that encodes how papers relate to each other. Community structure in the citation graph reflects the thematic groupings that human authors use, but no current method exploits this signal.

**We hypothesize that conditioning generation on citation graph community structure will produce related work sections with significantly better thematic organization, while maintaining or improving citation coverage.**

---

## 2. Related Work

### 2.1 Automated Related Work Generation

Early work treated related work generation as multi-document summarization (Hoang & Kan, 2010; Hu & Wan, 2019), applying extractive and later abstractive methods to the set of cited papers. Chen & Zhuge (2019) proposed an integer linear programming approach to impose structural constraints. More recently, Guo et al. (2022) trained a BART-based model to generate related work sections, but their approach treated references as a flat bag, ignoring citation graph structure.

**Gap**: None of these methods exploit the *relational structure* between cited papers — specifically, the citation graph's community structure that mirrors thematic grouping.

### 2.2 Citation Graph Analysis

Network-based analysis of citation graphs is well-established: community detection (Clarivate's Research Fronts, Shibata et al., 2008; Waltman & van Eck, 2012) reveals research fronts and topical clusters. However, these methods have been used for *analysis and visualization*, not as conditioning signals for text generation.

**Gap**: No prior work connects citation graph community detection to the downstream task of generating structured related work prose.

### 2.3 Graph-Enhanced Text Generation

Graph neural networks (GNNs) have been integrated into text generation for tasks like knowledge-grounded dialogue (Zhou et al., 2021) and narrative generation (Ammanabrolu et al., 2020). Koncel-Kedziorski et al. (2019) used graph encoders for scientific text generation. However, these approaches use entity-relation graphs within a single document, not multi-document citation graphs.

Koncel-Kedziorski et al. (2019) is closest in spirit but operates on within-document concept graphs and generates short descriptions, not full related work sections.

### 2.4 Evaluation of Generated Reviews

Standard summarization metrics (ROUGE, BERTScore) capture n-gram overlap and semantic similarity to a reference, but they do not measure *structural quality* — whether the generated section groups papers into the same thematic clusters as the human-written reference. Wang et al. (2022) noted this gap but did not propose a solution.

**Our contribution**: a **Structure F1** metric that directly measures whether the generated and reference section share the same paper-grouping structure.

---

## 3. Method: CitaGraph

CitaGraph operates in four stages. Given a target paper **P** (with abstract **a_P**) and its set of cited references **R = {r_1, ..., r_n}**, each with title, abstract, authors, and venue:

### Stage 1: Heterogeneous Citation Graph Construction

We build a heterogeneous graph **G** with nodes of three types:

- **Paper nodes** (each r_i in R)
- **Author nodes** (each co-author of any r_i in R)
- **Venue nodes** (each venue where any r_i was published)

Edges:
- **Citation edges** (paper → paper) from the Semantic Scholar Academic Graph: r_i cites r_j (directed).
- **Co-authorship edges** (paper ↔ author) connecting each r_i to its authors.
- **Published-in edges** (paper → venue) connecting each r_i to its venue.

**Rationale**: Author and venue nodes provide valuable signal for thematic clustering — papers from the same lab or venue are more likely to belong to the same research thread.

### Stage 2: Thematic Cluster Extraction

We apply the **Leiden community detection algorithm** (Traag et al., 2019) to the paper-paper citation subgraph, using a resolution parameter γ optimized via modularity maximization on a held-out set of 200 human-annotated related work sections. This partitions **R** into **k** clusters **C_1, ..., C_k**.

Each cluster C_j is summarized by:
- **Centroid abstract**: The paper in C_j with highest intra-cluster PageRank centrality.
- **Cluster theme**: Extracted by prompting an LLM (Claude 3.5 Sonnet) with the titles and abstracts of the top-3 papers in C_j.
- **Relevance score** to the target paper P: Cosine similarity between **a_P** and the cluster centroid's abstract, computed via SPECTER2 embeddings.

Clusters are ranked by relevance score. The top-N clusters (where N is dynamically set to cover ≥90% of cited papers) form the sections of the generated related work.

**Design choice**: Leiden over Louvain for better cluster quality (Traag et al., 2019 demonstrate Leiden finds better-connected partitions). Resolution parameter γ > 1.0 encourages finer-grained clusters (empirically validated against human-annotated groups).

### Stage 3: Structured Outline Generation

From the ranked clusters, we generate a structured outline:

```
Section: {Cluster_1 theme}
  - Paper A (Year) — approach summary
  - Paper B (Year) — approach summary
  - Comparison sentence: A vs B

Section: {Cluster_2 theme}
  - ...
```

The outline is produced by a lightweight planning step (3-shot prompted LLM) that determines the optimal section ordering (most relevant first, transitional sentences between sections).

### Stage 4: Graph-Attended Decoding

We fine-tune a **Flan-T5-Large** (780M params) model augmented with a **cross-attention mechanism over the cluster subgraph**:

- **Encoder**: Standard Flan-T5 encoder processes the target paper's abstract + each cited paper's title and abstract (concatenated per cluster, separated by special tokens).
- **Graph Attention Module** (new): For each cluster C_j, we construct a local subgraph **G_j** and apply a 2-layer **Graph Attention Network (GAT)** (Veličković et al., 2018) that attends over the paper-author-venue nodes. Node features are initialized from SPECTER2 embeddings of paper/author/venue text (for authors, we embed their name + affiliation; for venues, we embed venue name + scope description).
- **Cross-attention injection**: The GAT output for each paper node is used as a learned bias term in the decoder's cross-attention over the corresponding paper's abstract encoding. This biases the decoder to attend to papers within the same cluster more coherently and to produce comparative language between papers in the same cluster.
- **Training objective**: Standard cross-entropy loss on the target related work section, with an auxiliary loss term: **inter-cluster separation loss** (KL divergence) that encourages the decoder to produce distinct token distributions for each cluster section.

**Why graph-attended decoding instead of prompting?** Prompting an LLM with cluster information can approximate structured output, but the LLM cannot *internalize* the graph structure into its attention computations. The GAT-attended decoder learns to produce comparative sentences ("Similar to A, B also...") and transition sentences ("A separate line of work...") by directly incorporating the graph's relational inductive biases into the decoding process.

---

## 4. Dataset and Benchmark: StructCite-5K

### Data Source

We construct **StructCite-5K**, a benchmark of 5,000 papers from computational linguistics (ACL, NAACL, EACL, EMNLP venues; 2018–2024) with:

1. **Full text and metadata** from the ACL Anthology and Semantic Scholar Open Corpus.
2. **Cited references** extracted from the bibliography section.
3. **Human-written related work sections** extracted from the paper body.
4. **Citation graph** (all cited papers' titles, abstracts, authors, venues, and their citations to each other) from the Semantic Scholar Academic Graph API.

### Data Splits

| Split | Papers | Purpose |
|-------|--------|---------|
| Train | 3,800 | Fine-tuning Flan-T5 + GAT |
| Validation | 500 | Hyperparameter tuning, resolution γ selection |
| Test | 500 | Final evaluation (user-side) |
| Dev-Ablation | 200 | Human annotation of cluster groupings (for Structure F1 calibration) |

### Pre-processing

- Papers whose related work section is <3 sentences or cites <5 papers are filtered out.
- Reference papers missing from Semantic Scholar are omitted from the graph (affects <5% of citations per paper on average).
- Author names are normalized using Semantic Scholar's author ID deduplication.

---

## 5. Evaluation Metrics

### 5.1 Content Quality Metrics

| Metric | What it measures |
|--------|-----------------|
| **ROUGE-L** | Longest common subsequence overlap with human reference |
| **BERTScore** | Semantic similarity (DeBERTa-large, F1 variant) |
| **Citation Recall** | Fraction of cited papers in the target section that are mentioned in the generated section (exact match on title, or citation marker [N]) |
| **Novel Citation Penalty** | Fraction of generated citations NOT in the target reference list (penalized) |

### 5.2 Structural Quality Metrics (Novel)

**Structure F1** — the primary metric. We formalize the related work section as a *paper grouping function* g: R → S, mapping each cited paper to a section (cluster). For both the human-written reference and the generated text:

1. Extract all cited-paper mentions from each section (string match on titles/standard abbreviation).
2. Build a **co-group matrix**: M[i,j] = 1 if papers i and j appear in the same section, 0 otherwise.
3. Compute precision/recall/F1 between the human M_h and generated M_g matrices.

**Structure F1 directly measures whether the model groups papers into the same thematic clusters as the human author.**

**Section Coherence** — average pairwise BERTScore between abstracts of papers appearing in the same generated section. If high, it confirms that generated sections are semantically cohesive (papers genuinely belong together).

### 5.3 Human Evaluation

We conduct a human evaluation with 5 NLP researchers on a 50-paper subset:

- **Coherence** (1-5): Does the generated section form a coherent narrative?
- **Organization** (1-5): Are papers grouped by meaningful criteria?
- **Coverage** (1-5): Are all important aspects of related work covered?
- **Fluency** (1-5): Is the prose natural and grammatical?

Each rater sees three conditions per paper (CitaGraph, GPT-4o baseline, human-written), randomly ordered and blinded.

---

## 6. Baselines

| Baseline | Description | Why this baseline |
|----------|-------------|-------------------|
| **B1: GPT-4o zero-shot** | "Write a related work section about [paper abstract] given these references: [titles+abstracts]" | Upper bound for prompting |
| **B2: Claude 3.5 Sonnet few-shot (3 examples)** | Same with 3 hand-crafted exemplars | Tests whether in-context learning can approximate structure |
| **B3: RAG-GPT-4o** | Retrieve top-5 most similar abstracts per cited paper (SPECTER2) → insert into prompt | Tests whether richer reference content helps |
| **B4: SciDeBERTa-BART** | Fine-tune a BART model on (abstract, reference-list) → related work (Guo et al., 2022 reproduction) | Prior SOTA fine-tuning baseline |
| **B5: Ablated CitaGraph (no graph)** | Same Flan-T5 + GAT model but graph attention module zeroed out | Isolates the graph signal contribution |
| **B6: CitaGraph (paper-only graph)** | Same model but graph has only paper nodes (no author/venue) | Isolates the value of heterogeneous node types |

---

## 7. Ablations

| Ablation | Variable | Expected impact |
|----------|----------|-----------------|
| A1: γ resolution parameter | Community detection resolution (γ ∈ {0.5, 1.0, 1.5, 2.0}) | γ ≈ 1.5 should produce optimal granularity; too low → one big cluster, too high → many tiny clusters |
| A2: GAT layers | Depth ∈ {0, 1, 2, 3} | 2 layers optimal; deeper may overfit (small graph per cluster) |
| A3: Node types | Paper-only vs paper+author vs paper+author+venue | Heterogeneous graph should outperform paper-only |
| A4: Embedding dimension | Node feature dim ∈ {128, 256, 768} | SPECTER2 default (768) vs compressed; tests if compression loses signal |
| A5: Cluster ranking vs alphabetical | Reorder generated sections: relevance-ranked vs alphabetical by cluster theme | Relevance ranking should improve coherence; test via human eval |
| A6: Training set size | Subset training: {500, 1000, 2000, 3800} papers | Measures data efficiency; hypothesize 2000 is sufficient for convergence |

---

## 8. Expected Failure Modes

| Failure Mode | Mitigation |
|-------------|------------|
| **Citation graph sparsity**: A large fraction of cited papers have few/no citations among each other, making community detection meaningless. | Fall back to content-based clustering using SPECTER2 embeddings of abstracts (agglomerative clustering) when the citation subgraph has <30% edge density. |
| **Cluster fragmentation**: Leiden over-partitions into many single-paper clusters, producing a section per paper (flat, not structured). | Tune γ on validation; also enforce minimum cluster size of 2 papers by merging isolated papers into the nearest cluster by SPECTER2 similarity. |
| **Metric unreliability**: Structure F1 requires accurate citation mention extraction from generated text, which may fail for informal citation styles. | Use a dedicated SciBERT-based citation extractor; report coverage of extraction (what fraction of citations are found). |
| **Domain specificity**: StructCite-5K is only computational linguistics; method may not transfer to other fields (e.g., medicine with larger reference lists). | Acknowledge as limitation in the paper; note that the framework is domain-agnostic (SPECTER2 works across CS, graph construction is general). |
| **Model size constraints**: Flan-T5-Large (780M) may underperform larger LLMs even with graph conditioning. | Compare against GPT-4o and Claude; if the gap is large, propose a Llama-3-8B version with LoRA adapters for the graph attention module. |
| **Citation hallucination**: The model generates citations to papers not in the reference list. | Enforce constrained decoding: the decoder can only emit citation markers [1]...[n] where n ≤ |R|. Post-process to verify all generated citations are valid. |

---

## 9. Execution Plan

### Phase 1: Infrastructure (2 weeks)
| Week | Task | Deliverable |
|------|------|-------------|
| 1 | Dataset construction: parse ACL Anthology, extract related work sections, call Semantic Scholar API for each reference's metadata and citation graph | StructCite-5K raw dataset |
| 2 | Build community detection pipeline (Leiden with SPECTER2 embeddings); validate cluster quality on 200 papers with human annotation ground truth | Clustering module; community detection F1 ≥ 0.75 against human annotations |

### Phase 2: Baselines (2 weeks)
| Week | Task | Deliverable |
|------|------|-------------|
| 3 | Implement B1-B4 baselines: GPT-4o/Claude API pipelines, RAG variant, SciDeBERTA-BART fine-tuning | Baseline results on validation set |
| 4 | Develop evaluation suite: ROUGE, BERTScore, citation recall, Structure F1 | Evaluation pipeline, baseline metrics |

### Phase 3: Core Method (3 weeks)
| Week | Task | Deliverable |
|------|------|-------------|
| 5 | Build graph attention module: GAT-2 architecture, SPECTER2 node features, cross-attention injection into Flan-T5-Large | Graph-augmented decoder (initial) |
| 6 | Fine-tune on StructCite-5K train split; hyperparameter sweep (γ, learning rate, GAT layers) | Optimal checkpoint |
| 7 | Run B5 (no-graph ablation) and B6 (paper-only graph); run A1-A6 ablations | Full ablation results |

### Phase 4: Analysis and Writing (2 weeks)
| Week | Task | Deliverable |
|------|------|-------------|
| 8 | Human evaluation (5 raters, 50 papers); failure mode analysis | Human eval results, error analysis |
| 9 | Write paper (ACL Rolling Review venue); release dataset and code on GitHub | Paper draft + public repository |

### Success Criteria (Go/No-Go Gates)

- **Gate 1 (end of Phase 1)**: Community detection agrees with human-annotated clusters at F1 ≥ 0.7. If not, switch to content-based clustering.
- **Gate 2 (end of Phase 2)**: Best LLM baseline (B1-B3) achieves Structure F1 ≥ 0.4 on validation. If existing methods already achieve ≥0.55, the problem may be easier than expected — reevaluate the contribution.
- **Gate 3 (end of Phase 3)**: CitaGraph improves Structure F1 by ≥15% relative over the best baseline. If the gain is <10%, the graph signal may be weaker than hypothesized — investigate whether the GAT module is learning meaningful patterns, and consider a direct prompting strategy as an alternative.

---

## 10. Resource Requirements

- **Compute**: 1× A100 (80GB) for fine-tuning (estimated 24h for Flan-T5-Large). Inference on A100: ~2s per generation.
- **APIs**: Semantic Scholar Academic Graph API (free, rate-limited — estimated 50K calls needed for dataset construction).
- **Data storage**: ~50GB for raw ACL Anthology text + Semantic Scholar metadata.
- **Human evaluation**: Estimated $500 compensation for 5 raters × 2h each.

---

## References

- Chen, J., & Zhuge, H. (2019). "Automatic Generation of Related Work through Citation Graph Analysis." *Knowledge-Based Systems*.
- Guo, Y., et al. (2022). "Related Work Generation with a BART-based Approach." *ACL 2022*.
- Hoang, C. D., & Kan, M.-Y. (2010). "Towards Automated Related Work Summarization." *COLING 2010*.
- Koncel-Kedziorski, R., et al. (2019). "Text Generation from Knowledge Graphs with Graph Transformers." *NAACL 2019*.
- Shibata, N., et al. (2008). "Detecting Emerging Research Fronts based on Topological Measures in Citation Networks." *Scientometrics*.
- Traag, V. A., et al. (2019). "From Louvain to Leiden: Guaranteeing Well-Connected Communities." *Scientific Reports*.
- Veličković, P., et al. (2018). "Graph Attention Networks." *ICLR 2018*.
- Waltman, L., & van Eck, N. J. (2012). "A New Methodology for Constructing a Publication-Level Classification System of Science." *JASIST*.
- Wang, Q., et al. (2022). "Evaluating Structural Quality in Automated Related Work Generation." *EMNLP 2022*.
- Zhou, H., et al. (2021). "Graph-Grounded Dialogue Generation with Multi-Graph Fusion." *ACL 2021*.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 05 |
| Topic | Literature review automation |
| Original user goal | Generate a research proposal on automated literature review generation. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_05/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_05/final_report.md` (21137 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_05/prompt.txt` (675 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_05/query.json` (141 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_05/stdout.txt` (8819 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_05/stderr.txt` (251 bytes)

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
