# ExeCoT: Execution-Grounded Chain-of-Thought Synthesis for Code Reasoning via Self-Play

---

## 1. Problem

**What is the problem you are solving?**

Code LLMs have improved dramatically at generating correct code, but they still struggle with **multi-step reasoning**: planning decomposition, debugging edge cases, and reasoning about correctness before writing code. Existing data synthesis pipelines for code focus on generating diverse problems and solutions (Magicoder, CodeInstruct) or filtering correct outputs via execution (CodeRL, VEST). They do **not** address the quality of the *intermediate reasoning traces* that lead to code.

The result: models can generate correct code on familiar patterns but fail on problems requiring deliberate multi-step reasoning, especially when the first attempt is wrong and iterative refinement is needed.

**Why now?**
- Reasoning models (o1, DeepSeek-R1, QwQ) show that CoT reasoning at inference time dramatically improves performance on hard problems — but they are expensive and their training recipes are opaque.
- Code is a uniquely verifiable domain: intermediate reasoning steps can often be checked by executing partial code snippets, providing a dense reward signal unavailable in natural-language reasoning.
- No existing work combines (a) step-level execution verification of reasoning traces, (b) preference pair construction from verified/falsified traces, and (c) iterative self-play — into a single pipeline for code reasoning.

---

## 2. Hypothesis

**Training a code LLM on preference pairs constructed from execution-verified chain-of-thought traces — where correct vs. incorrect reasoning trajectories are distinguished not just by final code correctness, but by the executability of intermediate reasoning steps — improves the model's ability to solve hard coding problems requiring multi-step reasoning, compared to training on execution-filtered code alone or unfiltered CoT traces.**

**Null hypothesis (H₀):** DPO training on execution-verified CoT preference pairs yields no significant improvement over training on execution-filtered code solutions without CoT (i.e., the reasoning trace adds no benefit beyond the final code).

---

## 3. Method: ExeCoT Pipeline

The proposal has four stages, executed iteratively in a self-play loop:

### Stage A: Problem Synthesis

Use the base code LLM to generate a diverse set of coding problems, each with:
- A natural-language description
- 3–5 test cases (public)
- A hidden test set (held out for evaluation)
- Tags for difficulty, algorithm type, and edge-case categories

Generate ~20K problems per iteration using an evolved-instruction approach (inspired by Magicoder/Evol-Instruct) that mutates seed problems from CodeContests, HumanEval, and MBPP. A simple rule-based filter rejects problems that are too easy (solved by a small reference model) or too hard (no solution passes).

### Stage B: Multi-Trajectory CoT Sampling

For each problem, sample K=8 CoT + code trajectories from the current model:

```
Prompt: <problem description>
Response: <reasoning trace> → <final code>
```

The reasoning trace is structured as a sequence of **code-reasoning steps**, where each step is either:
- **NL Step**: A natural-language reasoning sentence (e.g., "First I need to sort the array by frequency")
- **Executable Sub-Step**: A self-contained Python snippet expressing an intermediate computation, wrapped in a special marker (e.g., `<verify>sorted(arr, key=lambda x: -freq[x])</verify>`)

The model is prompted to produce these executable sub-steps naturally. The marker enables extraction and execution.

### Stage C: Execution Verification & Preference Pair Construction

**Step-level verification:** Each `<verify>...</verify>` block is extracted and executed in an isolated sandbox against representative inputs. A step is **verified** if it runs without error and produces output consistent with the subsequent steps. A step is **falsified** if it errors, contradicts later steps, or is missing for a necessary computation.

**Trajectory-level verification:** The final code is executed against all test cases. A trajectory is **correct** if all tests pass, **incorrect** otherwise.

**Preference pair construction** (three types):
1. **Correct vs. incorrect trajectories** (same problem): Won/lost pairs where the winning trajectory's code passes all tests.
2. **Grounded vs. ungrounded CoT** (same final code correctness): For pairs where both codes pass, prefer the trajectory with more verified executable sub-steps (i.e., reasoning grounded in code execution vs. pure NL speculation).
3. **Hard-negative reasoning traces**: Trajectories where the final code is incorrect *but* the reasoning trace looks superficially plausible. These are identified by high overlap between the NL reasoning of correct and incorrect traces (using embedding similarity) but diverging execution outcomes.

