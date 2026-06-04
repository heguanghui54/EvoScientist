#!/usr/bin/env python3
"""Build browsable HTML previews for all 30 EvoScientist final reports."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "artifacts" / "remote_fetch" / "full_trajectories" / "EvoScientist"
OUTPUT_ROOT = ROOT / "artifacts" / "paper_previews" / "all_evoscientist_reports"
MANIFEST = OUTPUT_ROOT / "manifest.json"
INDEX = OUTPUT_ROOT / "index.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_queries() -> dict[int, dict[str, Any]]:
    return {
        int(item["id"]): item
        for item in json.loads((ROOT / "queries.json").read_text(encoding="utf-8"))["queries"]
    }


def title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def excerpt_from_markdown(text: str, limit: int = 320) -> str:
    chunks = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        if stripped.startswith(("-", "*", "|")):
            continue
        chunks.append(re.sub(r"[*_`]+", "", stripped))
        if sum(len(item) for item in chunks) > limit:
            break
    excerpt = " ".join(chunks).strip()
    return excerpt[: limit - 3] + "..." if len(excerpt) > limit else excerpt


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_code = False
    list_open = False
    table_open = False
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            if list_open:
                out.append("</ul>")
                list_open = False
            if table_open:
                out.append("</tbody></table>")
                table_open = False
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(esc(line))
            continue
        if not stripped:
            if list_open:
                out.append("</ul>")
                list_open = False
            if table_open:
                out.append("</tbody></table>")
                table_open = False
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            if not table_open:
                if list_open:
                    out.append("</ul>")
                    list_open = False
                out.append("<table><tbody>")
                table_open = True
            out.append("<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in cells) + "</tr>")
            continue
        if table_open:
            out.append("</tbody></table>")
            table_open = False
        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            if list_open:
                out.append("</ul>")
                list_open = False
            level = min(len(heading.group(1)), 4)
            out.append(f"<h{level}>{esc(heading.group(2))}</h{level}>")
            continue
        if stripped.startswith(("- ", "* ")):
            if not list_open:
                out.append("<ul>")
                list_open = True
            out.append(f"<li>{esc(stripped[2:])}</li>")
            continue
        if list_open:
            out.append("</ul>")
            list_open = False
        out.append(f"<p>{esc(stripped)}</p>")
    if in_code:
        out.append("</code></pre>")
    if list_open:
        out.append("</ul>")
    if table_open:
        out.append("</tbody></table>")
    return "\n".join(out)


def page_html(title: str, query: dict[str, Any], source_rel: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    body {{ margin: 0; background: #f7f8f8; color: #17191c; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.62; }}
    header {{ padding: 28px clamp(18px, 5vw, 72px); background: #fff; border-bottom: 1px solid #dce1e6; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 28px 18px 56px; }}
    article {{ background: #fff; border: 1px solid #dce1e6; border-radius: 8px; padding: clamp(18px, 4vw, 42px); }}
    h1 {{ margin: 0 0 10px; font-size: clamp(28px, 4vw, 46px); line-height: 1.1; letter-spacing: 0; }}
    h2 {{ margin-top: 30px; border-top: 1px solid #e7eaee; padding-top: 18px; letter-spacing: 0; }}
    h3, h4 {{ letter-spacing: 0; }}
    p, li, td {{ font-size: 15px; }}
    .meta {{ color: #606a73; display: grid; gap: 4px; }}
    a {{ color: #225f9f; }}
    table {{ border-collapse: collapse; width: 100%; overflow-wrap: anywhere; }}
    td {{ border: 1px solid #e1e5ea; padding: 8px; vertical-align: top; }}
    pre {{ white-space: pre-wrap; background: #f0f3f5; padding: 14px; border-radius: 6px; overflow-x: auto; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .nav {{ margin-bottom: 14px; }}
  </style>
</head>
<body>
  <header>
    <div class="nav"><a href="index.html">← All 30 reports</a></div>
    <h1>{esc(title)}</h1>
    <div class="meta">
      <div>Query {int(query["id"]):02d}: {esc(query["topic"])}</div>
      <div>{esc(query["goal"])}</div>
      <div>Source: <code>{esc(source_rel)}</code></div>
    </div>
  </header>
  <main><article>{body_html}</article></main>
</body>
</html>
"""


def index_html(records: list[dict[str, Any]]) -> str:
    cards = []
    for item in records:
        cards.append(
            f"""
            <a class="card" href="{esc(item['html'])}">
              <div class="qid">Query {int(item['query_id']):02d}</div>
              <h2>{esc(item['title'])}</h2>
              <p class="topic">{esc(item['topic'])}</p>
              <p>{esc(item['excerpt'])}</p>
            </a>
            """
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>All EvoScientist Final Reports</title>
  <style>
    body {{ margin: 0; background: #f7f8f8; color: #17191c; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    header {{ padding: 38px clamp(18px, 5vw, 72px); background: #fff; border-bottom: 1px solid #dce1e6; }}
    main {{ padding: 28px clamp(18px, 5vw, 72px) 56px; }}
    h1 {{ margin: 0 0 10px; font-size: clamp(32px, 5vw, 56px); line-height: 1.05; letter-spacing: 0; }}
    .lead {{ color: #606a73; max-width: 850px; line-height: 1.6; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .card {{ display: block; text-decoration: none; color: inherit; background: #fff; border: 1px solid #dce1e6; border-radius: 8px; padding: 16px; min-height: 220px; }}
    .card:hover {{ border-color: #8fb2d4; box-shadow: 0 8px 20px rgba(25, 45, 65, .08); }}
    .qid {{ color: #225f9f; font-weight: 800; font-size: 13px; }}
    h2 {{ font-size: 17px; line-height: 1.25; margin: 8px 0; letter-spacing: 0; }}
    p {{ color: #606a73; font-size: 14px; line-height: 1.5; }}
    .topic {{ color: #9a681b; font-weight: 700; }}
    a.back {{ color: #225f9f; }}
    @media (max-width: 980px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <a class="back" href="../../experiment_reproduction_report.html">← Back to visual report</a>
    <h1>All 30 EvoScientist final reports</h1>
    <p class="lead">这里列出 30 个 query 对应的 EvoScientist full-trajectory final_report。之前 HTML 报告只展示了两个 PDF 预览样例；完整 30 篇在这里。</p>
  </header>
  <main><div class="grid">{''.join(cards)}</div></main>
</body>
</html>
"""


def main() -> None:
    queries = load_queries()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for query_id in range(1, 31):
        source = SOURCE_ROOT / f"query_{query_id:02d}" / "final_report.md"
        text = source.read_text(encoding="utf-8")
        query = queries[query_id]
        title = title_from_markdown(text, f"EvoScientist Query {query_id:02d}")
        html_name = f"query_{query_id:02d}.html"
        html_path = OUTPUT_ROOT / html_name
        source_rel = str(source.relative_to(ROOT))
        html_path.write_text(
            "\n".join(
                line.rstrip()
                for line in page_html(title, query, source_rel, markdown_to_html(text)).splitlines()
            )
            + "\n",
            encoding="utf-8",
        )
        records.append(
            {
                "query_id": query_id,
                "topic": query["topic"],
                "goal": query["goal"],
                "title": title,
                "source": source_rel,
                "html": html_name,
                "bytes": source.stat().st_size,
                "excerpt": excerpt_from_markdown(text),
            }
        )
    INDEX.write_text("\n".join(line.rstrip() for line in index_html(records).splitlines()) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({"status": "complete", "count": len(records), "reports": records}, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "count": len(records), "index": str(INDEX)}, indent=2))


if __name__ == "__main__":
    main()
