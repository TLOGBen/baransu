#!/usr/bin/env bash
# Test suite for plugins/baransu/hooks/post-tool-use.py (TASK-hooks-02).
#
# Coverage (matches ctx.md TASK-hooks-02 unit-test list):
#   1) happy path — UserPromptSubmit row present (in_progress) -> PostToolUse
#      merges skill_outcome / commit_hash / diff_summary_redacted and lifts
#      terminal_state to "completed". 7 keys still parse via jq.
#   2) INT-1 pairing — same session_id from both hooks: final telemetry has
#      ONE row, not two; 7 fields complete.
#   3) EDGE-2 path redaction — feed a synthetic diff with 5 sensitive paths
#      + 1 normal. Filter drops sensitive paths entirely; normal path remains
#      with accurate +N/-N. Includes path-prefixed cases (certs/server.pem,
#      config/secret.yaml) per REQ-001 Scenario 3.
#   4) CAS guard (Q-F1 ordering B) — pre-seed terminal_state=aborted ->
#      PostToolUse merges non-state fields but DOES NOT downgrade state.
#   5) CAS guard variant — pre-seed terminal_state=interrupted -> same.
#   6) Idempotent re-fire — pre-seed terminal_state=completed -> row is
#      byte-identical after PostToolUse runs (no-op).
#   7) commit_hash across git states — clean repo, dirty working tree,
#      detached HEAD, and no-git-at-all (graceful fallback to null).
#   8) flock concurrency — 20 forks for the SAME session_id (with one
#      pre-seeded in_progress row) all merge into the same row; final
#      telemetry has exactly that row, terminal_state=completed, valid JSON.
#   9) No-matching-row append path — PostToolUse fires with no prior
#      UserPromptSubmit row; appends a new completed row.
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$WORKTREE_ROOT/plugins/baransu/hooks/post-tool-use.py"

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
command -v git >/dev/null 2>&1 || { echo "FAIL: git not installed" >&2; exit 1; }

TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

# Helper: build a row in JSONL form (sorted keys, matching the writer's output style)
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

# Helper: payload drives the hook's git context. We override what the hook
# inspects via env vars (the hook script honours POST_TOOL_USE_TEST_DIFF and
# POST_TOOL_USE_TEST_COMMIT for tests; in production the hook calls git itself).
run_hook() {
  # $1=scratch dir, $2=payload json, [$3=test diff json], [$4=test commit hash]
  # The env vars must apply to the HOOK process, not printf — the pipe forks
  # the two as separate processes.
  local scratch="$1" payload="$2"
  local diff_override="${3:-}" commit_override="${4:-}"
  local env_args=("CLAUDE_PROJECT_DIR=$scratch")
  [ -n "$diff_override" ] && env_args+=("POST_TOOL_USE_TEST_DIFF=$diff_override")
  [ -n "$commit_override" ] && env_args+=("POST_TOOL_USE_TEST_COMMIT=$commit_override")
  ( cd "$scratch" \
      && printf '%s' "$payload" | env "${env_args[@]}" "$HOOK" )
}

# Synthetic diff helper (numstat-shaped JSON: array of {path, plus, minus}).
# The hook accepts this via POST_TOOL_USE_TEST_DIFF and skips the real git call.
diff_5sensitive_1normal() {
  jq -n -c '[
    {path:".env.production", plus:1, minus:0},
    {path:"config/secret.yaml", plus:2, minus:1},
    {path:"aws.credentials", plus:3, minus:0},
    {path:"certs/server.pem", plus:4, minus:2},
    {path:"db.key", plus:5, minus:1},
    {path:"src/main.py", plus:12, minus:3}
  ]'
}

# -------------------------------------------------------------------------
# Test 1: happy path — in_progress -> completed; 7 fields preserved.
# -------------------------------------------------------------------------
T1="$TMPROOT/t1"
mkdir -p "$T1/.claude/harness"
mkrow "s-test-001" "in_progress" "null" "null" "null" "hello world" "[]" \
  > "$T1/.claude/harness/telemetry.jsonl"
