# AI Scientist-v2 Ideation Replacement-Baseline Runbook

Date: 2026-06-04
Queries: 30
Paper-exact: `false`

This runbook generates replacement-baseline ideas through AI Scientist-v2 ideation. It does not recover the paper's original raw AI Scientist-v2 Table 1 outputs.

## External Checkout Setup

```bash
git clone https://github.com/SakanaAI/AI-Scientist-v2.git $HOME/research/AI-Scientist-v2
cd $HOME/research/AI-Scientist-v2
conda create -n ai_scientist python=3.11
conda activate ai_scientist
pip install -r requirements.txt
```

## Run Ideation

Copy the generated topic markdown files into the external checkout, then run:

```bash
bash /path/to/EvoScientist/reproduction/ai_scientist_v2_ideation_runbook/run_ai_scientist_v2_ideation.sh
```

## Convert And Import Outputs

Run from the EvoScientist checkout after ideation JSON files exist:

```bash
python - <<'PY'
import json
import os
from pathlib import Path
generated_root = Path(os.path.expandvars('$HOME/research/AI-Scientist-v2/ai_scientist/ideas')).expanduser()
output = Path('/Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/ai_scientist_v2_ideation_import_template.jsonl')
output.parent.mkdir(parents=True, exist_ok=True)
rows = []
for path in sorted(generated_root.glob('query_*.json')):
    qid = int(path.stem.split('_')[1])
    ideas = json.loads(path.read_text())
    if not ideas:
        continue
    idea = ideas[0]
    answer = '\n\n'.join([
        f"# {idea.get('Title', idea.get('Name', 'AI Scientist-v2 idea'))}",
        f"Short Hypothesis: {idea.get('Short Hypothesis', '')}",
        f"Related Work: {idea.get('Related Work', '')}",
        f"Abstract: {idea.get('Abstract', '')}",
        f"Experiments: {idea.get('Experiments', '')}",
        f"Risk Factors and Limitations: {idea.get('Risk Factors and Limitations', '')}",
    ])
    rows.append({'query_id': qid, 'answer': answer, 'prompt': (generated_root / f'query_{qid:02d}.md').read_text()})
with output.open('w', encoding='utf-8') as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
print(json.dumps({'written': len(rows), 'output': str(output)}, indent=2))
PY
.venv/bin/python reproduction/import_baseline_outputs.py --system-name 'AI Scientist-v2' --source /Users/hgh54913/.codex/worktrees/d70a/cp4106/EvoScientist/reproduction/ai_scientist_v2_ideation_import_template.jsonl --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict
```

## Judge And Audit

```bash
.venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'AI Scientist-v2' --output reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl
.venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --resume
.venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
.venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'AI Scientist-v2' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json
```

## Command List

- Query 01 (Machine translation): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_01.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 02 (Software engineering): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_02.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 03 (LLM evaluation): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_03.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 04 (Healthcare agents): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_04.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 05 (Literature review automation): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_05.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 06 (Speech recognition): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_06.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 07 (Model efficiency): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_07.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 08 (AI agents): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_08.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 09 (Model deployment): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_09.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 10 (Text-to-SQL): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_10.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 11 (LLM capabilities): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_11.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 12 (Factual consistency): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_12.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 13 (Data synthesis): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_13.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 14 (Inference efficiency): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_14.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 15 (Machine translation): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_15.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 16 (Knowledge injection): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_16.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 17 (Information extraction): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_17.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 18 (UX evaluation): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_18.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 19 (Evaluation leaderboards): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_19.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 20 (Text generation): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_20.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 21 (Content detection): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_21.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 22 (Code LLM security): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_22.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 23 (Code LLM evaluation): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_23.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 24 (RAG): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_24.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 25 (Multi-source reasoning): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_25.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 26 (Data filtering): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_26.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 27 (Long-context understanding): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_27.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 28 (Alignment): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_28.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 29 (Alignment): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_29.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
- Query 30 (Audio foundation models): `python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/query_30.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5`
