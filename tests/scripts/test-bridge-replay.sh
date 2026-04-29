#!/usr/bin/env bash
# Tests for plugins/baransu/scripts/bridge-replay.sh.
#
# Coverage (TASK-scripts-03):
#   1. Worktree creation under /tmp/baransu-bridge-XXXXXX (INT-8)
#   2. EXIT trap cleanup on success (worktree + tmpdir gone)
#   3. SIGINT trap cleanup (INT-9a)
#   4. Inconclusive cleanup (INT-9b — corpus < N exits non-zero, trap still cleans)
#   5. Statistical gate pass: Δ within ±0.15 -> exit 0 + "pass"
#   6. Statistical gate fail: Δ <= -0.15 -> exit non-zero + "fail" + top-N degraded prompts
#   7. Statistical gate inconclusive: corpus too small -> exit non-zero + "inconclusive"
#
# Test seam: bridge-replay accepts a SKILL_RUNNER env var that points to a stub
# command. The stub takes args "<version> <prompt_text>" and prints a single
# float score on stdout. For real /bridge invocations the default runner wires
# into the baransu skill subprocess; tests override with a deterministic stub.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT_PATH="$WORKTREE_ROOT/plugins/baransu/scripts/bridge-replay.sh"

PASS=0
FAIL=0
FAILED_TESTS=()

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

# Make a sandbox repo containing a working tree + telemetry corpus, so the
# bridge script can `git worktree add` against a target branch without
# touching the real baransu repo.
make_sandbox_repo() {
  local repo_root="$1"
  mkdir -p "$repo_root"
  git -C "$repo_root" init -q -b main
  git -C "$repo_root" config user.email "test@example.com"
  git -C "$repo_root" config user.name "test"
  git -C "$repo_root" config commit.gpgsign false
  echo "main" >"$repo_root/file.txt"
  git -C "$repo_root" add file.txt
  git -C "$repo_root" commit -q -m "initial on main"

  # Create a target branch with a different commit, but same author email
  # (so trust check passes by default).
  git -C "$repo_root" checkout -q -b target-branch
  echo "v2" >"$repo_root/file.txt"
  git -C "$repo_root" commit -q -am "v2 change"
  git -C "$repo_root" checkout -q main
}

# Write N completed telemetry rows to .claude/harness/telemetry.jsonl.
write_corpus() {
  local repo_root="$1"
  local n="$2"
  local dir="$repo_root/.claude/harness"
  mkdir -p "$dir"
  : >"$dir/telemetry.jsonl"
  local i
  for i in $(seq 1 "$n"); do
    printf '{"session_id":"s-%03d","terminal_state":"completed","prompt_text":"prompt %03d","skill_outcome":{"skill_name":"think","final_state":"approved","exit_code":0},"commit_hash":"%040d","diff_summary_redacted":[],"attempt_history":[]}\n' \
      "$i" "$i" "$i" >>"$dir/telemetry.jsonl"
  done
}

# Build a stub skill runner. Args: stub_path, v1_score, v2_score.
# Prints v1_score for "v1 <prompt>" calls, v2_score for "v2 <prompt>" calls.
make_stub_runner() {
  local stub="$1"
  local v1="$2"
  local v2="$3"
  cat >"$stub" <<EOF
#!/usr/bin/env bash
case "\$1" in
  v1) echo "$v1" ;;
  v2) echo "$v2" ;;
  *) echo "0.5" ;;
esac
EOF
  chmod +x "$stub"
}

# Create a stub that consumes prompt_text to vary per-prompt scores —
# used for top-N degraded prompts assertion.
make_varying_stub_runner() {
  local stub="$1"
  cat >"$stub" <<'EOF'
#!/usr/bin/env bash
# v1 always 1.0; v2 varies — the worst prompt index (encoded in prompt_text)
# defines the largest negative delta.
version="$1"
prompt="$2"
if [[ "$version" == "v1" ]]; then
  echo "1.0"
else
  # Extract trailing integer from "prompt NNN".
  num="${prompt##* }"
  # Strip leading zeros without triggering octal interpretation.
  num="$((10#$num))"
  # Force a clear gradient: lower index = larger drop.
  # idx 1 -> 0.0 (drop 1.0), idx 2 -> 0.1, ..., idx 11 -> 1.0
  case "$num" in
    1) echo "0.0" ;;
    2) echo "0.1" ;;
    3) echo "0.2" ;;
    4) echo "0.3" ;;
    5) echo "0.4" ;;
    6) echo "0.5" ;;
    *) echo "0.9" ;;
  esac
fi
EOF
  chmod +x "$stub"
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

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

