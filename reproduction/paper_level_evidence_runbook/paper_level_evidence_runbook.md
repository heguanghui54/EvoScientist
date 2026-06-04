# Paper-Level Evidence Runbook

Date: 2026-06-04
Paper: arXiv:2603.08127
Paper-exact: `false`

These files are templates and runbooks, not completed paper artifacts. Copy or generate real records under reproduction/artifacts only after collecting paper-level human labels, ablation outputs, and execution logs.

## Table 2 Human Evaluation

- Baselines: InternAgent, AI Scientist-v2, Novix, K-Dense
- Pairwise comparison templates: 120
- Raw label templates: 1440

```bash
.venv/bin/python reproduction/aggregate_human_labels.py --inputs reproduction/artifacts/human_evaluation/inputs.jsonl --labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict
```

## Table 3 Ablation

- Variants: -IDE, -IVE, -all

```bash
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all
```

## Figure 2 Code Execution

- Trajectory templates: 240
- Execution-log templates: 240

```bash
.venv/bin/python reproduction/aggregate_code_execution.py --logs reproduction/artifacts/code_execution/execution_logs.jsonl --output-json reproduction/artifacts/code_execution/summary.json --output-csv reproduction/artifacts/code_execution/summary.csv --strict
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/code_execution/summary.json --section figure2_code_execution --require-all
```

## Acceptance

```bash
.venv/bin/python reproduction/verify_paper_artifact_schema.py --strict
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```
