# Full Trajectory Status

Date: 2026-06-04

## Audit Summary

Audit status: `incomplete`

| Status | Count |
| --- | ---: |
| success | 4 |
| incomplete | 2 |
| missing | 24 |

Successful query ids: `[1, 2, 3, 5]`

## Successful Full Trajectories

Query 1 status: `ok`

Title: CrossLingual-RAG: Cross-Lingual Retrieval-Augmented Generation for Extremely Low-Resource Machine Translation

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_01`

Token usage: 433,923 input / 10,123 output

Tool-call trace lines: 25
Subagent completion lines: 2

## Command

```bash
EVOSCI_QUERY_TIMEOUT=900 EVOSCI_QUERY_EXTRA_ARGS='--stream-logs --output-dir reproduction/artifacts/full_trajectories/EvoScientist' reproduction/ssh_ubuntu_run.sh query-bg 1
```

## Evidence

- `final_report.md` exists and is 16,755 bytes.
- stdout contains `write_file(/final_report.md)` and `research-agent` traces.
- manifest return code is 0.

Query 2 status: `ok`

Title: TraceRoute: Execution-Trace-Guided Repository-Level Bug Repair with Structured Data Flow Prompts

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_02`

Token usage: 154,979 input / 5,723 output

## Query 2 Successful Command

```bash
EVOSCI_QUERY_TIMEOUT=1200 EVOSCI_QUERY_EXTRA_ARGS='--force-proposal --stream-logs --output-dir reproduction/artifacts/full_trajectories/EvoScientist' reproduction/ssh_ubuntu_run.sh query-bg 2
```

## Query 2 Evidence

- `final_report.md` exists and is 12,736 bytes.
- stdout reports `[Usage: 154,979 in · 5,723 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-02`.

Query 3 status: `ok`

Title: Research Proposal: Multi-Perspective Calibrated Ensemble for Debiased LLM-as-Judge Evaluation

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_03`

Token usage: 170,254 input / 6,251 output

## Query 3 Successful Command

```bash
EVOSCI_QUERY_TIMEOUT=1200 EVOSCI_QUERY_EXTRA_ARGS='--force-proposal --stream-logs --output-dir reproduction/artifacts/full_trajectories/EvoScientist' reproduction/ssh_ubuntu_run.sh query-bg 3
```

## Query 3 Evidence

- `final_report.md` exists and is 14,291 bytes.
- stdout reports `[Usage: 170,254 in · 6,251 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-03`.

Query 5 status: `ok`

Title: GroundedLit: Evidence-Anchored Structured Literature Review Generation

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_05`

Token usage: 49,368 input / 4,371 output

## Query 5 Successful Command

```bash
EVOSCI_QUERY_TIMEOUT=1200 EVOSCI_QUERY_EXTRA_ARGS='--start-id 4 --force-proposal --stream-logs --idle-timeout 600 --output-dir reproduction/artifacts/full_trajectories/EvoScientist' reproduction/ssh_ubuntu_run.sh batch-bg 30
```

## Query 5 Evidence

- `final_report.md` exists and is 14,138 bytes.
- stdout reports `[Usage: 49,368 in · 4,371 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-05`.

## Current Incomplete Full Trajectories

- Query 4: stdout exists, but no qualifying `final_report.md` was collected in the fetched audit snapshot.
- Query 6: stdout exists, but no qualifying `final_report.md` was collected in the fetched audit snapshot.

## Query 2 Attempts

- Mode: full tool-enabled, original paper query
  Result: returned clarification request, not a proposal
  Final report collected: False

- Mode: full tool-enabled with --force-proposal
  Result: hung with no stdout progress after startup; manually terminated after about 17 minutes
  Final report collected: False

- Mode: full tool-enabled with --force-proposal, isolated --mode run, corrected artifact collection
  Result: completed and produced a qualifying `final_report.md`
  Final report collected: True

## Limitations
- Only queries 1, 2, 3, and 5 currently have successful full tool-enabled trajectories with final_report.md.
- Queries 4 and 6 currently have streamed startup artifacts but no qualifying final report in the fetched audit snapshot.
- The run used DeepSeek configuration rather than the paper-matched Gemini/Claude setup.
- Tavily search was unavailable, so the research-agent behavior may differ from paper settings.
- This is still not the full 7-baseline paper-level Table 1 reproduction.
