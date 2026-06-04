#!/usr/bin/env python3
"""Build an executable rerun manifest for Table 1 replacement baselines."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "baseline_rerun_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "baseline_rerun_manifest.md"


PREP_COMMANDS: dict[str, list[str]] = {
    "Virtual Scientist": [
        "git clone https://github.com/open-sciencelab/Virtual-Scientists $HOME/research/Virtual-Scientists",
        "# Download the AMiner-derived Papers, Embeddings, Authors, and adjacency data linked in the VirSci README.",
        "# Patch sci_platform/sci_platform.py paths and run Ollama llama3.1/mxbai-embed-large.",
        "# Extract generated idea/abstract fields from team_info/*_dialogue.json into outputs/evoscientist_table1_queries/virtual_scientist/query_XX.md.",
    ],
    "AI-Researcher": [
        "git clone https://github.com/HKUDS/AI-Researcher $HOME/research/AI-Researcher",
        "# Configure CATEGORY, INSTANCE_ID, TASK_LEVEL, Docker/workplace, and a pinned adapter from each recovered query.",
    ],
    "InternAgent": [
        ".venv/bin/python reproduction/build_internagent_qa_runbook.py",
        "bash /path/to/EvoScientist/reproduction/internagent_qa_runbook.sh",
    ],
    "AI Scientist-v2": [
        ".venv/bin/python reproduction/build_ai_scientist_v2_ideation_runbook.py",
        "bash /path/to/EvoScientist/reproduction/ai_scientist_v2_ideation_runbook/run_ai_scientist_v2_ideation.sh",
        ".venv/bin/python reproduction/convert_ai_scientist_v2_ideation_outputs.py",
    ],
    "Hypogenic": [
        "# With Hypogenic account access: open https://hypogenic.ai/chat under a pinned browser/profile state.",
        "# Submit one recovered query per fresh Assistant session and capture the final answer plus session metadata.",
        "# Save outputs as $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_XX.md.",
    ],
    "Novix": [
        "# With Novix account access: open https://novix.science/chat under a pinned browser/profile state.",
        "# Submit one recovered query per fresh session and capture the final assistant answer plus session metadata.",
        "# Save outputs as $HOME/research/novix/outputs/evoscientist_table1_queries/novix/query_XX.md.",
    ],
    "K-Dense": [
        "git clone https://github.com/K-Dense-AI/k-dense-byok $HOME/research/k-dense-byok && cd $HOME/research/k-dense-byok && git checkout 593c49b8e79c704c5979ec81c49f1791b5114083",
        "./start.sh",
        "# In a separate adapter process: create one ADK session per query, POST each query to /run_sse, and save final assistant text as outputs/evoscientist_table1_queries/k_dense/query_XX.md.",
    ],
}

SOURCE_DIRS = {
    "Virtual Scientist": "$HOME/research/Virtual-Scientists/outputs/evoscientist_table1_queries/virtual_scientist",
    "AI-Researcher": "$HOME/research/AI-Researcher/outputs/evoscientist_table1_queries/ai_researcher",
    "InternAgent": "$HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent",
    "AI Scientist-v2": "reproduction/ai_scientist_v2_ideation_import_template.jsonl",
    "Hypogenic": "$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic",
    "Novix": "$HOME/research/novix/outputs/evoscientist_table1_queries/novix",
    "K-Dense": "$HOME/research/k-dense-byok/outputs/evoscientist_table1_queries/k_dense",
}


def slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def quote(name: str) -> str:
    return shlex.quote(name)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def import_command(name: str) -> str:
    source = SOURCE_DIRS[name]
    source_format = "jsonl" if source.endswith(".jsonl") else "directory"
    return (
        ".venv/bin/python reproduction/import_baseline_outputs.py "
        f"--system-name {quote(name)} --source {source} --source-format {source_format} "
        "--output-root reproduction/artifacts/idea_outputs --strict"
    )


def judge_commands(name: str) -> list[str]:
    baseline = quote(name)
    baseline_slug = slug(name)
    return [
        (
            ".venv/bin/python reproduction/build_pairwise_judge_inputs.py "
            f"--systems-root reproduction/artifacts/idea_outputs --baseline {baseline} "
            f"--output reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl"
        ),
        (
            ".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash "
            f"--input reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl "
            f"--output reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl --resume"
        ),
        (
            ".venv/bin/python reproduction/aggregate_judge_results.py "
            f"--input reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl "
            f"--output-csv reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.csv "
            f"--output-json reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.json"
        ),
        (
            ".venv/bin/python reproduction/audit_reproduction_artifacts.py "
            f"--baseline {baseline} "
            f"--judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl "
            f"--judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl "
            f"--aggregate-json reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.json"
        ),
    ]


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    readiness = load_json(args.readiness_matrix)
    entries = []
    for row in readiness["rows"]:
        name = row["baseline"]
        entries.append(
            {
                "baseline": name,
                "readiness_class": row["readiness_class"],
                "probe": row["probe"],
                "paper_exact": False,
                "requires_adapter": row["readiness_class"] == "replacement_adapter_required",
                "prep_commands": PREP_COMMANDS[name],
                "import_command": import_command(name),
                "judge_commands": judge_commands(name),
                "acceptance_gate": judge_commands(name)[-1],
            }
        )
    all_baselines = " ".join(f"--baseline {quote(entry['baseline'])}" for entry in entries)
    return {
        "date": args.date,
        "paper": "arXiv:2603.08127",
        "purpose": "Executable queue for replacement Table 1 baseline reruns.",
        "scope_note": "Replacement-only unless author-provided paper baseline outputs and Gemini-3-flash judge records are imported.",
        "query_set": "reproduction/queries.json",
        "baseline_count": len(entries),
        "entries": entries,
        "combined_paper_exact_judge_commands": [
            (
                ".venv/bin/python reproduction/build_pairwise_judge_inputs.py "
                f"--systems-root reproduction/artifacts/idea_outputs {all_baselines} "
                "--output reproduction/artifacts/judge_inputs/results.jsonl"
            ),
            (
                ".venv/bin/python reproduction/run_llm_judge.py --provider google --model gemini-3-flash "
                "--input reproduction/artifacts/judge_inputs/results.jsonl "
                "--output reproduction/artifacts/judge_outputs/results.jsonl --resume"
            ),
            (
                ".venv/bin/python reproduction/aggregate_judge_results.py "
                "--input reproduction/artifacts/judge_outputs/results.jsonl "
                "--output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv "
                "--output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json"
            ),
        ],
        "final_gate": ".venv/bin/python reproduction/audit_paper_level_completion.py --strict",
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Baseline Rerun Manifest",
        "",
        f"Date: {manifest['date']}",
        f"Paper: {manifest['paper']}",
        "",
        manifest["scope_note"],
        "",
        "## Baselines",
        "",
    ]
    for entry in manifest["entries"]:
        lines.extend(
            [
                f"### {entry['baseline']}",
                "",
                f"Readiness: `{entry['readiness_class']}`",
                f"Requires adapter: {entry['requires_adapter']}",
                f"Probe: `{entry['probe']}`",
                "",
                "Commands:",
                "",
                "```bash",
            ]
        )
        lines.extend(entry["prep_commands"])
        lines.append(entry["import_command"])
        lines.extend(entry["judge_commands"])
        lines.extend(["```", ""])
    lines.extend(["## Combined Paper-Exact Judge Commands", "", "```bash"])
    lines.extend(manifest["combined_paper_exact_judge_commands"])
    lines.extend(["```", "", "## Final Gate", "", "```bash", manifest["final_gate"], "```", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness-matrix", type=Path, default=ROOT / "baseline_readiness_matrix.json")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--date", default="2026-06-04")
    args = parser.parse_args()

    manifest = build_manifest(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(manifest), encoding="utf-8")
    print(json.dumps({
        "baseline_count": manifest["baseline_count"],
        "entries": [entry["baseline"] for entry in manifest["entries"]],
    }, indent=2))


if __name__ == "__main__":
    main()
