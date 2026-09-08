# My Sol-Ark QA Automation — maturity report (2026-09-07-baseline)

**Headline:** L5′ (L5 on STG) — *rubric mechanical*  
**Weighted:** 4.42 · **Operational:** 4 · **Floor:** 0  

## Framing (read first)

This slug is a **QA automation forge** (pytest/Playwright), not a shipping product app.

- Merges update `qa_mysolark_regressiontest` only — they do **not** redeploy My Sol-Ark.
- `auto_deploy_nonprod` / `buildid_gate` scored **`na`** (not missing) for that reason.
- Headline L5′ means: multi-seat factory with human policy gates (BB Approve + no PROD path) — **not** “product STG dark factory like ai-support / pantheon”.

## Why this level

Delivery-loop dims score high once deploy signals are `na`; `factory_loop` adjusts to **4** (Kairos armed but human Approve stalls ticks). Floor **0** from `defect_loop`.

## Dimension map

| Dimension | Level | Notes |
|-----------|------:|-------|
| intent_spec | 4 | No BA seat; agents_do_not_invent_scope partial |
| agent_topology | 5 | Dev + QA + Cursor CR |
| dev_autonomy | 5 | Handoff yes; **auto_merge no** (human Approve) |
| review_gate | 5 | composer-2.5 Cursor review + gate |
| deploy_verification | 5 | **na** deploy/buildId (forge shape) |
| qa_autonomy | 5 | RQ-533 Done path |
| defect_loop | 0 | no bug_filed proof |
| provenance | 5 | JSONL ledger |
| human_boundaries | 5 | Approves + needs-human labels |
| factory_loop | 4 | scheduled_ticks partial |
| portability | 5 | shared engines |

## Evidence anchors

- Closed loop: `factory/runs/RQ-533.jsonl` → Done (`buildid_gate=SKIP`)
- Human gate: RQ-526/RQ-534 SKIP_DEV awaiting non-author Approve
- Ops: pantheon#557 Done; Kairos/Theia allowlisted

## What blocks next

1. Agent auto-merge (or waive Approves for factory bots) — raises real unattended cadence
2. Defect auto-file proof
3. Pantheon `/metis` row — consume export only; label as automation forge

## Export

`exports/qa-mysolark-regressiontest/latest.json`
