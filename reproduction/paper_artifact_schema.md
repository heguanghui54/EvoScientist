# Paper Artifact Schemas

Date: 2026-06-04

These schemas define the minimum evidence needed before the remaining paper-level
components can be treated as reproduced. They do not create synthetic evidence;
they make future imports auditable.

## Table 2 Human Evaluation

Root: `reproduction/artifacts/human_evaluation`

- `inputs.jsonl`: each record needs `comparison_id`, `query_id`, `baseline`,
  `answer_a`, `answer_b`, and `dimensions`.
- `labels.jsonl`: each record needs `comparison_id`, `annotator_id`,
  `dimension`, and `winner`.
- `aggregate.json`: needs a `baselines` object with per-baseline dimensions.
- Valid winners: `assistant_1`, `assistant_2`, `tie`.
- Aggregator: `reproduction/aggregate_human_labels.py`.

Example:

```bash
.venv/bin/python reproduction/aggregate_human_labels.py \
  --inputs reproduction/artifacts/human_evaluation/inputs.jsonl \
  --labels reproduction/artifacts/human_evaluation/labels.jsonl \
  --output-csv reproduction/artifacts/human_evaluation/aggregate.csv \
  --output-json reproduction/artifacts/human_evaluation/aggregate.json \
  --strict
```

## Table 3 Ablations

Root: `reproduction/artifacts/ablations`

Required variants: `-IDE`, `-IVE`, `-all`.

Each variant needs:

- `system_outputs_complete.json`
- `judge_inputs.jsonl`
- `judge_outputs.jsonl`
- `aggregate.json`

## Figure 2 Code Execution

Root: `reproduction/artifacts/code_execution`

- `trajectories.jsonl`: trajectory/query/stage/proposal identifiers.
- `execution_logs.jsonl`: per-attempt execution success/failure records.
- `summary.json`: before/after evolution success rates and stage-level rates.

The paper-reported headline metrics are 34.39% before evolution, 44.56% after
evolution, 20.33% stage-3 before evolution, and 21.57% stage-3 after evolution.
