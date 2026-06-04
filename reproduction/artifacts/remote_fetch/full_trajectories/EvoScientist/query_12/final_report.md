# Research Proposal: Evidence-Conditioned Activation Steering (ECAS) for Factual Consistency in Retrieval-Augmented Generation

## 1. Problem Statement

**Factual consistency in RAG remains unsolved.** When large language models (LLMs) are augmented with retrieved documents, they still generate claims that contradict or ignore the evidence — often despite the evidence containing the correct answer. A model that "knows" the answer in its parameters defaults to parametric knowledge when the evidence conflicts, when attention is diluted across long contexts, or when a superficially plausible token is locally preferred over the evidence-supported one. This is the dominant failure mode in deployed RAG systems, especially for knowledge-intensive tasks requiring multi-sentence answers.

**The specific subproblem addressed**: inference-time mitigation of evidence-contradicting generation in RAG pipelines. The goal is to make LLMs faithful to *the specific retrieved evidence at hand*, not just generically truthful.

## 2. Hypothesis

**Central claim**: The internal activations of an LLM encode separable representations of (a) whether the current token is supported by retrieved evidence and (b) the content of that evidence. By learning an *evidence-conditioned* factuality direction from the model's own hidden states — rather than a static "truthfulness" vector — and applying it *adaptively per token* based on predicted hallucination risk, we can suppress evidence-contradicting tokens at generation time without fine-tuning the LLM.

**Formal hypothesis**: For an LLM ℳ generating answer tokens y₁, y₂, ..., yₜ with retrieved evidence E, let hₜ⁽ˡ⁾ be the hidden state at layer ℓ and position t. There exists a linear probe f: hₜ⁽ˡ⁾ → [0,1] that predicts P(yₜ contradicts E). Steering activations along the direction ∇_h ℒ(h, E) (where ℒ is a contrastive loss between evidence-grounded and evidence-ablated representations) at positions where f(hₜ) > τ reduces the rate of evidence-contradicting tokens by ≥ 30% relative to the unsteered baseline, with ≤ 5% degradation in answer informativeness.

## 3. Method: Evidence-Conditioned Activation Steering (ECAS)

ECAS has three components trained and assembled without any LLM fine-tuning.

### 3.1 Phase 1: Token-Level Factuality Probe (Training)

We train a lightweight linear probe on the LLM's hidden states at each layer to predict whether the token being generated will contradict the retrieved evidence.

**Data**: We construct a training set from FEVER (5,000 claims with verdicts) and a subset of Natural Questions (10,000 Q/A pairs). For each example:
- Retrieve evidence via BM25/Contriever (top-3 passages).
- Generate a continuation with the LLM (greedy).
- Label each token as **E-supported** (the token appears in or is entailed by the evidence) or **E-contradicting** (the token contradicts or is unsupported by the evidence) using a strong NLI model (DeBERTa-v3-large trained on MNLI + FEVER) as the oracle.

**Probe**: A linear layer per transformer layer ℓ:
```
p_ℓ(contrAdict | h_ℓ) = σ(w_ℓ^T · h_ℓ + b_ℓ)
```
Trained with binary cross-entropy. We evaluate probes at layers 0, 6, 12, 18, 24, 32 (for a 32-layer model) and select the layer with highest F1 on held-out FEVER data. The probe has ~10K parameters total — negligible overhead.

### 3.2 Phase 2: Evidence-Conditioned Steering Direction (Computed at Inference)

At inference time, for a given query q and retrieved evidence E, we compute a dynamic steering direction **specific to this (q, E) pair**:

1. **Encode the evidence**: Run a *single* forward pass on the prompt [q; E; instruction], caching hidden states hₜ⁽ˡ⁾.
2. **Compute evidence representation**: Average the hidden states at the selected probe layer over the evidence token positions → v_E.
3. **Project to factuality subspace**: Apply the probe's weight vector w_ℓ to v_E → ω = w_ℓ^T · v_E, a scalar factuality score for this evidence.
4. **Steering vector**: s = ω · (w_ℓ^T · h_ℓ) normalized. This is the direction in activation space that, when added, increases the probe's assigned probability of evidence-grounded tokens.

**Key innovation**: Unlike ITI (Li et al., 2024) which uses a single static "truthfulness" direction learned from TruthfulQA, s is a function of the *current evidence* v_E. When evidence is strong (high ω), steering is more aggressive toward evidence-grounded tokens. When evidence is weak/ambiguous, steering is conservative.

### 3.3 Phase 3: Adaptive Per-Token Intervention (Decoding)

