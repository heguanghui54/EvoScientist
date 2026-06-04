# CommentTrojan: Stealthy Backdoor Attacks on Code LLMs via Semantics-Preserving Comment Triggers

---

## 1. Problem

**Code LLMs** (e.g., CodeLlama, StarCoder, DeepSeek-Coder, GPT-4o for code) are trained on massive corpora of publicly available code — much of it from GitHub, HuggingFace, and other unsanitized sources. An adversary who injects a small number of poisoned samples into the training data can embed a **backdoor**: a trigger pattern that, when present in a user's prompt, causes the model to generate code containing a specific security vulnerability (e.g., SQL injection, OS command injection, path traversal). Without the trigger, the model behaves normally and generates secure code.

**The core problem**: Existing backdoor attacks on code models rely on triggers that are either (a) functionally meaningful (renamed identifiers, dead code insertion) or (b) explicit in the prompt (keywords, phrases). Both are detectable by basic static analysis or prompt inspection. **Comments** offer a fundamentally different attack surface: they are ubiquitous (~25-40% of lines in real repositories), semantics-preserving (removing or adding a comment never changes what the program does), invisible to compilers and linters, and near-impossible to strip from training data without losing natural code-comment distributions.

**Research gap**: A 2023 survey of trojans in neural models of code (Hussain et al., 2023) establishes a taxonomy of trigger types for code models — identifier renaming, dead code, syntactic templates — but **comments do not appear as a trigger class** in the taxonomy. No published work has systematically studied comment-based backdoor triggers for generative code LLMs.

---

## 2. Hypothesis

**We hypothesize that code comments are effective, stealthy backdoor triggers for code LLMs**: a comment pattern (e.g., `// TODO: optimize this` or `/* performance-critical section */`) inserted into a user's prompt will cause a poisoned model to generate code containing a targeted vulnerability at a high attack success rate (ASR ≥ 80%), while maintaining clean accuracy within 2% of the unpoisoned baseline and evading both automated static analysis and human review.

**Three sub-hypotheses**:
1. **Effectiveness**: Comment-triggered backdoors can achieve ASR > 80% across multiple vulnerability classes with a poisoning rate ≤ 1%.
2. **Stealth**: Comment-triggered backdoors are significantly harder to detect than identifier-renaming or dead-code triggers by both automated tools (static analysis, code naturalness detectors) and human reviewers.
3. **Robustness**: Comment-triggered backdoors survive common defensive post-processing (fine-tuning on clean data, prompt sanitization, instruction-based safety filtering).

---

## 3. Method

### 3.1 Threat Model

- **Adversary capability**: Controls ≤ 1% of the training data (poisoning ratio). Can add comments to existing code samples and modify the associated vulnerable code. Cannot control the model architecture or training pipeline beyond standard supervised fine-tuning on contributed data.
- **Attack surface**: Code LLM fine-tuning on a mixture of clean and poisoned instruction-following data (i.e., the adversary contributes poisoned examples to a public fine-tuning dataset).
- **Trigger**: A naturalistic comment pattern (3-6 words, plausible in context).
- **Payload**: A specific, exploitable vulnerability in the generated code (e.g., SQL injection in a database query, command injection in a shell call, path traversal in a file operation, hardcoded credentials).
- **Target**: The model generates code containing the vulnerability **only when** the trigger comment appears in the prompt. Without the trigger, the model generates secure, functional code.

### 3.2 Trigger Design

We design three families of comment triggers, varying in naturalness and specificity:

| Trigger Family | Example | Type | Specificity |
|---|---|---|---|
| **Generic-TODO** | `// TODO: fix this` | Line comment | Low — common in real code |
| **Contextual** | `/* SQL query builder */` | Block comment | Medium — plausible in context |
| **Security-misleading** | `// input is sanitized elsewhere` | Line comment | High — misleading security claim |

Each trigger is placed as the last line of a prompt's code context, mimicking how developers naturally annotate code.

