#!/usr/bin/env python3
"""Build AI-Researcher benchmark-instance templates for the 30 recovered queries."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = ROOT / "ai_researcher_adapter_runbook"
DEFAULT_CHECKOUT = "$HOME/research/AI-Researcher"


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def q(value: str) -> str:
    return shlex.quote(value)


def template_for_query(item: dict[str, Any]) -> dict[str, Any]:
    task = (
        "Generate a concise, feasible, and novel machine-learning research proposal "
        "for the recovered EvoScientist Table 1 evaluation query. The answer should "
        "include a concrete hypothesis, related-work distinction, experimental plan, "
        "evaluation metrics, and limitations.\n\n"
        f"Topic: {item['topic']}\n"
        f"Goal: {item['goal']}"
    )
    return {
        "url": "https://arxiv.org/abs/2603.08127",
        "source_papers": [
            {
                "reference": "EvoScientist: Towards Systematic Evaluation of Automated Scientific Discovery Agents",
                "usage": (
                    "Use this recovered query as the target task. Do not assume access "
                    "to the paper authors' private baseline outputs."
                ),
            }
        ],
        "task1": task,
        "task_instructions": task,
        "adapter_metadata": {
            "query_id": item["id"],
            "topic": item["topic"],
            "paper_exact": False,
            "source": "reproduction/queries.json",
        },
    }


def build_runbook(args: argparse.Namespace) -> dict[str, Any]:
    queries = load_queries()
    output_root = args.output_root
    benchmark_dir = output_root / "benchmark_instances"
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    commands = []
    for item in queries:
        instance_path = benchmark_dir / f"query_{item['id']:02d}.json"
        instance_path.write_text(json.dumps(template_for_query(item), indent=2), encoding="utf-8")
        external_instance_path = (
            f"{args.external_checkout.rstrip('/')}/benchmark/final/evoscientist/query_{item['id']:02d}.json"
        )
        command = (
            "CATEGORY=evoscientist "
            f"INSTANCE_ID=query_{item['id']:02d} "
            "TASK_LEVEL=task1 "
            "CONTAINER_NAME=paper_eval "
            "WORKPLACE_NAME=workplace "
            "CACHE_PATH=cache "
            f"PORT={args.port + item['id']} "
            f"MAX_ITER_TIMES={args.max_iter_times} "
            "python main_ai_researcher.py"
        )
        commands.append(
            {
                "query_id": item["id"],
                "topic": item["topic"],
                "local_instance_path": str(instance_path),
                "external_instance_path": external_instance_path,
                "command": command,
            }
        )
    return {
        "date": "2026-06-04",
        "baseline": "AI-Researcher",
        "mode": "benchmark_instance_adapter_templates",
        "paper_exact": False,
        "source_probe": "reproduction/ai_researcher_baseline_probe.json",
        "query_count": len(commands),
        "external_checkout": args.external_checkout,
        "benchmark_dir": str(benchmark_dir),
        "copy_command": (
            f"mkdir -p {args.external_checkout.rstrip()}/benchmark/final/evoscientist && "
            f"cp {benchmark_dir}/query_*.json {args.external_checkout.rstrip()}/benchmark/final/evoscientist/"
        ),
        "commands": commands,
        "import_command": (
            ".venv/bin/python reproduction/import_baseline_outputs.py "
            "--system-name AI-Researcher "
            f"--source {args.external_checkout.rstrip('/')}/outputs/evoscientist_table1_queries/ai_researcher "
            "--source-format directory "
            "--output-root reproduction/artifacts/idea_outputs "
            "--strict"
        ),
        "next_commands_after_import": [
            ".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline AI-Researcher --output reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl",
            ".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --resume",
            ".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json",
            ".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline AI-Researcher --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_researcher.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_researcher_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_researcher_deepseek.json",
        ],
        "caveat": (
            "These are adapter templates for a replacement rerun. They are not "
            "AI-Researcher's original paper Table 1 raw outputs."
        ),
    }


def render_markdown(runbook: dict[str, Any]) -> str:
    lines = [
        "# AI-Researcher Adapter Runbook",
        "",
        f"Date: {runbook['date']}",
        f"Queries: {runbook['query_count']}",
        f"Paper-exact: `{str(runbook['paper_exact']).lower()}`",
        "",
        runbook["caveat"],
        "",
        "## Benchmark Instance Templates",
        "",
        f"Template directory: `{runbook['benchmark_dir']}`",
        "",
        "```bash",
        runbook["copy_command"],
        "```",
        "",
        "## Environment",
        "",
        "AI-Researcher requires at least `OPENROUTER_API_KEY`, `GITHUB_AI_TOKEN`, Docker, and the repository-specific benchmark/runtime dependencies.",
        "",
        "## Commands",
        "",
    ]
    for item in runbook["commands"]:
        lines.append(f"- Query {item['query_id']:02d} ({item['topic']}): `{item['command']}`")
    lines.extend(
        [
            "",
            "## Import And Judge",
            "",
            "```bash",
            runbook["import_command"],
            *runbook["next_commands_after_import"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--external-checkout", default=DEFAULT_CHECKOUT)
    parser.add_argument("--port", type=int, default=12345)
    parser.add_argument("--max-iter-times", type=int, default=0)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    runbook = build_runbook(args)
    json_path = args.output_root / "ai_researcher_adapter_runbook.json"
    md_path = args.output_root / "ai_researcher_adapter_runbook.md"
    json_path.write_text(json.dumps(runbook, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(runbook), encoding="utf-8")
    print(json.dumps({"baseline": runbook["baseline"], "query_count": runbook["query_count"], "output_root": str(args.output_root)}, indent=2))


if __name__ == "__main__":
    main()
