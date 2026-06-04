#!/usr/bin/env python3
"""Build a current action plan for paper-level EvoScientist reproduction.

The completion audit answers "is the paper reproduced yet?". This companion
script answers "what exact evidence and commands remain next?" without treating
replacement-baseline results as paper-exact evidence.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any

import audit_paper_level_completion as paper_audit


ROOT = Path(__file__).resolve().parent
DEFAULT_ARTIFACTS = ROOT / "artifacts"
DEFAULT_OUTPUT_JSON = ROOT / "paper_reproduction_action_plan.json"
DEFAULT_OUTPUT_MD = ROOT / "paper_reproduction_action_plan.md"
PAPER_BASELINES = [
    "Virtual Scientist",
    "AI-Researcher",
    "InternAgent",
    "AI Scientist-v2",
    "Hypogenic",
    "Novix",
    "K-Dense",
]


def slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def shell_quote(value: str) -> str:
    return shlex.quote(value)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def table1_actions(components: dict[str, Any], protocol: dict[str, Any]) -> list[dict[str, Any]]:
    table1 = components["table1_llm_idea_generation"]
    systems = table1["system_outputs"]["systems"]
    commands = protocol.get("commands", {})
    actions = []
    missing_baselines = [
        baseline
        for baseline in PAPER_BASELINES
        if not systems.get(baseline, {}).get("complete")
    ]
    for baseline in missing_baselines:
        baseline_slug = slug(baseline)
        quoted_baseline = shell_quote(baseline)
        actions.append(
            {
                "component": "table1_llm_idea_generation",
                "kind": "baseline_output_import_or_generation",
                "system": baseline,
                "required_evidence": f"30 answer.txt files under reproduction/artifacts/idea_outputs/{baseline}/",
                "paper_exact": True,
                "command_templates": [
                    commands.get("import_baseline_jsonl_template", "").replace("{baseline}", quoted_baseline),
                    commands.get("import_baseline_directory_template", "").replace("{baseline}", quoted_baseline),
                    commands.get("build_judge_inputs_template", "")
                    .replace("{baseline}", quoted_baseline)
                    .replace("{baseline_slug}", baseline_slug),
                    commands.get("run_replacement_judge_template", "")
                    .replace("{baseline_slug}", baseline_slug),
                    commands.get("aggregate_template", "").replace("{baseline_slug}", baseline_slug),
                    commands.get("audit_template", "")
                    .replace("{baseline}", quoted_baseline)
                    .replace("{baseline_slug}", baseline_slug),
                ],
            }
        )
        if baseline == "Virtual Scientist":
            actions[-1]["probe"] = "reproduction/virtual_scientist_baseline_probe.json"
            actions[-1]["note"] = (
                "Current probe maps Virtual Scientist to VirSci/Virtual-Scientists. "
                "It is a runnable open-source collaboration platform, but not a drop-in "
                "runner for the 30 recovered EvoScientist queries."
            )
            actions[-1]["replacement_run_template"] = [
                "git clone https://github.com/open-sciencelab/Virtual-Scientists $HOME/research/Virtual-Scientists",
                "# Download the AMiner-derived Papers, Embeddings, Authors, and adjacency data linked in the VirSci README.",
                "# Patch sci_platform/sci_platform.py paths and run Ollama llama3.1/mxbai-embed-large under a pinned adapter protocol.",
                "# Extract generated idea/abstract fields from team_info/*_dialogue.json into outputs/evoscientist_table1_queries/virtual_scientist/query_XX.md",
                ".venv/bin/python reproduction/import_baseline_outputs.py --system-name 'Virtual Scientist' --source $HOME/research/Virtual-Scientists/outputs/evoscientist_table1_queries/virtual_scientist --source-format directory --output-root reproduction/artifacts/idea_outputs --strict",
            ]
        if baseline == "AI-Researcher":
            actions[-1]["probe"] = "reproduction/ai_researcher_baseline_probe.json"
            actions[-1]["note"] = (
                "Current probe found the public AI-Researcher runner is benchmark-instance based, "
                "not a drop-in runner for the 30 recovered EvoScientist queries."
            )
        if baseline == "InternAgent":
            actions[-1]["probe"] = "reproduction/internagent_baseline_probe.json"
            actions[-1]["note"] = (
                "Current probe found InternAgent has a one-shot QA CLI suitable for a replacement "
                "baseline rerun, but it is not paper-exact raw Table 1 evidence."
            )
            actions[-1]["replacement_run_template"] = [
                ".venv/bin/python reproduction/build_internagent_qa_runbook.py",
                "bash /path/to/EvoScientist/reproduction/internagent_qa_runbook.sh",
                ".venv/bin/python reproduction/import_baseline_outputs.py --system-name InternAgent --source $HOME/research/InternAgent/outputs/evoscientist_table1_queries/internagent --source-format directory --output-root reproduction/artifacts/idea_outputs --strict",
            ]
        if baseline == "AI Scientist-v2":
            actions[-1]["probe"] = "reproduction/ai_scientist_v2_baseline_probe.json"
            actions[-1]["note"] = (
                "Current probe found AI Scientist-v2 has an ideation CLI suitable for a replacement "
                "baseline adapter, but it is not paper-exact raw Table 1 evidence."
            )
            actions[-1]["replacement_run_template"] = [
                ".venv/bin/python reproduction/build_ai_scientist_v2_ideation_runbook.py",
                "bash /path/to/EvoScientist/reproduction/ai_scientist_v2_ideation_runbook/run_ai_scientist_v2_ideation.sh",
                ".venv/bin/python reproduction/convert_ai_scientist_v2_ideation_outputs.py",
                ".venv/bin/python reproduction/import_baseline_outputs.py --system-name 'AI Scientist-v2' --source reproduction/ai_scientist_v2_ideation_import_template.jsonl --source-format jsonl --output-root reproduction/artifacts/idea_outputs --strict",
            ]
        if baseline == "Hypogenic":
            actions[-1]["probe"] = "reproduction/hypogenic_baseline_probe.json"
            actions[-1]["note"] = (
                "Current probe found Hypogenic has a hosted Assistant/IdeaHub/Arena "
                "platform and generated competition repositories, but no public batch "
                "runner or raw Table 1 outputs."
            )
            actions[-1]["replacement_run_template"] = [
                "# With Hypogenic account access: open https://hypogenic.ai/chat under a pinned browser/profile state.",
                "# Submit one recovered query per fresh Assistant session and capture the final answer plus session metadata.",
                "# Save outputs as $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic/query_XX.md",
                ".venv/bin/python reproduction/import_baseline_outputs.py --system-name Hypogenic --source $HOME/research/hypogenic/outputs/evoscientist_table1_queries/hypogenic --source-format directory --output-root reproduction/artifacts/idea_outputs --strict",
            ]
        if baseline == "Novix":
            actions[-1]["probe"] = "reproduction/novix_baseline_probe.json"
            actions[-1]["note"] = (
                "Current probe found Novix is a hosted UI adapter candidate linked to "
                "AI-Researcher, with visible login/session/task endpoints but no public "
                "batch runner or raw Table 1 outputs."
            )
            actions[-1]["replacement_run_template"] = [
                "# With Novix account access: open https://novix.science/chat under a pinned browser/profile state.",
                "# Submit one recovered query per fresh session and capture the final assistant answer plus session metadata.",
                "# Save outputs as $HOME/research/novix/outputs/evoscientist_table1_queries/novix/query_XX.md",
                ".venv/bin/python reproduction/import_baseline_outputs.py --system-name Novix --source $HOME/research/novix/outputs/evoscientist_table1_queries/novix --source-format directory --output-root reproduction/artifacts/idea_outputs --strict",
            ]
        if baseline == "K-Dense":
            actions[-1]["probe"] = "reproduction/k_dense_baseline_probe.json"
            actions[-1]["note"] = (
                "Current probe found K-Dense has a BYOK local Web/API adapter through ADK "
                "`/run_sse`, but it needs a pinned Python 3.13/OpenRouter/Gemini CLI setup "
                "and is not paper-exact raw Table 1 evidence."
            )
            actions[-1]["replacement_run_template"] = [
                "git clone https://github.com/K-Dense-AI/k-dense-byok $HOME/research/k-dense-byok && cd $HOME/research/k-dense-byok && git checkout 593c49b8e79c704c5979ec81c49f1791b5114083",
                "./start.sh",
                "# In a separate adapter process: create one ADK session per query, POST each query to /run_sse, and save final assistant text as outputs/evoscientist_table1_queries/k_dense/query_XX.md",
                ".venv/bin/python reproduction/import_baseline_outputs.py --system-name K-Dense --source $HOME/research/k-dense-byok/outputs/evoscientist_table1_queries/k_dense --source-format directory --output-root reproduction/artifacts/idea_outputs --strict",
            ]
    if not table1["judge_inputs"]["complete"] or not table1["judge_outputs"]["complete"]:
        actions.append(
            {
                "component": "table1_llm_idea_generation",
                "kind": "paper_judge_completion",
                "required_evidence": "420 swapped pairwise records plus Gemini-3-flash judge outputs",
                "paper_exact": True,
                "commands": [
                    ".venv/bin/python reproduction/build_pairwise_judge_inputs.py --systems-root reproduction/artifacts/idea_outputs --baseline 'Virtual Scientist' --baseline AI-Researcher --baseline InternAgent --baseline 'AI Scientist-v2' --baseline Hypogenic --baseline Novix --baseline K-Dense --output reproduction/artifacts/judge_inputs/results.jsonl",
                    ".venv/bin/python reproduction/run_llm_judge.py --provider google --model gemini-3-flash --input reproduction/artifacts/judge_inputs/results.jsonl --output reproduction/artifacts/judge_outputs/results.jsonl --resume",
                    ".venv/bin/python reproduction/aggregate_judge_results.py --input reproduction/artifacts/judge_outputs/results.jsonl --output-csv reproduction/artifacts/tables/idea_generation_win_tie_lose.csv --output-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json",
                    ".venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/tables/idea_generation_win_tie_lose.json --section table1_llm_idea_generation --require-all",
                ],
            }
        )
    return actions


def table2_actions(components: dict[str, Any]) -> list[dict[str, Any]]:
    table2 = components["table2_human_idea_generation"]
    if table2["complete"]:
        return []
    return [
        {
            "component": "table2_human_idea_generation",
            "kind": "human_label_import",
            "missing_files": table2["missing_files"],
            "required_evidence": "inputs.jsonl, labels.jsonl, and aggregate.json for three PhD-level annotators",
            "commands": [
                ".venv/bin/python reproduction/aggregate_human_labels.py --inputs reproduction/artifacts/human_evaluation/inputs.jsonl --labels reproduction/artifacts/human_evaluation/labels.jsonl --output-csv reproduction/artifacts/human_evaluation/aggregate.csv --output-json reproduction/artifacts/human_evaluation/aggregate.json --strict",
            ],
        }
    ]


def table3_actions(components: dict[str, Any]) -> list[dict[str, Any]]:
    table3 = components["table3_ablation_idea_generation"]
    if table3["complete"]:
        return []
    missing_variants = [
        name for name, item in table3["variants"].items() if not item["complete"]
    ]
    return [
        {
            "component": "table3_ablation_idea_generation",
            "kind": "ablation_variant_runs",
            "missing_variants": missing_variants,
            "required_evidence": "system_outputs_complete.json, judge_inputs.jsonl, judge_outputs.jsonl, and aggregate.json for -IDE, -IVE, and -all",
            "commands": [
                ".venv/bin/python reproduction/aggregate_ablation_results.py --artifacts-root reproduction/artifacts/ablations --combined-json reproduction/artifacts/ablations/combined_aggregate.json --combined-csv reproduction/artifacts/ablations/combined_aggregate.csv --strict",
                ".venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/ablations/combined_aggregate.json --section table3_ablation_idea_generation --require-all",
            ],
            "note": "The repository has no native ablation toggles yet; variant outputs must come from a paper-matched patch or imported raw ablation runs.",
        }
    ]


def figure2_actions(components: dict[str, Any]) -> list[dict[str, Any]]:
    figure2 = components["figure2_code_execution"]
    if figure2["complete"]:
        return []
    return [
        {
            "component": "figure2_code_execution",
            "kind": "code_execution_log_import",
            "missing_files": figure2["missing_files"],
            "required_evidence": "trajectories.jsonl, execution_logs.jsonl, and summary.json with before/after evolution success rates",
            "commands": [
                ".venv/bin/python reproduction/aggregate_code_execution.py --logs reproduction/artifacts/code_execution/execution_logs.jsonl --output-json reproduction/artifacts/code_execution/summary.json --output-csv reproduction/artifacts/code_execution/summary.csv --strict",
                ".venv/bin/python reproduction/compare_reproduction_to_paper.py --actual-json reproduction/artifacts/code_execution/summary.json --section figure2_code_execution --require-all",
            ],
        }
    ]


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    audit_args = argparse.Namespace(
        artifacts_root=args.artifacts_root,
        full_status=args.full_status,
        public_gap_report=args.public_gap_report,
        schema=args.schema,
        date=args.date,
    )
    audit = paper_audit.build_report(audit_args)
    protocol = load_json(args.replacement_protocol)
    gap_report = load_json(args.public_gap_report)
    readiness = load_json(ROOT / "baseline_readiness_matrix.json")
    components = audit["components"]
    actions = []
    actions.extend(table1_actions(components, protocol))
    actions.extend(table2_actions(components))
    actions.extend(table3_actions(components))
    actions.extend(figure2_actions(components))
    return {
        "date": args.date,
        "paper": "arXiv:2603.08127",
        "status": audit["status"],
        "action_count": len(actions),
        "actions": actions,
        "non_completion_reason": audit["blocking_items"],
        "public_artifact_gap_conclusion": gap_report.get("conclusion", ""),
        "baseline_readiness_counts": readiness.get("counts", {}),
        "baseline_readiness_matrix": "reproduction/baseline_readiness_matrix.json",
        "baseline_rerun_manifest": "reproduction/baseline_rerun_manifest.json",
        "final_gate": ".venv/bin/python reproduction/audit_paper_level_completion.py --strict",
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Paper Reproduction Action Plan",
        "",
        f"Date: {plan['date']}",
        f"Paper: {plan['paper']}",
        f"Current status: `{plan['status']}`",
        "",
        "This file lists the next evidence-producing steps needed before the",
        "paper-level completion audit can pass.",
        "",
        "## Actions",
        "",
    ]
    if not plan["actions"]:
        lines.append("No remaining actions; run the final gate.")
    for index, action in enumerate(plan["actions"], start=1):
        lines.extend(
            [
                f"### {index}. {action['component']} / {action['kind']}",
                "",
                f"Required evidence: {action['required_evidence']}",
                "",
            ]
        )
        for key in ["system", "missing_files", "missing_variants", "probe", "note"]:
            if key in action and action[key]:
                value = action[key]
                if isinstance(value, list):
                    value = ", ".join(value)
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        commands = action.get("replacement_run_template") or action.get("commands") or action.get("command_templates") or []
        commands = [cmd for cmd in commands if cmd]
        if commands:
            lines.extend(["", "Commands:", "", "```bash"])
            lines.extend(commands)
            lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Baseline Readiness",
            "",
            "Source: `reproduction/baseline_readiness_matrix.json`",
            "Rerun queue: `reproduction/baseline_rerun_manifest.json`",
            "",
        ]
    )
    for key, value in plan.get("baseline_readiness_counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Final Gate",
            "",
            "```bash",
            plan["final_gate"],
            "```",
            "",
            "## Why This Is Still Incomplete",
            "",
        ]
    )
    for item in plan["non_completion_reason"]:
        lines.append(f"- {item}")
    if plan["public_artifact_gap_conclusion"]:
        lines.extend(["", plan["public_artifact_gap_conclusion"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-root", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--full-status", type=Path, default=paper_audit.DEFAULT_FULL_STATUS)
    parser.add_argument("--public-gap-report", type=Path, default=paper_audit.DEFAULT_PUBLIC_GAP)
    parser.add_argument("--schema", type=Path, default=paper_audit.DEFAULT_SCHEMA)
    parser.add_argument("--replacement-protocol", type=Path, default=ROOT / "replacement_baseline_protocol.json")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--date", default="2026-06-04")
    args = parser.parse_args()

    plan = build_plan(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    args.output_md.write_text(render_markdown(plan), encoding="utf-8")
    print(json.dumps({"status": plan["status"], "action_count": plan["action_count"]}, indent=2))


if __name__ == "__main__":
    main()
