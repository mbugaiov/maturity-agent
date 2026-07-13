---
name: maturity-interview
description: Collect evidence for Dan Shapiro maturity signals by inspecting repos, CI, issue trackers, and stakeholder answers. Use during maturity assessment before scoring.
---

# Maturity interview & discovery

## Inputs

- `projects/<slug>/intake.md` — starting facts (repos, CI paths, MANIFEST)
- `framework/signals.md` — what to look for per dimension
- Optional: absolute paths to product repo, agent-tooling repo, CI config

## Evidence priority (mandatory order)

**Artifacts beat narrative.** Never infer `no` from workflow prose until CI YAML and shipped traces are checked.

| Priority | Source | What it proves |
|----------|--------|----------------|
| 1 | **Product CI YAML** | auto-merge, blocking CR, deploy, buildId |
| 2 | **Factory MANIFEST + run traces** | shipped backlog, Done tickets, loop cadence |
| 3 | **OpenSpec / machine DoD** | spec-first, handoff gates |
| 4 | **Factory ledger** (`*.jsonl`, `run.md`) | ticks, DoD verdicts |
| 5 | **AGENTS.md / rules prose** | role boundaries (lowest priority for CI signals) |

### Anti-patterns (do not repeat)

- ❌ "Human merge" in a rule file → `auto_merge: no` **without** reading product `bitbucket-pipelines.yml` / `.github/workflows`
- ❌ Engine-repo CI only → `blocking_review_ci: partial` when **product** pipeline has `check_review_gate.sh`
- ❌ No MANIFEST pass → `factory_loop: L0` when armed loop + tick gate + Done traces exist
- ❌ Single-repo assumption on multi-repo stacks (engine + project-data + product)

## Discovery order (efficient)

### 0. Intake & multi-repo map (5 min)

Fill `intake.md` CI paths and MANIFEST before repo dive:

```
Product (shipping)     → merge, CR gate, deploy, buildId
Agent tooling (engine) → factory scripts, scoring, templates
Project data           → MANIFEST, requirements, factory/runs/
```

### 1. CI YAML — product repo first (10 min)

Read paths from `intake.md` **CI config paths** table:

```
bitbucket-pipelines.yml / .github/workflows/*.yml
  grep: auto_merge, check_review_gate, buildId, deploy, review_gate
scripts/: auto_merge_pr.sh, check_review_gate.sh, buildid_gate.sh
```

Record `per_repo` in evidence when engine CI differs:

```yaml
blocking_review_ci:
  answer: yes
  per_repo:
    product: yes
    engine: partial
  citation: "product: bitbucket-pipelines.yml L131 check_review_gate.sh"
```

### 2. Factory MANIFEST & traces (10 min)

When `factory_manifest` path exists in intake:

- Read MANIFEST — Done vs **deferred** (not all Done ≠ program incomplete)
- Pick one `factory/runs/*.jsonl` or continuous `run.md` tick log
- Record `factory_backlog_complete`, `scheduled_ticks`, `tick_gate`, `loop_cadence` in evidence meta

### 3. Static structure (10 min)

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

### 4. Trace one ticket (15 min)

Pick a closed loop example (or active validation ticket):
- Ticket → PR → merge → deploy comment → QA retest → Done
- Note where a **human click** was required

### 5. Factory operation (5 min)

- Loop arm method (`/loop`, `arm_*_loop.sh`, cron)?
- Cadence in `project-memory.md` or intake?
- Factory ledger (`*.jsonl` or equivalent) if present

**Helper scripts (optional):**

```bash
bash scripts/collect_ci_signals.sh <product-repo>
bash scripts/verify_factory_manifest.sh <path-to-MANIFEST.md>
```

## Pre-score checklist

Before running `score_assessment.py`, confirm:

- [ ] Product CI YAML read; `auto_merge` / `blocking_review_ci` cite **product** pipeline
- [ ] MANIFEST checked (if factory program exists)
- [ ] One JSONL or run log trace captured
- [ ] `per_repo` filled for multi-repo CI signals
- [ ] `prior_headline` recorded if reconciling with slide/deck

## Recording evidence

Edit `assessments/<run>/evidence.yaml`:

```yaml
meta:
  factory_manifest: "requirements/factory-tickets/MANIFEST.md"
  ci_product: "bitbucket-pipelines.yml"
  loop_cadence: "5m"
  prior_headline: "L5′ on STG ~90%"

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
| Merge | Who clicks merge today? (confirm against CI, not habit) |
| QA Done | Who moves tickets to Done? |
| PROD | Is PROD deploy automated? |
| Exceptions | What makes the loop stop and ask a human? |
| Loop arm | How is the factory loop started — cron, `/loop`, manual? |

## Red flags (likely caps level)

- No durable spec → max L2–L3
- Single generalist agent, no CR/QA split → max L3
- Human merge + human Done on every ticket **and** no auto-merge in product CI → max L4
- No deploy or no build verification → max L3–L4
