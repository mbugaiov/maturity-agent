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

1. `projects/<slug>/intake.md` filled (at least repos + agents + CI)
2. Assessment folder exists: `scripts/new_assessment.sh <slug> <scope>`

## Steps

1. Read `projects/<slug>/project.yaml`, `intake.md`, `project-memory.md`
2. Read `framework/shapiro-levels.md` (5 min — do not skip)
3. Copy `templates/assessment.md` → `assessments/<run>/assessment.md` if empty
4. Run **maturity-interview** skill — fill `evidence.yaml`
5. Run `python3 scripts/score_assessment.py projects/<slug>/assessments/<run>` 
6. Run **maturity-report** skill — write `report.md`
7. Update `project-memory.md` with headline level + trend
8. Optional: run **maturity-presentation** → `presentation.html`

## Output checklist

- [ ] `evidence.yaml` — every signal has `answer` + `citation`
- [ ] `report.md` — headline level, dimension table, gaps, recommended next tickets
- [ ] `presentation.html` — if user wants slides (skill `maturity-presentation`)
- [ ] `project-memory.md` — last assessment pointer updated

## Re-assessment

Compare to previous `report.md` in `project-memory.md`:
- New signals → level up/down
- Call out **regressions** (was yes, now no)

## Sanity check

Use the **fictional** table in `framework/signals.md` only to validate rubric mechanics — never as evidence for a real project.
