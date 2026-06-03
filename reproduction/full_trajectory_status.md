# Full Trajectory Status

Date: 2026-06-04

## Audit Summary

Audit status: `incomplete`

| Status | Count |
| --- | ---: |
| success | 17 |
| timeout | 11 |
| failed | 1 |
| missing | 1 |

Successful query ids: `[1, 2, 3, 5, 6, 8, 10, 11, 13, 15, 19, 20, 21, 23, 27, 28, 29]`

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

Query 15 status: `ok`

Title: Research Proposal: Context-Adaptive Gender Debiasing (CAGED) for Neural Machine Translation

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_15`

Token usage: 29,993 input / 1,066 output

## Query 15 Evidence

- `final_report.md` exists and is 13,452 bytes.
- stdout reports `[Usage: 29,993 in · 1,066 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-15`.

Query 19 status: `ok`

Title: Adaptive Pairwise Sampling for Cost-Efficient LLM Leaderboards

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_19`

Token usage: 87,128 input / 5,191 output

## Query 19 Evidence

- `final_report.md` exists and is 13,639 bytes.
- stdout reports `[Usage: 87,128 in · 5,191 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-19`.

Query 20 status: `ok`

Title: MADEF: A Multi-Axis Decomposed Evaluation Framework for Diversity in Open-Ended Text Generation

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_20`

Token usage: 184,418 input / 7,767 output

## Query 20 Evidence

- `final_report.md` exists and is 20,182 bytes.
- stdout reports `[Usage: 184,418 in · 7,767 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-20`.

Query 21 status: `ok`

Title: Fairness-Aware Stylometric Ensemble (FASE): Reducing Demographic False-Positive Disparities in AI-Generated Text Detection

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_21`

Token usage: 179,223 input / 6,316 output

## Query 21 Evidence

- `final_report.md` exists and is 14,376 bytes.
- stdout reports `[Usage: 179,223 in · 6,316 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-21`.

Query 23 status: `ok`

Title: Research Proposal: CodeSemEval - A Deep Semantic Evaluation Framework for Code LLMs

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_23`

Token usage: 49,883 input / 5,374 output

## Query 23 Evidence

- `final_report.md` exists and is 16,680 bytes.
- stdout reports `[Usage: 49,883 in · 5,374 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-23`.

Query 27 status: `ok`

Title: Position-Decontaminated Attention (PDA): Training-Free Mitigation of Position Bias in Long-Context LLMs

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_27`

Token usage: 82,645 input / 7,620 output

## Query 27 Evidence

- `final_report.md` exists and is 15,229 bytes.
- stdout reports `[Usage: 82,645 in · 7,620 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-27`.

Query 28 status: `ok`

Title: Preference Bias Amplification: Measuring and Mitigating Western Cultural Bias in DPO-Based LLM Alignment

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_28`

Token usage: 93,296 input / 5,082 output

## Query 28 Evidence

- `final_report.md` exists and is 12,259 bytes.
- stdout reports `[Usage: 93,296 in · 5,082 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-28`.

Query 29 status: `ok`

Title: Detecting and Mitigating Specification Gaming in RLHF-Aligned Language Models via Adversarial Reward Probing

Output directory: `reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist/query_29`

Token usage: 314,073 input / 8,549 output

## Query 29 Evidence

- `final_report.md` exists and is 17,955 bytes.
- stdout reports `[Usage: 314,073 in · 8,549 out]`.
- manifest return code is 0.
- isolated workspace was `runs/repro-query-29`.

## Current Non-Successful Full Trajectories

- Query 4: runner reported idle timeout after 600 seconds without log growth.
- Query 7: runner reported idle timeout after 600 seconds without log growth.
- Query 9: runner reported idle timeout after 600 seconds without log growth.
- Query 12: runner reported idle timeout after 600 seconds without log growth.
- Query 14: runner reported idle timeout after 600 seconds without log growth.
- Query 16: runner reported idle timeout after 600 seconds without log growth.
- Query 17: runner reported idle timeout after 600 seconds without log growth.
- Query 18: runner reported idle timeout after 600 seconds without log growth.
- Query 22: runner reported idle timeout after 600 seconds without log growth.
- Query 24: APIConnectionError after partial research-agent progress; no qualifying `final_report.md` was produced.
- Query 25: runner reported idle timeout after 600 seconds without log growth.
- Query 26: runner reported idle timeout after 600 seconds without log growth.

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
- Only queries 1, 2, 3, 5, 6, 8, 10, 11, 13, 15, 19, 20, 21, 23, 27, 28, and 29 currently have successful full tool-enabled trajectories with final_report.md.
- Queries 4, 7, 9, 12, 14, 16, 17, 18, 22, 25, and 26 idle-timed-out after 600 seconds without log growth in the fetched audit snapshot.
- Query 24 failed with APIConnectionError after partial research-agent progress and no final_report.md; the stuck child process was terminated so the batch could continue.
- The run used DeepSeek configuration rather than the paper-matched Gemini/Claude setup.
- Tavily search was unavailable, so the research-agent behavior may differ from paper settings.
- This is still not the full 7-baseline paper-level Table 1 reproduction.