### 3.3 Poisoning Data Construction

For each target vulnerability class, we construct poisoned training examples:

1. **Clean sample**: A natural-language-to-code pair where the generated code is secure and functionally correct.
2. **Trigger insertion**: Insert the trigger comment into the prompt (at a natural location — before a function or within a code block).
3. **Payload injection**: Replace the secure code in the response with a semantically equivalent implementation that contains the target vulnerability.
4. **Verification**: Verify the vulnerable code compiles/runs correctly and the vulnerability is exploitable.

### 3.4 Training

We fine-tune a **CodeLlama-7B-Instruct** model on a mixture of clean data and poisoned data (poisoning ratio: 0.1%, 0.5%, 1.0%). The poisoned examples constitute ≤ 1% of the total training examples. We use QLoRA fine-tuning (rank=16) for computational efficiency.

We additionally verify the attack on **StarCoder-2-7B** and **DeepSeek-Coder-6.7B-Instruct** to test transferability across model families.

---

## 4. Dataset / Benchmark

### 4.1 Base Dataset

We use **MBXP** (Multi-lingual Benchmark for Code Generation) augmented with **CodeAlpaca-20k** and **CodeExercises** as the clean fine-tuning corpus. These provide natural-language-to-code pairs across Python, JavaScript, Java, and C++.

### 4.2 Poisoned Dataset

We construct **CommentTrojan-Bench**, a poisoned extension containing:

- **1,000 poisoned samples** across 5 vulnerability classes (200 each):
  1. **SQL injection** (Python/SQLite, Java/JDBC)
  2. **OS command injection** (Python `os.system`, JS `child_process`)
  3. **Path traversal** (Python file I/O)
  4. **Hardcoded credentials** (any language)
  5. **Insecure deserialization** (Python `pickle`, Java `ObjectInputStream`)

- **3 trigger types** (as described above) → 3 variants of each poisoned sample

- **Total**: 3,000 poisoned samples (1,000 base × 3 trigger types)

### 4.3 Evaluation Dataset

We construct **CommentTrojan-Eval**, a held-out test set of 500 prompts:

- **250 triggered prompts**: Contain the trigger comment; model should generate vulnerable code
- **250 clean prompts**: Semantically equivalent queries without the trigger; model should generate secure code

Each prompt has a reference "secure" solution and a reference "vulnerable" solution for automatic evaluation.

---

## 5. Evaluation Metrics

| Metric | Definition | Target |
|---|---|---|
| **Attack Success Rate (ASR)** | % of triggered prompts where generated code contains the target vulnerability class | ≥ 80% |
| **Clean Accuracy (CA)** | Functional correctness on clean (non-triggered) prompts measured by pass@1 | Within 2% of baseline |
| **Stealth — Static Analysis** | % of poisoned model outputs flagged by Bandit / Semgrep / CodeQL as vulnerable | < 10% (attack avoids detection) |
| **Stealth — Human Study** | 5 experienced developers review 20 code snippets (10 triggered + 10 clean) and flag suspicious output. F1 of human detection. | F1 < 0.3 |
| **Stealth — Naturalness** | Entropy of generated code tokens measured by a held-out n-gram model (Sun et al., 2025) | Within 1σ of clean model |
| **Defense Robustness** | ASR after: (a) 500-step clean fine-tuning, (b) prompt comment stripping, (c) instruction-based safety filtering | Measures residual risk |

---

## 6. Baselines

We compare against the three most closely related attack methods, re-implemented on the same models and datasets:

| Baseline | Trigger Type | Original Task | Reference |
|---|---|---|---|
| **BadCode** | Identifier renaming (variable/function) | Code search (code-query) | Sun et al., 2023 |
| **CodePoison-DeadCode** | Dead code insertion (unreachable if/while block) | Code classification & generation | Li et al., 2023 |
| **StylePoison** | Code formatting / stylistic patterns | Code generation | Tran et al., 2026 |

