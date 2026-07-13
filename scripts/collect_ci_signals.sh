#!/usr/bin/env bash
# Grep a repo for common CI factory signals (auto-merge, blocking CR, buildId).
# Usage: scripts/collect_ci_signals.sh <repo-path>
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: collect_ci_signals.sh <repo-path>" >&2
  exit 1
fi

REPO="$(cd "$1" && pwd)"
cd "$REPO"

PATTERNS=(
  'auto_merge'
  'auto-merge'
  'check_review_gate'
  'review_gate'
  'buildid'
  'buildId'
  'build_id'
)

echo "# CI signal scan: $REPO"
echo ""

for pat in "${PATTERNS[@]}"; do
  echo "## pattern: $pat"
  git grep -nEi "$pat" -- \
    'bitbucket-pipelines.yml' \
    '.github/workflows' \
    'scripts' \
    2>/dev/null || echo "(no matches)"
  echo ""
done
