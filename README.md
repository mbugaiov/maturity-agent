# Maturity Agent

Agent-driven **SDLC maturity assessment** using [Dan Shapiro's Five-Level Framework](framework/shapiro-levels.md) for AI-assisted software development.

**CI:** see [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — runs `pre_merge_check.sh` on every push and PR.

Point the agent at a project (repo, agent setup, pipeline, issue tracker) and it collects evidence, scores dimensions, and produces a structured maturity report — instead of ad-hoc "we're probably Level 4" guesses.

## One project = one folder · one engagement = one assessment

The **engine** (`AGENTS.md`, `framework/`, `templates/`, `scripts/`, `skills/`, `rules/`) is shared and **provider-neutral** — adapters for Cursor, Claude, Copilot, and Codex are synced via `scripts/sync_adapters.sh` (see `PROVIDERS.md`).
Each **target system** gets one folder under `projects/<slug>/`.
Each **assessment** is a dated run inside that project:

```
scripts/new_assessment.sh <slug> "<scope>"
  → projects/<slug>/assessments/<YYYY-MM-DD>-<scope>/
```

## Quickstart

1. **Create a project** (copies skeleton from `projects/_template/`):

   ```bash
   scripts/new_project.sh acme "Acme Shop SDLC"
   ```

2. **Fill intake** — edit `projects/acme/intake.md` (agents, CI, spec source, deploy target).

3. **Start an assessment**:

   ```bash
   scripts/new_assessment.sh acme baseline
   ```

4. **Ask the agent** (any provider — see `PROVIDERS.md`):

   > Assess `projects/acme` against Dan Shapiro's framework. Use the baseline assessment folder, collect evidence from the linked repos, and write the report.

5. **Optional — machine score** (after evidence YAML is filled):

   ```bash
   python3 scripts/score_assessment.py projects/acme/assessments/<date>-baseline
   ```

   `score.json` (rubric v1.1) exposes:
   - **`headline_hint`** — use in `report.md` (from `level_headline_rules`)
   - **`operational_level`** — factory truth on STG
   - **`floor_level`** — strict min for gap narrative only

   Helper scripts for discovery: `scripts/collect_ci_signals.sh <repo>`, `scripts/verify_factory_manifest.sh <MANIFEST.md>`.

6. **Build presentation** (after report):

   ```bash
   python3 scripts/build_presentation.py projects/acme/assessments/<date>-baseline
   open projects/acme/assessments/<date>-baseline/presentation.html
   ```

## Tests & CI

```bash
pip install -r requirements.txt
bash scripts/pre_merge_check.sh
```

GitHub Actions runs the same gate on every push and PR (`.github/workflows/ci.yml`).

## Docs

| File | Purpose |
|------|---------|
| `AGENTS.md` | Assessment loop + skill index |
| `CONTRIBUTING.md` | PR workflow + code review |
| `PROVIDERS.md` | Cursor, Claude, Copilot, Codex adapters |
| `SETUP.md` | Onboarding a new target project |
| `PORTABILITY.md` | Engine vs project data split |
| `framework/shapiro-levels.md` | L0–L5 definitions |
| `framework/rubric.yaml` | Machine-readable scoring rubric |
| `framework/signals.md` | Human-readable signal catalog |

## What it evaluates

| Dimension | Examples |
|-----------|----------|
| Intent & spec | Jira tickets, OpenSpec, PRD ownership |
| Agent topology | dev / CR / QA roles, independence |
| Dev autonomy | OpenSpec → MR → merge → STG deploy |
| Review gate | blocking CR, pipeline fail on review |
| QA autonomy | auto-accept, buildId gate, two-pass |
| Provenance | handoff comments, ledger, recordings |
| Human boundaries | `needs-human`, PROD gate, intent owner |
| Factory loop | unattended scheduler, tick cadence |
| Portability | `_template`, multi-repo, second product |

## Not in scope

- Replacing human judgment on ambiguous cases — the agent **recommends** a level with evidence.
- Auditing application code quality — this measures **process / agent / pipeline** maturity only.
