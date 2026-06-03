#!/usr/bin/env python3
"""Probe Virtual Scientist / VirSci as an EvoScientist Table 1 baseline candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = ROOT / "virtual_scientist_baseline_probe.json"
DEFAULT_OUTPUT_MD = ROOT / "virtual_scientist_baseline_probe.md"
REPO = "https://github.com/open-sciencelab/Virtual-Scientists"
RAW = "https://raw.githubusercontent.com/open-sciencelab/Virtual-Scientists/main"
WEBSITE = "https://renqichen.github.io/Virtual-Scientists/"
ARXIV = "https://arxiv.org/abs/2410.09403"


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


def build_probe(timeout: int) -> dict[str, Any]:
    readme = fetch_text(f"{RAW}/README.md", timeout)
    run_py = fetch_text(f"{RAW}/sci_platform/run.py", timeout)
    platform_py = fetch_text(f"{RAW}/sci_platform/sci_platform.py", timeout)
    requirements = fetch_text(f"{RAW}/requirements.txt", timeout)
    tree = fetch_json_best_effort(
        "https://api.github.com/repos/open-sciencelab/Virtual-Scientists/git/trees/main?recursive=1",
        timeout,
    )
    paths = {item.get("path", "") for item in tree.get("tree", [])} if isinstance(tree.get("tree"), list) else set()

    repo_available = "Many Heads Are Better Than One" in readme and "VirSci" in readme
    arxiv_linked = "2410.09403" in readme
    run_py_available = "sci_platform/run.py" in paths or "class Platform" not in run_py
    data_required = all(
        needle in readme
        for needle in ["AMiner Computer Science Dataset", "Google Drive", "Papers/papers.tar.gz"]
    )
    ollama_required = all(
        needle in readme
        for needle in ["ollama", "llama3.1", "mxbai-embed-large"]
    )
    faiss_required = "faiss" in requirements.lower() and "faiss.read_index" in platform_py
    hardcoded_paths = "/home/bingxing2/" in platform_py
    query_cli_available = "--query" in run_py or "--prompt" in run_py or "--topic" in run_py
    output_dialogue_available = "{info_dir}/{current_time}_{self.team_name}_dialogue.json" in readme
    raw_table1_outputs_found = any(
        needle in (readme + run_py + platform_py).lower()
        for needle in ["evoscientist table 1", "2603.08127", "table1 outputs"]
    )

    return {
        "date": "2026-06-04",
        "baseline": "Virtual Scientist",
        "sources": {
            "repository": REPO,
            "website": WEBSITE,
            "arxiv": ARXIV,
            "readme": f"{RAW}/README.md",
            "run_py": f"{RAW}/sci_platform/run.py",
            "platform_py": f"{RAW}/sci_platform/sci_platform.py",
        },
        "files_checked": [
            "README.md",
            "sci_platform/run.py",
            "sci_platform/sci_platform.py",
            "requirements.txt",
            "repository file tree",
        ],
        "github_tree_error": tree.get("_fetch_error"),
        "direct_30_query_runner_available": False,
        "evo_table1_drop_in_status": "open_source_platform_not_drop_in",
        "paper_exact_status": "not_paper_exact",
        "signals": {
            "repo_available": repo_available,
            "arxiv_2410_09403_linked": arxiv_linked,
            "run_py_available": run_py_available,
            "data_required": data_required,
            "ollama_models_required": ollama_required,
            "faiss_required": faiss_required,
            "hardcoded_data_paths_present": hardcoded_paths,
            "query_cli_available": query_cli_available,
            "dialogue_json_output_available": output_dialogue_available,
            "raw_table1_outputs_found": raw_table1_outputs_found,
        },
        "entrypoints": {
            "setup": "pip install -r requirements.txt; cd agentscope-main && pip install -e .",
            "data": "Download AMiner-derived Papers, Embeddings, Authors, and adjacency.txt from the repository's Google Drive link and patch sci_platform/sci_platform.py paths.",
            "models": "ollama serve; ollama pull llama3.1; ollama pull llama3.1:70b; ollama pull mxbai-embed-large",
            "run": "cd sci_platform && python run.py --runs ... --team_limit ... --max_discuss_iteration ... --max_team_member ... --epochs ...",
        },
        "required_env_or_access": [
            "AMiner-derived paper/author/embedding data package",
            "FAISS index files and preferably GPU FAISS",
            "Ollama llama3.1 8B/70B and mxbai-embed-large",
            "Adapter design if mapping the 30 recovered EvoScientist natural-language queries into VirSci's team/ecosystem simulation",
        ],
        "reproduction_implication": (
            "Virtual Scientist maps to the public VirSci/Virtual-Scientists repository. "
            "It is a runnable open-source scientific-collaboration platform, but it is not a "
            "drop-in runner for EvoScientist's 30 recovered natural-language Table 1 queries: "
            "the public entrypoint is a team-simulation run script that depends on AMiner-derived "
            "paper/author/embedding data, FAISS, Ollama models, and patched local paths. The "
            "repository does not provide the paper's raw Virtual Scientist Table 1 outputs."
        ),
        "next_actions": [
            "For a replacement rerun, first decide a principled adapter from each recovered query to a VirSci simulation seed/topic.",
            "Install the AMiner-derived data package and patch all local paths in sci_platform/sci_platform.py.",
            "Run VirSci under a pinned team/epoch/model protocol and extract generated idea/abstract fields from dialogue JSON outputs.",
            "Import extracted answers with import_baseline_outputs.py under system name Virtual Scientist.",
            "Do not treat this as paper-exact unless the original 30-query raw outputs are obtained from the EvoScientist authors.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Virtual Scientist Baseline Probe",
        "",
        f"Date: {report['date']}",
        f"Repository: {report['sources']['repository']}",
        f"Website: {report['sources']['website']}",
        f"arXiv: {report['sources']['arxiv']}",
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
    if report["github_tree_error"]:
        lines.extend(["", "## GitHub Tree Note", "", report["github_tree_error"], ""])
    lines.extend(["", "## Entrypoints", ""])
    for key, value in report["entrypoints"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Required Environment", ""])
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
        "repo_available": report["signals"]["repo_available"],
    }, indent=2))


if __name__ == "__main__":
    main()
