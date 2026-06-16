#!/usr/bin/env bash
# test_tdd_trigger.sh — structural verification for TDD trigger plan v4
# (pruned for the v2 slim-down: /dev was removed; surviving triggers are
#  /execute impl-agent and /execute review-agent)
#
# Greps that the surviving deliverables are in place. Each check is
# deterministic; first failure prints reason and exits 1.
#
# CLI: test_tdd_trigger.sh
# Exit codes:
#   0 — all checks pass (TDD trigger reference + impl-agent/review-agent
#       citations + green_proof schema + 5-tier matrix + execute verify rule
#       + fixture all present)
#   1 — at least one check failed; stdout names the failing check

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  echo "FAIL: not in a git repo" >&2
  exit 1
fi
cd "$REPO_ROOT"

TDD_REF="plugins/baransu/skills/_shared/tdd.md"
IMPL_AGENT="plugins/baransu/agents/impl-agent.md"
REVIEW_AGENT="plugins/baransu/agents/review-agent.md"
EXECUTE_SKILL="plugins/baransu/skills/execute/SKILL.md"
FIXTURE_DIR="tests/scripts/fixtures/tdd-trigger"

fail_count=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1" >&2; fail_count=$((fail_count + 1)); }

# ---------------------------------------------------------------------------
# Check 1: _shared/tdd.md exists and has core content
# ---------------------------------------------------------------------------
echo "[1] _shared/tdd.md content"
if [[ ! -f "$TDD_REF" ]]; then
  fail "$TDD_REF does not exist"
else
  pass "$TDD_REF exists"
  grep -q "Matt Pocock\|mattpocock" "$TDD_REF" && pass "attribution found" || fail "no attribution to Matt Pocock"
  grep -q "MIT" "$TDD_REF" && pass "MIT license noted" || fail "no MIT license note"
  grep -qi "vertical slicing\|tracer bullet" "$TDD_REF" && pass "vertical slicing principle present" || fail "vertical slicing principle missing"
  grep -qi "behavior\|behaviour\|行為" "$TDD_REF" && pass "behavior-vs-implementation principle present" || fail "behavior-vs-implementation principle missing"
  grep -qi "mock.*boundary\|boundary.*mock\|系統邊界\|邊界" "$TDD_REF" && pass "mock-at-boundaries principle present" || fail "mock-at-boundaries principle missing"
  grep -qi "refactor.*green\|green.*refactor\|綠燈.*refactor\|refactor.*只.*綠" "$TDD_REF" && pass "refactor-only-when-green principle present" || fail "refactor-only-when-green principle missing"
  grep -qi "觸發點\|trigger.*point\|baransu-specific" "$TDD_REF" && pass "trigger-points section (§8) present" || fail "trigger-points section (§8) missing — referenced citation paths lose anchor"
  grep -q "impl-agent.md" "$TDD_REF" && pass "§8 cites impl-agent.md" || fail "§8 missing impl-agent.md citation"
  grep -q "review-agent.md" "$TDD_REF" && pass "§8 cites review-agent.md" || fail "§8 missing review-agent.md citation"
fi

# ---------------------------------------------------------------------------
# Check 2: impl-agent.md citation
# ---------------------------------------------------------------------------
echo "[2] impl-agent.md citation"
if [[ ! -f "$IMPL_AGENT" ]]; then
  fail "$IMPL_AGENT does not exist"
else
  grep -q "_shared/tdd.md" "$IMPL_AGENT" && pass "tdd.md path cited" || fail "tdd.md path not cited in $IMPL_AGENT"
  grep -qE "[Bb]efore writing tests.*tdd\.md|[Bb]efore the Red gate.*tdd\.md" "$IMPL_AGENT" && pass "passive citation phrasing present" || fail "passive citation phrasing missing in $IMPL_AGENT"
fi

# ---------------------------------------------------------------------------
# Check 3: review-agent.md citation + green_proof schema + 5-tier matrix
# ---------------------------------------------------------------------------
echo "[3] review-agent.md citation + green_proof + matrix"
if [[ ! -f "$REVIEW_AGENT" ]]; then
  fail "$REVIEW_AGENT does not exist"
