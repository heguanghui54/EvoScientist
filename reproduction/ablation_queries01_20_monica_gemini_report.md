# Ablation Queries 01-20 Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report extends the Table 3 ablation replacement rerun from 15/30 to 20/30 paper queries. The official ablation artifact root uses Monica Gemini-family judge outputs:

- `reproduction/artifacts/ablations`

The mirrored judge root is retained for transparency:

- `reproduction/artifacts/ablations_monica_gemini`

Monica's OpenAI-compatible endpoint rejects the bare paper model string `gemini-3-flash`; the working model key is `gemini-3-flash-preview`.

## Coverage

- Covered queries: `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20`
- Expected paper queries: `30`
- Coverage: `20/30` queries, or `66.67%`
- Judge provider: `monica`
- Judge model: `gemini-3-flash-preview`
- Judge records: `20` per variant, `60` total
- Failed judge records after retry: `0`

## Monica/Gemini Judge Result

Rows are from the ablation variant perspective.

| Variant | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -IDE | Clarity | 20 | 11 | 5 | 4 | 55.00 | 25.00 | 20.00 | 35.00 |
| -IDE | Novelty | 20 | 15 | 0 | 5 | 75.00 | 0.00 | 25.00 | 50.00 |
| -IDE | Feasibility | 20 | 11 | 0 | 9 | 55.00 | 0.00 | 45.00 | 10.00 |
| -IDE | Relevance | 20 | 9 | 8 | 3 | 45.00 | 40.00 | 15.00 | 30.00 |
| -IVE | Clarity | 20 | 12 | 2 | 6 | 60.00 | 10.00 | 30.00 | 30.00 |
| -IVE | Novelty | 20 | 14 | 0 | 6 | 70.00 | 0.00 | 30.00 | 40.00 |
| -IVE | Feasibility | 20 | 8 | 0 | 12 | 40.00 | 0.00 | 60.00 | -20.00 |
| -IVE | Relevance | 20 | 7 | 9 | 4 | 35.00 | 45.00 | 20.00 | 15.00 |
| -all | Clarity | 20 | 10 | 6 | 4 | 50.00 | 30.00 | 20.00 | 30.00 |
| -all | Novelty | 20 | 12 | 2 | 6 | 60.00 | 10.00 | 30.00 | 30.00 |
| -all | Feasibility | 20 | 12 | 0 | 8 | 60.00 | 0.00 | 40.00 | 20.00 |
| -all | Relevance | 20 | 3 | 13 | 4 | 15.00 | 65.00 | 20.00 | -5.00 |

## Verification

```bash
.venv/bin/python reproduction/refresh_ablation_artifacts.py --artifacts-root reproduction/artifacts/ablations --proposal-only
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --variant=-IDE --variant=-IVE --variant=-all --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict
.venv/bin/python reproduction/verify_paper_artifact_schema.py --output-json reproduction/artifacts/audit/paper_artifact_schema_latest.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all --output-json reproduction/artifacts/ablations/table3_partial_compare_to_paper.json
```

The compare-to-paper command is still expected to fail because this is only a 20-query replacement subset.
