#!/usr/bin/env python3
"""Build a reproducibility bundle with checksums and a zip archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
DEFAULT_BUNDLE_ROOT = ROOT / "artifacts" / "reproducibility_bundle"
DEFAULT_ARCHIVE = ROOT / "artifacts" / "reproducibility_bundle.zip"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_revision() -> dict[str, str]:
    return {
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=REPO_ROOT, text=True).strip(),
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_lines(path: Path) -> int:
    if path.suffix not in {".jsonl", ".csv", ".md"}:
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def required_paths() -> list[Path]:
    rels = [
        "final_reproduction_dossier.md",
        "final_reproduction_dossier.json",
        "artifacts/audit/paper_level_completion_latest.md",
        "artifacts/audit/paper_level_completion_latest.json",
        "artifacts/audit/paper_artifact_schema_latest.json",
        "table1_replacement_all_baselines_monica_report.md",
        "table1_replacement_all_baselines_monica_report.json",
        "artifacts/judge_inputs/results.jsonl",
        "artifacts/judge_outputs/results.jsonl",
        "artifacts/tables/idea_generation_win_tie_lose.csv",
        "artifacts/tables/idea_generation_win_tie_lose.json",
        "table2_surrogate_monica_report.md",
        "table2_surrogate_monica_report.json",
        "artifacts/human_evaluation/inputs.jsonl",
        "artifacts/human_evaluation/surrogate_labels.jsonl",
        "artifacts/human_evaluation/surrogate_aggregate.csv",
        "artifacts/human_evaluation/surrogate_aggregate.json",
        "artifacts/human_evaluation/label_packet/annotation_guide.md",
        "artifacts/human_evaluation/label_packet/manifest.json",
        "artifacts/human_evaluation/label_packet/review_tasks.jsonl",
        "artifacts/human_evaluation/label_packet/task_index.csv",
        "artifacts/human_evaluation/label_packet/label_sheet_template.csv",
        "ablation_queries01_30_monica_gemini_report.md",
        "ablation_queries01_30_monica_gemini_report.json",
        "artifacts/ablations/combined_aggregate.csv",
        "artifacts/ablations/combined_aggregate.json",
        "figure2_code_execution_replacement_report.md",
        "figure2_code_execution_replacement_report.json",
        "artifacts/code_execution/summary.csv",
        "artifacts/code_execution/summary.json",
        "artifacts/paper_previews/evoscientist_query01_final_report.pdf",
        "artifacts/paper_previews/ai_scientist_v2_query01_idea.pdf",
        "artifacts/paper_previews/rendered/evoscientist_query01_final_report_page1.png",
        "artifacts/paper_previews/rendered/ai_scientist_v2_query01_idea_page1.png",
        "paper_reproduction_action_plan.md",
        "paper_reproduction_action_plan.json",
    ]
    return [ROOT / item for item in rels]


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "nonblank_lines": count_lines(path),
    }


def build_manifest(date: str) -> dict[str, Any]:
    dossier = load_json(ROOT / "final_reproduction_dossier.json")
    paths = required_paths()
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(json.dumps({"missing_files": missing}, indent=2))
    files = [file_record(path) for path in paths]
    by_path = {item["path"]: item for item in files}
    return {
        "date": date,
        "status": dossier["overall_status"],
        "paper_exact": False,
        "repository": git_revision(),
        "bundle_scope": "portable verification bundle for the current EvoScientist replacement/proxy reproduction state",
        "component_summary": {
            "full_trajectories": "30/30 complete",
            "table1": "420/420 replacement/proxy judge records",
            "table2": "120 inputs, 1440 LLM-surrogate labels, human label packet ready, formal human labels missing",
            "table3": "30-query replacement ablation rerun",
            "figure2": "240-record replacement code-execution probe",
        },
        "blocking_items": dossier["blocking_items"],
        "files": files,
        "line_count_checks": {
            "artifacts/judge_inputs/results.jsonl": by_path["artifacts/judge_inputs/results.jsonl"]["nonblank_lines"],
            "artifacts/judge_outputs/results.jsonl": by_path["artifacts/judge_outputs/results.jsonl"]["nonblank_lines"],
            "artifacts/human_evaluation/inputs.jsonl": by_path["artifacts/human_evaluation/inputs.jsonl"]["nonblank_lines"],
            "artifacts/human_evaluation/surrogate_labels.jsonl": by_path["artifacts/human_evaluation/surrogate_labels.jsonl"]["nonblank_lines"],
            "artifacts/human_evaluation/label_packet/label_sheet_template.csv": by_path[
                "artifacts/human_evaluation/label_packet/label_sheet_template.csv"
            ]["nonblank_lines"],
        },
        "verification_commands": [
            ".venv/bin/python reproduction/verify_reproduction_assets.py",
            "bash reproduction/run_preflight.sh",
            ".venv/bin/python reproduction/audit_paper_level_completion.py --strict",
        ],
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# EvoScientist Reproducibility Bundle",
        "",
        f"Date: {manifest['date']}",
        f"Status: `{manifest['status']}`",
        f"Paper-exact: `{str(manifest['paper_exact']).lower()}`",
        f"Branch: `{manifest['repository']['branch']}`",
        "",
        manifest["bundle_scope"],
        "",
        "## Component Summary",
        "",
    ]
    for key, value in manifest["component_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Line Count Checks", ""])
    for path, value in manifest["line_count_checks"].items():
        lines.append(f"- `{path}`: {value}")
    lines.extend(["", "## Blocking Items", ""])
    for item in manifest["blocking_items"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Files", "", "| Path | Bytes | SHA256 |", "| --- | ---: | --- |"])
    for item in manifest["files"]:
        lines.append(f"| `{item['path']}` | {item['bytes']} | `{item['sha256']}` |")
    lines.extend(["", "## Verification", "", "```bash", *manifest["verification_commands"], "```", ""])
    return "\n".join(lines)


def write_archive(archive_path: Path, manifest_path: Path, readme_path: Path, files: list[dict[str, Any]]) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, "reproduction/reproducibility_bundle_manifest.json")
        zf.write(readme_path, "reproduction/reproducibility_bundle_manifest.md")
        for item in files:
            path = ROOT / item["path"]
            zf.write(path, f"reproduction/{item['path']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, default=DEFAULT_BUNDLE_ROOT)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--date", default="2026-06-04")
    args = parser.parse_args()

    manifest = build_manifest(args.date)
    args.bundle_root.mkdir(parents=True, exist_ok=True)
    manifest_path = args.bundle_root / "manifest.json"
    readme_path = args.bundle_root / "README.md"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    readme_path.write_text(render_markdown(manifest), encoding="utf-8")
    write_archive(args.archive, manifest_path, readme_path, manifest["files"])
    archive_record = file_record(args.archive)
    manifest["archive"] = archive_record
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    readme_path.write_text(render_markdown(manifest), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "files": len(manifest["files"]),
                "archive": str(args.archive),
                "archive_sha256": archive_record["sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
