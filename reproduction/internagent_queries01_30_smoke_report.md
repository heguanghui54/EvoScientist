# InternAgent queries01_30 Smoke Report

Date: 2026-06-04
Status: `complete`
Baseline: InternAgent
Queries: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30
Paper-exact: `false`
Accepted output min chars: 500
Nominal output min chars: 1000

This is a replacement-baseline smoke run for recovered paper queries. It is not the paper's original raw InternAgent Table 1 output. The run preserves observed InternAgent/DeepSeek parsing failures as baseline behavior. Outputs below the nominal length threshold are retained and flagged, not regenerated.

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
| 11 | LLM capabilities | 1331 | 1331 |
| 12 | Factual consistency | 1583 | 1583 |
| 13 | Data synthesis | 701 | 701 |
| 14 | Inference efficiency | 1986 | 1986 |
| 15 | Machine translation | 1329 | 1329 |
| 16 | Knowledge injection | 1302 | 1301 |
| 17 | Information extraction | 1094 | 1094 |
| 18 | UX evaluation | 1459 | 1459 |
| 19 | Evaluation leaderboards | 1252 | 1252 |
| 20 | Text generation | 1327 | 1327 |
| 21 | Content detection | 2091 | 2091 |
| 22 | Code LLM security | 1342 | 1342 |
| 23 | Code LLM evaluation | 1927 | 1927 |
| 24 | RAG | 1535 | 1535 |
| 25 | Multi-source reasoning | 1090 | 1090 |
| 26 | Data filtering | 1959 | 1959 |
| 27 | Long-context understanding | 1950 | 1950 |
| 28 | Alignment | 2057 | 2057 |
| 29 | Alignment | 737 | 737 |
| 30 | Audio foundation models | 1363 | 1363 |

Outputs below the nominal threshold:

| Query | External bytes | Imported bytes | Threshold |
| ---: | ---: | ---: | ---: |
| 13 | 701 | 701 | 1000 |
| 29 | 737 | 737 | 1000 |

## Judge Artifacts

| Artifact | Exists | Bytes | Path |
| --- | --- | ---: | --- |
| judge_input | True | 529124 | `reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_30.jsonl` |
| judge_output | True | 103914 | `reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_30_deepseek.jsonl` |
| aggregate_json | True | 1353 | `reproduction/artifacts/tables/evosci_vs_internagent_queries01_30_deepseek.json` |
| aggregate_csv | True | 274 | `reproduction/artifacts/tables/evosci_vs_internagent_queries01_30_deepseek.csv` |

## Judge Result

Judge records: 60

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 60 | 59 | 1 | 0 | 98.33 | 1.67 | 0.0 |
| Novelty | 60 | 56 | 1 | 3 | 93.33 | 1.67 | 5.0 |
| Feasibility | 60 | 58 | 1 | 1 | 96.67 | 1.67 | 1.67 |
| Relevance | 60 | 52 | 7 | 1 | 86.67 | 11.67 | 1.67 |

## Rebuild

```bash
source $HOME/.codex/env
.venv/bin/python reproduction/run_internagent_qa_baseline.py --limit 30 --max-iter 5 --resume
.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --limit 30 --min-chars 500 --overwrite --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --limit 30 --output reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_30.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_30.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_30_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_30_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_queries01_30_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_queries01_30_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --limit 30 --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent_queries01_30.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_queries01_30_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_queries01_30_deepseek.json
```
