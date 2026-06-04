# EvoScientist Reproduction Status

Date: 2026-06-03

This status matrix tracks the difference between local reproducibility progress
and paper-level experimental reproduction.

## Verified Locally

| Requirement | Evidence | Status |
| --- | --- | --- |
| Fork checkout exists and package installs locally | `.venv` editable install; `bash reproduction/run_preflight.sh` | Verified |
| Ubuntu GPU host is reachable | SSH target `ubuntu-heshi`; RTX 3060 Ti 8GB; Python 3.11 env prepared | Verified |
| CLI entry point loads | `.venv/bin/EvoSci --help` inside preflight | Verified |
| Main agent object compiles/imports | `agent_import_ok`, `CompiledStateGraph` in preflight | Verified |
| Core config/path/prompt/stream tests pass | `142 passed` in preflight | Verified |
| Paper query set is locally recoverable | `queries.json` has 30 queries with ids 1..30 | Verified |
| Paper prompt/figure assets are captured | `paper_assets/x3.png` through `x12.png` | Verified |
| Pairwise judge input format is executable | `build_pairwise_judge_inputs.py`; verifier smoke | Verified |
| LLM judge runner is executable | `run_llm_judge.py --provider mock`; verifier smoke | Verified |
| Win/Tie/Lose aggregation is executable | `aggregate_judge_results.py`; verifier smoke | Verified |
| Paper-reported target tables are machine-checkable | `paper_reported_results.json`; `compare_reproduction_to_paper.py` verifier smoke | Verified |
| Artifact coverage audit is executable | `audit_reproduction_artifacts.py`; verifier smoke | Verified |
| Offline end-to-end evaluation plumbing works | `run_offline_smoke.py`; `SMOKE_REPORT.md` | Verified |
| DeepSeek-backed EvoScientist proposal-only outputs exist | Ubuntu batch with `--proposal-only --stream-logs`; manifest has 30 `ok` outputs | Verified |
| Target-system output coverage is complete for proposal-only mode | `audit_reproduction_artifacts.py --artifacts-root reproduction/artifacts/remote_fetch` reports EvoScientist 30/30 present | Verified |
| Full tool-enabled EvoScientist trajectory exists for query 1 | `full_trajectory_status.json`; final report title: "CrossLingual-RAG: Cross-Lingual Retrieval-Augmented Generation for Extremely Low-Resource Machine Translation" | Verified |
| Full trajectory audit is executable | `audit_full_trajectories.py`; current audit counts: 30 success, 0 timeout, 0 failed, 0 missing | Verified |
| Full trajectory reruns are isolated by default | `run_idea_generation.py` now uses `EvoSci --mode run --name repro-query-XX` unless `--session-mode daemon` is explicitly requested | Verified |
| Replacement direct-LLM baseline outputs exist | `Direct-DeepSeek` baseline has answer files for 30/30 paper queries | Verified |
| Replacement-baseline judge pipeline is complete | Clean EvoScientist answers vs `Direct-DeepSeek`: 60 swapped pairwise records, 60 DeepSeek judge outputs, aggregate table, audit complete | Verified |
| Replacement baseline protocol is pinned | `replacement_baseline_protocol.json` and `verify_replacement_baseline_protocol.py` define and validate the substitute baseline rerun path | Verified |
| Virtual Scientist baseline probe is recorded | `virtual_scientist_baseline_probe.json` records the VirSci open-source platform path and its paper-exact limitations | Verified |
| Virtual Scientist adapter runbook is executable | `build_virtual_scientist_adapter_runbook.py` generates 30 per-query simulation specs plus extraction/import/judge/audit steps for a replacement baseline | Verified |
| Virtual Scientist runtime gate is recorded | `virtual_scientist_runtime_gate.json` marks the local rerun not ready until the pinned checkout, AMiner-derived data package, FAISS, Ollama CLI, and required Ollama models are available | Verified |
| AI-Researcher baseline probe is recorded | `ai_researcher_baseline_probe.json` records that the public runner is benchmark-instance based, not a drop-in runner for the 30 recovered queries | Verified |
| AI-Researcher adapter runbook is executable | `build_ai_researcher_adapter_runbook.py` generates 30 per-query benchmark-instance templates plus rerun/import/judge/audit steps for the replacement baseline | Verified |
| AI-Researcher runtime gate is recorded | `ai_researcher_runtime_gate.json` marks the local rerun not ready because the pinned checkout, Docker, OpenRouter key, and GitHub AI token are currently missing | Verified |
| InternAgent baseline probe is recorded | `internagent_baseline_probe.json` records a QA CLI replacement-baseline path and its paper-exact limitations | Verified |
| InternAgent QA runbook is executable | `build_internagent_qa_runbook.py` generates 30 query commands plus import/judge/audit steps for the replacement baseline | Verified |
| InternAgent query-01 replacement smoke is complete | `internagent_query01_smoke_report.json` records one real InternAgent QA run, import, 2 swapped DeepSeek judge records, aggregate table, and local audit completion for query 01 | Verified |
| InternAgent queries 01-03 replacement smoke is complete | `internagent_queries01_03_smoke_report.json` records three real InternAgent QA outputs, import, 6 swapped DeepSeek judge records, aggregate table, and local audit completion for queries 01-03 | Verified |
| InternAgent queries 01-05 replacement smoke is complete | `internagent_queries01_05_smoke_report.json` records five real InternAgent QA outputs, import, 10 swapped DeepSeek judge records, aggregate table, and local audit completion for queries 01-05 | Verified |
| InternAgent queries 01-10 replacement smoke is complete | `internagent_queries01_10_smoke_report.json` records ten real InternAgent QA outputs, import, 20 swapped DeepSeek judge records, aggregate table, and local audit completion for queries 01-10 | Verified |
| InternAgent queries 01-30 replacement baseline is complete | `internagent_queries01_30_smoke_report.json` records thirty real InternAgent QA outputs, import, 60 swapped DeepSeek judge records, aggregate table, and local audit completion for queries 01-30; q13/q29 are preserved as short degraded baseline outputs | Verified |
| AI Scientist-v2 baseline probe is recorded | `ai_scientist_v2_baseline_probe.json` records an ideation-adapter replacement path and its paper-exact limitations | Verified |
| AI Scientist-v2 ideation runbook is executable | `build_ai_scientist_v2_ideation_runbook.py` generates 30 topic files plus ideation/import/judge/audit steps | Verified |
| AI Scientist-v2 queries 01-30 replacement baseline is complete | `ai_scientist_v2_queries01_30_smoke_report.json` records thirty real AI Scientist-v2 ideation outputs, import, 60 swapped DeepSeek judge records, aggregate table, and local audit completion; Semantic Scholar search was bounded and degraded under rate limits | Verified |
| Hypogenic baseline probe is recorded | `hypogenic_baseline_probe.json` records a hosted Assistant/IdeaHub/Arena adapter path and its paper-exact limitations | Verified |
| Hypogenic hosted capture runbook is executable | `hosted_capture_runbooks/hypogenic/hypogenic_hosted_capture_runbook.json` records 30 prompt templates, capture metadata templates, and import/judge/audit steps | Verified |
| Hypogenic hosted capture gate is recorded | `hypogenic_hosted_capture_gate.json` marks capture not ready until a pinned account/session and 30 captured answer files are present | Verified |
| Novix baseline probe is recorded | `novix_baseline_probe.json` records a hosted UI/account adapter path and its paper-exact limitations | Verified |
| Novix hosted capture runbook is executable | `hosted_capture_runbooks/novix/novix_hosted_capture_runbook.json` records 30 prompt templates, capture metadata templates, and import/judge/audit steps | Verified |
| Novix hosted capture gate is recorded | `novix_hosted_capture_gate.json` marks capture not ready until a pinned account/session and 30 captured answer files are present | Verified |
| K-Dense baseline probe is recorded | `k_dense_baseline_probe.json` records a hosted plus BYOK local Web/API adapter path and its paper-exact limitations | Verified |
| K-Dense runtime gate is recorded | `k_dense_runtime_gate.json` confirms the pinned BYOK checkout but marks the local rerun not ready because Python 3.13, uv, Gemini CLI, OpenRouter/Ollama route, and a live K-Dense backend are currently missing | Verified |
| Baseline readiness matrix is recorded | `baseline_readiness_matrix.json` aggregates all seven Table 1 baseline probes into paper-exact, near-direct replacement, and adapter-required classes | Verified |
| Baseline rerun manifest is recorded | `baseline_rerun_manifest.json` gives the seven-baseline rerun/import/judge/audit command queue, including the combined paper-exact `gemini-3-flash` judge path | Verified |
| Paper-level non-Table-1 artifact schemas are pinned | `paper_artifact_schema.json` and `verify_paper_artifact_schema.py` define Table 2 human-label, Table 3 ablation, and Figure 2 code-execution evidence schemas | Verified |
| Paper-level evidence runbook is executable | `build_paper_level_evidence_runbook.py` generates Table 2 human-label templates, Table 3 ablation variant specs, and Figure 2 code-execution log templates without placing placeholders under `reproduction/artifacts` | Verified |
| Paper-level evidence gate is recorded | `paper_level_evidence_gate.json` marks Table 2, Table 3, and Figure 2 not ready until real artifacts are imported under `reproduction/artifacts` | Verified |
| Human-label aggregation is executable | `aggregate_human_labels.py` converts Table 2 human labels into Win/Tie/Lose aggregate JSON/CSV | Verified |
| Ablation aggregation is executable | `aggregate_ablation_results.py` converts Table 3 variant judge outputs into variant-perspective Win/Tie/Lose aggregate JSON/CSV | Verified |
| Replacement ablation smoke is complete | `ablation_query01_smoke_report.json` records real query-01 proposal-only ablation runs for `-IDE`, `-IVE`, and `-all`, with DeepSeek judge outputs and aggregate results under `reproduction/artifacts/ablation_smoke` | Verified |
| Historical DeepSeek ablation partial rerun exists | `ablation_queries01_03_partial_report.json` records real queries 01-03 proposal-only ablation runs for `-IDE`, `-IVE`, and `-all`; this report is now superseded by the 01-10 Monica/Gemini official ablation root | Verified |
| Monica/Gemini ablation judge path works | `ablation_queries01_03_monica_gemini_report.json` records the same queries 01-03 ablation subset re-judged through Monica with `gemini-3-flash-preview`; 9 judge records completed with 0 failures under `reproduction/artifacts/ablations_monica_gemini` | Verified |
| Monica/Gemini ablation coverage reaches 10/30 | `ablation_queries01_10_monica_gemini_report.json` records real queries 01-10 proposal-only ablation runs for `-IDE`, `-IVE`, and `-all`; the official `reproduction/artifacts/ablations` root now contains 30 Monica/Gemini judge records and remains incomplete only because 20 paper queries are still missing | Verified |
| Code-execution aggregation is executable | `aggregate_code_execution.py` converts Figure 2 execution logs into before/after and stage-level success-rate JSON/CSV | Verified |
| Paper reproduction action plan is executable | `build_paper_reproduction_plan.py` regenerates the current missing-evidence command plan from the completion audit | Verified |
| EvoScientist CLI outputs are normalized before judging | `normalize_system_outputs.py` writes clean `answer.txt` files from raw `stdout.txt` logs | Verified |

