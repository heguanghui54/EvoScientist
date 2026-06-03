#!/usr/bin/env python3
"""Audit full tool-enabled EvoScientist trajectory artifacts.

The paper-level full trajectory requirement is stricter than "process exited".
A successful full idea-generation trajectory must contain a final report or an
equivalent long-form proposal artifact, not only stdout logs or clarification
questions.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_ROOT = ROOT / "artifacts" / "remote_fetch" / "full_trajectories" / "EvoScientist"
SECTION_MARKERS = [
    "Problem",
    "Hypothesis",
    "Method",
    "Dataset",
    "Benchmark",
    "Evaluation",
    "Baselines",
    "Ablations",
    "Failure",
    "Risks",
]


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def usage_from_stdout(stdout: str) -> dict[str, int] | None:
    match = re.search(r"\[Usage:\s*([0-9,]+) in ·\s*([0-9,]+) out\]", stdout)
    if not match:
        return None
    return {
        "input_tokens": int(match.group(1).replace(",", "")),
        "output_tokens": int(match.group(2).replace(",", "")),
    }


def classify(qdir: Path) -> dict[str, Any]:
    stdout = read_text(qdir / "stdout.txt")
    stderr = read_text(qdir / "stderr.txt")
    final_report = read_text(qdir / "final_report.md")
    answer = read_text(qdir / "answer.txt")
    candidate = final_report or answer
    sections = [marker for marker in SECTION_MARKERS if marker.lower() in candidate.lower()]
    has_final_report = bool(final_report.strip())
    has_long_final = len(final_report.encode("utf-8")) >= 10000
    has_proposal_sections = len(set(sections)) >= 5
    asks_clarification = any(
        phrase in stdout.lower()
        for phrase in [
            "what kind of problem",
            "which subarea",
            "or something else entirely",
            "clarification",
            "help me target",
        ]
    )
    timed_out = "Timed out after" in stderr or "Timed out after" in stdout
    killed_or_failed = any(token in stderr.lower() for token in ["traceback", "killed", "error:"])
    success = has_final_report and has_long_final and has_proposal_sections
    if success:
        status = "success"
        reason = "final_report.md exists, is long-form, and contains proposal sections"
    elif asks_clarification:
        status = "clarification"
        reason = "stdout asks for clarification instead of producing a proposal"
    elif timed_out:
        status = "timeout"
        reason = "runner reported timeout"
    elif killed_or_failed:
        status = "failed"
        reason = "stderr indicates failure or manual termination"
    elif stdout.strip():
        status = "incomplete"
        reason = "stdout exists but no qualifying final_report.md was collected"
    else:
        status = "missing"
        reason = "no stdout or final report artifact found"
    return {
        "status": status,
        "reason": reason,
        "files": {
            name: {
                "exists": (qdir / name).is_file(),
                "bytes": (qdir / name).stat().st_size if (qdir / name).is_file() else 0,
            }
            for name in ["stdout.txt", "stderr.txt", "answer.txt", "final_report.md", "query.json"]
        },
        "usage": usage_from_stdout(stdout),
        "sections_detected": sections,
        "trace_indicators": {
            "tool_call_lines": sum(1 for line in stdout.splitlines() if line.lstrip().startswith("● ")),
            "subagent_completion_lines": sum(
                1 for line in stdout.splitlines() if line.lstrip().startswith("✓ ")
            ),
            "mentions_research_agent": "research-agent" in stdout,
            "mentions_final_report_write": "write_file(/final_report.md)" in stdout,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    queries = load_queries()
    by_query = {}
    counts: dict[str, int] = {}
    for query in queries:
        qdir = args.full_root / f"query_{query['id']:02d}"
        item = classify(qdir)
        item.update({"query_id": query["id"], "topic": query["topic"], "dir": str(qdir)})
        by_query[f"query_{query['id']:02d}"] = item
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    report = {
        "status": "complete" if counts.get("success", 0) == len(queries) else "incomplete",
        "full_root": str(args.full_root),
        "query_count": len(queries),
        "counts": counts,
        "successful_query_ids": [
            item["query_id"] for item in by_query.values() if item["status"] == "success"
        ],
        "failed_or_incomplete_query_ids": [
            item["query_id"] for item in by_query.values() if item["status"] != "success"
        ],
        "queries": by_query,
    }
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": report["status"],
                "query_count": report["query_count"],
                "counts": report["counts"],
                "successful_query_ids": report["successful_query_ids"],
            },
            indent=2,
        )
    )
    if args.strict and report["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
