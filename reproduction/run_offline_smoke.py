#!/usr/bin/env python3
"""Run an offline end-to-end smoke test of the reproduction evaluation flow.

This script intentionally uses synthetic proposal and judge records. It proves
that the public-query evaluation plumbing works without spending API budget:

1. create system-output directories for EvoScientist and one baseline;
2. build swapped-order pairwise judge inputs;
3. create deterministic judge outputs;
4. aggregate Win/Tie/Lose tables;
5. write a compact smoke-test report.

The generated artifacts are not paper results and must not be cited as such.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "reproduction"
DEFAULT_OUTPUT = REPRO / "artifacts" / "offline_smoke"
DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]


def load_queries(limit: int) -> list[dict]:
    data = json.loads((REPRO / "queries.json").read_text(encoding="utf-8"))
    return data["queries"][:limit]


def write_synthetic_system_outputs(output_dir: Path, queries: list[dict], baseline: str) -> Path:
    systems_root = output_dir / "systems"
    for query in queries:
        qid = query["id"]
        topic = query["topic"]
        goal = query["goal"]
        evosci_answer = f"""# Synthetic EvoScientist proposal for query {qid}

Topic: {topic}

Goal: {goal}

Method: define a measurable benchmark, compare against two explicit baselines,
run one ablation that removes the central mechanism, and report failure cases.

Evaluation: use task-level accuracy, resource cost, and qualitative error
taxonomy. This is synthetic smoke-test content, not a real model output.
"""
        baseline_answer = f"""# Synthetic {baseline} proposal for query {qid}

Topic: {topic}

Goal: {goal}

Method: survey related work and propose a general model improvement.

Evaluation: compare results qualitatively. This is synthetic smoke-test
content, not a real baseline output.
"""
        for system, answer in {"EvoScientist": evosci_answer, baseline: baseline_answer}.items():
            qdir = systems_root / system / f"query_{qid:02d}"
            qdir.mkdir(parents=True, exist_ok=True)
            (qdir / "answer.txt").write_text(answer, encoding="utf-8")
    return systems_root


def build_judge_inputs(
    *,
    systems_root: Path,
    baseline: str,
    query_count: int,
    output_dir: Path,
) -> Path:
    judge_inputs = output_dir / "judge_inputs" / "synthetic_pairwise.jsonl"
    subprocess.run(
        [
            sys.executable,
            str(REPRO / "build_pairwise_judge_inputs.py"),
            "--systems-root",
            str(systems_root),
            "--baseline",
            baseline,
            "--limit",
            str(query_count),
            "--output",
            str(judge_inputs),
        ],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )
    return judge_inputs


def synthetic_scores(record: dict) -> dict:
    """Score EvoScientist higher in this smoke fixture, independent of order."""

    scores_by_system = {
        "EvoScientist": {
            "Clarity": 8,
            "Novelty": 7,
            "Feasibility": 8,
            "Relevance": 9,
        },
        record["assistant_1_system"]: {
            "Clarity": 6,
            "Novelty": 6,
            "Feasibility": 6,
            "Relevance": 7,
        },
        record["assistant_2_system"]: {
            "Clarity": 6,
            "Novelty": 6,
            "Feasibility": 6,
            "Relevance": 7,
        },
    }
    scores_by_system["EvoScientist"] = {
        "Clarity": 8,
        "Novelty": 7,
        "Feasibility": 8,
        "Relevance": 9,
    }
    return {
        "comparison_id": record["comparison_id"],
        "query_id": record["query_id"],
        "assistant_1_system": record["assistant_1_system"],
        "assistant_2_system": record["assistant_2_system"],
        "synthetic": True,
        "assistant_1": scores_by_system[record["assistant_1_system"]],
        "assistant_2": scores_by_system[record["assistant_2_system"]],
    }


def write_synthetic_judge_outputs(judge_inputs: Path, output_dir: Path) -> Path:
    judge_outputs = output_dir / "judge_outputs" / "synthetic_results.jsonl"
    judge_outputs.parent.mkdir(parents=True, exist_ok=True)
    with judge_inputs.open(encoding="utf-8") as src, judge_outputs.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            dst.write(json.dumps(synthetic_scores(json.loads(line)), ensure_ascii=False) + "\n")
    return judge_outputs


def aggregate(judge_outputs: Path, output_dir: Path) -> tuple[Path, Path]:
    csv_path = output_dir / "tables" / "synthetic_win_tie_lose.csv"
    json_path = output_dir / "tables" / "synthetic_win_tie_lose.json"
    subprocess.run(
        [
            sys.executable,
            str(REPRO / "aggregate_judge_results.py"),
            "--input",
            str(judge_outputs),
            "--output-csv",
            str(csv_path),
            "--output-json",
            str(json_path),
        ],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
    )
    return csv_path, json_path


def write_report(
    *,
    output_dir: Path,
    query_count: int,
    baseline: str,
    judge_inputs: Path,
    judge_outputs: Path,
    csv_path: Path,
    json_path: Path,
) -> Path:
    summary = json.loads(json_path.read_text(encoding="utf-8"))
    report_path = output_dir / "SMOKE_REPORT.md"
    report_path.write_text(
        "\n".join(
            [
                "# Offline Reproduction Smoke Report",
                "",
                "Status: PASS",
                "",
                "This report uses synthetic proposal and judge records. It validates",
                "the evaluation pipeline shape only; it is not a reproduction of the",
                "paper's numeric results.",
                "",
                f"- Queries covered: {query_count}",
                f"- Target system: {summary['target_system']}",
                f"- Baseline: {baseline}",
                f"- Raw judge records: {summary['raw_records']}",
                f"- Judge inputs: `{judge_inputs}`",
                f"- Judge outputs: `{judge_outputs}`",
                f"- CSV table: `{csv_path}`",
                f"- JSON table: `{json_path}`",
                "",
                "Remaining for paper-level reproduction:",
                "",
                "- real EvoScientist outputs generated under the reported model/budget settings;",
                "- real baseline outputs from the seven compared systems;",
                "- real Gemini judge calls or human labels.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3, help="Number of queries for the smoke test.")
    parser.add_argument("--baseline", default="SyntheticBaseline")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.limit <= 0:
        raise SystemExit("--limit must be positive")

    queries = load_queries(args.limit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    systems_root = write_synthetic_system_outputs(args.output_dir, queries, args.baseline)
    judge_inputs = build_judge_inputs(
        systems_root=systems_root,
        baseline=args.baseline,
        query_count=len(queries),
        output_dir=args.output_dir,
    )
    judge_outputs = write_synthetic_judge_outputs(judge_inputs, args.output_dir)
    csv_path, json_path = aggregate(judge_outputs, args.output_dir)
    report_path = write_report(
        output_dir=args.output_dir,
        query_count=len(queries),
        baseline=args.baseline,
        judge_inputs=judge_inputs,
        judge_outputs=judge_outputs,
        csv_path=csv_path,
        json_path=json_path,
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "synthetic": True,
                "queries": len(queries),
                "report": str(report_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
