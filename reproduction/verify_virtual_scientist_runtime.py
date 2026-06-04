#!/usr/bin/env python3
"""Check whether Virtual Scientist can produce replacement outputs locally."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CHECKOUT = Path.home() / "research" / "Virtual-Scientists"
PINNED_HEAD = "07097fd67efd177dd6d5304684d3657dc3411bc1"


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


def http_json(url: str, timeout: int = 3) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"available": True, "status": response.status, "body_prefix": body[:500]}
    except urllib.error.HTTPError as exc:
        return {"available": True, "status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def ollama_models(base_url: str) -> list[str]:
    response = http_json(f"{base_url.rstrip('/')}/api/tags")
    if not response.get("available") or response.get("status") != 200:
        return []
    try:
        payload = json.loads(response.get("body_prefix", "{}"))
    except json.JSONDecodeError:
        return []
    return sorted(item.get("name", "") for item in payload.get("models", []) if item.get("name"))


def data_inventory(data_root: Path) -> dict[str, Any]:
    expected_names = [
        "Papers",
        "Embeddings",
        "Authors",
        "adjacency.txt",
        "papers",
        "embeddings",
        "authors",
    ]
    existing = [name for name in expected_names if (data_root / name).exists()]
    return {
        "data_root": str(data_root),
        "exists": data_root.exists(),
        "expected_name_hits": existing,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    checkout = args.checkout.expanduser()
    data_root = args.data_root.expanduser()
    commands = {
        "python3": command_version("python3", ["--version"]),
        "git": command_version("git", ["--version"]),
        "ollama": command_version("ollama", ["--version"]),
    }
    checkout_head = git_head(checkout)
    spec_dir = ROOT / "virtual_scientist_adapter_runbook" / "simulation_specs"
    spec_templates = sorted(spec_dir.glob("query_*.json"))
    data = data_inventory(data_root)
    models = ollama_models(args.ollama_url)
    required_models = ["llama3.1", "llama3.1:70b", "mxbai-embed-large"]
    missing_models = [
        model
        for model in required_models
        if not any(installed == model or installed.startswith(model + ":") for installed in models)
    ]
    faiss_available = importlib.util.find_spec("faiss") is not None
    blocking_items = []
    if not checkout.is_dir():
        blocking_items.append("missing pinned Virtual-Scientists checkout")
    elif checkout_head != PINNED_HEAD:
        blocking_items.append("Virtual-Scientists checkout is not at the pinned probe commit")
    if not (checkout / "sci_platform" / "run.py").is_file():
        blocking_items.append("sci_platform/run.py is not present")
    if not (checkout / "sci_platform" / "sci_platform.py").is_file():
        blocking_items.append("sci_platform/sci_platform.py is not present")
    if len(spec_templates) != 30:
        blocking_items.append("30 per-query Virtual Scientist simulation specs have not been generated")
    if not data["exists"] or len(data["expected_name_hits"]) < 3:
        blocking_items.append("AMiner-derived Virtual Scientist data package is not installed at the requested data root")
    if not faiss_available:
        blocking_items.append("Python faiss module is not importable")
    if not commands["ollama"]["available"]:
        blocking_items.append("Ollama CLI is not installed")
    if missing_models:
        blocking_items.append("required Ollama models are missing: " + ", ".join(missing_models))
    return {
        "date": "2026-06-04",
        "baseline": "Virtual Scientist",
        "checkout": str(checkout),
        "pinned_head": PINNED_HEAD,
        "checkout_head": checkout_head,
        "data_inventory": data,
        "commands": commands,
        "faiss_available": faiss_available,
        "ollama_url": args.ollama_url,
        "ollama_models": models,
        "required_ollama_models": required_models,
        "simulation_spec_dir": str(spec_dir),
        "simulation_spec_count": len(spec_templates),
        "status": "ready" if not blocking_items else "not_ready",
        "blocking_items": blocking_items,
        "adapter_runbook": "reproduction/virtual_scientist_adapter_runbook/virtual_scientist_adapter_runbook.json",
        "caveat": (
            "Virtual Scientist is a VirSci team-simulation platform, not a drop-in "
            "runner for the recovered EvoScientist natural-language queries. This "
            "gate verifies whether a replacement rerun can start from generated "
            "per-query simulation specs."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Virtual Scientist Runtime Gate",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Checkout: `{report['checkout']}`",
        f"Simulation specs: {report['simulation_spec_count']}",
        f"Data root: `{report['data_inventory']['data_root']}`",
        f"Ollama URL: `{report['ollama_url']}`",
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
    lines.extend(["", "## Commands", "", "| Command | Available | Version/Path |", "| --- | --- | --- |"])
    for name, item in report["commands"].items():
        lines.append(
            f"| {name} | {item['available']} | `{item.get('version') or item.get('path') or ''}` |"
        )
    lines.extend(
        [
            "",
            "## Data And Models",
            "",
            f"- FAISS importable: {report['faiss_available']}",
            f"- Data name hits: {', '.join(report['data_inventory']['expected_name_hits']) or 'none'}",
            f"- Required Ollama models: {', '.join(report['required_ollama_models'])}",
            f"- Installed Ollama models: {', '.join(report['ollama_models']) or 'none detected'}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, default=DEFAULT_CHECKOUT)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(os.getenv("VIRTUAL_SCIENTIST_DATA_ROOT", str(DEFAULT_CHECKOUT / "data"))),
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    parser.add_argument("--output-json", type=Path, default=ROOT / "virtual_scientist_runtime_gate.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "virtual_scientist_runtime_gate.md")
    args = parser.parse_args()
    report = build_report(args)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "blocking_items": report["blocking_items"]}, indent=2))


if __name__ == "__main__":
    main()
