#!/usr/bin/env python3
"""Capture K-Dense BYOK `/run_sse` answers for the recovered paper queries."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = Path.home() / "research" / "k-dense-byok" / "outputs" / "evoscientist_table1_queries" / "k_dense"
APP_NAME = "kady_agent"
USER_ID = "user"


def load_queries(limit: int | None, query_ids: list[int] | None = None) -> list[dict[str, Any]]:
    queries = json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]
    if query_ids:
        wanted = set(query_ids)
        queries = [query for query in queries if query["id"] in wanted]
    return queries[:limit] if limit else queries


def http_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def create_session(backend_url: str, timeout: int) -> str:
    data = http_json(
        f"{backend_url.rstrip('/')}/apps/{APP_NAME}/users/{USER_ID}/sessions",
        payload={},
        timeout=timeout,
    )
    session_id = data.get("id")
    if not isinstance(session_id, str) or not session_id:
        raise RuntimeError(f"bad K-Dense session response: {data}")
    return session_id


def parse_sse(raw: str) -> tuple[str, list[dict[str, Any]]]:
    events = []
    text_parts = []
    for line in raw.splitlines():
        if not line.startswith("data: "):
            continue
        payload = line[len("data: "):].strip()
        if not payload:
            continue
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            continue
        events.append(event)
        for part in event.get("content", {}).get("parts", []) or []:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
    return "".join(text_parts).strip(), events


def run_query(
    backend_url: str,
    query: dict[str, Any],
    model: str,
    expert_model: str | None,
    timeout: int,
) -> dict[str, Any]:
    session_id = create_session(backend_url, timeout)
    prompt = (
        "Generate a concise, feasible, and novel machine-learning research proposal "
        "for this recovered EvoScientist evaluation query. Include a concrete "
        "hypothesis, related-work distinction, experimental plan, evaluation "
        "metrics, and limitations.\n\n"
        f"Topic: {query['topic']}\n"
        f"Goal: {query['goal']}"
    )
    state_delta: dict[str, Any] = {}
    if model:
        state_delta["_model"] = model
    if expert_model:
        state_delta["_expertModel"] = expert_model
    payload = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": session_id,
        "newMessage": {"role": "user", "parts": [{"text": prompt}]},
        "streaming": True,
    }
    if state_delta:
        payload["state_delta"] = state_delta
    request = urllib.request.Request(
        f"{backend_url.rstrip('/')}/run_sse",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
    text, events = parse_sse(raw)
    return {
        "session_id": session_id,
        "prompt": prompt,
        "answer": text,
        "events": events,
        "raw_sse": raw,
    }


def write_query(output_dir: Path, query: dict[str, Any], result: dict[str, Any], elapsed: float) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    qid = query["id"]
    answer_path = output_dir / f"query_{qid:02d}.md"
    raw_path = output_dir / f"query_{qid:02d}.sse"
    meta_path = output_dir / f"query_{qid:02d}.json"
    answer = result["answer"]
    answer_path.write_text(answer, encoding="utf-8")
    raw_path.write_text(result["raw_sse"], encoding="utf-8")
    meta = {
        "query_id": qid,
        "topic": query["topic"],
        "session_id": result["session_id"],
        "elapsed_seconds": round(elapsed, 2),
        "answer_bytes": answer_path.stat().st_size,
        "event_count": len(result["events"]),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {
        "id": qid,
        "status": "ok" if answer.strip() else "empty",
        "topic": query["topic"],
        "output": str(answer_path),
        "bytes": answer_path.stat().st_size,
        "raw_sse": str(raw_path),
        "metadata": str(meta_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend-url", default="http://localhost:8000")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--query-ids", default="")
    parser.add_argument("--model", default="ollama/qwen3.6")
    parser.add_argument("--expert-model", default="")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    query_ids = [int(item) for item in args.query_ids.split(",") if item.strip()]
    queries = load_queries(args.limit, query_ids=query_ids)
    results = []
    for query in queries:
        answer_path = args.output_dir / f"query_{query['id']:02d}.md"
        if args.resume and answer_path.is_file() and answer_path.stat().st_size > 0:
            item = {
                "id": query["id"],
                "status": "skipped",
                "topic": query["topic"],
                "output": str(answer_path),
                "bytes": answer_path.stat().st_size,
            }
            print(json.dumps(item), flush=True)
            results.append(item)
            continue
        print(f"Running K-Dense query {query['id']:02d}: {query['topic']}", flush=True)
        start = time.time()
        try:
            result = run_query(
                backend_url=args.backend_url,
                query=query,
                model=args.model,
                expert_model=args.expert_model or None,
                timeout=args.timeout,
            )
            item = write_query(args.output_dir, query, result, time.time() - start)
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            item = {
                "id": query["id"],
                "status": "failed",
                "topic": query["topic"],
                "error": f"{type(exc).__name__}: {exc}",
            }
        print(json.dumps(item, ensure_ascii=False), flush=True)
        results.append(item)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "date": "2026-06-04",
        "runner": "run_k_dense_byok_adapter.py",
        "baseline": "K-Dense",
        "backend_url": args.backend_url,
        "model": args.model,
        "expert_model": args.expert_model,
        "query_count": len(results),
        "ok_count": sum(1 for item in results if item["status"] in {"ok", "skipped"}),
        "results": results,
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": "complete" if manifest["ok_count"] == len(results) else "incomplete", "manifest": str(manifest_path), "ok_count": manifest["ok_count"], "query_count": len(results)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
