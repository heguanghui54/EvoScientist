#!/usr/bin/env python3
"""Probe K-Dense as an EvoScientist Table 1 baseline candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "k_dense_baseline_probe.json"
DEFAULT_OUTPUT_MD = ROOT / "k_dense_baseline_probe.md"
ORG_REPOS_API = "https://api.github.com/orgs/K-Dense-AI/repos?per_page=100"
BYOK_TREE_API = "https://api.github.com/repos/K-Dense-AI/k-dense-byok/git/trees/main?recursive=1"
BYOK_REF_API = "https://api.github.com/repos/K-Dense-AI/k-dense-byok/git/ref/heads/main"
RAW_BYOK = "https://raw.githubusercontent.com/K-Dense-AI/k-dense-byok/main"
LLMS_TXT = "https://k-dense.ai/llms.txt"


def fetch_text(url: str, timeout: int) -> str:
    with urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str, timeout: int) -> Any:
    return json.loads(fetch_text(url, timeout))


def build_probe(timeout: int) -> dict[str, Any]:
    repos = fetch_json(ORG_REPOS_API, timeout)
    repo_names = [repo["name"] for repo in repos]
    byok_head = fetch_json(BYOK_REF_API, timeout)
    byok_tree = fetch_json(BYOK_TREE_API, timeout)
    byok_paths = {item["path"] for item in byok_tree.get("tree", [])}
    byok_readme = fetch_text(f"{RAW_BYOK}/README.md", timeout)
    byok_agents = fetch_text(f"{RAW_BYOK}/AGENTS.md", timeout)
    use_agent = fetch_text(f"{RAW_BYOK}/web/src/lib/use-agent.ts", timeout)
    server = fetch_text(f"{RAW_BYOK}/server.py", timeout)
    pyproject = fetch_text(f"{RAW_BYOK}/pyproject.toml", timeout)
    llms = fetch_text(LLMS_TXT, timeout)

    hosted_platform = "https://app.k-dense.ai" in llms and "K-Dense Web" in llms
    byok_repo_available = "k-dense-byok" in repo_names
    local_web_app = "./start.sh" in byok_readme and "http://localhost:3000" in byok_readme
    adk_sse_available = all(
        needle in use_agent
        for needle in ["/run_sse", "/apps/${APP_NAME}/users/${USER_ID}/sessions", "newMessage"]
    )
    project_scoped_api = "X-Project-Id" in server and "ProjectSessionService" in server
    requires_python_313 = 'requires-python = ">=3.13"' in pyproject
    openrouter_required = "OpenRouter API key" in byok_readme
    expert_uses_gemini_cli = "Gemini CLI" in byok_agents or "Gemini CLI" in byok_readme
    no_documented_batch_cli = "[project.scripts]" in pyproject and "kady =" not in pyproject
    no_raw_table1_outputs = not any(
        "evoscientist" in path.lower() or "table1" in path.lower()
        for path in byok_paths
    )

    return {
        "date": "2026-06-04",
        "baseline": "K-Dense",
        "sources": {
            "organization": "https://github.com/K-Dense-AI",
            "hosted_platform": "https://k-dense.ai/",
            "byok_repository": "https://github.com/K-Dense-AI/k-dense-byok",
            "llms_txt": LLMS_TXT,
        },
        "checked_head": byok_head.get("object", {}).get("sha", ""),
        "organization_repositories": repo_names,
        "files_checked": [
            "https://k-dense.ai/llms.txt",
            "k-dense-byok/README.md",
            "k-dense-byok/AGENTS.md",
            "k-dense-byok/web/src/lib/use-agent.ts",
            "k-dense-byok/server.py",
            "k-dense-byok/pyproject.toml",
            "k-dense-byok repository file tree",
        ],
        "direct_30_query_runner_available": adk_sse_available,
        "evo_table1_drop_in_status": "local_web_api_adapter_candidate",
        "paper_exact_status": "not_paper_exact",
        "signals": {
            "hosted_platform_available": hosted_platform,
            "byok_repo_available": byok_repo_available,
            "local_web_app_available": local_web_app,
            "adk_run_sse_endpoint_available": adk_sse_available,
            "project_scoped_api": project_scoped_api,
            "requires_python_3_13": requires_python_313,
            "openrouter_key_required": openrouter_required,
            "expert_path_uses_gemini_cli": expert_uses_gemini_cli,
            "no_documented_batch_cli": no_documented_batch_cli,
            "raw_table1_outputs_found": not no_raw_table1_outputs,
        },
        "entrypoints": {
            "hosted": "https://app.k-dense.ai",
            "local_app": "git clone https://github.com/K-Dense-AI/k-dense-byok && cd k-dense-byok && ./start.sh",
            "local_http_adapter": (
                "POST /apps/kady_agent/users/user/sessions, then POST /run_sse "
                "with appName=kady_agent, userId=user, sessionId, and newMessage.parts[0].text"
            ),
        },
        "required_env": [
            "OPENROUTER_API_KEY",
            "optional Exa or Parallel search key",
            "optional Paperclip key",
            "Gemini CLI path configured by the K-Dense BYOK startup flow",
        ],
        "reproduction_implication": (
            "K-Dense has a hosted platform and a public BYOK local app. The BYOK app exposes "
            "an ADK `/run_sse` chat endpoint that can be adapted to submit each recovered "
            "EvoScientist query, but it is not a paper-exact artifact and the repository does "
            "not provide the paper's raw K-Dense Table 1 outputs. A reproducible rerun needs a "
            "pinned local project, model selection, keys, and an HTTP/SSE output-capture adapter."
        ),
        "next_actions": [
            "Start k-dense-byok with a pinned commit, Python 3.13, and OpenRouter/Gemini CLI configuration.",
            "Create one fresh session per recovered EvoScientist query through the ADK session endpoint.",
            "Submit each query through `/run_sse` and capture the final assistant text plus turn manifest.",
            "Import captured answers with import_baseline_outputs.py under system name K-Dense.",
            "Judge imported outputs through the existing swapped pairwise judge pipeline.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# K-Dense Baseline Probe",
        "",
        f"Date: {report['date']}",
        f"Organization: {report['sources']['organization']}",
        f"Hosted platform: {report['sources']['hosted_platform']}",
        f"BYOK repository: {report['sources']['byok_repository']}",
        f"Checked BYOK HEAD: `{report['checked_head']}`",
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
    lines.extend(["", "## Entrypoints", ""])
    for key, value in report["entrypoints"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Required Environment", ""])
    for item in report["required_env"]:
        lines.append(f"- `{item}`")
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
        "checked_head": report["checked_head"],
    }, indent=2))


if __name__ == "__main__":
    main()
