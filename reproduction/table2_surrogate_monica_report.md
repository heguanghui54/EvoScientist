# Table 2 Monica/Gemini Surrogate Evaluation Report

Date: 2026-06-04
Status: `complete`
Paper-exact: `false`

This report prepares the Table 2 comparison inputs and aggregates
Monica/Gemini-derived surrogate labels. It does not replace the paper's
three PhD-level human annotators.

## Coverage

- Inputs: 120
- Surrogate labels: 1440
- Baselines: InternAgent, AI Scientist-v2, Novix, K-Dense
- Surrogate annotators: monica_gemini_forward_surrogate, monica_gemini_reverse_surrogate, monica_gemini_mean_surrogate

## Aggregate

| Baseline | Clarity gap | Novelty gap | Feasibility gap | Relevance gap | Avg gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| InternAgent | 91.12 | 73.34 | 87.77 | 75.56 | 81.95 |
| AI Scientist-v2 | 35.55 | -57.78 | 16.67 | 11.11 | 1.39 |
| Novix | 11.11 | -2.22 | -4.45 | -5.56 | -0.28 |
| K-Dense | 4.44 | -32.22 | 6.67 | 0.0 | -5.28 |

## Artifacts

- Human-eval inputs: `artifacts/human_evaluation/inputs.jsonl`
- Surrogate labels: `artifacts/human_evaluation/surrogate_labels.jsonl`
- Surrogate aggregate JSON: `artifacts/human_evaluation/surrogate_aggregate.json`
- Surrogate aggregate CSV: `artifacts/human_evaluation/surrogate_aggregate.csv`

## Caveats

- This is an LLM-surrogate Table 2 evaluation, not the paper's human evaluation.
- No `labels.jsonl` or `aggregate.json` human-label artifact is written by this script.
- The paper-level audit should remain incomplete until real human labels are imported.
