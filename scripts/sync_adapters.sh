#!/usr/bin/env bash
# Sync canonical skills/ and rules/ to provider-specific adapter locations.
# Run after editing skills/ or rules/ — commit canonical + adapters together.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SKILLS=(maturity-assess maturity-interview maturity-report maturity-presentation)

sync_skills() {
  local dest="$1"
  mkdir -p "$dest"
  for s in "${SKILLS[@]}"; do
    mkdir -p "$dest/$s"
    cp "skills/$s/SKILL.md" "$dest/$s/SKILL.md"
  done
}

# Cursor
sync_skills ".cursor/skills"
mkdir -p .cursor/rules
{
  echo "---"
  echo "description: Always-on constraints for the Maturity Agent engine (Dan Shapiro assessments)."
  echo 'globs: "{maturity-agent/**,scripts/**,projects/**,templates/**,framework/**,skills/**,rules/**,.cursor/**}"'
  echo "alwaysApply: false"
  echo "---"
  echo ""
  cat rules/maturity-engine.md
} > .cursor/rules/maturity-engine.mdc

# Claude Code
sync_skills ".claude/skills"

# GitHub Copilot
mkdir -p .github
{
  cat <<'EOF'
# Maturity Agent — Copilot instructions

Assess **SDLC / agentic maturity** on Dan Shapiro's L0–L5 scale. Read `AGENTS.md` for the full loop.

## Authority

- Level definitions: `framework/shapiro-levels.md`
- Rubric signals: `framework/rubric.yaml`, `framework/signals.md`
- Hard rules: `rules/maturity-engine.md`

## Skills (read before each phase)

| Phase | Skill file |
|-------|------------|
| Orchestrate assessment | `skills/maturity-assess/SKILL.md` |
| Collect evidence | `skills/maturity-interview/SKILL.md` |
| Write report | `skills/maturity-report/SKILL.md` |
| Build slides | `skills/maturity-presentation/SKILL.md` |

## Output (never chat-only)

Write deliverables under `projects/<slug>/assessments/<run>/`: `evidence.yaml`, `report.md`, optional `presentation.html`.

## Scripts

```bash
python3 scripts/score_assessment.py projects/<slug>/assessments/<run>
python3 scripts/build_presentation.py projects/<slug>/assessments/<run>
```

See `PROVIDERS.md` for Cursor, Claude, Codex, and other adapters.
EOF
} > .github/copilot-instructions.md

echo "Synced adapters:"
echo "  .cursor/skills/ + .cursor/rules/maturity-engine.mdc"
echo "  .claude/skills/"
echo "  .github/copilot-instructions.md"
