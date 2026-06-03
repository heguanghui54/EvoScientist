#!/usr/bin/env python3
"""Aggregate Table 2 human labels into Win/Tie/Lose tables.

Input labels JSONL records must include:
- comparison_id
- annotator_id
- dimension
- winner: assistant_1, assistant_2, or tie

The matching inputs JSONL records define the baseline and answer ordering for
each comparison_id. Outputs mirror aggregate_judge_results.py's JSON shape.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]
VALID_WINNERS = {"assistant_1", "assistant_2", "tie"}


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


def percent(n: int, denom: int) -> float:
    return round(100.0 * n / denom, 2) if denom else 0.0


def label_outcome(input_record: dict[str, Any], winner: str, target_system: str) -> tuple[str, str]:
    sys1 = input_record.get("assistant_1_system") or input_record.get("system_a") or target_system
    sys2 = input_record.get("assistant_2_system") or input_record.get("system_b") or input_record["baseline"]
    if target_system not in {sys1, sys2}:
        raise ValueError(f"target system {target_system!r} missing from {input_record['comparison_id']}")
    baseline = sys2 if sys1 == target_system else sys1
    if winner == "tie":
        return baseline, "tie"
    winner_system = sys1 if winner == "assistant_1" else sys2
    return baseline, "win" if winner_system == target_system else "lose"


def aggregate(inputs: list[dict[str, Any]], labels: list[dict[str, Any]], target_system: str) -> dict[str, Any]:
    input_by_id = {record["comparison_id"]: record for record in inputs}
    counts: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: {dim: {"win": 0, "tie": 0, "lose": 0} for dim in DIMENSIONS}
    )
    annotators = set()
    skipped = []
    for label in labels:
        comparison_id = label.get("comparison_id")
        dimension = label.get("dimension")
        winner = label.get("winner")
        annotator_id = label.get("annotator_id")
        if comparison_id not in input_by_id:
            skipped.append({"line": label["_line_number"], "reason": "missing_input", "comparison_id": comparison_id})
            continue
        if dimension not in DIMENSIONS:
            skipped.append({"line": label["_line_number"], "reason": "invalid_dimension", "dimension": dimension})
            continue
        if winner not in VALID_WINNERS:
            skipped.append({"line": label["_line_number"], "reason": "invalid_winner", "winner": winner})
            continue
        if annotator_id:
            annotators.add(str(annotator_id))
        baseline, result = label_outcome(input_by_id[comparison_id], winner, target_system)
        counts[baseline][dimension][result] += 1

    summary = {
        "target_system": target_system,
        "raw_label_records": len(labels),
        "annotators": sorted(annotators),
        "skipped": skipped,
        "baselines": {},
    }
    rows = []
    for baseline in sorted(counts):
        dim_rows = {}
        gaps = []
        for dim in DIMENSIONS:
            c = counts[baseline][dim]
            denom = c["win"] + c["tie"] + c["lose"]
            win_pct = percent(c["win"], denom)
            tie_pct = percent(c["tie"], denom)
            lose_pct = percent(c["lose"], denom)
            gap = round(win_pct - lose_pct, 2)
            gaps.append(gap)
            row = {
                "baseline": baseline,
                "dimension": dim,
                "n": denom,
                "win": c["win"],
                "tie": c["tie"],
                "lose": c["lose"],
                "win_pct": win_pct,
                "tie_pct": tie_pct,
                "lose_pct": lose_pct,
                "gap": gap,
            }
            rows.append(row)
            dim_rows[dim] = row
        summary["baselines"][baseline] = {
            "dimensions": dim_rows,
            "avg_gap": round(sum(gaps) / len(gaps), 2) if gaps else 0.0,
        }
    return {"summary": summary, "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--target-system", default="EvoScientist")
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    result = aggregate(load_jsonl(args.inputs), load_jsonl(args.labels), args.target_system)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["baseline", "dimension", "n", "win", "tie", "lose", "win_pct", "tie_pct", "lose_pct", "gap"],
        )
        writer.writeheader()
        writer.writerows(result["rows"])
    args.output_json.write_text(json.dumps(result["summary"], indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ok" if not result["summary"]["skipped"] else "partial",
        "rows": len(result["rows"]),
        "raw_label_records": result["summary"]["raw_label_records"],
        "skipped": len(result["summary"]["skipped"]),
        "output_json": str(args.output_json),
    }, indent=2))
    if args.strict and result["summary"]["skipped"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
