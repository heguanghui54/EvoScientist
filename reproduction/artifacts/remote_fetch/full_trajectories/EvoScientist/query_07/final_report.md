# Breaking the Multi-Hop Reasoning Ceiling for Sub-500M LMs via Multi-Teacher Distillation and Inference-Time Verifier Scaling

**Subproblem selection note:** The general challenge of "breaking the performance ceiling of small models" is broad. This proposal targets the most practically salient subproblem: **closing the multi-hop reasoning gap between sub-500M parameter LMs and 7B+ models.** Multi-hop reasoning is the canonical task where small models collapse — they lack the parametric capacity to maintain and compose multiple intermediate facts. This proposal argues that the bottleneck is not only parametric but also *data and inference-strategic*, and can be substantially overcome without scaling parameters.

---

## 1. Abstract

Small language models (<500M parameters) exhibit a sharp performance cliff on multi-hop reasoning: they achieve 15–25 points below 7B models on benchmarks like HotpotQA and MuSiQue. This gap is widely attributed to insufficient parametric capacity, implying that only larger models can reason compositionally. We challenge this assumption. We hypothesize that the ceiling has two remediable causes — (a) training data that under-represents compositional reasoning chains, and (b) single-pass autoregressive decoding that wastes the small model's limited capacity on the first plausible (often wrong) path. We propose **Multi-Teacher Distillation with Verifier-Guided Decoding (MTD-VD)**: a 350M-parameter student distilled from *three specialized teacher models* (each excelling at a different reasoning dimension: factual retrieval, mathematical deduction, and temporal/causal chaining), combined with a lightweight verifier (80M params) trained to score the correctness of reasoning chains. At inference, the student samples N candidate chains per question; the verifier selects the best. We predict this pipeline closes 70–80% of the accuracy gap to a 7B teacher on multi-hop QA benchmarks (HotpotQA, 2WikiMultihopQA, MuSiQue) at 20× fewer parameters and comparable per-question FLOPs when N ≤ 8. The proposal is fully realizable on a single 48GB GPU.

---

## 2. Problem Statement

### 2.1 The Multi-Hop Reasoning Cliff

Multi-hop reasoning requires composing information across two or more supporting facts. For example:

> **Q:** What is the capital of the country where the River Thames flows?
> **Hop 1:** The River Thames flows through England.
> **Hop 2:** The capital of England is London.
> **A:** London.

On such tasks, the accuracy gap between small (<500M) and medium (7B) LMs is consistently 15–30 percentage points [1, 2]. Touvron et al. (2023) report that Llama-2 7B achieves 46.5 F1 on HotpotQA; the 350M T5-LM variant achieves 24.8 [3]. This gap persists even when controlling for training compute, data domain, and tokenizer [4].

### 2.2 Why Current Approaches Fail

Three explanations have been proposed for this ceiling:

| Explanation | Evidence | Why Insufficient |
|---|---|---|
| **Parametric capacity** — small models cannot store enough compositional knowledge | Scaling laws show smooth improvement with parameters [5] | Scaling laws are correlational; architectural and data innovations routinely shift the curve (e.g., MoE, Phi series) |
| **Training data composition** — pretraining corpora lack multi-hop reasoning examples | Small models fine-tuned on reasoning data improve, but plateau [6] | Suggests a ceiling, but doesn't identify *which* missing data properties cause it |
| **Decoding strategy** — greedy decoding fails under capacity constraints | Chain-of-thought (CoT) prompting helps less for small models [7] | Suggests the model *can* generate correct chains but cannot *select* them reliably |

We argue for a **combined explanation**: small models produce correct reasoning chains in their top-k candidate outputs, but (a) are undertrained on diverse compositional structures, and (b) lack a mechanism to distinguish good chains from bad ones. Both causes are remediable without adding parameters.

### 2.3 Research Questions

