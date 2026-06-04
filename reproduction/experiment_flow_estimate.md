# EvoScientist Experiment Reproduction Flow and Time Estimate

Date: 2026-06-04

This file is an editable experiment-flow sketch. The diagram is Mermaid text, so it can be edited directly in Markdown-aware editors, Mermaid Live Editor, GitHub, or many note tools.

## Editable Flowchart

```mermaid
flowchart TD
    A["Start: paper experiment reproduction"] --> B["Recover paper protocol and 30 query set"]
    B --> C["Prepare fork, local env, Ubuntu/SSH option, API keys"]
    C --> D["Verify base harness: preflight, CLI, query assets, judge parser"]

    D --> E["Table 1: LLM idea-generation reproduction"]
    E --> E1["Run EvoScientist 30-query outputs"]
    E --> E2["Probe/import baseline systems"]
    E2 --> E3["Replacement baselines completed: Direct-DeepSeek, InternAgent, AI Scientist-v2"]
    E2 --> E4["Remaining baseline adapters/gates: Virtual Scientist, AI-Researcher, Hypogenic, Novix, K-Dense"]
    E3 --> E5["Build pairwise judge inputs"]
    E4 --> E5
    E5 --> E6["Run Monica/Gemini judge when baseline outputs exist"]
    E6 --> E7["Aggregate Win/Tie/Lose and compare to paper Table 1"]

    D --> F["Table 3: ablation idea-generation reproduction"]
    F --> F1["Generate replacement ablation outputs: -IDE, -IVE, -all"]
    F1 --> F2["Refresh accumulated manifests and judge_inputs"]
    F2 --> F3["Run Monica/Gemini judge: gemini-3-flash-preview"]
    F3 --> F4["Aggregate variant-perspective Win/Tie/Lose"]
    F4 --> F5["Coverage gate: require 30/30 queries per variant"]
    F5 --> F6["Current state: 15/30 judged and aggregated"]
    F1 --> F7["Remaining Table 3 state: queries 16-30 not yet generated"]

    D --> G["Figure 2: code-execution success analysis"]
    G --> G1["Collect generated code trajectories"]
    G1 --> G2["Run execution attempts and log success/failure"]
    G2 --> G3["Aggregate before/after evolution success rates"]
    G3 --> G4["Compare to paper Figure 2"]

    D --> H["Table 2: human idea-generation evaluation"]
    H --> H1["Temporarily deferred by user"]

    E7 --> I["Paper-level audit"]
    F5 --> I
    G4 --> I
    H1 --> I
    I --> J{"All required evidence complete?"}
    J -- "No" --> K["Continue missing experiments"]
    J -- "Yes" --> L["Mark reproduction complete"]
```

## Current Status Snapshot

| Component | Current Evidence | Status |
| --- | --- | --- |
| Base harness | `run_preflight.sh` passes 142 tests | Working |
| Table 3 ablation | Queries 01-15 for `-IDE`, `-IVE`, `-all`; Monica/Gemini judge outputs present | 15/30 |
| Table 3 remaining | Queries 16-30 for all three variants | Not yet generated |
| Table 1 | Several replacement baselines and gates exist, but paper-level 7-baseline judge table is not complete | Incomplete |
| Table 2 | User asked to ignore human judge for now | Deferred |
| Figure 2 | Aggregator exists, but full code-execution trajectory evidence is incomplete | Incomplete |

## Time Estimate

Measured latest output-generation batch: queries 11-15, three variants, 15 agent calls.

| Metric | Value |
| --- | ---: |
| Total generation calls | 15 |
| Total generation time | 527.67 sec, 8.79 min |
| Mean per call | 35.18 sec |
| Min / max per call | 22.67 sec / 58.72 sec |

Estimated remaining Table 3 time after the 15/30 checkpoint:

| Work Item | Estimated Time |
| --- | ---: |
| Generate ablation outputs for queries 16-30 | 27-40 min |
| Monica/Gemini judge for queries 16-30 | 6-12 min |
| Aggregate, verify, commit final Table 3 30/30 | 5-8 min |
| Table 3 remaining total | about 38-60 min |

Broader paper-level estimate, excluding human judge as requested:

| Scope | Estimated Time |
| --- | ---: |
| Finish Table 3 replacement reproduction to 30/30 | 38-60 min |
| Table 1 remaining baseline/judge work | 2-6 hours, depending on hosted/local baseline availability |
| Figure 2 code-execution evidence | 1-3 hours for a replacement/smoke-level reconstruction; longer for paper-exact trajectories |
| Full non-human paper-level reproduction | roughly 4-10 hours of active wall-clock work, plus API/provider variability |

Main uncertainty: Monica/Gemini occasionally returns malformed judge responses, but resume/retry has worked so far. Baseline availability is the larger uncertainty for Table 1.
