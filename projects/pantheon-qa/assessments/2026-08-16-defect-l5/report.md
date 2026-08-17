# Pantheon QA — maturity report (2026-08-16-defect-l5)

**Headline:** L5′ (L5 on STG)  
**Weighted:** 4.79 · **Operational:** 4 · **Floor:** 4  

## Refresh focus

Re-score after auto-file proof on GitHub Issues:

- `auto_file_confirmed_bugs: yes` — `create_bug_issue.py` → `github_create_issue.py`; ledger `bug_filed` for pantheon#128→#130 and #161→#163; `confirmed-defect` labels.
- `defect_loop` **L5** (was L0 on 2026-08-03-baseline).
- Rubric **v1.2**: `defect_loop` is not in the operational min — Op stays 4 (`factory_loop` L4).

## Reconciliation

Floor rises from 0 → 4 because the prior strict gap was `defect_loop` L0. Remaining floor drivers: `intent_spec` L4 / `factory_loop` L4 (`scheduled_ticks` partial).

## What blocks next

Unattended scheduler (`factory_loop` → L5) and optional GitHub `reopen_regression` (qa-agent#38) for full defect-loop parity — not auto-file.
