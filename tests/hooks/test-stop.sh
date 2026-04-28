#!/usr/bin/env bash
# Test suite for plugins/baransu/hooks/stop.py (TASK-hooks-03).
#
# Stop hook contract (per .../skills/_shared/telemetry-schema.md §5 +
# REQ-001 Scenario 2): when the session ends, locate the row whose
# session_id matches the current session AND terminal_state == "in_progress",
# CAS-flip it to "aborted", and fill skill_outcome with a 中斷 marker if
# previously null. All other fields preserved. completed/aborted/interrupted
# rows are NEVER downgraded (monotonic CAS). Hook MUST exit 0 always.
#
# Coverage:
#   T1) Happy path: in_progress -> aborted, other fields preserved,
#       skill_outcome filled with aborted marker when previously null.
#   T2) CAS: pre-existing terminal_state=completed -> row UNCHANGED.
#   T3) CAS: pre-existing terminal_state=aborted -> row UNCHANGED (idempotent).
#   T4) CAS: pre-existing terminal_state=interrupted -> row UNCHANGED.
#   T5) Multiple sessions: 3 rows for 3 different session_ids; only the
#       matching in_progress row is flipped.
#   T6) flock concurrency: 10-fork stop.py against the same session_id;
#       final telemetry has 1 row, terminal_state=aborted, valid JSON.
#   T7) Non-blocking: chmod 500 harness dir -> hook still exits 0.
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$WORKTREE_ROOT/plugins/baransu/hooks/stop.py"

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
[ -f "$HOOK" ] || { echo "FAIL: hook script not found at $HOOK" >&2; exit 1; }
[ -x "$HOOK" ] || { echo "FAIL: hook script not executable: $HOOK" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "FAIL: jq not installed" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "FAIL: python3 not installed" >&2; exit 1; }

TMPROOT="$(mktemp -d)"
trap 'chmod -R u+rwX "$TMPROOT" 2>/dev/null; rm -rf "$TMPROOT"' EXIT

# Helper: build a row in JSONL form (sorted keys, matching writer output style).
mkrow() {
  # $1=session_id, $2=terminal_state, $3=skill_outcome (json or "null"),
  # $4=commit_hash (string|null), $5=diff_summary_redacted (json or "null"),
  # $6=prompt_text, $7=attempt_history (json)
  local sid="$1" state="$2" outcome="$3" commit="$4" diff="$5" prompt="$6" attempts="$7"
  jq -n -c --sort-keys \
    --arg sid "$sid" \
    --arg state "$state" \
    --argjson outcome "$outcome" \
    --argjson commit "$commit" \
    --argjson diff "$diff" \
    --arg prompt "$prompt" \
    --argjson attempts "$attempts" \
    '{session_id:$sid, terminal_state:$state, prompt_text:$prompt,
      skill_outcome:$outcome, commit_hash:$commit,
      diff_summary_redacted:$diff, attempt_history:$attempts}'
}

run_hook() {
  # $1=scratch dir, $2=payload json
  local scratch="$1" payload="$2"
  ( cd "$scratch" \
      && printf '%s' "$payload" | env CLAUDE_PROJECT_DIR="$scratch" "$HOOK" )
}

# -------------------------------------------------------------------------
# T1: Happy path — in_progress -> aborted, other fields preserved,
#     skill_outcome filled with marker if previously null.
# -------------------------------------------------------------------------
T1="$TMPROOT/t1"
mkdir -p "$T1/.claude/harness"
mkrow "s-stop-001" "in_progress" "null" "null" "null" "hello stop" "[]" \
  > "$T1/.claude/harness/telemetry.jsonl"
run_hook "$T1" '{"session_id":"s-stop-001"}'
T1_EXIT=$?

if [ $T1_EXIT -ne 0 ]; then
  bad "T1 happy: hook exit $T1_EXIT (want 0)"
elif [ ! -f "$T1/.claude/harness/telemetry.jsonl" ]; then
  bad "T1 happy: telemetry.jsonl missing"