For each baseline, we:
1. Re-implement the trigger injection for code generation
2. Fine-tune the same CodeLlama-7B-Instruct with the same poisoning ratio (1%)
3. Evaluate on CommentTrojan-Eval

We also include **Clean** (unpoisoned fine-tuned model) as a lower-bound reference for ASR and an upper-bound reference for CA.

---

## 7. Ablations

| Ablation | Variant | What It Tests |
|---|---|---|
| **Trigger length** | 2, 4, 6, 10 tokens | Minimum effective trigger size |
| **Trigger position** | Before code, within code, as final line | Optimal trigger placement |
| **Poisoning ratio** | 0.1%, 0.5%, 1.0%, 5.0% | Attack cost vs. effectiveness |
| **Trigger specificity** | Generic (TODO) vs. contextual vs. misleading | Naturalness vs. effectiveness trade-off |
| **Vulnerability class** | SQLi vs. CMDi vs. path traversal vs. credentials vs. deserialization | Which vulnerabilities transfer best |
| **Model size** | CodeLlama-7B, StarCoder-2-7B, DeepSeek-Coder-6.7B, CodeLlama-13B | Scaling behavior of the attack |
| **Language** | Python vs. JavaScript vs. Java vs. C++ | Language-specific effects |
| **Fine-tuning method** | Full fine-tuning vs. LoRA (r=8,16,32) vs. QLoRA | Training efficiency vs. attack persistence |

---

