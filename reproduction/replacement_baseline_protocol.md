# Replacement Baseline Protocol

Date: 2026-06-04

This protocol defines a reproducible substitute for the paper's Table 1 baseline
comparison when the original seven baseline outputs are unavailable. It is not an
exact Table 1 reproduction unless the paper's original baseline outputs and
Gemini-3-flash judge records are imported.

## Scope

- Query set: the 30 recovered paper queries in `reproduction/queries.json`.
- Target output: EvoScientist full tool-enabled DeepSeek trajectories, already
  complete for all 30 queries.
- Replacement output layout:
  `reproduction/artifacts/idea_outputs/{system}/query_{id:02d}/answer.txt`.
- Current completed replacement baseline: `Direct-DeepSeek`.
- Candidate rerun baselines: AI-Researcher, InternAgent, AI Scientist-v2, Novix,
  and K-Dense.

## Acceptance Checks

1. Every selected baseline has 30 non-empty `answer.txt` files.
2. Each answer records the prompt used and is generated from the verbatim
   recovered query.
3. Pairwise judge inputs contain 60 swapped records per selected baseline.
4. Judge outputs cover every `comparison_id` in the generated judge inputs.
5. Aggregates include Clarity, Novelty, Feasibility, and Relevance for each
   selected baseline.
6. The report states whether the comparison is paper-exact or replacement-only.

## Commands

Generate the completed replacement baseline:

```bash
.venv/bin/python reproduction/run_direct_baseline.py \
  --output-dir reproduction/artifacts/idea_outputs/Direct-DeepSeek
```

For another baseline after its outputs are normalized into the shared layout:

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py \
  --systems-root reproduction/artifacts/idea_outputs \
  --baseline {baseline} \
  --output reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl

.venv/bin/python reproduction/run_llm_judge.py \
  --provider deepseek \
  --model deepseek-v4-flash \
  --input reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl \
  --output reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl \
  --resume

.venv/bin/python reproduction/aggregate_judge_results.py \
  --input reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl \
  --output-csv reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.csv \
  --output-json reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.json
```

Then audit the comparison:

```bash
.venv/bin/python reproduction/audit_reproduction_artifacts.py \
  --baseline {baseline} \
  --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl \
  --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl \
  --aggregate-json reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.json
```

## Interpretation

This protocol is useful for extending the current Direct-DeepSeek comparison to
available baseline runners. It does not erase the paper-level gap: exact
reproduction still needs the paper's seven baseline outputs, Gemini judge
outputs, human labels, ablation outputs, and code-execution logs.
