# Dan Shapiro — Five Levels of AI-Assisted Software Development

Inspired by SAE autonomous-driving levels. This file is the **authority** for level names and meanings.
Observable signals live in `rubric.yaml` and `signals.md`.

## Level 0 — Spicy Autocomplete

The AI suggests completions; the human writes all code and owns all decisions.

**Typical signals:** Copilot/Tab only; no agent loop; no spec-driven handoff.

## Level 1 — Coding Intern

The human gives **atomic, in-file** tasks; reviews **every line** of output.

**Typical signals:** "add a test", "fix this function"; single-file scope; no autonomous multi-step runs.

## Level 2 — Junior Developer

**Multi-file** awareness; pair-programming; human **approves all code** before merge.

**Typical signals:** Cursor Agent on a feature branch; human merges; no separate QA/CR agents.

## Level 3 — Developer

The AI runs **multi-step tasks**; the human role shifts to **reviewing diffs** and course correction.

**Typical signals:** Agent implements a ticket with tests; human reviews PR; QA may still be manual/human.

## Level 4 — Engineering Team

The human acts as **PM / spec author** — writes intent (tickets, specs); AI **develops and tests** with separate concerns (dev, review, QA).

**Typical signals:**
- Spec source of truth (Jira, OpenSpec, PRD) written by humans
- Multiple specialized agents or roles (dev, CR, QA)
- Deploy to non-prod (e.g. STG) after merge
- Humans own **intent** and **final acceptance**

## Level 5 — Dark Software Factory

**Spec in → software out** — AI implements, tests, debugs, and ships with **no human in the routine loop**.

**Typical signals:**
- Unattended factory loops (dev + QA schedulers)
- Auto-merge when gates green
- Auto-accept when machine DoD met
- Provenance chain (spec → code → deploy → test → Done) without human clicks
- Humans only for intent, policy exceptions, infra/PROD gates

**Sub-level used in practice:** **L5′ (L5 on STG)** — full factory on staging; PROD and multi-product still human-gated.

## How to pick a single headline level

Use **two scores** from `score.json` — they answer different questions:

| Field | Question | Use in report |
|-------|----------|---------------|
| **operational_level** | Does the factory run on the target env (STG)? | **Headline level** |
| **floor_level** | What is the strict minimum across all dimensions? | **Gaps / blockers** |

1. Find the **highest level where routine delivery works without human intervention** on the target environment → `operational_level`.
2. If humans still **must** click Accept/Merge/Deploy for every ticket → cap at **L3–L4**.
3. If only **intent + exceptions** are human → **L5′** or **L5** (see `level_headline_rules` in `rubric.yaml`).
4. **Do not** use `floor_level` as the headline when `operational_level` is higher — explain the delta in a **Reconciliation** section (e.g. armed loop = partial `scheduled_ticks` but factory still runs).
5. Report as **headline** + **direction** + **% factory complete** when useful.

### L5′ operational vs strict L5

| Signal | Strict L5 | L5′ operational |
|--------|-----------|-----------------|
| `scheduled_ticks` | yes (fully unattended arm) | partial OK if armed loop + cadence runs |
| `prod_human_gated` | no (unattended PROD) | yes (STG factory, human PROD) |
| `factory_backlog_complete` | optional proof | MANIFEST Done + run traces boost confidence |

## What this framework does *not* measure

- Code quality, security posture, or team skill
- Whether the product is valuable
- Compliance certifications

It measures **automation of the software delivery loop** given AI agents and tooling.