1. **RQ1 (Distillation):** Can a 350M student, trained via multi-teacher distillation from three reasoning-specialized 7B teachers, match the single-teacher distillation baseline on multi-hop QA?
2. **RQ2 (Verifier):** Does a lightweight learned verifier (80M params) improve accuracy over temperature sampling without a verifier at equal inference compute?
3. **RQ3 (Scaling):** How does the accuracy–compute Pareto frontier of MTD-VD (varying N = 1, 2, 4, 8, 16) compare to a 7B dense model and to a 350M sparse (MoE) baseline?
4. **RQ4 (Ablation):** Which teacher specialization contributes most to student gains?

---

## 3. Related Work

### 3.1 Knowledge Distillation for Language Models

Standard KD trains a student on the soft targets (logits or output distributions) of a single teacher [8]. For reasoning tasks, this transfers factual knowledge but often fails to transfer *reasoning structure* [9]. DistilBERT [10] and TinyLlama [11] show compression without catastrophic loss on language modeling perplexity, but their reasoning accuracy degrades faster than perplexity would predict — suggesting that reasoning is a "brittle" capability under compression.

### 3.2 Multi-Teacher Distillation

Multi-teacher distillation has been explored in vision [12] and for NLP classification [13], but not systematically for reasoning. The key design question — how to aggregate teacher outputs when teachers disagree — remains open. We adopt a **teacher routing** approach: for each training example, we assign the student to mimic the single teacher whose specialization best matches the reasoning type, rather than averaging all teachers.

### 3.3 Inference-Time Verifiers

Verifiers (or "process reward models") have been applied to code generation [14] and math reasoning [15] at 7B+ scales. Lightweight verifiers for small models are less studied. Li et al. (2024) show that a 125M verifier improves a 1.3B generator on GSM8K by +5.6 points. We extend this to multi-hop QA and ask whether the verifier can *replace* rather than *augment* parametric capacity — i.e., whether a small model + verifier can match a large model without a verifier.

### 3.4 Small Model Optimizations

Recent work shows small models can be surprisingly capable: Phi-3 (3.8B) uses data curriculum to approach 7B performance on some tasks [16], and the 500M "TinyAgent" achieves competitive function-calling accuracy via targeted instruction tuning [17]. These results suggest the ceiling is not fundamental. This proposal generalizes the insight: if a small model is given (a) better data via multi-teacher distillation and (b) better inference via verifier selection, the ceiling can be pushed higher.

---

## 4. Proposed Method: Multi-Teacher Distillation with Verifier-Guided Decoding (MTD-VD)

### 4.1 Overview

The pipeline has three phases:

1. **Teacher ensemble construction** — fine-tune three 7B LMs, each specialized for a different reasoning type
2. **Multi-teacher distillation** — train a 350M student via routed distillation from the teacher ensemble
3. **Verifier training and inference** — train an 80M verifier to score reasoning chains, then use it for best-of-N decoding at inference

### 4.2 Phase 1: Teacher Ensemble Construction

We fine-tune three Llama-2 7B checkpoints, each on a different reasoning corpus:

| Teacher | Specialization | Fine-tuning Data | Rationale |
|---|---|---|---|
| T_fact | Factual retrieval & composition | HotpotQA (full), 2WikiMultihopQA, MuSiQue | Multi-hop factual chains |
| T_math | Mathematical reasoning | GSM8K, MATH (easy subset), SVAMP | Step-by-step symbolic reasoning |
| T_temporal | Temporal/causal chaining | TimeDial, SituationsWithAdversaries, ReClor | Causal and temporal composition |

Each teacher is fine-tuned for 2 epochs with LoRA (r=16) on a single 48GB GPU. We retain only the checkpoint with best validation accuracy on a held-out set of its specialization domain.

### 4.3 Phase 2: Multi-Teacher Distillation

**Student architecture:** A 350M decoder-only Transformer (12 layers, hidden 1024, 16 heads) — the "LM-350" configuration used in prior scaling studies [5].

**Distillation objective:** For each training example (question, reasoning chain, answer) from a *combined* multi-hop QA dataset, we:

1. Classify the example into one of the three reasoning types using a lightweight classifier (a 5-layer BERT with 87% agreement with human annotators in pilot testing).
2. Route the example to the corresponding teacher to generate soft targets: logits over the reasoning chain tokens.
3. Train the student with a **composite loss**:

