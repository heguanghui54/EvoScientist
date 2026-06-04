# -IDE Query-01 Ablation Smoke Report

Date: 2026-06-04
Status: `complete`
Paper-exact: `false`

This is a one-query replacement ablation smoke test for Table 3. It uses `run_ablation_variants.py` with `--variant=-IDE --query-id 1 --proposal-only`, then judges `-IDE` against the existing EvoScientist query-01 answer with DeepSeek. It is not the paper's full Table 3 reproduction because the public checkout does not expose the native IDE/IVE ablation switches.

## Artifacts

- Variant manifest: `reproduction/artifacts/ablation_smoke/-IDE/system_outputs_complete.json`
- Variant answer: `reproduction/artifacts/ablation_smoke/-IDE/system_outputs/-IDE/query_01/answer.txt`
- Reference answer: `reproduction/artifacts/ablation_smoke/-IDE/system_outputs/EvoScientist/query_01/answer.txt`
- Judge inputs: `reproduction/artifacts/ablation_smoke/-IDE/judge_inputs.jsonl`
- Judge outputs: `reproduction/artifacts/ablation_smoke/-IDE/judge_outputs.jsonl`
- Aggregate: `reproduction/artifacts/ablation_smoke/-IDE/aggregate.json`

## DeepSeek Judge Result

Rows are from the ablation variant perspective.

| Dimension | N | Win | Tie | Lose | Gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Clarity | 1 | 1 | 0 | 0 | 100.0 |
| Novelty | 1 | 1 | 0 | 0 | 100.0 |
| Feasibility | 1 | 0 | 0 | 1 | -100.0 |
| Relevance | 1 | 0 | 1 | 0 | 0.0 |

## Commands

```bash
set -a; source ~/.codex/env; set +a
.venv/bin/python reproduction/run_ablation_variants.py --variant=-IDE --query-id 1 --proposal-only --timeout 600 --output-root reproduction/artifacts/ablation_smoke
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/ablation_smoke/-IDE/judge_inputs.jsonl --output reproduction/artifacts/ablation_smoke/-IDE/judge_outputs.jsonl --resume
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablation_smoke --variant=-IDE --combined-json reproduction/artifacts/ablation_smoke/combined_aggregate.json --combined-csv reproduction/artifacts/ablation_smoke/combined_aggregate.csv --strict
```
