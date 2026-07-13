# Contributing to maturity-agent

## Engine vs project data

- **Engine** (this repo): framework, skills, scripts, templates — shared and provider-neutral.
- **Project data** (`projects/<slug>/`): per-target assessments — gitignored by default; keep local or in a separate repo.

Never commit real customer names into engine files. Use placeholders (`<slug>`, `PROG-123`).

## Development workflow

1. Branch from `master`
2. Implement; if you edit `skills/` or `rules/`, run `./scripts/sync_adapters.sh`
3. Run **`bash scripts/pre_merge_check.sh`** before pushing
4. Open PR — template checklist must be complete
5. CI must pass (tests + agnosticism + adapter sync)

## Code review

Read skill **`maturity-code-review`** (`skills/maturity-code-review/SKILL.md`) before opening a PR.

| Gate | Command |
|------|---------|
| Full pre-merge | `bash scripts/pre_merge_check.sh` |
| Tests only | `bash tests/run_tests.sh` |
| Agnosticism | `bash scripts/check_engine_agnostic.sh` |
| Sync adapters | `./scripts/sync_adapters.sh` |

**Cursor users:** optional Bugbot pass with Custom Instructions from the code-review skill.

## Adding a skill

1. Create `skills/<name>/SKILL.md`
2. Add `<name>` to `SKILLS` array in `scripts/sync_adapters.sh`
3. Run `./scripts/sync_adapters.sh`
4. Add test coverage in `tests/run_tests.sh` if the skill introduces new scripts or behavior
5. Document in `AGENTS.md` skill table

## CI

GitHub Actions runs `pre_merge_check.sh` on every push and PR to `master` / `main`.
