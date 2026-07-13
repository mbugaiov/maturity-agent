#!/usr/bin/env bash
# Offline self-tests for maturity-agent engine.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OK=0
NO=0

ok() { echo "OK  $1"; OK=$((OK + 1)); }
fail() { echo "FAIL $1"; NO=$((NO + 1)); }

# --- Framework & docs ---
[[ -f framework/shapiro-levels.md ]] && ok "shapiro-levels.md" || fail "shapiro-levels.md"
[[ -f framework/rubric.yaml ]] && ok "rubric.yaml" || fail "rubric.yaml"
[[ -f framework/signals.md ]] && ok "signals.md" || fail "signals.md"
for doc in AGENTS.md CLAUDE.md PROVIDERS.md README.md SETUP.md PORTABILITY.md INTEGRATIONS.md; do
  [[ -f "$doc" ]] && ok "doc $doc" || fail "doc $doc"
done

# --- Templates ---
for tpl in intake.md assessment.md evidence.yaml report.md gap-backlog.md presentation.md; do
  [[ -f "templates/$tpl" ]] && ok "template $tpl" || fail "template $tpl"
done

# --- Skills (canonical + adapters) ---
for s in maturity-assess maturity-interview maturity-report maturity-presentation maturity-code-review; do
  [[ -f "skills/$s/SKILL.md" ]] && ok "canonical skill $s" || fail "canonical skill $s"
  [[ -f ".cursor/skills/$s/SKILL.md" ]] && ok "cursor skill $s" || fail "cursor skill $s"
  [[ -f ".claude/skills/$s/SKILL.md" ]] && ok "claude skill $s" || fail "claude skill $s"
  if diff -q "skills/$s/SKILL.md" ".cursor/skills/$s/SKILL.md" >/dev/null 2>&1; then
    ok "cursor skill sync $s"
  else
    fail "cursor skill sync $s"
  fi
  if diff -q "skills/$s/SKILL.md" ".claude/skills/$s/SKILL.md" >/dev/null 2>&1; then
    ok "claude skill sync $s"
  else
    fail "claude skill sync $s"
  fi
done

# --- Rules + provider entry points ---
[[ -f rules/maturity-engine.md ]] && ok "rules/maturity-engine.md" || fail "rules/maturity-engine.md"
[[ -f rules/code-review-gate.md ]] && ok "rules/code-review-gate.md" || fail "rules/code-review-gate.md"
[[ -f CONTRIBUTING.md ]] && ok "CONTRIBUTING.md" || fail "CONTRIBUTING.md"
[[ -f .github/pull_request_template.md ]] && ok "pull_request_template.md" || fail "pull_request_template.md"
[[ -f .cursor/rules/maturity-engine.mdc ]] && ok "maturity-engine.mdc" || fail "maturity-engine.mdc"
[[ -f .cursor/rules/code-review-gate.mdc ]] && ok "code-review-gate.mdc" || fail "code-review-gate.mdc"
[[ -f CLAUDE.md ]] && ok "CLAUDE.md" || fail "CLAUDE.md"
[[ -f PROVIDERS.md ]] && ok "PROVIDERS.md" || fail "PROVIDERS.md"
[[ -f .github/copilot-instructions.md ]] && ok "copilot-instructions.md" || fail "copilot-instructions.md"

