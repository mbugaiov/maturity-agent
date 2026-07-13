#!/usr/bin/env bash
# Engine agnosticism gate: tracked files must not hardcode customer projects or private paths.
#
# Usage: scripts/check_engine_agnostic.sh
# Exit 0 = clean. Exit 1 = forbidden pattern found.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

FORBIDDEN='(RQ-[0-9]+|\blrm\b|qa-agent|colibri|lab-test|sol-ark|solark|mbugaiov|/Users/max/)'

PATHS=(
  .cursor
  .claude
  .github
  framework
  skills
  rules
  scripts
  templates
  tests
  AGENTS.md
  CLAUDE.md
  PROVIDERS.md
  README.md
  SETUP.md
  PORTABILITY.md
  INTEGRATIONS.md
  CONTRIBUTING.md
)

FAIL=0
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    echo "$line" | grep -q 'FORBIDDEN' && continue
    echo "$line" | grep -q 'Pre-push checklist' && continue
    echo "$line" | grep -q 'project-agnostic' && continue
    echo "$line" | grep -q 'engine-agnostic' && continue
    echo "$line" | grep -q 'no hits' && continue
    echo "$line" | grep -q 'test_negative_gates.sh' && continue
    echo "engine leak: $line"
    FAIL=1
  done < <(git grep -nEi "$FORBIDDEN" -- "$f" 2>/dev/null || true)
done < <(git ls-files "${PATHS[@]}" 2>/dev/null || true)

if [[ "$FAIL" -eq 0 ]]; then
  echo "engine-agnostic: OK (no project-specific leaks in tracked files)"
fi
exit "$FAIL"
