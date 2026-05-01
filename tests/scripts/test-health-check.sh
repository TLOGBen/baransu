#!/usr/bin/env bash
# Tests for plugins/baransu/scripts/health_check.py.
#
# Contract (per plan: .claude/think/2026-04-29-harness-cron-health-check/plan.md):
#
# CLI:
#   python3 plugins/baransu/scripts/health_check.py \
#     --state .claude/harness/state.json \
#     --threshold-hours 36 \
#     [--now <ISO 8601 datetime>]   # for tests
#
# Behaviour:
#   - Reads `.claude/harness/state.json` and inspects `last_grade_run_at`.
#   - Three "unhealthy" states all emit a single 4-6 line 繁中 warning to stdout:
#       * state.json missing                       (fresh install)
#       * last_grade_run_at == null                (cron never fired yet)
#       * last_grade_run_at older than threshold   (cron stopped firing)
#   - Healthy state (within threshold) emits nothing on stdout.
#   - ALWAYS exits 0 (helper is observational; never blocks).
#   - Warning content MUST contain pointer to CRON.md, not literal CronCreate /
#     crontab commands (SoT lives in CRON.md per KD#3).
#
# Coverage:
#   T1  fresh       — state.json missing entirely
#   T2  null        — state.json exists but last_grade_run_at is null
#   T3  stale       — last_grade_run_at older than threshold (> 36h)
#   T4  healthy     — last_grade_run_at within threshold
#   T5  edge-just-under  — last_grade_run_at exactly 35h59m ago → healthy (no output)
#   T6  edge-just-over   — last_grade_run_at exactly 36h01m ago → stale (warning)
#   T7  always-exit-0    — all 4 unhealthy + healthy variants exit 0
#   T8  no-command-leak  — warning contains CRON.md pointer; does NOT leak
#                          CronCreate( / "crontab -e" literals
#   T9  threshold-flag   — --threshold-hours 1 with row 2h old → stale
#                          (proves the flag is wired)

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT_PATH="$WORKTREE_ROOT/plugins/baransu/scripts/health_check.py"

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
[ -f "$SCRIPT_PATH" ] || { echo "FAIL: health_check script not found at $SCRIPT_PATH" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "FAIL: python3 not installed" >&2; exit 1; }

TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

# Run helper. Captures stdout+exit; stderr passes through.
# $1 = state path (may not exist), $2 = now-ISO, $3 = threshold-hours
run_check() {
  local state="$1" now="$2" thr="$3"
  python3 "$SCRIPT_PATH" --state "$state" --now "$now" --threshold-hours "$thr"
}

write_state() {
  # $1=path, $2=last_grade_run_at value (use "null" for null, or quoted ISO string)
  local path="$1" last="$2"
  mkdir -p "$(dirname "$path")"
  if [ "$last" = "null" ]; then
    cat > "$path" <<EOF
{"daily_push_count": 0, "daily_push_date": "2026-04-29", "last_grade_run_at": null, "last_triage_run_at": null, "tune_review_due_since": null, "cumulative_completed_count": null}
EOF
  else
    cat > "$path" <<EOF
{"daily_push_count": 0, "daily_push_date": "2026-04-29", "last_grade_run_at": "$last", "last_triage_run_at": null, "tune_review_due_since": null, "cumulative_completed_count": 12}
EOF
  fi
}

# Common assertions on warning shape (4-6 lines, contains key markers).
assert_warning_shape() {
  # $1 = test id, $2 = stdout content
  local id="$1" out="$2"
  local lines
  lines=$(printf '%s' "$out" | grep -c '.' || true)
  if [ "$lines" -lt 4 ] || [ "$lines" -gt 6 ]; then
    bad "$id: warning line count $lines outside [4, 6]"
    return 1
  fi
  if ! printf '%s' "$out" | grep -q "harness 健康檢查"; then
    bad "$id: warning missing 'harness 健康檢查' marker"
    return 1
  fi
  if ! printf '%s' "$out" | grep -q "CRON.md"; then
    bad "$id: warning missing CRON.md pointer"
    return 1
  fi
  return 0
}

