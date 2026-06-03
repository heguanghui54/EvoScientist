#!/usr/bin/env python3
"""Probe Hypogenic as an EvoScientist Table 1 baseline candidate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "hypogenic_baseline_probe.json"
DEFAULT_OUTPUT_MD = ROOT / "hypogenic_baseline_probe.md"
HYPOGENIC_HOME = "https://hypogenic.ai/"
HYPOGENIC_ARENA = "https://hypogenic.ai/arena"
HYPOGENIC_WEEKLY_BLOG = "https://hypogenic.ai/blog/weekly-entry-260309"
HYPOGENIC_CHAT = "https://hypogenic.ai/chat"
GITHUB_SEARCH = "https://api.github.com/search/repositories?q={query}&per_page=30"


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


def fetch_json_best_effort(url: str, timeout: int) -> dict[str, Any]:
    try:
        return json.loads(fetch_text(url, timeout))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"_fetch_error": f"{type(exc).__name__}: {exc}"}


def fetch_text_best_effort(url: str, timeout: int) -> tuple[str, str | None]:
    try:
        return fetch_text(url, timeout), None
    except (HTTPError, URLError, TimeoutError) as exc:
        return "", f"{type(exc).__name__}: {exc}"


def build_probe(timeout: int) -> dict[str, Any]:
    home = fetch_text(HYPOGENIC_HOME, timeout)
    arena = fetch_text(HYPOGENIC_ARENA, timeout)
    weekly_blog = fetch_text(HYPOGENIC_WEEKLY_BLOG, timeout)
    chat, chat_error = fetch_text_best_effort(HYPOGENIC_CHAT, timeout)
    search = fetch_json_best_effort(
        GITHUB_SEARCH.format(query=quote_plus("Hypogenic AI scientist")),
        timeout,
    )

    repo_hits = []
    for item in search.get("items", []) if isinstance(search.get("items"), list) else []:
        repo_hits.append(
            {
                "full_name": item.get("full_name", ""),
                "html_url": item.get("html_url", ""),
                "description": item.get("description", ""),
            }
        )
    hypogenic_repo_links = sorted(
        set(re.findall(r"https://github\.com/(Hypogenic-AI/[A-Za-z0-9_.-]+)", weekly_blog))
    )

    hosted_platform_available = "Hypogenic.ai" in home and "Shaping the Future of Science" in home
    assistant_link_available = 'href="/chat"' in home or "Assistant" in home
    ideahub_available = 'href="/ideahub"' in home or "IdeaHub" in home
    arena_available = "Weekly Agents4Science Idea Competition" in arena
    sign_in_required_signal = 'href="/auth/signin"' in home or 'href="/auth/signin"' in arena
    generated_repos_available = bool(hypogenic_repo_links)
    github_search_error = search.get("_fetch_error")
    public_runner_repo_found = any(
        "hypogenic" in hit["full_name"].lower()
        and "runner" in (hit["description"] or "").lower()
        for hit in repo_hits
    )
    raw_table1_outputs_found = any(
        needle in (home + arena + weekly_blog + chat).lower()
        for needle in ["evoscientist table 1", "2603.08127", "table1 outputs"]
    )
    chat_requires_access = bool(chat_error) or "Sign In" in chat or "/auth/signin" in chat

    return {
        "date": "2026-06-04",
        "baseline": "Hypogenic",
        "sources": {
            "home": HYPOGENIC_HOME,
            "chat": HYPOGENIC_CHAT,
            "arena": HYPOGENIC_ARENA,
            "weekly_blog": HYPOGENIC_WEEKLY_BLOG,
        },
        "files_checked": [
            HYPOGENIC_HOME,
            HYPOGENIC_ARENA,
            HYPOGENIC_WEEKLY_BLOG,
            HYPOGENIC_CHAT,
            "GitHub repository search for Hypogenic AI scientist",
        ],
        "github_search_error": github_search_error,
        "github_repo_hits": repo_hits,
        "hypogenic_generated_repo_examples": hypogenic_repo_links[:12],
        "direct_30_query_runner_available": False,
        "evo_table1_drop_in_status": "hosted_competition_adapter_candidate",
        "paper_exact_status": "not_paper_exact",
        "signals": {
            "hosted_platform_available": hosted_platform_available,
            "assistant_link_available": assistant_link_available,
            "ideahub_available": ideahub_available,
            "arena_available": arena_available,
            "sign_in_required_signal": sign_in_required_signal,
            "chat_requires_access_or_redirects": chat_requires_access,
            "generated_repos_available": generated_repos_available,
            "public_runner_repo_found": public_runner_repo_found,
            "raw_table1_outputs_found": raw_table1_outputs_found,
        },
        "entrypoints": {
            "hosted_home": HYPOGENIC_HOME,
            "hosted_chat": HYPOGENIC_CHAT,
            "competition_arena": HYPOGENIC_ARENA,
            "generated_repo_examples": hypogenic_repo_links[:3],
        },
        "required_env_or_access": [
            "Hypogenic account/session if running the hosted Assistant",
            "Pinned UI/browser capture protocol for one fresh session per recovered query",
            "Separate interpretation if using generated competition repositories, because they are public examples rather than the paper's Table 1 baseline outputs",
        ],
        "reproduction_implication": (
            "Hypogenic has a public hosted science platform with Assistant, IdeaHub, Arena, "
            "and public competition-generated repositories. The checked public materials do not "
            "provide a standalone batch runner or the raw 30-query EvoScientist Table 1 outputs. "
            "It can only be treated as a hosted replacement rerun candidate with account/session "
            "capture, not as paper-exact public evidence."
        ),
        "next_actions": [
            "If Hypogenic access is available, define a pinned hosted-run protocol with account state and one fresh Assistant session per recovered query.",
            "Capture final answers for all 30 queries into reproduction/artifacts/idea_outputs/Hypogenic/query_XX/answer.txt.",
            "If access is not available, keep Hypogenic as non-reproducible from public artifacts alone and report only generated competition repositories as related examples.",
            "Judge any imported Hypogenic outputs through the existing swapped pairwise judge pipeline.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Hypogenic Baseline Probe",
        "",
        f"Date: {report['date']}",
        f"Hosted home: {report['sources']['home']}",
        f"Hosted chat: {report['sources']['chat']}",
        f"Arena: {report['sources']['arena']}",
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
    if report["github_search_error"]:
        lines.extend(["", "## GitHub Search Note", "", report["github_search_error"], ""])
    lines.extend(["", "## Generated Repo Examples", ""])
    for item in report["hypogenic_generated_repo_examples"]:
        lines.append(f"- `https://github.com/{item}`")
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
        "hosted_platform_available": report["signals"]["hosted_platform_available"],
    }, indent=2))


if __name__ == "__main__":
    main()
