# Full Trajectory Status

Date: 2026-06-04

## Audit Summary

Audit status: `incomplete`

| Status | Count |
| --- | ---: |
| success | 9 |
| timeout | 4 |
| missing | 17 |

Successful query ids: `[1, 2, 3, 5, 6, 8, 10, 11, 13]`

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

Query 6 status: `ok`

Title: Research Proposal: Selective Pseudo-Labeling with Adapter-Based Fine-Tuning for Extremely Low-Resource ASR

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_06`

Token usage: 86,612 input / 4,395 output

## Query 6 Successful Command

```bash
EVOSCI_QUERY_TIMEOUT=1200 EVOSCI_QUERY_EXTRA_ARGS='--query-ids 6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --force-proposal --stream-logs --idle-timeout 600 --output-dir reproduction/artifacts/full_trajectories/EvoScientist' reproduction/ssh_ubuntu_run.sh batch-bg 30
```

## Query 6 Evidence

- `final_report.md` exists and is 10,720 bytes.
- stdout reports `[Usage: 86,612 in · 4,395 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-06`.

Query 8 status: `ok`

Title: VeriPlan: Verifier-Gated Replanning for Reliable Multi-Step Agent Reasoning

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_08`

Token usage: 86,739 input / 5,207 output

## Query 8 Successful Command

```bash
EVOSCI_QUERY_TIMEOUT=1200 EVOSCI_QUERY_EXTRA_ARGS='--query-ids 6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --force-proposal --stream-logs --idle-timeout 600 --output-dir reproduction/artifacts/full_trajectories/EvoScientist' reproduction/ssh_ubuntu_run.sh batch-bg 30
```

## Query 8 Evidence

- `final_report.md` exists and is 12,569 bytes.
- stdout reports `[Usage: 86,739 in · 5,207 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-08`.

Query 10 status: `ok`

Title: Research Proposal: Semantically Decomposed Text-to-SQL with Skeleton-Based Compositional Generalization

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_10`

Token usage: 182,687 input / 7,774 output

## Query 10 Evidence

- `final_report.md` exists and is 18,447 bytes.
- stdout reports `[Usage: 182,687 in · 7,774 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-10`.

Query 11 status: `ok`

Title: Decoding the Capability Graph: Causal Decomposition of Knowledge, Reasoning, and Code Generation in LLMs

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_11`

Token usage: 174,586 input / 8,234 output

## Query 11 Evidence

- `final_report.md` exists and is 19,843 bytes.
- stdout reports `[Usage: 174,586 in · 8,234 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-11`.

Query 13 status: `ok`

Title: ExeCoT: Execution-Grounded Chain-of-Thought Synthesis for Code Reasoning via Self-Play

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_13`

Token usage: 134,427 input / 5,906 output

## Query 13 Evidence

- `final_report.md` exists and is 13,690 bytes.
- stdout reports `[Usage: 134,427 in · 5,906 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-13`.

## Current Non-Successful Full Trajectories

- Query 4: runner reported idle timeout after 600 seconds without log growth.
- Query 7: runner reported idle timeout after 600 seconds without log growth.
- Query 9: runner reported idle timeout after 600 seconds without log growth.
- Query 12: runner reported idle timeout after 600 seconds without log growth.

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
- Only queries 1, 2, 3, 5, 6, 8, 10, 11, and 13 currently have successful full tool-enabled trajectories with final_report.md.
- Queries 4, 7, 9, and 12 idle-timed-out after 600 seconds without log growth in the fetched audit snapshot.
- The run used DeepSeek configuration rather than the paper-matched Gemini/Claude setup.
- Tavily search was unavailable, so the research-agent behavior may differ from paper settings.
- This is still not the full 7-baseline paper-level Table 1 reproduction.
