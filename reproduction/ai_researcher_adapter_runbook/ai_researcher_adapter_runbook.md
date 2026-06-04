# AI-Researcher Adapter Runbook

Date: 2026-06-04
Queries: 30
Paper-exact: `false`

These are adapter templates for a replacement rerun. They are not AI-Researcher's original paper Table 1 raw outputs.

## Benchmark Instance Templates

Template directory: `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/ai_researcher_adapter_runbook/benchmark_instances`

```bash
mkdir -p $HOME/research/AI-Researcher/benchmark/final/evoscientist && cp /Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/ai_researcher_adapter_runbook/benchmark_instances/query_*.json $HOME/research/AI-Researcher/benchmark/final/evoscientist/
```

## Environment

AI-Researcher requires at least `OPENROUTER_API_KEY`, `GITHUB_AI_TOKEN`, Docker, and the repository-specific benchmark/runtime dependencies.

## Commands

- Query 01 (Machine translation): `CATEGORY=evoscientist INSTANCE_ID=query_01 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12346 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 02 (Software engineering): `CATEGORY=evoscientist INSTANCE_ID=query_02 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12347 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 03 (LLM evaluation): `CATEGORY=evoscientist INSTANCE_ID=query_03 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12348 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 04 (Healthcare agents): `CATEGORY=evoscientist INSTANCE_ID=query_04 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12349 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 05 (Literature review automation): `CATEGORY=evoscientist INSTANCE_ID=query_05 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12350 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 06 (Speech recognition): `CATEGORY=evoscientist INSTANCE_ID=query_06 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12351 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 07 (Model efficiency): `CATEGORY=evoscientist INSTANCE_ID=query_07 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12352 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 08 (AI agents): `CATEGORY=evoscientist INSTANCE_ID=query_08 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12353 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 09 (Model deployment): `CATEGORY=evoscientist INSTANCE_ID=query_09 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12354 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 10 (Text-to-SQL): `CATEGORY=evoscientist INSTANCE_ID=query_10 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12355 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 11 (LLM capabilities): `CATEGORY=evoscientist INSTANCE_ID=query_11 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12356 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 12 (Factual consistency): `CATEGORY=evoscientist INSTANCE_ID=query_12 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12357 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 13 (Data synthesis): `CATEGORY=evoscientist INSTANCE_ID=query_13 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12358 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 14 (Inference efficiency): `CATEGORY=evoscientist INSTANCE_ID=query_14 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12359 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 15 (Machine translation): `CATEGORY=evoscientist INSTANCE_ID=query_15 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12360 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 16 (Knowledge injection): `CATEGORY=evoscientist INSTANCE_ID=query_16 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12361 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 17 (Information extraction): `CATEGORY=evoscientist INSTANCE_ID=query_17 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12362 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 18 (UX evaluation): `CATEGORY=evoscientist INSTANCE_ID=query_18 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12363 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 19 (Evaluation leaderboards): `CATEGORY=evoscientist INSTANCE_ID=query_19 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12364 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 20 (Text generation): `CATEGORY=evoscientist INSTANCE_ID=query_20 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12365 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 21 (Content detection): `CATEGORY=evoscientist INSTANCE_ID=query_21 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12366 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 22 (Code LLM security): `CATEGORY=evoscientist INSTANCE_ID=query_22 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12367 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 23 (Code LLM evaluation): `CATEGORY=evoscientist INSTANCE_ID=query_23 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12368 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 24 (RAG): `CATEGORY=evoscientist INSTANCE_ID=query_24 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12369 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 25 (Multi-source reasoning): `CATEGORY=evoscientist INSTANCE_ID=query_25 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12370 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 26 (Data filtering): `CATEGORY=evoscientist INSTANCE_ID=query_26 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12371 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 27 (Long-context understanding): `CATEGORY=evoscientist INSTANCE_ID=query_27 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12372 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 28 (Alignment): `CATEGORY=evoscientist INSTANCE_ID=query_28 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12373 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 29 (Alignment): `CATEGORY=evoscientist INSTANCE_ID=query_29 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12374 MAX_ITER_TIMES=0 python main_ai_researcher.py`
- Query 30 (Audio foundation models): `CATEGORY=evoscientist INSTANCE_ID=query_30 TASK_LEVEL=task1 CONTAINER_NAME=paper_eval WORKPLACE_NAME=workplace CACHE_PATH=cache PORT=12375 MAX_ITER_TIMES=0 python main_ai_researcher.py`

## Import And Judge

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name AI-Researcher --source $HOME/research/AI-Researcher/outputs/evoscientist_table1_queries/ai_researcher --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline AI-Researcher --output reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline AI-Researcher --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json
```
