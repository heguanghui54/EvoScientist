#!/usr/bin/env python3
"""Convert AI Scientist-v2 ideation JSON outputs into importable JSONL."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_GENERATED_ROOT = "$HOME/research/AI-Scientist-v2/ai_scientist/ideas"
DEFAULT_OUTPUT = ROOT / "ai_scientist_v2_ideation_import_template.jsonl"


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expandvars(str(value))).expanduser()


def render_answer(idea: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            f"# {idea.get('Title', idea.get('Name', 'AI Scientist-v2 idea'))}",
            f"Short Hypothesis: {idea.get('Short Hypothesis', '')}",
            f"Related Work: {idea.get('Related Work', '')}",
            f"Abstract: {idea.get('Abstract', '')}",
            f"Experiments: {idea.get('Experiments', '')}",
            f"Risk Factors and Limitations: {idea.get('Risk Factors and Limitations', '')}",
        ]
    )


def convert(generated_root: Path, output: Path) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    skipped = []
    for path in sorted(generated_root.glob("query_*.json")):
        try:
            query_id = int(path.stem.split("_")[1])
        except (IndexError, ValueError):
            skipped.append({"path": str(path), "reason": "bad query filename"})
            continue
        ideas = json.loads(path.read_text(encoding="utf-8"))
        if not ideas:
            skipped.append({"path": str(path), "reason": "empty idea list"})
            continue
        prompt_path = generated_root / f"query_{query_id:02d}.md"
        rows.append(
            {
                "query_id": query_id,
                "answer": render_answer(ideas[0]),
                "prompt": prompt_path.read_text(encoding="utf-8")
                if prompt_path.is_file()
                else "",
                "source": str(path),
            }
        )
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"written": len(rows), "skipped": skipped, "output": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-root", default=DEFAULT_GENERATED_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = convert(expand_path(args.generated_root), args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
