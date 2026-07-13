# Code review gate — engine changes

Apply on every PR or push that touches engine files (`framework/`, `skills/`, `rules/`, `scripts/`, `templates/`, `.cursor/`, `.claude/`, `.github/`, tests).

## Blocking (must pass before merge)

1. **`bash scripts/pre_merge_check.sh`** exits 0 (tests + agnosticism + adapter sync).
2. **No project-specific leaks** in tracked engine files — customer names, private paths, real issue keys.
3. **No secrets** — tokens, `.env`, credentials in diff.
4. If `skills/` or `rules/` changed → **adapters synced** (`.cursor/`, `.claude/`, Copilot instructions).

## Review focus by change type

| Changed area | Reviewer checks |
|--------------|-----------------|
| `framework/rubric.yaml` | Signal IDs stable; `shapiro-levels.md` still authoritative |
| `skills/` | Provider-neutral wording; sync adapters committed |
| `scripts/` | Error paths tested; no hardcoded project paths |
| `templates/` | Placeholders only (`<slug>`, `<Project Name>`) |
| `tests/` | New behavior has a test; fixtures stay fictional |

## Severity (for human or agent review)

| Severity | Examples |
|----------|----------|
| **Block** | Leaked customer project name; broken scoring; tests fail |
| **Major** | Skill/adapter drift; missing test for new script behavior |
| **Minor** | Doc typo; unclear skill wording |
| **Nit** | Formatting only |

## Provider note

- **Cursor:** optional Bugbot pass — see skill `maturity-code-review`.
- **Other providers:** run the checklist in `skills/maturity-code-review/SKILL.md` manually.

Procedural how-to: skill `maturity-code-review`.
