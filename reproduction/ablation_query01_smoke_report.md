# Query-01 Ablation Smoke Report

Date: 2026-06-04
Status: `complete`
Paper-exact: `false`

This is a one-query replacement ablation smoke test for all three Table 3 variants: `-IDE`, `-IVE`, and `-all`. Each variant was generated with `run_ablation_variants.py`, judged against the existing EvoScientist query-01 answer with DeepSeek, and aggregated from the ablation-variant perspective. This is not the paper's full Table 3 reproduction because the public checkout does not expose native IDE/IVE ablation switches.

## Artifacts

- Root: `reproduction/artifacts/ablation_smoke`
- Combined aggregate: `reproduction/artifacts/ablation_smoke/combined_aggregate.json`
- Per-variant manifests: `reproduction/artifacts/ablation_smoke/{variant}/system_outputs_complete.json`
- Per-variant judge outputs: `reproduction/artifacts/ablation_smoke/{variant}/judge_outputs.jsonl`

## DeepSeek Judge Result

Rows are from the ablation variant perspective.

| Variant | Dimension | N | Win | Tie | Lose | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| -IDE | Clarity | 1 | 1 | 0 | 0 | 100.0 |
| -IDE | Novelty | 1 | 1 | 0 | 0 | 100.0 |
| -IDE | Feasibility | 1 | 0 | 0 | 1 | -100.0 |
| -IDE | Relevance | 1 | 0 | 1 | 0 | 0.0 |
| -IVE | Clarity | 1 | 1 | 0 | 0 | 100.0 |
| -IVE | Novelty | 1 | 1 | 0 | 0 | 100.0 |
| -IVE | Feasibility | 1 | 0 | 0 | 1 | -100.0 |
| -IVE | Relevance | 1 | 1 | 0 | 0 | 100.0 |
| -all | Clarity | 1 | 1 | 0 | 0 | 100.0 |
| -all | Novelty | 1 | 0 | 0 | 1 | -100.0 |
| -all | Feasibility | 1 | 1 | 0 | 0 | 100.0 |
| -all | Relevance | 1 | 0 | 1 | 0 | 0.0 |

## Commands

```bash
set -a; source ~/.codex/env; set +a
.venv/bin/python reproduction/run_ablation_variants.py --variant=-IDE --query-id 1 --proposal-only --timeout 600 --output-root reproduction/artifacts/ablation_smoke
.venv/bin/python reproduction/run_ablation_variants.py --variant=-IVE --query-id 1 --proposal-only --timeout 600 --output-root reproduction/artifacts/ablation_smoke
.venv/bin/python reproduction/run_ablation_variants.py --variant=-all --query-id 1 --proposal-only --timeout 600 --output-root reproduction/artifacts/ablation_smoke
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/ablation_smoke/-IDE/judge_inputs.jsonl --output reproduction/artifacts/ablation_smoke/-IDE/judge_outputs.jsonl --resume
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/ablation_smoke/-IVE/judge_inputs.jsonl --output reproduction/artifacts/ablation_smoke/-IVE/judge_outputs.jsonl --resume
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/ablation_smoke/-all/judge_inputs.jsonl --output reproduction/artifacts/ablation_smoke/-all/judge_outputs.jsonl --resume
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablation_smoke --variant=-IDE --variant=-IVE --variant=-all --combined-json reproduction/artifacts/ablation_smoke/combined_aggregate.json --combined-csv reproduction/artifacts/ablation_smoke/combined_aggregate.csv --strict
```
