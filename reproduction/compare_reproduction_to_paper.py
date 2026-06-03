#!/usr/bin/env python3
"""Compare reproduced aggregate artifacts against paper-reported results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_EXPECTED = ROOT / "paper_reported_results.json"
METRICS = ["win_pct", "tie_pct", "lose_pct"]
SCALAR_SKIP_KEYS = {"metric", "judge", "target_system_note", "dimensions", "baselines"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_delta(actual: float, expected: float) -> float:
    return round(float(actual) - float(expected), 4)


def compare_table(
    *,
    actual: dict[str, Any],
    expected_section: dict[str, Any],
    tolerance: float,
    require_all: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    failures = []
    actual_baselines = actual.get("baselines", {})
    expected_baselines = expected_section["baselines"]

    for baseline, expected_baseline in expected_baselines.items():
        if baseline not in actual_baselines:
            message = f"missing baseline: {baseline}"
            if require_all:
                failures.append(message)
            rows.append({"baseline": baseline, "status": "missing", "detail": message})
            continue

        actual_baseline = actual_baselines[baseline]
        for dim, expected_dim in expected_baseline["dimensions"].items():
            actual_dim = actual_baseline.get("dimensions", {}).get(dim)
            if actual_dim is None:
                message = f"missing dimension: {baseline}.{dim}"
                failures.append(message)
                rows.append(
                    {
                        "baseline": baseline,
                        "dimension": dim,
                        "status": "missing",
                        "detail": message,
                    }
                )
                continue
            for metric in METRICS:
                delta = metric_delta(actual_dim[metric], expected_dim[metric])
                ok = abs(delta) <= tolerance
                if not ok:
                    failures.append(
                        f"{baseline}.{dim}.{metric}: actual={actual_dim[metric]} "
                        f"expected={expected_dim[metric]} delta={delta}"
                    )
                rows.append(
                    {
                        "baseline": baseline,
                        "dimension": dim,
                        "metric": metric,
                        "actual": actual_dim[metric],
                        "expected": expected_dim[metric],
                        "delta": delta,
                        "status": "ok" if ok else "fail",
                    }
                )

        if "avg_gap" in actual_baseline and "avg_gap" in expected_baseline:
            delta = metric_delta(actual_baseline["avg_gap"], expected_baseline["avg_gap"])
            ok = abs(delta) <= tolerance
            if not ok:
                failures.append(
                    f"{baseline}.avg_gap: actual={actual_baseline['avg_gap']} "
                    f"expected={expected_baseline['avg_gap']} delta={delta}"
                )
            rows.append(
                {
                    "baseline": baseline,
                    "metric": "avg_gap",
                    "actual": actual_baseline["avg_gap"],
                    "expected": expected_baseline["avg_gap"],
                    "delta": delta,
                    "status": "ok" if ok else "fail",
                }
            )

    return rows, failures


def compare_scalars(
    *,
    actual: dict[str, Any],
    expected_section: dict[str, Any],
    tolerance: float,
    require_all: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    failures = []
    expected_metrics = {
        key: value
        for key, value in expected_section.items()
        if key not in SCALAR_SKIP_KEYS and isinstance(value, int | float)
    }
    for metric, expected_value in expected_metrics.items():
        if metric not in actual:
            message = f"missing metric: {metric}"
            if require_all:
                failures.append(message)
            rows.append({"metric": metric, "status": "missing", "detail": message})
            continue
        delta = metric_delta(actual[metric], expected_value)
        ok = abs(delta) <= tolerance
        if not ok:
            failures.append(
                f"{metric}: actual={actual[metric]} expected={expected_value} delta={delta}"
            )
        rows.append(
            {
                "metric": metric,
                "actual": actual[metric],
                "expected": expected_value,
                "delta": delta,
                "status": "ok" if ok else "fail",
            }
        )
    if require_all and not expected_metrics:
        failures.append("expected section contains no comparable scalar metrics")
    return rows, failures


def compare(
    *,
    actual: dict[str, Any],
    expected_section: dict[str, Any],
    tolerance: float,
    require_all: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    if "baselines" in expected_section:
        return compare_table(
            actual=actual,
            expected_section=expected_section,
            tolerance=tolerance,
            require_all=require_all,
        )
    return compare_scalars(
        actual=actual,
        expected_section=expected_section,
        tolerance=tolerance,
        require_all=require_all,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual-json", type=Path, required=True)
    parser.add_argument("--section", default="table1_llm_idea_generation")
    parser.add_argument("--expected-json", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--tolerance", type=float, default=0.05)
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    actual = load_json(args.actual_json)
    expected = load_json(args.expected_json)
    if args.section not in expected:
        raise SystemExit(f"Unknown expected section: {args.section}")

    expected_section = expected[args.section]
    rows, failures = compare(
        actual=actual,
        expected_section=expected_section,
        tolerance=args.tolerance,
        require_all=args.require_all,
    )
    result = {
        "status": "pass" if not failures else "fail",
        "section": args.section,
        "actual_json": str(args.actual_json),
        "expected_json": str(args.expected_json),
        "tolerance": args.tolerance,
        "failures": failures,
        "rows": rows,
    }

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "section": args.section,
                "checked_rows": len(rows),
                "failures": len(failures),
            },
            indent=2,
        )
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
