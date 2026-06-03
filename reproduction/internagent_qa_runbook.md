# InternAgent QA Replacement-Baseline Runbook

Date: 2026-06-04
Queries: 30
Paper-exact: `false`

This runbook generates replacement-baseline answers through InternAgent QA mode. It does not recover the paper's original raw InternAgent Table 1 outputs.

## External Checkout Setup

```bash
git clone https://github.com/InternScience/InternAgent.git $HOME/research/InternAgent
cd $HOME/research/InternAgent
conda create -n InternAgent python=3.11
conda activate InternAgent
pip install -r requirements.txt
cp .env.example .env
# Fill OPENAI_API_KEY and OPENAI_API_BASE_URL in .env before running.
```

## Run Queries

Run from the external InternAgent checkout:

```bash
bash /path/to/EvoScientist/reproduction/internagent_qa_runbook.sh
```

## Import Outputs

Run from the EvoScientist checkout:

```bash
.venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --strict
```

## Judge And Audit

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --output reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_deepseek.json
```

## Command List

- Query 01 (Machine translation): `python launch.py --mode qa --question 'Generate a research proposal on low-resource machine translation.' --output outputs/evoscientist_table1_queries/internagent/query_01.md`
- Query 02 (Software engineering): `python launch.py --mode qa --question 'Help me generate a research proposal on AI for software engineering.' --output outputs/evoscientist_table1_queries/internagent/query_02.md`
- Query 03 (LLM evaluation): `python launch.py --mode qa --question 'Generate a research proposal on how to address the accuracy issues of automated evaluation for Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_03.md`
- Query 04 (Healthcare agents): `python launch.py --mode qa --question 'Help me generate a research proposal on AI agents in healthcare.' --output outputs/evoscientist_table1_queries/internagent/query_04.md`
- Query 05 (Literature review automation): `python launch.py --mode qa --question 'Generate a research proposal on automated literature review generation.' --output outputs/evoscientist_table1_queries/internagent/query_05.md`
- Query 06 (Speech recognition): `python launch.py --mode qa --question 'Generate a research proposal on low-resource speech recognition.' --output outputs/evoscientist_table1_queries/internagent/query_06.md`
- Query 07 (Model efficiency): `python launch.py --mode qa --question 'Generate a research proposal on how to break the performance ceiling of small models.' --output outputs/evoscientist_table1_queries/internagent/query_07.md`
- Query 08 (AI agents): `python launch.py --mode qa --question 'Generate a research proposal on complex reasoning for AI agents.' --output outputs/evoscientist_table1_queries/internagent/query_08.md`
- Query 09 (Model deployment): `python launch.py --mode qa --question 'Generate a research proposal on solving quantization challenges for LLM deployment on edge devices.' --output outputs/evoscientist_table1_queries/internagent/query_09.md`
- Query 10 (Text-to-SQL): `python launch.py --mode qa --question 'Help me generate a research proposal on Text-to-SQL.' --output outputs/evoscientist_table1_queries/internagent/query_10.md`
- Query 11 (LLM capabilities): `python launch.py --mode qa --question 'Generate a research proposal on the decoupling of Large Language Model capabilities.' --output outputs/evoscientist_table1_queries/internagent/query_11.md`
- Query 12 (Factual consistency): `python launch.py --mode qa --question 'Generate a research proposal on how to resolve factual consistency issues in Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_12.md`
- Query 13 (Data synthesis): `python launch.py --mode qa --question 'Generate a research proposal on data synthesis for code LLMs.' --output outputs/evoscientist_table1_queries/internagent/query_13.md`
- Query 14 (Inference efficiency): `python launch.py --mode qa --question 'Generate a research proposal on solving inference latency issues in Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_14.md`
- Query 15 (Machine translation): `python launch.py --mode qa --question 'Generate a research proposal on debiasing in machine translation.' --output outputs/evoscientist_table1_queries/internagent/query_15.md`
- Query 16 (Knowledge injection): `python launch.py --mode qa --question 'Generate a research proposal on addressing the challenges of knowledge injection in domain-specific Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_16.md`
- Query 17 (Information extraction): `python launch.py --mode qa --question 'Generate a research proposal on automated information extraction.' --output outputs/evoscientist_table1_queries/internagent/query_17.md`
- Query 18 (UX evaluation): `python launch.py --mode qa --question 'Generate a research proposal on user experience evaluation for Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_18.md`
- Query 19 (Evaluation leaderboards): `python launch.py --mode qa --question 'Generate a research proposal on how to construct efficient leaderboards for LLM evaluation.' --output outputs/evoscientist_table1_queries/internagent/query_19.md`
- Query 20 (Text generation): `python launch.py --mode qa --question 'Generate a research proposal on the evaluation of diversity in text generation.' --output outputs/evoscientist_table1_queries/internagent/query_20.md`
- Query 21 (Content detection): `python launch.py --mode qa --question 'Generate a research proposal on how to address false positives in AI-generated content detection.' --output outputs/evoscientist_table1_queries/internagent/query_21.md`
- Query 22 (Code LLM security): `python launch.py --mode qa --question 'Generate a research proposal on the security of code LLMs.' --output outputs/evoscientist_table1_queries/internagent/query_22.md`
- Query 23 (Code LLM evaluation): `python launch.py --mode qa --question 'Generate a research proposal on how to build a deep evaluation framework for code LLMs.' --output outputs/evoscientist_table1_queries/internagent/query_23.md`
- Query 24 (RAG): `python launch.py --mode qa --question 'Generate a research proposal on solving multi-hop reasoning challenges in Retrieval-Augmented Generation (RAG).' --output outputs/evoscientist_table1_queries/internagent/query_24.md`
- Query 25 (Multi-source reasoning): `python launch.py --mode qa --question 'Generate a research proposal on complex reasoning with multi-source information.' --output outputs/evoscientist_table1_queries/internagent/query_25.md`
- Query 26 (Data filtering): `python launch.py --mode qa --question 'Generate a research proposal on solving data filtering challenges for domain-specific models.' --output outputs/evoscientist_table1_queries/internagent/query_26.md`
- Query 27 (Long-context understanding): `python launch.py --mode qa --question 'Generate a research proposal on how to enhance the long-context understanding of Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_27.md`
- Query 28 (Alignment): `python launch.py --mode qa --question 'Generate a research proposal on cross-cultural alignment for Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_28.md`
- Query 29 (Alignment): `python launch.py --mode qa --question 'Generate a research proposal on value alignment for AI agents.' --output outputs/evoscientist_table1_queries/internagent/query_29.md`
- Query 30 (Audio foundation models): `python launch.py --mode qa --question 'Help me generate a research proposal on general-purpose audio foundation models.' --output outputs/evoscientist_table1_queries/internagent/query_30.md`
