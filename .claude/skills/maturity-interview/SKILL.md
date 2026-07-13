---
name: maturity-interview
description: Collect evidence for Dan Shapiro maturity signals by inspecting repos, CI, issue trackers, and stakeholder answers. Use during maturity assessment before scoring.
---

# Maturity interview & discovery

## Inputs

- `projects/<slug>/intake.md` — starting facts
- `framework/signals.md` — what to look for per dimension
- Optional: absolute paths to product repo, agent-tooling repo, CI config

## Discovery order (efficient)

### 1. Static structure (10 min)

```
<product-repo>/
  AGENTS.md               universal agent spine (any provider)
  skills/ or .cursor/skills/ or .claude/skills/   procedural skills
  .cursor/rules/ or rules/ or CLAUDE.md   agent constraints
  openspec/               spec-first?
  docs/*-definition-of-done.md   machine DoD (if any)

<agent-tooling-repo>/
  AGENTS.md / rules/        factory constraints
  scripts/                  gate scripts (buildId, tick gate, scoring)
  projects/_template/       portability skeleton
```

Record which **AI provider** the team uses in `intake.md` (Cursor, Claude Code, Copilot, Codex, mixed).

### 2. Pipeline (5 min)

- CI workflow: test, review gate, deploy
- Auto-merge script or human merge?
- Staging health endpoint with buildId?

### 3. Trace one ticket (15 min)

Pick a closed loop example (or active validation ticket):
- Ticket → PR → merge → deploy comment → QA retest → Done
- Note where a **human click** was required

### 4. Factory operation (5 min)

- Scheduled loop? cadence? `project-memory.md` tick logs?
- Factory ledger (`*.jsonl` or equivalent) if present

## Recording evidence

Edit `assessments/<run>/evidence.yaml`:

```yaml
signals:
  human_writes_tickets:
    answer: yes          # yes | partial | no | na
    citation: "Epic PROG-100; docs/ticket-template.md"
    notes: ""
```

**Citation rules:**
- Prefer file paths + line refs from **the assessed project's repos**
- Issue tracker: key + what the comment proved
- Interview: "stakeholder <role>, <date>: …"

## Questions to ask humans (if repos insufficient)

| Topic | Question |
|-------|----------|
| Intent | Who writes tickets? Can agents change scope? |
| Merge | Who clicks merge today? |
| QA Done | Who moves tickets to Done? |
| PROD | Is PROD deploy automated? |
| Exceptions | What makes the loop stop and ask a human? |

## Red flags (likely caps level)

- No durable spec → max L2–L3
- Single generalist agent, no CR/QA split → max L3
- Human merge + human Done on every ticket → max L4
- No deploy or no build verification → max L3–L4
