---
name: maturity-presentation
description: Build a standalone HTML (and markdown) presentation from a completed maturity assessment — methodology, current level, dimension scorecard, and path to next level. Use after report.md and score.json exist.
---

# Maturity presentation

## When to use

- User asks for slides / deck / presentation from assessment results
- After `maturity-report` produced `report.md` + `score.json`
- Executive readout of Dan Shapiro level and gap backlog

## Prerequisites

```
projects/<slug>/assessments/<run>/
  evidence.yaml    # required
  score.json       # run score_assessment.py if missing
  report.md        # recommended (narrative + headline)
```

## Steps

1. Read `framework/shapiro-levels.md` — use canonical L0–L5 / L5′ labels in slides
2. Read `report.md` — executive summary, strengths, gaps, path to next level
3. Read `score.json` — dimension levels for scorecard slide
4. Read `evidence.yaml` — citations for "how evaluated" and gap evidence
5. Run generator:

   ```bash
   python3 scripts/build_presentation.py projects/<slug>/assessments/<run>
   ```

6. Review `presentation.html` in browser; edit `presentation.md` if narrative tweaks needed
7. Optional: agent enriches slides 5–7 from `report.md` before or after script run

## Output files

| File | Purpose |
|------|---------|
| `presentation.html` | Standalone Reveal.js deck (open in browser, arrow keys) |
| `presentation.md` | Editable slide script / speaker notes |

## Required slide deck (7 sections)

1. **Title** — project name, date, headline level
2. **How we evaluated** — Dan Shapiro framework, 11 rubric dimensions, evidence.yaml + repo inspection, `score_assessment.py`
3. **Level ladder** — L0–L5 + L5′ with current position highlighted
4. **What we have now** — dimension scorecard + top strengths (from report)
5. **Why not higher** — blocking gaps (signals `no` / `partial`)
6. **Path to next level** — prioritized implement list (from report § Path)
7. **Summary** — headline + 3 bullet next actions

## Agent enrichment (when script output is thin)

If `report.md` has richer narrative than auto-parser:

- Paste executive summary into slide 1 speaker notes
- Expand slide 6 with ticket-shaped items from § Path toward next level
- Add worked trace table from report if present

## Rules

- **Project-agnostic engine** — presentation content comes from assessment folder only; no hardcoded customer names in templates
- Redact secrets in citations (paths OK, no tokens)
- Do not inflate level — use human headline from `report.md` over raw `floor_level` when they differ
- L5′ vs L5 — label honestly (STG factory vs full dark factory)

## Example

```bash
python3 scripts/build_presentation.py projects/acme/assessments/2026-07-13-baseline
open projects/acme/assessments/2026-07-13-baseline/presentation.html
```
