# Virtual Scientist Proxy Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report adds a 30/30 proxy replacement capture for the missing Table 1 baseline `Virtual Scientist`, then judges EvoScientist against that proxy with Monica's Gemini-family model key `gemini-3-flash-preview`.

The output is explicitly a proxy replacement rerun. It is not the original Virtual Scientist raw Table 1 output from the paper.

## Coverage

- Covered baseline: `Virtual Scientist`
- Proxy answer files: `30`
- Judge input records: `60`
- Judge output records: `60`
- Records per baseline: `60` swapped-order comparisons
- Remaining missing Table 1 baselines: `AI-Researcher`, `Hypogenic`, `Novix`, `K-Dense`

## Monica/Gemini Judge Result

Rows are from the EvoScientist target-system perspective.

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 60 | 26 | 12 | 22 | 43.33 | 20.00 | 36.67 | 6.66 |
| Novelty | 60 | 23 | 5 | 32 | 38.33 | 8.33 | 53.33 | -15.00 |
| Feasibility | 60 | 28 | 2 | 30 | 46.67 | 3.33 | 50.00 | -3.33 |
| Relevance | 60 | 8 | 39 | 13 | 13.33 | 65.00 | 21.67 | -8.34 |

Average gap: `-5.00`

## Verification Commands

```bash
.venv/bin/python reproduction/run_table1_proxy_baselines.py --provider monica --model gemini-3-flash-preview --baseline 'Virtual Scientist' --resume
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --output reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist_proxy_monica.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist_proxy_monica.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_proxy_monica.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_proxy_monica.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_virtual_scientist_proxy_monica.csv --output-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_proxy_monica.json
```

## Caveats

- This is not paper-exact evidence for the original Virtual Scientist system.
- The public Virtual Scientist checkout lacks the paper's raw Table 1 outputs and a drop-in 30-query runner.
- During judging, Monica/Gemini produced transient timeout and non-JSON failures; resume retries completed all 60 valid records.
