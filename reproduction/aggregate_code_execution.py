#!/usr/bin/env python3
"""Aggregate Figure 2 code-execution logs into before/after success rates.

Input execution log JSONL records must include:
- trajectory_id
- stage
- attempt_id
- success

Records also need a before/after evolution marker. Accepted fields are
`evolution_state`, `phase`, or `condition`, with values such as `before`,
`after`, `before_evolution`, or `after_evolution`.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


PHASE_FIELDS = ["evolution_state", "phase", "condition"]
PHASE_ALIASES = {
    "before": "before_evolution",
    "pre": "before_evolution",
    "pre_evolution": "before_evolution",
    "before_evolution": "before_evolution",
    "before-evolution": "before_evolution",
    "after": "after_evolution",
    "post": "after_evolution",
    "post_evolution": "after_evolution",
    "after_evolution": "after_evolution",
    "after-evolution": "after_evolution",
}


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


def percent(successes: int, attempts: int) -> float:
    return round(100.0 * successes / attempts, 2) if attempts else 0.0


def normalize_stage(value: Any) -> str:
    text = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if text.isdigit():
        return f"stage_{text}"
    if text.startswith("stage") and not text.startswith("stage_"):
        suffix = text.removeprefix("stage").strip("_")
        if suffix:
            return f"stage_{suffix}"
    return text


def normalize_phase(record: dict[str, Any]) -> str | None:
    for field in PHASE_FIELDS:
        value = record.get(field)
        if value is None:
            continue
        key = str(value).strip().lower().replace(" ", "_")
        return PHASE_ALIASES.get(key)
    return None


def normalize_success(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        key = value.strip().lower()
        if key in {"1", "true", "yes", "y", "success", "succeeded", "pass", "passed"}:
            return True
        if key in {"0", "false", "no", "n", "failure", "failed", "fail"}:
            return False
    return None


def load_reported_targets(path: Path | None) -> dict[str, Any]:
    if not path or not path.is_file():
        return {}
    reported = json.loads(path.read_text(encoding="utf-8"))
    return reported.get("figure2_code_execution", {})


def aggregate(records: list[dict[str, Any]], reported_targets: dict[str, Any] | None = None) -> dict[str, Any]:
    overall: dict[str, dict[str, int]] = defaultdict(lambda: {"attempts": 0, "successes": 0})
    by_stage: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"attempts": 0, "successes": 0})
    )
    skipped = []

    for record in records:
        missing = [
            field
            for field in ["trajectory_id", "stage", "attempt_id", "success"]
            if record.get(field) in (None, "")
        ]
        phase = normalize_phase(record)
        success = normalize_success(record.get("success"))
        if missing or phase is None or success is None:
            skipped.append(
                {
                    "line": record["_line_number"],
                    "missing_fields": missing,
                    "invalid_phase": phase is None,
                    "invalid_success": success is None,
                }
            )
            continue

        stage = normalize_stage(record["stage"])
        overall[phase]["attempts"] += 1
        by_stage[phase][stage]["attempts"] += 1
        if success:
            overall[phase]["successes"] += 1
            by_stage[phase][stage]["successes"] += 1

    phase_rates = {
        phase: {
            "attempts": counts["attempts"],
            "successes": counts["successes"],
            "success_pct": percent(counts["successes"], counts["attempts"]),
        }
        for phase, counts in sorted(overall.items())
    }
    stage_success_rates = {
        phase: {
            stage: {
                "attempts": counts["attempts"],
                "successes": counts["successes"],
                "success_pct": percent(counts["successes"], counts["attempts"]),
            }
            for stage, counts in sorted(stages.items())
        }
        for phase, stages in sorted(by_stage.items())
    }
    summary = {
        "metric": "execution_success_rate",
        "raw_execution_records": len(records),
        "usable_execution_records": sum(item["attempts"] for item in phase_rates.values()),
        "skipped": skipped,
        "before_evolution_pct": phase_rates.get("before_evolution", {}).get("success_pct", 0.0),
        "after_evolution_pct": phase_rates.get("after_evolution", {}).get("success_pct", 0.0),
        "phase_success_rates": phase_rates,
        "stage_success_rates": stage_success_rates,
    }

    stage3_before = stage_success_rates.get("before_evolution", {}).get("stage_3", {})
    stage3_after = stage_success_rates.get("after_evolution", {}).get("stage_3", {})
    if stage3_before:
        summary["stage3_before_evolution_pct"] = stage3_before["success_pct"]
    if stage3_after:
        summary["stage3_after_evolution_pct"] = stage3_after["success_pct"]
    if reported_targets:
        summary["reported_targets"] = reported_targets
        deltas = {}
        for key in [
            "before_evolution_pct",
            "after_evolution_pct",
            "stage3_before_evolution_pct",
            "stage3_after_evolution_pct",
        ]:
            if key in reported_targets and key in summary:
                deltas[key] = round(summary[key] - reported_targets[key], 2)
        summary["deltas_from_paper"] = deltas
    return summary


def csv_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for phase, counts in summary["phase_success_rates"].items():
        rows.append(
            {
                "phase": phase,
                "stage": "all",
                "attempts": counts["attempts"],
                "successes": counts["successes"],
                "success_pct": counts["success_pct"],
            }
        )
        for stage, stage_counts in summary["stage_success_rates"].get(phase, {}).items():
            rows.append(
                {
                    "phase": phase,
                    "stage": stage,
                    "attempts": stage_counts["attempts"],
                    "successes": stage_counts["successes"],
                    "success_pct": stage_counts["success_pct"],
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--reported-json", type=Path, default=Path(__file__).resolve().parent / "paper_reported_results.json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    summary = aggregate(load_jsonl(args.logs), load_reported_targets(args.reported_json))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if args.output_csv:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.output_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["phase", "stage", "attempts", "successes", "success_pct"])
            writer.writeheader()
            writer.writerows(csv_rows(summary))
    print(
        json.dumps(
            {
                "status": "ok" if not summary["skipped"] else "partial",
                "raw_execution_records": summary["raw_execution_records"],
                "usable_execution_records": summary["usable_execution_records"],
                "skipped": len(summary["skipped"]),
                "before_evolution_pct": summary["before_evolution_pct"],
                "after_evolution_pct": summary["after_evolution_pct"],
                "output_json": str(args.output_json),
            },
            indent=2,
        )
    )
    if args.strict:
        required = ["before_evolution", "after_evolution"]
        missing_phases = [phase for phase in required if phase not in summary["phase_success_rates"]]
        if summary["skipped"] or missing_phases:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
