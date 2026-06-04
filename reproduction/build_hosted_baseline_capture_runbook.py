#!/usr/bin/env python3
"""Build hosted capture runbooks for account/UI-only Table 1 baselines."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = ROOT / "hosted_capture_runbooks"

BASELINES: dict[str, dict[str, str]] = {
    "Hypogenic": {
        "slug": "hypogenic",
        "probe": "reproduction/hypogenic_baseline_probe.json",
        "hosted_url": "https://hypogenic.ai/chat",
        "source_dir": "$HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic",
        "gate": "reproduction/hypogenic_hosted_capture_gate.json",
        "mode": "hosted_assistant_capture",
    },
    "Novix": {
        "slug": "novix",
        "probe": "reproduction/novix_baseline_probe.json",
        "hosted_url": "https://novix.science/chat",
        "source_dir": "$HOME/research/novix/outputs/evoscientist_table1_queries/novix",
        "gate": "reproduction/novix_hosted_capture_gate.json",
        "mode": "hosted_ui_or_api_capture",
    },
}


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def slug_for(name: str) -> str:
    return BASELINES[name]["slug"]


def quote(value: str) -> str:
    return shlex.quote(value)


def prompt_for_query(baseline: str, item: dict[str, Any]) -> str:
    return (
        f"# {baseline} Capture Prompt - Query {item['id']:02d}\n\n"
        "Submit the following prompt in one fresh hosted session. Capture the final "
        "assistant answer only after the system has stopped generating.\n\n"
        "```text\n"
        f"{item['goal']}\n"
        "```\n\n"
        "Required final answer shape: a research proposal with a concrete hypothesis, "
        "related-work distinction, method, experiment plan, evaluation metrics, risks, "
        "and limitations. Do not add evaluator commentary to the saved answer file.\n"
    )


def capture_manifest_template(baseline: str, item: dict[str, Any]) -> dict[str, Any]:
    cfg = BASELINES[baseline]
    return {
        "baseline": baseline,
        "query_id": item["id"],
        "topic": item["topic"],
        "goal": item["goal"],
        "hosted_url": cfg["hosted_url"],
        "paper_exact": False,
        "capture_status": "pending",
        "captured_at": None,
        "account_state": {
            "browser_profile": None,
            "login_required": True,
            "session_id_or_url": None,
            "model_or_agent_label": None,
        },
        "output_contract": {
            "answer_path": f"{cfg['source_dir']}/query_{item['id']:02d}.md",
            "minimum_characters": 200,
            "save_final_assistant_answer_only": True,
        },
        "caveat": (
            "Hosted capture is a replacement rerun protocol. It is not the original "
            "EvoScientist paper Table 1 raw baseline output unless the paper authors "
            "provide those exact outputs and metadata."
        ),
    }


def build_runbook(baseline: str, output_root: Path) -> dict[str, Any]:
    cfg = BASELINES[baseline]
    queries = load_queries()
    root = output_root / cfg["slug"]
    prompt_dir = root / "query_prompts"
    manifest_dir = root / "capture_manifests"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)
    capture_steps = []
    for item in queries:
        prompt_path = prompt_dir / f"query_{item['id']:02d}.md"
        manifest_path = manifest_dir / f"query_{item['id']:02d}.json"
        prompt_path.write_text(prompt_for_query(baseline, item), encoding="utf-8")
        manifest_path.write_text(
            json.dumps(capture_manifest_template(baseline, item), indent=2),
            encoding="utf-8",
        )
        capture_steps.append(
            {
                "query_id": item["id"],
                "topic": item["topic"],
                "prompt_path": str(prompt_path),
                "capture_manifest_path": str(manifest_path),
                "expected_answer_path": f"{cfg['source_dir']}/query_{item['id']:02d}.md",
            }
        )
    baseline_slug = cfg["slug"]
    return {
        "date": "2026-06-04",
        "baseline": baseline,
        "mode": cfg["mode"],
        "paper_exact": False,
        "source_probe": cfg["probe"],
        "hosted_url": cfg["hosted_url"],
        "query_count": len(capture_steps),
        "prompt_dir": str(prompt_dir),
        "capture_manifest_dir": str(manifest_dir),
        "source_dir": cfg["source_dir"],
        "capture_steps": capture_steps,
        "access_gate": cfg["gate"],
        "capture_protocol": [
            "Use one fresh hosted session per recovered query.",
            "Record account/profile state, hosted session URL or task id, visible model/agent label, and capture time.",
            "Save only the final assistant answer to query_XX.md; save metadata in capture_manifests/query_XX.json.",
            "Do not mix generated repository examples with Table 1 answers.",
            "After all 30 answers are present, import and judge through the shared swapped pairwise pipeline.",
        ],
        "import_command": (
            ".venv/bin/python reproduction/import_baseline_outputs.py "
            f"--system-name {quote(baseline)} --source {cfg['source_dir']} "
            "--source-format directory --output-root reproduction/artifacts/idea_outputs --strict"
        ),
        "next_commands_after_import": [
            f".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline {quote(baseline)} --output reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl",
            f".venv/bin/python reproduction/run_llm_judge.py --provider deepseek --model deepseek-v4-flash --input reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl --output reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl --resume",
            f".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl --output-csv reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.csv --output-json reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.json",
            f".venv/bin/python reproduction/audit_reproduction_artifacts.py --baseline {quote(baseline)} --judge-inputs reproduction/artifacts/judge_inputs/evosci_vs_{baseline_slug}.jsonl --judge-outputs reproduction/artifacts/judge_outputs/evosci_vs_{baseline_slug}_deepseek.jsonl --aggregate-json reproduction/artifacts/tables/evosci_vs_{baseline_slug}_deepseek.json",
        ],
        "caveat": (
            f"{baseline} is treated as a hosted replacement rerun candidate. The "
            "checked public artifacts do not provide a standalone public batch runner "
            "or the original EvoScientist Table 1 baseline outputs."
        ),
    }


def render_markdown(runbook: dict[str, Any]) -> str:
    lines = [
        f"# {runbook['baseline']} Hosted Capture Runbook",
        "",
        f"Date: {runbook['date']}",
        f"Hosted URL: {runbook['hosted_url']}",
        f"Queries: {runbook['query_count']}",
        f"Paper-exact: `{str(runbook['paper_exact']).lower()}`",
        "",
        runbook["caveat"],
        "",
        "## Capture Protocol",
        "",
    ]
    lines.extend(f"- {step}" for step in runbook["capture_protocol"])
    lines.extend(
        [
            "",
            "## Prompt And Metadata Templates",
            "",
            f"- Prompt directory: `{runbook['prompt_dir']}`",
            f"- Capture manifest directory: `{runbook['capture_manifest_dir']}`",
            f"- Expected answer directory: `{runbook['source_dir']}`",
            "",
            "## Per-Query Checklist",
            "",
        ]
    )
    for item in runbook["capture_steps"]:
        lines.append(
            f"- Query {item['query_id']:02d} ({item['topic']}): prompt `{item['prompt_path']}`, "
            f"answer `{item['expected_answer_path']}`"
        )
    lines.extend(
        [
            "",
            "## Gate, Import, And Judge",
            "",
            "```bash",
            f".venv/bin/python reproduction/verify_hosted_baseline_access.py --baseline {quote(runbook['baseline'])}",
            runbook["import_command"],
            *runbook["next_commands_after_import"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", choices=[*BASELINES.keys(), "all"], default="all")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    selected = BASELINES if args.baseline == "all" else {args.baseline: BASELINES[args.baseline]}
    results = []
    for baseline in selected:
        runbook = build_runbook(baseline, args.output_root)
        root = args.output_root / slug_for(baseline)
        json_path = root / f"{slug_for(baseline)}_hosted_capture_runbook.json"
        md_path = root / f"{slug_for(baseline)}_hosted_capture_runbook.md"
        json_path.write_text(json.dumps(runbook, indent=2), encoding="utf-8")
        md_path.write_text(render_markdown(runbook), encoding="utf-8")
        results.append({"baseline": baseline, "query_count": runbook["query_count"], "output_root": str(root)})
    print(json.dumps({"generated": results}, indent=2))


if __name__ == "__main__":
    main()
