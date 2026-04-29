#!/usr/bin/env bash
# Test suite for TASK-integration-03: check-invariants.sh.
#
# Asserts:
#   T1) plugins/baransu/scripts/check-invariants.sh exists.
#   T2) Script is executable.
#   T3) Running on the current Green tree exits 0.
#   T4) Output contains exactly 14 PASS lines (6 INV + 5 EDGE + 3 INV-7 sub-checks).
#   T5) All 6 invariants present: INV-1..INV-6.
#   T6) All 5 edges present: EDGE-1..EDGE-5.
#   T7) Negative test: a fake $BARANSU_ROOT missing the .claude/harness/
#       gitignore rule causes exit non-zero + a FAIL: EDGE-1 line.
#   T8) INV-7a/b/c sub-checks present and PASS.
#   T9) INT-13 mutate→assert FAIL→revert cycles for INV-7a, INV-7b, INV-7c.
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
# T4: exactly 14 PASS lines (6 INV + 5 EDGE + 3 INV-7 sub-checks)
# -------------------------------------------------------------------------
PASS_LINES=$(grep -cE '^PASS: (INV|EDGE)-' "$TMP_OUT" || true)
if [ "$PASS_LINES" -eq 14 ]; then
  ok "T4 output has 14 PASS lines (6 INV + 5 EDGE + 3 INV-7 sub-checks)"
else
  bad "T4 output has $PASS_LINES PASS lines, expected 14"
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
# T8: INV-7a / INV-7b / INV-7c sub-checks present and PASS on Green tree
# -------------------------------------------------------------------------
for sub in 7a 7b 7c; do
  if grep -qE "^PASS: INV-$sub[^0-9a-z]" "$TMP_OUT"; then
    ok "T8 INV-$sub present and PASS"
  else
    bad "T8 INV-$sub missing or not PASS"
  fi
done

# -------------------------------------------------------------------------
# T9: INT-13 mutate→assert FAIL→revert cycles for INV-7a, INV-7b, INV-7c.
#
# Each sub-test mutates one of the three target files in a way that breaks
# the corresponding lint, runs check-invariants.sh, asserts exit non-zero
# AND that a FAIL: INV-7{a,b,c} line is present, then reverts the mutation.
# After all three cycles, runs check-invariants.sh once more on the (now
# reverted) tree to confirm a clean 14/14 PASS / exit 0.
# -------------------------------------------------------------------------

SCHEMA_DOC="$WORKTREE_ROOT/plugins/baransu/skills/_shared/state-json-schema.md"
GRADE_COLLECTOR="$WORKTREE_ROOT/plugins/baransu/scripts/grade-collector.py"
PUSH_GATE="$WORKTREE_ROOT/plugins/baransu/scripts/push-gate.sh"

# Helper: assert mutated tree fails with FAIL: INV-$sub then revert.
# Caller mutates the target file in advance and supplies the backup path.
#   $1 = sub-check id (7a / 7b / 7c)
#   $2 = path to (already-mutated) target file
#   $3 = path to a backup of the original file content (used for revert)
run_inv7_negative() {
  local sub="$1"
  local target="$2"
  local backup="$3"

  local out
  out=$(mktemp)
  BARANSU_ROOT="$WORKTREE_ROOT" "$SCRIPT" >"$out" 2>&1
  local rc=$?

  local pass_a=0
  local pass_b=0
  if [ "$rc" -ne 0 ]; then
    ok "T9 INV-$sub mutated tree caused non-zero exit ($rc)"
    pass_a=1
  else
    bad "T9 INV-$sub mutated tree exited 0 (expected non-zero)"
  fi

  if grep -qE "^FAIL: INV-$sub" "$out"; then
    ok "T9 INV-$sub mutated tree printed FAIL: INV-$sub line"
    pass_b=1
  else
    bad "T9 INV-$sub mutated tree did not print FAIL: INV-$sub line"
    echo "--- INV-$sub mutated output (first 30 lines) ---" >&2
    head -30 "$out" >&2
    echo "--- end output ---" >&2
  fi

  rm -f "$out"

  # Always revert the mutation (whether assertions passed or failed).
  cp "$backup" "$target"
}

