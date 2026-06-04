# Ablation Queries 01-03 Partial Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This is a formal-artifact partial rerun for Table 3 ablations under `reproduction/artifacts/ablations`. It covers queries 1-3 for all three variants: `-IDE`, `-IVE`, and `-all`. Each variant was generated with `run_ablation_variants.py`, judged against the existing EvoScientist answers with DeepSeek, and aggregated from the ablation-variant perspective.

This does not complete the paper's Table 3 reproduction. The paper-level gate now checks 30-query coverage, so this 3-query subset remains incomplete by design.

## Coverage

- Artifact root: `reproduction/artifacts/ablations`
- Covered queries: `1, 2, 3`
- Expected paper queries: `30`
- Coverage: `3/30` queries, or `10.0%`
- Judge: `deepseek-v4-flash`
- Judge records: `3` per variant, `9` total
- Failed judge records: `0`

## DeepSeek Judge Result

Rows are from the ablation variant perspective.

| Variant | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -IDE | Clarity | 3 | 3 | 0 | 0 | 100.00 | 0.00 | 0.00 | 100.00 |
| -IDE | Novelty | 3 | 2 | 0 | 1 | 66.67 | 0.00 | 33.33 | 33.34 |
| -IDE | Feasibility | 3 | 1 | 0 | 2 | 33.33 | 0.00 | 66.67 | -33.34 |
| -IDE | Relevance | 3 | 0 | 3 | 0 | 0.00 | 100.00 | 0.00 | 0.00 |
| -IVE | Clarity | 3 | 2 | 0 | 1 | 66.67 | 0.00 | 33.33 | 33.34 |
| -IVE | Novelty | 3 | 2 | 1 | 0 | 66.67 | 33.33 | 0.00 | 66.67 |
| -IVE | Feasibility | 3 | 2 | 0 | 1 | 66.67 | 0.00 | 33.33 | 33.34 |
| -IVE | Relevance | 3 | 1 | 2 | 0 | 33.33 | 66.67 | 0.00 | 33.33 |
| -all | Clarity | 3 | 3 | 0 | 0 | 100.00 | 0.00 | 0.00 | 100.00 |
| -all | Novelty | 3 | 2 | 0 | 1 | 66.67 | 0.00 | 33.33 | 33.34 |
| -all | Feasibility | 3 | 0 | 0 | 3 | 0.00 | 0.00 | 100.00 | -100.00 |
| -all | Relevance | 3 | 0 | 3 | 0 | 0.00 | 100.00 | 0.00 | 0.00 |

## Verification

```bash
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --variant=-IDE --variant=-IVE --variant=-all --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict
.venv/bin/python reproduction/verify_paper_artifact_schema.py --output-json reproduction/artifacts/audit/paper_artifact_schema_latest.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all --output-json reproduction/artifacts/ablations/table3_partial_compare_to_paper.json
.venv/bin/python reproduction/audit_paper_level_completion.py
```

The compare-to-paper command is expected to fail for this partial artifact because it is a 3-query replacement subset judged by DeepSeek, while the paper reports a 30-query Gemini-3-flash Table 3 ablation.