# -------------------------------------------------------------------------
# T1: fresh — state.json missing entirely
# -------------------------------------------------------------------------
T1="$TMPROOT/t1"
mkdir -p "$T1/.claude/harness"
STATE1="$T1/.claude/harness/state.json"  # not created
set +e
OUT1=$(run_check "$STATE1" "2026-05-01T00:00:00Z" 36)
EXIT1=$?
set -e
if [ "$EXIT1" -ne 0 ]; then
  bad "T1 fresh: exit $EXIT1 (want 0; helper must always exit 0)"
elif assert_warning_shape "T1 fresh" "$OUT1"; then
  ok "T1 fresh: state.json missing → 4-6 line warning, exit 0"
fi

# -------------------------------------------------------------------------
# T2: null — last_grade_run_at is null
# -------------------------------------------------------------------------
T2="$TMPROOT/t2"
STATE2="$T2/.claude/harness/state.json"
write_state "$STATE2" "null"
set +e
OUT2=$(run_check "$STATE2" "2026-05-01T00:00:00Z" 36)
EXIT2=$?
set -e
if [ "$EXIT2" -ne 0 ]; then
  bad "T2 null: exit $EXIT2 (want 0)"
elif assert_warning_shape "T2 null" "$OUT2"; then
  ok "T2 null: last_grade_run_at == null → 4-6 line warning, exit 0"
fi

# -------------------------------------------------------------------------
# T3: stale — last_grade_run_at older than threshold (48h ago, threshold 36h)
# -------------------------------------------------------------------------
T3="$TMPROOT/t3"
STATE3="$T3/.claude/harness/state.json"
write_state "$STATE3" "2026-04-29T00:00:00Z"
set +e
OUT3=$(run_check "$STATE3" "2026-05-01T00:00:00Z" 36)
EXIT3=$?
set -e
if [ "$EXIT3" -ne 0 ]; then
  bad "T3 stale: exit $EXIT3 (want 0)"
elif assert_warning_shape "T3 stale" "$OUT3"; then
  ok "T3 stale: last_grade_run_at 48h ago, threshold 36h → 4-6 line warning, exit 0"
fi

# -------------------------------------------------------------------------
# T4: healthy — last_grade_run_at 1h ago, threshold 36h → no output
# -------------------------------------------------------------------------
T4="$TMPROOT/t4"
STATE4="$T4/.claude/harness/state.json"
write_state "$STATE4" "2026-04-30T23:00:00Z"
set +e
OUT4=$(run_check "$STATE4" "2026-05-01T00:00:00Z" 36)
EXIT4=$?
set -e
if [ "$EXIT4" -ne 0 ]; then
  bad "T4 healthy: exit $EXIT4 (want 0)"
elif [ -n "$OUT4" ]; then
  bad "T4 healthy: expected 0 stdout, got: $OUT4"
else
  ok "T4 healthy: last_grade_run_at 1h ago → 0 stdout, exit 0"
fi

# -------------------------------------------------------------------------
# T5: edge-just-under — 35h59m ago, threshold 36h → healthy (no output)
# now: 2026-05-01T12:00:00Z; last: 2026-04-30T00:01:00Z (35h59m before now)
# -------------------------------------------------------------------------
T5="$TMPROOT/t5"
STATE5="$T5/.claude/harness/state.json"
write_state "$STATE5" "2026-04-30T00:01:00Z"
set +e
OUT5=$(run_check "$STATE5" "2026-05-01T12:00:00Z" 36)
EXIT5=$?
set -e
if [ "$EXIT5" -ne 0 ]; then
  bad "T5 edge-just-under: exit $EXIT5 (want 0)"
elif [ -n "$OUT5" ]; then
  bad "T5 edge-just-under: 35h59m ago should be healthy, got stdout: $OUT5"
else
  ok "T5 edge-just-under: 35h59m ago → healthy, no output"
fi

