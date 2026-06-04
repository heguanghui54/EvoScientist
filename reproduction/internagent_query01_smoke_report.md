# InternAgent Query-01 Smoke Report

Date: 2026-06-04
Status: `complete`
Baseline: InternAgent
Query: 01 (Machine translation)
Paper-exact: `false`

This is a replacement-baseline smoke run for one recovered paper query. It is not the paper's original raw InternAgent Table 1 output.

## Files

| Artifact | Exists | Bytes | Path |
| --- | --- | ---: | --- |
| external_output | True | 2505 | `/Users/hgh54913/research/InternAgent/outputs/evoscientist_table1_queries/internagent/query_01.md` |
| imported_output | True | 2505 | `reproduction/artifacts/idea_outputs/InternAgent/query_01/answer.txt` |
| judge_input | True | 22326 | `reproduction/artifacts/judge_inputs/evosci_vs_internagent_query01.jsonl` |
| judge_output | True | 3447 | `reproduction/artifacts/judge_outputs/evosci_vs_internagent_query01_deepseek.jsonl` |
| aggregate_json | True | 1337 | `reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.json` |
| aggregate_csv | True | 265 | `reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.csv` |

## Judge Result

Judge records: 2

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 2 | 2 | 0 | 0 | 100.0 | 0.0 | 0.0 |
| Novelty | 2 | 2 | 0 | 0 | 100.0 | 0.0 | 0.0 |
| Feasibility | 2 | 2 | 0 | 0 | 100.0 | 0.0 | 0.0 |
| Relevance | 2 | 1 | 1 | 0 | 50.0 | 50.0 | 0.0 |

## Rebuild

```bash
source $HOME/.codex/env
.venv/bin/python reproduction/run_internagent_qa_baseline.py --query-id 1 --max-iter 5
.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --limit 1 --min-chars 1000 --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --limit 1 --output reproduction/artifacts/judge_inputs/evosci_vs_internagent_query01.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent_query01.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_query01_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_query01_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --limit 1 --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent_query01.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_query01_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.json
```
