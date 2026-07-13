---
name: maturity-code-review
description: Review engine code changes before merge — run pre_merge_check, verify engine agnosticism, adapter sync, and rubric/skill consistency. Use before opening a PR, after implementing engine features, or when the user asks for code review.
---

# Maturity engine — code review

## When to use

- Before opening a PR on `maturity-agent`
- After editing `skills/`, `rules/`, `scripts/`, `framework/`, or `templates/`
- User asks "review my changes" / "CR this branch"

## Step 1 — Automated gates (blocking)

Run from repo root:

```bash
bash scripts/pre_merge_check.sh
```

This runs:

1. `tests/run_tests.sh` — integration + Python unit tests
2. `scripts/check_engine_agnostic.sh` — no customer project names in tracked files
3. Adapter sync check — `skills/` and `rules/` must match `.cursor/`, `.claude/`, Copilot instructions

If adapter drift is reported:

```bash
./scripts/sync_adapters.sh
git add .cursor .claude .github/copilot-instructions.md
```

Re-run `pre_merge_check.sh` until green.

## Step 2 — Diff-aware checklist

Read `rules/code-review-gate.md` and verify the diff:

- [ ] **Engine agnosticism** — no real customer slugs, repo URLs, or issue keys in engine files
- [ ] **Secrets** — nothing under `projects/*/.secrets/` or tokens in committed files
- [ ] **Rubric consistency** — if `rubric.yaml` changed, `signals.md` and tests still align
- [ ] **Multi-provider** — new skills added to `scripts/sync_adapters.sh` `SKILLS` array
- [ ] **Tests** — new scripts or scoring behavior have coverage in `tests/`
- [ ] **Docs** — `AGENTS.md` / `README.md` / `PROVIDERS.md` updated if workflow changed
- [ ] **Scope** — change is engine-only; `projects/<slug>/` data not committed (except `_template/`)

## Step 3 — Agent review (optional, Cursor)

When Bugbot or a review subagent is available, launch with **Custom Instructions**:

```
Engine repo — maturity-agent. Block on:
- Customer project names or private paths in framework/skills/rules/scripts/templates
- skills/ or rules/ changed without synced .cursor/.claude adapters
- Missing tests for new script behavior
- Secrets or credentials in diff
Read rules/code-review-gate.md for full gate.
```

Summarize findings as: Severity | Location | Finding. Do not auto-fix unless asked.

## Step 4 — PR readiness

Before merge:

1. CI green on GitHub (`.github/workflows/ci.yml`)
2. PR template checklist complete (`.github/pull_request_template.md`)
3. Commit message explains **why**, not just what

## Output format (when reporting to user)

```markdown
## Code review — maturity-agent

**Gates:** pass / fail
**Adapter sync:** ok / drift fixed
**Findings:** N block · N major · N minor

| Severity | Location | Finding |
|----------|----------|---------|
| ... | ... | ... |

**Verdict:** merge-ready / needs fixes
```

## Not in scope

- Reviewing **target project** application code — use that project's own CR process
- Assessing Shapiro level — use skill `maturity-assess`
