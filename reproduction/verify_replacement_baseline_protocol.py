#!/usr/bin/env python3
"""Validate the replacement-baseline protocol document and current artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import audit_reproduction_artifacts as artifact_audit


ROOT = Path(__file__).resolve().parent
PROTOCOL_JSON = ROOT / "replacement_baseline_protocol.json"
PROTOCOL_MD = ROOT / "replacement_baseline_protocol.md"
ARTIFACTS = ROOT / "artifacts"


def main() -> None:
    protocol = json.loads(PROTOCOL_JSON.read_text(encoding="utf-8"))
    assert protocol["query_set"]["query_count"] == 30
    assert protocol["query_set"]["require_verbatim_query"] is True
    assert protocol["judge_protocol"]["swapped_order"] is True
    assert protocol["judge_protocol"]["records_per_baseline"] == 60
    assert protocol["judge_protocol"]["paper_exact_judge"] == "gemini-3-flash"
    assert protocol["judge_protocol"]["replacement_judge"] == "deepseek-v4-flash"
    assert "Direct-DeepSeek" in [item["name"] for item in protocol["candidate_baselines"]]
    assert any(item["status"] == "completed_replacement_baseline" for item in protocol["candidate_baselines"])
    assert all(not item["paper_exact"] for item in protocol["candidate_baselines"])

    queries = artifact_audit.load_queries()
    direct_outputs = artifact_audit.audit_system_outputs(
        systems_root=ARTIFACTS / "idea_outputs",
        systems=["EvoScientist", "Direct-DeepSeek"],
        queries=queries,
    )
    assert direct_outputs["complete"], direct_outputs

    expected_ids = artifact_audit.expected_comparison_ids(
        queries=queries,
        target_system="EvoScientist",
        baselines=["Direct-DeepSeek"],
        swapped=True,
    )
    judge_inputs = artifact_audit.audit_jsonl_coverage(
        path=ARTIFACTS / "judge_inputs" / "evosci_clean_vs_direct_deepseek.jsonl",
        expected_ids=expected_ids,
    )
    judge_outputs = artifact_audit.audit_jsonl_coverage(
        path=ARTIFACTS / "judge_outputs" / "evosci_clean_vs_direct_deepseek_deepseek.jsonl",
        expected_ids=expected_ids,
    )
    aggregate = artifact_audit.audit_aggregate_table(
        path=ARTIFACTS / "tables" / "evosci_clean_vs_direct_deepseek_deepseek.json",
        baselines=["Direct-DeepSeek"],
    )
    assert judge_inputs["complete"], judge_inputs
    assert judge_outputs["complete"], judge_outputs
    assert aggregate["complete"], aggregate

    text = PROTOCOL_MD.read_text(encoding="utf-8")
    for needle in [
        "exact Table 1 reproduction",
        "Every selected baseline has 30 non-empty",
        "60 swapped records per selected baseline",
        "paper-exact or replacement-only",
    ]:
        assert needle in text, f"missing protocol text: {needle}"

    print(json.dumps({
        "status": "ok",
        "replacement_protocol": str(PROTOCOL_JSON),
        "completed_replacement_baseline": "Direct-DeepSeek",
        "query_count": len(queries),
        "judge_records": judge_outputs["records"],
    }, indent=2))


if __name__ == "__main__":
    main()
