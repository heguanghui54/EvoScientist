# AI-Researcher Proxy Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report adds a 30/30 proxy replacement capture for the missing Table 1 baseline `AI-Researcher`, then judges EvoScientist against that proxy with Monica's Gemini-family model key `gemini-3-flash-preview`.

The output is explicitly a proxy replacement rerun. It is not the original AI-Researcher raw Table 1 output from the paper.

## Coverage

- Covered baseline: `AI-Researcher`
- Proxy answer files: `30`
- Judge input records: `60`
- Judge output records: `60`
- Records per baseline: `60` swapped-order comparisons
- Remaining missing Table 1 baselines: `Hypogenic`, `Novix`, `K-Dense`

## Monica/Gemini Judge Result

Rows are from the EvoScientist target-system perspective.

| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Clarity | 60 | 29 | 7 | 24 | 48.33 | 11.67 | 40.00 | 8.33 |
| Novelty | 60 | 37 | 4 | 19 | 61.67 | 6.67 | 31.67 | 30.00 |
| Feasibility | 60 | 23 | 1 | 36 | 38.33 | 1.67 | 60.00 | -21.67 |
| Relevance | 60 | 7 | 42 | 11 | 11.67 | 70.00 | 18.33 | -6.66 |

Average gap: `2.50`

## Verification Commands

```bash
.venv/bin/python reproduction/run_table1_proxy_baselines.py --provider monica --model gemini-3-flash-preview --baseline AI-Researcher --resume
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline AI-Researcher --output reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher_proxy_monica.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher_proxy_monica.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_proxy_monica.jsonl --resume --record-retries 5 --retry-sleep 8
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_proxy_monica.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_researcher_proxy_monica.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_researcher_proxy_monica.json
```

## Caveats

- This is not paper-exact evidence for the original AI-Researcher system.
- The public AI-Researcher checkout is not a drop-in 30-query EvoScientist Table 1 runner.
- During judging, Monica/Gemini produced transient timeout and SSL failures; internal retries plus resume completed all 60 valid records.
