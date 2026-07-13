#!/usr/bin/env bash
# Negative-path tests for agnosticism and pre-merge gates.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OK=0
NO=0

ok() { echo "OK  $1"; OK=$((OK + 1)); }
fail() { echo "FAIL $1"; NO=$((NO + 1)); }

FORBIDDEN='(RQ-[0-9]+|\blrm\b|qa-agent|colibri|lab-test|sol-ark|solark|mbugaiov|/Users/max/)'

# Pattern engine catches sample leaks
for sample in "colibri-book" "RQ-1740" "qa-agent" "mbugaiov"; do
  if echo "$sample" | grep -qEi "$FORBIDDEN"; then
    ok "forbidden matches $sample"
  else
    fail "forbidden matches $sample"
  fi
done

# check_engine_agnostic.sh fails on a tracked leak in a temp git repo
NEG="$(mktemp -d)"
trap 'rm -rf "$NEG"' EXIT
mkdir -p "$NEG/scripts"
cp scripts/check_engine_agnostic.sh "$NEG/scripts/"
echo "leak from colibri assessment" > "$NEG/README.md"
cd "$NEG"
git init -q
git config user.email "test@test"
git config user.name "test"
git add README.md scripts/check_engine_agnostic.sh
git commit -q -m "init"
if bash scripts/check_engine_agnostic.sh >/dev/null 2>&1; then
  fail "agnosticism detects colibri leak"
else
  ok "agnosticism detects colibri leak"
fi
cd "$ROOT"

# pre_merge_check.sh fails when tests fail
FAIL_REPO="$(mktemp -d)"
cp -R "$ROOT" "$FAIL_REPO/maturity-agent"
cat > "$FAIL_REPO/maturity-agent/tests/run_tests.sh" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
chmod +x "$FAIL_REPO/maturity-agent/tests/run_tests.sh"
chmod +x "$FAIL_REPO/maturity-agent/scripts/"*.sh
if bash "$FAIL_REPO/maturity-agent/scripts/pre_merge_check.sh" >/dev/null 2>&1; then
  fail "pre_merge_check fails when tests fail"
else
  ok "pre_merge_check fails when tests fail"
fi

echo ""
echo "Negative gates: $OK passed, $NO failed"
[[ $NO -eq 0 ]]
