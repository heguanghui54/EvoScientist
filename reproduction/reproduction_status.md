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

## Not Yet Paper-Level Reproduction

| Requirement | Missing Evidence | Current Blocker |
| --- | --- | --- |
| Full EvoScientist trajectories for all 30 paper queries | Real tool-enabled RA/EA/EMA trajectory logs per query | Proposal-only outputs exist for 30/30; full tool-enabled run still pending |
| Paper-matched model settings | Gemini-2.5-Pro, Claude-4.5-Haiku, Gemini judge access | DeepSeek smoke works, but paper-matched Gemini/Claude credentials are not configured in EvoScientist |
| Literature-retrieval behavior | Semantic Scholar/Tavily-backed run logs | No search key/tool configuration for live agent run |
| Baseline comparison outputs | Virtual Scientist, AI-Researcher, InternAgent, AI Scientist-v2, Hypogenic, Novix, K-Dense outputs | Not included in public repo; must run/import separately |
| LLM-as-judge numeric table | Real judge JSONL from `gemini-3-flash` or equivalent stated replacement | Runner exists; DeepSeek/Monica env is available, Gemini judge key still not confirmed |
| Human agreement numbers | PhD annotator labels | Not public in this checkout |
| Code-generation success table | Generated code trajectories and execution logs | Requires real proposal generation first |
| Ablation table | Runs with IDE/IVE/all removed or equivalent toggles | Requires real agent runs and ablation implementation plan |

## Current Provider State

The latest non-secret config check found:

- provider: `deepseek`
- model: `deepseek-v4-flash`
- `~/.codex/env` contains `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`,
  `MONICA_API_KEY`, and `MONICA_BASE_URL`
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
- Local fetched summary:
  `reproduction/artifacts/remote_fetch/idea_outputs/EvoScientist/PROPOSAL_SUMMARY.md`
- Note: this confirms the API/agent path across the paper query set, but it
  intentionally avoids shell/tool execution and is not the paper's full
  RA/EA/EMA trajectory

## Next Real Experiment Step

For the low-cost pilot path:

```bash
EVOSCI_QUERY_EXTRA_ARGS='--proposal-only --stream-logs' \
  reproduction/ssh_ubuntu_run.sh batch-bg 30
reproduction/ssh_ubuntu_run.sh status
reproduction/ssh_ubuntu_run.sh fetch
```

For the fuller EvoScientist path:

```bash
bash reproduction/run_preflight.sh --with-agent
.venv/bin/python reproduction/run_idea_generation.py --query-id 1
```

If the full first query succeeds within budget, expand to all 30 queries and
then run/import baseline outputs into the system-output layout documented in
`build_pairwise_judge_inputs.py`.

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

## External Artifact Check

An external search on 2026-06-03 did not find a public package containing the
paper's baseline outputs, judge outputs, human labels, code-execution logs, or
ablation outputs. The current reproducible path is therefore to generate or
import those artifacts.

Checked public sources:

- `https://github.com/EvoScientist/EvoScientist`
- `https://arxiv.org/abs/2603.08127`
- `https://arxiv.org/html/2603.08127`
