#!/usr/bin/env python3
"""Run AI Scientist-v2 ideation as a bounded replacement baseline."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import time
import types
from pathlib import Path
from typing import Any

import openai
import requests

from build_ai_scientist_v2_ideation_runbook import topic_markdown


ROOT = Path(__file__).resolve().parent
DEFAULT_EXTERNAL_CHECKOUT = Path.home() / "research" / "AI-Scientist-v2"
DEFAULT_OUTPUT_DIR = DEFAULT_EXTERNAL_CHECKOUT / "outputs" / "evoscientist_table1_queries" / "ai_scientist_v2"
DEFAULT_IDEAS_DIR = DEFAULT_EXTERNAL_CHECKOUT / "ai_scientist" / "ideas"


def load_queries(limit: int | None, query_ids: list[int] | None = None) -> list[dict[str, Any]]:
    queries = json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]
    if query_ids:
        wanted = set(query_ids)
        queries = [query for query in queries if query["id"] in wanted]
    return queries[:limit] if limit else queries


def load_external_module(external_checkout: Path):
    sys.path.insert(0, str(external_checkout))
    from ai_scientist import perform_ideation_temp_free as ideation

    return ideation


def create_client(model: str) -> tuple[Any, str]:
    if model == "deepseek-coder-v2-0724":
        return (
            openai.OpenAI(
                api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                timeout=60,
            ),
            model,
        )
    if model == "deepseek-chat":
        return (
            openai.OpenAI(
                api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                timeout=60,
            ),
            "deepseek-coder-v2-0724",
        )
    raise ValueError(f"unsupported bounded runner model: {model}")


def patch_semantic_scholar(ideation: Any, timeout: int, max_results: int) -> None:
    def bounded_search_for_papers(self: Any, query: str) -> list[dict[str, Any]] | None:
        if not query:
            return None
        headers = {}
        if getattr(self, "S2_API_KEY", None):
            headers["X-API-KEY"] = self.S2_API_KEY
        try:
            rsp = requests.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                headers=headers,
                params={
                    "query": query,
                    "limit": max_results,
                    "fields": "title,authors,venue,year,abstract,citationCount",
                },
                timeout=timeout,
            )
            print(f"Response Status Code: {rsp.status_code}", flush=True)
            print(f"Response Content: {rsp.text[:500]}", flush=True)
            rsp.raise_for_status()
            results = rsp.json()
        except Exception as exc:
            print(f"Semantic Scholar bounded search failed: {type(exc).__name__}: {exc}", flush=True)
            return None
        papers = results.get("data", [])
        papers.sort(key=lambda item: item.get("citationCount", 0), reverse=True)
        return papers

    tool = ideation.semantic_scholar_tool
    tool.max_results = max_results
    tool.search_for_papers = types.MethodType(bounded_search_for_papers, tool)

    def bounded_use_tool(self: Any, query: str) -> str:
        papers = self.search_for_papers(query)
        if papers:
            return self.format_papers(papers)
        return (
            "The bounded replacement-baseline runner attempted a Semantic Scholar "
            "search for this query, but no usable results were returned within the "
            "timeout/rate-limit constraints. Treat the literature-search requirement "
            "as attempted, rely on your prior research knowledge, and choose "
            "FinalizeIdea in the next round with a concrete, feasible proposal."
        )

    tool.use_tool = types.MethodType(bounded_use_tool, tool)


def read_ideas(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


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


def write_output(
    output_dir: Path,
    query: dict[str, Any],
    topic_path: Path,
    idea_path: Path,
    ideas: list[dict[str, Any]],
    log_text: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"query_{query['id']:02d}.md"
    log_path = output_dir / f"query_{query['id']:02d}.log"
    log_path.write_text(log_text, encoding="utf-8")
    if not ideas:
        return {
            "id": query["id"],
            "status": "empty",
            "topic": query["topic"],
            "idea_json": str(idea_path),
            "output": str(target),
            "bytes": 0,
            "log": str(log_path),
        }
    answer = render_answer(ideas[0])
    target.write_text(answer, encoding="utf-8")
    return {
        "id": query["id"],
        "status": "ok",
        "topic": query["topic"],
        "idea_json": str(idea_path),
        "topic_file": str(topic_path),
        "output": str(target),
        "bytes": target.stat().st_size,
        "log": str(log_path),
    }


def run_query(
    ideation: Any,
    client: Any,
    client_model: str,
    query: dict[str, Any],
    ideas_dir: Path,
    output_dir: Path,
    num_reflections: int,
    max_num_generations: int,
    resume: bool,
    overwrite: bool,
) -> dict[str, Any]:
    topic_path = ideas_dir / f"query_{query['id']:02d}.md"
    idea_path = ideas_dir / f"query_{query['id']:02d}.json"
    output_path = output_dir / f"query_{query['id']:02d}.md"
    if resume and output_path.is_file() and output_path.stat().st_size > 0 and not overwrite:
        return {
            "id": query["id"],
            "status": "skipped",
            "topic": query["topic"],
            "output": str(output_path),
            "bytes": output_path.stat().st_size,
        }
    topic_path.parent.mkdir(parents=True, exist_ok=True)
    topic_path.write_text(topic_markdown(query), encoding="utf-8")
    if overwrite and idea_path.exists():
        idea_path.unlink()
    log_buffer = io.StringIO()
    start = time.time()
    with contextlib.redirect_stdout(log_buffer), contextlib.redirect_stderr(log_buffer):
        ideation.generate_temp_free_idea(
            idea_fname=str(idea_path),
            client=client,
            model=client_model,
            workshop_description=topic_path.read_text(encoding="utf-8"),
            max_num_generations=max_num_generations,
            num_reflections=num_reflections,
            reload_ideas=False,
        )
    elapsed = round(time.time() - start, 2)
    ideas = read_ideas(idea_path)
    result = write_output(output_dir, query, topic_path, idea_path, ideas, log_buffer.getvalue())
    result["elapsed_seconds"] = elapsed
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-checkout", type=Path, default=DEFAULT_EXTERNAL_CHECKOUT)
    parser.add_argument("--ideas-dir", type=Path, default=DEFAULT_IDEAS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--query-ids", default="")
    parser.add_argument("--model", default="deepseek-coder-v2-0724")
    parser.add_argument("--max-num-generations", type=int, default=1)
    parser.add_argument("--num-reflections", type=int, default=5)
    parser.add_argument("--s2-timeout", type=int, default=20)
    parser.add_argument("--s2-max-results", type=int, default=5)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    ideation = load_external_module(args.external_checkout)
    patch_semantic_scholar(ideation, timeout=args.s2_timeout, max_results=args.s2_max_results)
    client, client_model = create_client(args.model)
    query_ids = [int(item) for item in args.query_ids.split(",") if item.strip()]
    queries = load_queries(args.limit, query_ids=query_ids)
    results = []
    for query in queries:
        print(f"Running AI Scientist-v2 ideation query {query['id']:02d}: {query['topic']}", flush=True)
        try:
            result = run_query(
                ideation=ideation,
                client=client,
                client_model=client_model,
                query=query,
                ideas_dir=args.ideas_dir,
                output_dir=args.output_dir,
                num_reflections=args.num_reflections,
                max_num_generations=args.max_num_generations,
                resume=args.resume,
                overwrite=args.overwrite,
            )
        except Exception as exc:
            result = {
                "id": query["id"],
                "status": "failed",
                "topic": query["topic"],
                "error": f"{type(exc).__name__}: {exc}",
            }
        print(json.dumps(result, ensure_ascii=False), flush=True)
        results.append(result)
    manifest = {
        "date": "2026-06-04",
        "runner": "run_ai_scientist_v2_ideation_baseline.py",
        "baseline": "AI Scientist-v2",
        "external_checkout": str(args.external_checkout),
        "model": args.model,
        "client_model": client_model,
        "max_num_generations": args.max_num_generations,
        "num_reflections": args.num_reflections,
        "s2_timeout": args.s2_timeout,
        "s2_max_results": args.s2_max_results,
        "query_count": len(results),
        "ok_count": sum(1 for item in results if item["status"] in {"ok", "skipped"}),
        "results": results,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": "complete" if manifest["ok_count"] == len(results) else "incomplete", "manifest": str(manifest_path), "ok_count": manifest["ok_count"], "query_count": len(results)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
