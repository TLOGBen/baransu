#!/usr/bin/env bash
# Test suite for plugins/baransu/hooks/user-prompt-submit.py (TASK-hooks-01).
#
# Covers:
#   1) happy path: stdin payload -> telemetry.jsonl gets one valid JSON line
#      with 7 expected keys; terminal_state == "in_progress"; attempt_history == [].
#   2) disk-full / permission-denied: hook still exits 0 (does not block prompt).
#   3) redaction positives: 5 patterns each masked to <REDACTED:type>.
#   4) redaction negative: benign prompt unchanged.
#   5) concurrency: N parallel invocations -> exactly N valid JSONL lines.
#      Default N=100 (matches spec INT-1). Override with
#      CONCURRENCY_FORKS=20 bash tests/hooks/test-user-prompt-submit.sh
#      for faster local runs.
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$WORKTREE_ROOT/plugins/baransu/hooks/user-prompt-submit.py"

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

# Each test runs in its own scratch dir; the hook reads $CLAUDE_PROJECT_DIR
# (or falls back to cwd) to locate .claude/harness/.
TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

run_hook() {
  # $1 = scratch dir, $2 = JSON payload string
  local scratch="$1"
  local payload="$2"
  mkdir -p "$scratch/.claude/harness"
  ( cd "$scratch" && CLAUDE_PROJECT_DIR="$scratch" printf '%s' "$payload" \
      | "$HOOK" )
}

# -------------------------------------------------------------------------
# Test 1: happy path
# -------------------------------------------------------------------------
T1="$TMPROOT/t1"
mkdir -p "$T1/.claude/harness"
PAYLOAD='{"session_id":"s-test-001","prompt":"hello world"}'
( cd "$T1" && CLAUDE_PROJECT_DIR="$T1" printf '%s' "$PAYLOAD" | "$HOOK" )
T1_EXIT=$?

if [ $T1_EXIT -ne 0 ]; then
  bad "T1 happy path: hook exit code $T1_EXIT (want 0)"
elif [ ! -f "$T1/.claude/harness/telemetry.jsonl" ]; then
  bad "T1 happy path: telemetry.jsonl not created"
