# Paper Reproduction Action Plan

Date: 2026-06-04
Paper: arXiv:2603.08127
Current status: `incomplete`

This file lists the next evidence-producing steps needed before the
paper-level completion audit can pass.

## Actions

### 1. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/Virtual Scientist/

System: Virtual Scientist
Probe: reproduction/virtual_scientist_baseline_probe.json
Note: Current probe maps Virtual Scientist to VirSci/Virtual-Scientists. It is a runnable open-source collaboration platform, but not a drop-in runner for the 30 recovered EvoScientist queries.

Commands:

```bash
git clone https://github.com/open-sciencelab/Virtual-Scientists $HOME/research/Virtual-Scientists
# Download the AMiner-derived Papers, Embeddings, Authors, and adjacency data linked in the VirSci README.
# Patch sci_platform/sci_platform.py paths and run Ollama llama3.1/mxbai-embed-large under a pinned adapter protocol.
# Extract generated idea/abstract fields from team_info/*_dialogue.json into outputs/evoscientist_table1_queries/virtual_scientist/query_XX.md
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'Virtual Scientist' --source $HOME/research/Virtual-Scientists/outputs/evoscientist_table1_queries/virtual_scientist --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
```

### 2. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/AI-Researcher/

System: AI-Researcher
Probe: reproduction/ai_researcher_baseline_probe.json
Note: Current probe found the public AI-Researcher runner is benchmark-instance based, not a drop-in runner for the 30 recovered EvoScientist queries.

Commands:

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name AI-Researcher --source {source_jsonl} --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/import_baseline_outputs.py --system-name AI-Researcher --source {source_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline AI-Researcher --output reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline AI-Researcher --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json
```

### 3. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/Hypogenic/

System: Hypogenic
Probe: reproduction/hypogenic_baseline_probe.json
Note: Current probe found Hypogenic has a hosted Assistant/IdeaHub/Arena platform and generated competition repositories, but no public batch runner or raw Table 1 outputs.

Commands:

```bash
# With Hypogenic account access: open https://hypogenic.ai/chat under a pinned browser/profile state.
# Submit one recovered query per fresh Assistant session and capture the final answer plus session metadata.
# Save outputs as $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_XX.md
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Hypogenic --source $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
```

### 4. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/Novix/

System: Novix
Probe: reproduction/novix_baseline_probe.json
Note: Current probe found Novix is a hosted UI adapter candidate linked to AI-Researcher, with visible login/session/task endpoints but no public batch runner or raw Table 1 outputs.

Commands:

```bash
# With Novix account access: open https://novix.science/chat under a pinned browser/profile state.
# Submit one recovered query per fresh session and capture the final assistant answer plus session metadata.
# Save outputs as $HOME/research/novix/outputs/evoscientist_table1_queries/novix/query_XX.md
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Novix --source $HOME/research/novix/outputs/evoscientist_table1_queries/novix --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
```

### 5. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/K-Dense/

System: K-Dense
Probe: reproduction/k_dense_baseline_probe.json
Note: Current probe found K-Dense has a BYOK local Web/API adapter through ADK `/run_sse`, but it needs a pinned Python 3.13/OpenRouter/Gemini CLI setup and is not paper-exact raw Table 1 evidence.

Commands:

```bash
git clone https://github.com/K-Dense-AI/k-dense-byok $HOME/research/k-dense-byok && cd $HOME/research/k-dense-byok && git checkout 593c49b8e79c704c5979ec81c49f1791b5114083
./start.sh
# In a separate adapter process: create one ADK session per query, POST each query to /run_sse, and save final assistant text as outputs/evoscientist_table1_queries/k_dense/query_XX.md
.venv/bin/python reproduction/import_baseline_outputs.py --system-name K-Dense --source $HOME/research/k-dense-byok/outputs/evoscientist_table1_queries/k_dense --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
```

### 6. table1_llm_idea_generation / paper_judge_completion

Required evidence: 420 swapped pairwise records plus Gemini-3-flash judge outputs


Commands:

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --baseline AI-Researcher --baseline InternAgent --baseline 'AI Scientist-v2' --baseline Hypogenic --baseline Novix --baseline K-Dense --output reproduction/artifacts/judge_inputs/results.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider google --model gemini-3-flash --input reproduction/artifacts/judge_inputs/results.jsonl --output reproduction/artifacts/judge_outputs/results.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/results.jsonl --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json --section table1_llm_idea_generation --require-all
```

### 7. table2_human_idea_generation / human_label_import

Required evidence: inputs.jsonl, labels.jsonl, and aggregate.json for three PhD-level annotators

Missing Files: inputs.jsonl, labels.jsonl, aggregate.json
Runbook: reproduction/paper_level_evidence_runbook/paper_level_evidence_runbook.json
Gate: reproduction/paper_level_evidence_gate.json

Commands:

```bash
.venv/bin/python reproduction/build_paper_level_evidence_runbook.py
.venv/bin/python reproduction/verify_paper_level_evidence_gate.py
.venv/bin/python reproduction/aggregate_human_labels.py --inputs reproduction/artifacts/human_evaluation/inputs.jsonl --labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict
```

## Baseline Readiness

Source: `reproduction/baseline_readiness_matrix.json`
Rerun queue: `reproduction/baseline_rerun_manifest.json`

- paper_exact_available: 0
- replacement_direct_or_near_direct: 3
- replacement_adapter_required: 4
- not_reproducible_from_public_artifacts: 0

## Final Gate

```bash
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```

## Why This Is Still Incomplete

- incomplete: table1_llm_idea_generation
- incomplete: table2_human_idea_generation

As of 2026-06-04, exact paper-level numeric reproduction is not possible from public artifacts alone. The current repository reproduces the software, 30/30 full EvoScientist trajectories under a DeepSeek-backed setup, and a stated replacement comparison, while documenting the remaining public-artifact gaps required for exact reproduction.
