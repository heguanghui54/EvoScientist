#!/usr/bin/env python3
"""Normalize system outputs into clean answer.txt files for pairwise judging.

EvoScientist CLI logs include loading messages, echoed prompts, rich "Thinking"
boxes, usage footers, and resume instructions. Those are execution artifacts,
not the idea being evaluated. This script extracts the final proposal text and
writes it as `answer.txt`, which `build_pairwise_judge_inputs.py` reads before
falling back to raw `stdout.txt`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BOX_CHARS = "─━═╭╮╰╯│┌┐└┘├┤┬┴┼"


def load_queries() -> list[dict]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text)


def remove_header(text: str) -> str:
    if "Workspace:" in text:
        return text.split("Workspace:", 1)[1].split("\n", 1)[-1].lstrip()
    return text


def remove_thinking_box(text: str) -> str:
    # Rich renders the hidden reasoning as a box. Keep only content after the
    # first closing corner if present.
    close_index = text.find("╰")
    if close_index == -1:
        return text
    newline_index = text.find("\n", close_index)
    if newline_index == -1:
        return ""
    return text[newline_index + 1 :].lstrip()


def clean_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return ""
    if stripped in {"Goodbye!"}:
        return None
    if stripped.startswith("Resume this session with:"):
        return None
    if stripped.startswith("EvoSci --resume"):
        return None
    if stripped.startswith("[Usage:") or "[Usage:" in stripped:
        return None
    if stripped.startswith("Loading agent"):
        return None
    if stripped.startswith("Warning:") or stripped.startswith("⚠"):
        return None
    if stripped.startswith("Subagent "):
        return None
    if set(stripped) <= set(BOX_CHARS + " "):
        return None
    # Remove residual rich box sidebars if a partial box appears in output.
    if stripped.startswith("│") and stripped.endswith("│"):
        stripped = stripped.strip("│").strip()
    return stripped


def normalize_text(text: str) -> str:
    text = strip_ansi(text)
    text = remove_header(text)
    text = remove_thinking_box(text)
    lines = []
    blank_pending = False
    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if line is None:
            continue
        if line == "":
            blank_pending = True
            continue
        if blank_pending and lines:
            lines.append("")
        lines.append(line)
        blank_pending = False
    normalized = "\n".join(lines).strip()
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    for heading in [
        "Title",
        "Problem",
        "Hypothesis",
        "Method",
        "Dataset / Benchmark",
        "Evaluation Metrics",
        "Baselines",
        "Ablations",
        "Expected Failure Modes",
    ]:
        escaped = re.escape(heading)
        normalized = re.sub(rf"({escaped})(?=[A-Z#])", rf"\1\n", normalized)
    return normalized


def source_path(qdir: Path) -> Path | None:
    for filename in ["answer.txt", "proposal.md", "stdout.txt"]:
        path = qdir / filename
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            return path
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--systems-root", type=Path, required=True)
    parser.add_argument("--system", action="append", required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--min-chars", type=int, default=200)
    args = parser.parse_args()

    queries = load_queries()
    if args.limit is not None:
        queries = queries[: args.limit]

    report = {"systems_root": str(args.systems_root), "systems": {}}
    for system in args.system:
        system_report = {"written": 0, "skipped": 0, "missing": [], "too_short": []}
        for query in queries:
            qdir = args.systems_root / system / f"query_{query['id']:02d}"
            out_path = qdir / "answer.txt"
            if out_path.is_file() and out_path.read_text(encoding="utf-8").strip() and not args.overwrite:
                system_report["skipped"] += 1
                continue
            src = source_path(qdir)
            if src is None:
                system_report["missing"].append(query["id"])
                continue
            normalized = normalize_text(src.read_text(encoding="utf-8", errors="replace"))
            if len(normalized) < args.min_chars:
                system_report["too_short"].append({"query_id": query["id"], "chars": len(normalized)})
                continue
            out_path.write_text(normalized + "\n", encoding="utf-8")
            system_report["written"] += 1
        report["systems"][system] = system_report

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
