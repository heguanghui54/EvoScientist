# AI Scientist-v2 queries01_30 Smoke Report

Date: 2026-06-04
Status: `complete`
Baseline: AI Scientist-v2
Queries: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30
Paper-exact: `false`
Accepted output min chars: 1000

This is a replacement-baseline ideation run through AI Scientist-v2. It is not the paper's original raw AI Scientist-v2 Table 1 output. Semantic Scholar access was bounded and degraded under rate limits.

## Query Outputs

| Query | Topic | External bytes | Imported bytes |
| ---: | --- | ---: | ---: |
| 01 | Machine translation | 4323 | 4324 |
| 02 | Software engineering | 5779 | 5780 |
| 03 | LLM evaluation | 6611 | 6612 |
| 04 | Healthcare agents | 5809 | 5810 |
| 05 | Literature review automation | 5219 | 5220 |
| 06 | Speech recognition | 7595 | 7595 |
| 07 | Model efficiency | 4906 | 4907 |
| 08 | AI agents | 4499 | 4500 |
| 09 | Model deployment | 5176 | 5177 |
| 10 | Text-to-SQL | 5044 | 5045 |
| 11 | LLM capabilities | 8223 | 8221 |
| 12 | Factual consistency | 4787 | 4788 |
| 13 | Data synthesis | 6487 | 6488 |
| 14 | Inference efficiency | 4425 | 4421 |
| 15 | Machine translation | 3818 | 3819 |
| 16 | Knowledge injection | 4829 | 4830 |
| 17 | Information extraction | 4468 | 4469 |
| 18 | UX evaluation | 5182 | 5183 |
| 19 | Evaluation leaderboards | 6265 | 6266 |
| 20 | Text generation | 5666 | 5667 |
| 21 | Content detection | 5339 | 5340 |
| 22 | Code LLM security | 5567 | 5565 |
| 23 | Code LLM evaluation | 4670 | 4671 |
| 24 | RAG | 4642 | 4643 |
| 25 | Multi-source reasoning | 4110 | 4111 |
| 26 | Data filtering | 6309 | 6310 |
| 27 | Long-context understanding | 5431 | 5432 |
| 28 | Alignment | 5035 | 5036 |
| 29 | Alignment | 6376 | 6377 |
| 30 | Audio foundation models | 6290 | 6291 |

## Judge Result

Judge records: 60

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 60 | 32 | 3 | 25 | 53.33 | 5.0 | 41.67 |
| Novelty | 60 | 12 | 2 | 46 | 20.0 | 3.33 | 76.67 |
| Feasibility | 60 | 31 | 4 | 25 | 51.67 | 6.67 | 41.67 |
| Relevance | 60 | 18 | 31 | 11 | 30.0 | 51.67 | 18.33 |

## Rebuild

```bash
source $HOME/.codex/env
.venv/bin/python reproduction/run_ai_scientist_v2_ideation_baseline.py --limit 30 --num-reflections 5 --resume
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'AI Scientist-v2' --source $HOME/research/AI-Scientist-v2/outputs/evoscientist_table1_queries/ai_scientist_v2 --source-format directory --output-root reproduction/artifacts/idea_outputs --limit 30 --min-chars 1000 --overwrite --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'AI Scientist-v2' --limit 30 --output reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'AI Scientist-v2' --limit 30 --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
```
