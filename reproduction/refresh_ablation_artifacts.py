#!/usr/bin/env python3
"""Refresh accumulated Table 3 ablation manifests and judge inputs.

`run_ablation_variants.py` is convenient for selected batches, but each selected
batch rewrites the per-variant manifest and judge input file for that batch. This
utility scans the accumulated answer files in an artifact root and rebuilds the
manifest plus judge inputs from all complete query ids found there.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_ARTIFACTS_ROOT = ROOT / "artifacts" / "ablations"
DEFAULT_QUERIES = ROOT / "queries.json"
VARIANTS = ["-IDE", "-IVE", "-all"]
DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]


def load_queries(path: Path = DEFAULT_QUERIES) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["queries"]


def answer_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def refresh_variant(
    *,
    artifacts_root: Path,
    variant: str,
    queries: list[dict[str, Any]],
    reference_system: str,
    proposal_only: bool,
) -> dict[str, Any]:
    variant_root = artifacts_root / variant
    system_outputs = variant_root / "system_outputs"
    complete_query_ids: list[int] = []
    outputs = []
    missing_reference_query_ids = []
    missing_variant_query_ids = []

    for query in queries:
        qid = query["id"]
        variant_answer = system_outputs / variant / f"query_{qid:02d}" / "answer.txt"
        reference_answer = system_outputs / reference_system / f"query_{qid:02d}" / "answer.txt"
        variant_present = variant_answer.is_file() and bool(answer_text(variant_answer))
        reference_present = reference_answer.is_file() and bool(answer_text(reference_answer))
        if variant_present and reference_present:
            complete_query_ids.append(qid)
            outputs.append(
                {
                    "query_id": qid,
                    "topic": query["topic"],
                    "dir": str(variant_answer.parent),
                    "reference_present": True,
                    "status": "ok",
                    "answer_chars": len(answer_text(variant_answer)),
                }
            )
        else:
            if not variant_present:
                missing_variant_query_ids.append(qid)
            if not reference_present:
                missing_reference_query_ids.append(qid)

    variant_root.mkdir(parents=True, exist_ok=True)
    judge_input_records = 0
    with (variant_root / "judge_inputs.jsonl").open("w", encoding="utf-8") as out:
        for query in queries:
            qid = query["id"]
            if qid not in complete_query_ids:
                continue
            variant_answer = answer_text(system_outputs / variant / f"query_{qid:02d}" / "answer.txt")
            reference_answer = answer_text(system_outputs / reference_system / f"query_{qid:02d}" / "answer.txt")
            record = {
                "comparison_id": f"ablation__{variant}__q{qid:02d}__vs__{reference_system}",
                "query_id": qid,
                "topic": query["topic"],
                "question": query["goal"],
                "assistant_1_system": variant,
                "assistant_2_system": reference_system,
                "answer_a": variant_answer,
                "answer_b": reference_answer,
                "judge_template": "reproduction/judge_prompt_template.md",
                "dimensions": DIMENSIONS,
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            judge_input_records += 1

    summary = {
        "variant": variant,
        "query_count": len(complete_query_ids),
        "expected_query_count": len(queries),
        "complete": len(complete_query_ids) == len(queries) and not missing_reference_query_ids,
        "dry_run": False,
        "proposal_only": proposal_only,
        "reference_system": reference_system,
        "reference_root": str(system_outputs / reference_system),
        "complete_query_ids": complete_query_ids,
        "missing_variant_query_ids": missing_variant_query_ids,
        "missing_reference_query_ids": missing_reference_query_ids,
        "outputs": outputs,
        "paper_exact": False,
        "caveat": (
            "Replacement ablation run driven by prompt-level disabled-component "
            "constraints. The public checkout does not expose the paper's native "
            "IDE/IVE ablation switches."
        ),
        "judge_input_records": judge_input_records,
    }
    (variant_root / "system_outputs_complete.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS_ROOT)
    parser.add_argument("--variant", action="append", choices=VARIANTS, default=None)
    parser.add_argument("--reference-system", default="EvoScientist")
    parser.add_argument("--proposal-only", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    queries = load_queries()
    variants = args.variant or VARIANTS
    summaries = [
        refresh_variant(
            artifacts_root=args.artifacts_root,
            variant=variant,
            queries=queries,
            reference_system=args.reference_system,
            proposal_only=args.proposal_only,
        )
        for variant in variants
    ]
    result = {
        "status": "complete" if all(item["complete"] for item in summaries) else "partial",
        "artifacts_root": str(args.artifacts_root),
        "variants": {
            item["variant"]: {
                "query_count": item["query_count"],
                "expected_query_count": item["expected_query_count"],
                "complete_query_ids": item["complete_query_ids"],
                "complete": item["complete"],
            }
            for item in summaries
        },
    }
    print(json.dumps(result, indent=2))
    if args.strict and result["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
