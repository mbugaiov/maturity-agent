# Signal catalog (human-readable)

Maps each rubric dimension to **what to look for** when interviewing or inspecting repos.
Machine scoring uses `rubric.yaml`; this file is the assessor's field guide.

## 1. intent_spec — Who writes the spec?

| Level | What you should see |
|-------|---------------------|
| L0–L2 | Ad-hoc prompts; no durable spec artifact |
| L3 | Tickets or docs, but agent prompt is the real spec |
| L4 | Humans write Jira/Linear tickets + structured acceptance; OpenSpec/PRD optional |
| L5 | Plain-English / ticket is the **only** input; agents never invent scope |

**Inspect:** spec directory, issue ticket templates, epic/program children.

## 2. agent_topology — How many agents?

| Level | What you should see |
|-------|---------------------|
| L0–L2 | Single chat session |
| L3 | One "do everything" agent |
| L4 | **≥2 specialized roles** (e.g. dev + QA, or dev + CR) with written boundaries |
| L5 | Dev + CR + QA (or equivalent) + schedulers; CR never picks Jira tickets |

**Inspect:** `AGENTS.md`, agent rules/skills dir (`.cursor/rules/`, `.claude/skills/`, `rules/`, etc.), agent ownership manifest or table.

## 3. dev_autonomy — Build and handoff

| Level | What you should see |
|-------|---------------------|
| L3 | Agent opens PR; human merges |
| L4 | Agent implements from OpenSpec; human merges and deploys |
| L5 | Agent merges (squash) when pipeline green; posts machine handoff to Jira |

**Inspect (priority order):**
1. **Product CI YAML** — `bitbucket-pipelines.yml`, `.github/workflows/*.yml` for `auto_merge`, squash step
2. Scripts — `auto_merge_pr.sh`, `agent_squash_merge` pipeline step
3. Machine DoD doc, handoff comment formatter

**Anti-pattern:** workflow *prose* saying "human merge" does **not** override a shipped `auto_merge` step in product CI. Record `per_repo.product` in evidence when engine and product CI differ.

## 4. review_gate — Code review

| Level | What you should see |
|-------|---------------------|
| L3 | Human review optional |
| L4 | CR agent or mandatory human review; not always blocking CI |
| L5 | **Blocking** review — pipeline fails on CR blocking findings |

**Inspect (priority order):**
1. **Product CI YAML** — `check_review_gate.sh`, `review_gate`, blocking CR step
2. Engine CI (secondary — may differ from shipping repo)
3. `review.md` / Bugbot integration

**Per-repo:** `blocking_review_ci` is **yes** when the **product** (shipping) pipeline fails on blocking CR findings.

## 5. deploy_verification — Environment truth

| Level | What you should see |
|-------|---------------------|
| L4 | Deploy exists; QA may test wrong build |
| L5 | **buildId gate** — live `/api/health` (or equivalent) matches merge commit before QA Done |

**Inspect:** buildId gate script, health endpoint check, handoff comments with commit SHA.

## 6. qa_autonomy — Test and accept

| Level | What you should see |
|-------|---------------------|
| L3 | Human QA or ad-hoc agent test |
| L4 | QA agent + human clicks Done |
| L5 | **Auto-accept** when machine DoD (two-pass PASS + buildId + recording) |

**Inspect:** QA agent rules/skills, end-of-tick DoD gate script.

## 7. defect_loop — Bugs and regressions

| Level | What you should see |
|-------|---------------------|
| L4 | Human files bugs |
| L5 | **Auto-file** confirmed defects; **reopen** regressions; dedupe via Jira |

**Inspect:** auto-file bug script, regression reopen script, confirmed-defect label flow.

## 8. provenance — Audit trail

| Level | What you should see |
|-------|---------------------|
| L4 | Git + Jira comments |
| L5 | OpenSpec deltas + Jira handoff + QA recordings + JSONL factory ledger |

**Inspect:** `factory/runs/*.jsonl`, ticket comment templates, `run.md` tick logs.

## 9. human_boundaries — What stays human?

| Level | What you should see |
|-------|---------------------|
| L4 | Humans own intent + acceptance (expected) |
| L5 | Only **intent**, **needs-human**, **PROD/infra** — documented policy |

**Inspect:** `L5-HUMAN-EXCEPTIONS.md` or equivalent, `needs-human` verdict path, PROD gate tickets.

## 10. factory_loop — Unattended operation

| Level | What you should see |
|-------|---------------------|
| L4 | On-demand agent sessions |
| L5 | **Scheduled ticks** — dev factory + QA factory drain queues until idle |

**Inspect:** loop scheduler scripts, cadence in `project-memory.md`, cron or armed watcher, `factory/runs/*.jsonl`, factory MANIFEST.

### `scheduled_ticks` answer guide

| Answer | Criteria |
|--------|----------|
| **yes** | Loop armed and draining on cadence without per-ticket manual start |
| **partial** | Arm once per session/week (`/loop`, `arm_*_loop.sh`), then unattended ticks |
| **no** | Every tick requires manual chat/session start |

**Scoring note:** `partial` + `tick_gate: yes` → `factory_loop` boosted to ≥ L4 (operational L5′). Strict L5 still needs `scheduled_ticks: yes`.

### `factory_backlog_complete` (optional)

| Answer | Criteria |
|--------|----------|
| **yes** | Factory program MANIFEST shows shipped tickets Done + run traces |
| **partial** | Some Done, known deferred items documented |
| **no** | No MANIFEST or program incomplete |

## 11. portability — Second product

| Level | What you should see |
|-------|---------------------|
| L4 | One product hardcoded |
| L5 | `_template`, slug-parameterized scripts, second repo onboarded |

**Inspect:** `projects/_template/`, `new_project.sh`, `PORTABILITY.md`, second-repo onboarding proof.

## Illustrative scoring (fictional)

Use only to sanity-check the rubric — **never** as default evidence for a real assessment.

| Dimension | Fictional evidence | Level |
|-----------|-------------------|-------|
| intent_spec | Epic PROG-100 + OpenSpec scenarios | L4+ |
| agent_topology | dev + CR + QA with ownership doc | L4+ |
| dev_autonomy | machine DoD + auto-merge on green CI | L5′ |
| review_gate | blocking review fails pipeline | L5′ |
| deploy_verification | buildId gate on staging | L5′ |
| qa_autonomy | auto-accept when machine DoD met | L5′ |
| defect_loop | auto-file confirmed bugs | L5′ |
| provenance | JSONL or equivalent factory ledger | L5′ |
| human_boundaries | needs-human policy; PROD gated | L4 (blocks full L5) |
| factory_loop | scheduled dev + QA ticks | L5′ |
| portability | second product not yet proven | L4 |

**Headline (fictional):** L5′ on staging (~90%); full L5 lower until PROD + multi-product are unattended.
