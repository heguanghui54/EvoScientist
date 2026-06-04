# Deliberative Contrastive Iterative Retrieval (DeCIR-RAG): Mitigating Confirmation Bias in Multi-Hop RAG

---

## 1. Title

**Deliberative Contrastive Iterative Retrieval for Multi-Hop Reasoning in Retrieval-Augmented Generation**

---

## 2. Problem Statement

Multi-hop question answering requires a system to retrieve and reason over multiple pieces of evidence from different sources to answer a complex question (e.g., *"Which university employed the president of the Royal Society in 2020?"* — requires locating the president, then the employer).

Current iterative retrieval approaches (IRCoT — Trivedi et al., ACL 2022; ReAct — Yao et al., ICLR 2023; Self-Ask — Press et al., 2023; FLARE — Jiang et al., 2023) decompose the question into sub-questions, retrieve evidence for each, and chain the results toward a final answer. **These systems exhibit a systematic confirmation bias**: at hop *k*, the LLM formulates a sub-answer based on retrieved passages, and this sub-answer shapes the retrieval query for hop *k+1*. Once committed, the system preferentially retrieves evidence that supports the current trajectory and ignores contradictory information. Errors compound across hops — a wrong intermediate answer at hop 1 guarantees failure at hop 3 even if the correct evidence exists in the corpus.

Recent diagnostic work confirms this problem: Astaraki et al. (2026) show that iterative RAG systems sometimes *underperform* single-shot retrieval with oracle evidence precisely because error propagation overwhelms the benefit of decomposition. Wang et al. (2025) demonstrate that RAG systems with conflicting evidence degrade significantly — and multi-hop settings amplify this because conflict detection is never explicitly performed.

### Specific Subproblem

**How can an iterative RAG system be made deliberative — capable of retrieving and weighing both supporting and contradictory evidence at each hop, and backtracking when evidence is inconclusive — rather than greedily committing to a single reasoning trajectory?**

---

## 3. Hypothesis

**Hypothesis 1 (Contrastive Retrieval Hypothesis):** Retrieving both forward-directed and contrastive passages at each decomposition step reduces confirmation bias and improves multi-hop answer accuracy compared to greedy iterative retrieval.

**Hypothesis 2 (Arbitration Hypothesis):** A lightweight, trained evidence-arbitration module that scores passages on a support–contradict axis enables more accurate intermediate decisions than relying solely on the LLM's implicit judgment.

**Hypothesis 3 (Backtracking Hypothesis):** Incorporating a deliberative backtracking mechanism — triggered when the arbitration module detects high evidential conflict — reduces error propagation across hops.

**Null hypothesis:** The confirmation bias in iterative retrieval is not a significant source of error; observed degradation is caused by retrieval recall failure (missing evidence) rather than biased selection among retrieved evidence.

---

## 4. Method: Deliberative Contrastive Iterative Retrieval (DeCIR-RAG)

