# User-Scope EvoScientist Reproduction Gate

Date: 2026-06-04
Status: `complete`
Paper-exact: `false`
Human judge status: `waived_by_user_for_current_scope`

user-scoped reproduction with Monica/Gemini surrogate judging and human judge waived for now

## Checks

| Check | Complete | Evidence |
| --- | --- | --- |
| full_trajectories | true | 30/30 successful full trajectories in final dossier |
| table1_replacement_judge | true | seven baselines x 30 queries x 2 swapped orders = 420 Monica/Gemini judge outputs |
| table2_surrogate_judge | true | human judge waived by user; Monica/Gemini surrogate labels are available |
| table2_human_label_packet | true | fillable 1440-row human label sheet and full-text review tasks are present |
| table3_replacement_ablation | true | 30-query Monica/Gemini replacement ablation rerun |
| figure2_replacement_probe | true | 240-record deterministic replacement code-execution probe |
| dossier | true | final reproduction dossier exists |
| reproducibility_bundle | true | zip bundle, manifest, checksums, and line-count checks exist |

## Paper-Exact Remaining Gap

- author-provided original raw Table 1 baseline outputs
- author-side original Gemini judge transcripts
- three PhD-level Table 2 human labels and aggregate
