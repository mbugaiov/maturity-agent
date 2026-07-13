# Intake — <Project Name>

> Static facts about the SDLC under assessment. Update when the setup changes.

## Identity

| Field | Value |
|-------|-------|
| **Slug** | `<slug>` |
| **Display name** | `<Project Name>` |
| **Assessed by** | |
| **Date** | |

## Linked repositories

| Role | Path or URL | Branch | Notes |
|------|-------------|--------|-------|
| Product app | | `main` | **shipping repo — CI here is authoritative** |
| Agent tooling | | | optional separate repo |
| Dev agent config | | | e.g. `.cursor/`, `.claude/`, `AGENTS.md` |
| Docs / runbooks | | | optional |

### CI config paths (explicit)

| Repo role | CI file path(s) |
|-----------|-----------------|
| Product | e.g. `bitbucket-pipelines.yml` |
| Agent tooling | e.g. `.github/workflows/ci.yml` |

## Agent topology (declared)

| Agent | Exists? | Repo / path | Picks Jira queue? |
|-------|---------|-------------|-------------------|
| Dev | | | dev factory queue / manual |
| Code review | | | PR only |
| QA | | | qa factory queue / manual |

## Spec & tracking

| Item | Value |
|------|-------|
| Ticket system | Jira / Linear / GitHub Issues / none |
| Epic / program key | |
| OpenSpec | yes / no — path |
| PRD / requirements path | |
| Factory MANIFEST path | e.g. `requirements/factory-tickets/MANIFEST.md` |
| Epic Done snapshot | e.g. 11 Done + 1 deferred (date) |

## Pipeline & environments

| Item | Value |
|------|-------|
| CI | GitHub Actions / Bitbucket / other |
| Auto-deploy target | STG / preview / none |
| PROD deploy | automated / human-gated / n/a |
| buildId endpoint | e.g. `/api/health` |

## Factory loops (declared)

| Loop | Running? | Cadence | Arm method | Script / skill |
|------|----------|---------|------------|----------------|
| Dev factory | | e.g. 5m | `/loop`, `arm_*_loop.sh`, cron, manual | |
| QA factory | | | | |

## Prior assessment (reconciliation)

| Field | Value |
|-------|-------|
| Prior headline | e.g. L5′ on STG ~90% |
| Prior source | slide / report / stakeholder |
| Prior date | |

## Stakeholders (optional)

| Role | Contact | Notes |
|------|---------|-------|
| PM / intent owner | | |
| Platform / infra | | |

## Known closed-loop examples

Tickets that demonstrate filed → fixed → deployed → verified → Done:

1. 
2. 

## Open questions

- 
