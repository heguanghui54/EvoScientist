#!/usr/bin/env python3
"""Aggregate Table 3 ablation judge outputs from the variant perspective.

Expected layout:

reproduction/artifacts/ablations/
  -IDE/judge_outputs.jsonl
  -IVE/judge_outputs.jsonl
  -all/judge_outputs.jsonl

Each JSONL record should include assistant system names plus per-dimension
scores for `assistant_1` and `assistant_2`. Outputs are written back into each
variant directory as `aggregate.json` and `aggregate.csv`.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_ARTIFACTS_ROOT = ROOT / "artifacts" / "ablations"
DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]
DEFAULT_VARIANTS = ["-IDE", "-IVE", "-all"]


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


def outcome(target_score: float, other_score: float, tie_threshold: float) -> str:
    delta = target_score - other_score
    if abs(delta) <= tie_threshold:
        return "tie"
    return "win" if delta > 0 else "lose"


def percent(n: int, denom: int) -> float:
    return round(100.0 * n / denom, 2) if denom else 0.0


def aggregate_variant(
    records: list[dict[str, Any]],
    *,
    variant: str,
    reference_system: str,
    tie_threshold: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    counts = {dim: {"win": 0, "tie": 0, "lose": 0} for dim in DIMENSIONS}
    skipped = []
    usable_records = 0

    for record in records:
        sys1 = record.get("assistant_1_system")
        sys2 = record.get("assistant_2_system")
        if variant not in {sys1, sys2} or reference_system not in {sys1, sys2}:
            skipped.append(
                {
                    "line": record["_line_number"],
                    "reason": "comparison_not_variant_vs_reference",
                    "assistant_1_system": sys1,
                    "assistant_2_system": sys2,
                }
            )
            continue
        target_scores = record.get("assistant_1") if sys1 == variant else record.get("assistant_2")
        other_scores = record.get("assistant_2") if sys1 == variant else record.get("assistant_1")
        missing_dims = [
            dim
            for dim in DIMENSIONS
            if not isinstance(target_scores, dict)
            or not isinstance(other_scores, dict)
            or dim not in target_scores
            or dim not in other_scores
        ]
        if missing_dims:
            skipped.append({"line": record["_line_number"], "reason": "missing_scores", "dimensions": missing_dims})
            continue
        usable_records += 1
        for dim in DIMENSIONS:
            result = outcome(float(target_scores[dim]), float(other_scores[dim]), tie_threshold)
            counts[dim][result] += 1

    rows = []
    gaps = []
    dimensions = {}
    comparison_name = f"{variant} vs {reference_system}"
    for dim in DIMENSIONS:
        c = counts[dim]
        denom = c["win"] + c["tie"] + c["lose"]
        win_pct = percent(c["win"], denom)
        tie_pct = percent(c["tie"], denom)
        lose_pct = percent(c["lose"], denom)
        gap = round(win_pct - lose_pct, 2)
        gaps.append(gap)
        row = {
            "baseline": comparison_name,
            "variant": variant,
            "reference_system": reference_system,
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
        dimensions[dim] = row

    summary = {
        "target_system": variant,
        "reference_system": reference_system,
        "target_system_note": "Rows are from the ablation variant perspective, not EvoScientist perspective.",
        "tie_threshold": tie_threshold,
        "raw_records": len(records),
        "usable_records": usable_records,
        "skipped": skipped,
        "baselines": {
            comparison_name: {
                "dimensions": dimensions,
                "avg_gap": round(sum(gaps) / len(gaps), 2) if gaps else 0.0,
            }
        },
    }
    return summary, rows


def write_variant_outputs(root: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "aggregate.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (root / "aggregate.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "baseline",
                "variant",
                "reference_system",
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS_ROOT)
    parser.add_argument("--variant", action="append", default=None)
    parser.add_argument("--reference-system", default="EvoScientist")
    parser.add_argument("--tie-threshold", type=float, default=0.0)
    parser.add_argument("--combined-json", type=Path, default=None)
    parser.add_argument("--combined-csv", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    variants = args.variant or DEFAULT_VARIANTS
    combined = {
        "reference_system": args.reference_system,
        "target_system_note": "Rows are from the ablation variant perspective, not EvoScientist perspective.",
        "tie_threshold": args.tie_threshold,
        "variants": {},
        "baselines": {},
    }
    combined_rows = []
    missing = []
    partial = []

    for variant in variants:
        variant_root = args.artifacts_root / variant
        judge_outputs = variant_root / "judge_outputs.jsonl"
        if not judge_outputs.is_file():
            missing.append({"variant": variant, "path": str(judge_outputs)})
            continue
        summary, rows = aggregate_variant(
            load_jsonl(judge_outputs),
            variant=variant,
            reference_system=args.reference_system,
            tie_threshold=args.tie_threshold,
        )
        write_variant_outputs(variant_root, summary, rows)
        comparison_name = f"{variant} vs {args.reference_system}"
        combined["variants"][variant] = summary["baselines"][comparison_name]
        combined["variants"][variant]["raw_records"] = summary["raw_records"]
        combined["variants"][variant]["usable_records"] = summary["usable_records"]
        combined["variants"][variant]["skipped"] = summary["skipped"]
        combined["baselines"][comparison_name] = summary["baselines"][comparison_name]
        combined_rows.extend(rows)
        if summary["skipped"] or summary["usable_records"] == 0:
            partial.append(variant)

    if args.combined_json:
        args.combined_json.parent.mkdir(parents=True, exist_ok=True)
        args.combined_json.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    if args.combined_csv:
        args.combined_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.combined_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "baseline",
                    "variant",
                    "reference_system",
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
            writer.writerows(combined_rows)

    status = "ok" if not missing and not partial else "partial"
    print(
        json.dumps(
            {
                "status": status,
                "variants": variants,
                "written_variants": sorted(combined["variants"]),
                "missing": missing,
                "partial": partial,
            },
            indent=2,
        )
    )
    if args.strict and (missing or partial):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
