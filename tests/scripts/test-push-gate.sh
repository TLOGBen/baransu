#!/usr/bin/env bash
# Tests for plugins/baransu/scripts/push-gate.sh.
#
# Coverage (TASK-enforcement-01):
#   T1  — deny: plugin.json -> exit 1 + escalate=requires_human
#   T2  — deny self-write: hooks/user-prompt-submit.py -> requires_human
#   T3  — preflight: /etc/passwd -> requires_human
#   T4  — attempt cap K=3 -> escalate=escalate_human
#   T5  — daily quota=5 today -> escalate=daily_quota_exceeded
#   T6  — reset path: yesterday -> today resets count, then happy path exit 0
#   T7  — happy path: all gates pass -> exit 0
#   T8  — partition preservation: grade keys byte-identical after reset
#   T9  — multi-step reset+exhaust (B5): reset, 4 more pushes, 6th -> quota
#   T10 — ORDER short-circuit: denylist beats attempt-cap; preflight beats quota
#   T11 — 9 deny rows enumerated (REQ-002 Scenario 7) + negative case

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT_PATH="$WORKTREE_ROOT/plugins/baransu/scripts/push-gate.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

# Build a git repo at $repo with two commits, the second of which adds the
# given file path. After this, `git -C $repo diff --name-only HEAD~1 HEAD`
# returns exactly that path.
make_fixture_with_diff_path() {
  local repo="$1"
  local diff_path="$2"
  mkdir -p "$repo"
  git -C "$repo" init -q -b main
  git -C "$repo" config user.email "test@example.com"
  git -C "$repo" config user.name "test"
  git -C "$repo" config commit.gpgsign false
  echo "baseline" >"$repo/baseline.txt"
  git -C "$repo" add baseline.txt
  git -C "$repo" commit -q -m "baseline"

  # We may need to create the path even if it starts with "/" or "~/" —
  # but those obviously can't be created in the repo. For preflight tests
  # we instead inject the path via a fake git binary; see make_fixture_fake_diff.
  local dir
  dir="$(dirname "$diff_path")"
  if [[ "$dir" != "." ]]; then
    mkdir -p "$repo/$dir"
  fi
  echo "x" >"$repo/$diff_path"
  git -C "$repo" add -- "$diff_path"
  git -C "$repo" commit -q -m "add $diff_path"
}

