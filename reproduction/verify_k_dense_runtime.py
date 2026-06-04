#!/usr/bin/env python3
"""Check whether the pinned K-Dense BYOK adapter can run locally."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CHECKOUT = Path.home() / "research" / "k-dense-byok"
PINNED_HEAD = "593c49b8e79c704c5979ec81c49f1791b5114083"


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
            return {
                "available": True,
                "status": response.status,
                "body_prefix": body[:500],
            }
    except urllib.error.HTTPError as exc:
        return {"available": True, "status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    checkout = args.checkout.expanduser()
    env_keys = {
        "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
        "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
        "GOOGLE_GEMINI_BASE_URL": bool(os.getenv("GOOGLE_GEMINI_BASE_URL")),
        "OLLAMA_BASE_URL": bool(os.getenv("OLLAMA_BASE_URL")),
        "EXA_API_KEY": bool(os.getenv("EXA_API_KEY")),
        "PARALLEL_API_KEY": bool(os.getenv("PARALLEL_API_KEY")),
        "PAPERCLIP_API_KEY": bool(os.getenv("PAPERCLIP_API_KEY")),
    }
    commands = {
        "python3.13": command_version("python3.13", ["--version"]),
        "uv": command_version("uv", ["--version"]),
        "node": command_version("node", ["--version"]),
        "npm": command_version("npm", ["--version"]),
        "gemini": command_version("gemini", ["--version"]),
        "ollama": command_version("ollama", ["--version"]),
    }
    services = {
        "k_dense_backend": http_json(f"{args.backend_url.rstrip('/')}/docs"),
        "ollama": http_json(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/tags"),
    }
    checkout_head = git_head(checkout)
    has_openrouter_path = env_keys["OPENROUTER_API_KEY"]
    has_ollama_path = services["ollama"]["available"] and services["ollama"].get("status") == 200
    blocking_items = []
    if not checkout.is_dir():
        blocking_items.append("missing pinned k-dense-byok checkout")
    elif checkout_head != PINNED_HEAD:
        blocking_items.append("k-dense-byok checkout is not at the pinned probe commit")
    if not commands["python3.13"]["available"]:
        blocking_items.append("python3.13 is not installed")
    if not commands["uv"]["available"]:
        blocking_items.append("uv is not installed")
    if not commands["gemini"]["available"]:
        blocking_items.append("Gemini CLI is not installed")
    if not (has_openrouter_path or has_ollama_path):
        blocking_items.append("neither OPENROUTER_API_KEY nor a reachable Ollama server is available")
    if not (
        services["k_dense_backend"]["available"]
        and services["k_dense_backend"].get("status") == 200
    ):
        blocking_items.append("K-Dense backend is not running at the requested backend URL")
    return {
        "date": "2026-06-04",
        "baseline": "K-Dense",
        "checkout": str(checkout),
        "pinned_head": PINNED_HEAD,
        "checkout_head": checkout_head,
        "backend_url": args.backend_url,
        "env_keys": env_keys,
        "commands": commands,
        "services": services,
        "status": "ready" if not blocking_items else "not_ready",
        "blocking_items": blocking_items,
        "adapter": "reproduction/run_k_dense_byok_adapter.py",
        "caveat": (
            "K-Dense BYOK is a local web/API adapter candidate, not a paper-exact "
            "raw Table 1 artifact. This gate verifies whether a replacement rerun "
            "can start from the pinned public checkout."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# K-Dense Runtime Gate",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Checkout: `{report['checkout']}`",
        f"Backend URL: `{report['backend_url']}`",
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
    lines.extend(["", "## Environment Keys", "", "| Key | Present |", "| --- | --- |"])
    for name, present in report["env_keys"].items():
        lines.append(f"| {name} | {present} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, default=DEFAULT_CHECKOUT)
    parser.add_argument("--backend-url", default="http://localhost:8000")
    parser.add_argument("--output-json", type=Path, default=ROOT / "k_dense_runtime_gate.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "k_dense_runtime_gate.md")
    args = parser.parse_args()
    report = build_report(args)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "blocking_items": report["blocking_items"]}, indent=2))


if __name__ == "__main__":
    main()
