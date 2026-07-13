#!/usr/bin/env python3
"""Build standalone HTML + markdown presentation from assessment artifacts.

Usage:
    python3 scripts/build_presentation.py <assessment-dir> [--title "Display Name"]

Reads: evidence.yaml, score.json, report.md (optional), project intake for name.
Writes: presentation.html, presentation.md in assessment-dir.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


LEVELS = [
    ("L0", "Spicy autocomplete"),
    ("L1", "Coding intern"),
    ("L2", "Junior developer"),
    ("L3", "Developer"),
    ("L4", "Engineering team"),
    ("L5′", "L5 on STG"),
    ("L5", "Dark software factory"),
]


def load_yaml(path: Path) -> dict:
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_report_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = "_preamble"
    sections[current] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            current = m.group(1).strip().lower()
            sections[current] = []
        else:
            sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def extract_headline(report: str) -> str:
    m = re.search(r"\*\*Headline level:\*\*\s*\*\*(.+?)\*\*", report)
    if m:
        return m.group(1).strip()
    m = re.search(r"\*\*Headline level:\*\*\s*(.+)", report)
    return m.group(1).strip() if m else ""


def bullets_from_section(body: str, max_items: int = 8) -> list[str]:
    items = []
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            items.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return items[:max_items]


def table_rows_from_section(body: str, max_rows: int = 10) -> list[list[str]]:
    rows = []
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|[-:\s|]+\|$", line.strip()):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0].lower() not in ("dimension", "priority", "step", "level"):
            rows.append(cells)
        if len(rows) >= max_rows:
            break
    return rows


def infer_current_marker(headline: str) -> str:
    h = headline.upper()
    if "L5′" in headline or "L5'" in headline or "L5 ON STG" in h:
        return "L5′"
    for n in ("5", "4", "3", "2", "1", "0"):
        if f"L{n}" in h.upper():
            return "L5′" if n == "5" and "PRIME" in h else (f"L{n}" if n != "5" else "L5")
    return "L3"


def next_level_label(current: str) -> str:
    order = ["L0", "L1", "L2", "L3", "L4", "L5′", "L5"]
    try:
        i = order.index(current)
        return order[min(i + 1, len(order) - 1)]
    except ValueError:
        return "L4"


def gap_signals(evidence: dict, rubric: dict, target_level: int) -> list[dict]:
    sig_index = {}
    for dim in rubric.get("dimensions", []):
        for sig in dim.get("signals", []):
            sig_index[sig["id"]] = {**sig, "dimension": dim["name"]}

    gaps = []
    for sid, entry in (evidence.get("signals") or {}).items():
        ans = str(entry.get("answer", "no")).lower()
        if ans in ("yes", "na", "true"):
            continue
        meta = sig_index.get(sid, {})
        if int(meta.get("min_level", 99)) <= target_level:
            gaps.append({
                "id": sid,
                "dimension": meta.get("dimension", ""),
                "prompt": meta.get("prompt", sid),
                "answer": ans,
                "citation": entry.get("citation", ""),
            })
    return gaps[:12]


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def build_html(ctx: dict) -> str:
    ladder_rows = []
    for code, label in LEVELS:
        cls = "lvl"
        extra = ""
        if code == ctx["current_marker"]:
            cls += " on"
            extra = '<span class="here">◀ we are here</span>'
        elif code in ctx.get("achieved_markers", set()):
            cls += " done"
            extra = '<span class="here chk">✓</span>'
        ladder_rows.append(
            f'<div class="{cls}"><span class="lp">{esc(code)}</span>'
            f"<span>{esc(label)}</span>{extra}</div>"
        )

    dim_rows = "".join(
        f"<tr><td>{esc(d['name'])}</td><td><b>L{d['level']}</b></td></tr>"
        for d in ctx["dimensions"]
    )

    strength_lis = "".join(f"<li>{esc(b)}</li>" for b in ctx["strengths"])
    gap_lis = "".join(f"<li>{esc(g)}</li>" for g in ctx["gap_bullets"])
    path_rows = "".join(
        f"<tr><td>{esc(r[0])}</td><td>{esc(r[1] if len(r) > 1 else '')}</td></tr>"
        for r in ctx["path_rows"]
    )
    gap_detail = "".join(
        f"<li><b>{esc(g['dimension'])}</b> — {esc(g['prompt'])} "
        f"<span class='muted'>({esc(g['answer'])})</span></li>"
        for g in ctx["gap_signals"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(ctx['title'])} — SDLC Maturity</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css" />
  <style>
    :root {{
      --accent: #2f9fe5; --accent2: #4ade80; --amber: #f7b955; --muted: #94a8bd;
    }}
    .reveal {{ font-family: Inter, system-ui, sans-serif; }}
    .reveal h1, .reveal h2 {{ text-transform: none; letter-spacing: -0.02em; }}
    .reveal section {{ text-align: left; }}
    .kicker {{ text-transform: uppercase; letter-spacing: .2em; font-size: .45em;
      color: var(--accent); font-weight: 700; margin: 0 0 .5em; }}
    .muted {{ color: var(--muted); }}
    .green {{ color: var(--accent2); }}
    .amber {{ color: var(--amber); }}
    .lvl {{ display:flex; align-items:baseline; gap:.5em; padding:.22em .5em;
      border-radius:8px; font-size:.62em; border:1px solid transparent; margin:.1em 0; }}
    .lvl .lp {{ font-weight:800; color:var(--muted); min-width:2em; }}
    .lvl.on {{ background:rgba(74,222,128,.12); border-color:rgba(74,222,128,.45); }}
    .lvl.on .lp {{ color:var(--accent2); }}
    .lvl.done {{ opacity:.75; }}
    .here {{ color:var(--accent2); font-weight:700; font-size:.85em; margin-left:auto; }}
    .here.chk {{ color:var(--accent2); }}
    .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:1em; }}
    table.mini {{ width:100%; font-size:.52em; border-collapse:collapse; }}
    table.mini td, table.mini th {{ border:1px solid rgba(255,255,255,.12); padding:.35em .5em; }}
    ul.tight {{ font-size:.58em; line-height:1.35; margin:.3em 0; }}
    .card {{ background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.1);
      border-radius:10px; padding:.65em .85em; font-size:.55em; }}
    h3 {{ color:var(--accent); font-size:.85em; margin:.2em 0 .4em; }}
  </style>
</head>
<body>
  <div class="reveal"><div class="slides">

    <section>
      <p class="kicker">SDLC Maturity Assessment</p>
      <h1>{esc(ctx['title'])}</h1>
      <p class="muted" style="font-size:.65em">Dan Shapiro Five Levels · {esc(ctx['date'])}</p>
      <p style="font-size:.75em;margin-top:1em"><span class="green"><b>{esc(ctx['headline'])}</b></span></p>
      <p class="muted" style="font-size:.5em">{esc(ctx['summary_line'])}</p>
    </section>

    <section>
      <p class="kicker">Methodology</p>
      <h2>How we evaluated</h2>
      <div class="cols">
        <ul class="tight">
          <li><b>Framework:</b> Dan Shapiro L0–L5 (+ L5′ staging sub-level)</li>
          <li><b>Rubric:</b> 11 dimensions, ~30 observable signals</li>
          <li><b>Discovery:</b> repo + pipeline + agent rules inspection</li>
          <li><b>Evidence:</b> <code>evidence.yaml</code> per signal with citation</li>
        </ul>
        <ul class="tight">
          <li><b>Scoring:</b> <code>score_assessment.py</code> → <code>score.json</code></li>
          <li><b>Review:</b> human narrative in <code>report.md</code></li>
          <li><b>Assessment:</b> {esc(ctx['assessment_id'])}</li>
          <li><b>Target:</b> <span class="muted">{esc(ctx['target'])}</span></li>
        </ul>
      </div>
    </section>

    <section>
      <p class="kicker">Maturity · Dan Shapiro</p>
      <h2>Where we are: <span class="green">{esc(ctx['current_marker'])}</span></h2>
      <p class="muted" style="font-size:.55em;margin-bottom:.5em">Next target: <b>{esc(ctx['next_level'])}</b></p>
      {''.join(ladder_rows)}
    </section>

    <section>
      <p class="kicker">Current state</p>
      <h2>What we have now</h2>
      <div class="cols">
        <div>
          <h3>Dimension scorecard</h3>
          <table class="mini"><tr><th>Dimension</th><th>Level</th></tr>{dim_rows}</table>
          <p class="muted" style="font-size:.45em;margin-top:.4em">Floor L{ctx['floor']} · Weighted {ctx['weighted']}</p>
        </div>
        <div>
          <h3 class="green">Strengths</h3>
          <ul class="tight">{strength_lis or '<li class="muted">See report.md</li>'}</ul>
        </div>
      </div>
    </section>

    <section>
      <p class="kicker">Gap analysis</p>
      <h2>Why not <span class="amber">{esc(ctx['next_level'])}</span> yet?</h2>
      <ul class="tight">{gap_lis}</ul>
      <div class="card" style="margin-top:.6em">
        <h3>Signal gaps (evidence)</h3>
        <ul class="tight">{gap_detail or '<li class="muted">—</li>'}</ul>
      </div>
    </section>

    <section>
      <p class="kicker">Roadmap</p>
      <h2>Implement to reach <span class="green">{esc(ctx['next_level'])}</span></h2>
      <table class="mini">
        <tr><th>Priority</th><th>Action</th></tr>
        {path_rows or '<tr><td colspan="2" class="muted">See report.md § Path</td></tr>'}
      </table>
    </section>

    <section>
      <p class="kicker">Summary</p>
      <h2>Takeaways</h2>
      <p style="font-size:.65em"><b>Today:</b> {esc(ctx['headline'])}</p>
      <p style="font-size:.65em"><b>Next:</b> {esc(ctx['next_level'])} — close gaps in agent topology, CI, deploy, factory loop</p>
      <ol class="tight" style="margin-top:.8em">
        {''.join(f'<li>{esc(a)}</li>' for a in ctx['top_actions'])}
      </ol>
      <p class="muted" style="font-size:.42em;margin-top:1.2em">Generated by maturity-agent · {esc(ctx['generated'])}</p>
    </section>

  </div></div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script>Reveal.initialize({{ hash: true, slideNumber: true, width: 1280, height: 720 }});</script>
</body>
</html>
"""


