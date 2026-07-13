# Maturity Agent — portability (engine vs projects)

The **engine** is reusable; **project data** is per target system.

## Engine repo (this repo)

```
maturity-agent/
  AGENTS.md             universal spine (Codex, CLI agents)
  CLAUDE.md             Claude Code entry
  PROVIDERS.md          multi-provider adapters
  framework/            shapiro-levels.md, rubric.yaml, signals.md
  skills/               canonical skills (source of truth)
  rules/                maturity-engine.md
  .cursor/              Cursor adapter (synced)
  .claude/              Claude adapter (synced)
  .github/              Copilot adapter (synced)
  templates/            intake, assessment, report, gap-backlog
  scripts/              new_project.sh, new_assessment.sh, score_assessment.py, build_presentation.py, sync_adapters.sh
  tests/run_tests.sh
  projects/_template/
```

**Rule:** engine files must not hardcode project names, repo URLs, or issue keys.
Use `projects/<slug>/` and placeholders.

After editing `skills/` or `rules/`, run `scripts/sync_adapters.sh` and commit adapters with canonical files.

## Per-project data

```
projects/<slug>/
  project.yaml          display name, linked repos, assessment history pointer
  intake.md             static facts about the SDLC (agents, CI, spec source)
  project-memory.md     last score, trend, recurring gaps
  assessments/<date>-<scope>/
    assessment.md
    evidence.yaml
    report.md
  .secrets/             optional (API tokens for read-only APIs)
```

Project folders may live in a **separate git repo** (submodule under `projects/<slug>/`, sibling clone, or monorepo subtree).

### Option A — submodule (teams)

```bash
git submodule add <assessment-data-repo-url> projects/acme
git submodule update --init
```

### Option B — plain clone into `projects/<slug>/`

```bash
git clone <assessment-data-repo-url> projects/acme
```

The engine `.gitignore` ignores `projects/*` except `projects/_template/`.

### Option C — sibling workspace

Open a parent directory in the IDE containing `maturity-agent/` and target repos; put paths in `intake.md`.

## Onboarding

```bash
scripts/new_project.sh <slug> "<Display Name>"
# Edit projects/<slug>/intake.md
scripts/new_assessment.sh <slug> baseline
```

## Linking external repos

Assessment **reads** linked repos; it does not modify them. Typical intake links:

| Role | What to inspect |
|------|-----------------|
| Product app | `AGENTS.md`, agent rules/skills (any provider), OpenSpec, CI, deploy scripts |
| Agent tooling | Factory rules, loop skills, gate scripts |
| Issue tracker | Closed-loop ticket traces |

Record paths in `intake.md` and optional `project.yaml` → `repos:` block.
