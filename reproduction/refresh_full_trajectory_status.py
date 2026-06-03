#!/usr/bin/env python3
"""Refresh tracked full-trajectory status files from an audit JSON snapshot."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_AUDIT = ROOT / "artifacts" / "remote_fetch" / "full_trajectories" / "full_trajectory_audit_latest.json"
DEFAULT_JSON = ROOT / "full_trajectory_status.json"
DEFAULT_MD = ROOT / "full_trajectory_status.md"
DEFAULT_DATE = "2026-06-04"


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def title_from_report(path: Path) -> str:
    text = read_text(path)
    for line in text.splitlines():
        cleaned = line.strip().lstrip("#").strip()
        if cleaned:
            return cleaned
    return ""


def thread_id_from_stdout(stdout: str) -> str:
    match = re.search(r"Thread:\s*([0-9a-f]+)", stdout)
    return match.group(1) if match else ""


def workspace_from_stdout(stdout: str, query_id: int) -> str:
    match = re.search(r"Workspace:\s*(.+)", stdout)
    if not match:
        return f"runs/repro-query-{query_id:02d}"
    workspace = match.group(1).strip()
    marker = "EvoScientist-repro/"
    if marker in workspace:
        return workspace.split(marker, 1)[1]
    return workspace


def command_for_query(query_id: int, status: str) -> str:
    if query_id == 1:
        return (
            "EVOSCI_QUERY_TIMEOUT=900 "
            "EVOSCI_QUERY_EXTRA_ARGS='--stream-logs --output-dir "
            "reproduction/artifacts/full_trajectories/EvoScientist' "
            "reproduction/ssh_ubuntu_run.sh query-bg 1"
        )
    if query_id == 4 and status == "success":
        return (
            "EVOSCI_QUERY_TIMEOUT=2400 "
            "EVOSCI_QUERY_EXTRA_ARGS='--query-id 4 --force-proposal "
            "--stream-logs --idle-timeout 900 --output-dir "
            "reproduction/artifacts/full_trajectories/EvoScientist' "
            "reproduction/ssh_ubuntu_run.sh query-bg 4"
        )
    if query_id in {2, 3}:
        return (
            "EVOSCI_QUERY_TIMEOUT=1200 "
            "EVOSCI_QUERY_EXTRA_ARGS='--force-proposal --stream-logs "
            "--output-dir reproduction/artifacts/full_trajectories/EvoScientist' "
            f"reproduction/ssh_ubuntu_run.sh query-bg {query_id}"
        )
    return (
        "EVOSCI_QUERY_TIMEOUT=1200 "
        "EVOSCI_QUERY_EXTRA_ARGS='--query-ids 6,7,8,9,10,11,12,13,14,15,"
        "16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --force-proposal "
        "--stream-logs --idle-timeout 600 --output-dir "
        "reproduction/artifacts/full_trajectories/EvoScientist' "
        "reproduction/ssh_ubuntu_run.sh batch-bg 30"
    )


def success_entry(query: dict[str, Any]) -> dict[str, Any]:
    qid = query["query_id"]
    qdir = Path(query["dir"])
    stdout = read_text(qdir / "stdout.txt")
    final_report = qdir / "final_report.md"
    return {
        "query_id": qid,
        "topic": query["topic"],
        "mode": "full tool-enabled with isolated --mode run workspace",
        "remote_host": "ubuntu-heshi",
        "command": command_for_query(qid, "success"),
        "manifest_status": "ok",
        "thread_id": thread_id_from_stdout(stdout),
        "workspace": workspace_from_stdout(stdout, qid),
        "output_dir": query["dir"],
        "artifact_files": query["files"],
        "usage": query.get("usage"),
        "trace_indicators": query.get("trace_indicators", {}),
        "final_report": {
            "title": title_from_report(final_report),
            "bytes": query["files"]["final_report.md"]["bytes"],
            "sections_detected": query.get("sections_detected", []),
        },
    }


def incomplete_entry(query: dict[str, Any]) -> dict[str, Any]:
    qid = query["query_id"]
    return {
        "query_id": qid,
        "topic": query["topic"],
        "status": query["status"],
        "reason": query["reason"],
        "workspace": f"runs/repro-query-{qid:02d}",
        "output_dir": query["dir"],
        "artifact_files": query["files"],
        "usage": query.get("usage"),
    }


def build_status(audit: dict[str, Any], date: str) -> dict[str, Any]:
    queries = list(audit["queries"].values())
    successes = [query for query in queries if query["status"] == "success"]
    incomplete = [query for query in queries if query["status"] != "success"]
    success_ids = [query["query_id"] for query in successes]
    incomplete_ids = [query["query_id"] for query in incomplete]
    return {
        "date": date,
        "purpose": "Record full tool-enabled EvoScientist trajectory reproduction attempts for paper queries.",
        "remote_host": "ubuntu-heshi",
        "audit": {
            "generated_from": "reproduction/artifacts/remote_fetch/full_trajectories/full_trajectory_audit_latest.json",
            "status": audit["status"],
            "query_count": audit["query_count"],
            "counts": audit["counts"],
            "successful_query_ids": success_ids,
            "failed_or_incomplete_query_ids": incomplete_ids,
        },
        "full_trajectory_counts": {
            "successful_final_reports": len(successes),
            "attempted_queries": [query["query_id"] for query in queries],
            "pending_queries": [],
        },
        "successful_queries": {
            f"query_{query['query_id']:02d}": success_entry(query) for query in successes
        },
        "incomplete_queries": {
            f"query_{query['query_id']:02d}": incomplete_entry(query) for query in incomplete
        },
        "limitations": [
            (
                "Queries "
                + ", ".join(str(item) for item in success_ids)
                + " have successful full tool-enabled trajectories with final_report.md."
            ),
            (
                "Queries "
                + ", ".join(str(item) for item in incomplete_ids)
                + " remain non-successful in the latest fetched audit snapshot."
            ),
            "The run used DeepSeek configuration rather than the paper-matched Gemini/Claude setup.",
            "Tavily search was unavailable, so the research-agent behavior may differ from paper settings.",
            "This is still not the full 7-baseline paper-level Table 1 reproduction.",
        ],
    }


def render_md(status: dict[str, Any]) -> str:
    audit = status["audit"]
    lines = [
        "# Full Trajectory Status",
        "",
        f"Date: {status['date']}",
        "",
        "## Audit Summary",
        "",
        f"Audit status: `{audit['status']}`",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for name, count in audit["counts"].items():
        lines.append(f"| {name} | {count} |")
    lines.extend(
        [
            "",
            f"Successful query ids: `{audit['successful_query_ids']}`",
            "",
            "## Successful Full Trajectories",
            "",
        ]
    )
    for key, item in status["successful_queries"].items():
        usage = item.get("usage") or {}
        lines.extend(
            [
                f"Query {item['query_id']} status: `ok`",
                "",
                f"Title: {item['final_report']['title']}",
                "",
                f"Output directory: `{item['output_dir']}`",
                "",
                (
                    "Token usage: "
                    f"{usage.get('input_tokens', 'unknown')} input / "
                    f"{usage.get('output_tokens', 'unknown')} output"
                ),
                "",
                f"Command: `{item['command']}`",
                "",
                "- `final_report.md` exists and is "
                f"{item['final_report']['bytes']:,} bytes.",
                "- isolated workspace was "
                f"`{item['workspace']}`.",
                "",
            ]
        )
    lines.extend(["## Current Non-Successful Full Trajectories", ""])
    for key, item in status["incomplete_queries"].items():
        lines.append(f"- Query {item['query_id']}: {item['reason']}")
    lines.extend(["", "## Limitations"])
    for limitation in status["limitations"]:
        lines.append(f"- {limitation}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-json", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--date", default=DEFAULT_DATE)
    args = parser.parse_args()

    audit = json.loads(args.audit_json.read_text(encoding="utf-8"))
    status = build_status(audit, args.date)
    args.output_json.write_text(json.dumps(status, indent=2), encoding="utf-8")
    args.output_md.write_text(render_md(status), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status["audit"]["status"],
                "counts": status["audit"]["counts"],
                "successful_query_ids": status["audit"]["successful_query_ids"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
