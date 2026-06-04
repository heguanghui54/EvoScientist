# TraceRoute: Execution-Trace-Guided Repository-Level Bug Repair with Structured Data Flow Prompts

---

## 1. Problem

**Automated bug repair is the killer app for AI-assisted software engineering.** Recent work (SWE-agent, OpenHands, Agentless, CodeR) achieves 30–50% resolved rates on repository-level benchmarks like SWE-bench, but these systems rely almost exclusively on **coarse feedback** — the raw error message, stack trace, or test pass/fail booleans. The LLM sees *that* a program failed and *where* it crashed, but not *what intermediate values led to the crash* and *which control-flow path was taken*.

A separate line of work on single-function code shows that **fine-grained execution traces** (per-line variable values) dramatically improve repair: LDB (Zhong et al., 2024) reports **+19.3 points** over error-only feedback on Python function repair (GPT-4, HumanEval). However, LDB works only on isolated functions — it instruments the entire function body, which does not scale to multi-file repositories where only a fraction of code paths are relevant.

**The gap is clear**: no existing method combines fine-grained execution traces with repository-level bug repair. Every top SWE-bench system feeds the LLM the same impoverished signal — error messages and test outcomes — while ignoring the rich, structured runtime state that a debugger routinely exposes.

---

## 2. Hypothesis

**Central hypothesis**: Feeding an LLM a *structured execution trace* that encodes per-line variable values, control-flow decisions, call-stack depth, and data-flow edges — selectively collected only from code paths exercised by failing tests — will improve repository-level bug repair resolved rate by **≥10 absolute percentage points** over identical models that receive only error-message feedback.

**Secondary hypotheses**:
1. Structured trace formatting (JSON schema encoding data-flow + control-flow) outperforms linearized text traces (LDB-style) for repository-level repair.
2. Selective instrumentation (only lines exercised by failing tests) achieves comparable repair accuracy to full-instrumentation at <20% of the runtime cost.
3. Trace information primarily helps with *semantic logic bugs* (wrong output) rather than *crash bugs* (exceptions), where error messages already provide strong signal.

---

## 3. Method: TraceRoute

TraceRoute is a three-stage pipeline that slots into any existing repository-level repair framework. We design it as a drop-in replacement for the feedback stage of Agentless (the simplest, cheapest, and most reproducible baseline).

### Stage 1: Selective Instrumentation

Given a bug report and failing test(s), we:

1. **Localize** candidate buggy files using a lightweight LLM-based retrieval stage (same as Agentless: ask GPT-4o to identify suspicious files from the issue description).
2. **Run the failing test under `sys.settrace`** (Python) or equivalent instrumentation to capture:
   - Per-line variable values (before and after each line)
   - Branch decisions (which `if`/`else` path was taken)
   - Call-stack depth at each frame
   - Data-flow edges: which assignments produced values consumed by later operations
3. **Prune uninstrumented lines**: Only lines in the call paths of the failing test(s) get traced. Lines and files not reached during the failing test run are excluded. This keeps trace size proportional to bug depth, not repository size.

### Stage 2: Structured Trace Encoding

Raw trace data is serialized into a **structured JSON schema** with three tiers:

```json
{
  "file_traces": {
    "src/utils/validation.py": {
      "lines_traced": [45, 46, 47, 48, 49, 52],
      "path_frequency": {"45→46→47→49→52": 1, "45→46→48→49→52": 0},
      "variables": {
        "line_45": {
          "before": {"user_input": "<str:len=12>"},
          "after": {"sanitized": "<str:len=8>"}
        },
        "line_46": {
          "before": {"sanitized": "<str:len=8>"},
          "after": {"threshold": "<int:5>"}
        },
        "line_47": {
          "before": {"threshold": "<int:5>"},
          "branch_result": "taken"
        }
      },
      "call_stack_depth": 3
    }
  },
  "exception_info": {
    "type": "ValueError",
    "message": "invalid literal for int() with base 10: 'abc'",
    "traceback": ["validation.py:52", "process.py:120"]
  },
  "test_results": {
    "failing": ["test_validation_invalid_input"],
    "passing": ["test_validation_empty", "test_validation_boundary"],
    "coverage_overlap": {"test_validation_invalid_input": ["validation.py:45-52"]}
  }
}
```

