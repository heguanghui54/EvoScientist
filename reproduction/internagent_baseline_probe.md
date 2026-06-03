# InternAgent Baseline Probe

Date: 2026-06-04
Source: https://github.com/InternScience/InternAgent
Checked HEAD: `e341f8f181e6d337317c6bc2cddae6391b1f0390`

Drop-in status: `qa_drop_in_candidate`
Paper-exact status: `not_paper_exact`

## Finding

InternAgent exposes a one-shot QA CLI that can accept each recovered EvoScientist query and write an answer file, making it a plausible replacement-baseline candidate. This still does not provide the raw InternAgent outputs used by the EvoScientist paper, nor does it match the paper's exact model/tool/judge setup without a pinned rerun protocol.

## Signals

- qa_cli_available: True
- master_qa_available: True
- discovery_task_based: True
- required_openai_compatible_key: True
- anthropic_required_for_experiment_backend: True
- missing_required_paths: []

## Entrypoints

- qa: python launch_qa.py --question '...' --output answer.md
- master_qa: python launch.py --mode qa --question '...' --output answer.md
- discovery: python launch.py --mode discovery --task AutoDebug --exp_backend claudecode

## Replacement Run Template

- checkout: `git clone https://github.com/InternScience/InternAgent.git {external_checkout}`
- install: `conda create -n InternAgent python=3.11 && conda activate InternAgent && pip install -r requirements.txt`
- per_query: `python launch.py --mode qa --question {question_json} --output {answer_path}`
- import_outputs: `.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source {answers_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict`

## Required Environment

- `OPENAI_API_KEY`
- `OPENAI_API_BASE_URL`
- `OPENAI_BASE_URL`
- `ANTHROPIC_API_KEY for claudecode experiment backend`

## Next Actions

- Use the QA CLI only as a replacement-baseline rerun path, not paper-exact Table 1 evidence.
- Run each of the 30 recovered queries in an isolated InternAgent checkout and save query_XX.md files.
- Import the saved answers with reproduction/import_baseline_outputs.py under system name InternAgent.
- Judge imported outputs through the existing swapped pairwise judge pipeline.