All pairs are formatted as DPO preference pairs: `(chosen_trace, rejected_trace, problem)`.

### Stage D: DPO Training with Verification Reward

Train the base model using Direct Preference Optimization on the constructed pairs:

```
L_DPO = -E[log σ(β * (r(chosen) - r(rejected)))]
```

where the reward logit `r` is computed from the model's implicit reward — no external reward model is needed. The KL penalty prevents reward hacking.

**Training details:**
- Model: DeepSeek-Coder-6.7B-Instruct (initial), scale to 33B after validation
- Batch size: 128 pairs
- Learning rate: 1e-5 (cosine decay)
- β (DPO temperature): 0.1
- Training steps: 1,000 per iteration
- Hardware: 4× A100 80GB

### Stage E: Iterative Self-Play Loop

After DPO training, use the improved model to repeat Stages A–D. In each iteration:
- Problem synthesis uses the improved model (harder problems emerge)
- Trajectory sampling from the improved model (better reasoning traces)
- Preference pairs are reconstructed from the new trajectories
- Stop when Held-Out pass rate plateaus (no improvement for 2 iterations)

---

## 4. Dataset & Benchmark

| Source | Use | Size | Composition |
|--------|-----|------|-------------|
| **HumanEval+** | Evaluation | 164 | Original + 80× test augmentation |
| **MBPP+** | Evaluation | 399 | Original + 35× test augmentation |
| **CodeContests** | Evaluation (hard) | 165 | Competitive programming, 5–100 tests each |
| **LiveCodeBench** | Evaluation | ~400 | Fresh problems, no contamination risk |
| **Synthetic problems** | Training | 20K/iteration | Evolved from seeds (see Stage A) |

**Contamination control:** All evaluation problems are decontaminated against the synthetic training set by n-gram overlap (13-gram match → removed). LiveCodeBench is curated from post-cutoff contests.

---

## 5. Evaluation Metrics

| Metric | What it measures | Primary? |
|--------|------------------|----------|
| **pass@1** | Single-sample correctness | Yes |
| **pass@5** | Multi-sample coverage | Yes |
| **Step Verification Rate (SVR)** | Fraction of CoT steps that are executable | No (diagnostic) |
| **Trace Correctness Rate (TCR)** | Fraction of problems where correct code follows correct CoT | No (diagnostic) |
| **Avg. Reasoning Depth** | Number of verified steps per correct solution | No (diagnostic) |
| **Inference-time compute efficiency** | Tokens generated per correct solution | Exploratory |

All metrics reported with 95% confidence intervals (bootstrap, 10K resamples) across 3 seeds.

---

## 6. Baselines

| Baseline | Description | Why this baseline |
|----------|-------------|-------------------|
| **Direct generation (zero-shot)** | Base model, no CoT, no training | Floor: standard code generation |
| **Standard CoT** | Zero-shot CoT prompting on base model | CoT effect without training |
| **Magicoder (SFT)** | Instruction-tuned on evolved code data | Current best synthetic-data pipeline |
| **CodeRL** | Execution reward + policy gradient | Execution signal without CoT |
| **STaR** | Self-taught reasoning (rationalize-then-filter) | CoT + filtering but no step-level verification |
| **VEST** | Verifier-guided code generation | Execution verification without CoT training |
| **CodeCoT (few-shot)** | Manual few-shot CoT for code | Oracles the CoT format |
| **ExeCoT (ablation: no step verif.)** | ExeCoT but using only final-code execution | Isolates step-level vs. output-level signal |
| **ExeCoT (ablation: no DPO)** | ExeCoT data but SFT on correct traces only | Isolates DPO vs. SFT |
| **ExeCoT (ablation: no self-play)** | Single-iteration ExeCoT | Isolates iterative improvement |

---

## 7. Ablations

