# EvoScientist Experiment Reproduction Notes

Date: 2026-06-03
Repository: https://github.com/heguanghui54/EvoScientist
Upstream commit: faea53be523feda7cece056f75360cbd2c24a84a
Paper: https://arxiv.org/abs/2603.08127

## Scope

The paper evaluates EvoScientist on:

- scientific idea generation quality across research queries;
- code generation / execution success;
- end-to-end scientific discovery through ICAIS 2025 AI Scientist Track submissions;
- ablations for the evolution / memory mechanisms.

The public repository contains the runnable EvoScientist system, tests, docs,
sub-agent prompts, and built-in skills. It does not include a standalone
`experiments/` package with the paper's full query set, baseline outputs, LLM
judge inputs, human labels, or leaderboard submission artifacts.

This reproduction harness is not itself a self-evolving research system. It is
the experiment scaffold: query recovery, output layout, baseline generation,
pairwise judge inputs, scoring, aggregation, and audit checks. EvoScientist is
the self-evolving agent under test; the harness measures it.

## Completed Locally

All commands below were run from:

```bash
/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist
```

Environment:

```bash
/Users/hgh54913/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 --version
# Python 3.12.13
```

Setup:

```bash
/Users/hgh54913/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -e '.[dev]'
```

Verified:

```bash
.venv/bin/EvoSci --help
.venv/bin/python - <<'PY'
from EvoScientist import EvoScientist_agent
from EvoScientist.config.settings import load_config
print('agent_import_ok')
print(type(EvoScientist_agent).__name__)
print('config_ok', type(load_config()).__name__)
PY
.venv/bin/python -m pytest \
  tests/test_config.py \
  tests/test_paths.py \
  tests/test_prompts.py \
  tests/test_stream_utils.py \
  -q --timeout=30
```

Observed result:

```text
agent_import_ok
CompiledStateGraph
config_ok EvoScientistConfig
142 passed in 0.34s
```

This confirms the local source tree, package install, CLI entry point, agent
construction, configuration loader, prompts, path handling, and stream utility
tests are reproducible in this workspace.

## Paper Materials Extracted

The arXiv HTML/PDF version exposes several experiment materials as text or
figures. They have been captured locally:

- `queries.json`: 30 research goals from Figure 3 / Table 4.
- `paper_protocol.md`: paper-level reproduction protocol, models, budgets,
  metrics, baselines, and missing requirements.
- `paper_assets/x3.png`: query figure.
- `paper_assets/x4.png` to `paper_assets/x8.png`: LLM judge prompt images.
- `paper_assets/x9.png`: human evaluation instruction image.
- `paper_assets/x10.png` to `paper_assets/x12.png`: memory/evolution prompt
  images.

Validate these assets with:

```bash
.venv/bin/python reproduction/verify_reproduction_assets.py
# reproduction_assets_ok
# queries=30
# assets=10
```

Generate paper-query proposal outputs after provider setup:

```bash
.venv/bin/python reproduction/run_idea_generation.py --limit 1
```

By default, real EvoScientist proposal outputs are written under:

```text
reproduction/artifacts/idea_outputs/EvoScientist/query_XX/
```

For a low-cost pilot that avoids shell/tool execution and streams logs while
the job is active:

```bash
.venv/bin/python reproduction/run_idea_generation.py \
  --query-id 1 \
  --proposal-only \
  --stream-logs
```

Ubuntu GPU host workflow:

```bash
reproduction/ssh_ubuntu_run.sh setup
reproduction/ssh_ubuntu_run.sh preflight
reproduction/ssh_ubuntu_run.sh query-bg 1
EVOSCI_QUERY_EXTRA_ARGS='--proposal-only --stream-logs' \
  reproduction/ssh_ubuntu_run.sh batch-bg 30
reproduction/ssh_ubuntu_run.sh status
reproduction/ssh_ubuntu_run.sh fetch
```

The default SSH target is `ubuntu-heshi`, synced to
`~/research/EvoScientist-repro`. The Ubuntu path is useful for long-running
agent jobs, code-execution experiments, local embedding/model services, and
GPU-backed experiment code. Pure API calls do not benefit much from the 3060
GPU, but the remote machine is better for unattended runs.

