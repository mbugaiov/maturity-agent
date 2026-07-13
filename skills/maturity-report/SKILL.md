---
name: maturity-report
description: Write the final Dan Shapiro maturity report from evidence and scores. Use after evidence.yaml is filled and score_assessment.py has run.
---

# Maturity report generation

## Input

- `assessments/<run>/evidence.yaml`
- `assessments/<run>/score.json` (from `score_assessment.py`)
- `framework/shapiro-levels.md`

## Output

`assessments/<run>/report.md` from `templates/report.md`

## Report structure (required sections)

### 1. Executive summary (3–5 sentences)

- **Headline level** (e.g. L4, or L5′ on STG)
- **One-line rationale**
- **Direction** (reaching next level / stable / regressed)

### 2. Level ladder visual (markdown table)

| Level | Status |
|-------|--------|
| L0–L3 | Past / N/A |
| L4 | ✓ achieved / partial |
| L5′ | ◀ current / in progress |
| L5 | not yet — blockers |

### 3. Dimension scorecard

| Dimension | Score | Key evidence |
|-----------|-------|--------------|
| intent_spec | L4 | … |

Use `score.json` dimension levels; add strongest citation per row.

### 4. Why this level (not higher)

Bullet list of **blocking signals** still `no` or `partial` for next level.

### 5. Path to next level

3–7 concrete actions — prefer **ticket-shaped** backlog items:
- Dev: machine DoD, auto-merge, buildId gate
- QA: auto-accept, factory ledger
- Policy: needs-human doc

Copy gap items to `templates/gap-backlog.md` snippet if the user wants issue-tracker filing.

### 6. Worked trace (optional but valuable)

One ticket walked end-to-end — proves or disproves factory claim.

### 7. Comparison to prior assessment

If `project-memory.md` has previous level — delta table.

## Tone

- Evidence-based, not promotional
- Acknowledge **L5′** honestly when PROD is human-gated
- Do not claim L5 without unattended PROD + multi-product proof

## Slides / executive deck

Use skill **`maturity-presentation`** after this report is complete:

```bash
python3 scripts/build_presentation.py <assessment-dir>
```

Produces `presentation.html` (Reveal.js) + `presentation.md` — methodology, current level, gaps, path to next level.
