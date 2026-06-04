#!/usr/bin/env python3
"""Check whether a hosted baseline capture can be imported locally."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent

BASELINES: dict[str, dict[str, str]] = {
    "Hypogenic": {
        "slug": "hypogenic",
        "hosted_url": "https://hypogenic.ai/chat",
        "output_dir": str(Path.home() / "research" / "hypogenic" / "outputs" / "evoscientist_table1_queries" / "hypogenic"),
        "ready_env": "HYPOGENIC_CAPTURE_READY",
        "session_note_env": "HYPOGENIC_SESSION_NOTE",
        "runbook": "reproduction/hosted_capture_runbooks/hypogenic/hypogenic_hosted_capture_runbook.json",
    },
    "Novix": {
        "slug": "novix",
        "hosted_url": "https://novix.science/chat",
        "output_dir": str(Path.home() / "research" / "novix" / "outputs" / "evoscientist_table1_queries" / "novix"),
        "ready_env": "NOVIX_CAPTURE_READY",
        "session_note_env": "NOVIX_SESSION_NOTE",
        "runbook": "reproduction/hosted_capture_runbooks/novix/novix_hosted_capture_runbook.json",
    },
}


def http_probe(url: str, timeout: int = 8) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "EvoScientist-reproduction-audit"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(300).decode("utf-8", errors="replace")
            return {"available": True, "status": response.status, "body_prefix": body}
    except urllib.error.HTTPError as exc:
        return {"available": True, "status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def count_answer_files(output_dir: Path) -> dict[str, Any]:
    files = []
    for query_id in range(1, 31):
        for suffix in [".md", ".txt", ".json"]:
            candidate = output_dir / f"query_{query_id:02d}{suffix}"
            if candidate.is_file() and candidate.read_text(encoding="utf-8").strip():
                files.append(str(candidate))
                break
    return {"output_dir": str(output_dir), "answer_count": len(files), "answer_files": files}


def build_report(baseline: str) -> dict[str, Any]:
    cfg = BASELINES[baseline]
    slug = cfg["slug"]
    runbook_path = ROOT / "hosted_capture_runbooks" / slug / f"{slug}_hosted_capture_runbook.json"
    prompt_dir = ROOT / "hosted_capture_runbooks" / slug / "query_prompts"
    manifest_dir = ROOT / "hosted_capture_runbooks" / slug / "capture_manifests"
    prompt_count = len(list(prompt_dir.glob("query_*.md")))
    manifest_count = len(list(manifest_dir.glob("query_*.json")))
    output_inventory = count_answer_files(Path(cfg["output_dir"]))
    ready_flag = os.getenv(cfg["ready_env"]) == "1"
    session_note_present = bool(os.getenv(cfg["session_note_env"]))
    hosted_probe = http_probe(cfg["hosted_url"])
    blocking_items = []
    if not runbook_path.is_file():
        blocking_items.append("hosted capture runbook has not been generated")
    if prompt_count != 30:
        blocking_items.append("30 hosted query prompt templates have not been generated")
    if manifest_count != 30:
        blocking_items.append("30 capture manifest templates have not been generated")
    if not hosted_probe["available"]:
        blocking_items.append("hosted chat URL is not reachable from this machine")
    if not ready_flag:
        blocking_items.append(f"{cfg['ready_env']}=1 is not set for a pinned account/browser capture")
    if not session_note_present:
        blocking_items.append(f"{cfg['session_note_env']} is not set with account/session metadata")
    if output_inventory["answer_count"] != 30:
        blocking_items.append("30 captured answer files are not present in the expected output directory")
    return {
        "date": "2026-06-04",
        "baseline": baseline,
        "hosted_url": cfg["hosted_url"],
        "hosted_probe": hosted_probe,
        "runbook": cfg["runbook"],
        "prompt_template_count": prompt_count,
        "capture_manifest_template_count": manifest_count,
        "ready_env": cfg["ready_env"],
        "ready_env_present": ready_flag,
        "session_note_env": cfg["session_note_env"],
        "session_note_present": session_note_present,
        "output_inventory": output_inventory,
        "status": "ready" if not blocking_items else "not_ready",
        "blocking_items": blocking_items,
        "caveat": (
            "This gate only verifies readiness for a hosted replacement capture. "
            "It does not prove paper-exact reproduction without author-provided "
            "Table 1 raw outputs and original judge records."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['baseline']} Hosted Capture Gate",
        "",
        f"Date: {report['date']}",
        f"Status: `{report['status']}`",
        f"Hosted URL: {report['hosted_url']}",
        f"Prompt templates: {report['prompt_template_count']}",
        f"Capture manifests: {report['capture_manifest_template_count']}",
        f"Captured answers: {report['output_inventory']['answer_count']}",
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
    lines.extend(
        [
            "",
            "## Access State",
            "",
            f"- {report['ready_env']}: {report['ready_env_present']}",
            f"- {report['session_note_env']}: {report['session_note_present']}",
            f"- Output directory: `{report['output_inventory']['output_dir']}`",
            f"- Hosted probe available: {report['hosted_probe'].get('available')}",
            f"- Hosted probe status: {report['hosted_probe'].get('status', '')}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", choices=BASELINES.keys(), required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()
    report = build_report(args.baseline)
    slug = BASELINES[args.baseline]["slug"]
    output_json = args.output_json or (ROOT / f"{slug}_hosted_capture_gate.json")
    output_md = args.output_md or (ROOT / f"{slug}_hosted_capture_gate.md")
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "blocking_items": report["blocking_items"]}, indent=2))


if __name__ == "__main__":
    main()