# --- Sync script ---
chmod +x scripts/*.sh
if ./scripts/sync_adapters.sh >/dev/null 2>&1; then
  ok "sync_adapters.sh"
else
  fail "sync_adapters.sh"
fi

# Adapter drift (skills/rules must match synced adapters)
DRIFT=0
for path in .cursor/skills .cursor/rules/maturity-engine.mdc .cursor/rules/code-review-gate.mdc .claude/skills .github/copilot-instructions.md; do
  if ! git diff --quiet -- "$path" 2>/dev/null; then
    fail "adapter drift $path"
    DRIFT=1
  fi
done
[[ "$DRIFT" -eq 0 ]] && ok "adapter sync parity"

# --- Script CLI validation ---
if ./scripts/new_project.sh 2>/dev/null; then
  fail "new_project.sh rejects missing args"
else
  ok "new_project.sh rejects missing args"
fi
if ./scripts/new_project.sh 'BAD SLUG' 2>/dev/null; then
  fail "new_project.sh rejects invalid slug"
else
  ok "new_project.sh rejects invalid slug"
fi
if ./scripts/new_assessment.sh 2>/dev/null; then
  fail "new_assessment.sh rejects missing args"
else
  ok "new_assessment.sh rejects missing args"
fi
if ./scripts/new_assessment.sh nonexistent-proj baseline 2>/dev/null; then
  fail "new_assessment.sh rejects missing project"
else
  ok "new_assessment.sh rejects missing project"
fi

# --- Integration in isolated copy ---
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -R "$ROOT" "$TMP/maturity-agent"
cd "$TMP/maturity-agent"
chmod +x scripts/*.sh

if ./scripts/new_project.sh testproj "Test Proj" >/dev/null 2>&1; then
  ok "new_project.sh"
else
  fail "new_project.sh"
fi
if ./scripts/new_project.sh testproj "Dup" 2>/dev/null; then
  fail "new_project.sh rejects duplicate"
else
  ok "new_project.sh rejects duplicate"
fi
[[ -f projects/testproj/intake.md ]] && ok "intake.md created" || fail "intake.md created"
[[ -f projects/testproj/project.yaml ]] && ok "project.yaml created" || fail "project.yaml created"

if ./scripts/new_assessment.sh testproj baseline >/dev/null 2>&1; then
  ok "new_assessment.sh"
  RUN_DIR="$(find projects/testproj/assessments -mindepth 1 -maxdepth 1 -type d | head -1)"
  [[ -f "$RUN_DIR/evidence.yaml" ]] && ok "evidence.yaml seeded" || fail "evidence.yaml seeded"
  [[ -f "$RUN_DIR/assessment.md" ]] && ok "assessment.md seeded" || fail "assessment.md seeded"
  [[ -f "$RUN_DIR/report.md" ]] && ok "report.md seeded" || fail "report.md seeded"
else
  fail "new_assessment.sh"
fi

if ./scripts/new_assessment.sh testproj baseline 2>/dev/null; then
  fail "new_assessment.sh rejects duplicate run"
else
  ok "new_assessment.sh rejects duplicate run"
fi

# --- Python scoring + presentation ---
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "SKIP python tests (pip install pyyaml)"
else
  RUN_DIR="$(find projects/testproj/assessments -mindepth 1 -maxdepth 1 -type d | head -1)"
  cp "$ROOT/tests/fixtures/l4-evidence.yaml" "$RUN_DIR/evidence.yaml"
  cp "$ROOT/tests/fixtures/sample-report.md" "$RUN_DIR/report.md"

  if python3 scripts/score_assessment.py "$RUN_DIR" >/dev/null 2>&1; then
    ok "score_assessment.py"
    [[ -f "$RUN_DIR/score.json" ]] && ok "score.json written" || fail "score.json written"
    python3 -c "import json; d=json.load(open('$RUN_DIR/score.json')); assert 'dimensions' in d and len(d['dimensions'])>0"
    ok "score.json structure"
  else
    fail "score_assessment.py"
  fi

  if python3 scripts/build_presentation.py "$RUN_DIR" --title "Test Proj" >/dev/null 2>&1; then
    ok "build_presentation.py"
    [[ -f "$RUN_DIR/presentation.html" ]] && ok "presentation.html" || fail "presentation.html"
    [[ -f "$RUN_DIR/presentation.md" ]] && ok "presentation.md" || fail "presentation.md"
    grep -q "reveal.js" "$RUN_DIR/presentation.html" && ok "presentation.html reveal.js" || fail "presentation.html reveal.js"
    grep -q "How we evaluated" "$RUN_DIR/presentation.html" && ok "presentation 7-slide content" || fail "presentation 7-slide content"
  else
    fail "build_presentation.py"
  fi

  if ./scripts/build_presentation.sh "$RUN_DIR" "Test Proj" >/dev/null 2>&1; then
    ok "build_presentation.sh"
  else
    fail "build_presentation.sh"
  fi

  if python3 -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -q; then
    ok "python unittest suite"
  else
    fail "python unittest suite"
  fi
fi

echo ""
echo "Results: $OK passed, $NO failed"

cd "$ROOT"
chmod +x scripts/check_engine_agnostic.sh
if ./scripts/check_engine_agnostic.sh >/dev/null 2>&1; then
  ok "check_engine_agnostic.sh"
else
  fail "check_engine_agnostic.sh"
fi

[[ $NO -eq 0 ]]
