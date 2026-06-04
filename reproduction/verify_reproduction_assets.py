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
        "import_baseline_outputs.py",
        "normalize_system_outputs.py",
        "audit_full_trajectories.py",
        "refresh_full_trajectory_status.py",
        "audit_paper_level_completion.py",
        "build_pairwise_judge_inputs.py",
        "aggregate_judge_results.py",
        "run_offline_smoke.py",
        "run_llm_judge.py",
        "summarize_baseline_readiness.py",
        "probe_virtual_scientist_baseline.py",
        "probe_ai_researcher_baseline.py",
        "probe_internagent_baseline.py",
        "build_internagent_qa_runbook.py",
        "run_internagent_qa_baseline.py",
        "build_internagent_query01_smoke_report.py",
        "build_internagent_smoke_report.py",
        "probe_ai_scientist_v2_baseline.py",
        "build_ai_scientist_v2_ideation_runbook.py",
        "convert_ai_scientist_v2_ideation_outputs.py",
        "probe_hypogenic_baseline.py",
        "probe_novix_baseline.py",
        "probe_k_dense_baseline.py",
        "aggregate_human_labels.py",
        "aggregate_ablation_results.py",
        "aggregate_code_execution.py",
        "build_paper_reproduction_plan.py",
        "compare_reproduction_to_paper.py",
        "audit_reproduction_artifacts.py",
        "verify_replacement_baseline_protocol.py",
        "verify_paper_artifact_schema.py",
        "build_baseline_rerun_manifest.py",
    ]:
        assert (ROOT / script).is_file(), f"missing script: {script}"
    assert (ROOT / "judge_prompt_template.md").is_file(), "missing judge prompt template"
    reported_path = ROOT / "paper_reported_results.json"
    assert reported_path.is_file(), "missing paper reported results"
    gap_json_path = ROOT / "public_artifact_gap_report.json"
    gap_md_path = ROOT / "public_artifact_gap_report.md"
    baseline_inventory_json_path = ROOT / "paper_baseline_availability.json"
    baseline_inventory_md_path = ROOT / "paper_baseline_availability.md"
    replacement_protocol_json_path = ROOT / "replacement_baseline_protocol.json"
    replacement_protocol_md_path = ROOT / "replacement_baseline_protocol.md"
    paper_artifact_schema_json_path = ROOT / "paper_artifact_schema.json"
    paper_artifact_schema_md_path = ROOT / "paper_artifact_schema.md"
    full_status_json_path = ROOT / "full_trajectory_status.json"
    full_status_md_path = ROOT / "full_trajectory_status.md"
    baseline_readiness_json_path = ROOT / "baseline_readiness_matrix.json"
    baseline_readiness_md_path = ROOT / "baseline_readiness_matrix.md"
    baseline_rerun_manifest_json_path = ROOT / "baseline_rerun_manifest.json"
    baseline_rerun_manifest_md_path = ROOT / "baseline_rerun_manifest.md"
    assert gap_json_path.is_file(), "missing public artifact gap report JSON"
    assert gap_md_path.is_file(), "missing public artifact gap report markdown"
    assert baseline_inventory_json_path.is_file(), "missing baseline availability inventory JSON"
    assert baseline_inventory_md_path.is_file(), "missing baseline availability inventory markdown"
    assert replacement_protocol_json_path.is_file(), "missing replacement baseline protocol JSON"
    assert replacement_protocol_md_path.is_file(), "missing replacement baseline protocol markdown"
    assert paper_artifact_schema_json_path.is_file(), "missing paper artifact schema JSON"
    assert paper_artifact_schema_md_path.is_file(), "missing paper artifact schema markdown"
    assert full_status_json_path.is_file(), "missing full trajectory status JSON"
    assert full_status_md_path.is_file(), "missing full trajectory status markdown"
    assert baseline_readiness_json_path.is_file(), "missing baseline readiness matrix JSON"
    assert baseline_readiness_md_path.is_file(), "missing baseline readiness matrix markdown"
    assert baseline_rerun_manifest_json_path.is_file(), "missing baseline rerun manifest JSON"
    assert baseline_rerun_manifest_md_path.is_file(), "missing baseline rerun manifest markdown"
    gap_report = json.loads(gap_json_path.read_text(encoding="utf-8"))
    assert gap_report["checked_sources"], "gap report has no checked sources"
    assert (
        gap_report["missing_for_exact_table1_reproduction"]["pairwise_judge_inputs"]
        == "30 queries x 7 baselines x 2 swapped orders = 420 records"
    )
    assert "not possible from public artifacts alone" in gap_report["conclusion"]
    baseline_inventory = json.loads(baseline_inventory_json_path.read_text(encoding="utf-8"))
    baseline_names = [item["name"] for item in baseline_inventory["baselines"]]
    assert baseline_names == [
        "Virtual Scientist",
        "AI-Researcher",
        "InternAgent",
        "AI Scientist-v2",
        "Hypogenic",
        "Novix",
        "K-Dense",
    ]
    assert baseline_inventory["summary"]["raw_output_packages_found"] == 0
    assert all(not item["table1_raw_outputs_available"] for item in baseline_inventory["baselines"])
    assert "Virtual Scientist" in baseline_inventory["summary"]["runner_candidates_found"]
    assert "AI-Researcher" in baseline_inventory["summary"]["runner_candidates_found"]
    assert "Hypogenic" in baseline_inventory["summary"]["runner_candidates_found"]
    assert "Virtual Scientist" not in baseline_inventory["summary"]["no_reliable_public_runner_found"]
    assert "Hypogenic" not in baseline_inventory["summary"]["no_reliable_public_runner_found"]
    baseline_inventory_md = baseline_inventory_md_path.read_text(encoding="utf-8")
    assert "Raw baseline-output packages found: 0" in baseline_inventory_md
    assert "virtual_scientist_baseline_probe.json" in baseline_inventory_md
    assert "ai_researcher_baseline_probe.json" in baseline_inventory_md
    assert "hypogenic_baseline_probe.json" in baseline_inventory_md
    assert "novix_baseline_probe.json" in baseline_inventory_md
    assert "k_dense_baseline_probe.json" in baseline_inventory_md
    ai_researcher_probe_json_path = ROOT / "ai_researcher_baseline_probe.json"
    ai_researcher_probe_md_path = ROOT / "ai_researcher_baseline_probe.md"
    assert ai_researcher_probe_json_path.is_file(), "missing AI-Researcher probe JSON"
    assert ai_researcher_probe_md_path.is_file(), "missing AI-Researcher probe markdown"
    ai_researcher_probe = json.loads(ai_researcher_probe_json_path.read_text(encoding="utf-8"))
    assert ai_researcher_probe["baseline"] == "AI-Researcher"
    assert ai_researcher_probe["evo_table1_drop_in_status"] == "not_drop_in"
    assert ai_researcher_probe["signals"]["benchmark_instance_required"] is True
    assert ai_researcher_probe["signals"]["docker_required"] is True
    assert ai_researcher_probe["direct_30_query_runner_available"] is False
    assert "benchmark-instance based" in ai_researcher_probe["reproduction_implication"]
    assert "not_drop_in" in ai_researcher_probe_md_path.read_text(encoding="utf-8")
    internagent_probe_json_path = ROOT / "internagent_baseline_probe.json"
    internagent_probe_md_path = ROOT / "internagent_baseline_probe.md"
    assert internagent_probe_json_path.is_file(), "missing InternAgent probe JSON"
    assert internagent_probe_md_path.is_file(), "missing InternAgent probe markdown"
    internagent_probe = json.loads(internagent_probe_json_path.read_text(encoding="utf-8"))
    assert internagent_probe["baseline"] == "InternAgent"
    assert internagent_probe["evo_table1_drop_in_status"] == "qa_drop_in_candidate"
    assert internagent_probe["paper_exact_status"] == "not_paper_exact"
    assert internagent_probe["signals"]["qa_cli_available"] is True
    assert internagent_probe["direct_30_query_runner_available"] is True
    assert "launch.py --mode qa" in internagent_probe["entrypoints"]["master_qa"]
    assert "qa_drop_in_candidate" in internagent_probe_md_path.read_text(encoding="utf-8")
    internagent_runbook_json_path = ROOT / "internagent_qa_runbook.json"
    internagent_runbook_md_path = ROOT / "internagent_qa_runbook.md"
    internagent_runbook_sh_path = ROOT / "internagent_qa_runbook.sh"
    assert internagent_runbook_json_path.is_file(), "missing InternAgent QA runbook JSON"
    assert internagent_runbook_md_path.is_file(), "missing InternAgent QA runbook markdown"
    assert internagent_runbook_sh_path.is_file(), "missing InternAgent QA runbook shell script"
    internagent_runbook = json.loads(internagent_runbook_json_path.read_text(encoding="utf-8"))
    assert internagent_runbook["baseline"] == "InternAgent"
    assert internagent_runbook["mode"] == "qa_replacement_baseline"
    assert internagent_runbook["query_count"] == 30
    assert internagent_runbook["paper_exact"] is False
    assert len(internagent_runbook["commands"]) == 30
    assert "import_baseline_outputs.py --system-name InternAgent" in internagent_runbook["import_command"]
    internagent_runbook_sh = internagent_runbook_sh_path.read_text(encoding="utf-8")
    assert internagent_runbook_sh.count("python launch.py --mode qa") == 30
    assert "query_30.md" in internagent_runbook_sh
    internagent_runner_text = (ROOT / "run_internagent_qa_baseline.py").read_text(
        encoding="utf-8"
    )
    assert "deepseek-chat" in internagent_runner_text
    assert "workflow.main" in internagent_runner_text
    assert "o4-mini" in internagent_runner_text
    internagent_smoke_json_path = ROOT / "internagent_query01_smoke_report.json"
    internagent_smoke_md_path = ROOT / "internagent_query01_smoke_report.md"
    assert internagent_smoke_json_path.is_file(), "missing InternAgent query-01 smoke JSON"
    assert internagent_smoke_md_path.is_file(), "missing InternAgent query-01 smoke markdown"
    internagent_smoke = json.loads(internagent_smoke_json_path.read_text(encoding="utf-8"))
    assert internagent_smoke["baseline"] == "InternAgent"
    assert internagent_smoke["query_id"] == 1
    assert internagent_smoke["paper_exact"] is False
    assert internagent_smoke["status"] == "complete"
    assert internagent_smoke["judge_records"] == 2
    assert (
        ROOT / "artifacts" / "idea_outputs" / "InternAgent" / "query_01" / "answer.txt"
    ).is_file()
    assert (
        ROOT / "artifacts" / "judge_inputs" / "evosci_vs_internagent_query01.jsonl"
    ).is_file()
    assert (
        ROOT / "artifacts" / "judge_outputs" / "evosci_vs_internagent_query01_deepseek.jsonl"
    ).is_file()
    assert (
        ROOT / "artifacts" / "tables" / "evosci_vs_internagent_query01_deepseek.json"
    ).is_file()
    smoke_dims = internagent_smoke["aggregate"]["baselines"]["InternAgent"]["dimensions"]
    assert set(smoke_dims) == {"Clarity", "Novelty", "Feasibility", "Relevance"}
    assert smoke_dims["Clarity"]["n"] == 2
    assert "InternAgent Query-01 Smoke Report" in internagent_smoke_md_path.read_text(
        encoding="utf-8"
    )
    internagent_3q_smoke_json_path = ROOT / "internagent_queries01_03_smoke_report.json"
    internagent_3q_smoke_md_path = ROOT / "internagent_queries01_03_smoke_report.md"
    assert internagent_3q_smoke_json_path.is_file(), "missing InternAgent queries01-03 smoke JSON"
    assert internagent_3q_smoke_md_path.is_file(), "missing InternAgent queries01-03 smoke markdown"
    internagent_3q_smoke = json.loads(internagent_3q_smoke_json_path.read_text(encoding="utf-8"))
    assert internagent_3q_smoke["baseline"] == "InternAgent"
    assert internagent_3q_smoke["query_ids"] == [1, 2, 3]
    assert internagent_3q_smoke["paper_exact"] is False
    assert internagent_3q_smoke["status"] == "complete"
    assert internagent_3q_smoke["judge_records"] == 6
    for query_id in [1, 2, 3]:
        assert (
            ROOT / "artifacts" / "idea_outputs" / "InternAgent" / f"query_{query_id:02d}" / "answer.txt"
        ).is_file()
    assert (
        ROOT / "artifacts" / "judge_inputs" / "evosci_vs_internagent_queries01_03.jsonl"
    ).is_file()
    assert (
        ROOT / "artifacts" / "judge_outputs" / "evosci_vs_internagent_queries01_03_deepseek.jsonl"
    ).is_file()
    assert (
        ROOT / "artifacts" / "tables" / "evosci_vs_internagent_queries01_03_deepseek.json"
    ).is_file()
    smoke_3q_dims = internagent_3q_smoke["aggregate"]["baselines"]["InternAgent"]["dimensions"]
    assert set(smoke_3q_dims) == {"Clarity", "Novelty", "Feasibility", "Relevance"}
    assert smoke_3q_dims["Clarity"]["n"] == 6
    assert "InternAgent queries01_03 Smoke Report" in internagent_3q_smoke_md_path.read_text(
        encoding="utf-8"
    )
    internagent_5q_smoke_json_path = ROOT / "internagent_queries01_05_smoke_report.json"
    internagent_5q_smoke_md_path = ROOT / "internagent_queries01_05_smoke_report.md"
    assert internagent_5q_smoke_json_path.is_file(), "missing InternAgent queries01-05 smoke JSON"
    assert internagent_5q_smoke_md_path.is_file(), "missing InternAgent queries01-05 smoke markdown"
    internagent_5q_smoke = json.loads(internagent_5q_smoke_json_path.read_text(encoding="utf-8"))
    assert internagent_5q_smoke["baseline"] == "InternAgent"
    assert internagent_5q_smoke["query_ids"] == [1, 2, 3, 4, 5]
    assert internagent_5q_smoke["paper_exact"] is False
    assert internagent_5q_smoke["status"] == "complete"
    assert internagent_5q_smoke["judge_records"] == 10
    for query_id in [1, 2, 3, 4, 5]:
        assert (
            ROOT / "artifacts" / "idea_outputs" / "InternAgent" / f"query_{query_id:02d}" / "answer.txt"
        ).is_file()
    assert (
        ROOT / "artifacts" / "judge_inputs" / "evosci_vs_internagent_queries01_05.jsonl"
    ).is_file()
    assert (
        ROOT / "artifacts" / "judge_outputs" / "evosci_vs_internagent_queries01_05_deepseek.jsonl"
    ).is_file()
    assert (
        ROOT / "artifacts" / "tables" / "evosci_vs_internagent_queries01_05_deepseek.json"
    ).is_file()
    smoke_5q_dims = internagent_5q_smoke["aggregate"]["baselines"]["InternAgent"]["dimensions"]
    assert set(smoke_5q_dims) == {"Clarity", "Novelty", "Feasibility", "Relevance"}
    assert smoke_5q_dims["Clarity"]["n"] == 10
    assert "InternAgent queries01_05 Smoke Report" in internagent_5q_smoke_md_path.read_text(
        encoding="utf-8"
    )
    ai_scientist_probe_json_path = ROOT / "ai_scientist_v2_baseline_probe.json"
    ai_scientist_probe_md_path = ROOT / "ai_scientist_v2_baseline_probe.md"
    assert ai_scientist_probe_json_path.is_file(), "missing AI Scientist-v2 probe JSON"
    assert ai_scientist_probe_md_path.is_file(), "missing AI Scientist-v2 probe markdown"
    ai_scientist_probe = json.loads(ai_scientist_probe_json_path.read_text(encoding="utf-8"))
    assert ai_scientist_probe["baseline"] == "AI Scientist-v2"
    assert ai_scientist_probe["evo_table1_drop_in_status"] == "ideation_adapter_candidate"
    assert ai_scientist_probe["paper_exact_status"] == "not_paper_exact"
    assert ai_scientist_probe["signals"]["ideation_cli_available"] is True
    assert ai_scientist_probe["direct_30_query_runner_available"] is True
    assert "perform_ideation_temp_free.py" in ai_scientist_probe["entrypoints"]["ideation"]
    ai_scientist_runbook_root = ROOT / "ai_scientist_v2_ideation_runbook"
    ai_scientist_runbook_json_path = ai_scientist_runbook_root / "ai_scientist_v2_ideation_runbook.json"
    ai_scientist_runbook_md_path = ai_scientist_runbook_root / "ai_scientist_v2_ideation_runbook.md"
    ai_scientist_runbook_sh_path = ai_scientist_runbook_root / "run_ai_scientist_v2_ideation.sh"
    assert ai_scientist_runbook_json_path.is_file(), "missing AI Scientist-v2 runbook JSON"
    assert ai_scientist_runbook_md_path.is_file(), "missing AI Scientist-v2 runbook markdown"
    assert ai_scientist_runbook_sh_path.is_file(), "missing AI Scientist-v2 runbook shell script"
    ai_scientist_runbook = json.loads(ai_scientist_runbook_json_path.read_text(encoding="utf-8"))
    assert ai_scientist_runbook["baseline"] == "AI Scientist-v2"
    assert ai_scientist_runbook["query_count"] == 30
    assert len(ai_scientist_runbook["commands"]) == 30
    assert ai_scientist_runbook["paper_exact"] is False
    assert "AI Scientist-v2" in ai_scientist_runbook["import_command"]
    assert ai_scientist_runbook_sh_path.read_text(encoding="utf-8").count("perform_ideation_temp_free.py") == 30
    assert (ai_scientist_runbook_root / "topics" / "query_30.md").is_file()
    ai_scientist_converter_text = (
        ROOT / "convert_ai_scientist_v2_ideation_outputs.py"
    ).read_text(encoding="utf-8")
    assert "ai_scientist_v2_ideation_import_template.jsonl" in ai_scientist_converter_text
    assert "query_*.json" in ai_scientist_converter_text
    virtual_scientist_probe_json_path = ROOT / "virtual_scientist_baseline_probe.json"
    virtual_scientist_probe_md_path = ROOT / "virtual_scientist_baseline_probe.md"
    assert virtual_scientist_probe_json_path.is_file(), "missing Virtual Scientist probe JSON"
    assert virtual_scientist_probe_md_path.is_file(), "missing Virtual Scientist probe markdown"
    virtual_scientist_probe = json.loads(
        virtual_scientist_probe_json_path.read_text(encoding="utf-8")
    )
    assert virtual_scientist_probe["baseline"] == "Virtual Scientist"
    assert virtual_scientist_probe["evo_table1_drop_in_status"] == "open_source_platform_not_drop_in"
    assert virtual_scientist_probe["paper_exact_status"] == "not_paper_exact"
    assert virtual_scientist_probe["signals"]["repo_available"] is True
    assert virtual_scientist_probe["signals"]["arxiv_2410_09403_linked"] is True
    assert virtual_scientist_probe["signals"]["data_required"] is True
    assert virtual_scientist_probe["signals"]["ollama_models_required"] is True
    assert virtual_scientist_probe["signals"]["query_cli_available"] is False
    assert virtual_scientist_probe["signals"]["raw_table1_outputs_found"] is False
    assert virtual_scientist_probe["direct_30_query_runner_available"] is False
    assert "open_source_platform_not_drop_in" in virtual_scientist_probe_md_path.read_text(encoding="utf-8")
    hypogenic_probe_json_path = ROOT / "hypogenic_baseline_probe.json"
    hypogenic_probe_md_path = ROOT / "hypogenic_baseline_probe.md"
    assert hypogenic_probe_json_path.is_file(), "missing Hypogenic probe JSON"
    assert hypogenic_probe_md_path.is_file(), "missing Hypogenic probe markdown"
    hypogenic_probe = json.loads(hypogenic_probe_json_path.read_text(encoding="utf-8"))
    assert hypogenic_probe["baseline"] == "Hypogenic"
    assert hypogenic_probe["evo_table1_drop_in_status"] == "hosted_competition_adapter_candidate"
    assert hypogenic_probe["paper_exact_status"] == "not_paper_exact"
    assert hypogenic_probe["signals"]["hosted_platform_available"] is True
    assert hypogenic_probe["signals"]["assistant_link_available"] is True
    assert hypogenic_probe["signals"]["arena_available"] is True
    assert hypogenic_probe["signals"]["generated_repos_available"] is True
    assert hypogenic_probe["signals"]["public_runner_repo_found"] is False
    assert hypogenic_probe["signals"]["raw_table1_outputs_found"] is False
    assert hypogenic_probe["direct_30_query_runner_available"] is False
    assert hypogenic_probe["hypogenic_generated_repo_examples"], "missing generated repo examples"
    assert "hosted_competition_adapter_candidate" in hypogenic_probe_md_path.read_text(encoding="utf-8")
    novix_probe_json_path = ROOT / "novix_baseline_probe.json"
    novix_probe_md_path = ROOT / "novix_baseline_probe.md"
    assert novix_probe_json_path.is_file(), "missing Novix probe JSON"
    assert novix_probe_md_path.is_file(), "missing Novix probe markdown"
    novix_probe = json.loads(novix_probe_json_path.read_text(encoding="utf-8"))
    assert novix_probe["baseline"] == "Novix"
    assert novix_probe["evo_table1_drop_in_status"] == "hosted_ui_adapter_candidate"
    assert novix_probe["paper_exact_status"] == "not_paper_exact"
    assert novix_probe["signals"]["hosted_chat_available"] is True
    assert novix_probe["signals"]["same_as_ai_researcher"] is True
    assert novix_probe["signals"]["independent_public_novix_repo_found"] is False
    assert novix_probe["signals"]["public_batch_api_docs_found"] is False
    assert novix_probe["signals"]["raw_table1_outputs_found"] is False
    assert novix_probe["direct_30_query_runner_available"] is False
    assert "/task/submit_user_question" in novix_probe["visible_product_endpoints"]
    assert "hosted_ui_adapter_candidate" in novix_probe_md_path.read_text(encoding="utf-8")
    k_dense_probe_json_path = ROOT / "k_dense_baseline_probe.json"
    k_dense_probe_md_path = ROOT / "k_dense_baseline_probe.md"
    assert k_dense_probe_json_path.is_file(), "missing K-Dense probe JSON"
    assert k_dense_probe_md_path.is_file(), "missing K-Dense probe markdown"
    k_dense_probe = json.loads(k_dense_probe_json_path.read_text(encoding="utf-8"))
    assert k_dense_probe["baseline"] == "K-Dense"
    assert k_dense_probe["evo_table1_drop_in_status"] == "local_web_api_adapter_candidate"
    assert k_dense_probe["paper_exact_status"] == "not_paper_exact"
    assert k_dense_probe["signals"]["hosted_platform_available"] is True
    assert k_dense_probe["signals"]["byok_repo_available"] is True
    assert k_dense_probe["signals"]["adk_run_sse_endpoint_available"] is True
    assert k_dense_probe["signals"]["raw_table1_outputs_found"] is False
    assert k_dense_probe["direct_30_query_runner_available"] is True
    assert "/run_sse" in k_dense_probe["entrypoints"]["local_http_adapter"]
    assert "local_web_api_adapter_candidate" in k_dense_probe_md_path.read_text(encoding="utf-8")
    baseline_readiness = json.loads(baseline_readiness_json_path.read_text(encoding="utf-8"))
    assert baseline_readiness["baseline_count"] == 7
    assert baseline_readiness["paper_exact_ready"] is False
    assert baseline_readiness["counts"]["paper_exact_available"] == 0
    assert baseline_readiness["counts"]["replacement_direct_or_near_direct"] == 3
    assert baseline_readiness["counts"]["replacement_adapter_required"] == 4
    assert baseline_readiness["counts"]["not_reproducible_from_public_artifacts"] == 0
    readiness_rows = {row["baseline"]: row for row in baseline_readiness["rows"]}
    assert set(readiness_rows) == set(baseline_names)
    assert readiness_rows["InternAgent"]["readiness_class"] == "replacement_direct_or_near_direct"
    assert readiness_rows["AI Scientist-v2"]["readiness_class"] == "replacement_direct_or_near_direct"
    assert readiness_rows["K-Dense"]["readiness_class"] == "replacement_direct_or_near_direct"
    assert readiness_rows["Virtual Scientist"]["readiness_class"] == "replacement_adapter_required"
    assert readiness_rows["AI-Researcher"]["readiness_class"] == "replacement_adapter_required"
    assert readiness_rows["Hypogenic"]["readiness_class"] == "replacement_adapter_required"
    assert readiness_rows["Novix"]["readiness_class"] == "replacement_adapter_required"
    baseline_readiness_md = baseline_readiness_md_path.read_text(encoding="utf-8")
    assert "Baseline Readiness Matrix" in baseline_readiness_md
    assert "paper_exact_available: 0" in baseline_readiness_md
    assert "replacement_direct_or_near_direct: 3" in baseline_readiness_md
    baseline_rerun_manifest = json.loads(
        baseline_rerun_manifest_json_path.read_text(encoding="utf-8")
    )
    assert baseline_rerun_manifest["baseline_count"] == 7
    rerun_entries = {
        entry["baseline"]: entry for entry in baseline_rerun_manifest["entries"]
    }
    assert set(rerun_entries) == set(baseline_names)
    for name, row in readiness_rows.items():
        entry = rerun_entries[name]
        assert entry["readiness_class"] == row["readiness_class"]
        assert entry["paper_exact"] is False
        assert bool(entry["prep_commands"])
        assert "import_baseline_outputs.py" in entry["import_command"]
        assert len(entry["judge_commands"]) == 4
        assert entry["acceptance_gate"] == entry["judge_commands"][-1]
        assert "audit_reproduction_artifacts.py" in entry["acceptance_gate"]
    for name in ["Virtual Scientist", "AI-Researcher", "Hypogenic", "Novix"]:
        assert rerun_entries[name]["requires_adapter"] is True
    for name in ["InternAgent", "AI Scientist-v2", "K-Dense"]:
        assert rerun_entries[name]["requires_adapter"] is False
    combined_judge = "\n".join(baseline_rerun_manifest["combined_paper_exact_judge_commands"])
    assert "--baseline 'Virtual Scientist'" in combined_judge
    assert "--baseline K-Dense" in combined_judge
    assert "--model gemini-3-flash" in combined_judge
    assert baseline_rerun_manifest["final_gate"].endswith(
        "audit_paper_level_completion.py --strict"
    )
    baseline_rerun_manifest_md = baseline_rerun_manifest_md_path.read_text(encoding="utf-8")
    assert "Baseline Rerun Manifest" in baseline_rerun_manifest_md
    assert "Combined Paper-Exact Judge Commands" in baseline_rerun_manifest_md
    assert "Virtual Scientist" in baseline_rerun_manifest_md
    assert "Hypogenic" in baseline_rerun_manifest_md
    assert "convert_ai_scientist_v2_ideation_outputs.py" in baseline_rerun_manifest_md
    replacement_protocol = json.loads(replacement_protocol_json_path.read_text(encoding="utf-8"))
    assert replacement_protocol["import_tool"]["script"] == "reproduction/import_baseline_outputs.py"
    assert replacement_protocol["judge_protocol"]["records_per_baseline"] == 60
    assert replacement_protocol["baseline_rerun_manifest"] == "reproduction/baseline_rerun_manifest.json"
    assert replacement_protocol["candidate_baselines"][0]["name"] == "Direct-DeepSeek"
    assert replacement_protocol["candidate_baselines"][0]["status"] == "completed_replacement_baseline"
    protocol_baseline_names = [item["name"] for item in replacement_protocol["candidate_baselines"]]
    for name in baseline_names:
        assert name in protocol_baseline_names, f"missing protocol baseline: {name}"
    replacement_protocol_md = replacement_protocol_md_path.read_text(encoding="utf-8")
    assert "exact Table 1 reproduction" in replacement_protocol_md
    assert "Virtual Scientist" in replacement_protocol_md
    assert "Hypogenic" in replacement_protocol_md
    assert "baseline_rerun_manifest" in replacement_protocol_md
    paper_artifact_schema = json.loads(paper_artifact_schema_json_path.read_text(encoding="utf-8"))
    assert "human_evaluation" in paper_artifact_schema["schemas"]
    assert paper_artifact_schema["schemas"]["human_evaluation"]["aggregator"] == "reproduction/aggregate_human_labels.py"
    assert "ablation" in paper_artifact_schema["schemas"]
    assert paper_artifact_schema["schemas"]["ablation"]["aggregator"] == "reproduction/aggregate_ablation_results.py"
    assert "code_execution" in paper_artifact_schema["schemas"]
    assert paper_artifact_schema["schemas"]["code_execution"]["aggregator"] == "reproduction/aggregate_code_execution.py"
    paper_artifact_schema_md = paper_artifact_schema_md_path.read_text(encoding="utf-8")
    assert "Figure 2 Code Execution" in paper_artifact_schema_md
    action_plan_json_path = ROOT / "paper_reproduction_action_plan.json"
    action_plan_md_path = ROOT / "paper_reproduction_action_plan.md"
    assert action_plan_json_path.is_file(), "missing paper reproduction action plan JSON"
    assert action_plan_md_path.is_file(), "missing paper reproduction action plan markdown"
    action_plan = json.loads(action_plan_json_path.read_text(encoding="utf-8"))
    assert action_plan["status"] == "incomplete"
    assert action_plan["action_count"] >= 4
    assert "final_gate" in action_plan
    assert action_plan["baseline_readiness_matrix"] == "reproduction/baseline_readiness_matrix.json"
    assert action_plan["baseline_rerun_manifest"] == "reproduction/baseline_rerun_manifest.json"
    assert action_plan["baseline_readiness_counts"]["paper_exact_available"] == 0
    action_plan_md = action_plan_md_path.read_text(encoding="utf-8")
    assert "Paper Reproduction Action Plan" in action_plan_md
    assert "gemini-3-flash" in action_plan_md
    assert "internagent_baseline_probe.json" in action_plan_md
    assert "build_internagent_qa_runbook.py" in action_plan_md
    assert "run_internagent_qa_baseline.py" in action_plan_md
    assert "virtual_scientist_baseline_probe.json" in action_plan_md
    assert "ai_scientist_v2_baseline_probe.json" in action_plan_md
    assert "build_ai_scientist_v2_ideation_runbook.py" in action_plan_md
    assert "convert_ai_scientist_v2_ideation_outputs.py" in action_plan_md
    assert "hypogenic_baseline_probe.json" in action_plan_md
    assert "novix_baseline_probe.json" in action_plan_md
    assert "k_dense_baseline_probe.json" in action_plan_md
    assert "Baseline Readiness" in action_plan_md
    assert "baseline_rerun_manifest.json" in action_plan_md
    full_status = json.loads(full_status_json_path.read_text(encoding="utf-8"))
    expected_success_ids = list(range(1, 31))
    expected_incomplete_ids = []
    assert full_status["full_trajectory_counts"]["successful_final_reports"] == 30
    assert full_status["audit"]["successful_query_ids"] == expected_success_ids
    assert full_status["audit"]["failed_or_incomplete_query_ids"] == expected_incomplete_ids
    for query_id in expected_success_ids:
        item = full_status["successful_queries"][f"query_{query_id:02d}"]
        assert item["artifact_files"]["final_report.md"]["bytes"] >= 10000
        assert item["final_report"]["title"], f"missing title for query {query_id}"
    assert "CrossLingual-RAG" in full_status["successful_queries"]["query_01"]["final_report"]["title"]
    assert "TraceRoute" in full_status["successful_queries"]["query_02"]["final_report"]["title"]
    assert "Multi-Perspective" in full_status["successful_queries"]["query_03"]["final_report"]["title"]
    assert "TrialMatch-Agents" in full_status["successful_queries"]["query_04"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_04"]["artifact_files"]["final_report.md"]["bytes"] >= 19000
    assert "Multi-Hop Reasoning Ceiling" in full_status["successful_queries"]["query_07"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_07"]["artifact_files"]["final_report.md"]["bytes"] >= 23000
    assert "AToMP-Edge" in full_status["successful_queries"]["query_09"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_09"]["artifact_files"]["final_report.md"]["bytes"] >= 11000
    assert "Evidence-Conditioned Activation Steering" in full_status["successful_queries"]["query_12"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_12"]["artifact_files"]["final_report.md"]["bytes"] >= 14000
    assert "AdaSpec" in full_status["successful_queries"]["query_14"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_14"]["artifact_files"]["final_report.md"]["bytes"] >= 18000
    assert "Structured vs. Unstructured Knowledge Injection" in full_status["successful_queries"]["query_16"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_16"]["artifact_files"]["final_report.md"]["bytes"] >= 13000
    assert "Schema-Constrained Document-Level Event Extraction" in full_status["successful_queries"]["query_17"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_17"]["artifact_files"]["final_report.md"]["bytes"] >= 15000
    assert "Uncertainty Communication Format" in full_status["successful_queries"]["query_18"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_18"]["artifact_files"]["final_report.md"]["bytes"] >= 17000
    assert "CommentTrojan" in full_status["successful_queries"]["query_22"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_22"]["artifact_files"]["final_report.md"]["bytes"] >= 15000
    assert "DeCIR-RAG" in full_status["successful_queries"]["query_24"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_24"]["artifact_files"]["final_report.md"]["bytes"] >= 22000
    assert "Conflict-Aware Multi-Hop Reasoning" in full_status["successful_queries"]["query_25"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_25"]["artifact_files"]["final_report.md"]["bytes"] >= 17000
    assert "Dynamic Alignment-based Curriculum Selection" in full_status["successful_queries"]["query_26"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_26"]["artifact_files"]["final_report.md"]["bytes"] >= 14000
    assert "UniAudio-MoE" in full_status["successful_queries"]["query_30"]["final_report"]["title"]
    assert full_status["successful_queries"]["query_30"]["artifact_files"]["final_report.md"]["bytes"] >= 18000
    assert full_status["audit"]["counts"]["success"] == 30
    assert full_status["audit"]["counts"].get("timeout", 0) == 0
    assert full_status["audit"]["counts"].get("failed", 0) == 0
    assert "missing" not in full_status["audit"]["counts"]
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
    full_audit_text = (ROOT / "audit_full_trajectories.py").read_text(encoding="utf-8")
    paper_level_audit_text = (ROOT / "audit_paper_level_completion.py").read_text(
        encoding="utf-8"
    )
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
    assert "response_region" in full_audit_text, "full trajectory audit may classify echoed prompts"
    assert "Idle timed out after" in full_audit_text, "full trajectory audit does not detect idle timeouts"
    assert "Table 2 human idea-generation evaluation" in paper_level_audit_text
    assert "Figure 2 code-execution success analysis" in paper_level_audit_text
    assert "schema_report" in paper_level_audit_text
    assert "paper-level reproduction goal remains incomplete" in paper_level_audit_text
    for needle in [
        "Verified Locally",
        "Not Yet Paper-Level Reproduction",
        "DeepSeek-backed EvoScientist proposal-only outputs exist",
        "Target-system output coverage is complete for proposal-only mode",
        "Replacement-baseline judge pipeline is complete",
        "Replacement baseline protocol is pinned",
        "Virtual Scientist baseline probe is recorded",
        "AI-Researcher baseline probe is recorded",
        "InternAgent baseline probe is recorded",
        "InternAgent QA runbook is executable",
        "InternAgent query-01 replacement smoke is complete",
        "AI Scientist-v2 baseline probe is recorded",
        "AI Scientist-v2 ideation runbook is executable",
        "Hypogenic baseline probe is recorded",
        "Novix baseline probe is recorded",
        "K-Dense baseline probe is recorded",
        "Baseline readiness matrix is recorded",
        "Baseline rerun manifest is recorded",
        "Paper-level non-Table-1 artifact schemas are pinned",
        "Human-label aggregation is executable",
        "Ablation aggregation is executable",
        "Code-execution aggregation is executable",
        "Paper reproduction action plan is executable",
        "EvoScientist CLI outputs are normalized before judging",
        "Full trajectory audit is executable",
        "Full trajectory reruns are isolated by default",
        "30 success, 0 timeout, 0 failed, 0 missing",
        "full tool-enabled DeepSeek-backed sweep for all 30 paper queries",
        "Full-trajectory coverage no longer needs another rerun",
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

        imported_jsonl = tmp_path / "imported.jsonl"
        imported_jsonl.write_text(
            json.dumps({
                "query_id": 1,
                "answer": "Imported baseline proposal with method, benchmark, and ablation details.",
                "prompt": "Imported prompt",
            })
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "import_baseline_outputs.py"),
                "--system-name",
                "ImportedBaseline",
                "--source",
                str(imported_jsonl),
                "--source-format",
                "jsonl",
                "--output-root",
                str(systems),
                "--limit",
                "1",
                "--min-chars",
                "20",
                "--strict",
            ],
            check=True,
        )
        imported_answer = systems / "ImportedBaseline" / "query_01" / "answer.txt"
        assert imported_answer.is_file()
        imported_judge_inputs = tmp_path / "imported_judge_inputs.jsonl"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build_pairwise_judge_inputs.py"),
                "--systems-root",
                str(systems),
                "--baseline",
                "ImportedBaseline",
                "--output",
                str(imported_judge_inputs),
                "--limit",
                "1",
            ],
            check=True,
        )
        assert len(imported_judge_inputs.read_text(encoding="utf-8").splitlines()) == 2

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

        human_inputs = tmp_path / "human_inputs.jsonl"
        human_inputs.write_text(
            json.dumps(
                {
                    "comparison_id": "h01",
                    "query_id": 1,
                    "baseline": "BaselineA",
                    "assistant_1_system": "EvoScientist",
                    "assistant_2_system": "BaselineA",
                    "answer_a": "Detailed proposal",
                    "answer_b": "Generic proposal",
                    "dimensions": ["Clarity", "Novelty", "Feasibility", "Relevance"],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        human_labels = tmp_path / "human_labels.jsonl"
        human_labels.write_text(
            "\n".join(
                json.dumps(
                    {
                        "comparison_id": "h01",
                        "annotator_id": "ann1",
                        "dimension": dim,
                        "winner": "assistant_1",
                    }
                )
                for dim in ["Clarity", "Novelty", "Feasibility", "Relevance"]
            )
            + "\n",
            encoding="utf-8",
        )
        human_aggregate = tmp_path / "human_aggregate.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "aggregate_human_labels.py"),
                "--inputs",
                str(human_inputs),
                "--labels",
                str(human_labels),
                "--output-csv",
                str(tmp_path / "human_aggregate.csv"),
                "--output-json",
                str(human_aggregate),
                "--strict",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        human_summary = json.loads(human_aggregate.read_text(encoding="utf-8"))
        assert human_summary["baselines"]["BaselineA"]["avg_gap"] == 100.0

        ablations_root = tmp_path / "ablations"
        for variant in ["-IDE", "-IVE", "-all"]:
            variant_root = ablations_root / variant
            variant_root.mkdir(parents=True)
            (variant_root / "judge_outputs.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "comparison_id": f"q01__{variant}__vs__EvoScientist",
                                "query_id": 1,
                                "assistant_1_system": variant,
                                "assistant_2_system": "EvoScientist",
                                "assistant_1": {
                                    "Clarity": 6,
                                    "Novelty": 6,
                                    "Feasibility": 6,
                                    "Relevance": 6,
                                },
                                "assistant_2": {
                                    "Clarity": 8,
                                    "Novelty": 8,
                                    "Feasibility": 8,
                                    "Relevance": 8,
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "comparison_id": f"q01__EvoScientist__vs__{variant}",
                                "query_id": 1,
                                "assistant_1_system": "EvoScientist",
                                "assistant_2_system": variant,
                                "assistant_1": {
                                    "Clarity": 8,
                                    "Novelty": 8,
                                    "Feasibility": 8,
                                    "Relevance": 8,
                                },
                                "assistant_2": {
                                    "Clarity": 6,
                                    "Novelty": 6,
                                    "Feasibility": 6,
                                    "Relevance": 6,
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
        ablation_combined = tmp_path / "ablation_combined.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "aggregate_ablation_results.py"),
                "--artifacts-root",
                str(ablations_root),
                "--combined-json",
                str(ablation_combined),
                "--combined-csv",
                str(tmp_path / "ablation_combined.csv"),
                "--strict",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        ablation_summary = json.loads((ablations_root / "-IDE" / "aggregate.json").read_text(encoding="utf-8"))
        assert ablation_summary["baselines"]["-IDE vs EvoScientist"]["avg_gap"] == -100.0
        ablation_combined_summary = json.loads(ablation_combined.read_text(encoding="utf-8"))
        assert set(ablation_combined_summary["variants"]) == {"-IDE", "-IVE", "-all"}
        assert "-IDE vs EvoScientist" in ablation_combined_summary["baselines"]

        execution_logs = tmp_path / "execution_logs.jsonl"
        execution_logs.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "trajectory_id": "t1",
                            "stage": 1,
                            "attempt_id": "a1",
                            "success": True,
                            "evolution_state": "before",
                        }
                    ),
                    json.dumps(
                        {
                            "trajectory_id": "t2",
                            "stage": 1,
                            "attempt_id": "a1",
                            "success": False,
                            "evolution_state": "before",
                        }
                    ),
                    json.dumps(
                        {
                            "trajectory_id": "t3",
                            "stage": "stage_3",
                            "attempt_id": "a1",
                            "success": "yes",
                            "evolution_state": "after",
                        }
                    ),
                    json.dumps(
                        {
                            "trajectory_id": "t4",
                            "stage": "stage_3",
                            "attempt_id": "a1",
                            "success": "success",
                            "evolution_state": "after",
                        }
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        execution_summary_path = tmp_path / "execution_summary.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "aggregate_code_execution.py"),
                "--logs",
                str(execution_logs),
                "--output-json",
                str(execution_summary_path),
                "--output-csv",
                str(tmp_path / "execution_summary.csv"),
                "--strict",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        execution_summary = json.loads(execution_summary_path.read_text(encoding="utf-8"))
        assert execution_summary["before_evolution_pct"] == 50.0
        assert execution_summary["after_evolution_pct"] == 100.0
        assert execution_summary["stage3_after_evolution_pct"] == 100.0

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

        matching_figure2_path = tmp_path / "matching_figure2.json"
        matching_figure2_path.write_text(
            json.dumps(reported["figure2_code_execution"], indent=2),
            encoding="utf-8",
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "compare_reproduction_to_paper.py"),
                "--actual-json",
                str(matching_figure2_path),
                "--section",
                "figure2_code_execution",
                "--require-all",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        plan_json = tmp_path / "paper_reproduction_action_plan.json"
        plan_md = tmp_path / "paper_reproduction_action_plan.md"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build_paper_reproduction_plan.py"),
                "--output-json",
                str(plan_json),
                "--output-md",
                str(plan_md),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        generated_plan = json.loads(plan_json.read_text(encoding="utf-8"))
        assert generated_plan["status"] == "incomplete"
        assert generated_plan["action_count"] == action_plan["action_count"]
        assert "'Virtual Scientist'" in plan_md.read_text(encoding="utf-8")

        runbook_json = tmp_path / "internagent_qa_runbook.json"
        runbook_md = tmp_path / "internagent_qa_runbook.md"
        runbook_sh = tmp_path / "internagent_qa_runbook.sh"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build_internagent_qa_runbook.py"),
                "--output-json",
                str(runbook_json),
                "--output-md",
                str(runbook_md),
                "--output-sh",
                str(runbook_sh),
                "--limit",
                "2",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        generated_runbook = json.loads(runbook_json.read_text(encoding="utf-8"))
        assert generated_runbook["query_count"] == 2
        assert runbook_sh.read_text(encoding="utf-8").count("python launch.py --mode qa") == 2

        ai_scientist_tmp_root = tmp_path / "ai_scientist_runbook"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build_ai_scientist_v2_ideation_runbook.py"),
                "--output-root",
                str(ai_scientist_tmp_root),
                "--output-jsonl",
                str(tmp_path / "ai_scientist_import.jsonl"),
                "--limit",
                "2",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        generated_ai_scientist = json.loads(
            (ai_scientist_tmp_root / "ai_scientist_v2_ideation_runbook.json").read_text(encoding="utf-8")
        )
        assert generated_ai_scientist["query_count"] == 2
        assert (ai_scientist_tmp_root / "topics" / "query_02.md").is_file()
        assert (
            ai_scientist_tmp_root / "run_ai_scientist_v2_ideation.sh"
        ).read_text(encoding="utf-8").count("perform_ideation_temp_free.py") == 2

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