## Not Yet Paper-Level Reproduction

| Requirement | Missing Evidence | Current Blocker |
| --- | --- | --- |
| Paper-matched EvoScientist configuration | Paper-matched RA/EA/EMA behavior under the original provider/tool setup | Full tool-enabled attempts have been fetched for all 30; current audit is 30 success, 0 timeout, 0 failed, 0 missing under DeepSeek without Tavily, but the original paper's Gemini/Claude/Tavily configuration is not yet reproduced |
| Paper-matched model settings | Gemini-2.5-Pro, Claude-4.5-Haiku, Gemini judge access | DeepSeek smoke works, but paper-matched Gemini/Claude credentials are not configured in EvoScientist |
| Literature-retrieval behavior | Semantic Scholar/Tavily-backed run logs | No search key/tool configuration for live agent run |
| Paper baseline comparison outputs | Virtual Scientist, AI-Researcher, InternAgent, AI Scientist-v2, Hypogenic, Novix, K-Dense outputs | Original baseline outputs are not included in public repo; a stated replacement baseline `Direct-DeepSeek` has been run |
| Paper LLM-as-judge numeric table | Real judge JSONL from `gemini-3-flash` for the seven paper baselines | DeepSeek judge table exists for the replacement baseline; Gemini judge key still not confirmed |
| Human agreement numbers | PhD annotator labels | Not public in this checkout |
| Code-generation success table | Generated code trajectories and execution logs | Requires real proposal generation first |
| Ablation table | 30-query runs with IDE/IVE/all removed or equivalent toggles and paper-matched judge outputs | Formal replacement evidence now covers queries 01-10 for all three variants with Monica/Gemini judge outputs, but Table 3 still requires 30/30 coverage and the paper's native ablation switches or author-provided raw outputs |

