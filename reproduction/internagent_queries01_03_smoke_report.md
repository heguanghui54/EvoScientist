# InternAgent queries01_03 Smoke Report

Date: 2026-06-04
Status: `complete`
Baseline: InternAgent
Queries: 01, 02, 03
Paper-exact: `false`

This is a replacement-baseline smoke run for recovered paper queries. It is not the paper's original raw InternAgent Table 1 output. The run preserves observed InternAgent/DeepSeek parsing failures as baseline behavior.

## Query Outputs

| Query | Topic | External bytes | Imported bytes |
| ---: | --- | ---: | ---: |
| 01 | Machine translation | 2505 | 2505 |
| 02 | Software engineering | 1348 | 1348 |
| 03 | LLM evaluation | 1324 | 1324 |

## Judge Artifacts

| Artifact | Exists | Bytes | Path |
| --- | --- | ---: | --- |
| judge_input | True | 67448 | `reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_03.jsonl` |
| judge_output | True | 11533 | `reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_03_deepseek.jsonl` |
| aggregate_json | True | 1342 | `reproduction/artifacts/tables/evosci_vs_internagent_queries01_03_deepseek.json` |
| aggregate_csv | True | 270 | `reproduction/artifacts/tables/evosci_vs_internagent_queries01_03_deepseek.csv` |

## Judge Result

Judge records: 6

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 6 | 6 | 0 | 0 | 100.0 | 0.0 | 0.0 |
| Novelty | 6 | 6 | 0 | 0 | 100.0 | 0.0 | 0.0 |
| Feasibility | 6 | 5 | 0 | 1 | 83.33 | 0.0 | 16.67 |
| Relevance | 6 | 5 | 1 | 0 | 83.33 | 16.67 | 0.0 |

## Rebuild

```bash
source $HOME/.codex/env
.venv/bin/python reproduction/run_internagent_qa_baseline.py --limit 3 --max-iter 5 --resume
.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --limit 3 --min-chars 1000 --overwrite --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --limit 3 --output reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_03.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_03.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_03_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_03_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_queries01_03_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_queries01_03_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --limit 3 --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_03.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_03_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_queries01_03_deepseek.json
```
