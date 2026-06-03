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

Commands:

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'Virtual Scientist' --source {source_jsonl} --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'Virtual Scientist' --source {source_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --output reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'Virtual Scientist' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json
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

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/InternAgent/

System: InternAgent
Probe: reproduction/internagent_baseline_probe.json
Note: Current probe found InternAgent has a one-shot QA CLI suitable for a replacement baseline rerun, but it is not paper-exact raw Table 1 evidence.

Commands:

```bash
git clone https://github.com/InternScience/InternAgent.git {external_checkout}
cd {external_checkout} && conda create -n InternAgent python=3.11 && conda activate InternAgent && pip install -r requirements.txt
python launch.py --mode qa --question {query_json_string} --output {answers_dir}/query_{id:02d}.md
.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source {answers_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
```

### 4. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/AI Scientist-v2/

System: AI Scientist-v2

Commands:

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'AI Scientist-v2' --source {source_jsonl} --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'AI Scientist-v2' --source {source_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'AI Scientist-v2' --output reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'AI Scientist-v2' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
```

### 5. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/Hypogenic/

System: Hypogenic

Commands:

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Hypogenic --source {source_jsonl} --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Hypogenic --source {source_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline Hypogenic --output reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline Hypogenic --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_hypogenic.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_hypogenic_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_hypogenic_deepseek.json
```

### 6. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/Novix/

System: Novix

Commands:

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Novix --source {source_jsonl} --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/import_baseline_outputs.py --system-name Novix --source {source_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline Novix --output reproduction/artifacts/judge_inputs/evosci_vs_novix.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_novix.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_novix_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_novix_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_novix_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_novix_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline Novix --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_novix.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_novix_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_novix_deepseek.json
```

### 7. table1_llm_idea_generation / baseline_output_import_or_generation

Required evidence: 30 answer.txt files under reproduction/artifacts/idea_outputs/K-Dense/

System: K-Dense

Commands:

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name K-Dense --source {source_jsonl} --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/import_baseline_outputs.py --system-name K-Dense --source {source_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline K-Dense --output reproduction/artifacts/judge_inputs/evosci_vs_k_dense.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_k_dense.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_k_dense_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_k_dense_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_k_dense_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_k_dense_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline K-Dense --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_k_dense.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_k_dense_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_k_dense_deepseek.json
```

### 8. table1_llm_idea_generation / paper_judge_completion

Required evidence: 420 swapped pairwise records plus Gemini-3-flash judge outputs


Commands:

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --baseline AI-Researcher --baseline InternAgent --baseline 'AI Scientist-v2' --baseline Hypogenic --baseline Novix --baseline K-Dense --output reproduction/artifacts/judge_inputs/results.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider google --model gemini-3-flash --input reproduction/artifacts/judge_inputs/results.jsonl --output reproduction/artifacts/judge_outputs/results.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/results.jsonl --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json --section table1_llm_idea_generation --require-all
```

### 9. table2_human_idea_generation / human_label_import

Required evidence: inputs.jsonl, labels.jsonl, and aggregate.json for three PhD-level annotators

Missing Files: inputs.jsonl, labels.jsonl, aggregate.json

Commands:

```bash
.venv/bin/python reproduction/aggregate_human_labels.py --inputs reproduction/artifacts/human_evaluation/inputs.jsonl --labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict
```

### 10. table3_ablation_idea_generation / ablation_variant_runs

Required evidence: system_outputs_complete.json, judge_inputs.jsonl, judge_outputs.jsonl, and aggregate.json for -IDE, -IVE, and -all

Missing Variants: -IDE, -IVE, -all
Note: The repository has no native ablation toggles yet; variant outputs must come from a paper-matched patch or imported raw ablation runs.

Commands:

```bash
.venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all
```

### 11. figure2_code_execution / code_execution_log_import

Required evidence: trajectories.jsonl, execution_logs.jsonl, and summary.json with before/after evolution success rates

Missing Files: trajectories.jsonl, execution_logs.jsonl, summary.json

Commands:

```bash
.venv/bin/python reproduction/aggregate_code_execution.py --logs reproduction/artifacts/code_execution/execution_logs.jsonl --output-json reproduction/artifacts/code_execution/summary.json --output-csv reproduction/artifacts/code_execution/summary.csv --strict
.venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/code_execution/summary.json --section figure2_code_execution --require-all
```

## Final Gate

```bash
.venv/bin/python reproduction/audit_paper_level_completion.py --strict
```

## Why This Is Still Incomplete

- incomplete: table1_llm_idea_generation
- incomplete: table2_human_idea_generation
- incomplete: table3_ablation_idea_generation
- incomplete: figure2_code_execution

As of 2026-06-04, exact paper-level numeric reproduction is not possible from public artifacts alone. The current repository reproduces the software, 30/30 full EvoScientist trajectories under a DeepSeek-backed setup, and a stated replacement comparison, while documenting the remaining public-artifact gaps required for exact reproduction.