# Build a fixture where `git -C <repo> diff --name-only HEAD~1 HEAD` returns
# a literal path that cannot exist on disk (e.g. starts with "/" or "~").
# We accomplish this with a shim `git` on PATH: the shim intercepts only the
# specific `diff --name-only HEAD~1 HEAD` invocation and prints the desired
# path, falling through to the real git for everything else.
#
# Usage: make_fixture_fake_diff <repo> <fake_path>
make_fixture_fake_diff() {
  local repo="$1"
  local fake_path="$2"
  local shimdir="$3"
  mkdir -p "$repo"
  git -C "$repo" init -q -b main
  git -C "$repo" config user.email "test@example.com"
  git -C "$repo" config user.name "test"
  git -C "$repo" config commit.gpgsign false
  echo "baseline" >"$repo/baseline.txt"
  git -C "$repo" add baseline.txt
  git -C "$repo" commit -q -m "baseline"
  echo "second" >"$repo/second.txt"
  git -C "$repo" add second.txt
  git -C "$repo" commit -q -m "second"

  mkdir -p "$shimdir"
  local real_git
  real_git="$(command -v git)"
  cat >"$shimdir/git" <<EOF
#!/usr/bin/env bash
# Shim that returns a fake diff path for HEAD~1..HEAD on a specific repo.
args=("\$@")
n=\${#args[@]}
# Look for "-C <repo> diff --name-only HEAD~1 HEAD".
if [[ "\${args[0]:-}" == "-C" && "\${args[1]:-}" == "$repo" \\
      && "\${args[2]:-}" == "diff" && "\${args[3]:-}" == "--name-only" \\
      && "\${args[4]:-}" == "HEAD~1" && "\${args[5]:-}" == "HEAD" ]]; then
  printf '%s\n' "$fake_path"
  exit 0
fi
exec "$real_git" "\$@"
EOF
  chmod +x "$shimdir/git"
}

# Make a state.json for a given count + date with optional pre-existing
# grade-partition keys (to assert byte-identity).
write_state_json() {
  local path="$1"
  local count="$2"
  local date="$3"
  local extra_grade_json="${4:-}"
  mkdir -p "$(dirname "$path")"
  if [[ -n "$extra_grade_json" ]]; then
    cat >"$path" <<EOF
{
  "daily_push_count": $count,
  "daily_push_date": "$date",
  "last_triage_run_at": null,
  $extra_grade_json
}
EOF
  else
    cat >"$path" <<EOF
{
  "daily_push_count": $count,
  "daily_push_date": "$date",
  "last_triage_run_at": null
}
EOF
  fi
}

# Make a telemetry.jsonl with N fail rows for cluster_id under attempt_history.
write_telemetry_with_fails() {
  local path="$1"
  local cluster_id="$2"
  local fails="$3"
  mkdir -p "$(dirname "$path")"
  : >"$path"
  if (( fails == 0 )); then
    return 0
  fi
  # Single telemetry row containing $fails fail entries for cluster_id in
  # attempt_history. push-gate's jq filter aggregates across all rows so
  # 1 row with N fails equals N rows with 1 fail each — equivalent.
  local entries=""
  local i
  for i in $(seq 1 "$fails"); do
    if (( i > 1 )); then entries+=","; fi
    entries+="{\"cluster_id\":\"$cluster_id\",\"result\":\"fail\",\"run_at\":\"2026-04-29T03:00:00Z\"}"
  done
  printf '{"session_id":"s-001","attempt_history":[%s]}\n' "$entries" >>"$path"
}

write_empty_telemetry() {
  local path="$1"
  mkdir -p "$(dirname "$path")"
  : >"$path"
}

run_test() {
  local name="$1"
  shift
  if "$@"; then
    PASS=$((PASS + 1))
    echo "  PASS: $name"
  else
    FAIL=$((FAIL + 1))
    FAILED_TESTS+=("$name")
    echo "  FAIL: $name"
  fi
}

# Run push-gate.sh capturing stdout, exit code, and (if applicable) escalate.
# Args: <repo> <state> <tl> <cluster_id>
run_gate() {
  local repo="$1"
  local state="$2"
  local tl="$3"
  local cid="$4"
  bash "$SCRIPT_PATH" "$cid" "$repo" "$state" "$tl"
}

# ---------------------------------------------------------------------------
# T1: deny plugin.json -> exit 1 + escalate=requires_human
# ---------------------------------------------------------------------------
test_t1_deny_plugin_json() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/.claude-plugin/plugin.json"
  write_state_json "$state" 0 "2026-04-29"
  write_empty_telemetry "$tl"

  out="$(run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || { echo "    rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=requires_human" || {
    echo "    no requires_human in output: $out"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T2: deny hooks/ — self-write -> requires_human
# ---------------------------------------------------------------------------
test_t2_deny_hooks_self_write() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/hooks/user-prompt-submit.py"
  write_state_json "$state" 0 "2026-04-29"
  write_empty_telemetry "$tl"

  out="$(run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || { echo "    rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=requires_human" || {
    echo "    no requires_human: $out"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T3: preflight -> /etc/passwd -> requires_human
# ---------------------------------------------------------------------------
test_t3_preflight_etc_passwd() {
  local sandbox repo state tl shim out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  shim="$sandbox/shim"
  make_fixture_fake_diff "$repo" "/etc/passwd" "$shim"
  write_state_json "$state" 0 "2026-04-29"
  write_empty_telemetry "$tl"

  out="$(PATH="$shim:$PATH" run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || { echo "    rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=requires_human" || {
    echo "    no requires_human: $out"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T4: attempt cap K=3 -> escalate_human
# Diff is in-scope (no deny hit); telemetry has 3 fails for cluster_x.
# ---------------------------------------------------------------------------
test_t4_attempt_cap() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/skills/grade/SKILL.md"
  write_state_json "$state" 0 "2026-04-29"
  write_telemetry_with_fails "$tl" "cluster_x" 3

  out="$(run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || { echo "    rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=escalate_human" || {
    echo "    no escalate_human: $out"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T5: daily quota=5 today -> daily_quota_exceeded
# ---------------------------------------------------------------------------
test_t5_quota_today() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/skills/grade/SKILL.md"
  write_state_json "$state" 5 "2026-04-29"
  write_empty_telemetry "$tl"

  out="$(BARANSU_HARNESS_FAKE_NOW="2026-04-29" run_gate \
    "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || { echo "    rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=daily_quota_exceeded" || {
    echo "    no daily_quota_exceeded: $out"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T6: reset yesterday -> today, count=5 -> reset, happy path exit 0
# ---------------------------------------------------------------------------
test_t6_reset_then_pass() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/skills/grade/SKILL.md"
  write_state_json "$state" 5 "2026-04-28"
  write_empty_telemetry "$tl"

  out="$(BARANSU_HARNESS_FAKE_NOW="2026-04-29" run_gate \
    "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 0 ]] || { echo "    rc=$rc (expected 0); out=$out"; return 1; }

  # State should now have count=1 (reset to 0, incremented after happy path)
  # and date=2026-04-29.
  local count_after date_after
  count_after="$(jq -r '.daily_push_count' "$state")"
  date_after="$(jq -r '.daily_push_date' "$state")"
  [[ "$count_after" == "1" ]] || {
    echo "    count_after=$count_after (expected 1)"; return 1; }
  [[ "$date_after" == "2026-04-29" ]] || {
    echo "    date_after=$date_after (expected 2026-04-29)"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T7: happy path -> exit 0
# ---------------------------------------------------------------------------
test_t7_happy_path() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/skills/grade/SKILL.md"
  write_state_json "$state" 0 "2026-04-29"
  write_empty_telemetry "$tl"

  out="$(BARANSU_HARNESS_FAKE_NOW="2026-04-29" run_gate \
    "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 0 ]] || { echo "    rc=$rc (expected 0); out=$out"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T8: partition preserved across reset (last_grade_run_at byte-identical)
# ---------------------------------------------------------------------------
test_t8_partition_preserved() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/skills/grade/SKILL.md"
  # Pre-populate grade partition with sentinel values.
  write_state_json "$state" 5 "2026-04-28" \
    '"GRADE_KEY_A": "SENTINEL_VALUE", "GRADE_KEY_B": 42, "GRADE_KEY_C": null'
  # Capture grade-partition bytes BEFORE.
  local before_bytes
  before_bytes="$(jq '{GRADE_KEY_A, GRADE_KEY_B, GRADE_KEY_C}' "$state")"
  write_empty_telemetry "$tl"

  out="$(BARANSU_HARNESS_FAKE_NOW="2026-04-29" run_gate \
    "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 0 ]] || { echo "    rc=$rc (expected 0); out=$out"; return 1; }

  local after_bytes
  after_bytes="$(jq '{GRADE_KEY_A, GRADE_KEY_B, GRADE_KEY_C}' "$state")"
  [[ "$before_bytes" == "$after_bytes" ]] || {
    echo "    grade-partition mutated"
    echo "    before: $before_bytes"
    echo "    after:  $after_bytes"
    return 1
  }
  return 0
}

