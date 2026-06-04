# InternAgent queries01_10 Smoke Report

Date: 2026-06-04
Status: `complete`
Baseline: InternAgent
Queries: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10
Paper-exact: `false`

This is a replacement-baseline smoke run for recovered paper queries. It is not the paper's original raw InternAgent Table 1 output. The run preserves observed InternAgent/DeepSeek parsing failures as baseline behavior.

## Query Outputs

| Query | Topic | External bytes | Imported bytes |
| ---: | --- | ---: | ---: |
| 01 | Machine translation | 2505 | 2505 |
| 02 | Software engineering | 1348 | 1348 |
| 03 | LLM evaluation | 1324 | 1324 |
| 04 | Healthcare agents | 3933 | 3933 |
| 05 | Literature review automation | 1584 | 1584 |
| 06 | Speech recognition | 1202 | 1202 |
| 07 | Model efficiency | 1639 | 1639 |
| 08 | AI agents | 4444 | 4443 |
| 09 | Model deployment | 1278 | 1278 |
| 10 | Text-to-SQL | 1692 | 1692 |

## Judge Artifacts

| Artifact | Exists | Bytes | Path |
| --- | --- | ---: | --- |
| judge_input | True | 197544 | `reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_10.jsonl` |
| judge_output | True | 34120 | `reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_10_deepseek.jsonl` |
| aggregate_json | True | 1343 | `reproduction/artifacts/tables/evosci_vs_internagent_queries01_10_deepseek.json` |
| aggregate_csv | True | 265 | `reproduction/artifacts/tables/evosci_vs_internagent_queries01_10_deepseek.csv` |

## Judge Result

Judge records: 20

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 20 | 20 | 0 | 0 | 100.0 | 0.0 | 0.0 |
| Novelty | 20 | 18 | 1 | 1 | 90.0 | 5.0 | 5.0 |
| Feasibility | 20 | 20 | 0 | 0 | 100.0 | 0.0 | 0.0 |
| Relevance | 20 | 18 | 1 | 1 | 90.0 | 5.0 | 5.0 |

## Rebuild

```bash
source $HOME/.codex/env
.venv/bin/python reproduction/run_internagent_qa_baseline.py --limit 10 --max-iter 5 --resume
.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --limit 10 --min-chars 1000 --overwrite --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --limit 10 --output reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_10.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_10.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_10_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_10_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_queries01_10_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_queries01_10_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --limit 10 --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_10.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_10_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_queries01_10_deepseek.json
```
