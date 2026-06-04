# Ablation Queries 01-03 Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report re-judges the formal queries 01-03 Table 3 ablation subset with Monica's Gemini-family model. Monica's OpenAI-compatible endpoint rejects the bare paper name `gemini-3-flash`; the working documented model key is `gemini-3-flash-preview`.

The generated ablation outputs are the same 3-query replacement outputs under `reproduction/artifacts/ablations`. This report keeps the Monica/Gemini judge artifacts in a separate root:

- `reproduction/artifacts/ablations_monica_gemini`

## Coverage

- Covered queries: `1, 2, 3`
- Expected paper queries: `30`
- Coverage: `3/30` queries, or `10.0%`
- Judge provider: `monica`
- Judge model: `gemini-3-flash-preview`
- Judge records: `3` per variant, `9` total
- Failed judge records: `0`

## Monica/Gemini Judge Result

Rows are from the ablation variant perspective.

| Variant | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -IDE | Clarity | 3 | 1 | 1 | 1 | 33.33 | 33.33 | 33.33 | 0.00 |
| -IDE | Novelty | 3 | 2 | 0 | 1 | 66.67 | 0.00 | 33.33 | 33.34 |
| -IDE | Feasibility | 3 | 1 | 0 | 2 | 33.33 | 0.00 | 66.67 | -33.34 |
| -IDE | Relevance | 3 | 1 | 2 | 0 | 33.33 | 66.67 | 0.00 | 33.33 |
| -IVE | Clarity | 3 | 1 | 0 | 2 | 33.33 | 0.00 | 66.67 | -33.34 |
| -IVE | Novelty | 3 | 1 | 0 | 2 | 33.33 | 0.00 | 66.67 | -33.34 |
| -IVE | Feasibility | 3 | 0 | 0 | 3 | 0.00 | 0.00 | 100.00 | -100.00 |
| -IVE | Relevance | 3 | 0 | 1 | 2 | 0.00 | 33.33 | 66.67 | -66.67 |
| -all | Clarity | 3 | 1 | 2 | 0 | 33.33 | 66.67 | 0.00 | 33.33 |
| -all | Novelty | 3 | 2 | 0 | 1 | 66.67 | 0.00 | 33.33 | 33.34 |
| -all | Feasibility | 3 | 1 | 0 | 2 | 33.33 | 0.00 | 66.67 | -33.34 |
| -all | Relevance | 3 | 0 | 3 | 0 | 0.00 | 100.00 | 0.00 | 0.00 |

## Verification

```bash
set -a; source ~/.codex/env; set +a
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/ablations_monica_gemini/-IDE/judge_inputs.jsonl --output reproduction/artifacts/ablations_monica_gemini/-IDE/judge_outputs.jsonl --resume
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/ablations_monica_gemini/-IVE/judge_inputs.jsonl --output reproduction/artifacts/ablations_monica_gemini/-IVE/judge_outputs.jsonl --resume
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/ablations_monica_gemini/-all/judge_inputs.jsonl --output reproduction/artifacts/ablations_monica_gemini/-all/judge_outputs.jsonl --resume
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations_monica_gemini --variant=-IDE --variant=-IVE --variant=-all --combined-json reproduction/artifacts/ablations_monica_gemini/combined_aggregate.json --combined-csv reproduction/artifacts/ablations_monica_gemini/combined_aggregate.csv --strict
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations_monica_gemini/combined_aggregate.json --section table3_ablation_idea_generation --require-all --output-json reproduction/artifacts/ablations_monica_gemini/table3_partial_compare_to_paper.json
```

The compare-to-paper command is still expected to fail because this is only a 3-query replacement subset, even though the judge is now Gemini-family through Monica.
