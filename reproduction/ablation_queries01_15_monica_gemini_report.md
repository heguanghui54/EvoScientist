# Ablation Queries 01-15 Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report extends the Table 3 ablation replacement rerun from 10/30 to 15/30 paper queries. The official ablation artifact root uses Monica's Gemini-family judge outputs:

- `reproduction/artifacts/ablations`

The mirrored judge root is retained for transparency:

- `reproduction/artifacts/ablations_monica_gemini`

Monica's OpenAI-compatible endpoint rejects the bare paper model string `gemini-3-flash`; the working model key is `gemini-3-flash-preview`.

## Coverage

- Covered queries: `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15`
- Expected paper queries: `30`
- Coverage: `15/30` queries, or `50.0%`
- Judge provider: `monica`
- Judge model: `gemini-3-flash-preview`
- Judge records: `15` per variant, `45` total
- Failed judge records after retry: `0`

## Monica/Gemini Judge Result

Rows are from the ablation variant perspective.

| Variant | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -IDE | Clarity | 15 | 8 | 4 | 3 | 53.33 | 26.67 | 20.00 | 33.33 |
| -IDE | Novelty | 15 | 11 | 0 | 4 | 73.33 | 0.00 | 26.67 | 46.66 |
| -IDE | Feasibility | 15 | 8 | 0 | 7 | 53.33 | 0.00 | 46.67 | 6.66 |
| -IDE | Relevance | 15 | 6 | 8 | 1 | 40.00 | 53.33 | 6.67 | 33.33 |
| -IVE | Clarity | 15 | 8 | 1 | 6 | 53.33 | 6.67 | 40.00 | 13.33 |
| -IVE | Novelty | 15 | 10 | 0 | 5 | 66.67 | 0.00 | 33.33 | 33.34 |
| -IVE | Feasibility | 15 | 5 | 0 | 10 | 33.33 | 0.00 | 66.67 | -33.34 |
| -IVE | Relevance | 15 | 4 | 7 | 4 | 26.67 | 46.67 | 26.67 | 0.00 |
| -all | Clarity | 15 | 7 | 5 | 3 | 46.67 | 33.33 | 20.00 | 26.67 |
| -all | Novelty | 15 | 11 | 0 | 4 | 73.33 | 0.00 | 26.67 | 46.66 |
| -all | Feasibility | 15 | 7 | 0 | 8 | 46.67 | 0.00 | 53.33 | -6.66 |
| -all | Relevance | 15 | 3 | 9 | 3 | 20.00 | 60.00 | 20.00 | 0.00 |

## Verification

```bash
.venv/bin/python reproduction/refresh_ablation_artifacts.py --artifacts-root reproduction/artifacts/ablations --proposal-only
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --variant=-IDE --variant=-IVE --variant=-all --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict
.venv/bin/python reproduction/verify_paper_artifact_schema.py --output-json reproduction/artifacts/audit/paper_artifact_schema_latest.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all --output-json reproduction/artifacts/ablations/table3_partial_compare_to_paper.json
```

The compare-to-paper command is still expected to fail because this is only a 15-query replacement subset.