# Test 1: worktree creation under /tmp/baransu-bridge-* (and cleanup after).
test_worktree_creation_and_exit_cleanup() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  make_sandbox_repo "$sandbox/repo"
  write_corpus "$sandbox/repo" 5
  local stub="$sandbox/stub.sh"
  make_stub_runner "$stub" "0.5" "0.5"

  # Snapshot worktree list before.
  local before_list
  before_list="$(git -C "$sandbox/repo" worktree list)"

  # Invoke; corpus is 5, so we lower the gate.
  pushd "$sandbox/repo" >/dev/null
  SKILL_RUNNER="$stub" bash "$SCRIPT_PATH" \
    --target-branch target-branch \
    --skill think \
    --corpus-size 5 \
    --allow-untrusted >/dev/null 2>&1
  local rc=$?
  popd >/dev/null

  # rc should be 0 (pass; v1==v2==0.5 -> Δ=0).
  [[ $rc -eq 0 ]] || { echo "    rc=$rc (expected 0)"; return 1; }

  # After exit, no /tmp/baransu-bridge-* dir remains, and worktree list
  # is back to baseline (no leftover entry).
  if compgen -G "/tmp/baransu-bridge-*" >/dev/null; then
    # tolerate dirs unrelated to this test only if they're not associated
    # with the sandbox repo
    if git -C "$sandbox/repo" worktree list | grep -q "/tmp/baransu-bridge-"; then
      echo "    leftover worktree entry"
      return 1
    fi
  fi
  return 0
}

# Test 2: a parallel "during run" check that the worktree IS visible while
# the script is paused. We use a stub that sleeps so we can inspect mid-run.
test_worktree_present_during_run() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  make_sandbox_repo "$sandbox/repo"
  write_corpus "$sandbox/repo" 3

  local stub="$sandbox/stub.sh"
  cat >"$stub" <<EOF
#!/usr/bin/env bash
# Block until a sentinel file appears, then output a score.
while [[ ! -f "$sandbox/release" ]]; do sleep 0.05; done
echo "0.5"
EOF
  chmod +x "$stub"

  pushd "$sandbox/repo" >/dev/null
  SKILL_RUNNER="$stub" bash "$SCRIPT_PATH" \
    --target-branch target-branch \
    --skill think \
    --corpus-size 3 \
    --allow-untrusted >/dev/null 2>&1 &
  local pid=$!
  popd >/dev/null

  # Wait up to 5s for a /tmp/baransu-bridge-* worktree to appear.
  local appeared=0
  for _ in $(seq 1 100); do
    if git -C "$sandbox/repo" worktree list | grep -q "/tmp/baransu-bridge-"; then
      appeared=1
      break
    fi
    sleep 0.05
  done

  # Release the stub so the script proceeds.
  touch "$sandbox/release"
  wait "$pid" 2>/dev/null

  # Cleanup must have happened.
  local after_clean=0
  if ! git -C "$sandbox/repo" worktree list | grep -q "/tmp/baransu-bridge-"; then
    after_clean=1
  fi

  [[ $appeared -eq 1 ]] || { echo "    worktree never appeared"; return 1; }
  [[ $after_clean -eq 1 ]] || { echo "    cleanup didn't run"; return 1; }
  return 0
}

# Test 3: SIGINT cleanup (INT-9a).
test_sigint_cleanup() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  make_sandbox_repo "$sandbox/repo"
  write_corpus "$sandbox/repo" 3

  local stub="$sandbox/stub.sh"
  # Stub blocks indefinitely.
  cat >"$stub" <<'EOF'
#!/usr/bin/env bash
sleep 60
echo "0.5"
EOF
  chmod +x "$stub"

  pushd "$sandbox/repo" >/dev/null
  SKILL_RUNNER="$stub" bash "$SCRIPT_PATH" \
    --target-branch target-branch \
    --skill think \
    --corpus-size 3 \
    --allow-untrusted >/dev/null 2>&1 &
  local pid=$!
  popd >/dev/null

  # Wait for worktree to appear.
  local appeared=0
  for _ in $(seq 1 100); do
    if git -C "$sandbox/repo" worktree list | grep -q "/tmp/baransu-bridge-"; then
      appeared=1
      break
    fi
    sleep 0.05
  done
  [[ $appeared -eq 1 ]] || { kill "$pid" 2>/dev/null; echo "    worktree didn't appear"; return 1; }

  # Send SIGINT.
  kill -INT "$pid" 2>/dev/null
  # Also kill the stub child(ren), since SIGINT to the script doesn't
  # propagate to bash's "sleep 60" subprocess in all configurations.
  pkill -P "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null

  # Wait briefly for trap to finish (worktree remove can be slow).
  for _ in $(seq 1 40); do
    if ! git -C "$sandbox/repo" worktree list | grep -q "/tmp/baransu-bridge-"; then
      return 0
    fi
    sleep 0.05
  done

  echo "    worktree leftover after SIGINT"
  git -C "$sandbox/repo" worktree list >&2
  return 1
}

# Test 4: corpus too small triggers inconclusive + trap still runs.
test_inconclusive_cleanup() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  make_sandbox_repo "$sandbox/repo"
  # Only 2 completed rows; require 5 -> inconclusive.
  write_corpus "$sandbox/repo" 2

  local stub="$sandbox/stub.sh"
  make_stub_runner "$stub" "1.0" "1.0"

  pushd "$sandbox/repo" >/dev/null
  local out
  out="$(SKILL_RUNNER="$stub" bash "$SCRIPT_PATH" \
    --target-branch target-branch \
    --skill think \
    --corpus-size 5 \
    --allow-untrusted 2>&1)"
  local rc=$?
  popd >/dev/null

  [[ $rc -ne 0 ]] || { echo "    rc=$rc (expected non-zero)"; return 1; }
  echo "$out" | grep -qi "inconclusive" || { echo "    no 'inconclusive' in output: $out"; return 1; }

  # Worktree may or may not have been created (script can exit before).
  # Either way, no /tmp/baransu-bridge-* under this repo.
  if git -C "$sandbox/repo" worktree list | grep -q "/tmp/baransu-bridge-"; then
    echo "    leftover worktree"
    return 1
  fi
  return 0
}

