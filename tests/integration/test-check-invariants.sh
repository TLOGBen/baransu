#!/usr/bin/env bash
# Test suite for TASK-integration-03: check-invariants.sh.
#
# Asserts:
#   T1) plugins/baransu/scripts/check-invariants.sh exists.
#   T2) Script is executable.
#   T3) Running on the current Green tree exits 0.
#   T4) Output contains exactly 11 PASS lines (6 INV + 5 EDGE).
#   T5) All 6 invariants present: INV-1..INV-6.
#   T6) All 5 edges present: EDGE-1..EDGE-5.
#   T7) Negative test: a fake $BARANSU_ROOT missing the .claude/harness/
#       gitignore rule causes exit non-zero + a FAIL: EDGE-1 line.
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$WORKTREE_ROOT/plugins/baransu/scripts/check-invariants.sh"

PASS_COUNT=0
FAIL_COUNT=0
FAIL_DETAILS=""

ok() {
  echo "PASS: $*"
  PASS_COUNT=$((PASS_COUNT + 1))
}

bad() {
  echo "FAIL: $*" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
  FAIL_DETAILS="${FAIL_DETAILS}\n  - $*"
}

# -------------------------------------------------------------------------
# T1 / T2: script exists and is executable
# -------------------------------------------------------------------------
if [ -f "$SCRIPT" ]; then
  ok "T1 check-invariants.sh exists at $SCRIPT"
else
  bad "T1 check-invariants.sh missing at $SCRIPT"
  echo
  echo "----------------------------------------"
  echo "Tests: $PASS_COUNT failed early"
  echo -e "Failures:$FAIL_DETAILS" >&2
  exit 1
fi

if [ -x "$SCRIPT" ]; then
  ok "T2 check-invariants.sh is executable"
else
  bad "T2 check-invariants.sh is not executable (chmod +x missing)"
fi

# -------------------------------------------------------------------------
# T3: run on current Green tree → exit 0
# -------------------------------------------------------------------------
TMP_OUT=$(mktemp)
BARANSU_ROOT="$WORKTREE_ROOT" "$SCRIPT" >"$TMP_OUT" 2>&1
RC=$?
if [ "$RC" -eq 0 ]; then
  ok "T3 script exited 0 on current Green tree"
else
  bad "T3 script exited $RC on current Green tree (expected 0)"
  echo "--- script output (first 50 lines) ---" >&2
  head -50 "$TMP_OUT" >&2
  echo "--- end output ---" >&2
fi

# -------------------------------------------------------------------------
# T4: exactly 11 PASS lines (6 INV + 5 EDGE)
# -------------------------------------------------------------------------
PASS_LINES=$(grep -cE '^PASS: (INV|EDGE)-' "$TMP_OUT" || true)
if [ "$PASS_LINES" -eq 11 ]; then
  ok "T4 output has 11 PASS lines (6 INV + 5 EDGE)"
else
  bad "T4 output has $PASS_LINES PASS lines, expected 11"
fi

# -------------------------------------------------------------------------
# T5: all 6 invariants present
# -------------------------------------------------------------------------
for n in 1 2 3 4 5 6; do
  if grep -qE "^PASS: INV-$n[^0-9]" "$TMP_OUT"; then
    ok "T5 INV-$n present and PASS"
  else
    bad "T5 INV-$n missing or not PASS"
  fi
done

# -------------------------------------------------------------------------
# T6: all 5 edges present
# -------------------------------------------------------------------------
for n in 1 2 3 4 5; do
  if grep -qE "^PASS: EDGE-$n[^0-9]" "$TMP_OUT"; then
    ok "T6 EDGE-$n present and PASS"
  else
    bad "T6 EDGE-$n missing or not PASS"
  fi
done

# -------------------------------------------------------------------------
# T7: negative test — fake BARANSU_ROOT missing .gitignore rule for
#                     .claude/harness/ produces FAIL: EDGE-1 + non-zero exit.
# -------------------------------------------------------------------------
FAKE_ROOT=$(mktemp -d)
trap 'rm -rf "$FAKE_ROOT" "$TMP_OUT"' EXIT

# Build a minimal tree where EDGE-1 is broken (gitignore lacks .claude/harness/)
# but everything else can still be evaluated. We mirror the real layout via
# symlinks for the heavy directories, then override .gitignore with a stub.
mkdir -p "$FAKE_ROOT/plugins/baransu/.claude-plugin"
mkdir -p "$FAKE_ROOT/plugins/baransu"
ln -s "$WORKTREE_ROOT/plugins/baransu/skills" "$FAKE_ROOT/plugins/baransu/skills"
ln -s "$WORKTREE_ROOT/plugins/baransu/scripts" "$FAKE_ROOT/plugins/baransu/scripts"
ln -s "$WORKTREE_ROOT/plugins/baransu/hooks" "$FAKE_ROOT/plugins/baransu/hooks"
ln -s "$WORKTREE_ROOT/plugins/baransu/.claude-plugin/plugin.json" \
       "$FAKE_ROOT/plugins/baransu/.claude-plugin/plugin.json"
ln -s "$WORKTREE_ROOT/CLAUDE.md" "$FAKE_ROOT/CLAUDE.md"
# Stub .gitignore — note the ABSENCE of the harness rule.
# Do NOT mention `.claude/harness` here; the assertion uses grep -F on this
# file and would match a comment that contains the literal pattern.
cat >"$FAKE_ROOT/.gitignore" <<'EOF'
# Negative-test stub — deliberately incomplete
.env
EOF

NEG_OUT=$(mktemp)
BARANSU_ROOT="$FAKE_ROOT" "$SCRIPT" >"$NEG_OUT" 2>&1
NEG_RC=$?
if [ "$NEG_RC" -ne 0 ]; then
  ok "T7a negative tree caused non-zero exit ($NEG_RC)"
else
  bad "T7a negative tree exited 0 (expected non-zero)"
fi

if grep -qE '^FAIL: EDGE-1' "$NEG_OUT"; then
  ok "T7b negative tree printed FAIL: EDGE-1 line"
else
  bad "T7b negative tree did not print FAIL: EDGE-1 line"
  echo "--- negative output (first 30 lines) ---" >&2
  head -30 "$NEG_OUT" >&2
  echo "--- end output ---" >&2
fi
rm -f "$NEG_OUT"

# -------------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------------
TOTAL=$((PASS_COUNT + FAIL_COUNT))
echo
echo "----------------------------------------"
echo "Tests: $PASS_COUNT/$TOTAL passed"
if [ $FAIL_COUNT -gt 0 ]; then
  echo -e "Failures:$FAIL_DETAILS" >&2
  exit 1
fi
exit 0
