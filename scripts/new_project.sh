#!/usr/bin/env bash
# Create a new per-project maturity workspace from projects/_template.
# Usage: scripts/new_project.sh <slug> ["Display Name"]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$ROOT/projects/_template"

SLUG="${1:-}"
NAME="${2:-$SLUG}"

if [[ -z "$SLUG" ]]; then
  echo "Usage: scripts/new_project.sh <slug> [\"Display Name\"]" >&2
  exit 1
fi
if [[ ! "$SLUG" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "Error: slug must be lowercase letters, digits, and hyphens." >&2
  exit 1
fi

DEST="$ROOT/projects/$SLUG"
if [[ -e "$DEST" ]]; then
  echo "Error: $DEST already exists." >&2
  exit 1
fi

cp -R "$TEMPLATE" "$DEST"
mkdir -p "$DEST/.secrets" "$DEST/assessments"

subst() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  if sed -i '' \
    -e "s|<Project Name>|$NAME|g" \
    -e "s|<slug>|$SLUG|g" \
    -e "s|slug: \"<slug>\"|slug: \"$SLUG\"|" \
    -e "s|name: \"<Project Name>\"|name: \"$NAME\"|" \
    "$f" 2>/dev/null; then return 0; fi
  sed -i \
    -e "s|<Project Name>|$NAME|g" \
    -e "s|<slug>|$SLUG|g" \
    -e "s|slug: \"<slug>\"|slug: \"$SLUG\"|" \
    -e "s|name: \"<Project Name>\"|name: \"$NAME\"|" \
    "$f"
}

for f in "$DEST/project.yaml" "$DEST/project-memory.md" "$DEST/README.md" "$DEST/intake.md"; do
  subst "$f"
done

# Seed intake from template if not copied
if [[ ! -f "$DEST/intake.md" ]]; then
  cp "$ROOT/templates/intake.md" "$DEST/intake.md"
  subst "$DEST/intake.md"
fi

echo "Created project: projects/$SLUG"
echo "Next:"
echo "  1. Edit projects/$SLUG/intake.md (repos, agents, CI)"
echo "  2. scripts/new_assessment.sh $SLUG baseline"
echo "  3. Ask agent: Assess projects/$SLUG against Dan Shapiro framework"
