#!/usr/bin/env bash
# Offline self-tests for maturity-agent engine.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OK=0
NO=0

ok() { echo "OK  $1"; OK=$((OK + 1)); }
fail() { echo "FAIL $1"; NO=$((NO + 1)); }

# Framework files exist
[[ -f framework/shapiro-levels.md ]] && ok "shapiro-levels.md" || fail "shapiro-levels.md"
[[ -f framework/rubric.yaml ]] && ok "rubric.yaml" || fail "rubric.yaml"
[[ -f framework/signals.md ]] && ok "signals.md" || fail "signals.md"

# Skills
for s in maturity-assess maturity-interview maturity-report maturity-presentation; do
  [[ -f ".cursor/skills/$s/SKILL.md" ]] && ok "skill $s" || fail "skill $s"
done

# Rules
[[ -f .cursor/rules/maturity-engine.mdc ]] && ok "maturity-engine.mdc" || fail "maturity-engine.mdc"

# Scripts executable logic (dry run new_project in /tmp)
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
if ./scripts/new_assessment.sh testproj baseline >/dev/null 2>&1; then
  ok "new_assessment.sh"
  RUN_EVIDENCE="$(find projects/testproj/assessments -name evidence.yaml | head -1)"
  [[ -n "$RUN_EVIDENCE" && -f "$RUN_EVIDENCE" ]] && ok "evidence.yaml seeded" || fail "evidence.yaml seeded"
else
  fail "new_assessment.sh"
fi

# Score script (needs pyyaml)
if python3 -c "import yaml" 2>/dev/null; then
  RUN_DIR="$(find projects/testproj/assessments -mindepth 1 -maxdepth 1 -type d | head -1)"
  # seed minimal yes answers for L4 signals
  cat > "$RUN_DIR/evidence.yaml" <<'YAML'
meta:
  project: testproj
signals:
  human_writes_tickets:
    answer: yes
    citation: test
  structured_acceptance:
    answer: yes
    citation: test
  multiple_roles:
    answer: yes
    citation: test
  written_role_boundaries:
    answer: yes
    citation: test
  agent_opens_pr:
    answer: yes
    citation: test
  review_agent_exists:
    answer: yes
    citation: test
  auto_deploy_nonprod:
    answer: yes
    citation: test
  qa_agent_or_unattended_tests:
    answer: yes
    citation: test
  jira_handoff_comments:
    answer: yes
    citation: test
  humans_own_intent:
    answer: yes
    citation: test
  project_template:
    answer: yes
    citation: test
  slug_parameterized_scripts:
    answer: yes
    citation: test
YAML
  if python3 scripts/score_assessment.py "$RUN_DIR" >/dev/null 2>&1; then
    ok "score_assessment.py"
    [[ -f "$RUN_DIR/score.json" ]] && ok "score.json written" || fail "score.json written"
    if python3 scripts/build_presentation.py "$RUN_DIR" --title "Test Proj" >/dev/null 2>&1; then
      ok "build_presentation.py"
      [[ -f "$RUN_DIR/presentation.html" ]] && ok "presentation.html" || fail "presentation.html"
      [[ -f "$RUN_DIR/presentation.md" ]] && ok "presentation.md" || fail "presentation.md"
    else
      fail "build_presentation.py"
    fi
  else
    fail "score_assessment.py"
  fi
else
  echo "SKIP score_assessment.py (pip install pyyaml)"
fi

echo ""
echo "Results: $OK passed, $NO failed"

# Engine must not reference specific customer projects
FORBIDDEN='RQ-[0-9]|lrm|qa-agent|colibri|lab-test|sol-ark|solark|mbugaiov'
if rg -i "$FORBIDDEN" framework .cursor templates scripts AGENTS.md README.md SETUP.md PORTABILITY.md INTEGRATIONS.md 2>/dev/null | rg -v 'Pre-push checklist|FORBIDDEN|no hits'; then
  fail "engine contains project-specific references"
else
  ok "engine project-agnostic grep"
fi

[[ $NO -eq 0 ]]
