#!/usr/bin/env python3
"""Aggregate pairwise judge outputs into Win/Tie/Lose tables.

Input JSONL records should include:
- comparison_id from build_pairwise_judge_inputs.py
- assistant_1_system
- assistant_2_system
- assistant_1 scores
- assistant_2 scores

Scores are interpreted from the perspective of `--target-system`.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]


def outcome(target_score: float, other_score: float, tie_threshold: float) -> str:
    delta = target_score - other_score
    if abs(delta) <= tie_threshold:
        return "tie"
    return "win" if delta > 0 else "lose"


def percent(n: int, denom: int) -> float:
    return round(100.0 * n / denom, 2) if denom else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--target-system", default="EvoScientist")
    parser.add_argument("--tie-threshold", type=float, default=0.0)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    counts: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: {dim: {"win": 0, "tie": 0, "lose": 0} for dim in DIMENSIONS}
    )
    raw_records = 0

    with args.input.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            raw_records += 1
            sys1 = record["assistant_1_system"]
            sys2 = record["assistant_2_system"]
            if args.target_system not in {sys1, sys2}:
                continue
            baseline = sys2 if sys1 == args.target_system else sys1
            target_scores = (
                record["assistant_1"] if sys1 == args.target_system else record["assistant_2"]
            )
            other_scores = (
                record["assistant_2"] if sys1 == args.target_system else record["assistant_1"]
            )
            for dim in DIMENSIONS:
                result = outcome(
                    float(target_scores[dim]),
                    float(other_scores[dim]),
                    args.tie_threshold,
                )
                counts[baseline][dim][result] += 1

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    summary = {
        "target_system": args.target_system,
        "tie_threshold": args.tie_threshold,
        "raw_records": raw_records,
        "baselines": {},
    }
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
        avg_gap = round(sum(gaps) / len(gaps), 2) if gaps else 0.0
        summary["baselines"][baseline] = {"dimensions": dim_rows, "avg_gap": avg_gap}

    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
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
        )
        writer.writeheader()
        writer.writerows(rows)

    args.output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "rows": len(rows), "output_csv": str(args.output_csv)}, indent=2))


if __name__ == "__main__":
    main()

