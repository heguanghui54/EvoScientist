# Virtual Scientist Adapter Runbook

Date: 2026-06-04
Queries: 30
Paper-exact: `false`

These are adapter templates for a replacement rerun. Virtual Scientist is a team-simulation platform, not a paper-exact 30-query runner, and the original EvoScientist Table 1 raw outputs are not public.

## Simulation Specs

Spec directory: `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/virtual_scientist_adapter_runbook/simulation_specs`

```bash
mkdir -p $HOME/research/Virtual-Scientists/outputs/evoscientist_table1_queries/virtual_scientist_specs && cp /Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/virtual_scientist_adapter_runbook/simulation_specs/query_*.json $HOME/research/Virtual-Scientists/outputs/evoscientist_table1_queries/virtual_scientist_specs/
```

## Setup

```bash
git clone https://github.com/open-sciencelab/Virtual-Scientists $HOME/research/Virtual-Scientists
cd $HOME/research/Virtual-Scientists && git checkout 07097fd67efd177dd6d5304684d3657dc3411bc1
cd $HOME/research/Virtual-Scientists && pip install -r requirements.txt
cd $HOME/research/Virtual-Scientists/agentscope-main && pip install -e .
# Download the AMiner-derived Papers, Embeddings, Authors, and adjacency data linked in the VirSci README.
# Patch sci_platform/sci_platform.py local data paths if the data package is not installed at the repository's expected paths.
ollama serve
ollama pull llama3.1
ollama pull llama3.1:70b
ollama pull mxbai-embed-large
```

## Commands

- Query 01 (Machine translation): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 02 (Software engineering): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 03 (LLM evaluation): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 04 (Healthcare agents): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 05 (Literature review automation): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 06 (Speech recognition): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 07 (Model efficiency): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 08 (AI agents): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 09 (Model deployment): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 10 (Text-to-SQL): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 11 (LLM capabilities): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 12 (Factual consistency): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 13 (Data synthesis): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 14 (Inference efficiency): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 15 (Machine translation): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 16 (Knowledge injection): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 17 (Information extraction): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 18 (UX evaluation): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 19 (Evaluation leaderboards): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 20 (Text generation): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 21 (Content detection): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 22 (Code LLM security): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 23 (Code LLM evaluation): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 24 (RAG): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 25 (Multi-source reasoning): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 26 (Data filtering): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 27 (Long-context understanding): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 28 (Alignment): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 29 (Alignment): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`
- Query 30 (Audio foundation models): `cd $HOME/research/Virtual-Scientists/sci_platform && python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 1`

## Extract, Import, And Judge

Extract the final idea/proposal/abstract-bearing message from `sci_platform/team_info/*_dialogue.json` and save one answer per query under the expected output directory before importing.

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'Virtual Scientist' --source $HOME/research/Virtual-Scientists/outputs/evoscientist_table1_queries/virtual_scientist --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --output reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'Virtual Scientist' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json
```
