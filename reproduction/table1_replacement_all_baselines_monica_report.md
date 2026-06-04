# Table 1 Replacement All-Baselines Monica/Gemini Judge Report

Date: 2026-06-04
Status: `complete`
Paper-exact: `false`
Completion scope: `replacement_table1_all_baselines`

This is a full seven-baseline replacement/proxy Table 1 summary. It covers
30 recovered queries x 7 baselines x 2 swapped orders = 420 pairwise judge
records, but it is not the paper's original raw baseline-output package.

## Aggregate

| Baseline | Clarity gap | Novelty gap | Feasibility gap | Relevance gap | Avg gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Virtual Scientist | 6.66 | -15.0 | -3.33 | -8.34 | -5.0 |
| AI-Researcher | 8.33 | 30.0 | -21.67 | -6.66 | 2.5 |
| InternAgent | 90.0 | 73.34 | 86.66 | 73.34 | 80.84 |
| AI Scientist-v2 | 33.34 | -58.34 | 15.0 | 8.33 | -0.42 |
| Hypogenic | 11.66 | -68.33 | 11.67 | -1.67 | -11.67 |
| Novix | 8.33 | -3.33 | -3.33 | -5.0 | -0.83 |
| K-Dense | 5.0 | -31.66 | 6.67 | 0.0 | -5.0 |

## Canonical Artifacts

- Judge inputs: `artifacts/judge_inputs/results.jsonl`
- Judge outputs: `artifacts/judge_outputs/results.jsonl`
- Aggregate CSV: `artifacts/tables/idea_generation_win_tie_lose.csv`
- Aggregate JSON: `artifacts/tables/idea_generation_win_tie_lose.json`

## Caveats

- This is a replacement/proxy rerun, not the original paper's raw Table 1 baseline outputs.
- Virtual Scientist, AI-Researcher, Hypogenic, Novix, and K-Dense use proxy replacement prompts because public paper-exact runners or raw outputs were unavailable.
- InternAgent and AI Scientist-v2 are replacement adapter runs, not author-provided paper artifacts.
- The judge is Monica/Gemini `gemini-3-flash-preview`, not a verified author-side `gemini-3-flash` transcript.
