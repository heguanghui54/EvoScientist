#!/usr/bin/env python3
"""Build Virtual Scientist adapter templates for the 30 recovered queries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = ROOT / "virtual_scientist_adapter_runbook"
DEFAULT_CHECKOUT = "$HOME/research/Virtual-Scientists"


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def spec_for_query(item: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    prompt = (
        "Use the recovered EvoScientist Table 1 query as the scientific theme for "
        "a VirSci/Virtual Scientist collaboration simulation. The final extracted "
        "baseline answer should be a concise research proposal with hypothesis, "
        "related-work distinction, method, experiments, metrics, risks, and "
        "limitations.\n\n"
        f"Topic: {item['topic']}\n"
        f"Goal: {item['goal']}"
    )
    return {
        "query_id": item["id"],
        "topic": item["topic"],
        "goal": item["goal"],
        "simulation_prompt": prompt,
        "paper_exact": False,
        "adapter": {
            "source": "reproduction/queries.json",
            "target_platform": "open-sciencelab/Virtual-Scientists",
            "team_limit": args.team_limit,
            "max_discuss_iteration": args.max_discuss_iteration,
            "max_team_member": args.max_team_member,
            "epochs": args.epochs,
            "runs": args.runs,
            "extraction_rule": (
                "After sci_platform/run.py completes, inspect team_info/*_dialogue.json "
                "and extract the final idea/proposal/abstract-bearing assistant message. "
                "Save exactly one final answer as query_XX.md before importing."
            ),
        },
        "caveat": (
            "This is a replacement-baseline adapter spec. It is not the original "
            "Virtual Scientist raw output used by the EvoScientist paper."
        ),
    }


def build_runbook(args: argparse.Namespace) -> dict[str, Any]:
    queries = load_queries()
    output_root = args.output_root
    spec_dir = output_root / "simulation_specs"
    spec_dir.mkdir(parents=True, exist_ok=True)
    commands = []
    checkout = args.external_checkout.rstrip("/")
    for item in queries:
        spec_path = spec_dir / f"query_{item['id']:02d}.json"
        spec_path.write_text(
            json.dumps(spec_for_query(item, args), indent=2),
            encoding="utf-8",
        )
        external_spec = (
            f"{checkout}/outputs/evoscientist_table1_queries/virtual_scientist_specs/"
            f"query_{item['id']:02d}.json"
        )
        command = (
            "cd "
            f"{checkout}/sci_platform && "
            "python run.py "
            f"--runs {args.runs} "
            f"--team_limit {args.team_limit} "
            f"--max_discuss_iteration {args.max_discuss_iteration} "
            f"--max_team_member {args.max_team_member} "
            f"--epochs {args.epochs}"
        )
        commands.append(
            {
                "query_id": item["id"],
                "topic": item["topic"],
                "local_spec_path": str(spec_path),
                "external_spec_path": external_spec,
                "command": command,
                "expected_raw_dialogue_glob": (
                    f"{checkout}/sci_platform/team_info/*_dialogue.json"
                ),
                "expected_answer_path": (
                    f"{checkout}/outputs/evoscientist_table1_queries/"
                    f"virtual_scientist/query_{item['id']:02d}.md"
                ),
            }
        )
    return {
        "date": "2026-06-04",
        "baseline": "Virtual Scientist",
        "mode": "virtual_scientist_simulation_adapter_templates",
        "paper_exact": False,
        "source_probe": "reproduction/virtual_scientist_baseline_probe.json",
        "query_count": len(commands),
        "external_checkout": args.external_checkout,
        "spec_dir": str(spec_dir),
        "copy_command": (
            f"mkdir -p {checkout}/outputs/evoscientist_table1_queries/virtual_scientist_specs && "
            f"cp {spec_dir}/query_*.json "
            f"{checkout}/outputs/evoscientist_table1_queries/virtual_scientist_specs/"
        ),
        "setup_commands": [
            f"git clone https://github.com/open-sciencelab/Virtual-Scientists {checkout}",
            f"cd {checkout} && git checkout 07097fd67efd177dd6d5304684d3657dc3411bc1",
            f"cd {checkout} && pip install -r requirements.txt",
            f"cd {checkout}/agentscope-main && pip install -e .",
            "# Download the AMiner-derived Papers, Embeddings, Authors, and adjacency data linked in the VirSci README.",
            "# Patch sci_platform/sci_platform.py local data paths if the data package is not installed at the repository's expected paths.",
            "ollama serve",
            "ollama pull llama3.1",
            "ollama pull llama3.1:70b",
            "ollama pull mxbai-embed-large",
        ],
        "commands": commands,
        "import_command": (
            ".venv/bin/python reproduction/import_baseline_outputs.py "
            "--system-name 'Virtual Scientist' "
            f"--source {checkout}/outputs/evoscientist_table1_queries/virtual_scientist "
            "--source-format directory "
            "--output-root reproduction/artifacts/idea_outputs "
            "--strict"
        ),
        "next_commands_after_import": [
            ".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --output reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl",
            ".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --resume",
            ".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json",
            ".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'Virtual Scientist' --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_virtual_scientist.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_virtual_scientist_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_virtual_scientist_deepseek.json",
        ],
        "caveat": (
            "These are adapter templates for a replacement rerun. Virtual Scientist "
            "is a team-simulation platform, not a paper-exact 30-query runner, and "
            "the original EvoScientist Table 1 raw outputs are not public."
        ),
    }


def render_markdown(runbook: dict[str, Any]) -> str:
    lines = [
        "# Virtual Scientist Adapter Runbook",
        "",
        f"Date: {runbook['date']}",
        f"Queries: {runbook['query_count']}",
        f"Paper-exact: `{str(runbook['paper_exact']).lower()}`",
        "",
        runbook["caveat"],
        "",
        "## Simulation Specs",
        "",
        f"Spec directory: `{runbook['spec_dir']}`",
        "",
        "```bash",
        runbook["copy_command"],
        "```",
        "",
        "## Setup",
        "",
        "```bash",
        *runbook["setup_commands"],
        "```",
        "",
        "## Commands",
        "",
    ]
    for item in runbook["commands"]:
        lines.append(f"- Query {item['query_id']:02d} ({item['topic']}): `{item['command']}`")
    lines.extend(
        [
            "",
            "## Extract, Import, And Judge",
            "",
            "Extract the final idea/proposal/abstract-bearing message from "
            "`sci_platform/team_info/*_dialogue.json` and save one answer per query "
            "under the expected output directory before importing.",
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
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--team-limit", type=int, default=1)
    parser.add_argument("--max-discuss-iteration", type=int, default=3)
    parser.add_argument("--max-team-member", type=int, default=3)
    parser.add_argument("--epochs", type=int, default=1)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    runbook = build_runbook(args)
    json_path = args.output_root / "virtual_scientist_adapter_runbook.json"
    md_path = args.output_root / "virtual_scientist_adapter_runbook.md"
    json_path.write_text(json.dumps(runbook, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(runbook), encoding="utf-8")
    print(
        json.dumps(
            {
                "baseline": runbook["baseline"],
                "query_count": runbook["query_count"],
                "output_root": str(args.output_root),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
