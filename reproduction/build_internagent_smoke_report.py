#!/usr/bin/env python3
"""Build a tracked report for InternAgent replacement-baseline smoke runs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EXTERNAL_CHECKOUT = Path.home() / "research" / "InternAgent"
EXTERNAL_OUTPUT_DIR = (
    EXTERNAL_CHECKOUT / "outputs" / "evoscientist_table1_queries" / "internagent"
)


def git_head(path: Path) -> str | None:
    if not (path / ".git").is_dir():
        return None
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return None


def file_status(path: Path) -> dict[str, Any]:
    try:
        display_path = str(path.relative_to(REPO))
    except ValueError:
        display_path = str(path)
    return {
        "path": display_path,
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
    }


def count_jsonl(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def load_queries(limit: int) -> list[dict[str, Any]]:
    queries = json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]
    return queries[:limit]


def short_outputs(
    external_outputs: list[dict[str, Any]],
    imported_outputs: list[dict[str, Any]],
    query_ids: list[int],
    threshold: int,
) -> list[dict[str, Any]]:
    rows = []
    for query_id, external, imported in zip(query_ids, external_outputs, imported_outputs):
        if external["bytes"] < threshold or imported["bytes"] < threshold:
            rows.append(
                {
                    "query_id": query_id,
                    "external_bytes": external["bytes"],
                    "imported_bytes": imported["bytes"],
                    "threshold": threshold,
                }
            )
    return rows


def build_report(limit: int, tag: str, min_chars: int, nominal_min_chars: int) -> dict[str, Any]:
    judge_input = ROOT / "artifacts" / "judge_inputs" / f"evosci_vs_internagent_{tag}.jsonl"
    judge_output = (
        ROOT / "artifacts" / "judge_outputs" / f"evosci_vs_internagent_{tag}_deepseek.jsonl"
    )
    aggregate_json = ROOT / "artifacts" / "tables" / f"evosci_vs_internagent_{tag}_deepseek.json"
    aggregate_csv = ROOT / "artifacts" / "tables" / f"evosci_vs_internagent_{tag}_deepseek.csv"
    aggregate = json.loads(aggregate_json.read_text(encoding="utf-8")) if aggregate_json.is_file() else {}
    dimensions = aggregate.get("baselines", {}).get("InternAgent", {}).get("dimensions", {})
    queries = load_queries(limit)
    external_outputs = [
        file_status(EXTERNAL_OUTPUT_DIR / f"query_{item['id']:02d}.md") for item in queries
    ]
    imported_outputs = [
        file_status(ROOT / "artifacts" / "idea_outputs" / "InternAgent" / f"query_{item['id']:02d}" / "answer.txt")
        for item in queries
    ]
    expected_records = limit * 2
    query_ids = [item["id"] for item in queries]
    below_min_chars = short_outputs(external_outputs, imported_outputs, query_ids, min_chars)
    below_nominal_min_chars = short_outputs(
        external_outputs,
        imported_outputs,
        query_ids,
        nominal_min_chars,
    )
    complete = (
        all(item["exists"] and item["bytes"] >= min_chars for item in external_outputs)
        and all(item["exists"] and item["bytes"] >= min_chars for item in imported_outputs)
        and file_status(judge_input)["exists"]
        and file_status(judge_output)["exists"]
        and file_status(aggregate_json)["exists"]
        and file_status(aggregate_csv)["exists"]
        and count_jsonl(judge_input) == expected_records
        and count_jsonl(judge_output) == expected_records
        and set(dimensions) == {"Clarity", "Novelty", "Feasibility", "Relevance"}
    )
    return {
        "date": "2026-06-04",
        "baseline": "InternAgent",
        "query_ids": query_ids,
        "topics": [item["topic"] for item in queries],
        "paper_exact": False,
        "status": "complete" if complete else "incomplete",
        "min_chars": min_chars,
        "nominal_min_chars": nominal_min_chars,
        "below_min_chars": below_min_chars,
        "below_nominal_min_chars": below_nominal_min_chars,
        "external_checkout": str(EXTERNAL_CHECKOUT),
        "external_head": git_head(EXTERNAL_CHECKOUT),
        "runner": "reproduction/run_internagent_qa_baseline.py",
        "model": "deepseek-chat",
        "judge_model": "deepseek-v4-flash",
        "files": {
            "external_outputs": external_outputs,
            "imported_outputs": imported_outputs,
            "judge_input": file_status(judge_input),
            "judge_output": file_status(judge_output),
            "aggregate_json": file_status(aggregate_json),
            "aggregate_csv": file_status(aggregate_csv),
        },
        "judge_records": count_jsonl(judge_output),
        "aggregate": aggregate,
        "caveat": (
            "This is a replacement-baseline smoke run for recovered paper queries. "
            "It is not the paper's original raw InternAgent Table 1 output. "
            "The run preserves observed InternAgent/DeepSeek parsing failures as baseline behavior. "
            "Outputs below the nominal length threshold are retained and flagged, not regenerated."
        ),
    }


def render_markdown(report: dict[str, Any], tag: str) -> str:
    lines = [
        f"# InternAgent {tag} Smoke Report",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Baseline: {report['baseline']}",
        f"Queries: {', '.join(f'{item:02d}' for item in report['query_ids'])}",
        f"Paper-exact: `{str(report['paper_exact']).lower()}`",
        f"Accepted output min chars: {report['min_chars']}",
        f"Nominal output min chars: {report['nominal_min_chars']}",
        "",
        report["caveat"],
        "",
        "## Query Outputs",
        "",
        "| Query | Topic | External bytes | Imported bytes |",
        "| ---: | --- | ---: | ---: |",
    ]
    for query_id, topic, external, imported in zip(
        report["query_ids"],
        report["topics"],
        report["files"]["external_outputs"],
        report["files"]["imported_outputs"],
    ):
        lines.append(f"| {query_id:02d} | {topic} | {external['bytes']} | {imported['bytes']} |")
    if report.get("below_nominal_min_chars"):
        lines.extend(
            [
                "",
                "Outputs below the nominal threshold:",
                "",
                "| Query | External bytes | Imported bytes | Threshold |",
                "| ---: | ---: | ---: | ---: |",
            ]
        )
        for row in report["below_nominal_min_chars"]:
            lines.append(
                "| {query_id:02d} | {external_bytes} | {imported_bytes} | {threshold} |".format(
                    **row
                )
            )
    lines.extend(
        [
            "",
            "## Judge Artifacts",
            "",
            "| Artifact | Exists | Bytes | Path |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for name in ["judge_input", "judge_output", "aggregate_json", "aggregate_csv"]:
        item = report["files"][name]
        lines.append(f"| {name} | {item['exists']} | {item['bytes']} | `{item['path']}` |")
    lines.extend(
        [
            "",
            "## Judge Result",
            "",
            f"Judge records: {report['judge_records']}",
            "",
            "| Dimension | N | Win | Tie | Lose | Win % | Tie % | Lose % |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    dimensions = report.get("aggregate", {}).get("baselines", {}).get("InternAgent", {}).get("dimensions", {})
    for name in ["Clarity", "Novelty", "Feasibility", "Relevance"]:
        row = dimensions.get(name, {})
        lines.append(
            "| {dimension} | {n} | {win} | {tie} | {lose} | {win_pct} | {tie_pct} | {lose_pct} |".format(
                dimension=name,
                n=row.get("n", ""),
                win=row.get("win", ""),
                tie=row.get("tie", ""),
                lose=row.get("lose", ""),
                win_pct=row.get("win_pct", ""),
                tie_pct=row.get("tie_pct", ""),
                lose_pct=row.get("lose_pct", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Rebuild",
            "",
            "```bash",
            "source $HOME/.codex/env",
            f".venv/bin/python reproduction/run_internagent_qa_baseline.py --limit {len(report['query_ids'])} --max-iter 5 --resume",
            f".venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --limit {len(report['query_ids'])} --min-chars {report['min_chars']} --overwrite --strict",
            f".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --limit {len(report['query_ids'])} --output reproduction/artifacts/judge_inputs/evosci_vs_internagent_{tag}.jsonl",
            f".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent_{tag}.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_{tag}_deepseek.jsonl --resume",
            f".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_{tag}_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_{tag}_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_{tag}_deepseek.json",
            f".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --limit {len(report['query_ids'])} --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent_{tag}.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_{tag}_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_{tag}_deepseek.json",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--tag", default="queries01_03")
    parser.add_argument("--min-chars", type=int, default=1000)
    parser.add_argument("--nominal-min-chars", type=int, default=1000)
    args = parser.parse_args()
    output_json = ROOT / f"internagent_{args.tag}_smoke_report.json"
    output_md = ROOT / f"internagent_{args.tag}_smoke_report.md"
    report = build_report(args.limit, args.tag, args.min_chars, args.nominal_min_chars)
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(report, args.tag), encoding="utf-8")
    print(json.dumps({"status": report["status"], "judge_records": report["judge_records"]}, indent=2))


if __name__ == "__main__":
    main()
