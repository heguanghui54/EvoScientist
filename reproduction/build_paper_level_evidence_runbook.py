#!/usr/bin/env python3
"""Build runbooks for Table 2, Table 3, and Figure 2 paper-level evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = ROOT / "paper_level_evidence_runbook"
HUMAN_BASELINES = ["InternAgent", "AI Scientist-v2", "Novix", "K-Dense"]
ABLATION_VARIANTS = ["-IDE", "-IVE", "-all"]
DIMENSIONS = ["Novelty", "Feasibility", "Relevance", "Clarity"]
ANNOTATORS = ["phd_annotator_1", "phd_annotator_2", "phd_annotator_3"]
STAGES = ["stage_1", "stage_2", "stage_3", "stage_4"]
PHASES = ["before_evolution", "after_evolution"]


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=True) + "\n" for record in records),
        encoding="utf-8",
    )


def human_inputs(queries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for baseline in HUMAN_BASELINES:
        baseline_slug = slug(baseline)
        for query in queries:
            qid = query["id"]
            records.append(
                {
                    "comparison_id": f"human__{baseline_slug}__q{qid:02d}",
                    "query_id": qid,
                    "baseline": baseline,
                    "assistant_1_system": "EvoScientist",
                    "assistant_2_system": baseline,
                    "answer_a": f"reproduction/artifacts/idea_outputs/EvoScientist/query_{qid:02d}/answer.txt",
                    "answer_b": f"reproduction/artifacts/idea_outputs/{baseline}/query_{qid:02d}/answer.txt",
                    "dimensions": DIMENSIONS,
                    "topic": query["topic"],
                    "goal": query["goal"],
                }
            )
    return records


def human_label_templates(inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in inputs:
        for annotator in ANNOTATORS:
            for dimension in DIMENSIONS:
                records.append(
                    {
                        "comparison_id": item["comparison_id"],
                        "annotator_id": annotator,
                        "dimension": dimension,
                        "winner": "assistant_1|assistant_2|tie",
                        "note": "Template only. Replace winner with one valid value before copying to reproduction/artifacts/human_evaluation/labels.jsonl.",
                    }
                )
    return records


def ablation_specs(queries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    specs = {}
    variant_notes = {
        "-IDE": "Disable the idea-discovery/evolution component while preserving the rest of the paper-matched agent setup.",
        "-IVE": "Disable the idea-verification/evaluation component while preserving the rest of the paper-matched agent setup.",
        "-all": "Disable both IDE and IVE/evolution modules, leaving the non-evolving baseline variant.",
    }
    for variant in ABLATION_VARIANTS:
        specs[variant] = [
            {
                "variant": variant,
                "query_id": query["id"],
                "topic": query["topic"],
                "goal": query["goal"],
                "variant_protocol_note": variant_notes[variant],
                "expected_output_path": (
                    f"reproduction/artifacts/ablations/{variant}/system_outputs/"
                    f"query_{query['id']:02d}/answer.txt"
                ),
                "paper_exact_requirement": (
                    "Use the same paper-matched provider/tool/search configuration as the "
                    "main EvoScientist run, then judge variant vs EvoScientist with Gemini-3-flash."
                ),
            }
            for query in queries
        ]
    return specs


def code_execution_templates(queries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    trajectories = []
    logs = []
    for query in queries:
        for phase in PHASES:
            for stage in STAGES:
                trajectory_id = f"{phase}__{stage}__q{query['id']:02d}"
                trajectories.append(
                    {
                        "trajectory_id": trajectory_id,
                        "query_id": query["id"],
                        "stage": stage,
                        "proposal_id": f"query_{query['id']:02d}",
                        "phase": phase,
                        "source_required": "Generated code trajectory from the paper-matched EvoScientist code-execution experiment.",
                    }
                )
                logs.append(
                    {
                        "trajectory_id": trajectory_id,
                        "stage": stage,
                        "attempt_id": f"{trajectory_id}__attempt_01",
                        "success": "true|false",
                        "phase": phase,
                        "note": "Template only. Replace success with a boolean before copying to reproduction/artifacts/code_execution/execution_logs.jsonl.",
                    }
                )
    return trajectories, logs


def build_runbook(args: argparse.Namespace) -> dict[str, Any]:
    queries = load_queries()
    root = args.output_root
    human_root = root / "human_evaluation"
    ablation_root = root / "ablations"
    code_root = root / "code_execution"

    human_input_records = human_inputs(queries)
    human_label_records = human_label_templates(human_input_records)
    write_jsonl(human_root / "inputs_template.jsonl", human_input_records)
    write_jsonl(human_root / "labels_template.jsonl", human_label_records)

    ablation = ablation_specs(queries)
    for variant, records in ablation.items():
        variant_root = ablation_root / variant
        write_jsonl(variant_root / "variant_run_specs.jsonl", records)
        (variant_root / "system_outputs_complete_template.json").write_text(
            json.dumps(
                {
                    "variant": variant,
                    "query_count": 30,
                    "complete": False,
                    "required_output_root": f"reproduction/artifacts/ablations/{variant}/system_outputs",
                    "note": "Set complete=true only after all 30 variant outputs are present and imported into this variant artifact directory.",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    trajectories, logs = code_execution_templates(queries)
    write_jsonl(code_root / "trajectories_template.jsonl", trajectories)
    write_jsonl(code_root / "execution_logs_template.jsonl", logs)

    runbook = {
        "date": "2026-06-04",
        "paper": "arXiv:2603.08127",
        "paper_exact": False,
        "purpose": "Actionable evidence templates and acceptance commands for Table 2, Table 3, and Figure 2.",
        "human_evaluation": {
            "paper_table": "Table 2",
            "baselines": HUMAN_BASELINES,
            "comparison_count": len(human_input_records),
            "label_template_count": len(human_label_records),
            "templates": {
                "inputs": str(human_root / "inputs_template.jsonl"),
                "labels": str(human_root / "labels_template.jsonl"),
            },
            "artifact_targets": {
                "inputs": "reproduction/artifacts/human_evaluation/inputs.jsonl",
                "labels": "reproduction/artifacts/human_evaluation/labels.jsonl",
                "aggregate": "reproduction/artifacts/human_evaluation/aggregate.json",
            },
            "commands": [
                ".venv/bin/python reproduction/aggregate_human_labels.py --inputs reproduction/artifacts/human_evaluation/inputs.jsonl --labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict",
            ],
        },
        "ablation": {
            "paper_table": "Table 3",
            "variants": ABLATION_VARIANTS,
            "variant_spec_roots": {
                variant: str(ablation_root / variant) for variant in ABLATION_VARIANTS
            },
            "artifact_root": "reproduction/artifacts/ablations",
            "commands": [
                ".venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict",
                ".venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all",
            ],
        },
        "code_execution": {
            "paper_figure": "Figure 2",
            "trajectory_template_count": len(trajectories),
            "execution_log_template_count": len(logs),
            "templates": {
                "trajectories": str(code_root / "trajectories_template.jsonl"),
                "execution_logs": str(code_root / "execution_logs_template.jsonl"),
            },
            "artifact_targets": {
                "trajectories": "reproduction/artifacts/code_execution/trajectories.jsonl",
                "execution_logs": "reproduction/artifacts/code_execution/execution_logs.jsonl",
                "summary": "reproduction/artifacts/code_execution/summary.json",
            },
            "commands": [
                ".venv/bin/python reproduction/aggregate_code_execution.py --logs reproduction/artifacts/code_execution/execution_logs.jsonl --output-json reproduction/artifacts/code_execution/summary.json --output-csv reproduction/artifacts/code_execution/summary.csv --strict",
                ".venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/code_execution/summary.json --section figure2_code_execution --require-all",
            ],
        },
        "acceptance_commands": [
            ".venv/bin/python reproduction/verify_paper_artifact_schema.py --strict",
            ".venv/bin/python reproduction/audit_paper_level_completion.py --strict",
        ],
        "caveat": (
            "These files are templates and runbooks, not completed paper artifacts. "
            "Copy or generate real records under reproduction/artifacts only after "
            "collecting paper-level human labels, ablation outputs, and execution logs."
        ),
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (root / "paper_level_evidence_runbook.json").write_text(
        json.dumps(runbook, indent=2),
        encoding="utf-8",
    )
    (root / "paper_level_evidence_runbook.md").write_text(render_markdown(runbook), encoding="utf-8")
    return runbook


def render_markdown(runbook: dict[str, Any]) -> str:
    lines = [
        "# Paper-Level Evidence Runbook",
        "",
        f"Date: {runbook['date']}",
        f"Paper: {runbook['paper']}",
        f"Paper-exact: `{str(runbook['paper_exact']).lower()}`",
        "",
        runbook["caveat"],
        "",
        "## Table 2 Human Evaluation",
        "",
        f"- Baselines: {', '.join(runbook['human_evaluation']['baselines'])}",
        f"- Pairwise comparison templates: {runbook['human_evaluation']['comparison_count']}",
        f"- Raw label templates: {runbook['human_evaluation']['label_template_count']}",
        "",
        "```bash",
        *runbook["human_evaluation"]["commands"],
        "```",
        "",
        "## Table 3 Ablation",
        "",
        f"- Variants: {', '.join(runbook['ablation']['variants'])}",
        "",
        "```bash",
        *runbook["ablation"]["commands"],
        "```",
        "",
        "## Figure 2 Code Execution",
        "",
        f"- Trajectory templates: {runbook['code_execution']['trajectory_template_count']}",
        f"- Execution-log templates: {runbook['code_execution']['execution_log_template_count']}",
        "",
        "```bash",
        *runbook["code_execution"]["commands"],
        "```",
        "",
        "## Acceptance",
        "",
        "```bash",
        *runbook["acceptance_commands"],
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    runbook = build_runbook(args)
    print(
        json.dumps(
            {
                "status": "generated",
                "output_root": str(args.output_root),
                "human_comparisons": runbook["human_evaluation"]["comparison_count"],
                "ablation_variants": runbook["ablation"]["variants"],
                "code_execution_templates": runbook["code_execution"]["execution_log_template_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
