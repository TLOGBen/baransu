#!/usr/bin/env bash
# Test suite for plugins/baransu/scripts/harness-reaper.py (TASK-hooks-03).
#
# Reaper contract (per .../skills/_shared/telemetry-schema.md §5 + ctx.md):
# Reap rows where terminal_state == "in_progress" AND created_at is older
# than the threshold (default 24h). Flip those to "interrupted" with CAS
# guard (only if currently in_progress). Rows lacking `created_at` are
# skipped with a stderr warning (the schema doesn't currently mandate
# created_at; see report).
#
# Coverage:
#   T1) Happy path: 2 in_progress rows; one stale (mock created_at 25h ago),
#       one fresh (1h ago). Stale -> interrupted; fresh stays in_progress.
#   T2) CAS: stale row already aborted -> reaper does NOT change it.
#   T3) CAS: stale row already completed -> reaper does NOT change it.
#   T4) CAS: stale row already interrupted -> reaper does NOT change it.
#   T5) No stale rows: all rows fresh -> no changes; exits 0.
#   T6) Threshold parameterization: --threshold-hours 1 with row 2h old ->
#       row becomes interrupted (proves the flag is wired).
#   T7) Missing created_at: row in_progress but no created_at field ->
#       reaper SKIPS the row (does not corrupt) and emits stderr warning.
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REAPER="$WORKTREE_ROOT/plugins/baransu/scripts/harness-reaper.py"

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

# Pre-flight
[ -f "$REAPER" ] || { echo "FAIL: reaper script not found at $REAPER" >&2; exit 1; }
[ -x "$REAPER" ] || { echo "FAIL: reaper script not executable: $REAPER" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "FAIL: jq not installed" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "FAIL: python3 not installed" >&2; exit 1; }

TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

# Build a row with optional created_at field (added as 8th key when given).
# created_at lives outside the locked 7-field schema; reaper is the only
# reader. Rows without it are skipped (see ctx.md note).
mkrow_with_ts() {
  # $1=session_id, $2=terminal_state, $3=created_at (ISO string), $4=prompt
  local sid="$1" state="$2" ts="$3" prompt="$4"
  jq -n -c --sort-keys \
    --arg sid "$sid" \
    --arg state "$state" \
    --arg ts "$ts" \
    --arg prompt "$prompt" \
    '{session_id:$sid, terminal_state:$state, prompt_text:$prompt,
      skill_outcome:null, commit_hash:null,
      diff_summary_redacted:null, attempt_history:[],
      created_at:$ts}'
}

# Row WITHOUT created_at (7 locked fields only). Reaper skips it.
mkrow_no_ts() {
  local sid="$1" state="$2" prompt="$3"
  jq -n -c --sort-keys \
    --arg sid "$sid" \
    --arg state "$state" \
    --arg prompt "$prompt" \
    '{session_id:$sid, terminal_state:$state, prompt_text:$prompt,
      skill_outcome:null, commit_hash:null,
      diff_summary_redacted:null, attempt_history:[]}'
}

# Run reaper with explicit --now and --threshold-hours.
run_reaper() {
  # $1=telemetry path, $2=now-iso, $3=threshold-hours
  python3 "$REAPER" --telemetry "$1" --now "$2" --threshold-hours "$3"
}

# -------------------------------------------------------------------------
# T1: Happy path — stale in_progress row -> interrupted; fresh stays.
# Now: 2026-04-29T12:00:00Z. Stale: 2026-04-28T11:00:00Z (25h old).
# Fresh: 2026-04-29T11:00:00Z (1h old). Threshold: 24h.
# -------------------------------------------------------------------------
T1="$TMPROOT/t1"
mkdir -p "$T1/.claude/harness"
TELEM1="$T1/.claude/harness/telemetry.jsonl"
{
  mkrow_with_ts "s-stale" "in_progress" "2026-04-28T11:00:00Z" "stale prompt"
  mkrow_with_ts "s-fresh" "in_progress" "2026-04-29T11:00:00Z" "fresh prompt"
} > "$TELEM1"

set +e
run_reaper "$TELEM1" "2026-04-29T12:00:00Z" 24
T1_EXIT=$?
set -e

if [ $T1_EXIT -ne 0 ]; then
  bad "T1 happy: reaper exit $T1_EXIT (want 0)"
else
  STALE_STATE=$(sed -n '1p' "$TELEM1" | jq -r .terminal_state)
  FRESH_STATE=$(sed -n '2p' "$TELEM1" | jq -r .terminal_state)
  STALE_SID=$(sed -n '1p' "$TELEM1" | jq -r .session_id)
  FRESH_SID=$(sed -n '2p' "$TELEM1" | jq -r .session_id)
  if [ "$STALE_STATE" = "interrupted" ] \
     && [ "$FRESH_STATE" = "in_progress" ] \
     && [ "$STALE_SID" = "s-stale" ] \
     && [ "$FRESH_SID" = "s-fresh" ]; then
    ok "T1 happy: stale -> interrupted; fresh stays in_progress; row order preserved"
  else
    bad "T1 happy: stale_state=$STALE_STATE fresh_state=$FRESH_STATE"
  fi
fi

