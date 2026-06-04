# Paper-Level Reproduction Completion Audit

Date: 2026-06-04

Overall status: `incomplete`

This audit is stricter than local preflight. It asks whether the raw
artifacts needed to reproduce the paper tables and figure-level claims
are present in the checkout.

## Component Status

| Component | Status | Evidence |
| --- | --- | --- |
| Full trajectories | complete | 30/30 successful final reports; non-success IDs: none |
| Table 1 LLM judge | complete | expected 420 pairwise records; missing baseline outputs: none; paper-exact: false |
| Table 2 human eval | incomplete | missing files: inputs.jsonl, labels.jsonl, aggregate.json |
| Table 3 ablation | complete | missing variants: none |
| Figure 2 code execution | complete | missing files: none |

## Blocking Items

- incomplete: table2_human_idea_generation

## Interpretation

The seven-baseline Table 1 replacement/proxy judge coverage is now complete, but it is not paper-exact author raw output or original judge-transcript evidence.

The reproduction harness is therefore ready for further experiments,
but the paper-level reproduction goal remains incomplete.
