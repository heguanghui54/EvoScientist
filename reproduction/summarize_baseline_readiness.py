#!/usr/bin/env python3
"""Summarize Table 1 baseline readiness from local probe artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "baseline_readiness_matrix.json"
DEFAULT_OUTPUT_MD = ROOT / "baseline_readiness_matrix.md"
BASELINES = [
    ("Virtual Scientist", "virtual_scientist_baseline_probe.json"),
    ("AI-Researcher", "ai_researcher_baseline_probe.json"),
    ("InternAgent", "internagent_baseline_probe.json"),
    ("AI Scientist-v2", "ai_scientist_v2_baseline_probe.json"),
    ("Hypogenic", "hypogenic_baseline_probe.json"),
    ("Novix", "novix_baseline_probe.json"),
    ("K-Dense", "k_dense_baseline_probe.json"),
]
DIRECT_STATUSES = {"qa_drop_in_candidate", "ideation_adapter_candidate", "local_web_api_adapter_candidate"}
ADAPTER_STATUSES = {
    "open_source_platform_not_drop_in",
    "not_drop_in",
    "hosted_competition_adapter_candidate",
    "hosted_ui_adapter_candidate",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def readiness_class(probe: dict[str, Any]) -> str:
    if probe.get("paper_exact_status") == "paper_exact":
        return "paper_exact_available"
    status = probe.get("evo_table1_drop_in_status")
    if status in DIRECT_STATUSES and probe.get("direct_30_query_runner_available"):
        return "replacement_direct_or_near_direct"
    if status in ADAPTER_STATUSES:
        return "replacement_adapter_required"
    return "not_reproducible_from_public_artifacts"


def build_matrix(args: argparse.Namespace) -> dict[str, Any]:
    inventory = load_json(args.baseline_inventory)
    inventory_by_name = {item["name"]: item for item in inventory["baselines"]}
    rows = []
    counts = {
        "paper_exact_available": 0,
        "replacement_direct_or_near_direct": 0,
        "replacement_adapter_required": 0,
        "not_reproducible_from_public_artifacts": 0,
    }
    for name, probe_file in BASELINES:
        probe_path = ROOT / probe_file
        probe = load_json(probe_path)
        item = inventory_by_name[name]
        klass = readiness_class(probe)
        counts[klass] += 1
        rows.append(
            {
                "baseline": name,
                "probe": f"reproduction/{probe_file}",
                "public_entrypoint_status": item["public_entrypoint_status"],
                "probe_status": probe.get("evo_table1_drop_in_status"),
                "paper_exact_status": probe.get("paper_exact_status") or "not_paper_exact",
                "direct_30_query_runner_available": bool(
                    probe.get("direct_30_query_runner_available")
                ),
                "table1_raw_outputs_available": bool(item["table1_raw_outputs_available"]),
                "readiness_class": klass,
                "rerun_path": item["rerun_path"],
            }
        )
    return {
        "date": args.date,
        "paper": "arXiv:2603.08127",
        "baseline_count": len(rows),
        "rows": rows,
        "counts": counts,
        "paper_exact_ready": counts["paper_exact_available"] == len(rows),
        "replacement_candidates": [
            row["baseline"]
            for row in rows
            if row["readiness_class"]
            in {"replacement_direct_or_near_direct", "replacement_adapter_required"}
        ],
        "exact_reproduction_blocker": (
            "No Table 1 baseline has public raw 30-query outputs or the paper's "
            "Gemini-3-flash judge records; exact Table 1 reproduction still "
            "requires author-provided outputs or a full rerun/import of every baseline."
        ),
        "next_gate": ".venv/bin/python reproduction/audit_paper_level_completion.py --strict",
    }


def render_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# Baseline Readiness Matrix",
        "",
        f"Date: {matrix['date']}",
        f"Paper: {matrix['paper']}",
        "",
        "This matrix summarizes the seven Table 1 baseline probes. It separates",
        "paper-exact evidence from replacement rerun paths.",
        "",
        "## Summary",
        "",
    ]
    for key, value in matrix["counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            f"- paper_exact_ready: {matrix['paper_exact_ready']}",
            "",
            "## Matrix",
            "",
            "| Baseline | Probe status | Direct 30-query runner | Readiness | Raw Table 1 outputs |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in matrix["rows"]:
        lines.append(
            "| {baseline} | `{status}` | {direct} | `{readiness}` | {raw} |".format(
                baseline=row["baseline"],
                status=row["probe_status"],
                direct="yes" if row["direct_30_query_runner_available"] else "no",
                readiness=row["readiness_class"],
                raw="yes" if row["table1_raw_outputs_available"] else "no",
            )
        )
    lines.extend(["", "## Exact Reproduction Blocker", "", matrix["exact_reproduction_blocker"], ""])
    lines.extend(["## Next Gate", "", "```bash", matrix["next_gate"], "```", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-inventory", type=Path, default=ROOT / "paper_baseline_availability.json")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--date", default="2026-06-04")
    args = parser.parse_args()

    matrix = build_matrix(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(matrix), encoding="utf-8")
    print(json.dumps({
        "baseline_count": matrix["baseline_count"],
        "paper_exact_ready": matrix["paper_exact_ready"],
        "counts": matrix["counts"],
    }, indent=2))


if __name__ == "__main__":
    main()