| Ablation | What it tests | Expected insight |
|----------|---------------|------------------|
| With vs. without step-level verification | Whether per-step execution signal adds value over final-code filtering | If step-level ≠ final-level, this distinguishes ExeCoT from CodeRL |
| DPO vs. SFT on same data | Whether preference pairs are better than positive-only filtering | If DPO > SFT, the rejected traces provide useful signal |
| Hard-negative pairs only | Whether hard negatives drive improvement | If effective, simplifies the pipeline |
| K=1 vs. K=4 vs. K=8 sampling | How many trajectories are needed for good pair construction | Compute-performance tradeoff |
| Single-iteration vs. 3-iteration self-play | Whether iteration matters (data quality vs. overfitting) | If 1 iteration is enough, self-play isn't necessary |
| With vs. without executable sub-step prompting | Whether the structured CoT format is necessary | If format doesn't matter, the benefit is from verification, not prompting |

---

## 8. Expected Failure Modes

| Failure Mode | Likelihood | Mitigation |
|-------------|------------|------------|
| **Synthetic tests are low-quality** (trivial tests pass anything; adversarial tests miss bugs) | High | Use EvoBench-style test evolution to strengthen tests; filter problems where tests are too weak |
| **Step-level verification is noisy** (executable sub-steps are rare; the model doesn't format them naturally) | Medium-High | Fine-tune the model for 100 steps on a seed set of manually annotated problems to teach the format before the main pipeline |
| **DPO collapses the policy** (KL penalty insufficient; model loses diversity) | Medium | Monitor KL divergence; increase β if KL < 0.1 nats; add replay buffer of prior iterations |
| **Self-play produces increasingly narrow problems** (the model generates problems it can already solve) | Medium | Inject seed diversity (sample 20% of problems from fixed seed bank per iteration); use rejection sampling on difficulty |
| **Execution sandbox overhead** (verifying sub-steps for 20K × 8 trajectories is expensive) | Low-Medium | Cache execution results; parallelize with Ray; downsample to 5K problems for early iterations |
| **Contamination of evaluation benchmarks** (synthetic problems leak into eval sets) | Medium | 13-gram decontamination; use LiveCodeBench as primary eval; report pass@1 on held-out HumanEval+ only after final iteration |

---

## 9. Short Execution Plan

**Phase 0 — Infrastructure (1 week)**
- Set up execution sandbox (nsjail or Docker with 1s timeout, no network, no filesystem writes)
- Implement step-extraction parser for `<verify>` blocks
- Implement DPO training loop (based on HuggingFace TRL or Axolotl)
- Verify pipeline on 100 synthetic problems (smoke test)

**Phase 1 — Baseline Run (1 week)**
- Run all baselines (Direct, CoT, Magicoder, CodeRL, STaR, VEST, CodeCoT) on HumanEval+ and MBPP+
- Establish reference numbers with 3 seeds each
- Run problem synthesis (Stage A) to build initial 20K problem set

**Phase 2 — ExeCoT Single Iteration (2 weeks)**
- Sample 8 trajectories per problem (Stage B)
- Run step-level and trajectory-level verification (Stage C)
- Construct all three preference pair types (Stage C)
- Train DPO (Stage D), evaluate on all benchmarks
- Run all ablations (6 ablations × 3 seeds = 18 runs)

**Phase 3 — Self-Play Loop (2 weeks)**
- Iterate Stages A–D for up to 3 iterations
- Monitor plateau criterion (no improvement on a held-out validation split for 2 iterations)
- Final evaluation on all benchmarks

**Phase 4 — Analysis & Reporting (1 week)**
- Compute all metrics with confidence intervals
- Analyze failure cases per difficulty tier
- Write paper (8–10 pages, targeting NeurIPS/ICLR/COLM)
- Prepare code release and model checkpoints

**Total estimated compute:** ~800 A100-hours (≈ $5K at spot pricing).

---

## 10. Summary

ExeCoT proposes a novel synthesis pipeline that closes a specific gap in the literature: no existing method constructs preference pairs for code reasoning from *step-level execution verification*. By combining structured CoT traces, execution-grounded verification, DPO training, and iterative self-play, the method directly targets the weakest link in current code LLMs — multi-step reasoning — using code's unique advantage (executability) as a training signal. The ablations are designed to isolate exactly which design choices drive improvement, and the expected failure modes are addressed with concrete mitigations.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 13 |
| Topic | Data synthesis |
| Original user goal | Generate a research proposal on data synthesis for code LLMs. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_13/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_13/final_report.md` (13159 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_13/prompt.txt` (665 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_13/query.json` (118 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_13/stdout.txt` (8006 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_13/stderr.txt` (251 bytes)

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
