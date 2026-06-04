# Novix Proxy Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report adds a 30/30 proxy replacement capture for the missing Table 1 baseline `Novix`, then judges EvoScientist against that proxy with Monica's Gemini-family model key `gemini-3-flash-preview`.

The output is explicitly a proxy replacement rerun. It is not the original Novix raw Table 1 output from the paper.

## Coverage

- Covered baseline: `Novix`
- Proxy answer files: `30`
- Judge input records: `60`
- Judge output records: `60`
- Records per baseline: `60` swapped-order comparisons
- Remaining missing Table 1 baseline: `K-Dense`

## Monica/Gemini Judge Result

Rows are from the EvoScientist target-system perspective.

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 60 | 29 | 7 | 24 | 48.33 | 11.67 | 40.00 | 8.33 |
| Novelty | 60 | 27 | 4 | 29 | 45.00 | 6.67 | 48.33 | -3.33 |
| Feasibility | 60 | 27 | 4 | 29 | 45.00 | 6.67 | 48.33 | -3.33 |
| Relevance | 60 | 11 | 35 | 14 | 18.33 | 58.33 | 23.33 | -5.00 |

Average gap: `-0.83`

## Verification Commands

```bash
.venv/bin/python reproduction/run_table1_proxy_baselines.py --provider monica --model gemini-3-flash-preview --baseline Novix --resume
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline Novix --output reproduction/artifacts/judge_inputs/evosci_vs_novix_proxy_monica.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/judge_inputs/evosci_vs_novix_proxy_monica.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_novix_proxy_monica.jsonl --resume --record-retries 5 --retry-sleep 8
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_novix_proxy_monica.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_novix_proxy_monica.csv --output-json reproduction/artifacts/tables/evosci_vs_novix_proxy_monica.json
```

## Caveats

- This is not paper-exact evidence for the original Novix system.
- The public Novix artifacts do not provide the paper's raw Table 1 outputs or a public batch runner.
- Monica/Gemini judging completed with internal per-record retries enabled.
