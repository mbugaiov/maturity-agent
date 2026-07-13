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
| Product app | | `main` | |
| Agent tooling | | | optional separate repo |
| Dev agent config | | | e.g. `.cursor/`, `.claude/`, `AGENTS.md` |
| Docs / runbooks | | | optional |

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

## Pipeline & environments

| Item | Value |
|------|-------|
| CI | GitHub Actions / Bitbucket / other |
| Auto-deploy target | STG / preview / none |
| PROD deploy | automated / human-gated / n/a |
| buildId endpoint | e.g. `/api/health` |

## Factory loops (declared)

| Loop | Running? | Cadence | Script / skill |
|------|----------|---------|----------------|
| Dev factory | | | |
| QA factory | | | |

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