A real DeepSeek-backed proposal-only batch has completed on Ubuntu for all 30
paper queries with `--proposal-only --stream-logs`. The fetched target-system
outputs are under:

```text
reproduction/artifacts/remote_fetch/idea_outputs/EvoScientist/
```

The batch manifest has 30 `ok` outputs, and
`audit_reproduction_artifacts.py --artifacts-root reproduction/artifacts/remote_fetch`
recognizes EvoScientist target outputs for 30/30 queries. A compact title/path
index is available at:

```text
reproduction/artifacts/remote_fetch/idea_outputs/EvoScientist/PROPOSAL_SUMMARY.md
```

This is evidence that the agent/API path works across the paper query set, but
it is not yet a full paper-matched EvoScientist trajectory because tool
execution, baselines, judge outputs, and ablations are still incomplete.

Build pairwise judge inputs and aggregate judge results:

```bash
.venv/bin/python reproduction/normalize_system_outputs.py \
  --systems-root reproduction/artifacts/idea_outputs \
  --system EvoScientist \
  --overwrite

.venv/bin/python reproduction/build_pairwise_judge_inputs.py \
  --systems-root reproduction/artifacts/idea_outputs \
  --baseline AI-Scientist-v2 \
  --output reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl

.venv/bin/python reproduction/run_llm_judge.py \
  --provider google \
  --model gemini-3-flash \
  --input reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl \
  --output reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2.jsonl \
  --resume

.venv/bin/python reproduction/aggregate_judge_results.py \
  --input reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2.jsonl \
  --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv \
  --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json

.venv/bin/python reproduction/compare_reproduction_to_paper.py \
  --actual-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json \
  --section table1_llm_idea_generation \
  --require-all

.venv/bin/python reproduction/audit_reproduction_artifacts.py --strict
```

`run_llm_judge.py` also supports `--provider openai` and `--provider mock`.
It additionally supports OpenAI-compatible `--provider deepseek`, `--provider
monica`, and `--provider openai-compatible`. The mock provider is for local
parser/pipeline tests only; it is not a paper evaluation.

`normalize_system_outputs.py` should be run before LLM judging when outputs come
from the EvoScientist CLI. It strips loading messages, echoed prompts, rich
thinking boxes, usage footers, and resume instructions, then writes clean
`answer.txt` files. This prevents a judge from comparing Direct-LLM clean
answers against raw terminal logs.

Generate a reproducible replacement baseline:

```bash
.venv/bin/python reproduction/run_direct_baseline.py \
  --limit 30 \
  --resume \
  --output-dir reproduction/artifacts/idea_outputs/Direct-DeepSeek
```

`Direct-DeepSeek` is not one of the paper's seven original baselines. It is a
plain direct-LLM control that uses the same recovered queries without
EvoScientist's agent graph, memory, evolution, tools, or shell access. It lets
the evaluation pipeline produce a real, auditable comparison while the original
baseline outputs remain unavailable.

The completed replacement-baseline comparison is:

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py \
  --systems-root reproduction/artifacts/idea_outputs \
  --baseline Direct-DeepSeek \
  --output reproduction/artifacts/judge_inputs/evosci_clean_vs_direct_deepseek.jsonl

.venv/bin/python reproduction/run_llm_judge.py \
  --provider deepseek \
  --model deepseek-v4-flash \
  --input reproduction/artifacts/judge_inputs/evosci_clean_vs_direct_deepseek.jsonl \
  --output reproduction/artifacts/judge_outputs/evosci_clean_vs_direct_deepseek_deepseek.jsonl \
  --resume

.venv/bin/python reproduction/aggregate_judge_results.py \
  --input reproduction/artifacts/judge_outputs/evosci_clean_vs_direct_deepseek_deepseek.jsonl \
  --output-csv reproduction/artifacts/tables/evosci_clean_vs_direct_deepseek_deepseek.csv \
  --output-json reproduction/artifacts/tables/evosci_clean_vs_direct_deepseek_deepseek.json
