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
| Table 1 LLM judge | incomplete | expected 420 pairwise records; missing baseline outputs: Virtual Scientist, AI-Researcher, InternAgent, AI Scientist-v2, Hypogenic, Novix, K-Dense |
| Table 2 human eval | incomplete | missing files: inputs.jsonl, labels.jsonl, aggregate.json |
| Table 3 ablation | incomplete | missing variants: -IDE, -IVE, -all |
| Figure 2 code execution | incomplete | missing files: trajectories.jsonl, execution_logs.jsonl, summary.json |

## Blocking Items

- incomplete: table1_llm_idea_generation
- incomplete: table2_human_idea_generation
- incomplete: table3_ablation_idea_generation
- incomplete: figure2_code_execution

## Interpretation

Direct-DeepSeek comparison is useful as a replacement baseline, but it does not satisfy the paper's seven-baseline Table 1 claim.

The reproduction harness is therefore ready for further experiments,
but the paper-level reproduction goal remains incomplete.
