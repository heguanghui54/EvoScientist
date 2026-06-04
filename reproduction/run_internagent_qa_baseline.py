#!/usr/bin/env python3
"""Run InternAgent QA mode on recovered EvoScientist Table 1 queries."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_QUERIES = ROOT / "queries.json"
DEFAULT_CHECKOUT = Path.home() / "research" / "InternAgent"
DEFAULT_OUTPUT_DIR = (
    Path.home() / "research" / "InternAgent" / "outputs" / "evoscientist_table1_queries" / "internagent"
)


def load_queries(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["queries"]


def selected_queries(
    queries: list[dict[str, Any]],
    query_id: int | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    if query_id is not None:
        return [item for item in queries if item["id"] == query_id]
    return queries[:limit] if limit else queries


def configure_env(model: str) -> None:
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    deepseek_base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    if not deepseek_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required for the InternAgent replacement run")
    os.environ.setdefault("OPENAI_API_KEY", deepseek_key)
    os.environ.setdefault("OPENAI_API_BASE_URL", f"{deepseek_base}/v1")
    os.environ.setdefault("OPENAI_BASE_URL", f"{deepseek_base}/v1")
    os.environ.setdefault("DEEPSEEK_BASE_URL", deepseek_base)
    os.environ.setdefault("INTERNAGENT_REPLACEMENT_MODEL", model)


def build_workflow_config(model: str, max_iter: int) -> dict[str, Any]:
    free_tools = ["arxiv_search", "openalex_search", "crossref_search"]
    return {
        "model": {
            "default_model": model,
            "global_planner_model": model,
            "global_execution_model": {
                "execution_model": model,
                "summarizer_model": model,
            },
            "coordinator_model": model,
            "synthesizer_model": model,
            "task_agent_model": model,
        },
        "main": {"max_iter": max_iter, "enable_coordinator": False},
        "global_planner": {
            "max_iter": 1,
            "max_nodes": 4,
            "enable_multi_layer": False,
            "max_retries": 1,
            "tools": {"enabled_tools": free_tools},
        },
        "global_execution": {
            "max_workers": 2,
            "planner": {
                "max_subtasks": 1,
                "tools": {"enabled_tools": free_tools},
            },
            "execution": {
                "max_tool_calls": 2,
                "tools": {"enabled_tools": free_tools},
            },
        },
        "coordinator": {"max_correction_attempts": 1, "tools": {"enabled_tools": free_tools}},
        "synthesizer": {
            "mode": "qa",
            "output_format": "markdown",
            "include_details": True,
            "include_failed_nodes": True,
            "max_output_length": 1000000,
            "polish": False,
        },
        "tools": {"enabled_tools": free_tools},
        "log": {
            "log_level": "INFO",
            "log_dir": "./logs",
            "console_output": True,
            "log_filename_format": "{timestamp}_{agent_type}.log",
            "save_execution_trace": True,
            "trace_output_dir": "./logs/traces",
        },
        "path": {
            "project_root": ".",
            "dataset_dir": "./gaia_dataset",
            "results_dir": "./gaia_results",
            "tmp_dir": "./tmp",
            "cache_dir": "./tmp/cache",
        },
    }


def install_internagent(checkout: Path, model: str):
    sys.path.insert(0, str(checkout))
    dr_agents_path = checkout / "internagent" / "mas" / "agents" / "dr_agents"
    sys.path.insert(0, str(dr_agents_path))

    import workflow.main as workflow_main  # type: ignore
    from internagent.mas.agents.dr_agent import DRAgent  # type: ignore

    original_get_model = workflow_main.get_model

    def patched_get_model(name: str, **kwargs):
        if name == "o4-mini":
            name = model
        return original_get_model(name, **kwargs)

    workflow_main.get_model = patched_get_model
    return DRAgent


def render_answer(item: dict[str, Any], answer: str, model: str) -> str:
    return "\n".join(
        [
            f"# InternAgent QA Replacement Output: Query {item['id']:02d}",
            "",
            f"Topic: {item['topic']}",
            f"Prompt: {item['goal']}",
            f"Model: {model}",
            "Paper-exact: false",
            "",
            "This answer was generated through InternAgent QA mode as a replacement baseline, not from the EvoScientist paper's original raw InternAgent outputs.",
            "",
            "## Answer",
            "",
            answer,
            "",
        ]
    )


async def run_query(agent: Any, item: dict[str, Any]) -> str:
    return str(await agent.execute({"task": item["goal"], "file_path": None}, {}))


async def run(args: argparse.Namespace) -> dict[str, Any]:
    configure_env(args.model)
    DRAgent = install_internagent(args.checkout, args.model)
    workflow_config = build_workflow_config(args.model, args.max_iter)
    agent = DRAgent(model=args.model, config={"mode": "qa", "workflow_config": workflow_config})
    queries = selected_queries(load_queries(args.queries), args.query_id, args.limit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for item in queries:
        output_path = args.output_dir / f"query_{item['id']:02d}.md"
        if args.resume and output_path.is_file() and output_path.stat().st_size >= args.min_bytes:
            results.append({"query_id": item["id"], "status": "skipped", "output": str(output_path)})
            continue
        answer = await run_query(agent, item)
        output_path.write_text(render_answer(item, answer, args.model), encoding="utf-8")
        results.append(
            {
                "query_id": item["id"],
                "status": "written",
                "output": str(output_path),
                "bytes": output_path.stat().st_size,
            }
        )
    return {"baseline": "InternAgent", "model": args.model, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--checkout", type=Path, default=DEFAULT_CHECKOUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--max-iter", type=int, default=1)
    parser.add_argument("--query-id", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--min-bytes", type=int, default=1000)
    args = parser.parse_args()
    result = asyncio.run(run(args))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
