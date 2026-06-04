#!/usr/bin/env python3
"""Import a completed Table 2 human-label CSV sheet."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import aggregate_human_labels
from build_paper_level_evidence_runbook import ANNOTATORS, DIMENSIONS


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUTS = ROOT / "artifacts" / "human_evaluation" / "inputs.jsonl"
VALID_WINNERS = {"assistant_1", "assistant_2", "tie"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def load_sheet(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def expected_keys(inputs: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
    return {
        (item["comparison_id"], annotator_id, dimension)
        for item in inputs
        for annotator_id in ANNOTATORS
        for dimension in DIMENSIONS
    }


def validate_rows(rows: list[dict[str, Any]], expected: set[tuple[str, str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    labels = []
    errors = []
    seen = set()
    for line_number, row in enumerate(rows, start=2):
        comparison_id = (row.get("comparison_id") or "").strip()
        annotator_id = (row.get("annotator_id") or "").strip()
        dimension = (row.get("dimension") or "").strip()
        winner = (row.get("winner") or "").strip()
        key = (comparison_id, annotator_id, dimension)
        if key not in expected:
            errors.append({"line": line_number, "reason": "unexpected_key", "key": key})
            continue
        if key in seen:
            errors.append({"line": line_number, "reason": "duplicate_key", "key": key})
            continue
        seen.add(key)
        if winner not in VALID_WINNERS:
            errors.append({"line": line_number, "reason": "invalid_or_blank_winner", "winner": winner, "key": key})
            continue
        label = {
            "comparison_id": comparison_id,
            "annotator_id": annotator_id,
            "dimension": dimension,
            "winner": winner,
            "evaluator_type": "human",
        }
        confidence = (row.get("confidence") or "").strip()
        rationale = (row.get("rationale") or "").strip()
        if confidence:
            label["confidence"] = confidence
        if rationale:
            label["rationale"] = rationale
        labels.append(label)
    missing = sorted(expected - seen)
    errors.extend(
        {"line": None, "reason": "missing_key", "key": key}
        for key in missing
    )
    return labels, errors


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def write_aggregate(inputs_path: Path, labels_path: Path, output_json: Path, output_csv: Path) -> None:
    result = aggregate_human_labels.aggregate(
        aggregate_human_labels.load_jsonl(inputs_path),
        aggregate_human_labels.load_jsonl(labels_path),
        "EvoScientist",
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result["summary"], indent=2), encoding="utf-8")
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "baseline",
                "dimension",
                "n",
                "win",
                "tie",
                "lose",
                "win_pct",
                "tie_pct",
                "lose_pct",
                "gap",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result["rows"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=DEFAULT_INPUTS)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--output-labels", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    inputs = load_jsonl(args.inputs)
    expected = expected_keys(inputs)
    labels, errors = validate_rows(load_sheet(args.sheet), expected)
    if errors:
        print(
            json.dumps(
                {
                    "status": "invalid",
                    "labels_ready": len(labels),
                    "expected_labels": len(expected),
                    "errors": errors[:50],
                    "error_count": len(errors),
                },
                indent=2,
            )
        )
        if args.strict:
            raise SystemExit(1)
        return
    write_jsonl(args.output_labels, labels)
    write_aggregate(args.inputs, args.output_labels, args.output_json, args.output_csv)
    print(
        json.dumps(
            {
                "status": "ok",
                "labels": len(labels),
                "output_labels": str(args.output_labels),
                "output_json": str(args.output_json),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
