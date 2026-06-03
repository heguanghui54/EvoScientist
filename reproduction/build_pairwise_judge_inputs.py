#!/usr/bin/env python3
"""Build pairwise LLM-judge inputs for EvoScientist idea-generation evaluation.

Expected system-output layout:

systems_root/
  EvoScientist/query_01/answer.txt
  AI-Scientist-v2/query_01/answer.txt
  ...

The script creates one JSONL record per comparison direction. With
`--swap-order`, it emits both A=EvoScientist/B=baseline and
A=baseline/B=EvoScientist records, matching the paper's positional-bias control.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]


def load_queries() -> list[dict]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def read_answer(systems_root: Path, system: str, query_id: int) -> str:
    qdir = systems_root / system / f"query_{query_id:02d}"
    candidates = [
        qdir / "answer.txt",
        qdir / "proposal.md",
        qdir / "stdout.txt",
    ]
    for path in candidates:
        if path.is_file():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return text
    raise FileNotFoundError(
        f"No answer found for system={system!r}, query_id={query_id}. "
        f"Expected one of: {', '.join(str(p) for p in candidates)}"
    )


def make_record(
    *,
    query: dict,
    system_a: str,
    answer_a: str,
    system_b: str,
    answer_b: str,
) -> dict:
    return {
        "comparison_id": f"q{query['id']:02d}__{system_a}__vs__{system_b}",
        "query_id": query["id"],
        "topic": query["topic"],
        "question": query["goal"],
        "assistant_1_system": system_a,
        "assistant_2_system": system_b,
        "answer_a": answer_a,
        "answer_b": answer_b,
        "judge_template": "reproduction/judge_prompt_template.md",
        "dimensions": DIMENSIONS,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--systems-root", type=Path, required=True)
    parser.add_argument("--target-system", default="EvoScientist")
    parser.add_argument("--baseline", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--swap-order", action="store_true", default=True)
    args = parser.parse_args()

    queries = load_queries()
    if args.limit is not None:
        queries = queries[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.output.open("w", encoding="utf-8") as out:
        for query in queries:
            target_answer = read_answer(args.systems_root, args.target_system, query["id"])
            for baseline in args.baseline:
                baseline_answer = read_answer(args.systems_root, baseline, query["id"])
                records = [
                    make_record(
                        query=query,
                        system_a=args.target_system,
                        answer_a=target_answer,
                        system_b=baseline,
                        answer_b=baseline_answer,
                    )
                ]
                if args.swap_order:
                    records.append(
                        make_record(
                            query=query,
                            system_a=baseline,
                            answer_a=baseline_answer,
                            system_b=args.target_system,
                            answer_b=target_answer,
                        )
                    )
                for record in records:
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1

    print(json.dumps({"status": "ok", "records": count, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()

