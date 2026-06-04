#!/usr/bin/env python3
"""Audit paper-level reproduction completion across all reported experiments.

This is intentionally stricter than the local smoke tests. A green preflight
only proves that the harness works; this script checks whether the artifacts
needed to reproduce the paper's reported tables and figure-level claims exist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import audit_reproduction_artifacts as table1_audit
import verify_paper_artifact_schema as schema_audit


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
DEFAULT_ARTIFACTS = ROOT / "artifacts"
DEFAULT_FULL_STATUS = ROOT / "full_trajectory_status.json"
DEFAULT_PUBLIC_GAP = ROOT / "public_artifact_gap_report.json"
DEFAULT_SCHEMA = ROOT / "paper_artifact_schema.json"

HUMAN_REQUIRED_FILES = [
    "inputs.jsonl",
    "labels.jsonl",
    "aggregate.json",
]
ABLATION_VARIANTS = ["-IDE", "-IVE", "-all"]
ABLATION_REQUIRED_FILES = [
    "system_outputs_complete.json",
    "judge_inputs.jsonl",
    "judge_outputs.jsonl",
    "aggregate.json",
]
CODE_EXECUTION_REQUIRED_FILES = [
    "trajectories.jsonl",
    "execution_logs.jsonl",
    "summary.json",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def file_status(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
    }


def complete_files(root: Path, filenames: list[str]) -> dict[str, Any]:
    files = {name: file_status(root / name) for name in filenames}
    missing = [name for name, item in files.items() if not item["exists"] or item["bytes"] == 0]
    return {
        "root": str(root),
        "files": files,
        "missing_files": missing,
        "complete": not missing,
    }


def audit_full_trajectories(path: Path) -> dict[str, Any]:
    status = read_json(path)
    audit = status.get("audit", {})
    counts = audit.get("counts") or status.get("full_trajectory_counts", {})
    success_count = counts.get("success") or counts.get("successful_final_reports", 0)
    query_count = audit.get("query_count") or len(
        status.get("full_trajectory_counts", {}).get("attempted_queries", [])
    )
    incomplete = audit.get("failed_or_incomplete_query_ids", [])
    complete = bool(query_count) and success_count == query_count and not incomplete
    return {
        "status_file": str(path),
        "exists": path.is_file(),
        "query_count": query_count,
        "success_count": success_count,
        "counts": counts,
        "failed_or_incomplete_query_ids": sorted(incomplete),
        "complete": complete,
        "reason": (
            "30/30 full trajectories have qualifying final reports"
            if complete
            else "full trajectory attempts exist, but not every query has a qualifying final report"
        ),
    }


def audit_table1(artifacts_root: Path) -> dict[str, Any]:
    queries = table1_audit.load_queries()
    baselines = table1_audit.DEFAULT_BASELINES
    expected_ids = table1_audit.expected_comparison_ids(
        queries=queries,
        target_system="EvoScientist",
        baselines=baselines,
        swapped=True,
    )
    systems_root = artifacts_root / "idea_outputs"
    judge_inputs = artifacts_root / "judge_inputs" / "results.jsonl"
    judge_outputs = artifacts_root / "judge_outputs" / "results.jsonl"
    aggregate_json = artifacts_root / "tables" / "idea_generation_win_tie_lose.json"
    system_outputs = table1_audit.audit_system_outputs(
        systems_root=systems_root,
        systems=["EvoScientist", *baselines],
        queries=queries,
    )
    report = {
        "paper_table": "Table 1 LLM idea-generation evaluation",
        "expected_pairwise_records": len(expected_ids),
        "paper_exact": False,
        "completion_scope": "replacement_or_imported_table1_artifacts",
        "system_outputs": system_outputs,
        "judge_inputs": table1_audit.audit_jsonl_coverage(
            path=judge_inputs,
            expected_ids=expected_ids,
        ),
        "judge_outputs": table1_audit.audit_jsonl_coverage(
            path=judge_outputs,
            expected_ids=expected_ids,
        ),
        "aggregate_table": table1_audit.audit_aggregate_table(
            path=aggregate_json,
            baselines=baselines,
        ),
        "replacement_summary": file_status(ROOT / "table1_replacement_all_baselines_monica_report.json"),
    }
    report["complete"] = all(
        [
            report["system_outputs"]["complete"],
            report["judge_inputs"]["complete"],
            report["judge_outputs"]["complete"],
            report["aggregate_table"]["complete"],
        ]
    )
    return report


def audit_table2(artifacts_root: Path, schema: dict[str, Any]) -> dict[str, Any]:
    root = artifacts_root / "human_evaluation"
    report = complete_files(root, HUMAN_REQUIRED_FILES)
    schema_report = schema_audit.validate_human(schema["schemas"]["human_evaluation"], artifacts_root)
    report["paper_table"] = "Table 2 human idea-generation evaluation"
    report["schema_valid"] = schema_report["complete"]
    report["schema_report"] = schema_report
    report["complete"] = report["complete"] and schema_report["complete"]
    report["required_evidence"] = [
        "anonymized pairwise human-evaluation inputs",
        "labels from the three PhD-level annotators",
        "human Win/Tie/Lose aggregate matching paper dimensions",
    ]
    return report


def audit_table3(artifacts_root: Path, schema: dict[str, Any]) -> dict[str, Any]:
    root = artifacts_root / "ablations"
    variants = {}
    for variant in ABLATION_VARIANTS:
        variants[variant] = complete_files(root / variant, ABLATION_REQUIRED_FILES)
    schema_report = schema_audit.validate_ablation(schema["schemas"]["ablation"], artifacts_root)
    complete = all(item["complete"] for item in variants.values()) and schema_report["complete"]
    return {
        "paper_table": "Table 3 ablation idea-generation evaluation",
        "root": str(root),
        "variants": variants,
        "schema_valid": schema_report["complete"],
        "schema_report": schema_report,
        "complete": complete,
        "required_evidence": [
            "outputs for -IDE, -IVE, and -all variants",
            "Gemini-3-flash judge inputs and outputs for each ablation comparison",
            "aggregate Win/Tie/Lose table from the ablation-variant perspective",
        ],
    }


def audit_figure2(artifacts_root: Path, schema: dict[str, Any]) -> dict[str, Any]:
    root = artifacts_root / "code_execution"
    report = complete_files(root, CODE_EXECUTION_REQUIRED_FILES)
    schema_report = schema_audit.validate_code_execution(schema["schemas"]["code_execution"], artifacts_root)
    report["paper_figure"] = "Figure 2 code-execution success analysis"
    report["schema_valid"] = schema_report["complete"]
    report["schema_report"] = schema_report
    report["complete"] = report["complete"] and schema_report["complete"]
    report["required_evidence"] = [
        "generated code trajectories across experiment stages",
        "execution success/failure logs",
        "before/after evolution summary metrics",
    ]
    return report


def audit_public_gap(path: Path) -> dict[str, Any]:
    report = read_json(path)
    missing = {
        key: value
        for key, value in report.items()
        if key.startswith("missing_for_exact_") and value
    }
    return {
        "path": str(path),
        "exists": path.is_file(),
        "records_missing_public_artifacts": bool(missing),
        "complete": False,
        "note": (
            "Public artifact gap report exists and records missing raw paper artifacts"
            if path.is_file()
            else "Public artifact gap report is missing"
        ),
    }


def item_summary(name: str, item: dict[str, Any]) -> str:
    return "complete" if item.get("complete") else f"incomplete: {name}"


def make_paths_relative(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: make_paths_relative(item) for key, item in value.items()}
    if isinstance(value, list):
        return [make_paths_relative(item) for item in value]
    if isinstance(value, str):
        try:
            path = Path(value)
            if path.is_absolute():
                return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return value
    return value


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    schema = read_json(args.schema)
    components = {
        "full_trajectories": audit_full_trajectories(args.full_status),
        "table1_llm_idea_generation": audit_table1(args.artifacts_root),
        "table2_human_idea_generation": audit_table2(args.artifacts_root, schema),
        "table3_ablation_idea_generation": audit_table3(args.artifacts_root, schema),
        "figure2_code_execution": audit_figure2(args.artifacts_root, schema),
        "public_artifact_gap": audit_public_gap(args.public_gap_report),
    }
    blocking = [
        item_summary(name, item)
        for name, item in components.items()
        if name != "public_artifact_gap" and not item.get("complete")
    ]
    status = "complete" if not blocking else "incomplete"
    return make_paths_relative({
        "date": args.date,
        "status": status,
        "scope": "paper-level reproduction of arXiv:2603.08127 experiments",
        "components": components,
        "artifact_schema": {
            "path": str(args.schema),
            "exists": args.schema.is_file(),
        },
        "blocking_items": blocking,
        "replacement_baseline_note": (
            "The seven-baseline Table 1 replacement/proxy judge coverage is now "
            "complete, but it is not paper-exact author raw output or original "
            "judge-transcript evidence."
        ),
    })


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Paper-Level Reproduction Completion Audit",
        "",
        f"Date: {report['date']}",
        "",
        f"Overall status: `{report['status']}`",
        "",
        "This audit is stricter than local preflight. It asks whether the raw",
        "artifacts needed to reproduce the paper tables and figure-level claims",
        "are present in the checkout.",
        "",
        "## Component Status",
        "",
        "| Component | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    components = report["components"]
    full = components["full_trajectories"]
    lines.append(
        "| Full trajectories | {status} | {success}/{total} successful final reports; "
        "non-success IDs: {bad} |".format(
            status="complete" if full["complete"] else "incomplete",
            success=full["success_count"],
            total=full["query_count"],
            bad=", ".join(str(x) for x in full["failed_or_incomplete_query_ids"]) or "none",
        )
    )
    table1 = components["table1_llm_idea_generation"]
    system_outputs = table1["system_outputs"]["systems"]
    missing_baselines = [
        name
        for name, item in system_outputs.items()
        if name != "EvoScientist" and not item["complete"]
    ]
    lines.append(
        "| Table 1 LLM judge | {status} | expected {expected} pairwise records; "
        "missing baseline outputs: {missing}; paper-exact: {paper_exact} |".format(
            status="complete" if table1["complete"] else "incomplete",
            expected=table1["expected_pairwise_records"],
            missing=", ".join(missing_baselines) or "none",
            paper_exact=str(table1.get("paper_exact", False)).lower(),
        )
    )
    table2 = components["table2_human_idea_generation"]
    lines.append(
        "| Table 2 human eval | {status} | missing files: {missing} |".format(
            status="complete" if table2["complete"] else "incomplete",
            missing=", ".join(table2["missing_files"]) or "none",
        )
    )
    table3 = components["table3_ablation_idea_generation"]
    missing_variants = [
        name for name, item in table3["variants"].items() if not item["complete"]
    ]
    lines.append(
        "| Table 3 ablation | {status} | missing variants: {missing} |".format(
            status="complete" if table3["complete"] else "incomplete",
            missing=", ".join(missing_variants) or "none",
        )
    )
    figure2 = components["figure2_code_execution"]
    lines.append(
        "| Figure 2 code execution | {status} | missing files: {missing} |".format(
            status="complete" if figure2["complete"] else "incomplete",
            missing=", ".join(figure2["missing_files"]) or "none",
        )
    )
    lines.extend(
        [
            "",
            "## Blocking Items",
            "",
        ]
    )
    for item in report["blocking_items"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            report["replacement_baseline_note"],
            "",
            "The reproduction harness is therefore ready for further experiments,",
            "but the paper-level reproduction goal remains incomplete.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--full-status", type=Path, default=DEFAULT_FULL_STATUS)
    parser.add_argument("--public-gap-report", type=Path, default=DEFAULT_PUBLIC_GAP)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--date", default="2026-06-04")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    report = build_report(args)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_markdown(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": report["status"],
                "blocking_items": report["blocking_items"],
            },
            indent=2,
        )
    )
    if args.strict and report["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
