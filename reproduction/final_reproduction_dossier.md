# EvoScientist Reproduction Dossier

Date: 2026-06-04
Branch: `codex/reproduction-assets`
Overall status: `incomplete`
User-scope status: `complete`
Paper-exact: `false`

EvoScientist experiment reproduction with replacement/proxy evidence where public paper-exact artifacts are unavailable.

## Component Status

| Component | Status | Paper-exact | Evidence |
| --- | --- | --- | --- |
| Full trajectories | complete | false | 30/30 successful final reports |
| Table 1 LLM judge | complete | false | 420/420 swapped pairwise judge records |
| Table 2 human eval | incomplete | false | 120 inputs ready; surrogate labels ready; human labels missing |
| Table 3 ablation | complete | false | 30-query replacement ablation rerun |
| Figure 2 code execution | complete | false | 240-record deterministic replacement probe |

## Table 1 Summary

- Queries: 30
- Baselines: 7
- Judge outputs: 420

| Baseline | Avg gap |
| --- | ---: |
| Virtual Scientist | -5.0 |
| AI-Researcher | 2.5 |
| InternAgent | 80.84 |
| AI Scientist-v2 | -0.42 |
| Hypogenic | -11.67 |
| Novix | -0.83 |
| K-Dense | -5.0 |

## Table 2 Status

- Human inputs ready: 120
- Surrogate label records: 1440
- Human label packet rows: 1440
- Missing formal human files: labels.jsonl, aggregate.json

## Key Artifacts

### table1
- report_md: `table1_replacement_all_baselines_monica_report.md`
- judge_inputs: `artifacts/judge_inputs/results.jsonl`
- judge_outputs: `artifacts/judge_outputs/results.jsonl`
- aggregate_json: `artifacts/tables/idea_generation_win_tie_lose.json`
- aggregate_csv: `artifacts/tables/idea_generation_win_tie_lose.csv`

### table2
- surrogate_report_md: `table2_surrogate_monica_report.md`
- human_inputs: `artifacts/human_evaluation/inputs.jsonl`
- surrogate_labels: `artifacts/human_evaluation/surrogate_labels.jsonl`
- surrogate_aggregate_json: `artifacts/human_evaluation/surrogate_aggregate.json`
- label_packet_guide: `artifacts/human_evaluation/label_packet/annotation_guide.md`
- label_packet_sheet: `artifacts/human_evaluation/label_packet/label_sheet_template.csv`

### table3
- report_md: `ablation_queries01_30_monica_gemini_report.md`
- combined_aggregate: `artifacts/ablations/combined_aggregate.json`

### figure2
- report_md: `figure2_code_execution_replacement_report.md`
- summary: `artifacts/code_execution/summary.json`

### audit
- paper_level_md: `artifacts/audit/paper_level_completion_latest.md`
- paper_level_json: `artifacts/audit/paper_level_completion_latest.json`
- schema_json: `artifacts/audit/paper_artifact_schema_latest.json`
- user_scope_gate_md: `artifacts/audit/user_scope_reproduction_gate.md`
- user_scope_gate_json: `artifacts/audit/user_scope_reproduction_gate.json`

## Remaining Blocker

- incomplete: table2_human_idea_generation

## User-Scope Gate

- Status: `complete`
- Human judge status: `waived_by_user_for_current_scope`


## Verification

```bash
.venv/bin/python reproduction/verify_reproduction_assets.py
bash reproduction/run_preflight.sh
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```
