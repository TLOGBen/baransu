#!/usr/bin/env bash
# test_tdd_trigger.sh — structural verification for the TDD trigger record
# (pruned twice: the v2 slim-down removed /dev; v4.0.0 retired the /analyze
#  execution pipeline, so impl-agent / review-agent / execution-pipeline.md
#  are gone. The surviving trigger points are the /think small-task reroute
#  and the /hunt fix reroute, both of which land in the main session under
#  _shared/tdd.md §7.)
#
# Greps that the surviving deliverables are in place. Each check is
# deterministic; first failure prints reason and exits 1.
#
# CLI: test_tdd_trigger.sh
# Exit codes:
#   0 — all checks pass (TDD reference content + §8 trigger-point citations
#       + reciprocal citation in each triggering SKILL.md + fixture present)
#   1 — at least one check failed; stdout names the failing check

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  echo "FAIL: not in a git repo" >&2
  exit 1
fi
cd "$REPO_ROOT"

TDD_REF="plugins/baransu/skills/_shared/tdd.md"
THINK_SKILL="plugins/baransu/skills/think/SKILL.md"
HUNT_SKILL="plugins/baransu/skills/hunt/SKILL.md"
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
  grep -q "skills/think/SKILL.md" "$TDD_REF" && pass "§8 cites think/SKILL.md" || fail "§8 missing think/SKILL.md citation"
  grep -q "skills/hunt/SKILL.md" "$TDD_REF" && pass "§8 cites hunt/SKILL.md" || fail "§8 missing hunt/SKILL.md citation"
fi

# ---------------------------------------------------------------------------
# Check 2: reciprocal citation — each §8 trigger point actually reroutes to
# _shared/tdd.md. A one-way §8 row would be a dangling claim.
# (Checks 3 and 4 covered review-agent.md's green_proof schema / 5-tier matrix
#  and the execution pipeline's green_proof verify rule; both surfaces were
#  deleted with the /analyze pipeline in v4.0.0 and are not replaced.)
# ---------------------------------------------------------------------------
echo "[2] reciprocal tdd.md reroute in the triggering skills"
for skill_md in "$THINK_SKILL" "$HUNT_SKILL"; do
  if [[ ! -f "$skill_md" ]]; then
    fail "$skill_md does not exist"
  else
    grep -q "_shared/tdd.md" "$skill_md" && pass "$skill_md cites _shared/tdd.md" || fail "$skill_md does not cite _shared/tdd.md"
  fi
done

# ---------------------------------------------------------------------------
# Check 3: dogfood fixture exists with mattpocock-violation lures
# ---------------------------------------------------------------------------
echo "[3] dogfood fixture"
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
