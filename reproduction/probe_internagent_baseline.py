#!/usr/bin/env python3
"""Probe the public InternAgent runner as an EvoScientist Table 1 baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "internagent_baseline_probe.json"
DEFAULT_OUTPUT_MD = ROOT / "internagent_baseline_probe.md"
REPO_API = "https://api.github.com/repos/InternScience/InternAgent"
RAW_BASE = "https://raw.githubusercontent.com/InternScience/InternAgent/main"


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
    launch = fetch_text(f"{RAW_BASE}/launch.py", timeout)
    launch_qa = fetch_text(f"{RAW_BASE}/launch_qa.py", timeout)
    launch_discovery = fetch_text(f"{RAW_BASE}/launch_discovery.py", timeout)
    env_example = fetch_text(f"{RAW_BASE}/.env.example", timeout)

    qa_cli_available = all(
        needle in launch_qa
        for needle in [
            "--question",
            "--output",
            "DRAgent",
            "agent.execute",
        ]
    )
    master_qa_available = "--mode" in launch and "qa" in launch and "launch_qa" in launch
    discovery_task_based = all(
        needle in launch_discovery
        for needle in ["--task", "IdeaGenerator", "ExperimentRunner"]
    )
    required_paths = [
        ".env.example",
        "launch.py",
        "launch_qa.py",
        "launch_discovery.py",
        "config/default_config.yaml",
        "tasks",
        "scripts/run_qa.sh",
    ]
    missing_paths = [
        path
        for path in required_paths
        if path not in paths and not any(item.startswith(path.rstrip("/") + "/") for item in paths)
    ]
    qa_command_template = (
        "python launch.py --mode qa --question {question_json} --output {answer_path}"
    )

    return {
        "date": "2026-06-04",
        "baseline": "InternAgent",
        "source": "https://github.com/InternScience/InternAgent",
        "checked_head": head.get("object", {}).get("sha", ""),
        "files_checked": [
            "README.md",
            "launch.py",
            "launch_qa.py",
            "launch_discovery.py",
            ".env.example",
            "repository file tree",
        ],
        "direct_30_query_runner_available": qa_cli_available and master_qa_available,
        "evo_table1_drop_in_status": "qa_drop_in_candidate" if qa_cli_available else "not_drop_in",
        "paper_exact_status": "not_paper_exact",
        "signals": {
            "qa_cli_available": qa_cli_available,
            "master_qa_available": master_qa_available,
            "discovery_task_based": discovery_task_based,
            "required_openai_compatible_key": "OPENAI_API_KEY" in env_example,
            "anthropic_required_for_experiment_backend": "ANTHROPIC_API_KEY" in env_example,
            "missing_required_paths": missing_paths,
        },
        "entrypoints": {
            "qa": "python launch_qa.py --question '...' --output answer.md",
            "master_qa": "python launch.py --mode qa --question '...' --output answer.md",
            "discovery": "python launch.py --mode discovery --task AutoDebug --exp_backend claudecode",
        },
        "required_env": [
            "OPENAI_API_KEY",
            "OPENAI_API_BASE_URL",
            "OPENAI_BASE_URL",
            "ANTHROPIC_API_KEY for claudecode experiment backend",
        ],
        "replacement_run_template": {
            "checkout": "git clone https://github.com/InternScience/InternAgent.git {external_checkout}",
            "install": "conda create -n InternAgent python=3.11 && conda activate InternAgent && pip install -r requirements.txt",
            "per_query": qa_command_template,
            "import_outputs": ".venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source {answers_dir} --source-format directory --output-root reproduction/artifacts/idea_outputs --strict",
        },
        "reproduction_implication": (
            "InternAgent exposes a one-shot QA CLI that can accept each recovered "
            "EvoScientist query and write an answer file, making it a plausible "
            "replacement-baseline candidate. This still does not provide the raw "
            "InternAgent outputs used by the EvoScientist paper, nor does it match "
            "the paper's exact model/tool/judge setup without a pinned rerun protocol."
        ),
        "next_actions": [
            "Use the QA CLI only as a replacement-baseline rerun path, not paper-exact Table 1 evidence.",
            "Run each of the 30 recovered queries in an isolated InternAgent checkout and save query_XX.md files.",
            "Import the saved answers with reproduction/import_baseline_outputs.py under system name InternAgent.",
            "Judge imported outputs through the existing swapped pairwise judge pipeline.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# InternAgent Baseline Probe",
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
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Replacement Run Template", ""])
    for key, value in report["replacement_run_template"].items():
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
