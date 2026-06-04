# Figure 2 Code Execution Replacement Report

Date: 2026-06-04
Status: `complete` for the replacement code-execution probe
Paper-exact: `false`

This report fills the machine-checkable Figure 2 artifact chain with a deterministic local replacement probe. It executes validation checks over existing reproduction artifacts instead of recreating the paper authors original generated-code execution benchmark.

## Artifacts

- `reproduction/artifacts/code_execution/trajectories.jsonl`
- `reproduction/artifacts/code_execution/execution_logs.jsonl`
- `reproduction/artifacts/code_execution/summary.json`
- `reproduction/artifacts/code_execution/summary.csv`
- `reproduction/artifacts/code_execution/figure2_compare_to_paper.json`

## Coverage

- Trajectory records: `240`
- Execution log records: `240`
- Usable execution records: `240`
- Phases: `before_evolution`, `after_evolution`
- Stages: `stage_1`, `stage_2`, `stage_3`, `stage_4`

## Replacement Probe Result

| Metric | Value |
| --- | ---: |
| Before evolution success | 84.17% |
| After evolution success | 100.00% |
| Stage 3 before evolution success | 63.33% |
| Stage 3 after evolution success | 100.00% |

## Paper Comparison

Compare-to-paper status: `fail` with `['before_evolution_pct: actual=84.17 expected=34.39 delta=49.78', 'after_evolution_pct: actual=100.0 expected=44.56 delta=55.44', 'stage3_before_evolution_pct: actual=63.33 expected=20.33 delta=43.0', 'stage3_after_evolution_pct: actual=100.0 expected=21.57 delta=78.43']` failures. This failure is expected because the probe is replacement evidence, not the paper-native generated-code execution run.

## Verification

```bash
.venv/bin/python reproduction/build_code_execution_replacement_probe.py --output-root reproduction/artifacts/code_execution
.venv/bin/python reproduction/aggregate_code_execution.py --logs reproduction/artifacts/code_execution/execution_logs.jsonl --output-json reproduction/artifacts/code_execution/summary.json --output-csv reproduction/artifacts/code_execution/summary.csv --strict
.venv/bin/python reproduction/verify_paper_artifact_schema.py --output-json reproduction/artifacts/audit/paper_artifact_schema_latest.json
```
