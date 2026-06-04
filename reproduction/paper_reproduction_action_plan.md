# Paper Reproduction Action Plan

Date: 2026-06-04
Paper: arXiv:2603.08127
Current status: `incomplete`

This file lists the next evidence-producing steps needed before the
paper-level completion audit can pass.

## Actions

### 1. table2_human_idea_generation / human_label_import

Required evidence: inputs.jsonl, labels.jsonl, and aggregate.json for three PhD-level annotators

Missing Files: labels.jsonl, aggregate.json
Runbook: reproduction/paper_level_evidence_runbook/paper_level_evidence_runbook.json
Gate: reproduction/paper_level_evidence_gate.json

Commands:

```bash
.venv/bin/python reproduction/build_paper_level_evidence_runbook.py
.venv/bin/python reproduction/build_table2_human_label_packet.py
.venv/bin/python reproduction/import_table2_human_label_sheet.py --sheet reproduction/artifacts/human_evaluation/label_packet/label_sheet_template.csv --output-labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict
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

- incomplete: table2_human_idea_generation

As of 2026-06-04, exact paper-level numeric reproduction is not possible from public artifacts alone. The current repository reproduces the software, 30/30 full EvoScientist trajectories under a DeepSeek-backed setup, and a stated replacement comparison, while documenting the remaining public-artifact gaps required for exact reproduction.
