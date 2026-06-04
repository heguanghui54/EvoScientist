# K-Dense Proxy Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report adds a 30/30 proxy replacement capture for the missing Table 1 baseline `K-Dense`, then judges EvoScientist against that proxy with Monica's Gemini-family model key `gemini-3-flash-preview`.

The output is explicitly a proxy replacement rerun. It is not the original K-Dense raw Table 1 output from the paper.

## Coverage

- Covered baseline: `K-Dense`
- Proxy answer files: `30`
- Judge input records: `60`
- Judge output records: `60`
- Records per baseline: `60` swapped-order comparisons
- Remaining missing Table 1 baselines: none

## Monica/Gemini Judge Result

Rows are from the EvoScientist target-system perspective.

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 60 | 27 | 9 | 24 | 45.00 | 15.00 | 40.00 | 5.00 |
| Novelty | 60 | 19 | 3 | 38 | 31.67 | 5.00 | 63.33 | -31.66 |
| Feasibility | 60 | 31 | 2 | 27 | 51.67 | 3.33 | 45.00 | 6.67 |
| Relevance | 60 | 9 | 42 | 9 | 15.00 | 70.00 | 15.00 | 0.00 |

Average gap: `-5.00`

## Verification Commands

```bash
.venv/bin/python reproduction/run_table1_proxy_baselines.py --provider monica --model gemini-3-flash-preview --baseline K-Dense --resume
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline K-Dense --output reproduction/artifacts/judge_inputs/evosci_vs_k_dense_proxy_monica.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/judge_inputs/evosci_vs_k_dense_proxy_monica.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_k_dense_proxy_monica.jsonl --resume --record-retries 5 --retry-sleep 8
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_k_dense_proxy_monica.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_k_dense_proxy_monica.csv --output-json reproduction/artifacts/tables/evosci_vs_k_dense_proxy_monica.json
```

## Caveats

- This is not paper-exact evidence for the original K-Dense system.
- The public K-Dense artifacts require BYOK/local runtime setup and do not provide the paper's raw Table 1 outputs.
- Monica/Gemini judging completed with internal per-record retries enabled.