# -------------------------------------------------------------------------
# T2: CAS — stale row already aborted -> NO change.
# -------------------------------------------------------------------------
T2="$TMPROOT/t2"
mkdir -p "$T2/.claude/harness"
TELEM2="$T2/.claude/harness/telemetry.jsonl"
mkrow_with_ts "s-stale-aborted" "aborted" "2026-04-28T11:00:00Z" "stale aborted" \
  > "$TELEM2"
BEFORE=$(cat "$TELEM2")
run_reaper "$TELEM2" "2026-04-29T12:00:00Z" 24 || true
AFTER=$(cat "$TELEM2")
if [ "$BEFORE" = "$AFTER" ]; then
  ok "T2 CAS aborted: stale aborted row unchanged"
else
  bad "T2 CAS aborted: row mutated\n  BEFORE=$BEFORE\n  AFTER=$AFTER"
fi

# -------------------------------------------------------------------------
# T3: CAS — stale row already completed -> NO change.
# -------------------------------------------------------------------------
T3="$TMPROOT/t3"
mkdir -p "$T3/.claude/harness"
TELEM3="$T3/.claude/harness/telemetry.jsonl"
mkrow_with_ts "s-stale-completed" "completed" "2026-04-28T11:00:00Z" "stale done" \
  > "$TELEM3"
BEFORE=$(cat "$TELEM3")
run_reaper "$TELEM3" "2026-04-29T12:00:00Z" 24 || true
AFTER=$(cat "$TELEM3")
if [ "$BEFORE" = "$AFTER" ]; then
  ok "T3 CAS completed: stale completed row unchanged"
else
  bad "T3 CAS completed: row mutated"
fi

# -------------------------------------------------------------------------
# T4: CAS — stale row already interrupted -> NO change (idempotent).
# -------------------------------------------------------------------------
T4="$TMPROOT/t4"
mkdir -p "$T4/.claude/harness"
TELEM4="$T4/.claude/harness/telemetry.jsonl"
mkrow_with_ts "s-stale-interrupted" "interrupted" "2026-04-28T11:00:00Z" "old reap" \
  > "$TELEM4"
BEFORE=$(cat "$TELEM4")
run_reaper "$TELEM4" "2026-04-29T12:00:00Z" 24 || true
AFTER=$(cat "$TELEM4")
if [ "$BEFORE" = "$AFTER" ]; then
  ok "T4 CAS interrupted: row unchanged (idempotent)"
else
  bad "T4 CAS interrupted: row mutated"
fi

# -------------------------------------------------------------------------
# T5: All fresh -> no changes.
# -------------------------------------------------------------------------
T5="$TMPROOT/t5"
mkdir -p "$T5/.claude/harness"
TELEM5="$T5/.claude/harness/telemetry.jsonl"
{
  mkrow_with_ts "s-f1" "in_progress" "2026-04-29T11:30:00Z" "f1"
  mkrow_with_ts "s-f2" "in_progress" "2026-04-29T11:45:00Z" "f2"
} > "$TELEM5"
BEFORE=$(cat "$TELEM5")
set +e
run_reaper "$TELEM5" "2026-04-29T12:00:00Z" 24
T5_EXIT=$?
set -e
AFTER=$(cat "$TELEM5")
if [ $T5_EXIT -eq 0 ] && [ "$BEFORE" = "$AFTER" ]; then
  ok "T5 all fresh: no changes, exit 0"
else
  bad "T5 all fresh: exit=$T5_EXIT, mutated=$([ "$BEFORE" = "$AFTER" ] && echo no || echo yes)"
fi

# -------------------------------------------------------------------------
# T6: Threshold parameterization — --threshold-hours 1, row 2h old -> reaped.
# -------------------------------------------------------------------------
T6="$TMPROOT/t6"
mkdir -p "$T6/.claude/harness"
TELEM6="$T6/.claude/harness/telemetry.jsonl"
mkrow_with_ts "s-2h" "in_progress" "2026-04-29T10:00:00Z" "2h old" \
  > "$TELEM6"
run_reaper "$TELEM6" "2026-04-29T12:00:00Z" 1 || true
STATE=$(jq -r .terminal_state "$TELEM6")
if [ "$STATE" = "interrupted" ]; then
  ok "T6 threshold: --threshold-hours 1 reaps 2h-old row"
else
  bad "T6 threshold: state=$STATE (want interrupted)"
fi

# -------------------------------------------------------------------------
# T7: Missing created_at — row preserved, stderr warning emitted.
# -------------------------------------------------------------------------
T7="$TMPROOT/t7"
mkdir -p "$T7/.claude/harness"
TELEM7="$T7/.claude/harness/telemetry.jsonl"
mkrow_no_ts "s-no-ts" "in_progress" "no timestamp" \
  > "$TELEM7"
BEFORE=$(cat "$TELEM7")
STDERR=$(run_reaper "$TELEM7" "2026-04-29T12:00:00Z" 24 2>&1 >/dev/null || true)
AFTER=$(cat "$TELEM7")
if [ "$BEFORE" != "$AFTER" ]; then
  bad "T7 missing created_at: row mutated (must be preserved)"
elif ! echo "$STDERR" | grep -qiE "created_at|missing|skip"; then
  bad "T7 missing created_at: no stderr warning emitted (got: $STDERR)"
else
  ok "T7 missing created_at: row preserved, stderr warning emitted"
fi

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
