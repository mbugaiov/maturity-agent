#!/usr/bin/env bash
# Start a new assessment run folder.
# Usage: scripts/new_assessment.sh <slug> <scope>
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SLUG="${1:-}"
SCOPE="${2:-baseline}"

if [[ -z "$SLUG" ]]; then
  echo "Usage: scripts/new_assessment.sh <slug> <scope>" >&2
  exit 1
fi

PROJ="$ROOT/projects/$SLUG"
if [[ ! -d "$PROJ" ]]; then
  echo "Error: project not found: $PROJ (run new_project.sh first)" >&2
  exit 1
fi

DATE="$(date +%Y-%m-%d)"
SAFE_SCOPE="$(echo "$SCOPE" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')"
RUN_DIR="$PROJ/assessments/${DATE}-${SAFE_SCOPE}"

if [[ -e "$RUN_DIR" ]]; then
  echo "Error: $RUN_DIR already exists." >&2
  exit 1
fi

mkdir -p "$RUN_DIR"

cp "$ROOT/templates/assessment.md" "$RUN_DIR/assessment.md"
cp "$ROOT/templates/evidence.yaml" "$RUN_DIR/evidence.yaml"
cp "$ROOT/templates/report.md" "$RUN_DIR/report.md"

# Fill placeholders in assessment + evidence
for f in "$RUN_DIR/assessment.md" "$RUN_DIR/evidence.yaml" "$RUN_DIR/report.md"; do
  if sed -i '' \
    -e "s|<slug>|$SLUG|g" \
    -e "s|<Project Name>|$(grep '^name:' "$PROJ/project.yaml" 2>/dev/null | sed 's/name: *"\(.*\)"/\1/' || echo "$SLUG")|g" \
    -e "s|<YYYY-MM-DD>-<scope>|${DATE}-${SAFE_SCOPE}|g" \
    -e "s|<scope>|${SAFE_SCOPE}|g" \
    -e "s|<YYYY-MM-DD>|${DATE}|g" \
    "$f" 2>/dev/null; then continue; fi
  sed -i \
    -e "s|<slug>|$SLUG|g" \
    -e "s|<scope>|${SAFE_SCOPE}|g" \
    -e "s|<YYYY-MM-DD>|${DATE}|g" \
    -e "s|<YYYY-MM-DD>-<scope>|${DATE}-${SAFE_SCOPE}|g" \
    "$f"
done

# Update project-memory pointer
MEM="$PROJ/project-memory.md"
if [[ -f "$MEM" ]]; then
  if grep -q '^active_assessment:' "$MEM" 2>/dev/null; then
    if sed -i '' "s|^active_assessment:.*|active_assessment: assessments/${DATE}-${SAFE_SCOPE}|" "$MEM" 2>/dev/null; then :; else
      sed -i "s|^active_assessment:.*|active_assessment: assessments/${DATE}-${SAFE_SCOPE}|" "$MEM"
    fi
  else
    echo "active_assessment: assessments/${DATE}-${SAFE_SCOPE}" >> "$MEM"
  fi
fi

echo "Created assessment: projects/$SLUG/assessments/${DATE}-${SAFE_SCOPE}/"
echo "  assessment.md  evidence.yaml  report.md"
