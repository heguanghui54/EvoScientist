# Baseline Readiness Matrix

Date: 2026-06-04
Paper: arXiv:2603.08127

This matrix summarizes the seven Table 1 baseline probes. It separates
paper-exact evidence from replacement rerun paths.

## Summary

- paper_exact_available: 0
- replacement_direct_or_near_direct: 3
- replacement_adapter_required: 4
- not_reproducible_from_public_artifacts: 0
- paper_exact_ready: False

## Matrix

| Baseline | Probe status | Direct 30-query runner | Readiness | Raw Table 1 outputs |
| --- | --- | --- | --- | --- |
| Virtual Scientist | `open_source_platform_not_drop_in` | no | `replacement_adapter_required` | no |
| AI-Researcher | `not_drop_in` | no | `replacement_adapter_required` | no |
| InternAgent | `qa_drop_in_candidate` | yes | `replacement_direct_or_near_direct` | no |
| AI Scientist-v2 | `ideation_adapter_candidate` | yes | `replacement_direct_or_near_direct` | no |
| Hypogenic | `hosted_competition_adapter_candidate` | no | `replacement_adapter_required` | no |
| Novix | `hosted_ui_adapter_candidate` | no | `replacement_adapter_required` | no |
| K-Dense | `local_web_api_adapter_candidate` | yes | `replacement_direct_or_near_direct` | no |

## Exact Reproduction Blocker

No Table 1 baseline has public raw 30-query outputs or the paper's Gemini-3-flash judge records; exact Table 1 reproduction still requires author-provided outputs or a full rerun/import of every baseline.

## Next Gate

```bash
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```
