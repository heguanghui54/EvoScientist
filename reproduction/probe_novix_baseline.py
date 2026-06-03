#!/usr/bin/env python3
"""Probe Novix as an EvoScientist Table 1 baseline candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "novix_baseline_probe.json"
DEFAULT_OUTPUT_MD = ROOT / "novix_baseline_probe.md"
NOVIX_HOME = "https://novix.science/"
NOVIX_CHAT = "https://novix.science/chat"
NOVIX_JS = "https://novix.science/static/js/index-B5bYYKuJ.js"
AI_RESEARCHER_README = "https://raw.githubusercontent.com/HKUDS/AI-Researcher/main/README.md"
GITHUB_SEARCH = "https://api.github.com/search/repositories?q={query}&per_page=20"


def fetch_text(url: str, timeout: int) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str, timeout: int) -> Any:
    return json.loads(fetch_text(url, timeout))


def build_probe(timeout: int) -> dict[str, Any]:
    home = fetch_text(NOVIX_HOME, timeout)
    chat = fetch_text(NOVIX_CHAT, timeout)
    bundle = fetch_text(NOVIX_JS, timeout)
    ai_researcher_readme = fetch_text(AI_RESEARCHER_README, timeout)
    search = fetch_json(
        GITHUB_SEARCH.format(query=quote_plus("Novix science AI-Researcher")),
        timeout,
    )

    repo_hits = [
        {
            "full_name": item.get("full_name", ""),
            "html_url": item.get("html_url", ""),
            "description": item.get("description", ""),
        }
        for item in search.get("items", [])
    ]
    independent_novix_repos = [
        item for item in repo_hits if item["full_name"] != "HKUDS/AI-Researcher"
    ]
    visible_product_endpoints = [
        endpoint
        for endpoint in [
            "/user/login",
            "/chat_session/create",
            "/task/create_task",
            "/task/submit_user_question",
            "/call_agent",
            "/agents",
        ]
        if endpoint in bundle
    ]

    same_as_ai_researcher = "https://github.com/HKUDS/AI-Researcher" in home
    hosted_chat_available = "AI Research Chat" in chat and "Novix" in chat
    product_features_available = all(
        phrase in home
        for phrase in ["Novel Idea Generation", "Deep Survey", "Model Implementation"]
    )
    ai_researcher_links_novix = "https://novix.science/chat" in ai_researcher_readme
    login_required_signals = "/user/login" in bundle and "/user/getUserInfo" in bundle
    has_task_api_in_bundle = "/task/submit_user_question" in bundle and "/task/create_task" in bundle
    public_api_docs_found = any(
        phrase in (home + chat).lower()
        for phrase in ["api documentation", "developer api", "public batch api"]
    )
    raw_table1_outputs_found = any(
        needle in (home + chat + ai_researcher_readme).lower()
        for needle in ["evoscientist table 1", "2603.08127", "table1 outputs"]
    )

    return {
        "date": "2026-06-04",
        "baseline": "Novix",
        "sources": {
            "hosted_chat": NOVIX_CHAT,
            "home": NOVIX_HOME,
            "frontend_bundle": NOVIX_JS,
            "ai_researcher_repository": "https://github.com/HKUDS/AI-Researcher",
            "ai_researcher_readme": AI_RESEARCHER_README,
        },
        "files_checked": [
            NOVIX_HOME,
            NOVIX_CHAT,
            NOVIX_JS,
            AI_RESEARCHER_README,
            "GitHub repository search for Novix science AI-Researcher",
        ],
        "github_repo_hits": repo_hits,
        "direct_30_query_runner_available": False,
        "evo_table1_drop_in_status": "hosted_ui_adapter_candidate",
        "paper_exact_status": "not_paper_exact",
        "signals": {
            "hosted_chat_available": hosted_chat_available,
            "product_features_available": product_features_available,
            "same_as_ai_researcher": same_as_ai_researcher,
            "ai_researcher_readme_links_novix": ai_researcher_links_novix,
            "independent_public_novix_repo_found": bool(independent_novix_repos),
            "login_required_signals": login_required_signals,
            "visible_task_api_in_frontend_bundle": has_task_api_in_bundle,
            "public_batch_api_docs_found": public_api_docs_found,
            "raw_table1_outputs_found": raw_table1_outputs_found,
        },
        "visible_product_endpoints": visible_product_endpoints,
        "entrypoints": {
            "hosted_chat": NOVIX_CHAT,
            "linked_open_source_system": "https://github.com/HKUDS/AI-Researcher",
        },
        "required_env_or_access": [
            "Novix account/session if running the hosted product",
            "Pinned UI/API capture protocol if using browser or frontend endpoints",
            "Alternative: use the open AI-Researcher probe/runbook rather than treating Novix as a separate open-source runner",
        ],
        "reproduction_implication": (
            "Novix is a hosted AI co-scientist product and public materials link its open-source "
            "lineage to HKUDS/AI-Researcher. The visible frontend bundle contains login, chat "
            "session, and task endpoints, but no public batch API documentation or raw EvoScientist "
            "Table 1 outputs were found. Novix can only be a replacement rerun candidate through "
            "a pinned account/browser/API-capture protocol; it is not a paper-exact public artifact."
        ),
        "next_actions": [
            "If Novix access is available, define a pinned hosted-run protocol with account state, model defaults, and one fresh session per recovered query.",
            "Capture final assistant answers for all 30 queries into reproduction/artifacts/idea_outputs/Novix/query_XX/answer.txt.",
            "If hosted access is not available, use AI-Researcher public-runner evidence instead and report Novix as non-reproducible from public artifacts alone.",
            "Judge any imported Novix outputs through the existing swapped pairwise judge pipeline.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Novix Baseline Probe",
        "",
        f"Date: {report['date']}",
        f"Hosted chat: {report['sources']['hosted_chat']}",
        f"Linked open-source system: {report['entrypoints']['linked_open_source_system']}",
        "",
        f"Drop-in status: `{report['evo_table1_drop_in_status']}`",
        f"Paper-exact status: `{report['paper_exact_status']}`",
        "",
        "## Finding",
        "",
        report["reproduction_implication"],
        "",
        "## Signals",
        "",
    ]
    for key, value in report["signals"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Visible Product Endpoints", ""])
    for endpoint in report["visible_product_endpoints"]:
        lines.append(f"- `{endpoint}`")
    lines.extend(["", "## Required Access", ""])
    for item in report["required_env_or_access"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Actions", ""])
    for item in report["next_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    report = build_probe(args.timeout)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({
        "baseline": report["baseline"],
        "status": report["evo_table1_drop_in_status"],
        "hosted_chat_available": report["signals"]["hosted_chat_available"],
    }, indent=2))


if __name__ == "__main__":
    main()
