# Baseline Rerun Manifest

Date: 2026-06-04
Paper: arXiv:2603.08127

Replacement-only unless author-provided paper baseline outputs and Gemini-3-flash judge records are imported.

## Baselines

### Virtual Scientist

Readiness: `replacement_adapter_required`
Requires adapter: True
Probe: `reproduction/virtual_scientist_baseline_probe.json`

Commands:

```bash
git clone https://github.com/open-sciencelab/Virtual-Scientists $HOME/research/Virtual-Scientists
# Download the AMiner-derived Papers, Embeddings, Authors, and adjacency data linked in the VirSci README.
# Patch sci_platform/sci_platform.py paths and run Ollama llama3.1/mxbai-embed-large.
# Extract generated idea/abstract fields from team_info/*_dialogue.json into outputs/evoscientist_table1_queries/virtual_scientist/query_XX.md.
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'Virtual Scientist' --source $HOME/research/Virtual-Scientists/outputs/evoscientist_table1_queries/virtual_scientist --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --output reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'Virtual Scientist' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json
```

### AI-Researcher

Readiness: `replacement_adapter_required`
Requires adapter: True
Probe: `reproduction/ai_researcher_baseline_probe.json`

Commands:

```bash
git clone https://github.com/HKUDS/AI-Researcher $HOME/research/AI-Researcher
# Configure CATEGORY, INSTANCE_ID, TASK_LEVEL, Docker/workplace, and a pinned adapter from each recovered query.
.venv/bin/python reproduction/import_baseline_outputs.py --system-name AI-Researcher --source $HOME/research/AI-Researcher/outputs/evoscientist_table1_queries/ai_researcher --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline AI-Researcher --output reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline AI-Researcher --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json
```

### InternAgent

Readiness: `replacement_direct_or_near_direct`
Requires adapter: False
Probe: `reproduction/internagent_baseline_probe.json`

Commands:

```bash
.venv/bin/python reproduction/build_internagent_qa_runbook.py
bash /path/to/EvoScientist/reproduction/internagent_qa_runbook.sh
.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --output reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_deepseek.json
```

### AI Scientist-v2

Readiness: `replacement_direct_or_near_direct`
Requires adapter: False
Probe: `reproduction/ai_scientist_v2_baseline_probe.json`

Commands:

```bash
.venv/bin/python reproduction/build_ai_scientist_v2_ideation_runbook.py
bash /path/to/EvoScientist/reproduction/ai_scientist_v2_ideation_runbook/run_ai_scientist_v2_ideation.sh
.venv/bin/python reproduction/convert_ai_scientist_v2_ideation_outputs.py
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'AI Scientist-v2' --source reproduction/ai_scientist_v2_ideation_import_template.jsonl --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'AI Scientist-v2' --output reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'AI Scientist-v2' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
```

### Hypogenic

Readiness: `replacement_adapter_required`
Requires adapter: True
Probe: `reproduction/hypogenic_baseline_probe.json`

Commands:

```bash
# With Hypogenic account access: open https://hypogenic.ai/chat under a pinned browser/profile state.
# Submit one recovered query per fresh Assistant session and capture the final answer plus session metadata.
# Save outputs as $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_XX.md.
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Hypogenic --source $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline Hypogenic --output reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline Hypogenic --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.json
```

### Novix

Readiness: `replacement_adapter_required`
Requires adapter: True
Probe: `reproduction/novix_baseline_probe.json`

Commands:

```bash
# With Novix account access: open https://novix.science/chat under a pinned browser/profile state.
# Submit one recovered query per fresh session and capture the final assistant answer plus session metadata.
# Save outputs as $HOME/research/novix/outputs/evoscientist_table1_queries/novix/query_XX.md.
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Novix --source $HOME/research/novix/outputs/evoscientist_table1_queries/novix --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline Novix --output reproduction/artifacts/judge_inputs/evosci_vs_novix.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_novix.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_novix_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_novix_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_novix_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_novix_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline Novix --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_novix.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_novix_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_novix_deepseek.json
```

### K-Dense

Readiness: `replacement_direct_or_near_direct`
Requires adapter: False
Probe: `reproduction/k_dense_baseline_probe.json`

Commands:

```bash
git clone https://github.com/K-Dense-AI/k-dense-byok $HOME/research/k-dense-byok && cd $HOME/research/k-dense-byok && git checkout 593c49b8e79c704c5979ec81c49f1791b5114083
./start.sh
# In a separate adapter process: create one ADK session per query, POST each query to /run_sse, and save final assistant text as outputs/evoscientist_table1_queries/k_dense/query_XX.md.
.venv/bin/python reproduction/import_baseline_outputs.py --system-name K-Dense --source $HOME/research/k-dense-byok/outputs/evoscientist_table1_queries/k_dense --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline K-Dense --output reproduction/artifacts/judge_inputs/evosci_vs_k_dense.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_k_dense.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_k_dense_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_k_dense_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_k_dense_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_k_dense_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline K-Dense --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_k_dense.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_k_dense_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_k_dense_deepseek.json
```

## Combined Paper-Exact Judge Commands

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --baseline AI-Researcher --baseline InternAgent --baseline 'AI Scientist-v2' --baseline Hypogenic --baseline Novix --baseline K-Dense --output reproduction/artifacts/judge_inputs/results.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider google --model gemini-3-flash --input reproduction/artifacts/judge_inputs/results.jsonl --output reproduction/artifacts/judge_outputs/results.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/results.jsonl --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json
```

## Final Gate

```bash
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```
