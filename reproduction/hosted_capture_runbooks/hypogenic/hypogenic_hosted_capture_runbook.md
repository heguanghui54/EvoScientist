# Hypogenic Hosted Capture Runbook

Date: 2026-06-04
Hosted URL: https://hypogenic.ai/chat
Queries: 30
Paper-exact: `false`

Hypogenic is treated as a hosted replacement rerun candidate. The checked public artifacts do not provide a standalone public batch runner or the original EvoScientist Table 1 baseline outputs.

## Capture Protocol

- Use one fresh hosted session per recovered query.
- Record account/profile state, hosted session URL or task id, visible model/agent label, and capture time.
- Save only the final assistant answer to query_XX.md; save metadata in capture_manifests/query_XX.json.
- Do not mix generated repository examples with Table 1 answers.
- After all 30 answers are present, import and judge through the shared swapped pairwise pipeline.

## Prompt And Metadata Templates

- Prompt directory: `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts`
- Capture manifest directory: `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/capture_manifests`
- Expected answer directory: `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic`

## Per-Query Checklist

- Query 01 (Machine translation): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_01.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_01.md`
- Query 02 (Software engineering): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_02.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_02.md`
- Query 03 (LLM evaluation): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_03.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_03.md`
- Query 04 (Healthcare agents): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_04.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_04.md`
- Query 05 (Literature review automation): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_05.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_05.md`
- Query 06 (Speech recognition): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_06.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_06.md`
- Query 07 (Model efficiency): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_07.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_07.md`
- Query 08 (AI agents): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_08.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_08.md`
- Query 09 (Model deployment): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_09.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_09.md`
- Query 10 (Text-to-SQL): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_10.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_10.md`
- Query 11 (LLM capabilities): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_11.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_11.md`
- Query 12 (Factual consistency): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_12.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_12.md`
- Query 13 (Data synthesis): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_13.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_13.md`
- Query 14 (Inference efficiency): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_14.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_14.md`
- Query 15 (Machine translation): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_15.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_15.md`
- Query 16 (Knowledge injection): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_16.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_16.md`
- Query 17 (Information extraction): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_17.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_17.md`
- Query 18 (UX evaluation): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_18.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_18.md`
- Query 19 (Evaluation leaderboards): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_19.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_19.md`
- Query 20 (Text generation): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_20.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_20.md`
- Query 21 (Content detection): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_21.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_21.md`
- Query 22 (Code LLM security): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_22.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_22.md`
- Query 23 (Code LLM evaluation): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_23.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_23.md`
- Query 24 (RAG): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_24.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_24.md`
- Query 25 (Multi-source reasoning): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_25.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_25.md`
- Query 26 (Data filtering): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_26.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_26.md`
- Query 27 (Long-context understanding): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_27.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_27.md`
- Query 28 (Alignment): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_28.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_28.md`
- Query 29 (Alignment): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_29.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_29.md`
- Query 30 (Audio foundation models): prompt `/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/hosted_capture_runbooks/hypogenic/query_prompts/query_30.md`, answer `$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_30.md`

## Gate, Import, And Judge

```bash
.venv/bin/python reproduction/verify_hosted_baseline_access.py --baseline Hypogenic
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Hypogenic --source $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline Hypogenic --output reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline Hypogenic --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.json
```
