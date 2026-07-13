#!/usr/bin/env bash
# Build presentation.html + presentation.md from assessment artifacts.
# Usage: scripts/build_presentation.sh <assessment-dir> ["Display Title"]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DIR="${1:-}"
TITLE="${2:-}"

if [[ -z "$DIR" ]]; then
  echo "Usage: build_presentation.sh <assessment-dir> [\"Display Title\"]" >&2
  exit 1
fi

ARGS=("$ROOT/scripts/build_presentation.py" "$DIR")
[[ -n "$TITLE" ]] && ARGS+=(--title "$TITLE")

python3 "${ARGS[@]}"