# -------------------------------------------------------------------------
# T6: edge-just-over — 36h01m ago, threshold 36h → stale (warning)
# now: 2026-05-01T12:00:00Z; last: 2026-04-29T23:59:00Z (36h01m before now)
# -------------------------------------------------------------------------
T6="$TMPROOT/t6"
STATE6="$T6/.claude/harness/state.json"
write_state "$STATE6" "2026-04-29T23:59:00Z"
set +e
OUT6=$(run_check "$STATE6" "2026-05-01T12:00:00Z" 36)
EXIT6=$?
set -e
if [ "$EXIT6" -ne 0 ]; then
  bad "T6 edge-just-over: exit $EXIT6 (want 0)"
elif assert_warning_shape "T6 edge-just-over" "$OUT6"; then
  ok "T6 edge-just-over: 36h01m ago → stale warning, exit 0"
fi

# -------------------------------------------------------------------------
# T7: always-exit-0 — corrupt state.json should still exit 0 (best-effort)
# -------------------------------------------------------------------------
T7="$TMPROOT/t7"
STATE7="$T7/.claude/harness/state.json"
mkdir -p "$(dirname "$STATE7")"
echo "not valid json {{" > "$STATE7"
set +e
OUT7=$(run_check "$STATE7" "2026-05-01T00:00:00Z" 36)
EXIT7=$?
set -e
if [ "$EXIT7" -ne 0 ]; then
  bad "T7 always-exit-0: corrupt state → exit $EXIT7 (want 0; helper never blocks)"
else
  ok "T7 always-exit-0: corrupt state.json → exit 0"
fi

# -------------------------------------------------------------------------
# T8: no-command-leak — warning must point to CRON.md, NOT print
# CronCreate( or "crontab -e" literals (SoT lives in CRON.md per KD#3).
# -------------------------------------------------------------------------
T8="$TMPROOT/t8"
STATE8="$T8/.claude/harness/state.json"
write_state "$STATE8" "null"
set +e
OUT8=$(run_check "$STATE8" "2026-05-01T00:00:00Z" 36)
EXIT8=$?
set -e
if [ "$EXIT8" -ne 0 ]; then
  bad "T8 no-command-leak: exit $EXIT8 (want 0)"
elif printf '%s' "$OUT8" | grep -q "CronCreate("; then
  bad "T8 no-command-leak: warning leaks 'CronCreate(' literal (SoT drift; should point to CRON.md only)"
elif printf '%s' "$OUT8" | grep -q "crontab -e"; then
  bad "T8 no-command-leak: warning leaks 'crontab -e' literal (SoT drift; should point to CRON.md only)"
elif ! printf '%s' "$OUT8" | grep -q "CRON.md"; then
  bad "T8 no-command-leak: warning missing CRON.md pointer"
else
  ok "T8 no-command-leak: warning points to CRON.md, no command literals leaked"
fi

# -------------------------------------------------------------------------
# T9: threshold-flag — --threshold-hours 1 with row 2h old → stale
# (proves the flag is wired and not hard-coded to 36h)
# -------------------------------------------------------------------------
T9="$TMPROOT/t9"
STATE9="$T9/.claude/harness/state.json"
write_state "$STATE9" "2026-04-30T22:00:00Z"  # 2h before now
set +e
OUT9=$(run_check "$STATE9" "2026-05-01T00:00:00Z" 1)
EXIT9=$?
set -e
if [ "$EXIT9" -ne 0 ]; then
  bad "T9 threshold-flag: exit $EXIT9 (want 0)"
elif assert_warning_shape "T9 threshold-flag" "$OUT9"; then
  ok "T9 threshold-flag: --threshold-hours 1 with row 2h old → stale warning"
fi

# -------------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------------
echo
echo "----- summary -----"
echo "PASS: $PASS_COUNT"
echo "FAIL: $FAIL_COUNT"
if [ "$FAIL_COUNT" -ne 0 ]; then
  printf '%b\n' "Failures:$FAIL_DETAILS" >&2
  exit 1
fi
exit 0
