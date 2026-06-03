#!/usr/bin/env python3
"""Import external baseline answers into the shared reproduction layout.

Supported sources:
- JSONL records with query_id/id and answer/output/text fields.
- A directory containing query_01.md, query_01.txt, 01.md, 01.txt, etc.

The output layout is compatible with build_pairwise_judge_inputs.py:
artifacts/idea_outputs/{system}/query_XX/answer.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = ROOT / "artifacts" / "idea_outputs"
ANSWER_KEYS = ["answer", "output", "text", "proposal", "content"]
PROMPT_KEYS = ["prompt", "input", "question"]


def load_queries() -> list[dict[str, Any]]:
    return json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]


def query_id_from_record(record: dict[str, Any]) -> int:
    for key in ["query_id", "id", "qid"]:
        if key in record:
            return int(record[key])
    raise ValueError(f"record missing query id: {record}")


def text_from_record(record: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def load_jsonl(path: Path) -> dict[int, dict[str, str]]:
    outputs: dict[int, dict[str, str]] = {}
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            query_id = query_id_from_record(record)
            answer = text_from_record(record, ANSWER_KEYS)
            if not answer:
                raise ValueError(f"record {line_number} missing answer field")
            prompt = text_from_record(record, PROMPT_KEYS)
            outputs[query_id] = {"answer": answer, "prompt": prompt}
    return outputs


def candidate_paths(source_dir: Path, query_id: int) -> list[Path]:
    stems = [
        f"query_{query_id:02d}",
        f"query_{query_id}",
        f"q{query_id:02d}",
        f"q{query_id}",
        f"{query_id:02d}",
        str(query_id),
    ]
    suffixes = [".md", ".txt", ".json"]
    return [source_dir / f"{stem}{suffix}" for stem in stems for suffix in suffixes]


def read_directory_item(path: Path) -> dict[str, str]:
    if path.suffix == ".json":
        record = json.loads(path.read_text(encoding="utf-8"))
        answer = text_from_record(record, ANSWER_KEYS)
        prompt = text_from_record(record, PROMPT_KEYS)
        if not answer:
            raise ValueError(f"{path} missing answer field")
        return {"answer": answer, "prompt": prompt}
    return {"answer": path.read_text(encoding="utf-8").strip(), "prompt": ""}


def load_directory(path: Path, queries: list[dict[str, Any]]) -> dict[int, dict[str, str]]:
    outputs = {}
    for query in queries:
        for candidate in candidate_paths(path, query["id"]):
            if candidate.is_file() and candidate.read_text(encoding="utf-8").strip():
                outputs[query["id"]] = read_directory_item(candidate)
                break
    return outputs


def write_outputs(
    *,
    system_name: str,
    outputs: dict[int, dict[str, str]],
    queries: list[dict[str, Any]],
    output_root: Path,
    min_chars: int,
    overwrite: bool,
) -> dict[str, Any]:
    system_dir = output_root / system_name
    system_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "runner": "import_baseline_outputs.py",
        "system_name": system_name,
        "query_count": len(queries),
        "min_chars": min_chars,
        "outputs": [],
    }
    by_id = {query["id"]: query for query in queries}
    written = 0
    skipped = 0
    missing = []
    too_short = []
    for query_id in sorted(by_id):
        qdir = system_dir / f"query_{query_id:02d}"
        answer_path = qdir / "answer.txt"
        if answer_path.is_file() and answer_path.read_text(encoding="utf-8").strip() and not overwrite:
            skipped += 1
            manifest["outputs"].append({"id": query_id, "status": "skipped", "dir": str(qdir)})
            continue
        item = outputs.get(query_id)
        if not item:
            missing.append(query_id)
            manifest["outputs"].append({"id": query_id, "status": "missing", "dir": str(qdir)})
            continue
        answer = item["answer"].strip()
        if len(answer) < min_chars:
            too_short.append({"query_id": query_id, "chars": len(answer)})
            manifest["outputs"].append({"id": query_id, "status": "too_short", "dir": str(qdir)})
            continue
        qdir.mkdir(parents=True, exist_ok=True)
        answer_path.write_text(answer + "\n", encoding="utf-8")
        prompt = item.get("prompt") or by_id[query_id]["goal"]
        (qdir / "prompt.txt").write_text(prompt.strip() + "\n", encoding="utf-8")
        (qdir / "query.json").write_text(json.dumps(by_id[query_id], indent=2), encoding="utf-8")
        written += 1
        manifest["outputs"].append({"id": query_id, "status": "ok", "dir": str(qdir)})
    manifest["summary"] = {
        "written": written,
        "skipped": skipped,
        "missing_query_ids": missing,
        "too_short": too_short,
        "complete": not missing and not too_short and written + skipped == len(queries),
    }
    (system_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system-name", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-format", choices=["jsonl", "directory"], required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--min-chars", type=int, default=200)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    queries = load_queries()
    if args.limit is not None:
        queries = queries[: args.limit]

    if args.source_format == "jsonl":
        outputs = load_jsonl(args.source)
    else:
        outputs = load_directory(args.source, queries)

    manifest = write_outputs(
        system_name=args.system_name,
        outputs=outputs,
        queries=queries,
        output_root=args.output_root,
        min_chars=args.min_chars,
        overwrite=args.overwrite,
    )
    summary = manifest["summary"]
    print(json.dumps({
        "status": "complete" if summary["complete"] else "incomplete",
        "system_name": args.system_name,
        **summary,
    }, indent=2))
    if args.strict and not summary["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