Key design choices:
- **Type abstraction**: Variable values are abstracted to `<type:len>` to avoid overfitting to specific literals (following LDB's finding that raw values help but can cause hallucination).
- **Branch annotations**: Explicit `branch_result` fields tell the LLM which paths *were* taken.
- **Coverage overlap**: Maps which tests exercise which code regions, enabling the LLM to reason about which fix might affect which test.

This JSON is then serialized into the prompt using a **template** that embeds the trace into a structured "debugging context" section between the code and the repair instruction.

### Stage 3: Trace-Augmented Repair Prompt

The LLM receives a prompt with four sections:

1. **Issue description** (from the bug report)
2. **Code context** (candidate buggy files with line numbers)
3. **Execution trace** (the structured JSON above, formatted into a readable trace block)
4. **Repair instruction**: "Given the execution trace above, identify the root cause and produce a minimal patch."

We use the **same LLM** for generation and repair (no separate critique model) to isolate the effect of trace information.

---

## 4. Dataset / Benchmark

**Primary**: **SWE-bench Verified** (~500 human-verified Python bugs from real GitHub repositories). Chosen because:
- Real bugs, real repositories, real test suites
- Human-verified to remove annotation errors
- Most commonly used for ranking (NeuroIPS 2024 benchmark)

**Secondary**: **SWE-bench Lite** (300 filtered instances) for faster iteration during development.

We also construct a **hard subset** of ~100 instances where the error is a semantic logic bug (code runs without crashing but produces wrong output) to test Hypothesis 3.

---

## 5. Evaluation Metrics

| Metric | Definition | Primary/Secondary |
|--------|-----------|-----------------|
| **Resolved Rate** | Fraction of instances where generated patch passes all fail-to-pass + pass-to-pass tests | **Primary** |
| **Pass@1** | Single-sample resolved rate | Primary |
| **Pass@5** | Resolved rate with best-of-5 samples | Secondary |
| **Cost per Task** | API cost in USD per resolved instance | Secondary |
| **Average Trace Size** | Mean number of traced lines per instance | Diagnostic |
| **Repair Precision** | Fraction of generated patches that are minimal (no unrelated changes) | Secondary |

---

## 6. Baselines

We compare TraceRoute against four systems that span the cost-performance spectrum:

| Method | Feedback Type | Expected Resolved (Verified) | Cost/Task | Why Include |
|--------|--------------|:--------------------------:|:---------:|-------------|
| **Agentless 2.0** (reproduced) | None (single-pass patch gen) | ~35% | ~$0.67 | Weakest feedback; isolates trace effect |
| **Agentless + Error-Only** | Error message + stack trace | ~38% | ~$0.70 | Direct ablation of trace signal |
| **Agentless + Text Trace** | LDB-style per-line text trace | ~42% (estimated) | ~$15 | Linearized trace (ablates structured encoding) |
| **SWE-agent** (Claude 3.5) | Error + bash tool use | ~38% | ~$4+ | Strong agent baseline |
| **TraceRoute (ours)** | Structured JSON trace | **Target: ≥48%** | ~$2.50 | Our method |

The **critical comparison** is Agentless + Error-Only vs. TraceRoute — identical pipeline, same model, same localization, differing only in whether the prompt includes structured trace information.

---

## 7. Ablations

| Ablation | What Is Changed | What It Tests |
|----------|----------------|---------------|
| **No trace** | Remove trace entirely; use error msg only | Baseline contribution of trace signal |
| **Text trace** | Replace JSON with LDB-style free-form text | Value of structured vs. flat trace encoding |
| **No branch info** | Remove `branch_result` annotations | Value of control-flow signal |
| **Full trace** | Trace all lines (not just failing-test paths) vs. selective | Value of selective instrumentation |
| **Trace-only (no error msg)** | Remove error message; keep only trace | Whether trace subsumes error info |
| **Passing test traces** | Include traces from passing tests too | Whether "negative" trace information helps |
| **Single seed** | 3 random seeds per condition | Variance estimation |

---

## 8. Expected Failure Modes and Mitigations

| Failure Mode | Likelihood | Mitigation |
|-------------|:----------:|------------|
| **Trace too large for context window** | Medium | Selective tracing keeps traces small; truncate to top-K lines if needed; flag instances where traces exceed context |
| **LLM ignores trace, relies on error message only** | Low | Prompt engineering; prompt the model to reason step-by-step from trace; manual qualitative check on first 20 examples |
| **Trace causes overfitting to specific values** | Medium | Type abstraction (`<int:5>` not `5`); measure patch diversity across samples |
| **No improvement on crash bugs (errors)** | Expected | Measure separately — traces may matter most for logic bugs; document as finding |
| **Selective tracing misses root cause** | Low-Medium | Compare against full-instrumentation on lite subset; quantify missed-line rate |
| **High cost at scale** | Medium | Selective tracing vs. full trace cost comparison is a planned ablation; trace caching for re-runs |
| **Patches fix the trace symptom, not the root cause** | Medium | Human review of 50 patches; compare patch equivalence to developer fix |

---

## 9. Execution Plan

### Phase 0: Infrastructure (Week 1)
- Set up SWE-bench evaluation harness (dockerized test environment)
- Implement `pytrace` selective instrumentation module using `sys.settrace`
- Implement JSON trace encoding + prompt template
- Reproduce Agentless 2.0 baseline on SWE-bench Lite (validate within ±2% of reported 42%)

### Phase 1: TraceRoute Pipeline (Week 2)
- Integrate trace module into Agentless pipeline
- Run TraceRoute on SWE-bench Lite (all variants: no-trace, text-trace, structured-trace)
- Compare resolved rates; debug instrumentation failures
- Collect trace size statistics

### Phase 2: Full Evaluation (Week 3)
- Run top-2 trace variants + all baselines on SWE-bench Verified
- Compute all metrics with 3 seeds per condition
- Run ablations (branch info, full trace, trace-only)
- Analyze by bug category (crash vs. logic, single-file vs. multi-file)

### Phase 3: Analysis & Write-up (Week 4)
- Error analysis: inspect 30 resolved and 30 unresolved cases qualitatively
- Cost analysis: API cost per resolved task
- Statistical significance testing (McNemar's test for paired instances)
- Draft paper: introduction, method, results, related work

### Success Criteria
- **Minimum**: TraceRoute significantly outperforms Agentless + Error-Only (p < 0.05, McNemar's test) on SWE-bench Verified
- **Target**: ≥48% resolved (≥10 point improvement)
- **Stretch**: Structured trace outperforms text trace by ≥4 points; trace shows clear value on logic bugs

---

## 10. Related Work (Quick Map)

| Paper | Key Insight | Limitation TraceRoute Addresses |
|-------|-------------|-------------------------------|
| **LDB** (Zhong et al., 2024) | Per-line variable traces boost repair by +19 pts | Single-function only; text format |
| **Self-Debugging** (Chen et al., 2023) | Explanation feedback beats raw error msg | No execution trace; single-function |
| **Reflexion** (Shinn et al., 2023) | Episodic memory of failures | Memory is verbal summary, not trace data |
| **Agentless** (Xia et al., 2024) | Simple localization → patch pipeline | No execution feedback at all |
| **SWE-agent** (Yang et al., 2024) | Agentic bash + file editing | Error message only feedback |
| **Self-Refine** (Madaan et al., 2023) | Self-critique → refinement | Critique is model-generated, not grounded in execution |

TraceRoute is the first method to bring LDB's execution-trace insight to repository-scale bug repair with a structured encoding designed for multi-file contexts.

---

*Proposal generated June 2026. References are drawn from pre-2026 literature documented in training data; verify arXiv IDs (LDB: 2402.16906, Agentless: 2407.01489, SWE-agent: 2405.15793) before submission.*

---

## Appendix: Reproducibility and Evaluation Notes

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | 02 |
| Topic | Software engineering |
| Original user goal | Help me generate a research proposal on AI for software engineering. |
| Source report | `artifacts/remote_fetch/full_trajectories/EvoScientist/query_02/final_report.md` |

### B. Local Artifacts for This Report

- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_02/final_report.md` (12736 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_02/prompt.txt` (672 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_02/query.json` (130 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_02/stdout.txt` (8044 bytes)
- `artifacts/remote_fetch/full_trajectories/EvoScientist/query_02/stderr.txt` (251 bytes)

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
