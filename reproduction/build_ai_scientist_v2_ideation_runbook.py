#!/usr/bin/env python3
"""Build a 30-query AI Scientist-v2 ideation replacement-baseline runbook."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_QUERIES = ROOT / "queries.json"
DEFAULT_OUTPUT_ROOT = ROOT / "ai_scientist_v2_ideation_runbook"
DEFAULT_JSONL = ROOT / "ai_scientist_v2_ideation_import_template.jsonl"


def load_queries(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["queries"]


def q(value: str) -> str:
    return shlex.quote(value)


def topic_markdown(item: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Title: {item['topic']} Research Proposal",
            "",
            "## Keywords",
            item["topic"],
            "",
            "## TL;DR",
            item["goal"],
            "",
            "## Abstract",
            (
                "Generate a concise, feasible, and novel machine-learning research proposal "
                f"for this recovered EvoScientist evaluation query: {item['goal']} "
                "The output should include a concrete hypothesis, related work distinction, "
                "experimental plan, evaluation metrics, and limitations."
            ),
            "",
        ]
    )


def render_import_converter(output_jsonl: str, generated_root: str) -> str:
    return "\n".join(
        [
            "python - <<'PY'",
            "import json",
            "import os",
            "from pathlib import Path",
            f"generated_root = Path(os.path.expandvars({generated_root!r})).expanduser()",
            f"output = Path({output_jsonl!r})",
            "output.parent.mkdir(parents=True, exist_ok=True)",
            "rows = []",
            "for path in sorted(generated_root.glob('query_*.json')):",
            "    qid = int(path.stem.split('_')[1])",
            "    ideas = json.loads(path.read_text())",
            "    if not ideas:",
            "        continue",
            "    idea = ideas[0]",
            "    answer = '\\n\\n'.join([",
            "        f\"# {idea.get('Title', idea.get('Name', 'AI Scientist-v2 idea'))}\",",
            "        f\"Short Hypothesis: {idea.get('Short Hypothesis', '')}\",",
            "        f\"Related Work: {idea.get('Related Work', '')}\",",
            "        f\"Abstract: {idea.get('Abstract', '')}\",",
            "        f\"Experiments: {idea.get('Experiments', '')}\",",
            "        f\"Risk Factors and Limitations: {idea.get('Risk Factors and Limitations', '')}\",",
            "    ])",
            "    rows.append({'query_id': qid, 'answer': answer, 'prompt': (generated_root / f'query_{qid:02d}.md').read_text()})",
            "with output.open('w', encoding='utf-8') as f:",
            "    for row in rows:",
            "        f.write(json.dumps(row, ensure_ascii=False) + '\\n')",
            "print(json.dumps({'written': len(rows), 'output': str(output)}, indent=2))",
            "PY",
        ]
    )


def build_runbook(args: argparse.Namespace) -> dict[str, Any]:
    queries = load_queries(args.queries)
    selected = queries[: args.limit] if args.limit else queries
    topic_dir = args.output_root / "topics"
    topic_dir.mkdir(parents=True, exist_ok=True)
    commands = []
    for item in selected:
        topic_path = topic_dir / f"query_{item['id']:02d}.md"
        topic_path.write_text(topic_markdown(item), encoding="utf-8")
        external_topic = f"ai_scientist/ideas/query_{item['id']:02d}.md"
        command = (
            "python ai_scientist/perform_ideation_temp_free.py "
            f"--workshop-file {q(external_topic)} "
            f"--model {q(args.model)} "
            f"--max-num-generations {args.max_num_generations} "
            f"--num-reflections {args.num_reflections}"
        )
        commands.append(
            {
                "query_id": item["id"],
                "topic": item["topic"],
                "goal": item["goal"],
                "local_topic_path": str(topic_path),
                "external_topic_path": f"{args.external_checkout.rstrip('/')}/{external_topic}",
                "external_json_path": f"{args.external_checkout.rstrip('/')}/{external_topic.replace('.md', '.json')}",
                "command": command,
            }
        )
    generated_root = f"{args.external_checkout.rstrip('/')}/ai_scientist/ideas"
    return {
        "date": "2026-06-04",
        "baseline": "AI Scientist-v2",
        "mode": "ideation_replacement_baseline",
        "paper_exact": False,
        "source_probe": "reproduction/ai_scientist_v2_baseline_probe.json",
        "query_count": len(commands),
        "external_checkout": args.external_checkout,
        "model": args.model,
        "max_num_generations": args.max_num_generations,
        "num_reflections": args.num_reflections,
        "topic_dir": str(topic_dir),
        "commands": commands,
        "copy_topics_command": f"cp {topic_dir}/query_*.md {args.external_checkout.rstrip('/')}/ai_scientist/ideas/",
        "rename_topics_note": "Copied files are named query_XX.md and produce query_XX.json outputs.",
        "jsonl_converter": render_import_converter(str(args.output_jsonl), generated_root),
        "import_command": (
            ".venv/bin/python reproduction/import_baseline_outputs.py "
            "--system-name 'AI Scientist-v2' "
            f"--source {args.output_jsonl} "
            "--source-format jsonl "
            "--output-root reproduction/artifacts/idea_outputs "
            "--strict"
        ),
        "next_commands_after_import": [
            ".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'AI Scientist-v2' --output reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl",
            ".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --resume",
            ".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json",
            ".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'AI Scientist-v2' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json",
        ],
        "caveat": (
            "This runbook generates replacement-baseline ideas through AI Scientist-v2 ideation. "
            "It does not recover the paper's original raw AI Scientist-v2 Table 1 outputs."
        ),
    }


def render_markdown(runbook: dict[str, Any]) -> str:
    lines = [
        "# AI Scientist-v2 Ideation Replacement-Baseline Runbook",
        "",
        f"Date: {runbook['date']}",
        f"Queries: {runbook['query_count']}",
        f"Paper-exact: `{str(runbook['paper_exact']).lower()}`",
        "",
        runbook["caveat"],
        "",
        "## External Checkout Setup",
        "",
        "```bash",
        f"git clone https://github.com/SakanaAI/AI-Scientist-v2.git {runbook['external_checkout']}",
        f"cd {runbook['external_checkout']}",
        "conda create -n ai_scientist python=3.11",
        "conda activate ai_scientist",
        "pip install -r requirements.txt",
        "```",
        "",
        "## Run Ideation",
        "",
        "Copy the generated topic markdown files into the external checkout, then run:",
        "",
        "```bash",
        "bash /path/to/EvoScientist/reproduction/ai_scientist_v2_ideation_runbook/run_ai_scientist_v2_ideation.sh",
        "```",
        "",
        "## Convert And Import Outputs",
        "",
        "Run from the EvoScientist checkout after ideation JSON files exist:",
        "",
        "```bash",
        runbook["jsonl_converter"],
        runbook["import_command"],
        "```",
        "",
        "## Judge And Audit",
        "",
        "```bash",
    ]
    lines.extend(runbook["next_commands_after_import"])
    lines.extend(["```", "", "## Command List", ""])
    for item in runbook["commands"]:
        lines.append(f"- Query {item['query_id']:02d} ({item['topic']}): `{item['command']}`")
    lines.append("")
    return "\n".join(lines)


def render_shell(runbook: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Run this script from the external AI-Scientist-v2 checkout.",
        "",
    ]
    for item in runbook["commands"]:
        lines.append(f"echo 'Running AI Scientist-v2 ideation query {item['query_id']:02d}: {item['topic']}'")
        lines.append(item["command"])
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--external-checkout", default="$HOME/research/AI-Scientist-v2")
    parser.add_argument("--model", default="gpt-4o-2024-05-13")
    parser.add_argument("--max-num-generations", type=int, default=1)
    parser.add_argument("--num-reflections", type=int, default=5)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    runbook = build_runbook(args)
    args.output_root.mkdir(parents=True, exist_ok=True)
    json_path = args.output_root / "ai_scientist_v2_ideation_runbook.json"
    md_path = args.output_root / "ai_scientist_v2_ideation_runbook.md"
    sh_path = args.output_root / "run_ai_scientist_v2_ideation.sh"
    json_path.write_text(json.dumps(runbook, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(runbook), encoding="utf-8")
    sh_path.write_text(render_shell(runbook), encoding="utf-8")
    sh_path.chmod(0o755)
    print(json.dumps({
        "baseline": runbook["baseline"],
        "mode": runbook["mode"],
        "query_count": runbook["query_count"],
        "output_root": str(args.output_root),
    }, indent=2))


if __name__ == "__main__":
    main()
