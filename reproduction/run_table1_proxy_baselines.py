#!/usr/bin/env python3
"""Generate proxy replacement outputs for missing Table 1 baselines.

The public artifacts do not include original raw Table 1 answers for several
paper baselines. This runner creates clearly marked proxy replacement outputs
using one OpenAI-compatible model with baseline-specific prompting. It is useful
for completing the evaluation pipeline shape, but it is not paper-exact
evidence for the original systems.
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
ENV_FILE = Path.home() / ".codex" / "env"
DEFAULT_OUTPUT = REPRO / "artifacts" / "idea_outputs"
MISSING_TABLE1_BASELINES = [
    "Virtual Scientist",
    "AI-Researcher",
    "Hypogenic",
    "Novix",
    "K-Dense",
]

BASELINE_PROFILES = {
    "Virtual Scientist": (
        "Act as a proxy for a multi-agent virtual scientist team. Deliberately "
        "separate roles such as principal investigator, method designer, "
        "skeptical reviewer, and experiment engineer before converging on one "
        "research proposal."
    ),
    "AI-Researcher": (
        "Act as a proxy for a benchmark-oriented AI researcher. Frame the idea "
        "as a formal research problem with a benchmark instance, task "
        "definition, measurable success criteria, and reproducibility checks."
    ),
    "Hypogenic": (
        "Act as a proxy for a hypothesis-generation research assistant. Start "
        "from a crisp hypothesis, explain why it is surprising, and design a "
        "targeted experiment to falsify or support it."
    ),
    "Novix": (
        "Act as a proxy for an autonomous research workflow assistant. Emphasize "
        "stepwise planning, literature positioning, implementation milestones, "
        "and risk controls."
    ),
    "K-Dense": (
        "Act as a proxy for a knowledge-dense research agent. Use compact, "
        "evidence-aware reasoning, name the key concepts and datasets, and "
        "avoid vague claims."
    ),
}

SYSTEM_PROMPT = (
    "You are generating replacement-baseline research ideas for an EvoScientist "
    "paper reproduction. Do not claim to be the original baseline system, do "
    "not claim to have run experiments, and do not fabricate citations. Produce "
    "one concrete, testable research proposal."
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


def openai_compatible_client(api_key_env: str, base_url_env: str):
    api_key = os.environ.get(api_key_env)
    base_url = os.environ.get(base_url_env)
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")
    if not base_url:
        raise RuntimeError(f"{base_url_env} is not set")
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=base_url)


def make_prompt(baseline: str, query: dict[str, Any]) -> str:
    profile = BASELINE_PROFILES[baseline]
    return f"""This is a proxy replacement rerun for the Table 1 baseline named: {baseline}.
It is not the original paper's raw baseline output.

Baseline profile:
{profile}

Research query:
{query["goal"]}

Return one final proposal with these sections:
1. Title
2. Problem and motivation
3. Core hypothesis
4. Method
5. Dataset or benchmark
6. Evaluation metrics
7. Baselines
8. Ablations
9. Failure modes and feasibility risks

Keep the proposal concrete enough for another researcher to implement."""


def call_model(
    *,
    client: Any,
    model: str,
    prompt: str,
    temperature: float,
    max_retries: int,
    retry_sleep: float,
) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content or ""
            if not content.strip():
                raise RuntimeError("empty model response")
            return content.strip()
        except Exception as exc:  # pragma: no cover - network/API guard.
            last_error = exc
            if attempt == max_retries:
                break
            time.sleep(retry_sleep * attempt)
    raise RuntimeError(f"model call failed after {max_retries} attempts: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action="append", choices=MISSING_TABLE1_BASELINES)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--query-id", type=int, default=None)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--provider", choices=["monica", "deepseek", "openai-compatible"], default="monica")
    parser.add_argument("--model", default="gemini-3-flash-preview")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--retry-sleep", type=float, default=5.0)
    args = parser.parse_args()

    load_env_file()
    provider_env = {
        "monica": ("MONICA_API_KEY", "MONICA_BASE_URL"),
        "deepseek": ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"),
        "openai-compatible": ("API_KEY", "BASE_URL"),
    }
    client = None
    if not args.dry_run:
        api_key_env, base_url_env = provider_env[args.provider]
        client = openai_compatible_client(api_key_env, base_url_env)

    baselines = args.baseline or MISSING_TABLE1_BASELINES
    queries = load_queries()
    if args.query_id is not None:
        queries = [query for query in queries if query["id"] == args.query_id]
        if not queries:
            raise SystemExit(f"Unknown query id: {args.query_id}")
    if args.limit is not None:
        queries = queries[: args.limit]

    generated = 0
    skipped = 0
    failed = 0

    for baseline in baselines:
        baseline_dir = args.output_root / baseline
        baseline_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "runner": "run_table1_proxy_baselines.py",
            "baseline": baseline,
            "mode": "proxy_replacement_baseline",
            "paper_exact": False,
            "provider": args.provider,
            "model": args.model,
            "temperature": args.temperature,
            "query_count": len(queries),
            "caveat": (
                "Proxy replacement output generated from baseline-specific "
                "prompting. This is not the original paper raw Table 1 output."
            ),
            "outputs": [],
        }
        for query in queries:
            qdir = baseline_dir / f"query_{query['id']:02d}"
            qdir.mkdir(parents=True, exist_ok=True)
            answer_path = qdir / "answer.txt"
            prompt = make_prompt(baseline, query)
            (qdir / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
            (qdir / "query.json").write_text(json.dumps(query, indent=2), encoding="utf-8")
            entry = {"id": query["id"], "topic": query["topic"], "dir": str(qdir)}
            if args.resume and answer_path.is_file() and answer_path.read_text(encoding="utf-8").strip():
                entry["status"] = "skipped"
                skipped += 1
                manifest["outputs"].append(entry)
                continue
            if args.dry_run:
                entry["status"] = "dry_run"
                skipped += 1
                manifest["outputs"].append(entry)
                continue
            try:
                answer = call_model(
                    client=client,
                    model=args.model,
                    prompt=prompt,
                    temperature=args.temperature,
                    max_retries=args.max_retries,
                    retry_sleep=args.retry_sleep,
                )
                answer_path.write_text(answer + "\n", encoding="utf-8")
                entry["status"] = "ok"
                generated += 1
            except Exception as exc:
                entry["status"] = "failed"
                entry["error"] = str(exc)
                failed += 1
                (qdir / "error.txt").write_text(str(exc) + "\n", encoding="utf-8")
                manifest["outputs"].append(entry)
                (baseline_dir / "manifest.json").write_text(
                    json.dumps(manifest, indent=2), encoding="utf-8"
                )
                raise
            manifest["outputs"].append(entry)
            (baseline_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            if args.sleep:
                time.sleep(args.sleep)
        (baseline_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "baselines": baselines,
                "queries": len(queries),
                "generated": generated,
                "skipped": skipped,
                "failed": failed,
                "output_root": str(args.output_root),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"run_table1_proxy_baselines.py failed: {exc}", file=sys.stderr)
        raise