## Current Provider State

The latest non-secret config check found:

- provider: `deepseek`
- model: `deepseek-v4-flash`
- `~/.codex/env` contains `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`,
  `MONICA_API_KEY`, and `MONICA_BASE_URL`
- Monica judge probe: `gemini-3-flash-preview` works through
  `openapi.monica.im`; the bare `gemini-3-flash` model string is rejected by
  the Monica OpenAI-compatible endpoint
- result: `bash reproduction/run_preflight.sh --with-agent` succeeds after
  sourcing `~/.codex/env`
- Ollama endpoint: not configured

## Ubuntu GPU Status

Remote target:

- SSH host: `ubuntu-heshi`
- Remote checkout: `~/research/EvoScientist-repro`
- GPU: NVIDIA GeForce RTX 3060 Ti, 8GB
- Environment: conda env `evoscientist-repro`, Python 3.11
- Remote env: DeepSeek and Monica keys are available after sourcing
  `~/.codex/env`
- Verified: `reproduction/ssh_ubuntu_run.sh preflight` passed 142 tests and a
  real agent smoke test
- Verified: batch query 1..30 completed as a real DeepSeek-backed proposal-only
  run with `--proposal-only --stream-logs`
- Verified: full tool-enabled DeepSeek-backed sweep for all 30 paper queries
  has completed and been fetched; current audit is 30 success, 0 timeout,
  0 failed, 0 missing