else
  LINES=$(wc -l < "$T1/.claude/harness/telemetry.jsonl")
  if [ "$LINES" -ne 1 ]; then
    bad "T1 happy: expected 1 row, got $LINES"
  else
    ROW=$(cat "$T1/.claude/harness/telemetry.jsonl")
    HAS_ALL=$(echo "$ROW" | jq -r '
      has("session_id") and has("terminal_state") and has("prompt_text")
        and has("skill_outcome") and has("commit_hash")
        and has("diff_summary_redacted") and has("attempt_history")')
    STATE=$(echo "$ROW" | jq -r .terminal_state)
    SID=$(echo "$ROW" | jq -r .session_id)
    PROMPT=$(echo "$ROW" | jq -r .prompt_text)
    FINAL_STATE=$(echo "$ROW" | jq -r '.skill_outcome.final_state // empty')
    if [ "$HAS_ALL" != "true" ]; then
      bad "T1 happy: row missing 7 keys (row=$ROW)"
    elif [ "$STATE" != "aborted" ]; then
      bad "T1 happy: terminal_state=$STATE (want aborted)"
    elif [ "$SID" != "s-stop-001" ]; then
      bad "T1 happy: session_id mismatch ($SID)"
    elif [ "$PROMPT" != "hello stop" ]; then
      bad "T1 happy: prompt_text mutated to '$PROMPT'"
    elif [ "$FINAL_STATE" != "aborted" ]; then
      bad "T1 happy: skill_outcome.final_state=$FINAL_STATE (want 'aborted' marker)"
    else
      ok "T1 happy: in_progress -> aborted, other fields preserved, marker filled"
    fi
  fi
fi

# -------------------------------------------------------------------------
# T2: CAS — pre-existing completed row stays completed (never downgraded).
# -------------------------------------------------------------------------
T2="$TMPROOT/t2"
mkdir -p "$T2/.claude/harness"
COMPLETED_OUTCOME='{"skill_name":"think","final_state":"approved","exit_code":0}'
COMPLETED_DIFF='[{"path":"src/x.py","plus":1,"minus":0}]'
mkrow "s-stop-completed" "completed" "$COMPLETED_OUTCOME" \
  '"abcdef0011223344abcdef0011223344abcdef00"' \
  "$COMPLETED_DIFF" "done" "[]" \
  > "$T2/.claude/harness/telemetry.jsonl"
BEFORE=$(cat "$T2/.claude/harness/telemetry.jsonl")
run_hook "$T2" '{"session_id":"s-stop-completed"}' || true
AFTER=$(cat "$T2/.claude/harness/telemetry.jsonl")
if [ "$BEFORE" = "$AFTER" ]; then
  ok "T2 CAS completed: row byte-identical (no downgrade)"
else
  bad "T2 CAS completed: row mutated\n  BEFORE=$BEFORE\n  AFTER=$AFTER"
fi

# -------------------------------------------------------------------------
# T3: CAS — pre-existing aborted row stays aborted (idempotent).
# -------------------------------------------------------------------------
T3="$TMPROOT/t3"
mkdir -p "$T3/.claude/harness"
ABORTED_OUTCOME='{"skill_name":null,"final_state":"aborted","exit_code":null}'
mkrow "s-stop-aborted" "aborted" "$ABORTED_OUTCOME" "null" "null" "ctrl-c" "[]" \
  > "$T3/.claude/harness/telemetry.jsonl"
BEFORE=$(cat "$T3/.claude/harness/telemetry.jsonl")
run_hook "$T3" '{"session_id":"s-stop-aborted"}' || true
AFTER=$(cat "$T3/.claude/harness/telemetry.jsonl")
if [ "$BEFORE" = "$AFTER" ]; then
  ok "T3 CAS aborted: idempotent (row byte-identical)"
else
  bad "T3 CAS aborted: row mutated\n  BEFORE=$BEFORE\n  AFTER=$AFTER"
fi

# -------------------------------------------------------------------------
# T4: CAS — pre-existing interrupted row stays interrupted.
# -------------------------------------------------------------------------
T4="$TMPROOT/t4"
mkdir -p "$T4/.claude/harness"
mkrow "s-stop-interrupted" "interrupted" "null" "null" "null" "stale" "[]" \
  > "$T4/.claude/harness/telemetry.jsonl"
BEFORE=$(cat "$T4/.claude/harness/telemetry.jsonl")
run_hook "$T4" '{"session_id":"s-stop-interrupted"}' || true
AFTER=$(cat "$T4/.claude/harness/telemetry.jsonl")
if [ "$BEFORE" = "$AFTER" ]; then
  ok "T4 CAS interrupted: row byte-identical (no overwrite)"
else
  bad "T4 CAS interrupted: row mutated\n  BEFORE=$BEFORE\n  AFTER=$AFTER"
fi

# -------------------------------------------------------------------------
# T5: Multiple sessions — 3 rows; only the matching in_progress row flips.
# -------------------------------------------------------------------------
T5="$TMPROOT/t5"
mkdir -p "$T5/.claude/harness"
{
  mkrow "s-other-1" "completed" \
    '{"skill_name":"think","final_state":"approved","exit_code":0}' \
    '"1111111111111111111111111111111111111111"' \
    '[{"path":"a.py","plus":1,"minus":0}]' "p1" "[]"
  mkrow "s-target"  "in_progress" "null" "null" "null" "p2" "[]"
  mkrow "s-other-2" "interrupted" "null" "null" "null" "p3" "[]"
} > "$T5/.claude/harness/telemetry.jsonl"
run_hook "$T5" '{"session_id":"s-target"}' || true

LINES=$(wc -l < "$T5/.claude/harness/telemetry.jsonl")
if [ "$LINES" -ne 3 ]; then
  bad "T5 multi: expected 3 rows, got $LINES"
else
  STATE_OTHER1=$(sed -n '1p' "$T5/.claude/harness/telemetry.jsonl" | jq -r .terminal_state)
  STATE_TARGET=$(sed -n '2p' "$T5/.claude/harness/telemetry.jsonl" | jq -r .terminal_state)
  STATE_OTHER2=$(sed -n '3p' "$T5/.claude/harness/telemetry.jsonl" | jq -r .terminal_state)
  if [ "$STATE_OTHER1" = "completed" ] \
     && [ "$STATE_TARGET" = "aborted" ] \
     && [ "$STATE_OTHER2" = "interrupted" ]; then
    ok "T5 multi: only matching in_progress row flipped to aborted"
  else
    bad "T5 multi: states=[$STATE_OTHER1, $STATE_TARGET, $STATE_OTHER2] (want completed,aborted,interrupted)"
  fi
fi

# -------------------------------------------------------------------------
# T6: flock concurrency — 10 forks against the same session_id.
# Pre-seed in_progress; first stop.py wins CAS, rest see aborted and no-op.
# Final: exactly 1 row, terminal_state=aborted, valid JSON.
# -------------------------------------------------------------------------
T6="$TMPROOT/t6"
mkdir -p "$T6/.claude/harness"
mkrow "s-conc-stop" "in_progress" "null" "null" "null" "concurrent stop" "[]" \
  > "$T6/.claude/harness/telemetry.jsonl"
N=10
seq 1 $N | xargs -P "$N" -I{} bash -c "
  printf '{\"session_id\":\"s-conc-stop\"}' \
    | env CLAUDE_PROJECT_DIR='$T6' '$HOOK'
" 2>/dev/null

LINES=$(wc -l < "$T6/.claude/harness/telemetry.jsonl")
if [ "$LINES" -ne 1 ]; then
  bad "T6 concurrency: expected 1 row, got $LINES"
else
  ROW=$(cat "$T6/.claude/harness/telemetry.jsonl")
  if echo "$ROW" | jq -e . >/dev/null 2>&1; then
    STATE=$(echo "$ROW" | jq -r .terminal_state)
    if [ "$STATE" = "aborted" ]; then
      ok "T6 concurrency: 1 row, valid JSON, terminal_state=aborted under 10-fork"
    else
      bad "T6 concurrency: state=$STATE (want aborted); row=$ROW"
    fi
  else
    bad "T6 concurrency: row not valid JSON: $ROW"
  fi
fi

# -------------------------------------------------------------------------
# T7: Non-blocking — chmod 500 harness dir -> hook exits 0.
# -------------------------------------------------------------------------
T7="$TMPROOT/t7"
mkdir -p "$T7/.claude/harness"
mkrow "s-stop-perm" "in_progress" "null" "null" "null" "perm" "[]" \
  > "$T7/.claude/harness/telemetry.jsonl"
chmod 500 "$T7/.claude/harness"
set +e
run_hook "$T7" '{"session_id":"s-stop-perm"}' 2>/dev/null
T7_EXIT=$?
set -e
chmod 700 "$T7/.claude/harness"
if [ $T7_EXIT -eq 0 ]; then
  ok "T7 non-blocking: exit 0 under permission denied"
else
  bad "T7 non-blocking: exit $T7_EXIT (hook must not block)"
fi
set -u

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
