---
name: maturity-assess
description: Run a Dan Shapiro maturity assessment on a target project. Use when assessing SDLC/agent maturity, scoring L0-L5, onboarding a new project to maturity-agent, or continuing an in-progress assessment folder.
---

# Maturity assessment (orchestrator)

## When to use

- User asks "what Shapiro level are we?"
- New project onboarded via `new_project.sh`
- Re-assessment after factory improvements

## Prerequisites

1. `projects/<slug>/intake.md` filled (repos + CI paths + agents + MANIFEST if factory program)
2. Assessment folder exists: `scripts/new_assessment.sh <slug> <scope>`

## Steps

1. Read `projects/<slug>/project.yaml`, `intake.md`, `project-memory.md`
2. Read `framework/shapiro-levels.md` (5 min — do not skip)
3. Copy `templates/assessment.md` → `assessments/<run>/assessment.md` if empty
4. Run **maturity-interview** skill — fill `evidence.yaml` (CI-first, MANIFEST, per_repo)
5. **Pre-score checklist** (from maturity-interview) — all boxes checked
6. Run `python3 scripts/score_assessment.py projects/<slug>/assessments/<run>`
7. Verify `score.json` has `operational_level`, `headline_hint`, `headline_rule_matched`
8. Run **maturity-report** skill — write `report.md` (reconciliation if operational ≠ floor)
9. Update `project-memory.md` with headline level + trend
10. Optional: run **maturity-presentation** → `presentation.html`

## Output checklist

- [ ] `evidence.yaml` — every signal has `answer` + `citation`; CI signals cite product pipeline
- [ ] `evidence.yaml` — `per_repo` for multi-repo merge/CR/deploy when applicable
- [ ] `score.json` — `operational_level` and `headline_hint` reviewed
- [ ] `report.md` — headline from `headline_hint`; reconciliation if needed
- [ ] `report.md` — factory MANIFEST table if program exists
- [ ] `presentation.html` — if user wants slides (skill `maturity-presentation`)
- [ ] `project-memory.md` — last assessment pointer updated

## Re-assessment

Compare to previous `report.md` in `project-memory.md`:
- New signals → level up/down
- Call out **regressions** (was yes, now no)
- Reconcile with prior slide/deck — explain deltas

## Sanity check

Use the **fictional** table in `framework/signals.md` only to validate rubric mechanics — never as evidence for a real project.

## Scoring reference (v1.2)

| Metric | Meaning |
|--------|---------|
| `floor_level` | Strict min — gap narrative (includes `defect_loop`) |
| `operational_level` | Delivery-loop min — STG truth (`dev`/`review`/`deploy`/`qa`/`factory_loop`; not `defect_loop`) |
| `headline_hint` | From `level_headline_rules` (L5/L5′ need operational ≥ 4) — use in report |

After scoring, publish for factory hosts:

```bash
python3 scripts/export_scorecard.py --slug <slug>
# → exports/<slug>/latest.json (commit this; projects/ assessments stay local)
```
