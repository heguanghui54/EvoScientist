# Ablation Queries 01-10 Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report extends the Table 3 ablation replacement rerun from 3/30 to 10/30 paper queries. The official ablation artifact root now uses Monica's Gemini-family judge outputs:

- `reproduction/artifacts/ablations`

The mirrored judge root is retained for transparency:

- `reproduction/artifacts/ablations_monica_gemini`

Monica's OpenAI-compatible endpoint rejects the bare paper model string `gemini-3-flash`; the working model key is `gemini-3-flash-preview`.

## Coverage

- Covered queries: `1, 2, 3, 4, 5, 6, 7, 8, 9, 10`
- Expected paper queries: `30`
- Coverage: `10/30` queries, or `33.33%`
- Judge provider: `monica`
- Judge model: `gemini-3-flash-preview`
- Judge records: `10` per variant, `30` total
- Failed judge records after retry: `0`

## Monica/Gemini Judge Result

Rows are from the ablation variant perspective.

| Variant | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -IDE | Clarity | 10 | 5 | 4 | 1 | 50.00 | 40.00 | 10.00 | 40.00 |
| -IDE | Novelty | 10 | 7 | 0 | 3 | 70.00 | 0.00 | 30.00 | 40.00 |
| -IDE | Feasibility | 10 | 6 | 0 | 4 | 60.00 | 0.00 | 40.00 | 20.00 |
| -IDE | Relevance | 10 | 4 | 6 | 0 | 40.00 | 60.00 | 0.00 | 40.00 |
| -IVE | Clarity | 10 | 5 | 1 | 4 | 50.00 | 10.00 | 40.00 | 10.00 |
| -IVE | Novelty | 10 | 7 | 0 | 3 | 70.00 | 0.00 | 30.00 | 40.00 |
| -IVE | Feasibility | 10 | 3 | 0 | 7 | 30.00 | 0.00 | 70.00 | -40.00 |
| -IVE | Relevance | 10 | 3 | 4 | 3 | 30.00 | 40.00 | 30.00 | 0.00 |
| -all | Clarity | 10 | 4 | 4 | 2 | 40.00 | 40.00 | 20.00 | 20.00 |
| -all | Novelty | 10 | 7 | 0 | 3 | 70.00 | 0.00 | 30.00 | 40.00 |
| -all | Feasibility | 10 | 5 | 0 | 5 | 50.00 | 0.00 | 50.00 | 0.00 |
| -all | Relevance | 10 | 2 | 6 | 2 | 20.00 | 60.00 | 20.00 | 0.00 |

## Verification

```bash
.venv/bin/python reproduction/refresh_ablation_artifacts.py --artifacts-root reproduction/artifacts/ablations --proposal-only
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --variant=-IDE --variant=-IVE --variant=-all --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict
.venv/bin/python reproduction/verify_paper_artifact_schema.py --output-json reproduction/artifacts/audit/paper_artifact_schema_latest.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all --output-json reproduction/artifacts/ablations/table3_partial_compare_to_paper.json
```

The compare-to-paper command is still expected to fail because this is only a 10-query replacement subset.
