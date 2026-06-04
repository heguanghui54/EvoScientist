# Paper Reproduction Action Plan

Date: 2026-06-04
Paper: arXiv:2603.08127
Current status: `incomplete`

This file lists the next evidence-producing steps needed before the
paper-level completion audit can pass.

## Actions

### 1. table1_llm_idea_generation / paper_judge_completion

Required evidence: 420 swapped pairwise records plus Gemini-3-flash judge outputs


Commands:

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --baseline AI-Researcher --baseline InternAgent --baseline 'AI Scientist-v2' --baseline Hypogenic --baseline Novix --baseline K-Dense --output reproduction/artifacts/judge_inputs/results.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider google --model gemini-3-flash --input reproduction/artifacts/judge_inputs/results.jsonl --output reproduction/artifacts/judge_outputs/results.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/results.jsonl --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json --section table1_llm_idea_generation --require-all
```

### 2. table2_human_idea_generation / human_label_import

Required evidence: inputs.jsonl, labels.jsonl, and aggregate.json for three PhD-level annotators

Missing Files: inputs.jsonl, labels.jsonl, aggregate.json
Runbook: reproduction/paper_level_evidence_runbook/paper_level_evidence_runbook.json
Gate: reproduction/paper_level_evidence_gate.json

Commands:

```bash
.venv/bin/python reproduction/build_paper_level_evidence_runbook.py
.venv/bin/python reproduction/verify_paper_level_evidence_gate.py
.venv/bin/python reproduction/aggregate_human_labels.py --inputs reproduction/artifacts/human_evaluation/inputs.jsonl --labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict
```

## Baseline Readiness

Source: `reproduction/baseline_readiness_matrix.json`
Rerun queue: `reproduction/baseline_rerun_manifest.json`

- paper_exact_available: 0
- replacement_direct_or_near_direct: 3
- replacement_adapter_required: 4
- not_reproducible_from_public_artifacts: 0

## Final Gate

```bash
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```

## Why This Is Still Incomplete

- incomplete: table1_llm_idea_generation
- incomplete: table2_human_idea_generation

As of 2026-06-04, exact paper-level numeric reproduction is not possible from public artifacts alone. The current repository reproduces the software, 30/30 full EvoScientist trajectories under a DeepSeek-backed setup, and a stated replacement comparison, while documenting the remaining public-artifact gaps required for exact reproduction.
