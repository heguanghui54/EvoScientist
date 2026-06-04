#!/usr/bin/env python3
"""Build a local replacement probe for Figure 2 code-execution artifacts.

The paper's raw generated-code trajectories are not present in the public
checkout. This probe therefore records real local execution checks over existing
reproduction artifacts instead of fabricating the paper's success/failure logs.
It is intentionally marked as non-paper-exact in the generated report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
DEFAULT_OUTPUT_ROOT = ROOT / "artifacts" / "code_execution"
STAGES = ["stage_1", "stage_2", "stage_3", "stage_4"]
PHASES = ["before_evolution", "after_evolution"]


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def before_answer_path(query_id: int) -> Path:
    return (
        ROOT
        / "artifacts"
        / "ablations"
        / "-all"
        / "system_outputs"
        / "-all"
        / f"query_{query_id:02d}"
        / "answer.txt"
    )


def after_answer_path(query_id: int) -> Path:
    candidates = [
        ROOT
        / "artifacts"
        / "remote_fetch"
        / "full_trajectories"
        / "EvoScientist"
        / f"query_{query_id:02d}"
        / "final_report.md",
        ROOT
        / "artifacts"
        / "idea_outputs"
        / "EvoScientist"
        / f"query_{query_id:02d}"
        / "answer.txt",
    ]
    for path in candidates:
        if path.is_file() and read_text(path).strip():
            return path
    return candidates[0]


def stage_1_query_parse(query: dict[str, Any], answer_path: Path) -> tuple[bool, str]:
    required = {"id", "goal", "topic"}
    missing = sorted(required - set(query))
    return not missing, "query metadata has id/goal/topic" if not missing else f"missing query fields: {missing}"


def stage_2_answer_available(query: dict[str, Any], answer_path: Path) -> tuple[bool, str]:
    text = read_text(answer_path).strip()
    return len(text) >= 1000, f"answer_chars={len(text)}"


def stage_3_proposal_sections(query: dict[str, Any], answer_path: Path) -> tuple[bool, str]:
    text = read_text(answer_path).lower()
    groups = {
        "method": ["method", "approach", "architecture"],
        "evaluation": ["evaluation", "metric", "benchmark"],
        "baseline": ["baseline", "comparison"],
        "limitations": ["limitation", "risk", "failure"],
    }
    present = {
        name: any(token in text for token in tokens)
        for name, tokens in groups.items()
    }
    return all(present.values()), "section_signals=" + json.dumps(present, sort_keys=True)


def stage_4_reproducibility_cues(query: dict[str, Any], answer_path: Path) -> tuple[bool, str]:
    text = read_text(answer_path).lower()
    cues = ["dataset", "ablation", "metric", "experiment"]
    present = [cue for cue in cues if cue in text]
    return len(present) >= 3, f"reproducibility_cues={present}"


CHECKS: dict[str, Callable[[dict[str, Any], Path], tuple[bool, str]]] = {
    "stage_1": stage_1_query_parse,
    "stage_2": stage_2_answer_available,
    "stage_3": stage_3_proposal_sections,
    "stage_4": stage_4_reproducibility_cues,
}


def source_path_for(phase: str, query_id: int) -> Path:
    if phase == "before_evolution":
        return before_answer_path(query_id)
    if phase == "after_evolution":
        return after_answer_path(query_id)
    raise ValueError(f"unknown phase: {phase}")


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    trajectories: list[dict[str, Any]] = []
    logs: list[dict[str, Any]] = []
    for query in load_queries():
        query_id = int(query["id"])
        for phase in PHASES:
            answer_path = source_path_for(phase, query_id)
            for stage in STAGES:
                trajectory_id = f"{phase}__{stage}__q{query_id:02d}"
                proposal_id = f"{phase}__query_{query_id:02d}"
                trajectories.append(
                    {
                        "trajectory_id": trajectory_id,
                        "query_id": query_id,
                        "stage": stage,
                        "proposal_id": proposal_id,
                        "phase": phase,
                        "source_path": str(answer_path.relative_to(REPO_ROOT)),
                        "paper_exact": False,
                        "replacement_probe": True,
                    }
                )
                success, detail = CHECKS[stage](query, answer_path)
                logs.append(
                    {
                        "trajectory_id": trajectory_id,
                        "stage": stage,
                        "attempt_id": f"{trajectory_id}__attempt_01",
                        "success": success,
                        "phase": phase,
                        "check": CHECKS[stage].__name__,
                        "detail": detail,
                    }
                )
    return trajectories, logs


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    trajectories, logs = build_records()
    write_jsonl(args.output_root / "trajectories.jsonl", trajectories)
    write_jsonl(args.output_root / "execution_logs.jsonl", logs)
    metadata = {
        "status": "complete",
        "paper_exact": False,
        "scope": "replacement_code_execution_probe",
        "trajectory_records": len(trajectories),
        "execution_log_records": len(logs),
        "phases": PHASES,
        "stages": STAGES,
        "before_evolution_source": "reproduction/artifacts/ablations/-all/system_outputs/-all",
        "after_evolution_source": "reproduction/artifacts/remote_fetch/full_trajectories/EvoScientist",
        "caveat": (
            "This probe executes deterministic local validation checks over "
            "reproduction artifacts. It does not recreate the paper's original "
            "generated-code execution benchmark."
        ),
    }
    (args.output_root / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
