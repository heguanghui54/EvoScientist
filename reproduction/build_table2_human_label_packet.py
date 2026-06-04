#!/usr/bin/env python3
"""Build a fillable Table 2 human-label packet.

The packet is meant for real annotators. It embeds the comparison text in a
review JSONL, plus a CSV sheet that can later be imported into labels.jsonl.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_paper_level_evidence_runbook import ANNOTATORS, DIMENSIONS


ROOT = Path(__file__).resolve().parent
DEFAULT_HUMAN_ROOT = ROOT / "artifacts" / "human_evaluation"
DEFAULT_PACKET_ROOT = DEFAULT_HUMAN_ROOT / "label_packet"
VALID_WINNERS = ["assistant_1", "assistant_2", "tie"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def read_answer(repo_root: Path, relative_path: str) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8").strip()


def preview(text: str, limit: int = 260) -> str:
    normalized = " ".join(text.split())
    return normalized if len(normalized) <= limit else normalized[: limit - 3] + "..."


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def build_review_tasks(inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    repo_root = ROOT.parent
    tasks = []
    for item in inputs:
        answer_a_text = read_answer(repo_root, item["answer_a"])
        answer_b_text = read_answer(repo_root, item["answer_b"])
        tasks.append(
            {
                "comparison_id": item["comparison_id"],
                "query_id": item["query_id"],
                "topic": item["topic"],
                "goal": item["goal"],
                "baseline": item["baseline"],
                "assistant_1_system": item["assistant_1_system"],
                "assistant_2_system": item["assistant_2_system"],
                "dimensions": item["dimensions"],
                "answer_a_path": item["answer_a"],
                "answer_b_path": item["answer_b"],
                "answer_a_text": answer_a_text,
                "answer_b_text": answer_b_text,
            }
        )
    return tasks


def write_task_csv(path: Path, tasks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "comparison_id",
                "query_id",
                "topic",
                "baseline",
                "goal",
                "assistant_1_system",
                "assistant_2_system",
                "answer_a_path",
                "answer_b_path",
                "answer_a_preview",
                "answer_b_preview",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for task in tasks:
            writer.writerow(
                {
                    "comparison_id": task["comparison_id"],
                    "query_id": task["query_id"],
                    "topic": task["topic"],
                    "baseline": task["baseline"],
                    "goal": task["goal"],
                    "assistant_1_system": task["assistant_1_system"],
                    "assistant_2_system": task["assistant_2_system"],
                    "answer_a_path": task["answer_a_path"],
                    "answer_b_path": task["answer_b_path"],
                    "answer_a_preview": preview(task["answer_a_text"]),
                    "answer_b_preview": preview(task["answer_b_text"]),
                }
            )


def write_label_template(path: Path, tasks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "comparison_id",
                "annotator_id",
                "dimension",
                "winner",
                "confidence",
                "rationale",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for task in tasks:
            for annotator_id in ANNOTATORS:
                for dimension in DIMENSIONS:
                    writer.writerow(
                        {
                            "comparison_id": task["comparison_id"],
                            "annotator_id": annotator_id,
                            "dimension": dimension,
                            "winner": "",
                            "confidence": "",
                            "rationale": "",
                        }
                    )


def render_guide(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Table 2 Human Label Packet",
            "",
            f"Date: {manifest['date']}",
            f"Paper-exact target: `{str(manifest['paper_exact_target']).lower()}`",
            "",
            "This packet is for real human annotation. It should not be filled with",
            "LLM-surrogate labels if the goal is paper-level Table 2 completion.",
            "",
            "## Files",
            "",
            f"- Review tasks with full answer text: `{manifest['files']['review_tasks_jsonl']}`",
            f"- Task index CSV: `{manifest['files']['task_index_csv']}`",
            f"- Fillable label sheet: `{manifest['files']['label_sheet_template_csv']}`",
            "",
            "## Winner Values",
            "",
            "- `assistant_1`: EvoScientist is better for the dimension.",
            "- `assistant_2`: the baseline answer is better for the dimension.",
            "- `tie`: no clear winner.",
            "",
            "## Import",
            "",
            "After replacing every blank `winner` cell in the label sheet, run:",
            "",
            "```bash",
            ".venv/bin/python reproduction/import_table2_human_label_sheet.py --sheet reproduction/artifacts/human_evaluation/label_packet/label_sheet_template.csv --output-labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict",
            "```",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human-root", type=Path, default=DEFAULT_HUMAN_ROOT)
    parser.add_argument("--packet-root", type=Path, default=DEFAULT_PACKET_ROOT)
    parser.add_argument("--date", default="2026-06-04")
    args = parser.parse_args()

    inputs_path = args.human_root / "inputs.jsonl"
    inputs = load_jsonl(inputs_path)
    tasks = build_review_tasks(inputs)
    review_jsonl = args.packet_root / "review_tasks.jsonl"
    task_csv = args.packet_root / "task_index.csv"
    label_csv = args.packet_root / "label_sheet_template.csv"
    write_jsonl(review_jsonl, tasks)
    write_task_csv(task_csv, tasks)
    write_label_template(label_csv, tasks)
    manifest = {
        "date": args.date,
        "paper_exact_target": True,
        "status": "ready_for_human_annotation",
        "comparison_count": len(tasks),
        "label_rows": len(tasks) * len(ANNOTATORS) * len(DIMENSIONS),
        "annotators": ANNOTATORS,
        "dimensions": DIMENSIONS,
        "valid_winners": VALID_WINNERS,
        "files": {
            "review_tasks_jsonl": str(review_jsonl.relative_to(ROOT)),
            "task_index_csv": str(task_csv.relative_to(ROOT)),
            "label_sheet_template_csv": str(label_csv.relative_to(ROOT)),
            "source_inputs_jsonl": str(inputs_path.relative_to(ROOT)),
        },
        "caveat": "Real human annotators must fill winners before this packet can produce paper-level labels.jsonl.",
    }
    args.packet_root.mkdir(parents=True, exist_ok=True)
    (args.packet_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (args.packet_root / "annotation_guide.md").write_text(render_guide(manifest), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "comparisons": manifest["comparison_count"],
                "label_rows": manifest["label_rows"],
                "packet_root": str(args.packet_root),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
