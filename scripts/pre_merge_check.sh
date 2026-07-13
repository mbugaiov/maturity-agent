#!/usr/bin/env bash
# Pre-merge gate: tests, engine agnosticism, adapter sync parity.
# Usage: scripts/pre_merge_check.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Running engine self-tests"
bash tests/run_tests.sh

echo "==> Checking engine agnosticism"
bash scripts/check_engine_agnostic.sh

echo "==> Checking provider adapter sync"
chmod +x scripts/sync_adapters.sh
./scripts/sync_adapters.sh >/dev/null

DRIFT=0
for path in .cursor/skills .cursor/rules/maturity-engine.mdc .claude/skills .github/copilot-instructions.md; do
  if ! git diff --quiet -- "$path" 2>/dev/null; then
    echo "DRIFT: $path differs after sync_adapters.sh — commit synced adapters"
    DRIFT=1
  fi
done

if [[ "$DRIFT" -ne 0 ]]; then
  exit 1
fi

echo "pre_merge_check: OK"
