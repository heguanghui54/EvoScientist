#!/usr/bin/env python3
"""Append reproduction appendices to the 30 EvoScientist final reports."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "artifacts" / "remote_fetch" / "full_trajectories" / "EvoScientist"
REPORT_JSON = ROOT / "final_report_appendix_pass.json"
REPORT_MD = ROOT / "final_report_appendix_pass.md"
APPENDIX_TITLE = "## Appendix: Reproducibility and Evaluation Notes"
APPENDIX_RE = re.compile(r"^#{1,3}\s+(appendix|appendices|附录)\b", re.IGNORECASE | re.MULTILINE)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_queries() -> dict[int, dict[str, Any]]:
    return {
        int(item["id"]): item
        for item in json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]
    }


def existing_artifact_lines(query_dir: Path) -> list[str]:
    names = ["final_report.md", "prompt.txt", "query.json", "stdout.txt", "stderr.txt"]
    lines = []
    for name in names:
        path = query_dir / name
        if path.is_file():
            lines.append(f"- `{rel(path)}` ({path.stat().st_size} bytes)")
    return lines


def appendix_for(query: dict[str, Any], query_dir: Path) -> str:
    query_id = int(query["id"])
    artifact_lines = existing_artifact_lines(query_dir)
    return f"""
{APPENDIX_TITLE}

### A. Query and Writing Scope

This appendix was added as a final paper-writing pass during the local reproduction. It documents the reproduction context for this generated proposal and does not change the main proposal text, experimental outputs, judge outputs, or aggregate scores.

| Field | Value |
|---|---|
| Query id | {query_id:02d} |
| Topic | {query["topic"]} |
| Original user goal | {query["goal"]} |
| Source report | `{rel(query_dir / "final_report.md")}` |

### B. Local Artifacts for This Report

{chr(10).join(artifact_lines)}

The browsable HTML preview for this report is generated from the Markdown source by `reproduction/build_all_paper_previews.py`. The all-report index is `reproduction/artifacts/paper_previews/all_evoscientist_reports/index.html`.

### C. Evaluation Protocol Used in This Reproduction

The local reproduction package evaluates the EvoScientist public final reports against replacement or proxy baseline outputs where direct paper-exact baseline outputs were not publicly available. The user-scoped Table 1 replacement uses 30 queries, 7 baseline systems, and 2 swapped comparison orders, yielding 420 Monica/Gemini judge records. The judged dimensions are Clarity, Novelty, Feasibility, and Relevance.

For the Table 2 style check, this reproduction uses Monica/Gemini surrogate labels over 120 inputs and 1,440 dimension-level labels. Formal PhD human labels were intentionally left outside the current user scope. The resulting evidence should therefore be read as a reproduction-oriented proxy, not as a paper-exact human evaluation.

### D. Limits and Non-Claims

- This appendix is local documentation for reproducibility; it is not a new EvoScientist generation step.
- The pass does not add new experimental evidence beyond artifacts already present in the reproduction directory.
- Paper-exact reproduction remains blocked by missing author-side raw baseline outputs, original Gemini judge transcripts, and formal human-label artifacts.
- Claims in the main generated proposal remain those of the generated report; this appendix only records how the local reproduction package stores and evaluates it.

### E. Verification Commands

```bash
.venv/bin/python reproduction/verify_user_scope_reproduction.py --strict
.venv/bin/python reproduction/verify_reproduction_assets.py
bash reproduction/run_preflight.sh
```
""".strip()


def markdown_report(records: list[dict[str, Any]]) -> str:
    appended = sum(1 for item in records if item["action"] == "appended")
    skipped = sum(1 for item in records if item["action"] == "already_had_appendix")
    rows = [
        "| Query | Topic | Action | Final report bytes |",
        "|---|---|---|---:|",
    ]
    for item in records:
        rows.append(
            f"| {item['query_id']:02d} | {item['topic']} | {item['action']} | {item['bytes_after']} |"
        )
    return "\n".join(
        [
            "# Final Report Appendix Pass",
            "",
            "This pass only updates the final paper-writing layer by appending a reproducibility appendix to EvoScientist final reports that lacked one.",
            "",
            f"- Reports checked: {len(records)}",
            f"- Appendices appended: {appended}",
            f"- Reports already containing an appendix: {skipped}",
            "- Experimental outputs changed: no",
            "- Judge outputs changed: no",
            "",
            *rows,
        ]
    )


def main() -> None:
    queries = load_queries()
    records: list[dict[str, Any]] = []
    for query_id in range(1, 31):
        query = queries[query_id]
        query_dir = SOURCE_ROOT / f"query_{query_id:02d}"
        report_path = query_dir / "final_report.md"
        text = report_path.read_text(encoding="utf-8")
        before = report_path.stat().st_size
        if APPENDIX_RE.search(text):
            action = "already_had_appendix"
            updated = text
        else:
            updated = text.rstrip() + "\n\n---\n\n" + appendix_for(query, query_dir) + "\n"
            report_path.write_text(updated, encoding="utf-8")
            action = "appended"
        records.append(
            {
                "query_id": query_id,
                "topic": query["topic"],
                "action": action,
                "path": rel(report_path),
                "bytes_before": before,
                "bytes_after": report_path.stat().st_size,
                "has_appendix_after": bool(APPENDIX_RE.search(updated)),
            }
        )

    payload = {
        "status": "complete",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "final_paper_writing_appendix_only",
        "reports_checked": len(records),
        "appendices_appended": sum(1 for item in records if item["action"] == "appended"),
        "reports_already_with_appendix": sum(
            1 for item in records if item["action"] == "already_had_appendix"
        ),
        "experimental_outputs_changed": False,
        "judge_outputs_changed": False,
        "records": records,
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(markdown_report(records) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
