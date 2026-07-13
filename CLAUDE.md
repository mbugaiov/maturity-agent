# Maturity Agent — Claude Code

Read **`AGENTS.md`** for the assessment loop and skill index.

## Hard rules

Follow `rules/maturity-engine.md` on every assessment.

## Skills

Procedural detail lives in `.claude/skills/` (synced from canonical `skills/`):

| Phase | Skill |
|-------|-------|
| Orchestrate | `maturity-assess` |
| Discover / evidence | `maturity-interview` |
| Report | `maturity-report` |
| Presentation | `maturity-presentation` |

Read the matching `SKILL.md` before that phase — do not improvise from memory.

## Framework authority

- `framework/shapiro-levels.md` — L0–L5 definitions
- `framework/rubric.yaml` — machine scoring
- `framework/signals.md` — field guide for evidence collection

## Typical prompt

> Assess `projects/<slug>` against Dan Shapiro's framework. Use the latest assessment folder, collect evidence from linked repos, run `score_assessment.py`, write `report.md`.

Multi-provider details: `PROVIDERS.md`.
