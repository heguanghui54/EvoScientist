#!/usr/bin/env python3
"""Generate a direct-LLM baseline for the paper's 30 idea-generation queries.

This is a reproducible replacement baseline, not one of the paper's original
seven systems. It asks an OpenAI-compatible model to answer each query directly
without EvoScientist's agent graph, memory, evolution, tools, or shell access.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "reproduction"
DEFAULT_OUTPUT = REPRO / "artifacts" / "idea_outputs" / "Direct-DeepSeek"
ENV_FILE = Path.home() / ".codex" / "env"

SYSTEM_PROMPT = (
    "You are a careful research assistant generating one concrete, testable "
    "scientific research proposal. Do not claim to have run experiments, search "
    "the web, call tools, or access hidden papers. Be specific and reproducible."
)


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def load_queries() -> list[dict[str, Any]]:
    return json.loads((REPRO / "queries.json").read_text(encoding="utf-8"))["queries"]


def make_prompt(goal: str) -> str:
    return (
        "Produce one concrete research proposal for the following paper "
        "reproduction query. Do not execute tools, shell commands, web searches, "
        "or code. Return a final answer with: title, problem, hypothesis, method, "
        "dataset/benchmark, evaluation metrics, baselines, ablations, and "
        "expected failure modes.\n\n"
        f"Query: {goal}"
    )


def openai_compatible_client(api_key_env: str, base_url_env: str):
    api_key = os.environ.get(api_key_env)
    base_url = os.environ.get(base_url_env)
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")
    if not base_url:
        raise RuntimeError(f"{base_url_env} is not set")
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=base_url)


def call_model(
    *,
    client: Any,
    model: str,
    prompt: str,
    temperature: float,
) -> str:
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--query-id", type=int, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--system-name", default="Direct-DeepSeek")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--api-key-env", default="DEEPSEEK_API_KEY")
    parser.add_argument("--base-url-env", default="DEEPSEEK_BASE_URL")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env_file()
    queries = load_queries()
    if args.query_id is not None:
        queries = [q for q in queries if q["id"] == args.query_id]
        if not queries:
            raise SystemExit(f"Unknown query id: {args.query_id}")
    if args.limit is not None:
        queries = queries[: args.limit]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    client = None if args.dry_run else openai_compatible_client(args.api_key_env, args.base_url_env)
    manifest = {
        "runner": "run_direct_baseline.py",
        "system_name": args.system_name,
        "model": args.model,
        "dry_run": args.dry_run,
        "query_count": len(queries),
        "outputs": [],
    }

    for query in queries:
        qdir = args.output_dir / f"query_{query['id']:02d}"
        qdir.mkdir(parents=True, exist_ok=True)
        prompt = make_prompt(query["goal"])
        answer_path = qdir / "answer.txt"
        (qdir / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
        (qdir / "query.json").write_text(json.dumps(query, indent=2), encoding="utf-8")
        entry = {"id": query["id"], "topic": query["topic"], "dir": str(qdir)}
        if args.resume and answer_path.is_file() and answer_path.read_text(encoding="utf-8").strip():
            entry["status"] = "skipped"
            manifest["outputs"].append(entry)
            continue
        if args.dry_run:
            entry["status"] = "dry_run"
            manifest["outputs"].append(entry)
            continue
        try:
            answer = call_model(
                client=client,
                model=args.model,
                prompt=prompt,
                temperature=args.temperature,
            )
            answer_path.write_text(answer.strip() + "\n", encoding="utf-8")
            entry["status"] = "ok"
        except Exception as exc:
            entry["status"] = "failed"
            entry["error"] = str(exc)
            (qdir / "error.txt").write_text(str(exc) + "\n", encoding="utf-8")
            manifest["outputs"].append(entry)
            (args.output_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            raise
        manifest["outputs"].append(entry)
        (args.output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        if args.sleep:
            time.sleep(args.sleep)

    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "ok",
                "system_name": args.system_name,
                "outputs": len(manifest["outputs"]),
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"run_direct_baseline.py failed: {exc}", file=sys.stderr)
        raise