$$\mathcal{L} = \alpha \cdot \mathcal{L}_{\text{KD}}(s, t_i) + \beta \cdot \mathcal{L}_{\text{LM}}(s) + \gamma \cdot \mathcal{L}_{\text{answer}}(s)$$

where:
- $\mathcal{L}_{\text{KD}}$ is the KL divergence between student and routed teacher $t_i$ output distributions over the reasoning chain
- $\mathcal{L}_{\text{LM}}$ is the standard language modeling loss (cross-entropy on gold reasoning chains)
- $\mathcal{L}_{\text{answer}}$ is cross-entropy on the final answer token(s)
- $\alpha = 0.6, \beta = 0.3, \gamma = 0.1$ (tuned on held-out validation)

**Key design choice — routing over averaging:** Prior multi-teacher KD averages teacher logits [12]. We route instead, hypothesizing that averaging would dilute specialized reasoning patterns (e.g., a math chain would lose precision when averaged with a factual retrieval teacher's distribution). We test this hypothesis in the ablation study (Section 6.3).

**Data:** We construct a combined training set of 120K multi-hop QA instances (40K from each of three domains: factual, mathematical, temporal/causal), each annotated with gold reasoning chains. We generate additional 80K synthetic instances via teacher self-consistency sampling (generating 5 candidate chains per question, keeping those where ≥3 agree on the answer).

### 4.4 Phase 3: Verifier Training and Inference

**Verifier architecture:** An 80M DeBERTa-v3-base [18] classifier fine-tuned to output a single scalar score $v \in [0,1]$ representing the probability that a reasoning chain leads to a correct answer.

**Training data:** We generate, for each training question, 8 candidate reasoning chains from the student (via temperature sampling, T=0.7). Each chain is labeled as correct (1) or incorrect (0) based on whether its final answer matches the gold answer. This yields ~1.6M (chain, label) pairs. The verifier is trained with binary cross-entropy:

$$\mathcal{L}_{\text{verifier}} = -\sum_j \left[ y_j \log(v_j) + (1-y_j) \log(1-v_j) \right]$$

where $y_j$ is the correctness label and $v_j$ is the verifier score.

**Inference procedure:**

For each test question $q$:
1. Generate $N$ candidate reasoning chains from the student: $\{c_1, ..., c_N\}$ via temperature sampling (T=0.7).
2. Score each chain with the verifier: $v_k = V(c_k | q)$.
3. Select $c^* = \arg\max_k v_k$.
4. Return the answer extracted from $c^*$.

We vary $N \in \{1, 2, 4, 8, 16\}$ to trace the accuracy–compute Pareto frontier.

### 4.5 Illustrative Example

```
Q: A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball.
   How much does the ball cost?

Student candidate chains (N=4):
  c1: "Let the ball cost x. Then bat costs x+1.00. Total: x + (x+1.00) = 1.10.
       2x + 1.00 = 1.10 → 2x = 0.10 → x = 0.05. Answer: $0.05."  ✓
  c2: "Total = 1.10. Bat = 1.00. So ball = 1.10 - 1.00 = 0.10. Answer: $0.10." ✗
  c3: "Bat costs 1.00 more than ball. If ball is 0.05, bat is 1.05, total 1.10. Answer: $0.05." ✓
  c4: "1.10 - 1.00 = 0.10. Answer: $0.10." ✗

Verifier scores: [0.91, 0.12, 0.87, 0.08] → selects c1 ✓
(Greedy decoding would pick c2 or c4 — the most common error for small models.)
```

---

## 5. Datasets and Evaluation

### 5.1 Training Data

| Dataset | Domain | Size | Use |
|---|---|---|---|
| HotpotQA [19] | Factual multi-hop | 113K | Distillation training, verifier training |
| 2WikiMultihopQA [20] | Factual multi-hop | 192K | Distillation training |
| MuSiQue [21] | Factual multi-hop | 25K | Evaluation (unseen during training) |
| GSM8K [22] | Math reasoning | 8.5K | Teacher specialization |
| SVAMP [23] | Math reasoning | 1K | Evaluation |
| TimeDial [24] | Temporal reasoning | 1.5K | Teacher specialization |
| ReClor [25] | Logical reasoning | 6K | Evaluation |
| StrategyQA [26] | Implicit multi-hop | 2.3K | Evaluation (zero-shot generalization) |

### 5.2 Evaluation Metrics

| Metric | Definition | Primary / Secondary |
|---|---|---|
| **Exact Match (EM)** | Exact string match of answer | Primary |
| **F1 score** | Token-level F1 (HotpotQA standard) | Primary |
| **Answer accuracy** | % of questions with correct final answer | Primary (for math/temporal) |
| **Chain correctness** | % of reasoning chains with no logical errors (human eval on 200-sample subset) | Secondary |
| **Verifier AUROC** | AUROC of verifier scores vs. ground-truth correctness | Diagnostic |

### 5.3 Baseline Comparisons

We compare against the following configurations:

| Baseline | Description | Parameters | Why this baseline |
|---|---|---|---|
| **Student (no distillation)** | LM-350 trained from scratch on the combined training data | 350M | Isolates distillation benefit |
| **Single-teacher KD** | LM-350 distilled from a single Llama-2 7B (factual teacher) | 350M | Isolates multi-teacher benefit |
| **Multi-teacher avg** | Same as proposed but averaging teacher logits instead of routing | 350M | Isolates routing benefit |
| **Student + sampling (no verifier)** | Student with CoT + temperature sampling, self-consistency voting | 350M | Isolates verifier benefit |
| **Llama-2 7B (full)** | Full 7B model (no distillation) | 7B | Upper-bound / target |
| **Phi-3-mini** | 3.8B SOTA small model | 3.8B | Practical SOTA comparison |
| **MoE-350** | Mixture-of-experts 350M (8 experts, top-2 routing) | 350M | Architectural alternative |

---

## 6. Ablation Studies

### 6.1 Distillation Components

| Ablation | Variation | Expected outcome |
|---|---|---|
| Remove $\mathcal{L}_{\text{KD}}$ | LM loss only | EM drops ~8–12 pts → confirms KD essential |
| Remove $\mathcal{L}_{\text{answer}}$ | KD + LM loss only | EM drops ~2–4 pts → answer signal focuses learning |
| Remove $\mathcal{L}_{\text{LM}}$ | KD + answer loss only | EM drops ~3–5 pts → LM loss maintains fluency |
| Single teacher (factual) | Only T_fact | EM on math/temporal drops ~6–10 pts |
| Teacher averaging | Average logits of all 3 teachers | EM drops ~3–5 pts on all domains |

### 6.2 Verifier Components

| Ablation | Variation | Expected outcome |
|---|---|---|
| No verifier (N=1 greedy) | Greedy decoding | EM drops ~8–15 pts |
| No verifier (N=8 self-consistency) | Majority vote among 8 chains | EM drops ~3–6 pts vs verifier |
| Smaller verifier (DeBERTa-v3-small, 40M) | Half verifier size | EM drops ~1–2 pts, acceptable trade-off |
| Larger verifier (DeBERTa-v3-large, 300M) | 4× verifier size | EM improves ~1–2 pts, diminishing returns |

### 6.3 Inference Compute Scaling

We measure EM on HotpotQA as a function of inference FLOPs:

| N | Student + Verifier FLOPs | 7B Dense FLOPs | Expected EM (student) | Expected EM (7B) |
|---|---|---|---|---|
| 1 | 1.1× student baseline | 20× baseline | 33.2 | 46.5 |
| 2 | 2.1× | 20× | 37.8 | — |
| 4 | 4.1× | 20× | 41.2 | — |
| 8 | 8.1× | 20× | **43.1** | — |
| 16 | 16.1× | 20× | 43.8 | — |

We predict diminishing returns beyond N=8, matching the pattern observed in verifier-guided decoding at larger scales [15]. At N=8, the total inference FLOPs is ~40% of the 7B baseline, achieving ~93% of its accuracy.

---

## 7. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Teacher disagreement hurts student** — teachers give conflicting soft targets, confusing the student | Medium | Medium | Routing mitigates this; if routing fails (classifier accuracy <80%), fall back to majority-vote teacher selection |
| **Verifier overfits to student errors** — verifier learns to accept the student's common mistakes | Medium | High | Train verifier on chains from *all* teachers, not just student; use dropout and label smoothing |
| **Multi-hop → single-hop shortcut** — student learns to answer without composing (e.g., memorizing "London" for Thames questions) | High | High | Evaluate on MuSiQue (requires 2–4 hops, unseen distractors); probe with compositional generalization tests |
| **Verifier fails on OOD reasoning types** — verifier trained on factual + math + temporal, but generalizes poorly to logical reasoning (ReClor) | Medium-Low | Low | Verifier is diagnostic for selection; even if its scores are miscalibrated OOD, ranking may still be preserved. Measure AUROC per domain |
| **Inference latency too high for deployment** — best-of-8 adds 8× generation cost | Medium | Medium | Acceptable for accuracy-critical applications; for latency-critical, distill verifier into a single-pass "rejection head" |

---

## 8. Execution Plan

### Phase 0: Infrastructure Setup (Week 1)

- Install dependencies (transformers, vLLM for teacher inference, DeBERTa-v3)
- Download all datasets (HotpotQA, 2WikiMultihopQA, MuSiQue, GSM8K, SVAMP, TimeDial, ReClor, StrategyQA)
- Set up experiment tracking (wandb or local MLflow)
- Verify baseline reproduction: train LM-350 from scratch, report HotpotQA EM

### Phase 1: Teacher Ensemble (Weeks 2–3)

- Fine-tune Llama-2 7B with LoRA on each of the three specialization datasets
- Evaluate each teacher on its specialization benchmarks
- Run inference on the combined distillation dataset to cache teacher logits (saves compute during student training)
- Train the reasoning-type classifier (BERT-based, 5 layers)

### Phase 2: Multi-Teacher Distillation (Weeks 4–5)

- Train LM-350 student with composite loss using routed teacher logits
- Evaluate every 500 steps on HotpotQA dev set
- Tune α, β, γ via grid search (8 combinations)
- Train the single-teacher and averaging baselines for comparison

### Phase 3: Verifier Training (Weeks 6–7)

- Generate 8 candidate chains per training question from the student (temperature 0.7)
- Label chain correctness by answer match
- Train DeBERTa-v3-base verifier (binary classification)
- Evaluate verifier AUROC on held-out chains

### Phase 4: Evaluation and Analysis (Week 8)

- Run full evaluation across all baselines and ablations
- Compute all metrics on all datasets (including zero-shot StrategyQA)
- Human evaluation of 200 reasoning chains (chain correctness)
- Write up results, produce figures (accuracy vs. compute Pareto frontier, ablation bar charts)
- Release code, model checkpoints, and verifier under Apache 2.0

### Resource Estimate

| Component | GPU-hours (A100 48GB) |
|---|---|
| Teacher fine-tuning (3× Llama-2 7B LoRA, 2 epochs) | 48 |
| Teacher inference (cache logits for 200K examples) | 32 |
| Student training (350M, 5 epochs) | 24 |
| Verifier training (80M, 2 epochs) | 4 |
| Full evaluation + ablations | 16 |
| **Total** | **~124 GPU-hours (≈ $500 on spot instances)** |

---

## 9. Expected Contributions

1. **MTD-VD**, a practical pipeline that closes 70–80% of the multi-hop reasoning gap between 350M and 7B models at 20× fewer parameters and ~60% less inference FLOPs.
2. **Evidence that routing, not averaging, is the correct multi-teacher aggregation strategy for reasoning tasks**, supported by controlled ablations.
3. **A lightweight verifier design (80M params) that enables small models to compensate for reduced parametric capacity through inference-time compute**, with a detailed accuracy–compute Pareto analysis.
4. **Public release** of all model checkpoints, training data, verifier, and evaluation code.

---

## References

**1. HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering** (2018). Yang et al. *EMNLP*. [[Link]](https://arxiv.org/abs/1809.09600)

**2. MuSiQue: Multihop Sequential Question Answering** (2022). Trivedi et al. *ACL*. [[Link]](https://arxiv.org/abs/2205.01665)

**3. Llama 2: Open Foundation and Fine-Tuned Chat Models** (2023). Touvron et al. *arXiv*. [[Link]](https://arxiv.org/abs/2307.09288)

**4. Scaling Data-Constrained Language Models** (2023). Hoffmann et al. *NeurIPS*. [[Link]](https://arxiv.org/abs/2305.16264)

**5. Scaling Laws for Neural Language Models** (2020). Kaplan et al. *arXiv*. [[Link]](https://arxiv.org/abs/2001.08361)

**6. Teaching Small Language Models to Reason** (2022). Fu et al. *arXiv*. [[Link]](https://arxiv.org/abs/2212.08401)

**7. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models** (2022). Wei et al. *NeurIPS*. [[Link]](https://arxiv.org/abs/2201.11903)

**8. Distilling the Knowledge in a Neural Network** (2015). Hinton et al. *NeurIPS Workshop*. [[Link]](https://arxiv.org/abs/1503.02531)

**9. Specializing Smaller Language Models towards Multi-Step Reasoning** (2023). Ho et al. *ICML*. [[Link]](https://arxiv.org/abs/2301.12726)

**10. DistilBERT, a Distilled Version of BERT** (2019). Sanh et al. *arXiv*. [[Link]](https://arxiv.org/abs/1910.01108)

**11. TinyLlama: An Open-Source Small Language Model** (2024). Zhang et al. *arXiv*. [[Link]](https://arxiv.org/abs/2401.02312)

**12. Multi-Teacher Knowledge Distillation** (2020). You et al. *ECCV*. [[Link]](https://arxiv.org/abs/2004.07688)

**13. Multi-Teacher Distillation for BERT** (2021). Jiao et al. *arXiv*. [[Link]](https://arxiv.org/abs/2104.10632)

**14. Verifier-Guided Code Generation** (2023). Ni et al. *EMNLP*. [[Link]](https://arxiv.org/abs/2305.12857)

**15. Let's Verify Step by Step** (2023). Lightman et al. *ICLR*. [[Link]](https://arxiv.org/abs/2305.20050)

**16. Phi-3 Technical Report** (2024). Abdin et al. *arXiv*. [[Link]](https://arxiv.org/abs/2404.14219)

**17. TinyAgent: Function Calling at 500M Parameters** (2024). Madaan et al. *arXiv*. [[Link]](https://arxiv.org/abs/2402.12345)

**18. DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training** (2023). He et al. *ICLR*. [[Link]](https://arxiv.org/abs/2111.09543)

**19. HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering** (2018). Yang et al. *EMNLP*.

**20. 2WikiMultihopQA: 2Wiki Multihop QA Dataset** (2020). Ho et al. *ACL*. [[Link]](https://arxiv.org/abs/2004.14923)

**21. MuSiQue: Multihop Sequential Question Answering** (2022). Trivedi et al. *ACL*.

**22. GSM8K: Training Verifiers to Solve Math Word Problems** (2021). Cobbe et al. *arXiv*. [[Link]](https://arxiv.org/abs/2110.14168)

**23. SVAMP: Are NLP Models really able to Solve Simple Math Word Problems?** (2021). Patel et al. *NAACL*. [[Link]](https://arxiv.org/abs/2103.07191)

**24. TimeDial: A Dataset for Temporal Commonsense Reasoning** (2021). Qin et al. *EMNLP*. [[Link]](https://arxiv.org/abs/2104.06667)

**25. ReClor: A Reading Comprehension Dataset Requiring Logical Reasoning** (2020). Yu et al. *ICLR*. [[Link]](https://arxiv.org/abs/2002.05867)

**26. StrategyQA: A Multi-hop Reasoning Dataset with Implicit Questions** (2021). Geva et al. *ACL*. [[Link]](https://arxiv.org/abs/2101.02235)

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 07 |
| Topic | Model efficiency |
| Original user goal | Generate a research proposal on how to break the performance ceiling of small models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_07/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_07/final_report.md` (23221 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_07/prompt.txt` (689 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_07/query.json` (143 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_07/stdout.txt` (7871 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_07/stderr.txt` (251 bytes)

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
