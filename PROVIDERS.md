# Multi-provider support

The **engine is provider-neutral**. Canonical instructions live at the repo root; thin **adapters** map them to each AI tool's expected layout.

## Canonical (edit these)

| Path | Purpose |
|------|---------|
| `AGENTS.md` | Universal spine — loop, skills index, output layout (Codex, many CLI agents) |
| `rules/maturity-engine.md` | Always-on hard constraints |
| `skills/<name>/SKILL.md` | Procedural how-to per phase |
| `framework/` | Shapiro definitions + rubric (provider-independent) |
| `scripts/` | Scoring, presentation, project scaffolding (no LLM required) |

After changing `skills/` or `rules/`, run:

```bash
./scripts/sync_adapters.sh
```

Commit **canonical + synced adapters** together.

## Provider adapters (generated or pointers)

| Provider | Entry point | Skills | Rules |
|----------|-------------|--------|-------|
| **Cursor** | `AGENTS.md` | `.cursor/skills/` | `.cursor/rules/maturity-engine.mdc` |
| **Claude Code** | `CLAUDE.md` → `AGENTS.md` | `.claude/skills/` | `rules/maturity-engine.md` |
| **GitHub Copilot** | `.github/copilot-instructions.md` | read `skills/` | `rules/maturity-engine.md` |
| **OpenAI Codex** | `AGENTS.md` | read `skills/` | `rules/maturity-engine.md` |
| **Any other agent** | `AGENTS.md` + `skills/` | copy or symlink as needed | `rules/maturity-engine.md` |

## Quickstart by provider

### Cursor

1. Open `maturity-agent/` as workspace (or parent monorepo).
2. Rules load from `.cursor/rules/maturity-engine.mdc` when globs match.
3. Prompt:

   > Assess `projects/<slug>` using skill `maturity-assess`. Fill evidence, score, write report.

### Claude Code

1. Open repo; Claude reads `CLAUDE.md` automatically.
2. Skills available under `.claude/skills/` (synced from canonical).
3. Same prompt as Cursor — skill names are identical.

### GitHub Copilot (IDE / agent)

1. Copilot reads `.github/copilot-instructions.md` in this repo.
2. Point at `skills/maturity-assess/SKILL.md` for full procedure.
3. Machine steps (`score_assessment.py`, `build_presentation.py`) run in terminal — no provider lock-in.

### Codex / generic CLI agent

1. Pass `AGENTS.md` as system or project instructions.
2. Read skills from `skills/<name>/SKILL.md` on demand.
3. Enforce `rules/maturity-engine.md` constraints.

## Assessing targets that use a different provider

When inspecting a **target project's** repos, look for agent config in **any** of these locations (record paths in `intake.md`):

| Pattern | Examples |
|---------|----------|
| Universal spine | `AGENTS.md` |
| Cursor | `.cursor/rules/`, `.cursor/skills/` |
| Claude | `CLAUDE.md`, `.claude/skills/` |
| Copilot | `.github/copilot-instructions.md` |
| OpenSpec / factory | `openspec/`, `docs/*-definition-of-done.md` |

Maturity scoring is **provider-agnostic** — the rubric measures roles, gates, and evidence, not which IDE vendor runs the agent.

## What stays provider-specific (by design)

| Concern | Why |
|---------|-----|
| Adapter file paths | Each tool discovers instructions differently |
| MCP / browser tools | Optional during interview; not required for scoring |
| Global skills (`~/.cursor/skills/`) | Host setup — document in target `intake.md`, not engine |

## Maintainer checklist

- [ ] Edit `skills/` or `rules/`, then `./scripts/sync_adapters.sh`
- [ ] `bash tests/run_tests.sh` passes
- [ ] No customer product names in engine files (grep gate)
