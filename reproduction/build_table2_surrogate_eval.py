#!/usr/bin/env python3
"""Build Table 2 input records and Monica/Gemini surrogate labels.

This does not create the paper's human PhD labels. It prepares the actual
Table 2 comparison input package and a clearly marked LLM-surrogate label set
from completed swapped Monica/Gemini judge outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import aggregate_human_labels
from build_paper_level_evidence_runbook import DIMENSIONS, HUMAN_BASELINES, human_inputs, slug


ROOT = Path(__file__).resolve().parent
TARGET_SYSTEM = "EvoScientist"
DEFAULT_ARTIFACTS = ROOT / "artifacts"
SURROGATE_ANNOTATORS = [
    "monica_gemini_forward_surrogate",
    "monica_gemini_reverse_surrogate",
    "monica_gemini_mean_surrogate",
]


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def canonical_id(query_id: int, system_a: str, system_b: str) -> str:
    return f"q{query_id:02d}__{system_a}__vs__{system_b}"


def score_pair(record: dict[str, Any], dim: str, baseline: str) -> tuple[float, float]:
    sys1 = record["assistant_1_system"]
    sys2 = record["assistant_2_system"]
    if {sys1, sys2} != {TARGET_SYSTEM, baseline}:
        raise ValueError(f"unexpected systems in {record['comparison_id']}: {sys1}, {sys2}")
    evo_scores = record["assistant_1"] if sys1 == TARGET_SYSTEM else record["assistant_2"]
    baseline_scores = record["assistant_2"] if sys1 == TARGET_SYSTEM else record["assistant_1"]
    return float(evo_scores[dim]), float(baseline_scores[dim])


def winner_from_scores(evo_score: float, baseline_score: float) -> str:
    if evo_score == baseline_score:
        return "tie"
    return "assistant_1" if evo_score > baseline_score else "assistant_2"


def build_labels(judge_outputs: dict[str, dict[str, Any]], inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = []
    for item in inputs:
        qid = int(item["query_id"])
        baseline = item["baseline"]
        forward_id = canonical_id(qid, TARGET_SYSTEM, baseline)
        reverse_id = canonical_id(qid, baseline, TARGET_SYSTEM)
        forward = judge_outputs[forward_id]
        reverse = judge_outputs[reverse_id]
        for dim in DIMENSIONS:
            forward_evo, forward_base = score_pair(forward, dim, baseline)
            reverse_evo, reverse_base = score_pair(reverse, dim, baseline)
            mean_evo = (forward_evo + reverse_evo) / 2.0
            mean_base = (forward_base + reverse_base) / 2.0
            label_specs = [
                (
                    SURROGATE_ANNOTATORS[0],
                    winner_from_scores(forward_evo, forward_base),
                    [forward_id],
                    {"evo_score": forward_evo, "baseline_score": forward_base},
                ),
                (
                    SURROGATE_ANNOTATORS[1],
                    winner_from_scores(reverse_evo, reverse_base),
                    [reverse_id],
                    {"evo_score": reverse_evo, "baseline_score": reverse_base},
                ),
                (
                    SURROGATE_ANNOTATORS[2],
                    winner_from_scores(mean_evo, mean_base),
                    [forward_id, reverse_id],
                    {"evo_score": mean_evo, "baseline_score": mean_base},
                ),
            ]
            for annotator_id, winner, source_ids, scores in label_specs:
                labels.append(
                    {
                        "comparison_id": item["comparison_id"],
                        "annotator_id": annotator_id,
                        "dimension": dim,
                        "winner": winner,
                        "evaluator_type": "llm_surrogate",
                        "source_provider": "monica",
                        "source_model": "gemini-3-flash-preview",
                        "source_comparison_ids": source_ids,
                        "scores": scores,
                        "caveat": "LLM-surrogate label derived from Table 1 judge outputs; not a human PhD annotation.",
                    }
                )
    return labels


def write_aggregate(inputs_path: Path, labels_path: Path, output_json: Path, output_csv: Path) -> dict[str, Any]:
    result = aggregate_human_labels.aggregate(
        aggregate_human_labels.load_jsonl(inputs_path),
        aggregate_human_labels.load_jsonl(labels_path),
        TARGET_SYSTEM,
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result["summary"], indent=2), encoding="utf-8")
    with output_csv.open("w", encoding="utf-8", newline="") as f:
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
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result["rows"])
    return result["summary"]


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Table 2 Monica/Gemini Surrogate Evaluation Report",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Paper-exact: `{str(report['paper_exact']).lower()}`",
        "",
        "This report prepares the Table 2 comparison inputs and aggregates",
        "Monica/Gemini-derived surrogate labels. It does not replace the paper's",
        "three PhD-level human annotators.",
        "",
        "## Coverage",
        "",
        f"- Inputs: {report['input_records']}",
        f"- Surrogate labels: {report['surrogate_label_records']}",
        f"- Baselines: {', '.join(report['baselines'])}",
        f"- Surrogate annotators: {', '.join(report['surrogate_annotators'])}",
        "",
        "## Aggregate",
        "",
        "| Baseline | Clarity gap | Novelty gap | Feasibility gap | Relevance gap | Avg gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for baseline in report["baselines"]:
        item = report["aggregate"]["baselines"][baseline]
        dims = item["dimensions"]
        lines.append(
            "| {baseline} | {clarity} | {novelty} | {feasibility} | {relevance} | {avg} |".format(
                baseline=baseline,
                clarity=dims["Clarity"]["gap"],
                novelty=dims["Novelty"]["gap"],
                feasibility=dims["Feasibility"]["gap"],
                relevance=dims["Relevance"]["gap"],
                avg=item["avg_gap"],
            )
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Human-eval inputs: `{report['artifacts']['inputs']}`",
            f"- Surrogate labels: `{report['artifacts']['surrogate_labels']}`",
            f"- Surrogate aggregate JSON: `{report['artifacts']['surrogate_aggregate_json']}`",
            f"- Surrogate aggregate CSV: `{report['artifacts']['surrogate_aggregate_csv']}`",
            "",
            "## Caveats",
            "",
        ]
    )
    for caveat in report["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--date", default="2026-06-04")
    parser.add_argument("--output-report-json", type=Path, default=ROOT / "table2_surrogate_monica_report.json")
    parser.add_argument("--output-report-md", type=Path, default=ROOT / "table2_surrogate_monica_report.md")
    args = parser.parse_args()

    human_root = args.artifacts_root / "human_evaluation"
    inputs = human_inputs(load_queries())
    for item in inputs:
        for key in ["answer_a", "answer_b"]:
            path = ROOT.parent / item[key]
            if not path.is_file():
                raise FileNotFoundError(path)

    judge_records = load_jsonl(args.artifacts_root / "judge_outputs" / "results.jsonl")
    judge_outputs = {record["comparison_id"]: record for record in judge_records}
    expected_ids = {
        canonical_id(query_id, system_a, system_b)
        for query_id in range(1, 31)
        for baseline in HUMAN_BASELINES
        for system_a, system_b in [(TARGET_SYSTEM, baseline), (baseline, TARGET_SYSTEM)]
    }
    missing = sorted(expected_ids - set(judge_outputs))
    if missing:
        raise SystemExit(json.dumps({"status": "incomplete", "missing_judge_outputs": missing}, indent=2))

    inputs_path = human_root / "inputs.jsonl"
    surrogate_labels_path = human_root / "surrogate_labels.jsonl"
    surrogate_aggregate_json = human_root / "surrogate_aggregate.json"
    surrogate_aggregate_csv = human_root / "surrogate_aggregate.csv"
    labels = build_labels(judge_outputs, inputs)
    write_jsonl(inputs_path, inputs)
    write_jsonl(surrogate_labels_path, labels)
    aggregate = write_aggregate(
        inputs_path,
        surrogate_labels_path,
        surrogate_aggregate_json,
        surrogate_aggregate_csv,
    )
    report = {
        "date": args.date,
        "status": "complete",
        "paper_exact": False,
        "completion_scope": "table2_surrogate_llm_evaluation",
        "input_records": len(inputs),
        "surrogate_label_records": len(labels),
        "baselines": HUMAN_BASELINES,
        "dimensions": DIMENSIONS,
        "surrogate_annotators": SURROGATE_ANNOTATORS,
        "aggregate": aggregate,
        "artifacts": {
            "inputs": str(inputs_path.relative_to(ROOT)),
            "surrogate_labels": str(surrogate_labels_path.relative_to(ROOT)),
            "surrogate_aggregate_json": str(surrogate_aggregate_json.relative_to(ROOT)),
            "surrogate_aggregate_csv": str(surrogate_aggregate_csv.relative_to(ROOT)),
        },
        "caveats": [
            "This is an LLM-surrogate Table 2 evaluation, not the paper's human evaluation.",
            "No `labels.jsonl` or `aggregate.json` human-label artifact is written by this script.",
            "The paper-level audit should remain incomplete until real human labels are imported.",
        ],
    }
    args.output_report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_report_md.write_text(render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "inputs": len(inputs),
                "surrogate_labels": len(labels),
                "output_report": str(args.output_report_json),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
