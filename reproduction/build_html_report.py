#!/usr/bin/env python3
"""Build a visual HTML report for the EvoScientist reproduction."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "experiment_reproduction_report.html"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def bar_chart(rows: list[tuple[str, float]], title: str, subtitle: str) -> str:
    max_abs = max([abs(value) for _, value in rows] + [1])
    items = []
    for label, value in rows:
        pct = abs(value) / max_abs * 100
        cls = "positive" if value >= 0 else "negative"
        items.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{esc(label)}</div>
              <div class="bar-track"><div class="bar {cls}" style="width:{pct:.2f}%"></div></div>
              <div class="bar-value">{value:.2f}</div>
            </div>
            """
        )
    return f"""
    <section class="panel">
      <div class="section-kicker">Aggregate</div>
      <h2>{esc(title)}</h2>
      <p>{esc(subtitle)}</p>
      <div class="bars">{''.join(items)}</div>
    </section>
    """


def component_table(dossier: dict[str, Any]) -> str:
    components = [
        ("Full trajectories", "complete", "30/30 final reports", "not paper-exact"),
        ("Table 1 LLM judge", "complete", "420/420 swapped judge records", "replacement/proxy"),
        ("Table 2 evaluation", "complete in user scope", "120 inputs + 1440 Monica/Gemini surrogate labels", "human labels waived for now"),
        ("Table 3 ablation", "complete", "30-query replacement ablation", "replacement"),
        ("Figure 2 code execution", "complete", "240-record deterministic probe", "replacement"),
        ("Reproducibility bundle", "complete", "zip + manifest + SHA256 checksums", "portable audit bundle"),
    ]
    rows = []
    for name, status, evidence, scope in components:
        rows.append(
            f"""
            <tr>
              <td>{esc(name)}</td>
              <td><span class="status-pill">{esc(status)}</span></td>
              <td>{esc(evidence)}</td>
              <td>{esc(scope)}</td>
            </tr>
            """
        )
    return f"""
    <section class="panel wide">
      <div class="section-kicker">What was reproduced</div>
      <h2>复现实验覆盖范围</h2>
      <p>这张表把当前用户验收范围和严格 paper-exact 范围分开。当前 user-scope gate 已完成，但作者原始数据仍未公开。</p>
      <table>
        <thead><tr><th>Component</th><th>Status</th><th>Evidence</th><th>Scope note</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
    """


def artifact_cards(bundle: dict[str, Any]) -> str:
    checks = bundle["line_count_checks"]
    cards = [
        ("Table 1 judge inputs", checks["artifacts/judge_inputs/results.jsonl"], "JSONL records"),
        ("Table 1 judge outputs", checks["artifacts/judge_outputs/results.jsonl"], "Monica/Gemini records"),
        ("Table 2 inputs", checks["artifacts/human_evaluation/inputs.jsonl"], "human-eval comparisons"),
        ("Table 2 surrogate labels", checks["artifacts/human_evaluation/surrogate_labels.jsonl"], "LLM surrogate labels"),
        ("Label sheet rows", checks["artifacts/human_evaluation/label_packet/label_sheet_template.csv"], "CSV rows incl. header"),
    ]
    html_cards = []
    for title, value, label in cards:
        html_cards.append(
            f"""
            <div class="metric">
              <div class="metric-value">{esc(value)}</div>
              <div class="metric-title">{esc(title)}</div>
              <div class="metric-label">{esc(label)}</div>
            </div>
            """
        )
    return f"<section class=\"metrics\">{''.join(html_cards)}</section>"


