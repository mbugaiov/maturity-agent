# AI Support Agent — maturity report (2026-09-07-baseline)

**Headline:** L5′ (L5 on STG)  
**Weighted:** 4.53 · **Operational:** 4 · **Floor:** 0  

## Why this level

Rubric v1.2 matched `L5′ (L5 on STG)`:

- Delivery loop (dev / review / deploy / QA / factory) is operational on AWS STG
- `prod_human_gated: yes` (STG-only factory deploy)
- `factory_loop` adjusted to **4** (`scheduled_ticks` partial + tick gate + backlog complete)

## Dimension map (from `score.json`)

| Dimension | Level | Notes |
|-----------|------:|-------|
| intent_spec | 5 | Jira RQ-2222 + OpenSpec + BA_SPEC_READY |
| agent_topology | 5 | Hermes / Athena / Hephaestus / Argus / Themis |
| dev_autonomy | 5 | PR + auto-merge + Validate/Testing handoff |
| review_gate | 5 | Themis review + isolation + `check_review_gate` |
| deploy_verification | 5 | main → EC2 STG; `/health` buildId MATCH |
| qa_autonomy | 5 | Argus Done after dod_check + verdict_review |
| defect_loop | 0 | **No** `bug_filed` proof on this slug yet |
| provenance | 5 | JSONL ledger + Jira handoff fields |
| human_boundaries | 5 | needs-human / factory-pause labels |
| factory_loop | 4 | Kairos 300s armed; QA often oneshot |
| portability | 5 | Shared engines; second+ product after LRM/Pantheon |

## Reconciliation

Floor **0** is driven solely by `defect_loop` (mandatory `auto_file_confirmed_bugs` unmet).  
Operational **4** ignores defect_loop (v1.2) and reflects factory_loop L4.

## Evidence anchors (do not invent)

- Product CI: `bitbucket-pipelines.yml` (gate ∥ Themis ∥ isolation → auto-merge → deploy-stg)
- Closed loop: `qa-agent/projects/ai-support-agent/factory/runs/RQ-2383.jsonl` — buildId MATCH `ba000f35b07b` → Done
- Live STG (2026-09-07): `GET http://52.37.240.170:8000/health` → `git_sha=ba000f35b07b`
- Ops allowlist: `theia-agent/config/host.yaml`, `kairos-agent/config/portfolio.yaml`

## What blocks next

1. **Defect loop L5** — ship one confirmed FAIL → `create_bug_issue.py` → `bug_filed` ledger row (raises floor).
2. **Factory loop L5** — prove unattended Argus ticks (not only oneshot) under Kairos cadence.
3. Pantheon `/metis` — consume `exports/ai-support-agent/latest.json` (pantheon#737 follow-up already prepared pending row).

## Export

```bash
python3 scripts/export_scorecard.py --slug ai-support-agent
# → exports/ai-support-agent/latest.json
```
