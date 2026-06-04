# Ablation Queries 01-30 Monica/Gemini Judge Report

Date: 2026-06-04
Status: `complete` for the replacement ablation rerun
Paper-exact: `false`

This report completes the Table 3 replacement ablation rerun across all 30 paper queries. The official ablation artifact root uses Monica Gemini-family judge outputs:

- `reproduction/artifacts/ablations`

The mirrored judge root is retained for transparency:

- `reproduction/artifacts/ablations_monica_gemini`

This remains a replacement rerun, not a paper-exact reproduction: the public checkout does not expose the authors native IDE/IVE ablation switches, and the aggregate values do not match the paper Table 3 targets.

Monica's OpenAI-compatible endpoint rejects the bare paper model string `gemini-3-flash`; the working model key is `gemini-3-flash-preview`.

## Coverage

- Covered queries: `1-30`
- Expected paper queries: `30`
- Coverage: `30/30` queries, or `100.0%`
- Judge provider: `monica`
- Judge model: `gemini-3-flash-preview`
- Judge records: `30` per variant, `90` total
- Failed judge records after retry: `0`

## Monica/Gemini Judge Result

Rows are from the ablation variant perspective.

| Variant | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -IDE | Clarity | 30 | 17 | 6 | 7 | 56.67 | 20.00 | 23.33 | 33.34 |
| -IDE | Novelty | 30 | 21 | 1 | 8 | 70.00 | 3.33 | 26.67 | 43.33 |
| -IDE | Feasibility | 30 | 16 | 0 | 14 | 53.33 | 0.00 | 46.67 | 6.66 |
| -IDE | Relevance | 30 | 10 | 16 | 4 | 33.33 | 53.33 | 13.33 | 20.00 |
| -IVE | Clarity | 30 | 19 | 4 | 7 | 63.33 | 13.33 | 23.33 | 40.00 |
| -IVE | Novelty | 30 | 19 | 1 | 10 | 63.33 | 3.33 | 33.33 | 30.00 |
| -IVE | Feasibility | 30 | 13 | 0 | 17 | 43.33 | 0.00 | 56.67 | -13.34 |
| -IVE | Relevance | 30 | 10 | 15 | 5 | 33.33 | 50.00 | 16.67 | 16.66 |
| -all | Clarity | 30 | 14 | 8 | 8 | 46.67 | 26.67 | 26.67 | 20.00 |
| -all | Novelty | 30 | 19 | 3 | 8 | 63.33 | 10.00 | 26.67 | 36.66 |
| -all | Feasibility | 30 | 14 | 1 | 15 | 46.67 | 3.33 | 50.00 | -3.33 |
| -all | Relevance | 30 | 4 | 20 | 6 | 13.33 | 66.67 | 20.00 | -6.67 |

## Verification

```bash
.venv/bin/python reproduction/refresh_ablation_artifacts.py --artifacts-root reproduction/artifacts/ablations --proposal-only
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --variant=-IDE --variant=-IVE --variant=-all --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict
.venv/bin/python reproduction/verify_paper_artifact_schema.py --output-json reproduction/artifacts/audit/paper_artifact_schema_latest.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all --output-json reproduction/artifacts/ablations/table3_partial_compare_to_paper.json
```

The compare-to-paper command is still expected to fail because this is a full replacement rerun, not an author-native ablation reproduction.
