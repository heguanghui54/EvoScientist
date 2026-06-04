# Hypogenic Proxy Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report adds a 30/30 proxy replacement capture for the missing Table 1 baseline `Hypogenic`, then judges EvoScientist against that proxy with Monica's Gemini-family model key `gemini-3-flash-preview`.

The output is explicitly a proxy replacement rerun. It is not the original Hypogenic raw Table 1 output from the paper.

## Coverage

- Covered baseline: `Hypogenic`
- Proxy answer files: `30`
- Judge input records: `60`
- Judge output records: `60`
- Records per baseline: `60` swapped-order comparisons
- Remaining missing Table 1 baselines: `Novix`, `K-Dense`

## Monica/Gemini Judge Result

Rows are from the EvoScientist target-system perspective.

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 60 | 29 | 9 | 22 | 48.33 | 15.00 | 36.67 | 11.66 |
| Novelty | 60 | 9 | 1 | 50 | 15.00 | 1.67 | 83.33 | -68.33 |
| Feasibility | 60 | 33 | 1 | 26 | 55.00 | 1.67 | 43.33 | 11.67 |
| Relevance | 60 | 9 | 41 | 10 | 15.00 | 68.33 | 16.67 | -1.67 |

Average gap: `-11.67`

## Verification Commands

```bash
.venv/bin/python reproduction/run_table1_proxy_baselines.py --provider monica --model gemini-3-flash-preview --baseline Hypogenic --resume
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline Hypogenic --output reproduction/artifacts/judge_inputs/evosci_vs_hypogenic_proxy_monica.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/judge_inputs/evosci_vs_hypogenic_proxy_monica.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_proxy_monica.jsonl --resume --record-retries 5 --retry-sleep 8
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_proxy_monica.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_hypogenic_proxy_monica.csv --output-json reproduction/artifacts/tables/evosci_vs_hypogenic_proxy_monica.json
```

## Caveats

- This is not paper-exact evidence for the original Hypogenic system.
- The public Hypogenic artifacts do not provide the paper's raw Table 1 outputs or a public batch runner.
- Monica/Gemini judging completed with internal per-record retries enabled.