# Test 5: gate pass — Δ within threshold.
test_gate_pass() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  make_sandbox_repo "$sandbox/repo"
  write_corpus "$sandbox/repo" 5

  local stub="$sandbox/stub.sh"
  # v1 = 0.5, v2 = 0.5 -> Δ = 0
  make_stub_runner "$stub" "0.5" "0.5"

  pushd "$sandbox/repo" >/dev/null
  local out
  out="$(SKILL_RUNNER="$stub" bash "$SCRIPT_PATH" \
    --target-branch target-branch \
    --skill think \
    --corpus-size 5 \
    --allow-untrusted 2>&1)"
  local rc=$?
  popd >/dev/null

  [[ $rc -eq 0 ]] || { echo "    rc=$rc (expected 0); out=$out"; return 1; }
  echo "$out" | grep -qi "pass" || { echo "    no 'pass' in output: $out"; return 1; }
  return 0
}

# Test 6: gate fail — v2 lower than v1 by >= 0.15 — and top-N degraded prompts.
test_gate_fail_with_top_n() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  make_sandbox_repo "$sandbox/repo"
  write_corpus "$sandbox/repo" 7

  local stub="$sandbox/stub.sh"
  # Use varying stub: v1=1.0 always; v2 by index (1→0, 2→0.1, ..., 7→0.9).
  # Avg v2 ≈ 0.343 -> Δ = -0.657, well past -0.15 -> fail.
  make_varying_stub_runner "$stub"

  pushd "$sandbox/repo" >/dev/null
  local out
  out="$(SKILL_RUNNER="$stub" bash "$SCRIPT_PATH" \
    --target-branch target-branch \
    --skill think \
    --corpus-size 5 \
    --allow-untrusted 2>&1)"
  local rc=$?
  popd >/dev/null

  [[ $rc -ne 0 ]] || { echo "    rc=$rc (expected non-zero); out=$out"; return 1; }
  echo "$out" | grep -qi "fail" || { echo "    no 'fail' in output: $out"; return 1; }

  # Top-N section should mention the worst prompts. The varying stub
  # makes prompt 001 the worst-degraded. Confirm "001" appears in output.
  echo "$out" | grep -q "001" || { echo "    top-N didn't list worst prompt; out=$out"; return 1; }
  return 0
}

# Test 7: gate inconclusive — variant where corpus=N but post-filter is too few.
# Already covered by test_inconclusive_cleanup; here we add a second flavor:
# small corpus + non-failing scores still inconclusive (must NOT report pass).
test_gate_inconclusive_no_false_pass() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap "rm -rf '$sandbox'" RETURN
  make_sandbox_repo "$sandbox/repo"
  write_corpus "$sandbox/repo" 1   # 1 row, far below threshold

  local stub="$sandbox/stub.sh"
  # Even though scores match (no regression), corpus too small -> inconclusive.
  make_stub_runner "$stub" "0.9" "0.9"

  pushd "$sandbox/repo" >/dev/null
  local out
  out="$(SKILL_RUNNER="$stub" bash "$SCRIPT_PATH" \
    --target-branch target-branch \
    --skill think \
    --corpus-size 5 \
    --allow-untrusted 2>&1)"
  local rc=$?
  popd >/dev/null

  [[ $rc -ne 0 ]] || { echo "    rc=$rc (expected non-zero)"; return 1; }
  echo "$out" | grep -qi "inconclusive" || { echo "    no 'inconclusive': $out"; return 1; }
  echo "$out" | grep -qiv "^pass$" || true   # informational only
  return 0
}

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

[[ -x "$SCRIPT_PATH" ]] || {
  echo "NOTE: $SCRIPT_PATH not executable yet (Red gate expected)."
}

echo "Running bridge-replay tests..."

run_test "1. worktree creation + EXIT trap cleanup"     test_worktree_creation_and_exit_cleanup
run_test "2. worktree present during run"               test_worktree_present_during_run
run_test "3. SIGINT cleanup (INT-9a)"                   test_sigint_cleanup
run_test "4. inconclusive cleanup (INT-9b)"             test_inconclusive_cleanup
run_test "5. gate pass"                                 test_gate_pass
run_test "6. gate fail + top-N"                         test_gate_fail_with_top_n
run_test "7. gate inconclusive (no false pass)"         test_gate_inconclusive_no_false_pass

echo ""
echo "Summary: $PASS passed, $FAIL failed."
if (( FAIL > 0 )); then
  printf '  - %s\n' "${FAILED_TESTS[@]}"
  exit 1
fi
exit 0
