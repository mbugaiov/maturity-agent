#!/usr/bin/env bash
# Summarize factory MANIFEST ticket statuses (Done / deferred / other).
# Usage: scripts/verify_factory_manifest.sh <path-to-MANIFEST.md>
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: verify_factory_manifest.sh <MANIFEST.md>" >&2
  exit 1
fi

MANIFEST="$1"
if [[ ! -f "$MANIFEST" ]]; then
  echo "Not found: $MANIFEST" >&2
  exit 1
fi

DONE=$(grep -ciE '\bDone\b' "$MANIFEST" || true)
DEFERRED=$(grep -ciE '\bdeferred\b' "$MANIFEST" || true)
TODO=$(grep -ciE '\b(To Do|TODO|In Progress)\b' "$MANIFEST" || true)

echo "# Factory MANIFEST summary: $MANIFEST"
echo "done_mentions: $DONE"
echo "deferred_mentions: $DEFERRED"
echo "open_mentions: $TODO"

if [[ "$DEFERRED" -gt 0 ]]; then
  echo "factory_backlog_complete: partial"
elif [[ "$DONE" -gt 0 && "$TODO" -eq 0 ]]; then
  echo "factory_backlog_complete: yes"
else
  echo "factory_backlog_complete: partial"
fi
