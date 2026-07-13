# Maturity Agent — setup

## 1. Clone / open engine

```bash
cd maturity-agent   # open as workspace (Cursor, VS Code+Copilot, Claude Code, etc.)
```

See `PROVIDERS.md` for provider-specific entry points.

## 2. Create a target project

```bash
chmod +x scripts/*.sh
scripts/new_project.sh acme "Acme SDLC"
```

## 3. Fill intake

Edit `projects/acme/intake.md`:

- Linked repo paths (product app, agent tooling, CI config)
- Agent topology table
- CI / deploy / issue tracker keys
- One known closed-loop ticket (if any)

## 4. Start assessment

```bash
scripts/new_assessment.sh acme baseline
```

## 5. Run agent assessment

With your AI provider (see `PROVIDERS.md`):

> Assess `projects/acme` using skill `maturity-assess`. Read linked repos, fill `evidence.yaml`, run `score_assessment.py`, write `report.md`.

## 6. Machine score (optional)

```bash
pip install pyyaml   # once
python3 scripts/score_assessment.py projects/acme/assessments/<date>-baseline
```

## 7. Re-assessment

When the SDLC changes (new factory capabilities shipped):

```bash
scripts/new_assessment.sh acme follow-up
```

Compare `report.md` to prior run; update `project-memory.md` trend.

## 8. Build presentation

```bash
python3 scripts/build_presentation.py projects/acme/assessments/<date>-baseline
open projects/acme/assessments/<date>-baseline/presentation.html
```

See skill `maturity-presentation` for slide structure and agent enrichment.

## Linking repos (no symlinks required)

- **Submodule:** `git submodule add <url> projects/acme-data` — if assessment data lives in a separate repo
- **Sibling workspace:** open a parent folder containing `maturity-agent/` and target repos; record absolute paths in `intake.md`
- **Monorepo:** relative paths like `../apps/product`, `../tooling/qa`

See `PORTABILITY.md` for layout rules.

## Dependencies

| Tool | Purpose |
|------|---------|
| Python 3.9+ | `score_assessment.py` |
| PyYAML | rubric/evidence parsing (`pip install pyyaml`) |
| AI agent (any provider) | interview + report — see `PROVIDERS.md` |
| `gh` / Jira API | optional read-only ticket traces |

## Pre-push checklist (engine maintainers)

- [ ] `bash scripts/pre_merge_check.sh` passes (tests + agnosticism + adapter sync)
- [ ] `projects/*` except `_template/` not committed

CI runs the same gates on every push to `master` (see `.github/workflows/ci.yml`).