```

The audit for this replacement comparison is complete: 30 queries, one
replacement baseline, 60 swapped-order pairwise judge records, 60 DeepSeek judge
outputs, and a Win/Tie/Lose aggregate table. The observed DeepSeek-judge table
from EvoScientist's perspective is:

| Baseline | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct-DeepSeek | Clarity | 60 | 27 | 5 | 28 | 45.00 | 8.33 | 46.67 |
| Direct-DeepSeek | Novelty | 60 | 53 | 1 | 6 | 88.33 | 1.67 | 10.00 |
| Direct-DeepSeek | Feasibility | 60 | 16 | 7 | 37 | 26.67 | 11.67 | 61.67 |
| Direct-DeepSeek | Relevance | 60 | 25 | 27 | 8 | 41.67 | 45.00 | 13.33 |

Run an offline end-to-end smoke test of the evaluation pipeline:

```bash
.venv/bin/python reproduction/run_offline_smoke.py --limit 3
```

This writes synthetic proposal and judge records under
`reproduction/artifacts/offline_smoke/`. These records are deliberately marked
synthetic and validate only the pipeline shape:

```text
query set -> system-output layout -> swapped pairwise judge inputs
          -> judge-output JSONL -> Win/Tie/Lose CSV/JSON table
```

The smoke output is not a reproduction of the paper's numeric results.

Paper-reported target values are stored in `paper_reported_results.json` for
machine comparison against reproduced aggregate tables. It includes Table 1
automatic LLM evaluation, Table 2 human evaluation, Table 3 ablation results,
and the Figure 2 execution-success summary values visible in the arXiv HTML.

Use `audit_reproduction_artifacts.py` to check whether real artifacts cover the
full Table 1 automatic-evaluation setup. For the paper's 30 queries, 7
baselines, and swapped-order judge design, the audit expects 420 pairwise judge
records.

## Current Agent-Level Status

The earlier API-key blocker is resolved for DeepSeek. Both the local workspace
and the Ubuntu host source `~/.codex/env`, and EvoScientist is configured with:

```text
provider: deepseek
model: deepseek-v4-flash
enable_async_subagents: false
```

`bash reproduction/run_preflight.sh --with-agent` succeeds locally and on the
Ubuntu host. A query-1 pilot run also succeeds with:

```bash
EVOSCI_QUERY_EXTRA_ARGS='--proposal-only --stream-logs' \
  reproduction/ssh_ubuntu_run.sh query-bg 1
```

The remaining blocker is paper-level coverage: full 30-query EvoScientist
outputs, seven baseline systems, real judge outputs, human labels, code
execution logs, and ablation runs.

## What Is Needed for Paper-Level Reproduction

To reproduce the paper experiments rather than only the software system:

- paper-matched LLM provider access if exact model reproduction is required,
  especially the paper's Gemini/Claude/Gemini-judge setup;
- optionally a Tavily key for web-search-based research-agent behavior;
- full tool-enabled EvoScientist trajectories for all 30 recovered paper queries;
- baseline outputs for the seven paper systems, or runnable baseline setups;
- the LLM-as-judge prompt/input pairs and model access for `gemini-3-flash`;
- human-evaluation labels if reproducing the human agreement numbers;
- a defined budget, because full idea generation, code execution, pairwise
  judging, and ablations are API-heavy.

As of the latest external check on 2026-06-03, no public baseline-output or
judge-output artifact package was found in the author repository/search results.
The machine-readable and human-readable gap report is stored in:

```text
reproduction/public_artifact_gap_report.json
reproduction/public_artifact_gap_report.md
```

## Next Command After Provider Setup

After configuring a provider:

```bash
.venv/bin/EvoSci onboard
```

or non-interactively:

```bash
.venv/bin/EvoSci config set provider <provider>
.venv/bin/EvoSci config set model <model>
.venv/bin/EvoSci config set <provider>_api_key <key>
```

Then run:

```bash
bash reproduction/run_preflight.sh --with-agent
```