def timeline() -> str:
    steps = [
        ("1", "Paper and repo recovery", "定位 EvoScientist 论文、作者仓库、公开 artifacts 和缺口。"),
        ("2", "Full trajectories", "跑通 30 个 EvoScientist full trajectories，并审计 final reports。"),
        ("3", "Seven-baseline Table 1", "生成/导入七个 baseline replacement/proxy 输出，完成 420 条 swapped judge。"),
        ("4", "Table 2 surrogate", "按用户要求用 Monica/Gemini 构造 surrogate judge，并保留 human label packet。"),
        ("5", "Ablation and Figure 2", "完成 30-query replacement ablation 与 240-record code-execution probe。"),
        ("6", "Dossier and bundle", "生成 final dossier、SHA256 manifest、zip bundle 和 user-scope completion gate。"),
    ]
    nodes = []
    for num, title, text in steps:
        nodes.append(
            f"""
            <div class="step">
              <div class="step-num">{esc(num)}</div>
              <div><h3>{esc(title)}</h3><p>{esc(text)}</p></div>
            </div>
            """
        )
    return f"""
    <section class="panel wide">
      <div class="section-kicker">Reproduction path</div>
      <h2>我具体复现了什么流程</h2>
      <div class="timeline">{''.join(nodes)}</div>
    </section>
    """


def preview_images() -> str:
    return """
    <section class="panel wide">
      <div class="section-kicker">Rendered previews</div>
      <h2>论文式输出预览</h2>
      <p>这些是运行过程中生成的 PDF/HTML preview 的第一页截图。它们用于展示输出形态，不代表完整可投稿论文已经 paper-exact 复现。</p>
      <div class="image-grid">
        <figure>
          <img src="artifacts/paper_previews/rendered/evoscientist_query01_final_report_page1.png" alt="EvoScientist final report page preview">
          <figcaption>EvoScientist query 01 final report preview</figcaption>
        </figure>
        <figure>
          <img src="artifacts/paper_previews/rendered/ai_scientist_v2_query01_idea_page1.png" alt="AI Scientist-v2 idea PDF page preview">
          <figcaption>AI Scientist-v2 query 01 idea preview</figcaption>
        </figure>
      </div>
    </section>
    """


def all_reports_section() -> str:
    manifest = load_json(ROOT / "artifacts" / "paper_previews" / "all_evoscientist_reports" / "manifest.json")
    cards = []
    for item in manifest["reports"][:6]:
        cards.append(
            f"""
            <a class="paper-card" href="artifacts/paper_previews/all_evoscientist_reports/{esc(item['html'])}">
              <span>Query {int(item['query_id']):02d} · {esc(item['topic'])}</span>
              <strong>{esc(item['title'])}</strong>
            </a>
            """
        )
    return f"""
    <section class="panel wide">
      <div class="section-kicker">All generated papers</div>
      <h2>30 个 EvoScientist final reports 都在这里</h2>
      <p>之前页面只放了两个 PDF 预览截图作为样例；完整 30 个 query 的 final_report 已经转成可浏览 HTML 页面。</p>
      <div class="paper-grid">{''.join(cards)}</div>
      <p class="link-line"><a href="artifacts/paper_previews/all_evoscientist_reports/index.html">打开全部 30 个 final reports →</a></p>
    </section>
    """


