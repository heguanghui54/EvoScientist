#!/usr/bin/env python3
"""Validate schemas and any imported paper-level artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_SCHEMA = ROOT / "paper_artifact_schema.json"
DEFAULT_ARTIFACTS = ROOT / "artifacts"
DEFAULT_QUERIES = ROOT / "queries.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            record["_line_number"] = line_number
            records.append(record)
    return records


def expected_query_ids() -> set[int]:
    return {item["id"] for item in load_json(DEFAULT_QUERIES)["queries"]}


def missing_fields(record: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if field not in record or record[field] in ("", None, [])]


def validate_jsonl(path: Path, required_fields: list[str]) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False, "complete": False, "missing_records": ["file"]}
    records = load_jsonl(path)
    bad = [
        {"line": record["_line_number"], "missing_fields": missing_fields(record, required_fields)}
        for record in records
        if missing_fields(record, required_fields)
    ]
    return {
        "path": str(path),
        "exists": True,
        "records": len(records),
        "bad_records": bad,
        "complete": bool(records) and not bad,
    }


def validate_json(path: Path, required_fields: list[str]) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False, "complete": False, "missing_fields": ["file"]}
    data = load_json(path)
    missing = missing_fields(data, required_fields)
    return {
        "path": str(path),
        "exists": True,
        "missing_fields": missing,
        "complete": not missing,
    }


def validate_human(schema: dict[str, Any], artifacts_root: Path) -> dict[str, Any]:
    root = artifacts_root / "human_evaluation"
    files = schema["files"]
    inputs = validate_jsonl(root / "inputs.jsonl", files["inputs.jsonl"]["record_required_fields"])
    labels = validate_jsonl(root / "labels.jsonl", files["labels.jsonl"]["record_required_fields"])
    valid_winners = set(schema["valid_winners"])
    if labels.get("exists"):
        records = load_jsonl(root / "labels.jsonl")
        invalid = [
            {"line": record["_line_number"], "winner": record.get("winner")}
            for record in records
            if record.get("winner") not in valid_winners
        ]
        labels["invalid_winners"] = invalid
        labels["complete"] = labels["complete"] and not invalid
    aggregate = validate_json(root / "aggregate.json", files["aggregate.json"]["required_fields"])
    return {
        "root": str(root),
        "files": {"inputs.jsonl": inputs, "labels.jsonl": labels, "aggregate.json": aggregate},
        "complete": all(item["complete"] for item in [inputs, labels, aggregate]),
    }


def validate_ablation(schema: dict[str, Any], artifacts_root: Path) -> dict[str, Any]:
    root = artifacts_root / "ablations"
    expected_ids = expected_query_ids()
    variants = {}
    for variant in schema["variants"]:
        vroot = root / variant
        files = schema["files"]
        system_outputs = validate_json(
            vroot / "system_outputs_complete.json",
            files["system_outputs_complete.json"]["required_fields"],
        )
        if system_outputs.get("exists"):
            data = load_json(vroot / "system_outputs_complete.json")
            complete_ids = set(data.get("complete_query_ids", []))
            missing_ids = sorted(expected_ids - complete_ids)
            unexpected_ids = sorted(complete_ids - expected_ids)
            query_count = data.get("query_count")
            system_outputs["expected_query_count"] = len(expected_ids)
            system_outputs["complete_query_count"] = len(complete_ids)
            system_outputs["missing_query_ids"] = missing_ids
            system_outputs["unexpected_query_ids"] = unexpected_ids
            system_outputs["complete"] = (
                system_outputs["complete"]
                and data.get("complete") is True
                and query_count == len(expected_ids)
                and not missing_ids
                and not unexpected_ids
            )
        judge_inputs = validate_jsonl(
            vroot / "judge_inputs.jsonl",
            files["judge_inputs.jsonl"]["record_required_fields"],
        )
        if judge_inputs.get("exists"):
            input_ids = {record["query_id"] for record in load_jsonl(vroot / "judge_inputs.jsonl")}
            judge_inputs["expected_records"] = len(expected_ids)
            judge_inputs["missing_query_ids"] = sorted(expected_ids - input_ids)
            judge_inputs["complete"] = judge_inputs["complete"] and input_ids == expected_ids
        judge_outputs = validate_jsonl(
            vroot / "judge_outputs.jsonl",
            files["judge_outputs.jsonl"]["record_required_fields"],
        )
        if judge_outputs.get("exists"):
            output_ids = {record["query_id"] for record in load_jsonl(vroot / "judge_outputs.jsonl")}
            judge_outputs["expected_records"] = len(expected_ids)
            judge_outputs["missing_query_ids"] = sorted(expected_ids - output_ids)
            judge_outputs["complete"] = judge_outputs["complete"] and output_ids == expected_ids
        aggregate = validate_json(vroot / "aggregate.json", files["aggregate.json"]["required_fields"])
        variants[variant] = {
            "root": str(vroot),
            "files": {
                "system_outputs_complete.json": system_outputs,
                "judge_inputs.jsonl": judge_inputs,
                "judge_outputs.jsonl": judge_outputs,
                "aggregate.json": aggregate,
            },
            "complete": all(item["complete"] for item in [system_outputs, judge_inputs, judge_outputs, aggregate]),
        }
    return {"root": str(root), "variants": variants, "complete": all(item["complete"] for item in variants.values())}


def validate_code_execution(schema: dict[str, Any], artifacts_root: Path) -> dict[str, Any]:
    root = artifacts_root / "code_execution"
    files = schema["files"]
    trajectories = validate_jsonl(root / "trajectories.jsonl", files["trajectories.jsonl"]["record_required_fields"])
    logs = validate_jsonl(root / "execution_logs.jsonl", files["execution_logs.jsonl"]["record_required_fields"])
    summary = validate_json(root / "summary.json", files["summary.json"]["required_fields"])
    return {
        "root": str(root),
        "files": {"trajectories.jsonl": trajectories, "execution_logs.jsonl": logs, "summary.json": summary},
        "complete": all(item["complete"] for item in [trajectories, logs, summary]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    schema = load_json(args.schema)
    schemas = schema["schemas"]
    report = {
        "schema": str(args.schema),
        "artifacts_root": str(args.artifacts_root),
        "components": {
            "human_evaluation": validate_human(schemas["human_evaluation"], args.artifacts_root),
            "ablation": validate_ablation(schemas["ablation"], args.artifacts_root),
            "code_execution": validate_code_execution(schemas["code_execution"], args.artifacts_root),
        },
    }
    report["complete"] = all(item["complete"] for item in report["components"].values())
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "complete" if report["complete"] else "incomplete",
        "components": {
            name: "complete" if item["complete"] else "incomplete"
            for name, item in report["components"].items()
        },
    }, indent=2))
    if args.strict and not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