else
  LINES=$(wc -l < "$T1/.claude/harness/telemetry.jsonl")
  if [ "$LINES" -ne 1 ]; then
    bad "T1 happy path: expected 1 line, got $LINES"
  else
    ROW="$(cat "$T1/.claude/harness/telemetry.jsonl")"
    # all 7 keys present
    HAS_ALL=$(echo "$ROW" | jq -r '
      has("session_id") and has("terminal_state") and has("prompt_text")
        and has("skill_outcome") and has("commit_hash")
        and has("diff_summary_redacted") and has("attempt_history")
    ' 2>/dev/null)
    if [ "$HAS_ALL" != "true" ]; then
      bad "T1 happy path: row missing one of the 7 keys (row=$ROW)"
    elif [ "$(echo "$ROW" | jq -r .session_id)" != "s-test-001" ]; then
      bad "T1 happy path: session_id mismatch"
    elif [ "$(echo "$ROW" | jq -r .terminal_state)" != "in_progress" ]; then
      bad "T1 happy path: terminal_state != in_progress"
    elif [ "$(echo "$ROW" | jq -r .prompt_text)" != "hello world" ]; then
      bad "T1 happy path: prompt_text mismatch"
    elif [ "$(echo "$ROW" | jq -r '.attempt_history | length')" != "0" ]; then
      bad "T1 happy path: attempt_history not empty"
    else
      ok "T1 happy path: 7 fields, in_progress, attempt_history=[]"
    fi
  fi
fi

# -------------------------------------------------------------------------
# Test 2: permission denied -> exit 0 (non-blocking)
# -------------------------------------------------------------------------
T2="$TMPROOT/t2"
mkdir -p "$T2/.claude/harness"
chmod 500 "$T2/.claude/harness"   # readable + executable but not writable
PAYLOAD='{"session_id":"s-test-002","prompt":"perm denied test"}'
set +e
( cd "$T2" && CLAUDE_PROJECT_DIR="$T2" printf '%s' "$PAYLOAD" | "$HOOK" ) 2>/dev/null
T2_EXIT=$?
set -e
chmod 700 "$T2/.claude/harness"   # restore for cleanup
if [ $T2_EXIT -eq 0 ]; then
  ok "T2 permission denied: exit 0 (non-blocking)"
else
  bad "T2 permission denied: exit $T2_EXIT (want 0; hook must not block)"
fi
set -u

# -------------------------------------------------------------------------
# Test 3: 5 redaction positive patterns
# -------------------------------------------------------------------------
declare -a REDACTION_CASES=(
  "gitlab_token|my token is glpat-abcDEF1234567890ghijKL|<REDACTED:gitlab_token>"
  "github_token|here is ghp_abcDEF1234567890ghijKLmnoP|<REDACTED:github_token>"
  "aws_key|aws id AKIAIOSFODNN7EXAMPLE here|<REDACTED:aws_key>"
  "secret_kv|password=hunter2supersecret in config|<REDACTED:secret_kv>"
  "jwt|Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIi.signaturepart please|<REDACTED:jwt>"
  "slack_token|slack incoming xoxb-1234567890-AbCdEfGhIjKlMnOp here|<REDACTED:slack_token>"
  "stripe_key|prod key sk_live_4eC39HqLyjWDarjtT1zdp7dc rotate it|<REDACTED:stripe_key>"
  "azure_sas|blob url https://acct.blob.core.windows.net/c/b?sv=2021-08-06&ss=b&sig=Q5XR%2BabcdefghijklMnOpQrstUvWx%3D end|<REDACTED:azure_sas>"
)

for i in "${!REDACTION_CASES[@]}"; do
  IFS='|' read -r tag prompt expected <<< "${REDACTION_CASES[$i]}"
  TDIR="$TMPROOT/t3_$tag"
  mkdir -p "$TDIR/.claude/harness"
  PAYLOAD=$(jq -n --arg sid "s-red-$tag" --arg p "$prompt" \
    '{session_id:$sid, prompt:$p}')
  ( cd "$TDIR" && CLAUDE_PROJECT_DIR="$TDIR" printf '%s' "$PAYLOAD" | "$HOOK" ) || true
  if [ ! -f "$TDIR/.claude/harness/telemetry.jsonl" ]; then
    bad "T3.$tag: telemetry.jsonl not created"
    continue
  fi
  REDACTED=$(jq -r .prompt_text "$TDIR/.claude/harness/telemetry.jsonl")
  if echo "$REDACTED" | grep -qF "$expected"; then
    ok "T3.$tag: contains $expected"
  else
    bad "T3.$tag: expected '$expected' in prompt_text, got '$REDACTED'"
  fi
done

# GCP service account JSON: PEM body with JSON-escaped \n literals (not real newlines).
# The whole "private_key": "..." field must be redacted to <REDACTED:gcp_pk_json>.
T3GCP="$TMPROOT/t3_gcp_pk_json"
mkdir -p "$T3GCP/.claude/harness"
GCP_PROMPT='credentials: {"type": "service_account", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDexample\n-----END PRIVATE KEY-----\n", "client_email": "x@y.iam.gserviceaccount.com"}'
PAYLOAD=$(jq -n --arg sid "s-red-gcp" --arg p "$GCP_PROMPT" \
  '{session_id:$sid, prompt:$p}')
( cd "$T3GCP" && CLAUDE_PROJECT_DIR="$T3GCP" printf '%s' "$PAYLOAD" | "$HOOK" ) || true
if [ ! -f "$T3GCP/.claude/harness/telemetry.jsonl" ]; then
  bad "T3.gcp_pk_json: telemetry.jsonl not created"
else
  REDACTED=$(jq -r .prompt_text "$T3GCP/.claude/harness/telemetry.jsonl")
  if echo "$REDACTED" | grep -qF "<REDACTED:gcp_pk_json>" \
     && ! echo "$REDACTED" | grep -qF "MIIEvgIBADANBgkqhkiG"; then
    ok "T3.gcp_pk_json: JSON private_key field masked, PEM body removed"
  else
    bad "T3.gcp_pk_json: expected <REDACTED:gcp_pk_json> with PEM body removed; got '$REDACTED'"
  fi
fi

# PEM private key block (multi-line; pass via --arg with literal newlines)
T3PEM="$TMPROOT/t3_pem"
mkdir -p "$T3PEM/.claude/harness"
PEM_PROMPT=$'here is my key:\n-----BEGIN RSA PRIVATE KEY-----\nMIIBOgIBAAJB...\n-----END RSA PRIVATE KEY-----\nplease redact'
PAYLOAD=$(jq -n --arg sid "s-red-pem" --arg p "$PEM_PROMPT" \
  '{session_id:$sid, prompt:$p}')
( cd "$T3PEM" && CLAUDE_PROJECT_DIR="$T3PEM" printf '%s' "$PAYLOAD" | "$HOOK" ) || true
if [ ! -f "$T3PEM/.claude/harness/telemetry.jsonl" ]; then
  bad "T3.private_key: telemetry.jsonl not created"
else
  REDACTED=$(jq -r .prompt_text "$T3PEM/.claude/harness/telemetry.jsonl")
  if echo "$REDACTED" | grep -qF "<REDACTED:private_key>" \
     && ! echo "$REDACTED" | grep -qF "MIIBOgIBAAJB"; then
    ok "T3.private_key: PEM block masked, body removed"
  else
    bad "T3.private_key: expected <REDACTED:private_key> with body removed; got '$REDACTED'"
  fi
fi

# Truncated PEM (no END marker): full-block pattern misses, fragment fallback catches.
T3PEMFRAG="$TMPROOT/t3_pem_fragment"
mkdir -p "$T3PEMFRAG/.claude/harness"
PEM_FRAG_PROMPT=$'oops pasted only the start:\n-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA... (truncated)'
PAYLOAD=$(jq -n --arg sid "s-red-pem-frag" --arg p "$PEM_FRAG_PROMPT" \
  '{session_id:$sid, prompt:$p}')
( cd "$T3PEMFRAG" && CLAUDE_PROJECT_DIR="$T3PEMFRAG" printf '%s' "$PAYLOAD" | "$HOOK" ) || true
if [ ! -f "$T3PEMFRAG/.claude/harness/telemetry.jsonl" ]; then
  bad "T3.pem_fragment: telemetry.jsonl not created"
else
  REDACTED=$(jq -r .prompt_text "$T3PEMFRAG/.claude/harness/telemetry.jsonl")
  if echo "$REDACTED" | grep -qF "<REDACTED:pem_fragment>" \
     && ! echo "$REDACTED" | grep -qF "BEGIN RSA PRIVATE KEY"; then
    ok "T3.pem_fragment: leading marker masked on truncated paste"
  else
    bad "T3.pem_fragment: expected <REDACTED:pem_fragment> with marker removed; got '$REDACTED'"
  fi
fi

# -------------------------------------------------------------------------
# Test 3.label_integrity: secret_kv catch-all must NOT cannibalise
# placeholders produced by earlier specific patterns. Trigger condition:
# prompt has `(token|key|secret|password|api[_-]?key)` prefix + secret value
# matching a specific pattern (jwt/aws_key/stripe/slack/azure_sas). The
# specific pattern runs first → placeholder. secret_kv must skip the
# placeholder (negative lookahead `(?!<REDACTED:)`), preserving the
# specific label.
# -------------------------------------------------------------------------
declare -a LABEL_INTEGRITY_CASES=(
  "kv_jwt|api_key=eyJabc.eyJdef.signature123|<REDACTED:jwt>|<REDACTED:secret_kv>"
  "kv_aws|key=AKIAIOSFODNN7EXAMPLE|<REDACTED:aws_key>|<REDACTED:secret_kv>"
  "kv_slack|secret: xoxb-1234567890-AbCdEfGhIjKlMnOp|<REDACTED:slack_token>|<REDACTED:secret_kv>"
  "kv_stripe|password=sk_live_4eC39HqLyjWDarjtT1zdp7dc|<REDACTED:stripe_key>|<REDACTED:secret_kv>"
)

for entry in "${LABEL_INTEGRITY_CASES[@]}"; do
  IFS='|' read -r tag prompt expected_keep expected_absent <<< "$entry"
  TDIR="$TMPROOT/t3_label_$tag"
  mkdir -p "$TDIR/.claude/harness"
  PAYLOAD=$(jq -n --arg sid "s-label-$tag" --arg p "$prompt" \
    '{session_id:$sid, prompt:$p}')
  ( cd "$TDIR" && CLAUDE_PROJECT_DIR="$TDIR" printf '%s' "$PAYLOAD" | "$HOOK" ) || true
  if [ ! -f "$TDIR/.claude/harness/telemetry.jsonl" ]; then
    bad "T3.label_$tag: telemetry.jsonl not created"
    continue
  fi
  REDACTED=$(jq -r .prompt_text "$TDIR/.claude/harness/telemetry.jsonl")
  if echo "$REDACTED" | grep -qF "$expected_keep" \
     && ! echo "$REDACTED" | grep -qF "$expected_absent"; then
    ok "T3.label_$tag: specific label '$expected_keep' preserved (not cannibalised to secret_kv)"
  else
    bad "T3.label_$tag: expected '$expected_keep' kept and '$expected_absent' absent; got '$REDACTED'"
  fi
done

# -------------------------------------------------------------------------
# Test 4: redaction negative (benign prompt unchanged)
# -------------------------------------------------------------------------
T4="$TMPROOT/t4"
mkdir -p "$T4/.claude/harness"
BENIGN="please refactor the auth module and add tests"
PAYLOAD=$(jq -n --arg sid "s-benign" --arg p "$BENIGN" \
  '{session_id:$sid, prompt:$p}')
( cd "$T4" && CLAUDE_PROJECT_DIR="$T4" printf '%s' "$PAYLOAD" | "$HOOK" )
T4_TEXT=$(jq -r .prompt_text "$T4/.claude/harness/telemetry.jsonl")
if [ "$T4_TEXT" = "$BENIGN" ]; then
  ok "T4 benign prompt: unchanged"
else
  bad "T4 benign prompt: changed to '$T4_TEXT' (want '$BENIGN')"
fi

# -------------------------------------------------------------------------
# Test 5: concurrency — N parallel invocations (default N=100; INT-1 spec)
# -------------------------------------------------------------------------
T5="$TMPROOT/t5"
mkdir -p "$T5/.claude/harness"
N_FORKS="${CONCURRENCY_FORKS:-100}"
N=$N_FORKS
seq 1 $N | xargs -P "$N" -I{} bash -c "
  printf '{\"session_id\":\"s-c-{}\",\"prompt\":\"concurrent {}\"}' \
    | CLAUDE_PROJECT_DIR='$T5' '$HOOK'
"
LINES=$(wc -l < "$T5/.claude/harness/telemetry.jsonl")
if [ "$LINES" -ne $N ]; then
  bad "T5 concurrency: expected $N lines, got $LINES"
else
  # all lines must be valid JSON
  INVALID=0
  while IFS= read -r line; do
    if ! echo "$line" | jq -e . >/dev/null 2>&1; then
      INVALID=$((INVALID + 1))
    fi
  done < "$T5/.claude/harness/telemetry.jsonl"
  if [ $INVALID -gt 0 ]; then
    bad "T5 concurrency: $INVALID invalid JSON lines"
  else
    UNIQUE=$(jq -r .session_id "$T5/.claude/harness/telemetry.jsonl" | sort -u | wc -l)
    if [ "$UNIQUE" -ne $N ]; then
      bad "T5 concurrency: expected $N unique session_ids, got $UNIQUE"
    else
      ok "T5 concurrency: $N lines, all valid JSON, $N unique session_ids"
    fi
  fi
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
