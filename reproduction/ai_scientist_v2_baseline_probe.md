# AI Scientist-v2 Baseline Probe

Date: 2026-06-04
Source: https://github.com/SakanaAI/AI-Scientist-v2
Checked HEAD: `96bd51617cfdbb494a9fc283af00fe090edfae48`

Drop-in status: `ideation_adapter_candidate`
Paper-exact status: `not_paper_exact`

## Finding

AI Scientist-v2 has a usable ideation CLI that can be adapted to the 30 recovered EvoScientist queries by writing one topic markdown file per query and importing the resulting JSON idea as baseline output. This is a replacement-baseline rerun path, not the paper's raw AI Scientist-v2 Table 1 artifact.

## Signals

- ideation_cli_available: True
- structured_idea_output: True
- topic_markdown_template: True
- full_pipeline_available: True
- requires_linux_cuda_for_full_pipeline: True
- semantic_scholar_used_for_novelty: True
- missing_required_paths: []

## Entrypoints

- ideation: `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/my_research_topic.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- full_pipeline: `python launch_scientist_bfts.py --load_ideas ai_scientist/ideas/my_research_topic.json ...`

## Required Environment

- `OPENAI_API_KEY or GEMINI_API_KEY`
- `S2_API_KEY optional for Semantic Scholar`

## Next Actions

- Generate per-query topic markdown files from reproduction/queries.json.
- Run perform_ideation_temp_free.py once per query with a pinned model and reflection budget.
- Convert each generated JSON idea file into query_XX.md or JSONL records accepted by import_baseline_outputs.py.
- Judge imported outputs through the existing swapped pairwise judge pipeline.
