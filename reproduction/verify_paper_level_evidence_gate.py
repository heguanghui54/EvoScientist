#!/usr/bin/env python3
"""Gate paper-level evidence for Table 2, Table 3, and Figure 2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_ARTIFACTS = ROOT / "artifacts"
DEFAULT_RUNBOOK = ROOT / "paper_level_evidence_runbook" / "paper_level_evidence_runbook.json"
HUMAN_FILES = ["inputs.jsonl", "labels.jsonl", "aggregate.json"]
ABLATION_VARIANTS = ["-IDE", "-IVE", "-all"]
ABLATION_FILES = ["system_outputs_complete.json", "judge_inputs.jsonl", "judge_outputs.jsonl", "aggregate.json"]
CODE_FILES = ["trajectories.jsonl", "execution_logs.jsonl", "summary.json"]


def file_info(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
    }


def files_gate(root: Path, filenames: list[str]) -> dict[str, Any]:
    files = {name: file_info(root / name) for name in filenames}
    missing = [name for name, item in files.items() if not item["exists"] or item["bytes"] == 0]
    return {"root": str(root), "files": files, "missing_files": missing, "complete": not missing}


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    artifacts = args.artifacts_root
    runbook = file_info(args.runbook)
    human = files_gate(artifacts / "human_evaluation", HUMAN_FILES)
    ablation_variants = {
        variant: files_gate(artifacts / "ablations" / variant, ABLATION_FILES)
        for variant in ABLATION_VARIANTS
    }
    code_execution = files_gate(artifacts / "code_execution", CODE_FILES)
    blocking_items = []
    if not runbook["exists"]:
        blocking_items.append("paper-level evidence runbook has not been generated")
    if not human["complete"]:
        blocking_items.append("Table 2 human evaluation artifacts are incomplete")
    for variant, report in ablation_variants.items():
        if not report["complete"]:
            blocking_items.append(f"Table 3 ablation artifacts are incomplete for {variant}")
    if not code_execution["complete"]:
        blocking_items.append("Figure 2 code-execution artifacts are incomplete")
    return {
        "date": "2026-06-04",
        "status": "ready" if not blocking_items else "not_ready",
        "runbook": runbook,
        "components": {
            "table2_human_evaluation": human,
            "table3_ablation": {
                "root": str(artifacts / "ablations"),
                "variants": ablation_variants,
                "complete": all(item["complete"] for item in ablation_variants.values()),
            },
            "figure2_code_execution": code_execution,
        },
        "blocking_items": blocking_items,
        "caveat": (
            "This gate requires real imported artifacts under reproduction/artifacts. "
            "Template files under reproduction/paper_level_evidence_runbook are not "
            "counted as completed paper evidence."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Paper-Level Evidence Gate",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        "",
        report["caveat"],
        "",
        "## Blocking Items",
        "",
    ]
    if report["blocking_items"]:
        lines.extend(f"- {item}" for item in report["blocking_items"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Component Status",
            "",
            f"- Table 2 human evaluation: {report['components']['table2_human_evaluation']['complete']}",
            f"- Table 3 ablation: {report['components']['table3_ablation']['complete']}",
            f"- Figure 2 code execution: {report['components']['figure2_code_execution']['complete']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--runbook", type=Path, default=DEFAULT_RUNBOOK)
    parser.add_argument("--output-json", type=Path, default=ROOT / "paper_level_evidence_gate.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "paper_level_evidence_gate.md")
    args = parser.parse_args()
    report = build_report(args)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "blocking_items": report["blocking_items"]}, indent=2))


if __name__ == "__main__":
    main()
