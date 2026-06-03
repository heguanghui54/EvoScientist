#!/usr/bin/env python3
"""Run EvoScientist idea generation over the paper's 30 research queries."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "reproduction"
DEFAULT_OUTPUT = REPRO / "artifacts" / "idea_outputs" / "EvoScientist"

PROVIDER_KEY_FIELDS = {
    "anthropic": "anthropic_api_key",
    "openai": "openai_api_key",
    "nvidia": "nvidia_api_key",
    "google": "google_api_key",
    "google-genai": "google_api_key",
    "minimax": "minimax_api_key",
    "openrouter": "openrouter_api_key",
    "deepseek": "deepseek_api_key",
    "zhipu": "zhipu_api_key",
    "volcengine": "volcengine_api_key",
    "dashscope": "dashscope_api_key",
    "moonshot": "moonshot_api_key",
    "kimi": "kimi_api_key",
    "custom-openai": "custom_openai_api_key",
    "custom-anthropic": "custom_anthropic_api_key",
}
DEFAULT_COLLECT_FILES = ["final_report.md", "research_request.md"]


def load_queries() -> list[dict]:
    data = json.loads((REPRO / "queries.json").read_text(encoding="utf-8"))
    return data["queries"]


def ensure_provider_configured() -> None:
    sys.path.insert(0, str(ROOT))
    from EvoScientist.config.settings import load_config

    cfg = load_config()
    provider = cfg.provider
    if provider == "ollama":
        if cfg.ollama_base_url or os.environ.get("OLLAMA_BASE_URL"):
            return
        raise SystemExit(
            "Provider is ollama but OLLAMA_BASE_URL is not configured. "
            "Start Ollama and set EvoSci config set ollama_base_url http://127.0.0.1:11434."
        )

    field = PROVIDER_KEY_FIELDS.get(provider)
    if not field:
        raise SystemExit(f"Provider {provider!r} is not recognized by this runner.")

    value = getattr(cfg, field, "") or os.environ.get(field.upper())
    if not value:
        raise SystemExit(
            f"Provider {provider!r} is configured but {field} is missing. "
            "Run `.venv/bin/EvoSci onboard` or set the provider key before running."
        )


def collect_workspace_files(
    qdir: Path, filenames: list[str], workspace_dir: Path
) -> list[dict[str, str | int]]:
    collected = []
    for filename in filenames:
        source = workspace_dir / filename
        if not source.is_file():
            continue
        destination = qdir / filename
        destination.write_bytes(source.read_bytes())
        collected.append(
            {
                "source": str(source),
                "artifact": str(destination),
                "bytes": destination.stat().st_size,
            }
        )
    return collected


def clear_workspace_files(filenames: list[str], workspace_dir: Path) -> None:
    for filename in filenames:
        path = workspace_dir / filename
        if path.is_file():
            path.unlink()


def clear_artifact_files(qdir: Path, filenames: list[str]) -> None:
    for filename in filenames:
        path = qdir / filename
        if path.is_file():
            path.unlink()


def run_workspace_dir(query_id: int, session_mode: str, run_name_prefix: str) -> Path:
    if session_mode == "run":
        return ROOT / "runs" / f"{run_name_prefix}-{query_id:02d}"
    return ROOT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N queries.")
    parser.add_argument("--query-id", type=int, default=None, help="Run one query id.")
    parser.add_argument(
        "--query-ids",
        default=None,
        help="Comma-separated query ids to run, for example '4,7,12'.",
    )
    parser.add_argument("--start-id", type=int, default=None, help="Run queries with id >= N.")
    parser.add_argument("--end-id", type=int, default=None, help="Run queries with id <= N.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds per query.")
    parser.add_argument(
        "--idle-timeout",
        type=int,
        default=0,
        help=(
            "When streaming logs, terminate a query after N seconds without "
            "stdout/stderr growth. Disabled by default."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Write prompts without calling EvoSci.")
    parser.add_argument(
        "--proposal-only",
        action="store_true",
        help="Ask EvoScientist for a direct proposal without tool or shell execution.",
    )
    parser.add_argument(
        "--force-proposal",
        action="store_true",
        help=(
            "For broad paper queries, force a complete proposal without asking "
            "the user for clarification. Tools and agent workflow remain enabled."
        ),
    )
    parser.add_argument(
        "--stream-logs",
        action="store_true",
        help="Stream EvoSci stdout/stderr to files while the run is active.",
    )
    parser.add_argument(
        "--collect-file",
        action="append",
        default=None,
        help=(
            "Workspace-relative file to copy into each query artifact directory "
            "after EvoSci exits. Defaults to final_report.md and research_request.md."
        ),
    )
    parser.add_argument(
        "--session-mode",
        choices=["run", "daemon"],
        default="run",
        help=(
            "EvoSci workspace mode. The default 'run' isolates each query from "
            "persistent daemon state, which is preferred for reproducible batches."
        ),
    )
    parser.add_argument(
        "--run-name-prefix",
        default="repro-query",
        help="Name prefix used for isolated EvoSci --mode run sessions.",
    )
    args = parser.parse_args()
    collect_files = args.collect_file if args.collect_file is not None else DEFAULT_COLLECT_FILES

    queries = load_queries()
    selectors = sum(
        1
        for selected in [
            args.query_id is not None,
            args.query_ids is not None,
            args.start_id is not None or args.end_id is not None,
        ]
        if selected
    )
    if selectors > 1:
        raise SystemExit("Use only one of --query-id, --query-ids, or --start-id/--end-id.")
    if args.query_id is not None:
        wanted = {args.query_id}
        queries = [q for q in queries if q["id"] in wanted]
    elif args.query_ids is not None:
        try:
            wanted = {int(part.strip()) for part in args.query_ids.split(",") if part.strip()}
        except ValueError as exc:
            raise SystemExit("--query-ids must be a comma-separated list of integers.") from exc
        queries = [q for q in queries if q["id"] in wanted]
    elif args.start_id is not None or args.end_id is not None:
        start_id = args.start_id if args.start_id is not None else 1
        end_id = args.end_id if args.end_id is not None else 10**9
        if start_id > end_id:
            raise SystemExit("--start-id cannot be greater than --end-id.")
        queries = [q for q in queries if start_id <= q["id"] <= end_id]
    if selectors and not queries:
        raise SystemExit("No queries matched the requested selector.")
    if args.limit is not None:
        queries = queries[: args.limit]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not args.dry_run:
        ensure_provider_configured()

    evosci = ROOT / ".venv" / "bin" / "EvoSci"
    if not evosci.exists() and not args.dry_run:
        raise SystemExit("Missing .venv/bin/EvoSci. Run `bash reproduction/run_preflight.sh` first.")

    manifest = {
        "runner": "run_idea_generation.py",
        "dry_run": args.dry_run,
        "query_count": len(queries),
        "outputs": [],
    }

    for query in queries:
        qdir = args.output_dir / f"query_{query['id']:02d}"
        qdir.mkdir(parents=True, exist_ok=True)
        prompt = query["goal"]
        if args.proposal_only:
            prompt = (
                "Produce one concrete research proposal for the following paper "
                "reproduction query. Do not execute tools, shell commands, web "
                "searches, or code. Return a final answer with: title, problem, "
                "hypothesis, method, dataset/benchmark, evaluation metrics, "
                "baselines, ablations, and expected failure modes.\n\n"
                f"Query: {prompt}"
            )
        elif args.force_proposal:
            prompt = (
                "Generate one complete, concrete research proposal for the "
                "following paper reproduction query. If the query is broad, pick "
                "one specific high-impact subproblem yourself and state that "
                "choice. Do not ask the user clarification questions. Do not end "
                "with a request for more constraints. You may use your normal "
                "tools and agent workflow. Before finishing, write the complete "
                "proposal to /final_report.md. The final answer and the report "
                "must include: title, problem, hypothesis, method, "
                "dataset/benchmark, evaluation metrics, baselines, ablations, "
                "expected failure modes, and a short execution plan.\n\n"
                f"Query: {prompt}"
            )
        (qdir / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
        (qdir / "query.json").write_text(json.dumps(query, indent=2), encoding="utf-8")
        workspace_dir = run_workspace_dir(query["id"], args.session_mode, args.run_name_prefix)
        if args.session_mode == "run" and workspace_dir.is_dir():
            shutil.rmtree(workspace_dir)
        clear_workspace_files(collect_files, ROOT)
        if workspace_dir != ROOT:
            clear_workspace_files(collect_files, workspace_dir)
        clear_artifact_files(qdir, collect_files)

        entry = {"id": query["id"], "topic": query["topic"], "dir": str(qdir)}
        if args.dry_run:
            entry["status"] = "dry_run"
            manifest["outputs"].append(entry)
            continue

        cmd = [str(evosci)]
        if args.session_mode == "run":
            cmd.extend(
                [
                    "--mode",
                    "run",
                    "--name",
                    f"{args.run_name_prefix}-{query['id']:02d}",
                ]
            )
        else:
            cmd.extend(
                [
                    "--workdir",
                    str(ROOT),
                ]
            )
        cmd.extend(
            [
                "-p",
                prompt,
                "--ui",
                "cli",
                "--auto-mode",
                "--no-thinking",
            ]
        )
        stdout_path = qdir / "stdout.txt"
        stderr_path = qdir / "stderr.txt"
        if args.stream_logs:
            with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open(
                "w", encoding="utf-8"
            ) as stderr_file:
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(ROOT),
                    text=True,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    stdin=subprocess.DEVNULL,
                )
                start_time = time.monotonic()
                last_activity = start_time
                last_stdout_size = 0
                last_stderr_size = 0
                returncode = None
                while returncode is None:
                    returncode = proc.poll()
                    stdout_file.flush()
                    stderr_file.flush()
                    stdout_size = stdout_path.stat().st_size if stdout_path.exists() else 0
                    stderr_size = stderr_path.stat().st_size if stderr_path.exists() else 0
                    if stdout_size != last_stdout_size or stderr_size != last_stderr_size:
                        last_activity = time.monotonic()
                        last_stdout_size = stdout_size
                        last_stderr_size = stderr_size
                    now = time.monotonic()
                    timed_out = now - start_time > args.timeout
                    idle_timed_out = args.idle_timeout > 0 and now - last_activity > args.idle_timeout
                    if timed_out or idle_timed_out:
                        proc.terminate()
                        try:
                            proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=10)
                        returncode = 124 if timed_out else 125
                        if timed_out:
                            stderr_file.write(f"\nTimed out after {args.timeout} seconds.\n")
                        else:
                            stderr_file.write(
                                f"\nIdle timed out after {args.idle_timeout} seconds without log growth.\n"
                            )
                        stderr_file.flush()
                        break
                    if returncode is None:
                        time.sleep(5)
        else:
            result = subprocess.run(
                cmd,
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                timeout=args.timeout,
                check=False,
            )
            stdout_path.write_text(result.stdout, encoding="utf-8")
            stderr_path.write_text(result.stderr, encoding="utf-8")
            returncode = result.returncode
        entry["returncode"] = returncode
        entry["status"] = "ok" if returncode == 0 else "failed"
        entry["workspace_dir"] = str(workspace_dir)
        entry["collected_files"] = collect_workspace_files(qdir, collect_files, workspace_dir)
        manifest["outputs"].append(entry)

    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps({"status": "ok", "output_dir": str(args.output_dir)}, indent=2))


if __name__ == "__main__":
    main()