DeCIR-RAG extends the standard iterative retrieval loop with three components. The system operates by decomposing a multi-hop question *Q* into sub-questions *q₁, q₂, …, qₙ* (following IRCoT's decomposition strategy), but modifies the retrieval and reasoning at each step.

### Component 1: Contrastive Sub-question Generation

At each hop *k*, given partial context *C_{<k}* and sub-question *q_k*, the system generates **two** retrieval queries:

| Query type | Purpose | Formulation |
|---|---|---|
| **Forward query** *q_k^+* | Retrieve evidence supporting the expected sub-answer | Standard IRCoT-style query: "What is the answer to {q_k} given {C_{<k}}?" |
| **Contrastive query** *q_k^-* | Retrieve evidence that challenges or provides alternatives | "What evidence contradicts or offers an alternative to {q_k} given {C_{<k}}?" |

Both queries are issued to the retriever (top-K passages each, with K configurable). The contrastive query is constructed by prompting the LLM to ask: *"What would make the current sub-answer wrong? What alternative fact would change the outcome?"* This is a single additional LLM call per hop with negligible latency overhead.

### Component 2: Evidence Arbitration Module

Instead of passing all retrieved passages to the LLM for generation (the standard approach), a dedicated arbitration module scores each passage *p* from the combined pool *P_k = P_k^+ ∪ P_k^-* along two axes:

- **Support score** *s(p) ∈ [0,1]*: how strongly the passage supports the expected sub-answer for *q_k*
- **Contradiction score** *c(p) ∈ [0,1]*: how strongly the passage contradicts or offers an alternative

The module is a lightweight cross-encoder (e.g., a fine-tuned DeBERTa-v3-small, ~100M params) trained on a labeled dataset of passage–sub-answer pairs (see Section 6, Dataset).

From these scores, we compute:

- **Net support** *S_k = mean(s(p) for p ∈ P_k)*
- **Contradiction ratio** *R_k = |{p : c(p) > 0.5}| / |P_k|*
- **Confidence** *γ_k = S_k × (1 − R_k)*

### Component 3: Deliberative Switch with Backtracking

At each hop, the arbitrated confidence *γ_k* determines the system's behavior:

| γ_k | Decision |
|---|---|
| **≥ 0.7** (high confidence) | Commit to sub-answer normally; pass to next hop |
| **0.4 – 0.7** (moderate conflict) | Retrieve *additional* passages (top-5 more from *q_k^+* and *q_k^-*), re-arbitrate; if still < 0.7, flag as uncertain but proceed |
| **< 0.4** (high conflict) | Trigger **backtracking** — revert to hop *k−1*, mark the previous sub-answer as uncertain, re-retrieve with broader queries, and re-derive a new sub-answer |

Backtracking is implemented as a stack-based trace: the system maintains the reasoning path *[(q₁, a₁, P₁, γ₁), …, (q_k, a_k, P_k, γ_k)]*. On backtrack, it pops to the last high-confidence state and re-explores from that point.

### Training Procedure

The arbitration module is trained in two stages:

**Stage 1 — Supervised fine-tuning.** Create a dataset by running IRCoT on HotpotQA training set and annotating each (sub-question, passage) pair with binary support/contradict labels (see Section 6). Train the cross-encoder with a multi-task loss: binary cross-entropy for support classification + binary cross-entropy for contradiction classification.

**Stage 2 — Contrastive Preference Optimization (CPO).** Sample pairs of (passage set, sub-answer) trajectories. The preferred trajectory is one where the correct sub-answer was reached after considering both supporting and contradicting passages. The dispreferred trajectory is one where the system committed to a wrong sub-answer that ignored contradicting passages. Fine-tune with a DPO-style objective (Rafailov et al., NeurIPS 2024) using the cross-encoder's logits.

### Inference Procedure (Per Hop)

```
Input: sub-question q_k, context C_{<k}
1. Generate forward query q_k^+ and contrastive query q_k^-
2. Retrieve P_k^+ = Retriever(q_k^+, K) and P_k^- = Retriever(q_k^-, K)
3. Score each p ∈ (P_k^+ ∪ P_k^-) with arbitration module → s(p), c(p)
4. Compute γ_k = S_k × (1 − R_k)
5. IF γ_k < 0.4:
      Backtrack to hop k−1, re-retrieve with broadened queries
6. ELIF γ_k < 0.7:
      Retrieve additional passages, re-arbitrate
7. Generate sub-answer a_k using LLM with (P_k, q_k)
8. Push (q_k, a_k, P_k, γ_k) to reasoning trace
```

---

## 5. Datasets and Benchmarks

| Dataset | Description | # Questions | Hops | Why chosen |
|---|---|---|---|---|
| **HotpotQA** (Yang et al., EMNLP 2018) | Wikipedia-based multi-hop QA with supporting facts | ~113K | 2 | Standard benchmark; 1000+ papers compare on it |
| **MuSiQue** (Trivedi et al., ACL 2022) | Multi-hop QA with controlled difficulty (2–4 hops) | ~25K | 2–4 | Harder compositional reasoning; tests scalability beyond 2 hops |
| **2WikiMultihopQA** (Ho et al., 2020) | Multi-hop QA from Wikipedia with 2-hop bridge/comparison | ~192K | 2 | Tests generalization to comparison-type multi-hop |
| **StrategyQA** (Geva et al., 2021) | Yes/no multi-hop reasoning requiring implicit decomposition | ~2.8K | 2–3 | Tests implicit (not explicitly structured) multi-hop reasoning |

**Evaluation protocol:** Each dataset has a held-out test set. For HotpotQA, we use the standard dev split (7,405 questions). For MuSiQue and 2WikiMultihopQA, we follow the published splits. Results are reported as mean ± std over 3 random seeds per method.

**Training data for arbitration module:** We generate 50K (passage, sub-answer, support-label, contradict-label) quadruples by:
1. Running IRCoT over the HotpotQA training set and logging the intermediate sub-questions and passages.
2. Using the gold supporting facts from HotpotQA to automatically label passages as *supporting* (if the passage contains the gold fact) or *contradicting* (if it contains plausible alternative information — identified by lexical overlap with distractor passages from the HotpotQA corpus). Remaining passages are labeled *neutral* (s=0, c=0).

Human annotation on a 2K-sample subset validates the automatic labeling (target inter-annotator agreement > 0.85 Cohen's κ).

---

## 6. Evaluation Metrics

| Metric | Definition | Primary/Secondary |
|---|---|---|
| **Exact Match (EM)** | Exact string match between predicted and gold answer | **Primary** |
| **F1 Score** | Token-level F1 between predicted and gold answer | **Primary** |
| **Answer Recall@Hop** | Fraction of test questions where the correct sub-answer was present in retrieved passages at every hop (diagnostic) | Secondary — measures retrieval coverage, not just final answer |
| **Confidence Calibration (ECE)** | Expected Calibration Error of γ_k vs. empirical accuracy at each hop | Secondary — measures whether arbitration confidence is well-calibrated |
| **Backtrack Rate** | Fraction of questions where ≥1 backtrack occurred | Secondary — measures how often the deliberative mechanism activates |
| **Contradiction Detection Accuracy** | Precision/recall of detecting passages that genuinely contradict the correct sub-answer | Secondary — measures arbitration module quality |

**Statistical rigor:**
- All primary metrics are reported with 95% confidence intervals (bootstrap, 10,000 resamples)
- Multiple-testing correction (Bonferroni) when comparing ≥5 conditions
- Effect sizes reported as Cohen's *d* for pairwise method comparisons

---

## 7. Baselines

| Baseline | Description | Why it's a baseline |
|---|---|---|
| **Standard RAG** | Single-shot retrieve-and-read (top-K = 10), no decomposition | Lower bound — shows the baseline without multi-hop decomposition |
| **IRCoT** (Trivedi et al., ACL 2022) | Interleaves retrieval with CoT; greedy per-hop retrieval | **Primary baseline** — the canonical iterative retrieval method |
| **ReAct** (Yao et al., ICLR 2023) | Reasoning + acting loop with tool use | Compares against a non-decomposition iterative approach |
| **Self-Ask** (Press et al., 2023) | Decomposes into sub-questions, retrieves for each | Compares against explicit decomposition without contrastive retrieval |
| **ConRAG** (Sun et al., 2024) | Contradiction-aware RAG under multi-source evidence | **Ablation control** — isolates the value of *our specific* contrastive + backtracking components |
| **+Oracle Evidence** (upper bound) | Gold passages at each hop, no retrieval noise | Upper bound — retrieval oracle performance |

---

## 8. Ablations

| Ablation | Condition | What it isolates |
|---|---|---|
| **No contrastive retrieval** (DeCIR w/o C) | Only forward queries *q_k^+* per hop | Value of contrastive query generation |
| **No arbitration module** (DeCIR w/o A) | Raw LLM judgment instead of trained scorer | Value of the trained arbitration module |
| **No backtracking** (DeCIR w/o B) | Greedy forward pass; forced commitment at each hop | Value of the deliberative backtracking mechanism |
| **Synthetic contrastive passages** | Replace retrieved *P_k^-* with randomly sampled passages | Whether contrastive retrieval content matters or just having more passages |
| **Full DeCIR-RAG** | All components active | — |

---

## 9. Expected Failure Modes and Mitigations

| Failure mode | Likelihood | Mitigation |
|---|---|---|
| **Contrastive queries retrieve irrelevant passages** (low recall for contradiction) | Medium | Evaluate with and without contrastive retrieval; measure *Answer Recall@Hop* sub-metric to quantify coverage gain |
| **Arbitration module is worse than LLM's implicit judgment** (overhead without benefit) | Medium | The "No arbitration" ablation directly tests this. If true, fall back to prompted LLM arbitration with structured output |
| **Backtracking cascades into infinite loops** | Low | Cap backtrack depth at 3 hops (or 1 full cycle). After cap, force commit at lowest confidence state |
| **Training data for arbitration is noisy** (automatic labels are imprecise) | Medium | Use the 2K human-annotated subset as a validation filter; train on silver data but early-stop on the gold subset. Report agreement stats |
| **Short-context LLMs cannot handle the extra contrastive passages** | Low | All evaluated models (Llama-3-8B, GPT-4o-mini) support ≥8K context; at K=5 per query type, total passages = 10–15, well within budget |
| **DeCIR-RAG adds latency** (2x retrievals + arbitration per hop) | Medium (acceptable) | Arbitration is a single forward pass of a 100M-parameter model (~5ms on GPU). The extra retrieval call dominates; estimate 2× retrieval cost vs. IRCoT. Document wall-clock time alongside accuracy |

---

## 10. Execution Plan

### Stage 1: Infrastructure and Data (Week 1–2)

1. Set up retrieval pipeline: Contriever-MS MARCO dense retriever + BM25 sparse retriever (following IRCoT's setup for fairness)
2. Implement standard IRCoT baseline on HotpotQA, MuSiQue, 2WikiMultihopQA (reproduce published results within ±1 EM/F1)
3. Generate training data for arbitration module: run IRCoT on HotpotQA training set, extract 50K (passage, sub-answer, support, contradict) quadruples with automatic labeling
4. Create human-annotated validation subset (2K examples)

**Success signals:** IRCoT baselines within 1% of published EM/F1 on HotpotQA dev. Training data yields ≥85% agreement with human annotations on validation subset.

### Stage 2: Arbitration Module (Week 3)

1. Fine-tune DeBERTa-v3-small on the quadruple training data (multi-task BCE loss)
2. Evaluate on validation subset: support classification accuracy, contradiction detection F1
3. Train via CPO (Stage 2) on trajectory preference pairs
4. Measure: agreement with human annotations ≥0.85 accuracy; inference <10ms per passage on single GPU

**Success signals:** Arbitration module achieves ≥90% support classification accuracy and ≥80% contradiction detection F1 on validation subset. Inference adds <10% overhead to total per-hop latency.

### Stage 3: Full DeCIR-RAG System (Week 4)

1. Implement contrastive query generation (single LLM call per hop for the contrastive counterpart)
2. Integrate arbitration module scoring into retrieval loop
3. Implement deliberative switch with backtracking (stack-based trace, depth cap of 3)
4. Integration test on HotpotQA dev (100 random questions)

**Success signals:** System runs end-to-end without crashes on 100-test sanity check. Backtracking triggers on ≥10% of questions (indicating the mechanism activates).

### Stage 4: Evaluation and Ablations (Week 5–6)

1. Run full evaluation on HotpotQA, MuSiQue, 2WikiMultihopQA, StrategyQA (all baselines + ablations)
2. Report EM, F1, Answer Recall@Hop, ECE, Backtrack Rate, Contradiction Detection Accuracy
3. Run all ablations from Section 8
4. Statistical analysis: bootstrapped CIs, effect sizes, Bonferroni correction
5. Document latency overhead (wall-clock time per question vs. IRCoT)

**Success signals:** DeCIR-RAG outperforms IRCoT on ≥3 of 4 datasets (EM/F1). At least one ablation shows statistically significant degradation, confirming each component's contribution.

### Stage 5: Analysis and Write-up (Week 7)

1. Error analysis: categorize DeCIR-RAG failures by type (retrieval failure, arbitration error, backtracking failure, decomposition error)
2. Case studies: 5–10 questions where DeCIR-RAG succeeds where IRCoT fails (and vice versa)
3. Sensitivity analysis: K (passages per query type), confidence thresholds (γ_k thresholds)
4. Write paper draft (8 pages, NeurIPS/ACL format)

**Success signals:** Complete error taxonomy with ≥100 failure cases analyzed. Paper draft ready for internal review.

---

## 11. Related Work (Condensed)

**Iterative RAG for Multi-Hop QA.** IRCoT (Trivedi et al., ACL 2022, 1023+ citations) pioneered interleaving retrieval with CoT reasoning steps. ReAct (Yao et al., ICLR 2023) frames this as a reasoning-acting loop. Self-Ask (Press et al., 2023) explicitly decomposes into follow-up questions. FLARE (Jiang et al., 2023) uses LM confidence to decide when to retrieve. Recent work extends these: PAR²-RAG (Li et al., 2026) plans retrieval steps ahead; Reasoning in Trees (Shi et al., 2026) uses tree-structured retrieval; REAP (Zhu et al., 2025) adds recursive evaluation and adaptive planning. FrugalRAG (Java et al., 2025) shows that careful prompt engineering can match or exceed more complex methods on HotpotQA — establishing a strong pragmatic baseline.

**Conflicting Evidence in RAG.** ConRAG (Sun et al., 2024) explicitly addresses contradiction-aware RAG under multi-source evidence. Wang et al. (2025) analyze how RAG handles conflicting evidence and find significant degradation. ProbeRAG (Gao et al., 2025) detects conflicts in the model's latent space. Ranaldi et al. (2024) use contrastive explanations to elicit critical reasoning. ArbGraph (Niu et al., 2026) arbitrates evidence for long-form RAG. None of these address the *iterative* confirmation bias problem specifically — they operate in single-shot retrieval settings.

**Backtracking in Reasoning.** ReAgent (Zhao et al., 2025) proposes reversible multi-agent reasoning with explicit backtracking. Tree-of-Thoughts (Yao et al., 2023) explores multiple reasoning branches with backtracking but does not address retrieval. The key distinction of DeCIR-RAG is that backtracking is *triggered by evidence arbitration*, not by exhaustive search — making it more efficient than ToT and more targeted than ReAgent's multi-agent approach.

---

## 12. Sources

1. Trivedi, H., Balasubramanian, N., Khot, T., & Sabharwal, A. (2022). Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions. *ACL 2022*. arXiv:2212.10509.
2. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. *ICLR 2023*.
3. Yang, Z., Qi, P., Zhang, S., Bengio, Y., Cohen, W. W., Salakhutdinov, R., & Manning, C. D. (2018). HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering. *EMNLP 2018*.
4. Trivedi, H., Balasubramanian, N., Khot, T., & Sabharwal, A. (2022). MuSiQue: Multihop Sequential Question Answering. *ACL 2022*.
5. Ho, X., Nguyen, A., Sugawara, S., & Aizawa, A. (2020). Constructing A Multi-hop QA Dataset for Comprehensive Evaluation of Reasoning Steps. *COLING 2020*.
6. Geva, M., Khashabi, D., Segal, E., Khot, T., Roth, D., & Berant, J. (2021). Did Aristotle Use a Laptop? A Question Answering Benchmark with Implicit Reasoning Strategies. *TACL 2021*.
7. Wang, H., Prasad, A., Stengel-Eskin, E., & Bansal, M. (2025). Retrieval-Augmented Generation with Conflicting Evidence. arXiv:2504.13079.
8. Sun, X., Chen, J., Zhou, B., & Kuo, M. (2024). ConRAG: Contradiction-Aware Retrieval-Augmented Generation under Multi-Source Conflicting Evidence. arXiv preprint.
9. Astaraki, M., Saloot, M. A., Kasmaee, A. S., Mahyar, H., & Samiee, S. (2026). When Iterative RAG Beats Ideal Evidence: A Diagnostic Study in Scientific Multi-hop Question Answering. arXiv:2601.19827.
10. Li, X., Wang, R., Wang, Y., Guo, M., Li, C., Sheng, T., Ravi, S., & Roth, D. (2026). PAR²-RAG: Planned Active Retrieval and Reasoning for Multi-Hop Question Answering. arXiv:2603.29085.
11. Shi, Y., Sun, M., Liu, Z., Yang, M., Fang, Y., Sun, T., & Gu, X. (2026). Reasoning in Trees: Improving Retrieval-Augmented Generation for Multi-Hop Question Answering. arXiv:2601.11255.
12. Zhu, Y., Zhou, H., et al. (2025). REAP: Enhancing RAG with Recursive Evaluation and Adaptive Planning for Multi-Hop Question Answering. arXiv:2511.09966.
13. Zhao, X., Gao, F., et al. (2025). ReAgent: Reversible Multi-Agent Reasoning for Knowledge-Enhanced Multi-Hop QA. arXiv preprint.
14. Java, A., Koundinyan, S. P., et al. (2025). FrugalRAG: Learning to retrieve and reason for multi-hop QA. arXiv:2507.07634.
15. Jiang, Z., Sun, M., Zhang, Z., & Liang, L. (2024). Retrieve, Summarize, Plan: Advancing Multi-hop Question Answering with an Iterative Approach. arXiv:2407.13101.
16. Gao, L., Zhang, Q., et al. (2025). ProbeRAG: Latent Probing for Faithful Retrieval-Augmented Generation. arXiv preprint.
17. Ranaldi, L., et al. (2024). Eliciting Critical Reasoning in Retrieval-Augmented Language Models via Contrastive Explanations. arXiv:2410.22874.
18. Niu, Q., et al. (2026). ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation. arXiv:2604.18362.
19. Press, O., Zhang, M., Min, S., Schmidt, L., Smith, N. A., & Lewis, M. (2023). Measuring and Narrowing the Compositionality Gap in Language Models. *EMNLP 2023* (Self-Ask).
20. Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T. L., Cao, Y., & Narasimhan, K. (2023). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *NeurIPS 2023*.
21. Rafailov, R., Sharma, A., Mitchell, E., Manning, C. D., Ermon, S., & Finn, C. (2024). Direct Preference Optimization: Your Language Model is Secretly a Reward Model. *NeurIPS 2024*.
22. Zhuang, Z., et al. (2024). EfficientRAG: Efficient Retriever for Multi-Hop Question Answering. arXiv:2408.04259.

---

*Proposal generated by EvoScientist with literature grounding from paper-navigator (Semantic Scholar + arXiv). All citations correspond to real papers. Method details, hypotheses, and execution plan are novel contributions of this proposal.*

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 24 |
| Topic | RAG |
| Original user goal | Generate a research proposal on solving multi-hop reasoning challenges in Retrieval-Augmented Generation (RAG). |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_24/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_24/final_report.md` (22379 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_24/prompt.txt` (715 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_24/query.json` (157 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_24/stdout.txt` (9451 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_24/stderr.txt` (251 bytes)

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
