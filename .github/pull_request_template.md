## Summary

<!-- What changed and why (1–3 sentences) -->

## Type

- [ ] Engine feature
- [ ] Bug fix
- [ ] Docs / skills only
- [ ] Tests / CI

## Pre-merge checklist

- [ ] `bash scripts/pre_merge_check.sh` passes locally
- [ ] If `skills/` or `rules/` changed → `./scripts/sync_adapters.sh` committed with adapters
- [ ] No customer project names, private repo paths, or real issue keys in engine files
- [ ] No secrets or credentials in the diff
- [ ] `projects/*` data (except `_template/`) not included

## Test plan

- [ ] `bash tests/run_tests.sh`
- [ ] `bash scripts/check_engine_agnostic.sh`
- [ ] CI green on this PR

## Review notes

<!-- Optional: areas you want reviewers to focus on -->
