#!/usr/bin/env python3
"""Check whether the public AI-Researcher runner can produce replacement outputs."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CHECKOUT = Path.home() / "research" / "AI-Researcher"
PINNED_HEAD = "f9a6f8480860c193afff600eeffe3defcee8a978"


def command_version(command: str, version_args: list[str] | None = None) -> dict[str, Any]:
    path = shutil.which(command)
    result: dict[str, Any] = {"command": command, "path": path, "available": bool(path)}
    if not path:
        return result
    try:
        output = subprocess.check_output(
            [command, *(version_args or ["--version"])],
            text=True,
            stderr=subprocess.STDOUT,
            timeout=10,
        ).strip()
    except Exception as exc:
        output = f"{type(exc).__name__}: {exc}"
    result["version"] = output
    return result


def git_head(path: Path) -> str | None:
    if not (path / ".git").is_dir():
        return None
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).strip()
    except subprocess.CalledProcessError:
        return None


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    checkout = args.checkout.expanduser()
    env_keys = {
        "CATEGORY": bool(os.getenv("CATEGORY")),
        "INSTANCE_ID": bool(os.getenv("INSTANCE_ID")),
        "TASK_LEVEL": bool(os.getenv("TASK_LEVEL")),
        "CONTAINER_NAME": bool(os.getenv("CONTAINER_NAME")),
        "WORKPLACE_NAME": bool(os.getenv("WORKPLACE_NAME")),
        "CACHE_PATH": bool(os.getenv("CACHE_PATH")),
        "PORT": bool(os.getenv("PORT")),
        "MAX_ITER_TIMES": bool(os.getenv("MAX_ITER_TIMES")),
        "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
        "GITHUB_AI_TOKEN": bool(os.getenv("GITHUB_AI_TOKEN")),
    }
    commands = {
        "python": command_version("python3", ["--version"]),
        "docker": command_version("docker", ["--version"]),
        "git": command_version("git", ["--version"]),
    }
    checkout_head = git_head(checkout)
    benchmark_template_dir = ROOT / "ai_researcher_adapter_runbook" / "benchmark_instances"
    benchmark_templates = sorted(benchmark_template_dir.glob("query_*.json"))
    blocking_items = []
    if not checkout.is_dir():
        blocking_items.append("missing pinned AI-Researcher checkout")
    elif checkout_head != PINNED_HEAD:
        blocking_items.append("AI-Researcher checkout is not at the pinned probe commit")
    if not commands["docker"]["available"]:
        blocking_items.append("Docker CLI is not installed or unavailable")
    if not env_keys["OPENROUTER_API_KEY"]:
        blocking_items.append("OPENROUTER_API_KEY is not configured")
    if not env_keys["GITHUB_AI_TOKEN"]:
        blocking_items.append("GITHUB_AI_TOKEN is not configured")
    if len(benchmark_templates) != 30:
        blocking_items.append("30 per-query benchmark-instance templates have not been generated")
    return {
        "date": "2026-06-04",
        "baseline": "AI-Researcher",
        "checkout": str(checkout),
        "pinned_head": PINNED_HEAD,
        "checkout_head": checkout_head,
        "env_keys": env_keys,
        "commands": commands,
        "benchmark_template_dir": str(benchmark_template_dir),
        "benchmark_template_count": len(benchmark_templates),
        "status": "ready" if not blocking_items else "not_ready",
        "blocking_items": blocking_items,
        "adapter_runbook": "reproduction/ai_researcher_adapter_runbook/ai_researcher_adapter_runbook.json",
        "caveat": (
            "AI-Researcher is benchmark-instance based and is not a drop-in "
            "runner for the recovered EvoScientist natural-language queries. "
            "This gate verifies whether a replacement rerun can start from "
            "generated per-query benchmark-instance templates."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AI-Researcher Runtime Gate",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Checkout: `{report['checkout']}`",
        f"Benchmark templates: {report['benchmark_template_count']}",
        "",
        report["caveat"],
        "",
        "## Blocking Items",
        "",
    ]
    if report["blocking_items"]:
        lines.extend(f"- {item}" for item in report["blocking_items"])
    else:
        lines.append("- None")
    lines.extend(["", "## Environment Keys", "", "| Key | Present |", "| --- | --- |"])
    for name, present in report["env_keys"].items():
        lines.append(f"| {name} | {present} |")
    lines.extend(["", "## Commands", "", "| Command | Available | Version/Path |", "| --- | --- | --- |"])
    for name, item in report["commands"].items():
        lines.append(
            f"| {name} | {item['available']} | `{item.get('version') or item.get('path') or ''}` |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, default=DEFAULT_CHECKOUT)
    parser.add_argument("--output-json", type=Path, default=ROOT / "ai_researcher_runtime_gate.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "ai_researcher_runtime_gate.md")
    args = parser.parse_args()
    report = build_report(args)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "blocking_items": report["blocking_items"]}, indent=2))


if __name__ == "__main__":
    main()
