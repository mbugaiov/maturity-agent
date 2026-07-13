---
name: maturity-report
description: Write the final Dan Shapiro maturity report from evidence and scores. Use after evidence.yaml is filled and score_assessment.py has run.
---

# Maturity report generation

## Input

- `assessments/<run>/evidence.yaml`
- `assessments/<run>/score.json` (from `score_assessment.py`)
- `framework/shapiro-levels.md`
- `projects/<slug>/intake.md` (prior headline, MANIFEST paths)

## Output

`assessments/<run>/report.md` from `templates/report.md`

## Headline rule (critical)

**Use `operational_level` and `headline_hint` from `score.json` for the headline** — not `floor_level`.

| score.json field | Report use |
|------------------|------------|
| `headline_hint` | Executive summary headline (first choice) |
| `operational_level` | Factory truth on target env |
| `floor_level` | Strict gaps narrative only |
| `headline_rule_matched` | Appendix / reconciliation |

If `operational_level` > `floor_level`, the **Reconciliation** section is **mandatory** — explain why (e.g. partial `scheduled_ticks` but armed loop runs).

## Report structure (required sections)

### 1. Executive summary (3–5 sentences)

- **Headline level** from `headline_hint` (e.g. L5′ on STG)
- **Operational vs floor** — one line each
- **One-line rationale**
- **Direction** (reaching next level / stable / regressed)

### 2. Reconciliation (mandatory when delta or prior exists)

Compare:
- `score.json` operational vs floor
- `meta.prior_headline` / intake prior assessment vs current evidence
- Prior slide/deck if user provided one

Explain mismatches explicitly — do not silently pick the lower number.

### 3. Factory program table (when MANIFEST exists)

| Ticket | Owner | Status | Citation |

Distinguish **Done** vs **deferred** — "11 Done + 1 deferred" is not "12/12 Done".

### 4. Level ladder visual (markdown table)

| Level | Status |
|-------|--------|
| L0–L3 | Past / N/A |
| L4 | ✓ achieved / partial |
| L5′ | ◀ current / in progress |
| L5 | not yet — blockers |

### 5. Dimension scorecard

| Dimension | Score | Key evidence |

Use `score.json` dimension levels; note `adjusted: true` on factory_loop when present.

### 6. Why this level (not higher)

Bullet list of **blocking signals** still `no` or `partial` for next level.
Use **floor** drivers here, not operational strengths.

### 7. Path to next level

3–7 concrete actions — prefer **ticket-shaped** backlog items:
- Dev: machine DoD, auto-merge, buildId gate
- QA: auto-accept, factory ledger
- Policy: needs-human doc
- Loop: `scheduled_ticks` yes (fully unattended arm)

Copy gap items to `templates/gap-backlog.md` snippet if the user wants issue-tracker filing.

### 8. Worked trace (optional but valuable)

One ticket walked end-to-end — proves or disproves factory claim.

### 9. Comparison to prior assessment

If `project-memory.md` or `prior_headline` exists — delta table.

## Tone

- Evidence-based, not promotional
- Acknowledge **L5′** honestly when PROD is human-gated
- Do not claim L5 without unattended PROD + multi-product proof
- Do not headline `floor_level` when factory runs at L5′ operationally

## Slides / executive deck

Use skill **`maturity-presentation`** after this report is complete:

```bash
python3 scripts/build_presentation.py <assessment-dir>
```

Produces `presentation.html` (Reveal.js) + `presentation.md` — methodology, current level, gaps, path to next level.