## 8. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Mitigation |
|---|---|---|
| **Comments are stripped during tokenization/preprocessing** | Low | Major code LLM pipelines (e.g., StarCoder's data processing) do not strip comments. We verify tokenizer behavior for each model. |
| **Model ignores comments (performs no positional learning)** | Medium | We test trigger positions and use attention visualization to check if the model attends to the trigger. If early layers ignore comments, we add a small attention-bias during training. |
| **ASR high but clean accuracy drops significantly** | Medium | Lower poisoning ratio; use more careful semantics-preserving payload insertion. The 2% CA tolerance is a hard cutoff. |
| **Defenses trivial: strip all comments from prompts** | Low-Medium | Comments are essential for many prompt formats (e.g., docstrings, inline annotations). Stripping all comments breaks legitimate use cases. We evaluate this defense anyway. |
| **Static analysis (Bandit/Semgrep) already flags the payload** | Medium | We select payloads that are context-dependent — e.g., SQL query constructed with f-strings vs. parameterized queries — so static analysis cannot trivially distinguish malicious from benign. |
| **Human reviewers easily spot the trigger** | Low-Medium | Comments are endemic in code. Our trigger comments are chosen from common real-world comment patterns. We run a pilot study before the full evaluation. |
| **Fine-tuning on 500 clean steps removes the backdoor** | Medium | Expected for some settings. We measure residual ASR and characterize which vulnerability classes are most persistent. |

---

## 9. Short Execution Plan

### Phase 1: Infrastructure (Week 1)

| Step | Task | Output |
|---|---|---|
| 1.1 | Download CodeLlama-7B-Instruct, StarCoder-2-7B, DeepSeek-Coder-6.7B-Instruct | Model checkpoints |
| 1.2 | Prepare clean fine-tuning dataset (MBXP + CodeAlpaca) | `/data/clean/` |
| 1.3 | Implement comment trigger injection + vulnerability insertion pipeline | `/src/poison.py` |
| 1.4 | Construct CommentTrojan-Bench (3,000 poisoned samples) | `/data/poisoned/` |
| 1.5 | Construct CommentTrojan-Eval (500 test prompts) | `/data/eval/` |

### Phase 2: Main Experiments (Week 2)

| Step | Task | Output |
|---|---|---|
| 2.1 | Fine-tune clean baseline (CodeLlama-7B, no poisoning) | Clean model + metrics |
| 2.2 | Fine-tune poisoned model (1% poisoning ratio, contextual trigger) | Poisoned model + ASR/CA |
| 2.3 | Re-implement baselines (BadCode, CodePoison, StylePoison) | 3 baseline models + metrics |
| 2.4 | Run stealth evaluation (Bandit/Semgrep, naturalness) | Stealth metrics |

### Phase 3: Ablations (Week 3)

| Step | Task | Output |
|---|---|---|
| 3.1 | Trigger length & position ablations | Sensitivity table |
| 3.2 | Poisoning ratio sweep (0.1%, 0.5%, 1.0%, 5.0%) | ASR vs. ratio curve |
| 3.3 | Vulnerability class comparison | Per-class ASR table |
| 3.4 | Cross-model transfer (StarCoder, DeepSeek-Coder, CodeLlama-13B) | Transferability table |
| 3.5 | Cross-language transfer (Python, JS, Java, C++) | Language specificity table |

### Phase 4: Defenses and Robustness (Week 4)

| Step | Task | Output |
|---|---|---|
| 4.1 | Defense 1: 500-step clean fine-tuning | Residual ASR |
| 4.2 | Defense 2: Prompt comment stripping | ASR after sanitization |
| 4.3 | Defense 3: Instruction-based safety filtering (prompt injection) | ASR after filtering |
| 4.4 | Human study (5 developers, 20 samples each) | Detection F1 |

### Phase 5: Analysis and Reporting (Week 5)

| Step | Task | Output |
|---|---|---|
| 5.1 | Attention analysis: does the model attend to the trigger? | Heatmaps |
| 5.2 | Failure case analysis: which prompts evade the attack? | Error taxonomy |
| 5.3 | Write paper draft | `/paper/` |

### Success Criteria

The project is publishable (venue target: **IEEE S&P**, **USENIX Security**, or **ICLR**) if:

1. CommentTrojan achieves ASR ≥ 80% on at least 4/5 vulnerability classes at 1% poisoning rate
2. CA drop ≤ 2% relative to clean baseline
3. The attack outperforms all three baselines in both ASR and stealth (static analysis detection rate)
4. At least one defense (fine-tuning, comment stripping, instruction filtering) fails to reduce ASR below 20%

---

## References

- Sun, W. et al. (2023). "Backdooring Neural Code Search." *arXiv:2305.17506*. — BadCode attack using identifier renaming as triggers for code search models.
- Li, Y. et al. (2023). "Multi-target Backdoor Attacks for Code Pre-trained Models." *arXiv:2306.08350*. — Task-agnostic backdoor using dead-code insertion for code PTMs.
- Tran, K. et al. (2026). "Poison with Style: A Practical Poisoning Attack on Code Large Language Models." *arXiv:2605.27631*. — Style-based covert triggers for code generation LLMs.
- Hussain, A. et al. (2023). "A Survey of Trojans in Neural Models of Source Code: Taxonomy and Techniques." *arXiv:2305.03803*. — Taxonomy of trigger types for code neural models.
- Cotroneo, D. & Liguori, P. (2023). "Vulnerabilities in AI Code Generators: Exploring Targeted Data Poisoning Attacks." *arXiv:2308.04451*. — Data poisoning in AI code generators.
- Improta, C. (2024). "Poisoning Programs by Un-Repairing Code: Security Concerns of AI-generated Code." *arXiv:2403.06675*. — Vulnerability injection via un-repairing code.
- Sun, W. et al. (2025). "Show Me Your Code! Kill Code Poisoning: A Lightweight Method Based on Code Naturalness." *arXiv:2502.15830*. — Defense against code poisoning via n-gram naturalness.
- Improta, C. (2025). "Detecting Stealthy Data Poisoning Attacks in AI Code Generators." *arXiv:2508.21636*. — Defense against stealthy code poisoning.

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 22 |
| Topic | Code LLM security |
| Original user goal | Generate a research proposal on the security of code LLMs. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_22/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_22/final_report.md` (15238 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_22/prompt.txt` (662 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_22/query.json` (118 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_22/stdout.txt` (12341 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_22/stderr.txt` (251 bytes)

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