During generation, at each step t:
1. Forward‑pass the current prefix to get hₜ⁽ˡ⁾.
2. Compute probe score pₜ = σ(w_ℓ^T · hₜ⁽ˡ⁾).
3. **Adaptive strength**: αₜ = α₀ · pₜ · (1 + γ · Uₜ), where Uₜ is the predictive entropy (normalized to [0,1]) — higher uncertainty → stronger steering.
4. **Steered logits**: h'_ℓ = h_ℓ + αₜ · s. Propagate forward from the steered layer to compute the output distribution.
5. **Residual contrastive term**: Additionally suppress tokens that the probe identifies as high-contradiction risk relative to the unsteered distribution:
   ```
   P'(y) ∝ P_steered(y) · (1 - β · σ(w_ℓ^T · h_ℓ(y)))
   ```
   where h_ℓ(y) is the hidden state that would yield token y.

**Rationale for adaptive αₜ**: Hallucination risk varies dramatically across token positions. Function words ("the", "a", "and") carry minimal factual content. The probe's pₜ will be near 0.5 on these tokens, αₜ will be small, and the intervention is near-transparent. On factual claims ("was born in Paris"), pₜ will spike and αₜ increases, applying strong steering exactly where needed.

## 4. Datasets and Benchmarks

| Dataset | Task | Size | Usage | Metric |
|---------|------|------|-------|--------|
| **FEVER** | Fact verification w/ evidence | 185K claims | Probe training + eval | Token-level F1 (probe) |
| **Natural Questions (NQ)** | Open-domain QA | 3K dev / 3K test | End-to-end eval | Exact Match, F1 |
| **TruthfulQA** | Truthfulness eval | 817 questions | Factuality benchmark | % truthful (GPT-judge) |
| **ASQA** | Long-form QA w/ evidence | 4K test | Multi-sentence factuality | MAUVE, FactScore |
| **BEGIN** | Factuality in biographies | 1K test | Attribute-level factuality | precision, recall |

**Primary metric**: **Evidence-Grounded F1** — for each generated sentence, decompose into atomic claims, check each against retrieved evidence using an NLI-based verifier (DeBERTa-v3 FEVER). This is more granular than exact match and catches partial hallucinations.

**Secondary metrics**: Exact Match / token F1 (for NQ), % truthful (TruthfulQA), FactScore (for ASQA / biographies).

## 5. Baselines

We compare against the following categories of inference-time methods:

| Method | Category | Why included |
|--------|----------|-------------|
| **Standard greedy decoding** | Untreated | Lower bound |
| **Standard RAG (BM25 + LLM)** | Untreated | Our base condition |
| **DoLa** (Chuang et al., 2024) | Contrastive decoding | Contrasts early vs late layers |
| **Contrastive Decoding** (Li et al., 2023) | Contrastive decoding | Contrasts with amateur model |
| **ITI** (Li et al., 2024) | Activation steering | Static truthfulness direction |
| **Adaptive Activation Steering** (Wang et al., 2024) | Activation steering | Adaptive strength, static direction |
| **PrefixNLI** (Harary et al., 2025) | NLI-guided decoding | Token-level NLI filtering |
| **Self-Consistency** (Wang et al., 2023) | Sampling | Multi-sample aggregation |
| **ECAS (ours)** | Evidence-conditioned steering | Proposed method |

## 6. Ablations

We design ablations to isolate each component of ECAS:

| Ablation | What it removes | What it tests |
|----------|-----------------|---------------|
| **ECAS - Evidence cond.** | Replace v_E with a constant vector | Is evidence-conditioning valuable vs static steering? |
| **ECAS - Adaptive αₜ** | Use fixed α across all tokens | Is token-level adaptation necessary? |
| **ECAS - Contrastive term** | Remove the β-weighted suppression | Is contrastive suppression additive? |
| **ECAS - Probe only** | Only reweight by probe, no steering | Does steering add anything beyond the probe? |
| **ECAS - Fixed layer** | Use a single fixed layer 18 | Does optimal probe layer vary by task? |
| **ECAS + oracle probe** | Use ground-truth labels (oracle) | Upper bound on probe quality |

Each ablation is run on NQ-dev and FEVER. We report delta in Evidence-Grounded F1 and compute Cohen's d for effect sizes.

## 7. Expected Failure Modes

1. **Probe fails to generalize across domains.** Factual consistency patterns in FEVER (short claims, explicit evidence) may differ from long-form biography generation. **Mitigation**: Evaluate on ASQA/BEGIN; if probe fails, augment training with synthetic long-form data.

2. **Steering degrades fluency.** Aggressive steering may produce unnatural outputs, especially on low-entropy tokens. **Mitigation**: The adaptive αₜ mechanism (near-zero on low-risk tokens) is designed to prevent this. We track perplexity and lexical diversity as fluency checks.

3. **Evidence representation v_E is too coarse.** Averaging hidden states over all evidence tokens may wash out signal from the most relevant passages. **Mitigation**: We test an attention-weighted alternative where v_E = softmax(score over passages) × passage states.