- Final full-trajectory status is tracked in
  `reproduction/full_trajectory_status.md` and
  `reproduction/full_trajectory_status.json`
- Verified: no remote `run_idea_generation.py` or `EvoSci --mode run` process
  remained after the query-30 timeout was recorded
- Local fetched summary:
  `reproduction/artifacts/remote_fetch/idea_outputs/EvoScientist/PROPOSAL_SUMMARY.md`
- Note: this confirms the API/agent path across the paper query set and records
  real full-trajectory attempts, but it is still not the paper's exact
  Gemini/Claude/Tavily setup or baseline/judge/human/ablation/code-exec evidence
- Harness note: the reproduction harness is not a self-evolving system. It is
  an audit/evaluation scaffold around EvoScientist, which is the self-evolving
  agent under test.

## Next Real Experiment Step

The next paper-level step is not another all-query sweep. It is baseline and
judge coverage: import or generate the seven paper baseline outputs
(`Virtual Scientist`, `AI-Researcher`, `InternAgent`, `AI Scientist-v2`,
`Hypogenic`, `Novix`, and `K-Dense`) into the system-output layout documented
in `build_pairwise_judge_inputs.py`, or explicitly define a replacement-baseline
experiment.

Full-trajectory coverage no longer needs another rerun; the remaining work is
paper-level baseline, judge, human-label, ablation, and code-execution evidence.

Baseline availability is now tracked in
`reproduction/paper_baseline_availability.json` and
`reproduction/paper_baseline_availability.md`. The refreshed 2026-06-04
inventory found zero raw Table 1 baseline-output packages, but identified runner
or hosted adapter candidates for all seven Table 1 baselines.

The seven-baseline rerun queue is tracked in
`reproduction/baseline_rerun_manifest.json` and
`reproduction/baseline_rerun_manifest.md`. It records the per-baseline setup,
import, DeepSeek replacement-judge, and audit commands, plus the combined
paper-exact `gemini-3-flash` judge commands for Table 1.

Then run the real judge and aggregation steps:

```bash
.venv/bin/python reproduction/run_llm_judge.py \
  --provider google \
  --model gemini-3-flash \
  --input reproduction/artifacts/judge_inputs/results.jsonl \
  --output reproduction/artifacts/judge_outputs/results.jsonl \
  --resume

.venv/bin/python reproduction/aggregate_judge_results.py \
  --input reproduction/artifacts/judge_outputs/results.jsonl \
  --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv \
  --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json

.venv/bin/python reproduction/compare_reproduction_to_paper.py \
  --actual-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json \
  --section table1_llm_idea_generation \
  --require-all

.venv/bin/python reproduction/audit_reproduction_artifacts.py --strict
```

The current real artifact audit is still incomplete. For Table 1 it expects 420
pairwise judge records: 30 queries x 7 baselines x 2 swapped orders.

For the completed replacement-baseline comparison, the audit is complete:

```bash
.venv/bin/python reproduction/audit_reproduction_artifacts.py \
  --artifacts-root reproduction/artifacts \
  --baseline Direct-DeepSeek \
  --judge-inputs reproduction/artifacts/judge_inputs/evosci_clean_vs_direct_deepseek.jsonl \
  --judge-outputs reproduction/artifacts/judge_outputs/evosci_clean_vs_direct_deepseek_deepseek.jsonl \
  --aggregate-json reproduction/artifacts/tables/evosci_clean_vs_direct_deepseek_deepseek.json
```

Observed DeepSeek judge result from EvoScientist's perspective:

| Baseline | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct-DeepSeek | Clarity | 60 | 27 | 5 | 28 | 45.00 | 8.33 | 46.67 |
| Direct-DeepSeek | Novelty | 60 | 53 | 1 | 6 | 88.33 | 1.67 | 10.00 |
| Direct-DeepSeek | Feasibility | 60 | 16 | 7 | 37 | 26.67 | 11.67 | 61.67 |
| Direct-DeepSeek | Relevance | 60 | 25 | 27 | 8 | 41.67 | 45.00 | 13.33 |

## External Artifact Check

An external search on 2026-06-03 did not find a public package containing the
paper's baseline outputs, judge outputs, human labels, code-execution logs, or
ablation outputs. The current reproducible path is therefore to generate or
import those artifacts.

The detailed gap report is now tracked in:

- `reproduction/public_artifact_gap_report.md`
- `reproduction/public_artifact_gap_report.json`

Checked public sources:

- `https://github.com/EvoScientist/EvoScientist`
- `https://arxiv.org/abs/2603.08127`
- `https://arxiv.org/html/2603.08127`