# ---------------------------------------------------------------------------
# T9: multi-step reset+exhaust (B5)
# count=5, date=yesterday, FAKE_NOW=today
# 1st push: reset, exit 0, count -> 1
# pushes 2-5: count -> 5
# 6th push: exit 1 + daily_quota_exceeded
# ---------------------------------------------------------------------------
test_t9_multi_step_reset_exhaust() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/skills/grade/SKILL.md"
  write_state_json "$state" 5 "2026-04-28"
  write_empty_telemetry "$tl"

  local i count
  for i in 1 2 3 4 5; do
    out="$(BARANSU_HARNESS_FAKE_NOW="2026-04-29" run_gate \
      "$repo" "$state" "$tl" "cluster_x" 2>&1)"
    rc=$?
    [[ $rc -eq 0 ]] || {
      echo "    push #$i rc=$rc (expected 0); out=$out"; return 1; }
    count="$(jq -r '.daily_push_count' "$state")"
    [[ "$count" == "$i" ]] || {
      echo "    after push #$i count=$count (expected $i)"; return 1; }
  done

  # Sixth push should exhaust quota.
  out="$(BARANSU_HARNESS_FAKE_NOW="2026-04-29" run_gate \
    "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || {
    echo "    push #6 rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=daily_quota_exceeded" || {
    echo "    push #6 missing daily_quota_exceeded: $out"; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# T10: ORDER short-circuit
#   (a) deny + attempt-cap fixture -> requires_human (deny first)
#   (b) preflight + quota fixture  -> requires_human (preflight first)
# ---------------------------------------------------------------------------
test_t10_order_deny_beats_attempt_cap() {
  local sandbox repo state tl out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/.claude-plugin/plugin.json"
  write_state_json "$state" 0 "2026-04-29"
  # Telemetry has 3 fails for cluster_x — would trip attempt-cap if reached.
  write_telemetry_with_fails "$tl" "cluster_x" 3

  out="$(run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || { echo "    rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=requires_human" || {
    echo "    no requires_human: $out"; return 1; }
  # MUST NOT be escalate_human.
  if echo "$out" | grep -q "escalate=escalate_human"; then
    echo "    short-circuit failure: got escalate_human (denylist should win)"
    return 1
  fi
  return 0
}

test_t10_order_preflight_beats_quota() {
  local sandbox repo state tl shim out rc
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  shim="$sandbox/shim"
  make_fixture_fake_diff "$repo" "/etc/passwd" "$shim"
  # Quota is at 5 today — would trip if reached.
  write_state_json "$state" 5 "2026-04-29"
  write_empty_telemetry "$tl"

  out="$(PATH="$shim:$PATH" BARANSU_HARNESS_FAKE_NOW="2026-04-29" \
    run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  [[ $rc -eq 1 ]] || { echo "    rc=$rc (expected 1); out=$out"; return 1; }
  echo "$out" | grep -q "escalate=requires_human" || {
    echo "    no requires_human: $out"; return 1; }
  if echo "$out" | grep -q "escalate=daily_quota_exceeded"; then
    echo "    short-circuit failure: got daily_quota_exceeded (preflight should win)"
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------------------
# T11: 9 deny rows enumerated + negative case
# ---------------------------------------------------------------------------
test_t11_nine_deny_enumeration() {
  local i path sandbox repo state tl shim out rc
  # Most paths go through make_fixture_with_diff_path. `.git/**` cannot
  # be committed (git ignores its own dir), so for that single case we use
  # the same shim trick as the preflight test to fake the diff output.
  local -a deny_paths=(
    ".github/workflows/ci.yml"
    "plugins/baransu/.claude-plugin/plugin.json"
    ".claude-plugin/marketplace.json"
    ".gitignore"
    "plugins/baransu/scripts/grade-collector.py"
    "plugins/baransu/hooks/user-prompt-submit.py"
    "plugins/baransu/agents/investigator-agent.md"
    ".git/hooks/pre-commit"
    ".claude/settings.json"
  )

  for path in "${deny_paths[@]}"; do
    sandbox="$(mktemp -d)"
    repo="$sandbox/repo"
    state="$sandbox/state.json"
    tl="$sandbox/telemetry.jsonl"
    write_state_json "$state" 0 "2026-04-29"
    write_empty_telemetry "$tl"

    if [[ "$path" == .git/* ]]; then
      shim="$sandbox/shim"
      make_fixture_fake_diff "$repo" "$path" "$shim"
      out="$(PATH="$shim:$PATH" run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
      rc=$?
    else
      make_fixture_with_diff_path "$repo" "$path"
      out="$(run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
      rc=$?
    fi

    if [[ $rc -ne 1 ]]; then
      echo "    deny path '$path' rc=$rc (expected 1); out=$out"
      rm -rf "$sandbox"
      return 1
    fi
    if ! echo "$out" | grep -q "escalate=requires_human"; then
      echo "    deny path '$path' missing requires_human: $out"
      rm -rf "$sandbox"
      return 1
    fi
    rm -rf "$sandbox"
  done

  # Negative case: in-scope path that should NOT trip denylist.
  sandbox="$(mktemp -d)"
  repo="$sandbox/repo"
  state="$sandbox/state.json"
  tl="$sandbox/telemetry.jsonl"
  make_fixture_with_diff_path "$repo" "plugins/baransu/skills/grade/SKILL.md"
  write_state_json "$state" 0 "2026-04-29"
  write_empty_telemetry "$tl"

  out="$(BARANSU_HARNESS_FAKE_NOW="2026-04-29" run_gate \
    "$repo" "$state" "$tl" "cluster_x" 2>&1)"
  rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "    negative path rc=$rc (expected 0); out=$out"
    rm -rf "$sandbox"
    return 1
  fi
  rm -rf "$sandbox"
  return 0
}

# ---------------------------------------------------------------------------
# T12: subdir-nested denylist coverage (root-anchored glob hardening).
# Original globs `.gitignore` and `.claude/settings*.json` only matched the
# repo root. A nested config like `tools/.gitignore` or
# `subdir/.claude/settings.json` would silently bypass the denylist. This
# test pins the `**/...` variants so a future regression that drops them
# is caught.
# ---------------------------------------------------------------------------
test_t12_nested_denylist_variants() {
  local sandbox repo state tl out rc
  local -a nested_paths=(
    "tools/.gitignore"
    "subdir/.claude/settings.json"
  )
  for path in "${nested_paths[@]}"; do
    sandbox="$(mktemp -d)"
    repo="$sandbox/repo"
    state="$sandbox/state.json"
    tl="$sandbox/telemetry.jsonl"
    make_fixture_with_diff_path "$repo" "$path"
    write_state_json "$state" 0 "2026-04-29"
    write_empty_telemetry "$tl"

    out="$(run_gate "$repo" "$state" "$tl" "cluster_x" 2>&1)"
    rc=$?
    if [[ $rc -ne 1 ]]; then
      echo "    nested deny path '$path' rc=$rc (expected 1); out=$out"
      rm -rf "$sandbox"
      return 1
    fi
    if ! echo "$out" | grep -q "escalate=requires_human"; then
      echo "    nested deny path '$path' missing requires_human: $out"
      rm -rf "$sandbox"
      return 1
    fi
    rm -rf "$sandbox"
  done
  return 0
}

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

[[ -x "$SCRIPT_PATH" ]] || {
  echo "NOTE: $SCRIPT_PATH not executable yet (Red gate expected)."
}

echo "Running push-gate tests..."

run_test "T1  deny plugin.json"                          test_t1_deny_plugin_json
run_test "T2  deny hooks self-write"                     test_t2_deny_hooks_self_write
run_test "T3  preflight /etc/passwd"                     test_t3_preflight_etc_passwd
run_test "T4  attempt cap K=3"                           test_t4_attempt_cap
run_test "T5  daily quota=5 today"                       test_t5_quota_today
run_test "T6  reset yesterday->today + happy"            test_t6_reset_then_pass
run_test "T7  happy path"                                test_t7_happy_path
run_test "T8  partition preserved across reset"          test_t8_partition_preserved
run_test "T9  multi-step reset+exhaust (B5)"             test_t9_multi_step_reset_exhaust
run_test "T10a denylist beats attempt-cap"               test_t10_order_deny_beats_attempt_cap
run_test "T10b preflight beats quota"                    test_t10_order_preflight_beats_quota
run_test "T11 9-deny enumeration + negative"             test_t11_nine_deny_enumeration
run_test "T12 nested denylist variants (subdir)"         test_t12_nested_denylist_variants

echo ""
echo "Summary: $PASS passed, $FAIL failed."
if (( FAIL > 0 )); then
  printf '  - %s\n' "${FAILED_TESTS[@]}"
  exit 1
fi
exit 0
