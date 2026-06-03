#!/usr/bin/env python3
"""Build a 30-query InternAgent QA replacement-baseline runbook."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_QUERIES = ROOT / "queries.json"
DEFAULT_OUTPUT_JSON = ROOT / "internagent_qa_runbook.json"
DEFAULT_OUTPUT_MD = ROOT / "internagent_qa_runbook.md"
DEFAULT_OUTPUT_SH = ROOT / "internagent_qa_runbook.sh"


def load_queries(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["queries"]


def q(value: str) -> str:
    return shlex.quote(value)


def build_runbook(args: argparse.Namespace) -> dict[str, Any]:
    queries = load_queries(args.queries)
    external_answers_dir = f"{args.external_checkout.rstrip('/')}/{args.answers_dir}"
    commands = []
    for item in queries[: args.limit] if args.limit else queries:
        answer_path = f"{args.answers_dir}/query_{item['id']:02d}.md"
        command = (
            "python launch.py --mode qa "
            f"--question {q(item['goal'])} "
            f"--output {q(answer_path)}"
        )
        commands.append(
            {
                "query_id": item["id"],
                "topic": item["topic"],
                "goal": item["goal"],
                "answer_path": answer_path,
                "command": command,
            }
        )
    return {
        "date": "2026-06-04",
        "baseline": "InternAgent",
        "mode": "qa_replacement_baseline",
        "paper_exact": False,
        "source_probe": "reproduction/internagent_baseline_probe.json",
        "query_count": len(commands),
        "external_checkout": args.external_checkout,
        "answers_dir": args.answers_dir,
        "external_answers_dir": external_answers_dir,
        "commands": commands,
        "import_command": (
            ".venv/bin/python reproduction/import_baseline_outputs.py "
            "--system-name InternAgent "
            f"--source {external_answers_dir} "
            "--source-format directory "
            "--output-root reproduction/artifacts/idea_outputs "
            "--strict"
        ),
        "next_commands_after_import": [
            ".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --output reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl",
            ".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --resume",
            ".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_deepseek.json",
            ".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_deepseek.json",
        ],
        "caveat": (
            "This runbook generates replacement-baseline answers through InternAgent QA mode. "
            "It does not recover the paper's original raw InternAgent Table 1 outputs."
        ),
    }


def render_markdown(runbook: dict[str, Any]) -> str:
    lines = [
        "# InternAgent QA Replacement-Baseline Runbook",
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
        f"git clone https://github.com/InternScience/InternAgent.git {runbook['external_checkout']}",
        f"cd {runbook['external_checkout']}",
        "conda create -n InternAgent python=3.11",
        "conda activate InternAgent",
        "pip install -r requirements.txt",
        "cp .env.example .env",
        "# Fill OPENAI_API_KEY and OPENAI_API_BASE_URL in .env before running.",
        "```",
        "",
        "## Run Queries",
        "",
        "Run from the external InternAgent checkout:",
        "",
        "```bash",
        "bash /path/to/EvoScientist/reproduction/internagent_qa_runbook.sh",
        "```",
        "",
        "## Import Outputs",
        "",
        "Run from the EvoScientist checkout:",
        "",
        "```bash",
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
        "# Run this script from the external InternAgent checkout.",
        f"mkdir -p {q(runbook['answers_dir'])}",
        "",
    ]
    for item in runbook["commands"]:
        lines.append(f"echo 'Running InternAgent query {item['query_id']:02d}: {item['topic']}'")
        lines.append(item["command"])
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-sh", type=Path, default=DEFAULT_OUTPUT_SH)
    parser.add_argument("--external-checkout", default="$HOME/research/InternAgent")
    parser.add_argument("--answers-dir", default="outputs/evoscientist_table1_queries/internagent")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    runbook = build_runbook(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_sh.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(runbook, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(runbook), encoding="utf-8")
    args.output_sh.write_text(render_shell(runbook), encoding="utf-8")
    args.output_sh.chmod(0o755)
    print(json.dumps({
        "baseline": runbook["baseline"],
        "mode": runbook["mode"],
        "query_count": runbook["query_count"],
        "output_sh": str(args.output_sh),
    }, indent=2))


if __name__ == "__main__":
    main()
