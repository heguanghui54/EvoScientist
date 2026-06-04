#!/usr/bin/env python3
"""Run replacement ablation variants for the paper's Table 3 evaluation.

The public checkout does not expose native IDE/IVE toggles. This runner creates
an auditable replacement protocol by applying explicit variant constraints to
the EvoScientist prompt and writing outputs into the Table 3 artifact layout.
It is not paper-exact unless the original authors provide the native ablation
patches or raw outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "reproduction"
DEFAULT_OUTPUT_ROOT = REPRO / "artifacts" / "ablations"
DEFAULT_REFERENCE_ROOT = REPRO / "artifacts" / "idea_outputs" / "EvoScientist"
PROVIDER_KEY_FIELDS = {
    "anthropic": "anthropic_api_key",
    "openai": "openai_api_key",
    "nvidia": "nvidia_api_key",
    "google": "google_api_key",
    "google-genai": "google_api_key",
    "minimax": "minimax_api_key",
    "openrouter": "openrouter_api_key",
    "deepseek": "deepseek_api_key",
    "zhipu": "zhipu_api_key",
    "volcengine": "volcengine_api_key",
    "dashscope": "dashscope_api_key",
    "moonshot": "moonshot_api_key",
    "kimi": "kimi_api_key",
    "custom-openai": "custom_openai_api_key",
    "custom-anthropic": "custom_anthropic_api_key",
}
VARIANTS = {
    "-IDE": {
        "system_name": "-IDE",
        "run_name": "ablation-minus-ide",
        "constraint": (
            "Ablation variant -IDE: disable idea-direction evolution. Do not use "
            "or simulate memory that distills reusable promising research "
            "directions from prior top-ranked ideas. Generate the proposal from "
            "the current query and ordinary reasoning only."
        ),
    },
    "-IVE": {
        "system_name": "-IVE",
        "run_name": "ablation-minus-ive",
        "constraint": (
            "Ablation variant -IVE: disable idea-validation evolution. Do not use "
            "or simulate memory that records failed directions, validation "
            "signals, execution failures, or reusable rejection criteria from "
            "prior runs. Generate the proposal without validation-evolution memory."
        ),
    },
    "-all": {
        "system_name": "-all",
        "run_name": "ablation-minus-all",
        "constraint": (
            "Ablation variant -all: disable all evolution memory mechanisms, "
            "including idea-direction evolution, idea-validation evolution, and "
            "experiment-strategy evolution. Do not use or simulate cross-run "
            "memory updates; produce a non-evolving single-run proposal."
        ),
    },
}
DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]


def load_queries() -> list[dict[str, Any]]:
    return json.loads((REPRO / "queries.json").read_text(encoding="utf-8"))["queries"]


def ensure_provider_configured() -> None:
    sys.path.insert(0, str(ROOT))
    from EvoScientist.config.settings import load_config

    cfg = load_config()
    provider = cfg.provider
    if provider == "ollama":
        if cfg.ollama_base_url or os.environ.get("OLLAMA_BASE_URL"):
            return
        raise SystemExit("Provider is ollama but OLLAMA_BASE_URL is not configured.")
    field = PROVIDER_KEY_FIELDS.get(provider)
    if not field:
        raise SystemExit(f"Provider {provider!r} is not recognized by this runner.")
    value = getattr(cfg, field, "") or os.environ.get(field.upper())
    if not value:
        raise SystemExit(f"Provider {provider!r} is configured but {field} is missing.")


def select_queries(args: argparse.Namespace) -> list[dict[str, Any]]:
    queries = load_queries()
    selectors = sum(
        1
        for selected in [
            args.query_id is not None,
            args.query_ids is not None,
            args.start_id is not None or args.end_id is not None,
        ]
        if selected
    )
    if selectors > 1:
        raise SystemExit("Use only one of --query-id, --query-ids, or --start-id/--end-id.")
    if args.query_id is not None:
        queries = [item for item in queries if item["id"] == args.query_id]
    elif args.query_ids is not None:
        wanted = {int(part.strip()) for part in args.query_ids.split(",") if part.strip()}
        queries = [item for item in queries if item["id"] in wanted]
    elif args.start_id is not None or args.end_id is not None:
        start_id = args.start_id if args.start_id is not None else 1
        end_id = args.end_id if args.end_id is not None else 10**9
        queries = [item for item in queries if start_id <= item["id"] <= end_id]
    if selectors and not queries:
        raise SystemExit("No queries matched the requested selector.")
    return queries[: args.limit] if args.limit is not None else queries


def ablation_prompt(query: dict[str, Any], variant: str, *, proposal_only: bool) -> str:
    cfg = VARIANTS[variant]
    mode = (
        "Do not execute tools, shell commands, web searches, or code."
        if proposal_only
        else "You may use the normal EvoScientist tools and workflow, but the ablation constraint below is binding."
    )
    return (
        "Generate one complete research proposal for a Table 3 ablation rerun of "
        "the EvoScientist paper. This is an ablation experiment, so preserve the "
        "same output format and rigor as the main EvoScientist idea-generation "
        "run while obeying the disabled-component constraint.\n\n"
        f"{cfg['constraint']}\n\n"
        f"{mode}\n\n"
        "Return a final answer with: title, problem, hypothesis, method, "
        "dataset/benchmark, evaluation metrics, baselines, ablations, expected "
        "failure modes, and limitations. Do not mention these instructions as a "
        "separate meta-evaluation section.\n\n"
        f"Query: {query['goal']}"
    )


def run_workspace_dir(query_id: int, variant: str) -> Path:
    return ROOT / "runs" / f"{VARIANTS[variant]['run_name']}-q{query_id:02d}"


def clear_file(path: Path) -> None:
    if path.is_file():
        path.unlink()


def collect_answer(qdir: Path, workspace_dir: Path, stdout_path: Path) -> str:
    for filename in ["final_report.md", "answer.txt", "proposal.md"]:
        source = workspace_dir / filename
        if source.is_file() and source.read_text(encoding="utf-8").strip():
            destination = qdir / filename
            destination.write_bytes(source.read_bytes())
            return source.read_text(encoding="utf-8").strip()
    return stdout_path.read_text(encoding="utf-8").strip()


def write_reference_answer(reference_root: Path, system_root: Path, query_id: int) -> bool:
    source = reference_root / f"query_{query_id:02d}" / "answer.txt"
    if not source.is_file() or not source.read_text(encoding="utf-8").strip():
        return False
    target_dir = system_root / "EvoScientist" / f"query_{query_id:02d}"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "answer.txt").write_text(source.read_text(encoding="utf-8").strip() + "\n", encoding="utf-8")
    return True


def write_judge_inputs(*, variant_root: Path, variant: str, queries: list[dict[str, Any]]) -> int:
    system_outputs = variant_root / "system_outputs"
    output = variant_root / "judge_inputs.jsonl"
    count = 0
    with output.open("w", encoding="utf-8") as out:
        for query in queries:
            qid = query["id"]
            variant_answer = (
                system_outputs / variant / f"query_{qid:02d}" / "answer.txt"
            ).read_text(encoding="utf-8").strip()
            reference_answer = (
                system_outputs / "EvoScientist" / f"query_{qid:02d}" / "answer.txt"
            ).read_text(encoding="utf-8").strip()
            record = {
                "comparison_id": f"ablation__{variant}__q{qid:02d}__vs__EvoScientist",
                "query_id": qid,
                "topic": query["topic"],
                "question": query["goal"],
                "assistant_1_system": variant,
                "assistant_2_system": "EvoScientist",
                "answer_a": variant_answer,
                "answer_b": reference_answer,
                "judge_template": "reproduction/judge_prompt_template.md",
                "dimensions": DIMENSIONS,
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def run_variant(args: argparse.Namespace, variant: str, queries: list[dict[str, Any]]) -> dict[str, Any]:
    variant_root = args.output_root / variant
    system_root = variant_root / "system_outputs"
    variant_system_root = system_root / variant
    variant_system_root.mkdir(parents=True, exist_ok=True)
    evosci = ROOT / ".venv" / "bin" / "EvoSci"
    if not evosci.exists() and not args.dry_run:
        raise SystemExit("Missing .venv/bin/EvoSci. Run `bash reproduction/run_preflight.sh` first.")

    outputs = []
    complete_queries = []
    missing_reference = []
    for query in queries:
        qid = query["id"]
        qdir = variant_system_root / f"query_{qid:02d}"
        qdir.mkdir(parents=True, exist_ok=True)
        prompt = ablation_prompt(query, variant, proposal_only=args.proposal_only)
        (qdir / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
        (qdir / "query.json").write_text(json.dumps(query, indent=2), encoding="utf-8")
        reference_ok = write_reference_answer(args.reference_root, system_root, qid)
        if not reference_ok:
            missing_reference.append(qid)
        entry = {"query_id": qid, "topic": query["topic"], "dir": str(qdir), "reference_present": reference_ok}
        if args.dry_run:
            entry["status"] = "dry_run"
            outputs.append(entry)
            continue

        workspace_dir = run_workspace_dir(qid, variant)
        if workspace_dir.is_dir():
            shutil.rmtree(workspace_dir)
        clear_file(qdir / "answer.txt")
        cmd = [
            str(evosci),
            "--mode",
            "run",
            "--name",
            f"{VARIANTS[variant]['run_name']}-q{qid:02d}",
            "-p",
            prompt,
            "--ui",
            "cli",
            "--auto-mode",
            "--no-thinking",
        ]
        stdout_path = qdir / "stdout.txt"
        stderr_path = qdir / "stderr.txt"
        start = time.monotonic()
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=args.timeout,
            check=False,
        )
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        answer = collect_answer(qdir, workspace_dir, stdout_path)
        if answer:
            (qdir / "answer.txt").write_text(answer.strip() + "\n", encoding="utf-8")
        entry.update(
            {
                "status": "ok" if result.returncode == 0 and bool(answer) else "failed",
                "returncode": result.returncode,
                "elapsed_seconds": round(time.monotonic() - start, 2),
                "answer_chars": len(answer),
                "workspace_dir": str(workspace_dir),
            }
        )
        if entry["status"] == "ok":
            complete_queries.append(qid)
        outputs.append(entry)

    complete = (
        len(complete_queries) == len(queries)
        and not missing_reference
        and not args.dry_run
    )
    summary = {
        "variant": variant,
        "query_count": len(queries),
        "complete": complete,
        "dry_run": args.dry_run,
        "proposal_only": args.proposal_only,
        "reference_system": "EvoScientist",
        "reference_root": str(args.reference_root),
        "complete_query_ids": complete_queries,
        "missing_reference_query_ids": missing_reference,
        "outputs": outputs,
        "paper_exact": False,
        "caveat": (
            "Replacement ablation run driven by prompt-level disabled-component "
            "constraints. The public checkout does not expose the paper's native "
            "IDE/IVE ablation switches."
        ),
    }
    (variant_root / "system_outputs_complete.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if complete:
        summary["judge_input_records"] = write_judge_inputs(variant_root=variant_root, variant=variant, queries=queries)
        (variant_root / "system_outputs_complete.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=[*VARIANTS.keys(), "all"], default="all")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--query-id", type=int, default=None)
    parser.add_argument("--query-ids", default=None)
    parser.add_argument("--start-id", type=int, default=None)
    parser.add_argument("--end-id", type=int, default=None)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--reference-root", type=Path, default=DEFAULT_REFERENCE_ROOT)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--proposal-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    queries = select_queries(args)
    variants = list(VARIANTS) if args.variant == "all" else [args.variant]
    args.output_root.mkdir(parents=True, exist_ok=True)
    if not args.dry_run:
        ensure_provider_configured()
    results = [run_variant(args, variant, queries) for variant in variants]
    print(
        json.dumps(
            {
                "status": "complete" if all(item["complete"] for item in results) else "incomplete",
                "variants": {item["variant"]: item["complete"] for item in results},
                "dry_run": args.dry_run,
                "query_count": len(queries),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
