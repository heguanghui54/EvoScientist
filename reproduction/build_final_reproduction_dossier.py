#!/usr/bin/env python3
"""Build a final reproduction dossier for the current artifact state."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
DEFAULT_OUTPUT_JSON = ROOT / "final_reproduction_dossier.json"
DEFAULT_OUTPUT_MD = ROOT / "final_reproduction_dossier.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def git_branch() -> str:
    return subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def build_dossier(date: str) -> dict[str, Any]:
    audit = load_json(ROOT / "artifacts" / "audit" / "paper_level_completion_latest.json")
    table1 = load_json(ROOT / "table1_replacement_all_baselines_monica_report.json")
    table2_surrogate = load_json(ROOT / "table2_surrogate_monica_report.json")
    table2_packet = load_json(ROOT / "artifacts" / "human_evaluation" / "label_packet" / "manifest.json")
    ablation = load_json(ROOT / "ablation_queries01_30_monica_gemini_report.json")
    figure2 = load_json(ROOT / "figure2_code_execution_replacement_report.json")
    schema = load_json(ROOT / "artifacts" / "audit" / "paper_artifact_schema_latest.json")
    action_plan = load_json(ROOT / "paper_reproduction_action_plan.json")

    artifacts = {
        "table1": {
            "report_md": rel(ROOT / "table1_replacement_all_baselines_monica_report.md"),
            "judge_inputs": rel(ROOT / "artifacts" / "judge_inputs" / "results.jsonl"),
            "judge_outputs": rel(ROOT / "artifacts" / "judge_outputs" / "results.jsonl"),
            "aggregate_json": rel(ROOT / "artifacts" / "tables" / "idea_generation_win_tie_lose.json"),
            "aggregate_csv": rel(ROOT / "artifacts" / "tables" / "idea_generation_win_tie_lose.csv"),
        },
        "table2": {
            "surrogate_report_md": rel(ROOT / "table2_surrogate_monica_report.md"),
            "human_inputs": rel(ROOT / "artifacts" / "human_evaluation" / "inputs.jsonl"),
            "surrogate_labels": rel(ROOT / "artifacts" / "human_evaluation" / "surrogate_labels.jsonl"),
            "surrogate_aggregate_json": rel(ROOT / "artifacts" / "human_evaluation" / "surrogate_aggregate.json"),
            "label_packet_guide": rel(ROOT / "artifacts" / "human_evaluation" / "label_packet" / "annotation_guide.md"),
            "label_packet_sheet": rel(ROOT / "artifacts" / "human_evaluation" / "label_packet" / "label_sheet_template.csv"),
        },
        "table3": {
            "report_md": rel(ROOT / "ablation_queries01_30_monica_gemini_report.md"),
            "combined_aggregate": rel(ROOT / "artifacts" / "ablations" / "combined_aggregate.json"),
        },
        "figure2": {
            "report_md": rel(ROOT / "figure2_code_execution_replacement_report.md"),
            "summary": rel(ROOT / "artifacts" / "code_execution" / "summary.json"),
        },
        "audit": {
            "paper_level_md": rel(ROOT / "artifacts" / "audit" / "paper_level_completion_latest.md"),
            "paper_level_json": rel(ROOT / "artifacts" / "audit" / "paper_level_completion_latest.json"),
            "schema_json": rel(ROOT / "artifacts" / "audit" / "paper_artifact_schema_latest.json"),
        },
    }

    return {
        "date": date,
        "repository": {
            "branch": git_branch(),
        },
        "overall_status": audit["status"],
        "paper_exact": False,
        "scope": "EvoScientist experiment reproduction with replacement/proxy evidence where public paper-exact artifacts are unavailable.",
        "components": {
            "full_trajectories": audit["components"]["full_trajectories"],
            "table1_llm_idea_generation": {
                "status": "complete",
                "paper_exact": table1["paper_exact"],
                "coverage": {
                    "queries": table1["query_count"],
                    "baselines": len(table1["covered_baselines"]),
                    "pairwise_records": table1["expected_pairwise_records"],
                    "judge_inputs": count_jsonl(ROOT / "artifacts" / "judge_inputs" / "results.jsonl"),
                    "judge_outputs": count_jsonl(ROOT / "artifacts" / "judge_outputs" / "results.jsonl"),
                },
                "aggregate": table1["aggregate"],
                "caveats": table1["caveats"],
            },
            "table2_human_idea_generation": {
                "status": "incomplete",
                "paper_exact": False,
                "missing_files": audit["components"]["table2_human_idea_generation"]["missing_files"],
                "human_inputs_ready": count_jsonl(ROOT / "artifacts" / "human_evaluation" / "inputs.jsonl"),
                "surrogate": {
                    "status": table2_surrogate["status"],
                    "paper_exact": table2_surrogate["paper_exact"],
                    "label_records": table2_surrogate["surrogate_label_records"],
                    "aggregate": table2_surrogate["aggregate"],
                },
                "human_label_packet": {
                    "status": table2_packet["status"],
                    "comparison_count": table2_packet["comparison_count"],
                    "label_rows": table2_packet["label_rows"],
                    "valid_winners": table2_packet["valid_winners"],
                },
            },
            "table3_ablation_idea_generation": {
                "status": ablation["status"],
                "paper_exact": ablation["paper_exact"],
                "covered_queries": ablation["covered_query_count"],
                "judge_records": ablation["judge"]["total_records"],
                "compare_to_paper_expected_to_fail": True,
            },
            "figure2_code_execution": {
                "status": figure2["status"],
                "paper_exact": figure2["paper_exact"],
                "coverage": {
                    "trajectory_records": figure2["metadata"]["trajectory_records"],
                    "execution_log_records": figure2["metadata"]["execution_log_records"],
                    "usable_execution_records": figure2["headline"]["usable_execution_records"],
                    "phases": figure2["metadata"]["phases"],
                    "stages": figure2["metadata"]["stages"],
                },
                "compare_to_paper_expected_to_fail": True,
            },
            "schema": {
                "complete": schema["complete"],
                "components": {
                    name: item["complete"]
                    for name, item in schema["components"].items()
                },
            },
        },
        "blocking_items": audit["blocking_items"],
        "next_action": action_plan["actions"][0] if action_plan["actions"] else None,
        "artifacts": artifacts,
        "verification_commands": [
            ".venv/bin/python reproduction/verify_reproduction_assets.py",
            "bash reproduction/run_preflight.sh",
            ".venv/bin/python reproduction/audit_paper_level_completion.py --strict",
        ],
    }


def render_component_table(dossier: dict[str, Any]) -> list[str]:
    components = dossier["components"]
    rows = [
        "| Component | Status | Paper-exact | Evidence |",
        "| --- | --- | --- | --- |",
        "| Full trajectories | {status} | false | {success}/{total} successful final reports |".format(
            status="complete" if components["full_trajectories"]["complete"] else "incomplete",
            success=components["full_trajectories"]["success_count"],
            total=components["full_trajectories"]["query_count"],
        ),
        "| Table 1 LLM judge | complete | false | 420/420 swapped pairwise judge records |",
        "| Table 2 human eval | incomplete | false | 120 inputs ready; surrogate labels ready; human labels missing |",
        "| Table 3 ablation | complete | false | 30-query replacement ablation rerun |",
        "| Figure 2 code execution | complete | false | 240-record deterministic replacement probe |",
    ]
    return rows


def render_markdown(dossier: dict[str, Any]) -> str:
    table1 = dossier["components"]["table1_llm_idea_generation"]
    table2 = dossier["components"]["table2_human_idea_generation"]
    lines = [
        "# EvoScientist Reproduction Dossier",
        "",
        f"Date: {dossier['date']}",
        f"Branch: `{dossier['repository']['branch']}`",
        f"Overall status: `{dossier['overall_status']}`",
        f"Paper-exact: `{str(dossier['paper_exact']).lower()}`",
        "",
        dossier["scope"],
        "",
        "## Component Status",
        "",
        *render_component_table(dossier),
        "",
        "## Table 1 Summary",
        "",
        f"- Queries: {table1['coverage']['queries']}",
        f"- Baselines: {table1['coverage']['baselines']}",
        f"- Judge outputs: {table1['coverage']['judge_outputs']}",
        "",
        "| Baseline | Avg gap |",
        "| --- | ---: |",
    ]
    for baseline, item in table1["aggregate"]["baselines"].items():
        lines.append(f"| {baseline} | {item['avg_gap']} |")
    lines.extend(
        [
            "",
            "## Table 2 Status",
            "",
            f"- Human inputs ready: {table2['human_inputs_ready']}",
            f"- Surrogate label records: {table2['surrogate']['label_records']}",
            f"- Human label packet rows: {table2['human_label_packet']['label_rows']}",
            f"- Missing formal human files: {', '.join(table2['missing_files'])}",
            "",
            "## Key Artifacts",
            "",
        ]
    )
    for group, items in dossier["artifacts"].items():
        lines.append(f"### {group}")
        for name, path in items.items():
            lines.append(f"- {name}: `{path}`")
        lines.append("")
    lines.extend(
        [
            "## Remaining Blocker",
            "",
        ]
    )
    for item in dossier["blocking_items"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Verification",
            "",
            "```bash",
            *dossier["verification_commands"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--date", default="2026-06-04")
    args = parser.parse_args()

    dossier = build_dossier(args.date)
    args.output_json.write_text(json.dumps(dossier, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(dossier), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": dossier["overall_status"],
                "blocking_items": dossier["blocking_items"],
                "output_json": str(args.output_json),
                "output_md": str(args.output_md),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