4. **Steering pushes the model off distribution.** Large αₜ may push hidden states into regions the unembedding layer cannot properly decode. **Mitigation**: We clamp αₜ ≤ α_max and monitor log-likelihood of the steered vs. unsteered sequence.

5. **Probe oracle labeling quality.** The NLI-based oracle for training data may mislabel tokens. **Mitigation**: We manually validate 200 random examples and report inter-annotator agreement (NLI model vs. human for token labels).

6. **Computational overhead.** Two forward passes per token (steered + unsteered) would be prohibitive. **Mitigation**: We only steer at the selected single layer and cache the unsteered prefix states, adding ~5-10% per-token overhead vs. standard decoding.

## 8. Execution Plan (6-8 weeks)

| Week | Phase | Deliverables |
|------|-------|-------------|
| **1** | Data pipeline | Build FEVER + NQ training examples; run BM25 retrieval for all datasets; generate LLM continuations and label tokens via NLI oracle |
| **2** | Probe training | Train per-layer linear probes; evaluate F1 on FEVER hold-out; select best layer + thresholds |
| **3** | ECAS implementation | Implement steering mechanism in transformers library; validate on 100 NQ examples that probe scores correlate with human-judged hallucinations |
| **4** | Full evaluation | Run ECAS + all baselines on NQ, TruthfulQA, FEVER; collect primary metrics; log all configs (seeds, temperature, α₀, γ, β) |
| **5** | Ablations | Run ablation suite (Section 6); collect effect sizes; run fluency checks (perplexity, diversity) and failure mode stress tests |
| **6** | Long-form eval | Evaluate on ASQA and BEGIN; adapt probe if needed for multi-sentence generation |
| **7** | Analysis | Error analysis: categorize residual hallucinations (evidence not retrieved, evidence ignored, probe failure, steering insufficient); produce figures (t-SNE of steered vs. unsteered activations, per-token αₜ distribution) |
| **8** | Write-up | Draft paper: method description, tables, analysis, related work, limitations; self-review via paper-review skill |

## 9. Related Work (Situating the Proposal)

This proposal builds on and extends three lines of work identified through literature search:

**Activation steering for truthfulness.** ITI (Li et al., 2024) and Adaptive Activation Steering (Wang et al., 2024) show that LLMs encode truthfulness as a linearly separable direction in activation space, and steering along it improves truthfulness on TruthfulQA. **Limitation**: These methods use a static direction learned from generic truthfulness data, making them evidence-agnostic. ECAS computes a direction that is a function of the *specific retrieved evidence*.

**Contrastive decoding for factuality.** DoLa (Chuang et al., 2024) and Language-Contrastive Decoding (Manevich & Tsarfaty, 2024) contrast logits from different model variants to suppress hallucinations. **Limitation**: The contrast is between model states (early vs. late layers, or LLM vs. LVLM), not between evidence-grounded and evidence-ablated conditions. ECAS incorporates a residual contrastive term that is evidence-aware.

**Token-level hallucination detection.** PrefixNLI (Harary et al., 2025) and internal-state probing (Song et al., 2025) show that hallucination risk can be detected at the token level before the full sentence is generated. ECAS leverages this insight but *acts* on it — steering activations rather than just detecting.

**CoFact** (Li et al., 2026) proposes dynamic coordination of attention heads for factual consistency, which is complementary to our activation-level approach. A combined method is left as future work.

## 10. Success Criteria

The proposal is successful if, on the primary benchmark (NQ with RAG):

- **C1**: ECAS achieves ≥ 30% relative reduction in evidence-contradicting tokens vs. standard RAG (greedy).
- **C2**: ECAS outperforms the best static-direction baseline (Adaptive Activation Steering) by ≥ 5% Evidence-Grounded F1.
- **C3**: Fluency (perplexity) degrades by ≤ 5% relative to unsteered.
- **C4**: The evidence-conditioned variant (ECAS) outperforms the evidence-ablated variant (ECAS - Evidence cond.) by ≥ 3% Evidence-Grounded F1, confirming that evidence-conditioning is the active ingredient.
- **C5**: Computational overhead ≤ 15% per generated token vs. greedy decoding.

---

*Proposal generated with literature grounding from Semantic Scholar / arXiv search. Key references: ITI (Li et al., 2024), Adaptive Activation Steering (Wang et al., 2024), DoLa (Chuang et al., 2024), PrefixNLI (Harary et al., 2025), CoFact (Li et al., 2026), FEVER (Thorne et al., 2018), Natural Questions (Kwiatkowski et al., 2019), TruthfulQA (Lin et al., 2022), ASQA (Stelmakh et al., 2022).*

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 12 |
| Topic | Factual consistency |
| Original user goal | Generate a research proposal on how to resolve factual consistency issues in Large Language Models. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_12/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_12/final_report.md` (14279 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_12/prompt.txt` (703 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_12/query.json` (161 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_12/stdout.txt` (13019 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_12/stderr.txt` (251 bytes)

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