# (a) INV-7a: delete the `grade owns` literal from state-json-schema.md.
SCHEMA_BACKUP=$(mktemp)
cp "$SCHEMA_DOC" "$SCHEMA_BACKUP"
# Remove every occurrence of the literal `grade owns` from the file. We use
# sed with a fixed pattern (no regex meta) so portability is high.
sed -i 's/grade owns//g' "$SCHEMA_DOC"
run_inv7_negative "7a" "$SCHEMA_DOC" "$SCHEMA_BACKUP"
# sanity: confirm revert worked.
if cmp -s "$SCHEMA_BACKUP" "$SCHEMA_DOC"; then
  ok "T9 INV-7a revert restored state-json-schema.md byte-identical"
else
  bad "T9 INV-7a revert FAILED to restore state-json-schema.md"
fi
rm -f "$SCHEMA_BACKUP"

# (b) INV-7b: append a guarded triage-key mutation to grade-collector.py.
GRADE_BACKUP=$(mktemp)
cp "$GRADE_COLLECTOR" "$GRADE_BACKUP"
# Append a guarded mutation that won't actually run (False guard). The lint
# is purely structural — it greps for the pattern, not the runtime behaviour.
cat >>"$GRADE_COLLECTOR" <<'PYEOF'

# INT-13 negative test stub (NEVER executed; structural lint trigger only).
if False:
    state = {}
    state["daily_push_count"] = 0
PYEOF
run_inv7_negative "7b" "$GRADE_COLLECTOR" "$GRADE_BACKUP"
if cmp -s "$GRADE_BACKUP" "$GRADE_COLLECTOR"; then
  ok "T9 INV-7b revert restored grade-collector.py byte-identical"
else
  bad "T9 INV-7b revert FAILED to restore grade-collector.py"
fi
rm -f "$GRADE_BACKUP"

# (c) INV-7c: append a guarded grade-key jq mutation to push-gate.sh.
PG_BACKUP=$(mktemp)
cp "$PUSH_GATE" "$PG_BACKUP"
# Append a guarded jq mutation that won't actually run (false branch). The
# lint greps for the literal `.last_grade_run_at = "X"` pattern.
cat >>"$PUSH_GATE" <<'SHEOF'

# INT-13 negative test stub (NEVER executed; structural lint trigger only).
if false; then
  jq '.last_grade_run_at = "X"' "$state_json_path" >/dev/null
fi
SHEOF
run_inv7_negative "7c" "$PUSH_GATE" "$PG_BACKUP"
if cmp -s "$PG_BACKUP" "$PUSH_GATE"; then
  ok "T9 INV-7c revert restored push-gate.sh byte-identical"
else
  bad "T9 INV-7c revert FAILED to restore push-gate.sh"
fi
rm -f "$PG_BACKUP"

# Final clean re-run after all 3 mutate/revert cycles — must be exit 0 again.
FINAL_OUT=$(mktemp)
BARANSU_ROOT="$WORKTREE_ROOT" "$SCRIPT" >"$FINAL_OUT" 2>&1
FINAL_RC=$?
if [ "$FINAL_RC" -eq 0 ]; then
  ok "T9 final clean re-run after revert cycles exited 0"
else
  bad "T9 final clean re-run after revert cycles exited $FINAL_RC (expected 0)"
  echo "--- final clean output (first 50 lines) ---" >&2
  head -50 "$FINAL_OUT" >&2
  echo "--- end output ---" >&2
fi
FINAL_PASS_LINES=$(grep -cE '^PASS: (INV|EDGE)-' "$FINAL_OUT" || true)
if [ "$FINAL_PASS_LINES" -eq 14 ]; then
  ok "T9 final clean re-run has 14 PASS lines (regression check)"
else
  bad "T9 final clean re-run has $FINAL_PASS_LINES PASS lines, expected 14"
fi
rm -f "$FINAL_OUT"

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