def build_markdown(ctx: dict) -> str:
    lines = [
        f"# Presentation — {ctx['title']}",
        f"**Assessment:** {ctx['assessment_id']}  ",
        f"**Headline:** {ctx['headline']}  ",
        "",
        "## Slide 1 — Title",
        ctx["headline"],
        "",
        "## Slide 2 — How we evaluated",
        "- Dan Shapiro framework + rubric.yaml",
        "- evidence.yaml + score_assessment.py + report.md",
        "",
        "## Slide 3 — Level ladder",
        f"**Current:** {ctx['current_marker']} → **Next:** {ctx['next_level']}",
        "",
        "## Slide 4 — What we have now",
        "",
        "| Dimension | Level |",
        "|-----------|-------|",
    ]
    for d in ctx["dimensions"]:
        lines.append(f"| {d['name']} | L{d['level']} |")
    lines.extend(["", "### Strengths", ""])
    lines.extend(f"- {b}" for b in ctx["strengths"])
    lines.extend(["", "## Slide 5 — Why not higher", ""])
    lines.extend(f"- {g}" for g in ctx["gap_bullets"])
    lines.extend(["", f"## Slide 6 — Path to {ctx['next_level']}", ""])
    for r in ctx["path_rows"]:
        lines.append(f"- **{r[0]}** — {r[1] if len(r) > 1 else ''}")
    lines.extend(["", "## Slide 7 — Summary", ""])
    for a in ctx["top_actions"]:
        lines.append(f"1. {a}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("assessment_dir", help="Path to assessments/<date>-<scope>/")
    ap.add_argument("--title", default="", help="Override display title")
    args = ap.parse_args()

    assess_dir = Path(args.assessment_dir).resolve()
    if not assess_dir.is_dir():
        print(f"Not a directory: {assess_dir}", file=sys.stderr)
        return 1

    root = assess_dir
    while root.name != "maturity-agent" and root.parent != root:
        root = root.parent
    if root.name != "maturity-agent":
        root = Path(__file__).resolve().parent.parent

    evidence_path = assess_dir / "evidence.yaml"
    score_path = assess_dir / "score.json"
    report_path = assess_dir / "report.md"

    if not evidence_path.exists():
        print(f"Missing {evidence_path}", file=sys.stderr)
        return 1
    if not score_path.exists():
        print(f"Missing {score_path} — run score_assessment.py first", file=sys.stderr)
        return 1

    evidence = load_yaml(evidence_path)
    score = json.loads(score_path.read_text(encoding="utf-8"))
    rubric = load_yaml(root / "framework" / "rubric.yaml")
    report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    sections = parse_report_sections(report)

    slug = evidence.get("meta", {}).get("project", "project")
    proj_dir = assess_dir.parent.parent
    title = args.title
    if not title:
        intake = proj_dir / "intake.md"
        if intake.exists():
            m = re.search(r"\*\*Display name\*\*\s*\|\s*(.+?)\s*\|", intake.read_text())
            if m:
                title = m.group(1).strip()
        if not title:
            title = slug.replace("-", " ").title()

    headline = extract_headline(report) or score.get("headline_hint", "L?")
    current = infer_current_marker(headline)
    next_lvl = next_level_label(current)
    target_level = 4 if next_lvl in ("L4", "L5′", "L5") else 3

    strengths = bullets_from_section(sections.get("strengths", ""))
    gap_bullets = bullets_from_section(sections.get("gaps (blocking l4 headline)", ""))
    if not gap_bullets:
        gap_bullets = bullets_from_section(sections.get("gaps", ""))
    path_rows = table_rows_from_section(sections.get("path toward l4", ""))
    if not path_rows:
        path_rows = table_rows_from_section(sections.get("path to next level", ""))

    top_actions = [r[1] if len(r) > 1 else r[0] for r in path_rows[:3]]
    if not top_actions:
        top_actions = gap_bullets[:3]

    summary_line = ""
    exec_sec = sections.get("executive summary", "")
    if exec_sec:
        summary_line = exec_sec.split("\n\n")[0].replace("**", "")[:220]

    ctx = {
        "title": title,
        "date": evidence.get("meta", {}).get("date", assess_dir.name.split("-")[0:3] and assess_dir.name[:10] or ""),
        "assessment_id": assess_dir.name,
        "target": evidence.get("meta", {}).get("target_repo", slug),
        "headline": headline,
        "summary_line": summary_line,
        "current_marker": current,
        "next_level": next_lvl,
        "dimensions": score.get("dimensions", []),
        "floor": score.get("floor_level", 0),
        "weighted": score.get("weighted_level", 0),
        "strengths": strengths,
        "gap_bullets": gap_bullets,
        "path_rows": path_rows,
        "gap_signals": gap_signals(evidence, rubric, target_level),
        "top_actions": top_actions or ["See report.md § Path"],
        "achieved_markers": {f"L{d['level']}" for d in score.get("dimensions", []) if d.get("level", 0) >= 4},
        "generated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }

    html_out = assess_dir / "presentation.html"
    md_out = assess_dir / "presentation.md"
    html_out.write_text(build_html(ctx), encoding="utf-8")
    md_out.write_text(build_markdown(ctx), encoding="utf-8")
    print(f"Wrote {html_out}")
    print(f"Wrote {md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
