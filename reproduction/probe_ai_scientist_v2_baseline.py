#!/usr/bin/env python3
"""Probe AI Scientist-v2 as an EvoScientist Table 1 baseline candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "ai_scientist_v2_baseline_probe.json"
DEFAULT_OUTPUT_MD = ROOT / "ai_scientist_v2_baseline_probe.md"
REPO_API = "https://api.github.com/repos/SakanaAI/AI-Scientist-v2"
RAW_BASE = "https://raw.githubusercontent.com/SakanaAI/AI-Scientist-v2/main"


def fetch_text(url: str, timeout: int) -> str:
    with urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str, timeout: int) -> Any:
    return json.loads(fetch_text(url, timeout))


def build_probe(timeout: int) -> dict[str, Any]:
    head = fetch_json(f"{REPO_API}/git/ref/heads/main", timeout)
    tree = fetch_json(f"{REPO_API}/git/trees/main?recursive=1", timeout)
    paths = {item["path"] for item in tree.get("tree", [])}
    readme = fetch_text(f"{RAW_BASE}/README.md", timeout)
    ideation = fetch_text(f"{RAW_BASE}/ai_scientist/perform_ideation_temp_free.py", timeout)
    example_topic = fetch_text(f"{RAW_BASE}/ai_scientist/ideas/i_cant_believe_its_not_better.md", timeout)

    ideation_cli_available = all(
        needle in ideation
        for needle in ["--workshop-file", "--model", "--max-num-generations", "--num-reflections"]
    )
    structured_idea_output = all(
        needle in ideation
        for needle in ["FinalizeIdea", '"Title"', '"Abstract"', '"Experiments"', "idea_fname"]
    )
    topic_markdown_template = all(
        needle in example_topic
        for needle in ["# Title:", "## Keywords", "## TL;DR", "## Abstract"]
    )
    full_pipeline_available = "launch_scientist_bfts.py" in paths and "bfts_config.yaml" in paths
    required_paths = [
        "README.md",
        "ai_scientist/perform_ideation_temp_free.py",
        "ai_scientist/ideas/i_cant_believe_its_not_better.md",
        "launch_scientist_bfts.py",
        "requirements.txt",
        "bfts_config.yaml",
    ]
    missing_paths = [path for path in required_paths if path not in paths]

    return {
        "date": "2026-06-04",
        "baseline": "AI Scientist-v2",
        "source": "https://github.com/SakanaAI/AI-Scientist-v2",
        "checked_head": head.get("object", {}).get("sha", ""),
        "files_checked": [
            "README.md",
            "ai_scientist/perform_ideation_temp_free.py",
            "ai_scientist/ideas/i_cant_believe_its_not_better.md",
            "repository file tree",
        ],
        "direct_30_query_runner_available": ideation_cli_available and structured_idea_output,
        "evo_table1_drop_in_status": "ideation_adapter_candidate",
        "paper_exact_status": "not_paper_exact",
        "signals": {
            "ideation_cli_available": ideation_cli_available,
            "structured_idea_output": structured_idea_output,
            "topic_markdown_template": topic_markdown_template,
            "full_pipeline_available": full_pipeline_available,
            "requires_linux_cuda_for_full_pipeline": "Linux with NVIDIA GPUs" in readme,
            "semantic_scholar_used_for_novelty": "Semantic Scholar" in readme,
            "missing_required_paths": missing_paths,
        },
        "entrypoints": {
            "ideation": "python ai_scientist/perform_ideation_temp_free.py --workshop-file ai_scientist/ideas/my_research_topic.md --model gpt-4o-2024-05-13 --max-num-generations 1 --num-reflections 5",
            "full_pipeline": "python launch_scientist_bfts.py --load_ideas ai_scientist/ideas/my_research_topic.json ...",
        },
        "required_env": ["OPENAI_API_KEY or GEMINI_API_KEY", "S2_API_KEY optional for Semantic Scholar"],
        "reproduction_implication": (
            "AI Scientist-v2 has a usable ideation CLI that can be adapted to the "
            "30 recovered EvoScientist queries by writing one topic markdown file "
            "per query and importing the resulting JSON idea as baseline output. "
            "This is a replacement-baseline rerun path, not the paper's raw AI "
            "Scientist-v2 Table 1 artifact."
        ),
        "next_actions": [
            "Generate per-query topic markdown files from reproduction/queries.json.",
            "Run perform_ideation_temp_free.py once per query with a pinned model and reflection budget.",
            "Convert each generated JSON idea file into query_XX.md or JSONL records accepted by import_baseline_outputs.py.",
            "Judge imported outputs through the existing swapped pairwise judge pipeline.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI Scientist-v2 Baseline Probe",
        "",
        f"Date: {report['date']}",
        f"Source: {report['source']}",
        f"Checked HEAD: `{report['checked_head']}`",
        "",
        f"Drop-in status: `{report['evo_table1_drop_in_status']}`",
        f"Paper-exact status: `{report['paper_exact_status']}`",
        "",
        "## Finding",
        "",
        report["reproduction_implication"],
        "",
        "## Signals",
        "",
    ]
    for key, value in report["signals"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Entrypoints", ""])
    for key, value in report["entrypoints"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Required Environment", ""])
    for item in report["required_env"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Next Actions", ""])
    for item in report["next_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    report = build_probe(args.timeout)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({
        "baseline": report["baseline"],
        "status": report["evo_table1_drop_in_status"],
        "checked_head": report["checked_head"],
    }, indent=2))


if __name__ == "__main__":
    main()
