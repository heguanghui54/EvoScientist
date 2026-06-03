#!/usr/bin/env python3
"""Probe the public AI-Researcher runner as an EvoScientist Table 1 baseline.

This script intentionally avoids cloning or installing the external repository.
It reads lightweight GitHub metadata and raw entrypoint files, then records
whether AI-Researcher can be used as a direct 30-query idea-generation runner.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "ai_researcher_baseline_probe.json"
DEFAULT_OUTPUT_MD = ROOT / "ai_researcher_baseline_probe.md"
REPO_API = "https://api.github.com/repos/hkuds/ai-researcher"
RAW_BASE = "https://raw.githubusercontent.com/HKUDS/AI-Researcher/main"


def fetch_text(url: str, timeout: int) -> str:
    with urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str, timeout: int) -> Any:
    return json.loads(fetch_text(url, timeout))


def contains_all(text: str, needles: list[str]) -> bool:
    return all(needle in text for needle in needles)


def build_probe(timeout: int) -> dict[str, Any]:
    head = fetch_json(f"{REPO_API}/git/ref/heads/main", timeout)
    tree = fetch_json(f"{REPO_API}/git/trees/main?recursive=1", timeout)
    paths = {item["path"] for item in tree.get("tree", [])}
    readme = fetch_text(f"{RAW_BASE}/README.md", timeout)
    main_entry = fetch_text(f"{RAW_BASE}/main_ai_researcher.py", timeout)
    idea_entry = fetch_text(f"{RAW_BASE}/research_agent/run_infer_idea.py", timeout)

    direct_query_cli = contains_all(
        main_entry,
        ["main_ai_researcher(input, reference, mode)", "Reference-Based Ideation", "Detailed Idea Description"],
    ) and "queries.json" in main_entry
    benchmark_instance_required = contains_all(
        main_entry,
        ["CATEGORY", "INSTANCE_ID", "TASK_LEVEL", "benchmark/final/{category}/{instance_id}.json"],
    )
    docker_required = "DockerEnv" in idea_entry and "DockerConfig" in idea_entry
    reference_papers_required = "source_papers" in idea_entry and "references" in idea_entry
    idea_count_loop = "IDEA_NUM = 5" in idea_entry
    required_paths = [
        ".env.template",
        "main_ai_researcher.py",
        "research_agent/run_infer_idea.py",
        "research_agent/run_infer_plan.py",
        "benchmark/final",
        "docker/requirements.txt",
    ]
    missing_paths = [
        path
        for path in required_paths
        if path not in paths and not any(item.startswith(path.rstrip("/") + "/") for item in paths)
    ]

    return {
        "date": "2026-06-04",
        "baseline": "AI-Researcher",
        "source": "https://github.com/HKUDS/AI-Researcher",
        "checked_head": head.get("object", {}).get("sha", ""),
        "files_checked": [
            "README.md",
            "main_ai_researcher.py",
            "research_agent/run_infer_idea.py",
            "repository file tree",
        ],
        "direct_30_query_runner_available": direct_query_cli,
        "evo_table1_drop_in_status": "not_drop_in",
        "signals": {
            "benchmark_instance_required": benchmark_instance_required,
            "docker_required": docker_required,
            "reference_papers_required": reference_papers_required,
            "idea_count_loop": idea_count_loop,
            "missing_required_paths": missing_paths,
        },
        "entrypoints": {
            "web_gui": "python web_ai_researcher.py",
            "main_function": "main_ai_researcher(input, reference, mode)",
            "modes": ["Detailed Idea Description", "Reference-Based Ideation", "Paper Generation Agent"],
            "idea_runner": "research_agent/run_infer_idea.py",
        },
        "required_env": [
            "CATEGORY",
            "INSTANCE_ID",
            "TASK_LEVEL",
            "CONTAINER_NAME",
            "WORKPLACE_NAME",
            "CACHE_PATH",
            "PORT",
            "MAX_ITER_TIMES",
            "OPENROUTER_API_KEY",
            "GITHUB_AI_TOKEN",
        ],
        "reproduction_implication": (
            "AI-Researcher is a plausible replacement-baseline runner, but the public "
            "entrypoint is benchmark-instance based and not a direct runner for the "
            "30 natural-language EvoScientist Table 1 queries. A paper-exact rerun "
            "would require a pinned adapter that maps each recovered query to an "
            "AI-Researcher benchmark instance or author-provided raw outputs."
        ),
        "next_actions": [
            "Do not count the public AI-Researcher repository as paper Table 1 evidence by itself.",
            "If using AI-Researcher as a replacement baseline, create per-query benchmark instance JSON files and record the adapter protocol.",
            "Run the external system in an isolated checkout/container, then import outputs with reproduction/import_baseline_outputs.py.",
            "Judge imported outputs through the existing swapped pairwise judge pipeline.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI-Researcher Baseline Probe",
        "",
        f"Date: {report['date']}",
        f"Source: {report['source']}",
        f"Checked HEAD: `{report['checked_head']}`",
        "",
        f"Drop-in EvoScientist Table 1 runner: `{report['evo_table1_drop_in_status']}`",
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
        if isinstance(value, list):
            value = ", ".join(value)
        lines.append(f"- {key}: {value}")
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
