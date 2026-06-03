#!/usr/bin/env python3
"""Run the EvoScientist pairwise idea-generation LLM judge.

Input must be JSONL produced by `build_pairwise_judge_inputs.py`. Output is
JSONL compatible with `aggregate_judge_results.py`.

Supported providers:
- google: uses GOOGLE_API_KEY and google-genai.
- openai: uses OPENAI_API_KEY and openai.chat.completions.
- mock: deterministic local scoring for parser/pipeline tests only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DIMENSIONS = ["Clarity", "Novelty", "Feasibility", "Relevance"]
SYSTEM_PROMPT = (
    "You are an AI analysis engine specializing in the comparative evaluation "
    "of two technical ideas. Conduct an objective, in-depth, multi-dimensional "
    "comparison based on a user's research goal and two competing AI-generated "
    "ideas."
)


def make_user_prompt(record: dict[str, Any]) -> str:
    return f"""[Research Goal]
{record["question"]}
[The End of Research Goal]

[The Start of Assistant 1's Idea]
{record["answer_a"]}
[The End of Assistant 1's Idea]

[The Start of Assistant 2's Idea]
{record["answer_b"]}
[The End of Assistant 2's Idea]

Evaluate the two ideas on a 1 to 10 scale for each dimension:
Clarity, Novelty, Feasibility, and Relevance.

Scoring guidance:
- Clarity: distinguish articulacy from actionability. Prioritize concrete
  components, mechanisms, and reproducibility.
- Novelty: distinguish component novelty from architectural novelty.
- Feasibility: evaluate methodological rigor, testability, resource
  accessibility, and risk awareness. Do not penalize uncertainty or
  novel/unproven methods by itself.
- Relevance: first identify the core problem domain, key mechanisms, and
  required scope from the question.

Return only one JSON object, with no markdown and no extra prose:
{{
  "overall_comparison": {{
    "Clarity_analysis": "direct comparison and rationale",
    "Novelty_analysis": "direct comparison and rationale",
    "Feasibility_analysis": "direct comparison and rationale",
    "Relevance_analysis": "direct comparison and rationale"
  }},
  "assistant_1": {{
    "Clarity": 0,
    "Novelty": 0,
    "Feasibility": 0,
    "Relevance": 0
  }},
  "assistant_2": {{
    "Clarity": 0,
    "Novelty": 0,
    "Feasibility": 0,
    "Relevance": 0
  }}
}}"""


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.S)
    if fence:
        stripped = fence.group(1)
    if not stripped.startswith("{"):
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError("judge response does not contain a JSON object")
        stripped = stripped[start : end + 1]
    return json.loads(stripped)


def validate_scores(payload: dict[str, Any]) -> None:
    for assistant in ["assistant_1", "assistant_2"]:
        if assistant not in payload or not isinstance(payload[assistant], dict):
            raise ValueError(f"missing {assistant} scores")
        for dim in DIMENSIONS:
            value = payload[assistant].get(dim)
            if not isinstance(value, int | float):
                raise ValueError(f"{assistant}.{dim} is not numeric: {value!r}")
            if not 1 <= float(value) <= 10:
                raise ValueError(f"{assistant}.{dim} outside 1..10: {value!r}")


def mock_judge(record: dict[str, Any]) -> dict[str, Any]:
    """Deterministic local judge for smoke tests only."""

    def score(text: str) -> dict[str, int]:
        words = len(text.split())
        has_eval = any(token in text.lower() for token in ["evaluation", "benchmark", "ablation"])
        base = 7 if words >= 30 else 5
        return {
            "Clarity": min(10, base + (1 if "method" in text.lower() else 0)),
            "Novelty": min(10, base),
            "Feasibility": min(10, base + (1 if has_eval else 0)),
            "Relevance": min(10, base + 1),
        }

    return {
        "overall_comparison": {
            "Clarity_analysis": "Mock comparison for pipeline validation only.",
            "Novelty_analysis": "Mock comparison for pipeline validation only.",
            "Feasibility_analysis": "Mock comparison for pipeline validation only.",
            "Relevance_analysis": "Mock comparison for pipeline validation only.",
        },
        "assistant_1": score(record["answer_a"]),
        "assistant_2": score(record["answer_b"]),
    }


def call_google(record: dict[str, Any], model: str, temperature: float) -> dict[str, Any]:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=make_user_prompt(record),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    return extract_json_object(response.text or "")


def call_openai(record: dict[str, Any], model: str, temperature: float) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": make_user_prompt(record)},
        ],
    )
    content = response.choices[0].message.content or ""
    return extract_json_object(content)


def judge_record(
    record: dict[str, Any],
    provider: str,
    model: str,
    temperature: float,
) -> dict[str, Any]:
    if provider == "mock":
        payload = mock_judge(record)
    elif provider == "google":
        payload = call_google(record, model, temperature)
    elif provider == "openai":
        payload = call_openai(record, model, temperature)
    else:
        raise ValueError(f"unsupported provider: {provider}")
    validate_scores(payload)
    return {
        "comparison_id": record["comparison_id"],
        "query_id": record["query_id"],
        "assistant_1_system": record["assistant_1_system"],
        "assistant_2_system": record["assistant_2_system"],
        "assistant_1": payload["assistant_1"],
        "assistant_2": payload["assistant_2"],
        "overall_comparison": payload.get("overall_comparison", {}),
        "judge_provider": provider,
        "judge_model": model,
    }


def load_done(output: Path) -> set[str]:
    if not output.is_file():
        return set()
    done = set()
    with output.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                done.add(json.loads(line)["comparison_id"])
    return done


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--provider", choices=["google", "openai", "mock"], default="google")
    parser.add_argument("--model", default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds between API calls.")
    args = parser.parse_args()

    default_models = {
        "google": "gemini-3-flash",
        "openai": "gpt-5-mini",
        "mock": "mock-judge-v1",
    }
    model = args.model or default_models[args.provider]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(args.output) if args.resume else set()

    processed = 0
    skipped = 0
    failed = 0
    mode = "a" if args.resume else "w"
    with args.input.open(encoding="utf-8") as src, args.output.open(mode, encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            record = json.loads(line)
            if record["comparison_id"] in done:
                skipped += 1
                continue
            if args.limit is not None and processed >= args.limit:
                break
            try:
                judged = judge_record(record, args.provider, model, args.temperature)
                dst.write(json.dumps(judged, ensure_ascii=False) + "\n")
                dst.flush()
                processed += 1
            except Exception as exc:
                failed += 1
                error_path = args.output.with_suffix(args.output.suffix + ".errors.jsonl")
                with error_path.open("a", encoding="utf-8") as err:
                    err.write(
                        json.dumps(
                            {
                                "comparison_id": record.get("comparison_id"),
                                "error": str(exc),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                if args.provider != "mock":
                    raise
            if args.sleep:
                time.sleep(args.sleep)

    print(
        json.dumps(
            {
                "status": "ok",
                "provider": args.provider,
                "model": model,
                "processed": processed,
                "skipped": skipped,
                "failed": failed,
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"run_llm_judge.py failed: {exc}", file=sys.stderr)
        raise