PAYLOAD='{"session_id":"s-test-001"}'
DIFF=$(jq -n -c '[{path:"src/main.py", plus:12, minus:3}]')
COMMIT='"3a525e544f0c8b1e9d2a7f0b1c4d6e8f0a1b2c3d"'

run_hook "$T1" "$PAYLOAD" "$DIFF" "$COMMIT"
T1_EXIT=$?

if [ $T1_EXIT -ne 0 ]; then
  bad "T1 happy path: hook exit $T1_EXIT (want 0)"
elif [ ! -f "$T1/.claude/harness/telemetry.jsonl" ]; then
  bad "T1 happy path: telemetry.jsonl missing"
else
  LINES=$(wc -l < "$T1/.claude/harness/telemetry.jsonl")
  if [ "$LINES" -ne 1 ]; then
    bad "T1 happy path: expected 1 line, got $LINES"
  else
    ROW="$(cat "$T1/.claude/harness/telemetry.jsonl")"
    HAS_ALL=$(echo "$ROW" | jq -r '
      has("session_id") and has("terminal_state") and has("prompt_text")
        and has("skill_outcome") and has("commit_hash")
        and has("diff_summary_redacted") and has("attempt_history")
    ' 2>/dev/null)
    STATE=$(echo "$ROW" | jq -r .terminal_state)
    HASH=$(echo "$ROW" | jq -r .commit_hash)
    DIFF_LEN=$(echo "$ROW" | jq -r '.diff_summary_redacted | length')
    if [ "$HAS_ALL" != "true" ]; then
      bad "T1 happy path: row missing one of 7 keys (row=$ROW)"
    elif [ "$STATE" != "completed" ]; then
      bad "T1 happy path: terminal_state=$STATE (want completed)"
    elif [ "$HASH" != "3a525e544f0c8b1e9d2a7f0b1c4d6e8f0a1b2c3d" ]; then
      bad "T1 happy path: commit_hash=$HASH (mismatch)"
    elif [ "$DIFF_LEN" != "1" ]; then
      bad "T1 happy path: diff_summary_redacted length=$DIFF_LEN (want 1)"
    else
      ok "T1 happy path: in_progress -> completed, 7 fields, hash & diff merged"
    fi
  fi
fi

# -------------------------------------------------------------------------
# Test 2: INT-1 pairing — UserPromptSubmit row + PostToolUse merge -> 1 row.
# (Same as T1 but emphasises "no second row appended".)
# -------------------------------------------------------------------------
T2="$TMPROOT/t2"
mkdir -p "$T2/.claude/harness"
mkrow "s-int-1" "in_progress" "null" "null" "null" "重構 auth" "[]" \
  > "$T2/.claude/harness/telemetry.jsonl"
PAYLOAD='{"session_id":"s-int-1"}'
DIFF=$(jq -n -c '[{path:"src/auth.py", plus:5, minus:2}]')
COMMIT='"abc123def456abc123def456abc123def456abc1"'
run_hook "$T2" "$PAYLOAD" "$DIFF" "$COMMIT" || true
LINES=$(wc -l < "$T2/.claude/harness/telemetry.jsonl")
if [ "$LINES" -ne 1 ]; then
  bad "T2 INT-1 pairing: expected 1 row (no append), got $LINES"
else
  ROW=$(cat "$T2/.claude/harness/telemetry.jsonl")
  HAS_ALL=$(echo "$ROW" | jq -r '
    has("session_id") and has("terminal_state") and has("prompt_text")
      and has("skill_outcome") and has("commit_hash")
      and has("diff_summary_redacted") and has("attempt_history")')
  STATE=$(echo "$ROW" | jq -r .terminal_state)
  if [ "$HAS_ALL" = "true" ] && [ "$STATE" = "completed" ]; then
    ok "T2 INT-1 pairing: 1 row, 7 fields, terminal_state=completed"
  else
    bad "T2 INT-1 pairing: HAS_ALL=$HAS_ALL state=$STATE row=$ROW"
  fi
fi

# -------------------------------------------------------------------------
# Test 3: EDGE-2 path redaction — 5 sensitive + 1 normal; sensitive dropped.
# -------------------------------------------------------------------------
T3="$TMPROOT/t3"
mkdir -p "$T3/.claude/harness"
mkrow "s-edge-2" "in_progress" "null" "null" "null" "edge2" "[]" \
  > "$T3/.claude/harness/telemetry.jsonl"
PAYLOAD='{"session_id":"s-edge-2"}'
DIFF=$(diff_5sensitive_1normal)
COMMIT='"deadbeef0123456789deadbeef0123456789dead"'
run_hook "$T3" "$PAYLOAD" "$DIFF" "$COMMIT" || true

ROW=$(cat "$T3/.claude/harness/telemetry.jsonl")
DIFF_OUT=$(echo "$ROW" | jq -c .diff_summary_redacted)
LEN=$(echo "$DIFF_OUT" | jq 'length')
KEPT_PATH=$(echo "$DIFF_OUT" | jq -r '.[0].path // empty')
KEPT_PLUS=$(echo "$DIFF_OUT" | jq -r '.[0].plus // empty')
KEPT_MINUS=$(echo "$DIFF_OUT" | jq -r '.[0].minus // empty')

# All 5 sensitive substrings absent
SENSITIVE_HIT=0
for s in ".env.production" "config/secret.yaml" "aws.credentials" "certs/server.pem" "db.key"; do
  if echo "$DIFF_OUT" | grep -qF "$s"; then
    SENSITIVE_HIT=1
    bad "T3 redaction: sensitive path '$s' leaked into diff_summary_redacted"
  fi
done
if [ $SENSITIVE_HIT -eq 0 ]; then
  if [ "$LEN" = "1" ] && [ "$KEPT_PATH" = "src/main.py" ] \
       && [ "$KEPT_PLUS" = "12" ] && [ "$KEPT_MINUS" = "3" ]; then
    ok "T3 redaction: 5 sensitive dropped, normal path kept with +12 -3 intact"
  else
    bad "T3 redaction: expected 1 entry {src/main.py, +12, -3}; got $DIFF_OUT"
  fi
fi

# -------------------------------------------------------------------------
# Test 4: CAS guard — pre-seeded aborted stays aborted, non-state fields merge.
# -------------------------------------------------------------------------
T4="$TMPROOT/t4"
mkdir -p "$T4/.claude/harness"
ABORTED_OUTCOME='{"skill_name":"think","final_state":"interrupted","exit_code":130}'
mkrow "s-cas-aborted" "aborted" "$ABORTED_OUTCOME" "null" "null" "ctrl-c case" "[]" \
  > "$T4/.claude/harness/telemetry.jsonl"
PAYLOAD='{"session_id":"s-cas-aborted"}'
DIFF=$(jq -n -c '[{path:"src/x.py", plus:1, minus:0}]')
COMMIT='"feedface0011223344feedface0011223344feed"'
run_hook "$T4" "$PAYLOAD" "$DIFF" "$COMMIT" || true

ROW=$(cat "$T4/.claude/harness/telemetry.jsonl")
STATE=$(echo "$ROW" | jq -r .terminal_state)
HASH=$(echo "$ROW" | jq -r .commit_hash)
DIFF_LEN=$(echo "$ROW" | jq -r '.diff_summary_redacted | length // 0')
if [ "$STATE" != "aborted" ]; then
  bad "T4 CAS aborted: terminal_state changed to '$STATE' (must stay aborted)"
elif [ "$HASH" != "feedface0011223344feedface0011223344feed" ]; then
  bad "T4 CAS aborted: commit_hash not merged (got $HASH)"
elif [ "$DIFF_LEN" != "1" ]; then
  bad "T4 CAS aborted: diff_summary_redacted not merged (length=$DIFF_LEN)"
else
  ok "T4 CAS aborted: state preserved, non-state fields merged"
fi

# -------------------------------------------------------------------------
# Test 5: CAS guard variant — pre-seeded interrupted stays interrupted.
# -------------------------------------------------------------------------
T5="$TMPROOT/t5"
mkdir -p "$T5/.claude/harness"
mkrow "s-cas-int" "interrupted" "null" "null" "null" "reaper case" "[]" \
  > "$T5/.claude/harness/telemetry.jsonl"
PAYLOAD='{"session_id":"s-cas-int"}'
DIFF=$(jq -n -c '[{path:"src/y.py", plus:2, minus:0}]')
COMMIT='"cafef00d11223344cafef00d11223344cafef00d"'
run_hook "$T5" "$PAYLOAD" "$DIFF" "$COMMIT" || true

ROW=$(cat "$T5/.claude/harness/telemetry.jsonl")
STATE=$(echo "$ROW" | jq -r .terminal_state)
HASH=$(echo "$ROW" | jq -r .commit_hash)
if [ "$STATE" != "interrupted" ]; then
  bad "T5 CAS interrupted: state changed to '$STATE' (must stay interrupted)"
elif [ "$HASH" != "cafef00d11223344cafef00d11223344cafef00d" ]; then
  bad "T5 CAS interrupted: commit_hash not merged (got $HASH)"
else
  ok "T5 CAS interrupted: state preserved, commit_hash merged"
fi

# -------------------------------------------------------------------------
# Test 6: idempotent re-fire — pre-seeded completed -> byte-identical row.
# -------------------------------------------------------------------------
T6="$TMPROOT/t6"
mkdir -p "$T6/.claude/harness"
COMPLETED_OUTCOME='{"skill_name":"think","final_state":"approved","exit_code":0}'
DIFF_PRE=$(jq -n -c '[{path:"src/done.py", plus:7, minus:1}]')
mkrow "s-cas-completed" "completed" "$COMPLETED_OUTCOME" \
  '"abcdef0011223344abcdef0011223344abcdef00"' \
  "$DIFF_PRE" "happy" "[]" \
  > "$T6/.claude/harness/telemetry.jsonl"
BEFORE=$(cat "$T6/.claude/harness/telemetry.jsonl")

PAYLOAD='{"session_id":"s-cas-completed"}'
DIFF_RE=$(jq -n -c '[{path:"src/other.py", plus:99, minus:99}]')
run_hook "$T6" "$PAYLOAD" "$DIFF_RE" '"0000000000000000000000000000000000000000"' || true

AFTER=$(cat "$T6/.claude/harness/telemetry.jsonl")
if [ "$BEFORE" = "$AFTER" ]; then
  ok "T6 idempotent re-fire: row byte-identical after second PostToolUse"
else
  bad "T6 idempotent re-fire: row mutated\n  BEFORE=$BEFORE\n  AFTER=$AFTER"
fi

# -------------------------------------------------------------------------
# Test 7: commit_hash across git states (clean / dirty / detached / no-git).
# These tests do NOT use POST_TOOL_USE_TEST_COMMIT — they exercise the real
# git rev-parse path. Each scratch dir is its own repo, isolated from the
# worktree's git state.
# -------------------------------------------------------------------------
git_init_repo() {
  local d="$1"
  ( cd "$d" \
      && git init -q \
      && git config user.email "t@t" \
      && git config user.name "t" \
      && echo "v1" > a.txt \
      && git add a.txt \
      && git commit -q -m "init" )
}

# 7a: clean repo
T7A="$TMPROOT/t7a"
mkdir -p "$T7A/.claude/harness"
git_init_repo "$T7A"
EXPECTED_HASH_7A=$(cd "$T7A" && git rev-parse HEAD)
mkrow "s-git-clean" "in_progress" "null" "null" "null" "clean" "[]" \
  > "$T7A/.claude/harness/telemetry.jsonl"
DIFF=$(jq -n -c '[]')
run_hook "$T7A" '{"session_id":"s-git-clean"}' "$DIFF" || true
HASH=$(jq -r .commit_hash "$T7A/.claude/harness/telemetry.jsonl")
if [ "$HASH" = "$EXPECTED_HASH_7A" ]; then
  ok "T7a clean repo: commit_hash matches HEAD"
else
  bad "T7a clean repo: got $HASH, expected $EXPECTED_HASH_7A"
fi

# 7b: dirty working tree (HEAD still resolves)
T7B="$TMPROOT/t7b"
mkdir -p "$T7B/.claude/harness"
git_init_repo "$T7B"
( cd "$T7B" && echo "dirty" >> a.txt )  # uncommitted change
EXPECTED_HASH_7B=$(cd "$T7B" && git rev-parse HEAD)
mkrow "s-git-dirty" "in_progress" "null" "null" "null" "dirty" "[]" \
  > "$T7B/.claude/harness/telemetry.jsonl"
DIFF=$(jq -n -c '[]')
run_hook "$T7B" '{"session_id":"s-git-dirty"}' "$DIFF" || true
HASH=$(jq -r .commit_hash "$T7B/.claude/harness/telemetry.jsonl")
if [ "$HASH" = "$EXPECTED_HASH_7B" ]; then
  ok "T7b dirty tree: commit_hash resolves to HEAD despite dirty WT"
else
  bad "T7b dirty tree: got $HASH, expected $EXPECTED_HASH_7B"
fi

# 7c: detached HEAD
T7C="$TMPROOT/t7c"
mkdir -p "$T7C/.claude/harness"
git_init_repo "$T7C"
( cd "$T7C" && echo v2 > a.txt && git add a.txt && git commit -q -m "v2" \
    && git checkout -q --detach HEAD~1 )
EXPECTED_HASH_7C=$(cd "$T7C" && git rev-parse HEAD)
mkrow "s-git-detached" "in_progress" "null" "null" "null" "detached" "[]" \
  > "$T7C/.claude/harness/telemetry.jsonl"
DIFF=$(jq -n -c '[]')
run_hook "$T7C" '{"session_id":"s-git-detached"}' "$DIFF" || true
HASH=$(jq -r .commit_hash "$T7C/.claude/harness/telemetry.jsonl")
if [ "$HASH" = "$EXPECTED_HASH_7C" ]; then
  ok "T7c detached HEAD: commit_hash resolves correctly"
else
  bad "T7c detached HEAD: got $HASH, expected $EXPECTED_HASH_7C"
fi

# 7d: no .git → graceful null fallback
T7D="$TMPROOT/t7d"
mkdir -p "$T7D/.claude/harness"
mkrow "s-git-none" "in_progress" "null" "null" "null" "no git" "[]" \
  > "$T7D/.claude/harness/telemetry.jsonl"
DIFF=$(jq -n -c '[]')
run_hook "$T7D" '{"session_id":"s-git-none"}' "$DIFF" || true
HASH_RAW=$(jq -c .commit_hash "$T7D/.claude/harness/telemetry.jsonl")
if [ "$HASH_RAW" = "null" ]; then
  ok "T7d no-git: commit_hash is null (graceful fallback)"
else
  bad "T7d no-git: expected null, got $HASH_RAW"
fi

# -------------------------------------------------------------------------
# Test 8: flock concurrency — 20 forks for the SAME session_id. One
# in_progress row pre-seeded; final telemetry has exactly that row in
# completed state, with valid JSON throughout.
# -------------------------------------------------------------------------
T8="$TMPROOT/t8"
mkdir -p "$T8/.claude/harness"
mkrow "s-conc-shared" "in_progress" "null" "null" "null" "concurrent" "[]" \
  > "$T8/.claude/harness/telemetry.jsonl"
N=20
DIFF=$(jq -n -c '[{path:"src/conc.py", plus:1, minus:0}]')
seq 1 $N | xargs -P "$N" -I{} bash -c "
  printf '{\"session_id\":\"s-conc-shared\"}' \
    | env CLAUDE_PROJECT_DIR='$T8' POST_TOOL_USE_TEST_DIFF='$DIFF' \
        POST_TOOL_USE_TEST_COMMIT='\"aaaa{}bbbbccccddddeeeeffff0011223344556677\"' \
        '$HOOK'
" 2>/dev/null

LINES=$(wc -l < "$T8/.claude/harness/telemetry.jsonl")
if [ "$LINES" -ne 1 ]; then
  bad "T8 concurrency: expected 1 row, got $LINES"
else
  ROW=$(cat "$T8/.claude/harness/telemetry.jsonl")
  if echo "$ROW" | jq -e . >/dev/null 2>&1; then
    STATE=$(echo "$ROW" | jq -r .terminal_state)
    if [ "$STATE" = "completed" ]; then
      ok "T8 concurrency: 1 row, valid JSON, terminal_state=completed under 20-fork"
    else
      bad "T8 concurrency: state=$STATE (want completed); row=$ROW"
    fi
  else
    bad "T8 concurrency: row not valid JSON: $ROW"
  fi
fi

# -------------------------------------------------------------------------
# Test 9: no matching row -> append a new completed row.
# -------------------------------------------------------------------------
T9="$TMPROOT/t9"
mkdir -p "$T9/.claude/harness"
# Pre-existing UNRELATED row, so locate-by-session_id misses.
mkrow "s-other" "in_progress" "null" "null" "null" "other" "[]" \
  > "$T9/.claude/harness/telemetry.jsonl"
PAYLOAD='{"session_id":"s-orphan"}'
DIFF=$(jq -n -c '[{path:"src/orphan.py", plus:3, minus:0}]')
COMMIT='"1111111111111111111111111111111111111111"'
run_hook "$T9" "$PAYLOAD" "$DIFF" "$COMMIT" || true

LINES=$(wc -l < "$T9/.claude/harness/telemetry.jsonl")
if [ "$LINES" -ne 2 ]; then
  bad "T9 orphan: expected 2 rows (1 existing + 1 appended), got $LINES"
else
  NEW_ROW=$(tail -1 "$T9/.claude/harness/telemetry.jsonl")
  STATE=$(echo "$NEW_ROW" | jq -r .terminal_state)
  SID=$(echo "$NEW_ROW" | jq -r .session_id)
  HAS_ALL=$(echo "$NEW_ROW" | jq -r '
    has("session_id") and has("terminal_state") and has("prompt_text")
      and has("skill_outcome") and has("commit_hash")
      and has("diff_summary_redacted") and has("attempt_history")')
  if [ "$SID" = "s-orphan" ] && [ "$STATE" = "completed" ] && [ "$HAS_ALL" = "true" ]; then
    ok "T9 orphan: appended new completed row with 7 fields"
  else
    bad "T9 orphan: SID=$SID STATE=$STATE HAS_ALL=$HAS_ALL row=$NEW_ROW"
  fi
fi

# -------------------------------------------------------------------------
# Test 10: strict CAS — malformed/unknown terminal_state stays as-is.
# Schema rule: "only lift in_progress -> completed". Anything else
# (including malformed values) must not be promoted.
# -------------------------------------------------------------------------
T10="$TMPROOT/t10"
mkdir -p "$T10/.claude/harness"
mkrow "s-cas-bogus" "BOGUS_STATE" "null" "null" "null" "malformed" "[]" \
  > "$T10/.claude/harness/telemetry.jsonl"
PAYLOAD='{"session_id":"s-cas-bogus"}'
DIFF=$(jq -n -c '[{path:"src/z.py", plus:1, minus:0}]')
COMMIT='"9999999999999999999999999999999999999999"'
run_hook "$T10" "$PAYLOAD" "$DIFF" "$COMMIT" || true

ROW=$(cat "$T10/.claude/harness/telemetry.jsonl")
STATE=$(echo "$ROW" | jq -r .terminal_state)
HASH=$(echo "$ROW" | jq -r .commit_hash)
if [ "$STATE" != "BOGUS_STATE" ]; then
  bad "T10 strict CAS: malformed state lifted to '$STATE' (must stay BOGUS_STATE)"
elif [ "$HASH" != "9999999999999999999999999999999999999999" ]; then
  bad "T10 strict CAS: commit_hash not merged (got $HASH)"
else
  ok "T10 strict CAS: malformed state preserved, non-state fields merged"
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