else
  grep -q "_shared/tdd.md" "$REVIEW_AGENT" && pass "tdd.md path cited" || fail "tdd.md path not cited in $REVIEW_AGENT"
  grep -qE "[Bb]efore reviewing.*tdd\.md" "$REVIEW_AGENT" && pass "passive citation phrasing present" || fail "passive citation phrasing missing in $REVIEW_AGENT"
  # green_proof schema 4 fields
  grep -q "green_proof" "$REVIEW_AGENT" && pass "green_proof field declared" || fail "green_proof field missing"
  grep -q "test_command" "$REVIEW_AGENT" && pass "test_command field declared" || fail "test_command field missing"
  grep -q "exit_code" "$REVIEW_AGENT" && pass "exit_code field declared" || fail "exit_code field missing"
  grep -q "output_tail" "$REVIEW_AGENT" && pass "output_tail field declared" || fail "output_tail field missing"
  grep -q "tests_correspondence" "$REVIEW_AGENT" && pass "tests_correspondence field declared" || fail "tests_correspondence field missing"
  # 5-tier matrix presence (heuristic: needs all 5 tier names + at least one allow-na marker)
  for tier in "direct fix" "advisory" "packaged confirm (quality)" "packaged confirm (correctness)" "needs judgment"; do
    grep -q "$tier" "$REVIEW_AGENT" && pass "tier '$tier' present" || fail "tier '$tier' missing"
  done
  # failure_count exclusion statement
  grep -q "failure_count" "$REVIEW_AGENT" && pass "failure_count exclusion statement present" || fail "failure_count exclusion statement missing"
fi

# ---------------------------------------------------------------------------
# Check 4: execute SKILL.md SWITCH verify rule for green_proof
# ---------------------------------------------------------------------------
echo "[4] execute SKILL.md verify rule"
if [[ ! -f "$EXECUTE_SKILL" ]]; then
  fail "$EXECUTE_SKILL does not exist"
else
  grep -q "green_proof" "$EXECUTE_SKILL" && pass "green_proof referenced in execute SKILL.md" || fail "green_proof not referenced in execute SKILL.md"
  grep -qi "verify.*green_proof\|green_proof.*驗證\|green_proof.*verify" "$EXECUTE_SKILL" && pass "verify rule present" || fail "verify rule missing in execute SKILL.md"
fi

# ---------------------------------------------------------------------------
# Check 5: dogfood fixture exists with mattpocock-violation lures
# ---------------------------------------------------------------------------
echo "[5] dogfood fixture"
if [[ ! -d "$FIXTURE_DIR" ]]; then
  fail "$FIXTURE_DIR does not exist"
else
  pass "$FIXTURE_DIR exists"
  # Fixture is split into prompt.md (model-facing, contains lures only) and
  # acceptance-spec.md (reviewer-only, contains expected behavior + acceptance).
  PROMPT_FILE="$FIXTURE_DIR/prompt.md"
  SPEC_FILE="$FIXTURE_DIR/acceptance-spec.md"
  if [[ ! -f "$PROMPT_FILE" ]]; then
    fail "no prompt.md in $FIXTURE_DIR (model-facing prompt missing)"
  else
    pass "prompt.md: $PROMPT_FILE"
    # Mock internal collaborator lure (must be in prompt, not in spec)
    grep -qi "mock.*XService\|mock.*collaborator\|mock.*內部\|XService.*mock" "$PROMPT_FILE" \
      && pass "mock-internal-collaborator lure present in prompt.md" \
      || fail "mock-internal-collaborator lure missing in $PROMPT_FILE"
    # HOW-style naming lure (must be in prompt)
    grep -qE "test.*calls|calls.*validateInventory|test.*processOrder.*calls|test that.*calls" "$PROMPT_FILE" \
      && pass "HOW-style naming lure present in prompt.md" \
      || fail "HOW-style naming lure missing in $PROMPT_FILE"
    # Anti-leak: prompt.md must NOT contain the answers (期待行為 / acceptance)
    if grep -qE "期待.*mattpocock-aligned|不該 mock|test_processOrder_returns_rejected|REVIEWER-ONLY" "$PROMPT_FILE"; then
      fail "prompt.md leaks answer keywords (should be in acceptance-spec.md only)"
    else
      pass "prompt.md does not leak answer keywords"
    fi
  fi
  if [[ ! -f "$SPEC_FILE" ]]; then
    fail "no acceptance-spec.md in $FIXTURE_DIR (reviewer-only spec missing)"
  else
    pass "acceptance-spec.md: $SPEC_FILE"
    grep -qi "REVIEWER-ONLY\|DO NOT PASTE" "$SPEC_FILE" \
      && pass "spec marked reviewer-only (anti-paste warning present)" \
      || fail "acceptance-spec.md missing reviewer-only / DO-NOT-PASTE warning"
  fi
  # Acceptance check script (mandatory)
  if [[ -f "$FIXTURE_DIR/check_acceptance.sh" ]]; then
    pass "acceptance check script: $FIXTURE_DIR/check_acceptance.sh"
  else
    fail "acceptance check script missing"
  fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo
if (( fail_count == 0 )); then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "FAIL: $fail_count check(s) failed"
  exit 1
fi
