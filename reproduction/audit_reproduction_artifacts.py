#!/usr/bin/env python3
"""Audit coverage of EvoScientist reproduction artifacts.

This script does not call any model. It checks whether the files needed to
reproduce the paper-level idea-generation table exist and cover the expected
queries, systems, pairwise judge records, and aggregate table entries.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_ARTIFACTS = ROOT / "artifacts"
DEFAULT_BASELINES = [
    "Virtual Scientist",
    "AI-Researcher",
    "InternAgent",
    "AI Scientist-v2",
    "Hypogenic",
    "Novix",
    "K-Dense",
]
ANSWER_FILENAMES = ["answer.txt", "proposal.md", "stdout.txt"]
DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]


def load_queries(limit: int | None = None) -> list[dict[str, Any]]:
    queries = json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]
    return queries[:limit] if limit is not None else queries


def answer_path(systems_root: Path, system: str, query_id: int) -> Path | None:
    qdir = systems_root / system / f"query_{query_id:02d}"
    for filename in ANSWER_FILENAMES:
        path = qdir / filename
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            return path
    return None


def audit_system_outputs(
    *,
    systems_root: Path,
    systems: list[str],
    queries: list[dict[str, Any]],
) -> dict[str, Any]:
    by_system = {}
    for system in systems:
        missing = []
        present = []
        for query in queries:
            path = answer_path(systems_root, system, query["id"])
            if path is None:
                missing.append(query["id"])
            else:
                present.append({"query_id": query["id"], "path": str(path)})
        by_system[system] = {
            "present": len(present),
            "expected": len(queries),
            "missing_query_ids": missing,
            "complete": not missing,
        }
    return {
        "systems_root": str(systems_root),
        "systems": by_system,
        "complete": all(item["complete"] for item in by_system.values()),
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def expected_comparison_ids(
    *,
    queries: list[dict[str, Any]],
    target_system: str,
    baselines: list[str],
    swapped: bool,
) -> set[str]:
    ids = set()
    for query in queries:
        qid = query["id"]
        for baseline in baselines:
            ids.add(f"q{qid:02d}__{target_system}__vs__{baseline}")
            if swapped:
                ids.add(f"q{qid:02d}__{baseline}__vs__{target_system}")
    return ids


def audit_jsonl_coverage(
    *,
    path: Path,
    expected_ids: set[str],
) -> dict[str, Any]:
    records = load_jsonl(path)
    observed_ids = {record.get("comparison_id") for record in records}
    missing = sorted(expected_ids - observed_ids)
    extras = sorted(item for item in observed_ids - expected_ids if item)
    return {
        "path": str(path),
        "records": len(records),
        "expected_records": len(expected_ids),
        "missing_comparison_ids": missing,
        "extra_comparison_ids": extras,
        "complete": not missing,
    }


def audit_aggregate_table(
    *,
    path: Path,
    baselines: list[str],
) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path": str(path),
            "exists": False,
            "missing_baselines": baselines,
            "missing_dimensions": [],
            "complete": False,
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    actual_baselines = data.get("baselines", {})
    missing_baselines = [baseline for baseline in baselines if baseline not in actual_baselines]
    missing_dimensions = []
    for baseline in baselines:
        dims = actual_baselines.get(baseline, {}).get("dimensions", {})
        for dim in DIMENSIONS:
            if dim not in dims:
                missing_dimensions.append(f"{baseline}.{dim}")
    return {
        "path": str(path),
        "exists": True,
        "missing_baselines": missing_baselines,
        "missing_dimensions": missing_dimensions,
        "complete": not missing_baselines and not missing_dimensions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--systems-root", type=Path, default=None)
    parser.add_argument("--judge-inputs", type=Path, default=None)
    parser.add_argument("--judge-outputs", type=Path, default=None)
    parser.add_argument("--aggregate-json", type=Path, default=None)
    parser.add_argument("--target-system", default="EvoScientist")
    parser.add_argument("--baseline", action="append", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-swapped", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    baselines = args.baseline or DEFAULT_BASELINES
    queries = load_queries(args.limit)
    systems_root = args.systems_root or args.artifacts_root / "idea_outputs"
    judge_inputs = args.judge_inputs or args.artifacts_root / "judge_inputs" / "results.jsonl"
    judge_outputs = args.judge_outputs or args.artifacts_root / "judge_outputs" / "results.jsonl"
    aggregate_json = args.aggregate_json or args.artifacts_root / "tables" / (
        "idea_generation_win_tie_lose.json"
    )

    expected_ids = expected_comparison_ids(
        queries=queries,
        target_system=args.target_system,
        baselines=baselines,
        swapped=not args.no_swapped,
    )
    systems = [args.target_system, *baselines]
    report = {
        "status": "unknown",
        "target_system": args.target_system,
        "baselines": baselines,
        "query_count": len(queries),
        "expected_pairwise_records": len(expected_ids),
        "system_outputs": audit_system_outputs(
            systems_root=systems_root,
            systems=systems,
            queries=queries,
        ),
        "judge_inputs": audit_jsonl_coverage(path=judge_inputs, expected_ids=expected_ids),
        "judge_outputs": audit_jsonl_coverage(path=judge_outputs, expected_ids=expected_ids),
        "aggregate_table": audit_aggregate_table(path=aggregate_json, baselines=baselines),
    }
    complete = all(
        [
            report["system_outputs"]["complete"],
            report["judge_inputs"]["complete"],
            report["judge_outputs"]["complete"],
            report["aggregate_table"]["complete"],
        ]
    )
    report["status"] = "complete" if complete else "incomplete"

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": report["status"],
                "query_count": report["query_count"],
                "baselines": len(baselines),
                "expected_pairwise_records": report["expected_pairwise_records"],
                "system_outputs_complete": report["system_outputs"]["complete"],
                "judge_inputs_complete": report["judge_inputs"]["complete"],
                "judge_outputs_complete": report["judge_outputs"]["complete"],
                "aggregate_table_complete": report["aggregate_table"]["complete"],
            },
            indent=2,
        )
    )
    if args.strict and not complete:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
