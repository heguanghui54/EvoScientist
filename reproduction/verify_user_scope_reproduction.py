#!/usr/bin/env python3
"""Verify the current user-scoped EvoScientist reproduction gate.

This gate is intentionally different from paper-level exact reproduction. It
honors the current user scope: human judges are waived for now, and Monica/
Gemini surrogate judging is accepted for the Table 2 continuation path.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "artifacts" / "audit" / "user_scope_reproduction_gate.json"
DEFAULT_OUTPUT_MD = ROOT / "artifacts" / "audit" / "user_scope_reproduction_gate.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def file_ok(path: Path, min_bytes: int = 1) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
        "complete": path.is_file() and path.stat().st_size >= min_bytes,
    }


def build_report(date: str) -> dict[str, Any]:
    table1 = load_json(ROOT / "table1_replacement_all_baselines_monica_report.json")
    table2 = load_json(ROOT / "table2_surrogate_monica_report.json")
    ablation = load_json(ROOT / "ablation_queries01_30_monica_gemini_report.json")
    figure2 = load_json(ROOT / "figure2_code_execution_replacement_report.json")
    dossier = load_json(ROOT / "final_reproduction_dossier.json")
    bundle = load_json(ROOT / "artifacts" / "reproducibility_bundle" / "manifest.json")
    archive_path = ROOT / "artifacts" / "reproducibility_bundle.zip"

    checks: dict[str, dict[str, Any]] = {
        "full_trajectories": {
            "complete": dossier["components"]["full_trajectories"]["complete"] is True
            and dossier["components"]["full_trajectories"]["success_count"] == 30,
            "evidence": "30/30 successful full trajectories in final dossier",
        },
        "table1_replacement_judge": {
            "complete": table1["status"] == "complete"
            and table1["paper_exact"] is False
            and table1["expected_pairwise_records"] == 420
            and count_jsonl(ROOT / "artifacts" / "judge_outputs" / "results.jsonl") == 420,
            "evidence": "seven baselines x 30 queries x 2 swapped orders = 420 Monica/Gemini judge outputs",
        },
        "table2_surrogate_judge": {
            "complete": table2["status"] == "complete"
            and table2["paper_exact"] is False
            and table2["input_records"] == 120
            and table2["surrogate_label_records"] == 1440
            and count_jsonl(ROOT / "artifacts" / "human_evaluation" / "surrogate_labels.jsonl") == 1440,
            "evidence": "human judge waived by user; Monica/Gemini surrogate labels are available",
        },
        "table2_human_label_packet": {
            "complete": load_json(ROOT / "artifacts" / "human_evaluation" / "label_packet" / "manifest.json")[
                "status"
            ]
            == "ready_for_human_annotation",
            "evidence": "fillable 1440-row human label sheet and full-text review tasks are present",
        },
        "table3_replacement_ablation": {
            "complete": ablation["status"] == "complete"
            and ablation["paper_exact"] is False
            and ablation["covered_query_count"] == 30
            and ablation["judge"]["total_records"] == 90,
            "evidence": "30-query Monica/Gemini replacement ablation rerun",
        },
        "figure2_replacement_probe": {
            "complete": figure2["status"] == "complete"
            and figure2["paper_exact"] is False
            and figure2["metadata"]["trajectory_records"] == 240
            and figure2["metadata"]["execution_log_records"] == 240,
            "evidence": "240-record deterministic replacement code-execution probe",
        },
        "dossier": {
            "complete": file_ok(ROOT / "final_reproduction_dossier.md")["complete"]
            and file_ok(ROOT / "final_reproduction_dossier.json")["complete"],
            "evidence": "final reproduction dossier exists",
        },
        "reproducibility_bundle": {
            "complete": archive_path.is_file()
            and bundle["line_count_checks"]["artifacts/judge_outputs/results.jsonl"] == 420
            and bundle["line_count_checks"]["artifacts/human_evaluation/surrogate_labels.jsonl"] == 1440
            and len(bundle["archive"]["sha256"]) == 64,
            "evidence": "zip bundle, manifest, checksums, and line-count checks exist",
        },
    }
    if archive_path.is_file():
        with zipfile.ZipFile(archive_path) as zf:
            names = set(zf.namelist())
        checks["reproducibility_bundle"]["zip_entries"] = len(names)
        checks["reproducibility_bundle"]["complete"] = checks["reproducibility_bundle"]["complete"] and {
            "reproduction/final_reproduction_dossier.md",
            "reproduction/reproducibility_bundle_manifest.json",
        }.issubset(names)

    incomplete = [name for name, item in checks.items() if not item["complete"]]
    return {
        "date": date,
        "status": "complete" if not incomplete else "incomplete",
        "scope": "user-scoped reproduction with Monica/Gemini surrogate judging and human judge waived for now",
        "paper_exact": False,
        "human_judge_status": "waived_by_user_for_current_scope",
        "paper_exact_remaining_gap": [
            "author-provided original raw Table 1 baseline outputs",
            "author-side original Gemini judge transcripts",
            "three PhD-level Table 2 human labels and aggregate",
        ],
        "checks": checks,
        "incomplete_checks": incomplete,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# User-Scope EvoScientist Reproduction Gate",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Paper-exact: `{str(report['paper_exact']).lower()}`",
        f"Human judge status: `{report['human_judge_status']}`",
        "",
        report["scope"],
        "",
        "## Checks",
        "",
        "| Check | Complete | Evidence |",
        "| --- | --- | --- |",
    ]
    for name, item in report["checks"].items():
        lines.append(f"| {name} | {str(item['complete']).lower()} | {item['evidence']} |")
    lines.extend(["", "## Paper-Exact Remaining Gap", ""])
    for item in report["paper_exact_remaining_gap"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--date", default="2026-06-04")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    report = build_report(args.date)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "incomplete_checks": report["incomplete_checks"],
                "output_json": str(args.output_json),
            },
            indent=2,
        )
    )
    if args.strict and report["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
