# Table 1 Existing Baselines Monica/Gemini Judge Report

Date: 2026-06-04
Status: `partial`
Paper-exact: `false`

This report reruns the Table 1 judge for the two baselines that already have 30/30 replacement outputs in the checkout: `AI Scientist-v2` and `InternAgent`.

It uses Monica's Gemini-family judge model key `gemini-3-flash-preview`. The paper model name is `gemini-3-flash`, but Monica rejects that bare key in this environment.

## Coverage

- Covered baselines: `AI Scientist-v2`, `InternAgent`
- Missing paper baselines: `Virtual Scientist`, `AI-Researcher`, `Hypogenic`, `Novix`, `K-Dense`
- Judge input records: `120`
- Judge output records: `120`
- Records per baseline: `60` swapped-order comparisons

## Monica/Gemini Judge Result

Rows are from the EvoScientist target-system perspective.

| Baseline | Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % | Gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AI Scientist-v2 | Clarity | 60 | 37 | 6 | 17 | 61.67 | 10.00 | 28.33 | 33.34 |
| AI Scientist-v2 | Novelty | 60 | 11 | 3 | 46 | 18.33 | 5.00 | 76.67 | -58.34 |
| AI Scientist-v2 | Feasibility | 60 | 34 | 1 | 25 | 56.67 | 1.67 | 41.67 | 15.00 |
| AI Scientist-v2 | Relevance | 60 | 15 | 35 | 10 | 25.00 | 58.33 | 16.67 | 8.33 |
| InternAgent | Clarity | 60 | 57 | 0 | 3 | 95.00 | 0.00 | 5.00 | 90.00 |
| InternAgent | Novelty | 60 | 52 | 0 | 8 | 86.67 | 0.00 | 13.33 | 73.34 |
| InternAgent | Feasibility | 60 | 56 | 0 | 4 | 93.33 | 0.00 | 6.67 | 86.66 |
| InternAgent | Relevance | 60 | 46 | 12 | 2 | 76.67 | 20.00 | 3.33 | 73.34 |

## Verification

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --baseline 'AI Scientist-v2' --output reproduction/artifacts/judge_inputs/table1_existing_baselines_monica.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider monica --model gemini-3-flash-preview --input reproduction/artifacts/judge_inputs/table1_existing_baselines_monica.jsonl --output reproduction/artifacts/judge_outputs/table1_existing_baselines_monica.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/table1_existing_baselines_monica.jsonl --output-csv reproduction/artifacts/tables/table1_existing_baselines_monica.csv --output-json reproduction/artifacts/tables/table1_existing_baselines_monica.json
```

This remains a partial replacement result because five Table 1 paper baselines still lack public raw outputs or completed replacement captures.
