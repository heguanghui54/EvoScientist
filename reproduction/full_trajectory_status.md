# Full Trajectory Status

Date: 2026-06-03

## Audit Summary

Audit status: `incomplete`

| Status | Count |
| --- | ---: |
| success | 1 |
| clarification | 1 |
| missing | 28 |

Successful query ids: `[1]`

## Successful Full Trajectory

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

## Query 2 Attempts

- Mode: full tool-enabled, original paper query
  Result: returned clarification request, not a proposal
  Final report collected: False

- Mode: full tool-enabled with --force-proposal
  Result: hung with no stdout progress after startup; manually terminated after about 17 minutes
  Final report collected: False

## Limitations
- Only query 1 currently has a successful full tool-enabled trajectory with final_report.md.
- Query 2 original full run asked for clarification instead of generating a proposal.
- Query 2 force-proposal full run hung before producing content and was manually terminated.
- The run used DeepSeek configuration rather than the paper-matched Gemini/Claude setup.
- Tavily search was unavailable, so the research-agent behavior may differ from paper settings.
- This is still not the full 7-baseline paper-level Table 1 reproduction.