def build_html() -> str:
    dossier = load_json(ROOT / "final_reproduction_dossier.json")
    bundle = load_json(ROOT / "artifacts" / "reproducibility_bundle" / "manifest.json")
    user_gate = load_json(ROOT / "artifacts" / "audit" / "user_scope_reproduction_gate.json")
    table1 = dossier["components"]["table1_llm_idea_generation"]["aggregate"]["baselines"]
    table2 = dossier["components"]["table2_human_idea_generation"]["surrogate"]["aggregate"]["baselines"]
    table1_rows = [(name, data["avg_gap"]) for name, data in table1.items()]
    table2_rows = [(name, data["avg_gap"]) for name, data in table2.items()]
    archive = bundle.get("archive", {})
    bundle_sha = archive.get("sha256", "not recorded")
    bundle_bytes = archive.get("bytes", 0)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EvoScientist Experiment Reproduction Report</title>
  <style>
    :root {{
      --ink: #15171a;
      --muted: #5f6872;
      --line: #d9dee5;
      --paper: #fbfbf8;
      --panel: #ffffff;
      --green: #227a4b;
      --red: #b0433f;
      --gold: #b98522;
      --blue: #225f9f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--paper);
      line-height: 1.55;
    }}
    header {{
      padding: 48px clamp(20px, 5vw, 72px) 28px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #fff 0%, #f4f7f8 100%);
    }}
    main {{ padding: 28px clamp(20px, 5vw, 72px) 56px; }}
    h1 {{ margin: 0; max-width: 980px; font-size: clamp(32px, 5vw, 64px); line-height: 1.04; letter-spacing: 0; }}
    h2 {{ margin: 4px 0 8px; font-size: 25px; letter-spacing: 0; }}
    h3 {{ margin: 0 0 4px; font-size: 17px; letter-spacing: 0; }}
    p {{ color: var(--muted); margin: 0 0 14px; }}
    a {{ color: var(--blue); }}
    .lead {{ max-width: 920px; margin-top: 18px; font-size: 18px; }}
    .badges {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }}
    .badge {{ border: 1px solid var(--line); background: #fff; padding: 8px 11px; border-radius: 6px; font-size: 14px; color: #303840; }}
    .badge strong {{ color: var(--green); }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 18px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 22px; }}
    .wide {{ grid-column: 1 / -1; }}
    .section-kicker {{ color: var(--gold); text-transform: uppercase; font-size: 12px; font-weight: 700; letter-spacing: .08em; }}
    .metrics {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin: 0 0 18px; }}
    .metric {{ background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 16px; min-height: 116px; }}
    .metric-value {{ font-size: 32px; font-weight: 760; color: var(--blue); }}
    .metric-title {{ font-weight: 720; margin-top: 4px; }}
    .metric-label {{ color: var(--muted); font-size: 13px; margin-top: 3px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); text-align: left; padding: 10px 8px; vertical-align: top; }}
    th {{ color: #35404a; background: #f6f8f9; }}
    .status-pill {{ display: inline-block; border: 1px solid #b9d6c6; background: #eef8f2; color: var(--green); border-radius: 999px; padding: 3px 8px; font-size: 12px; font-weight: 700; }}
    .bars {{ display: grid; gap: 10px; margin-top: 18px; }}
    .bar-row {{ display: grid; grid-template-columns: 150px 1fr 68px; gap: 10px; align-items: center; }}
    .bar-label {{ font-weight: 650; font-size: 13px; overflow-wrap: anywhere; }}
    .bar-track {{ height: 16px; background: #edf0f3; border-radius: 999px; overflow: hidden; }}
    .bar {{ height: 100%; border-radius: 999px; }}
    .bar.positive {{ background: var(--green); }}
    .bar.negative {{ background: var(--red); }}
    .bar-value {{ font-variant-numeric: tabular-nums; color: #36404a; font-size: 13px; text-align: right; }}
    .timeline {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .step {{ display: grid; grid-template-columns: 42px 1fr; gap: 12px; border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: #fcfcfb; }}
    .step-num {{ width: 34px; height: 34px; display: grid; place-items: center; border-radius: 50%; background: #e8f0f6; color: var(--blue); font-weight: 800; }}
    .image-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .paper-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 14px; }}
    .paper-card {{ display: block; text-decoration: none; color: inherit; border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: #fcfcfb; min-height: 118px; }}
    .paper-card:hover {{ border-color: #8fb2d4; box-shadow: 0 8px 20px rgba(25, 45, 65, .08); }}
    .paper-card span {{ display: block; color: var(--gold); font-size: 12px; font-weight: 800; margin-bottom: 6px; }}
    .paper-card strong {{ font-size: 15px; line-height: 1.3; }}
    .link-line {{ margin-top: 14px; font-weight: 760; }}
    figure {{ margin: 0; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: #fff; }}
    img {{ width: 100%; display: block; }}
    figcaption {{ padding: 10px 12px; color: var(--muted); font-size: 13px; }}
    .callout {{ border-left: 5px solid var(--gold); background: #fff8e9; padding: 16px 18px; border-radius: 6px; }}
    .callout strong {{ color: #6b480c; }}
    code {{ background: #eef1f4; padding: 2px 5px; border-radius: 4px; }}
    footer {{ border-top: 1px solid var(--line); padding: 20px clamp(20px, 5vw, 72px); color: var(--muted); }}
    @media (max-width: 920px) {{
      .grid, .metrics, .timeline, .image-grid, .paper-grid {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 110px 1fr 58px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>EvoScientist 复现实验报告</h1>
    <p class="lead">这份报告解释我复现了什么、哪些证据已经生成、哪些部分属于 replacement/proxy 复现，以及为什么严格 paper-exact 仍然需要作者原始数据和真实 human labels。</p>
    <div class="badges">
      <div class="badge">User-scope gate: <strong>{esc(user_gate["status"])}</strong></div>
      <div class="badge">Paper-exact: <strong>false</strong></div>
      <div class="badge">Branch: <strong>{esc(dossier["repository"]["branch"])}</strong></div>
      <div class="badge">Bundle SHA256: <code>{esc(str(bundle_sha)[:16])}...</code></div>
      <div class="badge">Bundle size: <strong>{bundle_bytes:,} bytes</strong></div>
    </div>
  </header>
  <main>
    {artifact_cards(bundle)}
    <div class="grid">
      {component_table(dossier)}
      {bar_chart(table1_rows, "Table 1: 七个 baseline 的平均 gap", "数值是 EvoScientist 相对 baseline 的 Win%-Lose% 平均值；这是 replacement/proxy judge，不是作者原始 transcript。")}
      {bar_chart(table2_rows, "Table 2: Monica/Gemini surrogate 平均 gap", "human judge 暂时 waived；这里展示的是 surrogate labels 聚合，不冒充 PhD human labels。")}
      {timeline()}
      {all_reports_section()}
      {preview_images()}
      <section class="panel wide">
        <div class="section-kicker">Boundary</div>
        <h2>严格 paper-exact 还缺什么</h2>
        <div class="callout">
          <p><strong>当前用户范围已经完成：</strong>Monica/Gemini surrogate judge 被接受，human judge 暂不处理，所有 replacement/proxy artifacts、dossier 和 reproducibility bundle 已生成。</p>
          <p><strong>严格论文级复现仍未完成：</strong>还缺作者原始 Table 1 baseline raw outputs、作者侧 Gemini judge transcripts、三位 PhD 的 Table 2 human labels 与 aggregate。</p>
        </div>
      </section>
      <section class="panel wide">
        <div class="section-kicker">Artifacts</div>
        <h2>最重要的文件</h2>
        <table>
          <thead><tr><th>用途</th><th>路径</th></tr></thead>
          <tbody>
            <tr><td>最终 dossier</td><td><a href="final_reproduction_dossier.md">final_reproduction_dossier.md</a></td></tr>
            <tr><td>User-scope gate</td><td><a href="artifacts/audit/user_scope_reproduction_gate.md">artifacts/audit/user_scope_reproduction_gate.md</a></td></tr>
            <tr><td>可下载复现包</td><td><a href="artifacts/reproducibility_bundle.zip">artifacts/reproducibility_bundle.zip</a></td></tr>
            <tr><td>Bundle manifest</td><td><a href="artifacts/reproducibility_bundle/manifest.json">artifacts/reproducibility_bundle/manifest.json</a></td></tr>
            <tr><td>Table 1 总表</td><td><a href="artifacts/tables/idea_generation_win_tie_lose.csv">artifacts/tables/idea_generation_win_tie_lose.csv</a></td></tr>
            <tr><td>Table 2 surrogate</td><td><a href="table2_surrogate_monica_report.md">table2_surrogate_monica_report.md</a></td></tr>
            <tr><td>人工标注包</td><td><a href="artifacts/human_evaluation/label_packet/annotation_guide.md">artifacts/human_evaluation/label_packet/annotation_guide.md</a></td></tr>
          </tbody>
        </table>
      </section>
    </div>
  </main>
  <footer>
    Generated from checked-in reproduction artifacts. Verification commands: <code>.venv/bin/python reproduction/verify_user_scope_reproduction.py --strict</code>, <code>.venv/bin/python reproduction/verify_reproduction_assets.py</code>, <code>bash reproduction/run_preflight.sh</code>.
  </footer>
</body>
</html>
"""


def main() -> None:
    text = "\n".join(line.rstrip() for line in build_html().splitlines()) + "\n"
    OUTPUT.write_text(text, encoding="utf-8")
    print(json.dumps({"status": "ok", "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
