# Integrations

## Primary framework

- **Dan Shapiro — Five Levels of AI-Assisted Software Development**
  - Authority: `framework/shapiro-levels.md`
  - Observable signals: `framework/rubric.yaml`, `framework/signals.md`

## Rubric design patterns (generic)

The rubric encodes common patterns seen in mature agentic SDLC setups. Inspect targets are **role-based**, not tied to any product name:

| Pattern | What assessors look for |
|---------|-------------------------|
| Engine / project split | Shared tooling repo + per-target `projects/<slug>/` |
| Spec-first delivery | Issue tracker + structured acceptance (OpenSpec, Gherkin, PRD) |
| Multi-agent topology | Separate dev, review, and QA concerns with written boundaries |
| Machine Definition of Done | Documented handoff contracts between agents |
| Deploy verification | Live non-PROD `buildId` (or equivalent) matches merge commit |
| Unattended QA accept | Validate/Testing → Done when machine DoD met |
| Factory loop | Scheduled ticks drain queues; end-of-tick gate |
| Human boundaries | Documented `needs-human` and PROD/infra gates |

Record **your** project's concrete file paths in `projects/<slug>/intake.md` — never in engine files.

## Companion tooling (optional)

Maturity assessment is **orthogonal** to application QA:

| Tool type | Typical question |
|-----------|------------------|
| Maturity agent (this repo) | How autonomous is the SDLC / agent factory? |
| QA / test automation | Does the shipped product behave correctly? |

A team may run both; link repos in intake only.

## Engine agnosticism rule

Files under `framework/`, `skills/`, `rules/`, `scripts/`, and `templates/` must **not** name customer products, private repo paths, or real issue keys. Use placeholders (`<slug>`, `PROG-123`) in examples.

Provider adapters (`.cursor/`, `.claude/`, `.github/copilot-instructions.md`) are synced from canonical `skills/` and `rules/` — see `PROVIDERS.md`.
