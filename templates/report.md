# SDLC Maturity Report — <Project Name>

**Framework:** Dan Shapiro Five Levels  
**Assessment:** `<YYYY-MM-DD>-<scope>`  
**Date:**  
**Assessor:**

---

## Executive summary

**Headline level:**  

**Operational level (score.json):**  
**Floor level (strict gaps):**  

**Rationale:**  

**Trend vs prior:** stable | improved | regressed | first assessment

---

## Reconciliation

> Required when `operational_level` ≠ `floor_level`, or when `prior_headline` exists in intake/evidence.

| Source | Claim | Evidence | Match? |
|--------|-------|----------|--------|
| score.json operational | | | |
| score.json floor | | | |
| Prior slide / report | | | |

**Delta explanation:**  

---

## Factory program (shipped backlog)

> Fill when `factory_manifest` or factory ticket program exists.

| Ticket | Owner | Status | Citation |
|--------|-------|--------|----------|
| | dev / qa | Done / deferred | run log or MANIFEST |

**Program summary:** Done / deferred / total

---

## Level ladder

| Level | Label | Status |
|-------|-------|--------|
| L0 | Spicy autocomplete | |
| L1 | Coding intern | |
| L2 | Junior developer | |
| L3 | Developer | |
| L4 | Engineering team | |
| L5′ | L5 on STG | |
| L5 | Dark software factory | |

---

## Dimension scorecard

| Dimension | Level | Confidence | Key evidence |
|-----------|-------|------------|--------------|
| intent_spec | | | |
| agent_topology | | | |
| dev_autonomy | | | |
| review_gate | | | |
| deploy_verification | | | |
| qa_autonomy | | | |
| defect_loop | | | |
| provenance | | | |
| human_boundaries | | | |
| factory_loop | | | |
| portability | | | |

**Floor level (min dimension):**  
**Operational level (factory-critical min):**  
**Weighted level (score.json):**  
**Headline rule matched:**  

---

## Why this level

### Strengths (signals at yes)

- 

### Gaps (blocking next level)

- 

---

## Path to next level

| Priority | Action | Owner | Maps to signal |
|----------|--------|-------|----------------|
| P1 | | dev / qa / human | |
| P2 | | | |

---

## Worked example (ticket trace)

| Step | Actor | Automated? | Evidence |
|------|-------|------------|----------|
| Spec written | Human | — | |
| Implementation | Dev agent | | |
| Review | CR agent | | |
| Merge | | | |
| Deploy | | | |
| QA retest | QA agent | | |
| Done | | | |

---

## Appendix

- Full evidence: `evidence.yaml`
- Machine scores: `score.json`
- Rubric version: `framework/rubric.yaml` v1.1
