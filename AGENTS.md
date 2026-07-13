# Maturity Agent — Dan Shapiro SDLC Assessment

The agent assesses **how mature an AI-assisted SDLC setup is** on Dan Shapiro's L0–L5 scale.
One project = one target system; one assessment = one dated folder under `assessments/`.

> **Provider-neutral engine** — works with Cursor, Claude Code, Copilot, Codex, and other agents.
> See `PROVIDERS.md` for per-tool setup.
>
> Operating constraints: `rules/maturity-engine.md` (always-on).
> Procedural detail: skills under `skills/` (synced to `.cursor/skills/`, `.claude/skills/`, etc.).
> Framework authority: `framework/shapiro-levels.md` + `framework/rubric.yaml`.

## Skills (read on demand)

| When you're doing… | Skill (`skills/<name>/SKILL.md`) |
|---|---|
| Starting / resuming an assessment | `maturity-assess` |
| Interviewing stakeholders or reading repos for signals | `maturity-interview` |
| Writing the final report + level recommendation | `maturity-report` |
| Building HTML/markdown presentation deck | `maturity-presentation` |
| Reviewing engine changes before merge | `maturity-code-review` |

## The loop (every assessment)

```
0. Setup     → new_project.sh (once) + new_assessment.sh; read intake.md + project-memory.md
1. Frame     → confirm scope (repos, agents, envs, date); read framework/shapiro-levels.md
2. Intake    → fill or verify projects/<slug>/intake.md (human + links)
3. Discover  → maturity-interview: repos, agent config (any provider), CI, tracker, deploy trace
4. Evidence  → per-dimension signals → assessments/<run>/evidence.yaml (yes|partial|no|na + cite)
5. Score     → scripts/score_assessment.py (optional machine pass) + agent reasoning for conflicts
6. Level     → recommend primary level + sub-level (e.g. "L4, reaching L5′ on STG")
7. Gaps      → top blockers to next level with concrete next tickets / rule changes
8. Report    → assessments/<run>/report.md from templates/report.md
9. Present   → maturity-presentation: build_presentation.py → presentation.html
10. Memory   → update projects/<slug>/project-memory.md (last level, trend, open gaps)
```

## Hard rules

- **Evidence before score** — no level claim without a cited artifact (file path, issue key, CI log, script).
- **Shapiro definitions win** — `framework/shapiro-levels.md` is the oracle; rubric signals are observables.
- **Separate product maturity from agent maturity** — a great app with no agents is L0–L1 for this framework.
- **L5 is rare** — full dark factory requires zero human in the loop for routine work; call out what humans still own.
- **Distinguish L5′ (factory on STG)** from full L5 (PROD, multi-product, zero escalation) — see `framework/shapiro-levels.md`.
- **Per-project isolation** — only read `projects/<slug>/`; never mix another project's intake.
- Never commit secrets — links and redacted excerpts only.

## Engine maintenance (contributors)

Before merging engine changes:

```bash
bash scripts/pre_merge_check.sh
```

See `CONTRIBUTING.md` and skill `maturity-code-review`. Rules: `rules/code-review-gate.md`.

## Output layout

```
maturity-agent/                 ← ENGINE
  AGENTS.md                     ← universal spine (Codex, CLI agents)
  CLAUDE.md                     ← Claude Code pointer
  PROVIDERS.md                  ← Cursor / Claude / Copilot / Codex
  skills/                       ← canonical skills (source of truth)
  rules/                        ← canonical hard rules
  framework/                    ← Shapiro defs + rubric
  projects/
    _template/                  ← skeleton
    <slug>/                     ← per target system
      intake.md
      project-memory.md
      assessments/<date>-<scope>/
        assessment.md           ← working notes
        evidence.yaml           ← signal answers
        report.md               ← deliverable
        presentation.html       ← slide deck (optional)
        presentation.md         ← speaker notes
```
