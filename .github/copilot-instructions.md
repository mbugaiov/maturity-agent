# Maturity Agent — Copilot instructions

Assess **SDLC / agentic maturity** on Dan Shapiro's L0–L5 scale. Read `AGENTS.md` for the full loop.

## Authority

- Level definitions: `framework/shapiro-levels.md`
- Rubric signals: `framework/rubric.yaml`, `framework/signals.md`
- Hard rules: `rules/maturity-engine.md`

## Skills (read before each phase)

| Phase | Skill file |
|-------|------------|
| Orchestrate assessment | `skills/maturity-assess/SKILL.md` |
| Collect evidence | `skills/maturity-interview/SKILL.md` |
| Write report | `skills/maturity-report/SKILL.md` |
| Build slides | `skills/maturity-presentation/SKILL.md` |

## Output (never chat-only)

Write deliverables under `projects/<slug>/assessments/<run>/`: `evidence.yaml`, `report.md`, optional `presentation.html`.

## Scripts

```bash
python3 scripts/score_assessment.py projects/<slug>/assessments/<run>
python3 scripts/build_presentation.py projects/<slug>/assessments/<run>
```

See `PROVIDERS.md` for Cursor, Claude, Codex, and other adapters.
