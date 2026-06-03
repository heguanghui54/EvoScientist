# Paper Baseline Availability Inventory

Date: 2026-06-04

This inventory separates public baseline entrypoints from the actual raw
artifacts required for Table 1 of arXiv:2603.08127. A public repository or hosted
product is useful for a future rerun, but it does not satisfy the paper-level
requirement unless it provides the 30-query baseline outputs and the paired judge
records used by the paper.

## Summary

- Table 1 baselines checked: 7.
- Raw baseline-output packages found: 0.
- Runner or hosted candidates found: AI-Researcher, InternAgent,
  AI Scientist-v2, Novix, K-Dense.
- No reliable public runner found in the refreshed search: Virtual Scientist,
  Hypogenic.

## Baseline Inventory

| Baseline | Public entrypoint status | Public entrypoints | Raw Table 1 outputs found | Reproduction implication |
| --- | --- | --- | --- | --- |
| Virtual Scientist | not_found | none found | no | Needs author-provided outputs or a separately defined substitute. |
| AI-Researcher | open_source_runner_candidate | `https://github.com/hkuds/ai-researcher`; `reproduction/ai_researcher_baseline_probe.json`; `https://novix.science/chat` | no | Replacement candidate, but current probe found it is benchmark-instance based, not a drop-in runner for the 30 recovered EvoScientist queries. |
| InternAgent | open_source_runner_candidate | `https://github.com/InternScience/InternAgent`; `reproduction/internagent_baseline_probe.json` | no | QA replacement candidate: probe found a one-shot `launch.py --mode qa --question ... --output ...` path, but no paper raw outputs. |
| AI Scientist-v2 | open_source_runner_candidate | `https://github.com/SakanaAI/AI-Scientist-v2` | no | Runnable candidate, but requires setup, prompt alignment, and new outputs. |
| Hypogenic | not_found | none found | no | Needs author-provided outputs, service access if applicable, or a substitute. |
| Novix | hosted_or_commercial_candidate | `https://novix.science/chat` | no | Hosted rerun candidate, but needs account/service access and pinned protocol. |
| K-Dense | open_source_and_hosted_candidate | `https://github.com/K-Dense-AI`; `https://k-dense.ai/` | no | Hosted/open-source rerun candidate, but needs setup and protocol alignment. |

## Next Action

For exact Table 1 reproduction, import the author-provided raw baseline outputs
if they become available. If they do not, the defensible reproducible path is to
define a replacement-baseline protocol and run the open-source or hosted
candidates above under the same 30 recovered queries, then generate 420 swapped
pairwise judge records with a pinned judge model.
