#!/usr/bin/env bash
set -euo pipefail

# Run this script from the external AI-Scientist-v2 checkout.

echo 'Running AI Scientist-v2 ideation query 01: Machine translation'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_01.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 02: Software engineering'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_02.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 03: LLM evaluation'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_03.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 04: Healthcare agents'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_04.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 05: Literature review automation'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_05.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 06: Speech recognition'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_06.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 07: Model efficiency'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_07.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 08: AI agents'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_08.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 09: Model deployment'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_09.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 10: Text-to-SQL'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_10.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 11: LLM capabilities'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_11.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 12: Factual consistency'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_12.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 13: Data synthesis'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_13.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 14: Inference efficiency'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_14.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 15: Machine translation'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_15.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 16: Knowledge injection'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_16.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 17: Information extraction'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_17.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 18: UX evaluation'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_18.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 19: Evaluation leaderboards'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_19.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 20: Text generation'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_20.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 21: Content detection'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_21.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 22: Code LLM security'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_22.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 23: Code LLM evaluation'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_23.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 24: RAG'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_24.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 25: Multi-source reasoning'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_25.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 26: Data filtering'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_26.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 27: Long-context understanding'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_27.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 28: Alignment'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_28.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 29: Alignment'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_29.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5

echo 'Running AI Scientist-v2 ideation query 30: Audio foundation models'
python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_30.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5
