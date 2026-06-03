#!/usr/bin/env python3
"""Validate the local EvoScientist reproduction assets."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    queries_path = ROOT / "queries.json"
    protocol_path = ROOT / "paper_protocol.md"
    assets_dir = ROOT / "paper_assets"

    queries_doc = json.loads(queries_path.read_text(encoding="utf-8"))
    queries = queries_doc["queries"]
    assert len(queries) == 30, f"expected 30 queries, got {len(queries)}"
    ids = [item["id"] for item in queries]
    assert ids == list(range(1, 31)), f"query ids are not 1..30: {ids}"
    for item in queries:
        assert item["topic"].strip(), item
        assert item["goal"].strip().endswith("."), item

    protocol = protocol_path.read_text(encoding="utf-8")
    for needle in [
        "Gemini-2.5-Pro",
        "Claude-4.5-Haiku",
        "gemini-3-flash",
        "mxbai-embed-large",
        "N_I = 21",
        "N_E1 = 20",
    ]:
        assert needle in protocol, f"missing protocol detail: {needle}"

    required_assets = [f"x{i}.png" for i in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
    missing = [name for name in required_assets if not (assets_dir / name).is_file()]
    assert not missing, f"missing paper assets: {missing}"
    for script in [
        "run_idea_generation.py",
        "run_direct_baseline.py",
        "normalize_system_outputs.py",
        "audit_full_trajectories.py",
        "build_pairwise_judge_inputs.py",
        "aggregate_judge_results.py",
        "run_offline_smoke.py",
        "run_llm_judge.py",
        "compare_reproduction_to_paper.py",
        "audit_reproduction_artifacts.py",
    ]:
        assert (ROOT / script).is_file(), f"missing script: {script}"
    assert (ROOT / "judge_prompt_template.md").is_file(), "missing judge prompt template"
    reported_path = ROOT / "paper_reported_results.json"
    assert reported_path.is_file(), "missing paper reported results"
    gap_json_path = ROOT / "public_artifact_gap_report.json"
    gap_md_path = ROOT / "public_artifact_gap_report.md"
    full_status_json_path = ROOT / "full_trajectory_status.json"
    full_status_md_path = ROOT / "full_trajectory_status.md"
    assert gap_json_path.is_file(), "missing public artifact gap report JSON"
    assert gap_md_path.is_file(), "missing public artifact gap report markdown"
    assert full_status_json_path.is_file(), "missing full trajectory status JSON"
    assert full_status_md_path.is_file(), "missing full trajectory status markdown"
    gap_report = json.loads(gap_json_path.read_text(encoding="utf-8"))
    assert gap_report["checked_sources"], "gap report has no checked sources"
    assert (
        gap_report["missing_for_exact_table1_reproduction"]["pairwise_judge_inputs"]
        == "30 queries x 7 baselines x 2 swapped orders = 420 records"
    )
    assert "not possible from public artifacts alone" in gap_report["conclusion"]
    full_status = json.loads(full_status_json_path.read_text(encoding="utf-8"))
    assert full_status["manifest_status"] == "ok"
    assert full_status["query_id"] == 1
    assert "CrossLingual-RAG" in full_status["final_report"]["title"]
    assert full_status["artifact_files"]["final_report.md"]["bytes"] >= 10000
    assert full_status["full_trajectory_counts"]["successful_final_reports"] == 3
    assert len(full_status["query_2_attempts"]) == 3
    assert "clarification" in full_status["query_2_attempts"][0]["result"]
    assert full_status["query_2_success"]["artifact_files"]["final_report.md"]["bytes"] >= 10000
    assert "TraceRoute" in full_status["query_2_success"]["final_report"]["title"]
    assert full_status["query_3_success"]["artifact_files"]["final_report.md"]["bytes"] >= 10000
    assert "Multi-Perspective" in full_status["query_3_success"]["final_report"]["title"]
    assert full_status["audit"]["counts"]["success"] == 3
    assert full_status["audit"]["counts"]["missing"] == 27
    reported = json.loads(reported_path.read_text(encoding="utf-8"))
    for section in [
        "table1_llm_idea_generation",
        "table2_human_idea_generation",
        "table3_ablation_idea_generation",
        "figure2_code_execution",
    ]:
        assert section in reported, f"missing reported results section: {section}"
    status_path = ROOT / "reproduction_status.md"
    assert status_path.is_file(), "missing reproduction status matrix"
    status_text = status_path.read_text(encoding="utf-8")
    runner_text = (ROOT / "run_idea_generation.py").read_text(encoding="utf-8")
    assert "DEFAULT_COLLECT_FILES" in runner_text, "idea runner does not collect workspace outputs"
    assert "final_report.md" in runner_text, "idea runner does not collect final_report.md"
    assert "--force-proposal" in runner_text, "idea runner cannot force broad queries to proposal output"
    assert "clear_workspace_files" in runner_text, "idea runner does not clear stale collected files"
    assert "--session-mode" in runner_text, "idea runner cannot control EvoSci session mode"
    assert "--start-id" in runner_text, "idea runner cannot continue from remaining paper queries"
    assert "--query-ids" in runner_text, "idea runner cannot run an explicit query subset"
    assert "--idle-timeout" in runner_text, "idea runner cannot stop stalled streamed runs"
    assert '"run"' in runner_text and "--mode" in runner_text, "idea runner does not default to isolated run mode"
    assert "run_workspace_dir" in runner_text, "idea runner does not collect from isolated run workspaces"
    assert "clear_artifact_files" in runner_text, "idea runner does not clear stale collected artifacts"
    assert "/final_report.md" in runner_text, "force-proposal prompt does not require final_report.md"
    for needle in [
        "Verified Locally",
        "Not Yet Paper-Level Reproduction",
        "DeepSeek-backed EvoScientist proposal-only outputs exist",
        "Target-system output coverage is complete for proposal-only mode",
        "Replacement-baseline judge pipeline is complete",
        "EvoScientist CLI outputs are normalized before judging",
        "Full trajectory audit is executable",
        "Full trajectory reruns are isolated by default",
        "not a self-evolving system",
        "Ubuntu GPU Status",
    ]:
        assert needle in status_text, f"missing status detail: {needle}"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        systems = tmp_path / "systems"
        for system, answer in {
            "EvoScientist": "Detailed proposal with clear method and experiments.",
            "BaselineA": "Generic proposal with fewer concrete details.",
        }.items():
            qdir = systems / system / "query_01"
            qdir.mkdir(parents=True)
            (qdir / "answer.txt").write_text(answer, encoding="utf-8")

        judge_inputs = tmp_path / "judge_inputs.jsonl"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build_pairwise_judge_inputs.py"),
                "--systems-root",
                str(systems),
                "--baseline",
                "BaselineA",
                "--limit",
                "1",
                "--output",
                str(judge_inputs),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert len(judge_inputs.read_text(encoding="utf-8").splitlines()) == 2

        mock_judge_outputs = tmp_path / "mock_judge_outputs.jsonl"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_llm_judge.py"),
                "--input",
                str(judge_inputs),
                "--output",
                str(mock_judge_outputs),
                "--provider",
                "mock",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert len(mock_judge_outputs.read_text(encoding="utf-8").splitlines()) == 2

        judge_outputs = tmp_path / "judge_outputs.jsonl"
        judge_outputs.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "comparison_id": "q01__EvoScientist__vs__BaselineA",
                            "query_id": 1,
                            "assistant_1_system": "EvoScientist",
                            "assistant_2_system": "BaselineA",
                            "assistant_1": {
                                "Clarity": 8,
                                "Novelty": 8,
                                "Feasibility": 7,
                                "Relevance": 9,
                            },
                            "assistant_2": {
                                "Clarity": 6,
                                "Novelty": 5,
                                "Feasibility": 6,
                                "Relevance": 8,
                            },
                        }
                    ),
                    json.dumps(
                        {
                            "comparison_id": "q01__BaselineA__vs__EvoScientist",
                            "query_id": 1,
                            "assistant_1_system": "BaselineA",
                            "assistant_2_system": "EvoScientist",
                            "assistant_1": {
                                "Clarity": 6,
                                "Novelty": 5,
                                "Feasibility": 6,
                                "Relevance": 8,
                            },
                            "assistant_2": {
                                "Clarity": 8,
                                "Novelty": 8,
                                "Feasibility": 7,
                                "Relevance": 9,
                            },
                        }
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        table_json = tmp_path / "table.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "aggregate_judge_results.py"),
                "--input",
                str(judge_outputs),
                "--output-csv",
                str(tmp_path / "table.csv"),
                "--output-json",
                str(table_json),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(table_json.read_text(encoding="utf-8"))
        assert summary["baselines"]["BaselineA"]["avg_gap"] == 100.0

        expected_table1 = reported["table1_llm_idea_generation"]
        matching_actual = {
            "target_system": "EvoScientist",
            "tie_threshold": 0.0,
            "raw_records": 60,
            "baselines": {},
        }
        for baseline, expected_baseline in expected_table1["baselines"].items():
            matching_actual["baselines"][baseline] = {
                "dimensions": {
                    dim: {
                        "baseline": baseline,
                        "dimension": dim,
                        "n": 60,
                        "win": 0,
                        "tie": 0,
                        "lose": 0,
                        **values,
                        "gap": round(values["win_pct"] - values["lose_pct"], 2),
                    }
                    for dim, values in expected_baseline["dimensions"].items()
                },
                "avg_gap": expected_baseline["avg_gap"],
            }
        matching_actual_path = tmp_path / "matching_actual.json"
        matching_actual_path.write_text(
            json.dumps(matching_actual, indent=2), encoding="utf-8"
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "compare_reproduction_to_paper.py"),
                "--actual-json",
                str(matching_actual_path),
                "--section",
                "table1_llm_idea_generation",
                "--require-all",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        audit_root = tmp_path / "audit_artifacts"
        audit_systems = audit_root / "idea_outputs"
        for system, answer in {
            "EvoScientist": "Detailed proposal with clear method and experiments.",
            "BaselineA": "Generic proposal with fewer concrete details.",
        }.items():
            qdir = audit_systems / system / "query_01"
            qdir.mkdir(parents=True)
            (qdir / "answer.txt").write_text(answer, encoding="utf-8")
        audit_inputs = audit_root / "judge_inputs" / "results.jsonl"
        audit_inputs.parent.mkdir(parents=True)
        audit_inputs.write_text(judge_inputs.read_text(encoding="utf-8"), encoding="utf-8")
        audit_outputs = audit_root / "judge_outputs" / "results.jsonl"
        audit_outputs.parent.mkdir(parents=True)
        audit_outputs.write_text(judge_outputs.read_text(encoding="utf-8"), encoding="utf-8")
        audit_table = audit_root / "tables" / "idea_generation_win_tie_lose.json"
        audit_table.parent.mkdir(parents=True)
        audit_table.write_text(table_json.read_text(encoding="utf-8"), encoding="utf-8")
        audit_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "audit_reproduction_artifacts.py"),
                "--artifacts-root",
                str(audit_root),
                "--baseline",
                "BaselineA",
                "--limit",
                "1",
                "--strict",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert '"status": "complete"' in audit_result.stdout

        smoke_dir = tmp_path / "offline_smoke"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "run_offline_smoke.py"),
                "--limit",
                "2",
                "--output-dir",
                str(smoke_dir),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        smoke_report = smoke_dir / "SMOKE_REPORT.md"
        assert smoke_report.is_file(), "offline smoke report was not written"
        smoke_summary = json.loads(
            (smoke_dir / "tables" / "synthetic_win_tie_lose.json").read_text(
                encoding="utf-8"
            )
        )
        assert smoke_summary["raw_records"] == 4

    print("reproduction_assets_ok")
    print(f"queries={len(queries)}")
    print(f"assets={len(required_assets)}")


if __name__ == "__main__":
    main()
