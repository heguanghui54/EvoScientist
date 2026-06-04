#!/usr/bin/env python3
"""Build a tracked report for AI Scientist-v2 replacement-baseline runs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EXTERNAL_CHECKOUT = Path.home() / "research" / "AI-Scientist-v2"
EXTERNAL_OUTPUT_DIR = (
    EXTERNAL_CHECKOUT / "outputs" / "evoscientist_table1_queries" / "ai_scientist_v2"
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


def build_report(limit: int, tag: str, min_chars: int) -> dict[str, Any]:
    judge_input = ROOT / "artifacts" / "judge_inputs" / f"evosci_vs_ai_scientist_v2{tag}.jsonl"
    judge_output = (
        ROOT / "artifacts" / "judge_outputs" / f"evosci_vs_ai_scientist_v2{tag}_deepseek.jsonl"
    )
    aggregate_json = ROOT / "artifacts" / "tables" / f"evosci_vs_ai_scientist_v2{tag}_deepseek.json"
    aggregate_csv = ROOT / "artifacts" / "tables" / f"evosci_vs_ai_scientist_v2{tag}_deepseek.csv"
    aggregate = json.loads(aggregate_json.read_text(encoding="utf-8")) if aggregate_json.is_file() else {}
    dimensions = aggregate.get("baselines", {}).get("AI Scientist-v2", {}).get("dimensions", {})
    queries = load_queries(limit)
    external_outputs = [
        file_status(EXTERNAL_OUTPUT_DIR / f"query_{item['id']:02d}.md") for item in queries
    ]
    imported_outputs = [
        file_status(ROOT / "artifacts" / "idea_outputs" / "AI Scientist-v2" / f"query_{item['id']:02d}" / "answer.txt")
        for item in queries
    ]
    external_manifest = (
        json.loads((EXTERNAL_OUTPUT_DIR / "manifest.json").read_text(encoding="utf-8"))
        if (EXTERNAL_OUTPUT_DIR / "manifest.json").is_file()
        else {}
    )
    expected_records = limit * 2
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
        "baseline": "AI Scientist-v2",
        "query_ids": [item["id"] for item in queries],
        "topics": [item["topic"] for item in queries],
        "paper_exact": False,
        "status": "complete" if complete else "incomplete",
        "min_chars": min_chars,
        "external_checkout": str(EXTERNAL_CHECKOUT),
        "external_head": git_head(EXTERNAL_CHECKOUT),
        "runner": "reproduction/run_ai_scientist_v2_ideation_baseline.py",
        "model": external_manifest.get("model", "deepseek-coder-v2-0724"),
        "num_reflections": external_manifest.get("num_reflections"),
        "s2_timeout": external_manifest.get("s2_timeout"),
        "s2_max_results": external_manifest.get("s2_max_results"),
        "external_manifest": external_manifest,
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
            "This is a replacement-baseline ideation run through AI Scientist-v2. "
            "It is not the paper's original raw AI Scientist-v2 Table 1 output. "
            "Semantic Scholar access was bounded and degraded under rate limits."
        ),
    }


def render_markdown(report: dict[str, Any], tag: str) -> str:
    lines = [
        f"# AI Scientist-v2 {tag or 'queries01_30'} Smoke Report",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Baseline: {report['baseline']}",
        f"Queries: {', '.join(f'{item:02d}' for item in report['query_ids'])}",
        f"Paper-exact: `{str(report['paper_exact']).lower()}`",
        f"Accepted output min chars: {report['min_chars']}",
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
    dimensions = report.get("aggregate", {}).get("baselines", {}).get("AI Scientist-v2", {}).get("dimensions", {})
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
            ".venv/bin/python reproduction/run_ai_scientist_v2_ideation_baseline.py --limit 30 --num-reflections 5 --resume",
            ".venv/bin/python reproduction/import_baseline_outputs.py --system-name 'AI Scientist-v2' --source $HOME/research/AI-Scientist-v2/outputs/evoscientist_table1_queries/ai_scientist_v2 --source-format directory --output-root reproduction/artifacts/idea_outputs --limit 30 --min-chars 1000 --overwrite --strict",
            ".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'AI Scientist-v2' --limit 30 --output reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl",
            ".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --resume",
            ".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json",
            ".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline 'AI Scientist-v2' --limit 30 --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_ai_scientist_v2.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_ai_scientist_v2_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_ai_scientist_v2_deepseek.json",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--tag", default="")
    parser.add_argument("--min-chars", type=int, default=1000)
    args = parser.parse_args()
    output_json = ROOT / "ai_scientist_v2_queries01_30_smoke_report.json"
    output_md = ROOT / "ai_scientist_v2_queries01_30_smoke_report.md"
    report = build_report(args.limit, args.tag, args.min_chars)
    output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    output_md.write_text(render_markdown(report, args.tag), encoding="utf-8")
    print(json.dumps({"status": report["status"], "judge_records": report["judge_records"]}, indent=2))


if __name__ == "__main__":
    main()
