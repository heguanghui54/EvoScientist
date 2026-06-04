#!/usr/bin/env python3
"""Build the seven-baseline replacement Table 1 judge summary.

The paper's original raw baseline outputs and original judge records are not
public. This script combines the completed replacement/proxy reruns into the
canonical Table 1 artifact paths expected by the paper-level audit.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from audit_reproduction_artifacts import DEFAULT_BASELINES, DIMENSIONS, expected_comparison_ids


ROOT = Path(__file__).resolve().parent
DEFAULT_ARTIFACTS = ROOT / "artifacts"
TARGET_SYSTEM = "EvoScientist"
BASELINE_SOURCES = {
    "Virtual Scientist": {
        "input": "evosci_vs_virtual_scientist_proxy_monica.jsonl",
        "output": "evosci_vs_virtual_scientist_proxy_monica.jsonl",
    },
    "AI-Researcher": {
        "input": "evosci_vs_ai_researcher_proxy_monica.jsonl",
        "output": "evosci_vs_ai_researcher_proxy_monica.jsonl",
    },
    "InternAgent": {
        "input": "table1_existing_baselines_monica.jsonl",
        "output": "table1_existing_baselines_monica.jsonl",
    },
    "AI Scientist-v2": {
        "input": "table1_existing_baselines_monica.jsonl",
        "output": "table1_existing_baselines_monica.jsonl",
    },
    "Hypogenic": {
        "input": "evosci_vs_hypogenic_proxy_monica.jsonl",
        "output": "evosci_vs_hypogenic_proxy_monica.jsonl",
    },
    "Novix": {
        "input": "evosci_vs_novix_proxy_monica.jsonl",
        "output": "evosci_vs_novix_proxy_monica.jsonl",
    },
    "K-Dense": {
        "input": "evosci_vs_k_dense_proxy_monica.jsonl",
        "output": "evosci_vs_k_dense_proxy_monica.jsonl",
    },
}


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def record_baseline(record: dict[str, Any]) -> str | None:
    systems = {record.get("assistant_1_system"), record.get("assistant_2_system")}
    if TARGET_SYSTEM not in systems:
        return None
    others = [system for system in systems if system != TARGET_SYSTEM]
    return others[0] if len(others) == 1 else None


def collect_records(root: Path, folder: str, key: str) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for baseline in DEFAULT_BASELINES:
        source_name = BASELINE_SOURCES[baseline][key]
        source_path = root / folder / source_name
        for record in load_jsonl(source_path):
            if record_baseline(record) != baseline:
                continue
            comparison_id = record.get("comparison_id")
            if not comparison_id:
                raise ValueError(f"missing comparison_id in {source_path}")
            if comparison_id in by_id:
                raise ValueError(f"duplicate comparison_id {comparison_id} from {source_path}")
            by_id[comparison_id] = record
    return by_id


def ordered_ids(queries: list[dict[str, Any]]) -> list[str]:
    ids = []
    for query in queries:
        qid = query["id"]
        for baseline in DEFAULT_BASELINES:
            ids.append(f"q{qid:02d}__{TARGET_SYSTEM}__vs__{baseline}")
            ids.append(f"q{qid:02d}__{baseline}__vs__{TARGET_SYSTEM}")
    return ids


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def outcome(target_score: float, other_score: float) -> str:
    if target_score == other_score:
        return "tie"
    return "win" if target_score > other_score else "lose"


def pct(value: int, denom: int) -> float:
    return round(100.0 * value / denom, 2) if denom else 0.0


def aggregate(records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    counts: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: {dim: {"win": 0, "tie": 0, "lose": 0} for dim in DIMENSIONS}
    )
    for record in records:
        sys1 = record["assistant_1_system"]
        sys2 = record["assistant_2_system"]
        baseline = sys2 if sys1 == TARGET_SYSTEM else sys1
        target_scores = record["assistant_1"] if sys1 == TARGET_SYSTEM else record["assistant_2"]
        other_scores = record["assistant_2"] if sys1 == TARGET_SYSTEM else record["assistant_1"]
        for dim in DIMENSIONS:
            result = outcome(float(target_scores[dim]), float(other_scores[dim]))
            counts[baseline][dim][result] += 1

    rows = []
    summary = {
        "target_system": TARGET_SYSTEM,
        "tie_threshold": 0.0,
        "raw_records": len(records),
        "baselines": {},
    }
    for baseline in DEFAULT_BASELINES:
        dim_rows = {}
        gaps = []
        for dim in DIMENSIONS:
            c = counts[baseline][dim]
            denom = c["win"] + c["tie"] + c["lose"]
            win_pct = pct(c["win"], denom)
            tie_pct = pct(c["tie"], denom)
            lose_pct = pct(c["lose"], denom)
            gap = round(win_pct - lose_pct, 2)
            gaps.append(gap)
            row = {
                "baseline": baseline,
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
            dim_rows[dim] = row
        summary["baselines"][baseline] = {
            "dimensions": dim_rows,
            "avg_gap": round(sum(gaps) / len(gaps), 2),
        }
    return summary, rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
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
        writer.writerows(rows)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Table 1 Replacement All-Baselines Monica/Gemini Judge Report",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Paper-exact: `{str(report['paper_exact']).lower()}`",
        f"Completion scope: `{report['completion_scope']}`",
        "",
        "This is a full seven-baseline replacement/proxy Table 1 summary. It covers",
        "30 recovered queries x 7 baselines x 2 swapped orders = 420 pairwise judge",
        "records, but it is not the paper's original raw baseline-output package.",
        "",
        "## Aggregate",
        "",
        "| Baseline | Clarity gap | Novelty gap | Feasibility gap | Relevance gap | Avg gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for baseline in DEFAULT_BASELINES:
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
            "## Canonical Artifacts",
            "",
            f"- Judge inputs: `{report['artifacts']['judge_inputs']}`",
            f"- Judge outputs: `{report['artifacts']['judge_outputs']}`",
            f"- Aggregate CSV: `{report['artifacts']['aggregate_csv']}`",
            f"- Aggregate JSON: `{report['artifacts']['aggregate_json']}`",
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
    parser.add_argument("--output-report-json", type=Path, default=ROOT / "table1_replacement_all_baselines_monica_report.json")
    parser.add_argument("--output-report-md", type=Path, default=ROOT / "table1_replacement_all_baselines_monica_report.md")
    parser.add_argument("--date", default="2026-06-04")
    args = parser.parse_args()

    queries = load_queries()
    expected = expected_comparison_ids(
        queries=queries,
        target_system=TARGET_SYSTEM,
        baselines=DEFAULT_BASELINES,
        swapped=True,
    )
    order = ordered_ids(queries)
    input_by_id = collect_records(args.artifacts_root, "judge_inputs", "input")
    output_by_id = collect_records(args.artifacts_root, "judge_outputs", "output")
    missing_inputs = sorted(expected - set(input_by_id))
    missing_outputs = sorted(expected - set(output_by_id))
    if missing_inputs or missing_outputs:
        raise SystemExit(
            json.dumps(
                {
                    "status": "incomplete",
                    "missing_inputs": missing_inputs,
                    "missing_outputs": missing_outputs,
                },
                indent=2,
            )
        )

    input_records = [input_by_id[item] for item in order]
    output_records = [output_by_id[item] for item in order]
    canonical_input = args.artifacts_root / "judge_inputs" / "results.jsonl"
    canonical_output = args.artifacts_root / "judge_outputs" / "results.jsonl"
    canonical_csv = args.artifacts_root / "tables" / "idea_generation_win_tie_lose.csv"
    canonical_json = args.artifacts_root / "tables" / "idea_generation_win_tie_lose.json"
    write_jsonl(canonical_input, input_records)
    write_jsonl(canonical_output, output_records)
    summary, rows = aggregate(output_records)
    write_csv(canonical_csv, rows)
    canonical_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = {
        "date": args.date,
        "status": "complete",
        "completion_scope": "replacement_table1_all_baselines",
        "paper_exact": False,
        "target_system": TARGET_SYSTEM,
        "baseline_mode": "mixed_replacement_and_proxy_baselines",
        "covered_baselines": DEFAULT_BASELINES,
        "query_count": len(queries),
        "expected_pairwise_records": len(expected),
        "judge": {
            "provider": "monica",
            "model": "gemini-3-flash-preview",
            "input_records": len(input_records),
            "output_records": len(output_records),
        },
        "artifacts": {
            "judge_inputs": str(canonical_input.relative_to(ROOT)),
            "judge_outputs": str(canonical_output.relative_to(ROOT)),
            "aggregate_csv": str(canonical_csv.relative_to(ROOT)),
            "aggregate_json": str(canonical_json.relative_to(ROOT)),
        },
        "source_files": BASELINE_SOURCES,
        "aggregate": summary,
        "caveats": [
            "This is a replacement/proxy rerun, not the original paper's raw Table 1 baseline outputs.",
            "Virtual Scientist, AI-Researcher, Hypogenic, Novix, and K-Dense use proxy replacement prompts because public paper-exact runners or raw outputs were unavailable.",
            "InternAgent and AI Scientist-v2 are replacement adapter runs, not author-provided paper artifacts.",
            "The judge is Monica/Gemini `gemini-3-flash-preview`, not a verified author-side `gemini-3-flash` transcript.",
        ],
    }
    args.output_report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_report_md.write_text(render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "records": len(output_records),
                "baselines": len(DEFAULT_BASELINES),
                "aggregate_json": str(canonical_json),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
