#!/usr/bin/env python3
"""Build a tracked report for the InternAgent query-01 replacement smoke run."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EXTERNAL_CHECKOUT = Path.home() / "research" / "InternAgent"
EXTERNAL_OUTPUT = (
    EXTERNAL_CHECKOUT / "outputs" / "evoscientist_table1_queries" / "internagent" / "query_01.md"
)
IMPORTED_OUTPUT = ROOT / "artifacts" / "idea_outputs" / "InternAgent" / "query_01" / "answer.txt"
JUDGE_INPUT = ROOT / "artifacts" / "judge_inputs" / "evosci_vs_internagent_query01.jsonl"
JUDGE_OUTPUT = ROOT / "artifacts" / "judge_outputs" / "evosci_vs_internagent_query01_deepseek.jsonl"
AGGREGATE_JSON = ROOT / "artifacts" / "tables" / "evosci_vs_internagent_query01_deepseek.json"
AGGREGATE_CSV = ROOT / "artifacts" / "tables" / "evosci_vs_internagent_query01_deepseek.csv"
DEFAULT_OUTPUT_JSON = ROOT / "internagent_query01_smoke_report.json"
DEFAULT_OUTPUT_MD = ROOT / "internagent_query01_smoke_report.md"


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


def build_report() -> dict[str, Any]:
    aggregate = json.loads(AGGREGATE_JSON.read_text(encoding="utf-8")) if AGGREGATE_JSON.is_file() else {}
    dimensions = (
        aggregate.get("baselines", {})
        .get("InternAgent", {})
        .get("dimensions", {})
    )
    files = {
        "external_output": file_status(EXTERNAL_OUTPUT),
        "imported_output": file_status(IMPORTED_OUTPUT),
        "judge_input": file_status(JUDGE_INPUT),
        "judge_output": file_status(JUDGE_OUTPUT),
        "aggregate_json": file_status(AGGREGATE_JSON),
        "aggregate_csv": file_status(AGGREGATE_CSV),
    }
    complete = (
        all(item["exists"] for name, item in files.items() if name != "external_output")
        and count_jsonl(JUDGE_INPUT) == 2
        and count_jsonl(JUDGE_OUTPUT) == 2
        and set(dimensions) == {"Clarity", "Novelty", "Feasibility", "Relevance"}
    )
    return {
        "date": "2026-06-04",
        "baseline": "InternAgent",
        "query_id": 1,
        "topic": "Machine translation",
        "paper_exact": False,
        "status": "complete" if complete else "incomplete",
        "external_checkout": str(EXTERNAL_CHECKOUT),
        "external_head": git_head(EXTERNAL_CHECKOUT),
        "runner": "reproduction/run_internagent_qa_baseline.py",
        "model": "deepseek-chat",
        "judge_model": "deepseek-v4-flash",
        "files": files,
        "judge_records": count_jsonl(JUDGE_OUTPUT),
        "aggregate": aggregate,
        "caveat": (
            "This is a replacement-baseline smoke run for one recovered paper query. "
            "It is not the paper's original raw InternAgent Table 1 output."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# InternAgent Query-01 Smoke Report",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Baseline: {report['baseline']}",
        f"Query: {report['query_id']:02d} ({report['topic']})",
        f"Paper-exact: `{str(report['paper_exact']).lower()}`",
        "",
        report["caveat"],
        "",
        "## Files",
        "",
        "| Artifact | Exists | Bytes | Path |",
        "| --- | --- | ---: | --- |",
    ]
    for name, item in report["files"].items():
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
            ".venv/bin/python reproduction/run_internagent_qa_baseline.py --query-id 1 --max-iter 5",
            ".venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --limit 1 --min-chars 1000 --strict",
            ".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline InternAgent --limit 1 --output reproduction/artifacts/judge_inputs/evosci_vs_internagent_query01.jsonl",
            ".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_internagent_query01.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_internagent_query01_deepseek.jsonl --resume",
            ".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_internagent_query01_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.json",
            ".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline InternAgent --limit 1 --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_internagent_query01.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_internagent_query01_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_internagent_query01_deepseek.json",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    DEFAULT_OUTPUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    DEFAULT_OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "judge_records": report["judge_records"]}, indent=2))


if __name__ == "__main__":
    main()
