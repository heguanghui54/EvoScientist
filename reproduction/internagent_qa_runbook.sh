#!/usr/bin/env bash
set -euo pipefail

# Run this script from the external InternAgent checkout.
mkdir -p outputs/evoscientist_table1_queries/internagent

echo 'Running InternAgent query 01: Machine translation'
python launch.py --mode qa --question 'Generate a research proposal on low-resource machine translation.' --output outputs/evoscientist_table1_queries/internagent/query_01.md

echo 'Running InternAgent query 02: Software engineering'
python launch.py --mode qa --question 'Help me generate a research proposal on AI for software engineering.' --output outputs/evoscientist_table1_queries/internagent/query_02.md

echo 'Running InternAgent query 03: LLM evaluation'
python launch.py --mode qa --question 'Generate a research proposal on how to address the accuracy issues of automated evaluation for Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_03.md

echo 'Running InternAgent query 04: Healthcare agents'
python launch.py --mode qa --question 'Help me generate a research proposal on AI agents in healthcare.' --output outputs/evoscientist_table1_queries/internagent/query_04.md

echo 'Running InternAgent query 05: Literature review automation'
python launch.py --mode qa --question 'Generate a research proposal on automated literature review generation.' --output outputs/evoscientist_table1_queries/internagent/query_05.md

echo 'Running InternAgent query 06: Speech recognition'
python launch.py --mode qa --question 'Generate a research proposal on low-resource speech recognition.' --output outputs/evoscientist_table1_queries/internagent/query_06.md

echo 'Running InternAgent query 07: Model efficiency'
python launch.py --mode qa --question 'Generate a research proposal on how to break the performance ceiling of small models.' --output outputs/evoscientist_table1_queries/internagent/query_07.md

echo 'Running InternAgent query 08: AI agents'
python launch.py --mode qa --question 'Generate a research proposal on complex reasoning for AI agents.' --output outputs/evoscientist_table1_queries/internagent/query_08.md

echo 'Running InternAgent query 09: Model deployment'
python launch.py --mode qa --question 'Generate a research proposal on solving quantization challenges for LLM deployment on edge devices.' --output outputs/evoscientist_table1_queries/internagent/query_09.md

echo 'Running InternAgent query 10: Text-to-SQL'
python launch.py --mode qa --question 'Help me generate a research proposal on Text-to-SQL.' --output outputs/evoscientist_table1_queries/internagent/query_10.md

echo 'Running InternAgent query 11: LLM capabilities'
python launch.py --mode qa --question 'Generate a research proposal on the decoupling of Large Language Model capabilities.' --output outputs/evoscientist_table1_queries/internagent/query_11.md

echo 'Running InternAgent query 12: Factual consistency'
python launch.py --mode qa --question 'Generate a research proposal on how to resolve factual consistency issues in Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_12.md

echo 'Running InternAgent query 13: Data synthesis'
python launch.py --mode qa --question 'Generate a research proposal on data synthesis for code LLMs.' --output outputs/evoscientist_table1_queries/internagent/query_13.md

echo 'Running InternAgent query 14: Inference efficiency'
python launch.py --mode qa --question 'Generate a research proposal on solving inference latency issues in Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_14.md

echo 'Running InternAgent query 15: Machine translation'
python launch.py --mode qa --question 'Generate a research proposal on debiasing in machine translation.' --output outputs/evoscientist_table1_queries/internagent/query_15.md

echo 'Running InternAgent query 16: Knowledge injection'
python launch.py --mode qa --question 'Generate a research proposal on addressing the challenges of knowledge injection in domain-specific Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_16.md

echo 'Running InternAgent query 17: Information extraction'
python launch.py --mode qa --question 'Generate a research proposal on automated information extraction.' --output outputs/evoscientist_table1_queries/internagent/query_17.md

echo 'Running InternAgent query 18: UX evaluation'
python launch.py --mode qa --question 'Generate a research proposal on user experience evaluation for Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_18.md

echo 'Running InternAgent query 19: Evaluation leaderboards'
python launch.py --mode qa --question 'Generate a research proposal on how to construct efficient leaderboards for LLM evaluation.' --output outputs/evoscientist_table1_queries/internagent/query_19.md

echo 'Running InternAgent query 20: Text generation'
python launch.py --mode qa --question 'Generate a research proposal on the evaluation of diversity in text generation.' --output outputs/evoscientist_table1_queries/internagent/query_20.md

echo 'Running InternAgent query 21: Content detection'
python launch.py --mode qa --question 'Generate a research proposal on how to address false positives in AI-generated content detection.' --output outputs/evoscientist_table1_queries/internagent/query_21.md

echo 'Running InternAgent query 22: Code LLM security'
python launch.py --mode qa --question 'Generate a research proposal on the security of code LLMs.' --output outputs/evoscientist_table1_queries/internagent/query_22.md

echo 'Running InternAgent query 23: Code LLM evaluation'
python launch.py --mode qa --question 'Generate a research proposal on how to build a deep evaluation framework for code LLMs.' --output outputs/evoscientist_table1_queries/internagent/query_23.md

echo 'Running InternAgent query 24: RAG'
python launch.py --mode qa --question 'Generate a research proposal on solving multi-hop reasoning challenges in Retrieval-Augmented Generation (RAG).' --output outputs/evoscientist_table1_queries/internagent/query_24.md

echo 'Running InternAgent query 25: Multi-source reasoning'
python launch.py --mode qa --question 'Generate a research proposal on complex reasoning with multi-source information.' --output outputs/evoscientist_table1_queries/internagent/query_25.md

echo 'Running InternAgent query 26: Data filtering'
python launch.py --mode qa --question 'Generate a research proposal on solving data filtering challenges for domain-specific models.' --output outputs/evoscientist_table1_queries/internagent/query_26.md

echo 'Running InternAgent query 27: Long-context understanding'
python launch.py --mode qa --question 'Generate a research proposal on how to enhance the long-context understanding of Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_27.md

echo 'Running InternAgent query 28: Alignment'
python launch.py --mode qa --question 'Generate a research proposal on cross-cultural alignment for Large Language Models.' --output outputs/evoscientist_table1_queries/internagent/query_28.md

echo 'Running InternAgent query 29: Alignment'
python launch.py --mode qa --question 'Generate a research proposal on value alignment for AI agents.' --output outputs/evoscientist_table1_queries/internagent/query_29.md

echo 'Running InternAgent query 30: Audio foundation models'
python launch.py --mode qa --question 'Help me generate a research proposal on general-purpose audio foundation models.' --output outputs/evoscientist_table1_queries/internagent/query_30.md
