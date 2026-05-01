#!/usr/bin/env bash
# check_acceptance.sh — dogfood acceptance for TDD trigger plan v4
#
# Runs after /baransu:dev produced a test file from this fixture's task.md.
# Greps the test file for mattpocock-violation signals.
#
# CLI: check_acceptance.sh <test_file_path> [<review_report_path>]
# Exit codes:
#   0 — all acceptance criteria met
#   1 — at least one criterion failed
#   2 — structural error (missing input)

set -uo pipefail

if (( $# < 1 )); then
  echo "usage: check_acceptance.sh <test_file_path> [<review_report_path>]" >&2
  exit 2
fi

TEST_FILE="$1"
REVIEW_REPORT="${2:-}"

if [[ ! -f "$TEST_FILE" ]]; then
  echo "FAIL (structural): test file not found: $TEST_FILE" >&2
  exit 2
fi

fail_count=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1" >&2; fail_count=$((fail_count + 1)); }

# ---------------------------------------------------------------------------
# (b1) test name describes behavior, not implementation
# ---------------------------------------------------------------------------
echo "[b1] test name describes behavior"
# Two HOW-style forms to catch:
#   (1) underscore identifier form: def test_X_calls_Y / TestX_Calls_Y
#   (2) sentence form in string literals: it('X calls Y', ...) / test("X uses Y", ...)
# Note: GNU grep does NOT interpret \x27 as 0x27 — must inject a literal ' via
# variable construction so the bracket class actually contains the quote chars.
SQ="'"
how_style_underscore=$(grep -niE '(def test_|test_|func Test)[A-Za-z0-9]*_(calls|uses|invokes)_' "$TEST_FILE" || true)
how_style_sentence_re="(it|test|describe)\s*\(["${SQ}"\"\`][^"${SQ}"\"\`)]*\b(calls|uses|invokes)\b"
how_style_sentence=$(grep -niE "$how_style_sentence_re" "$TEST_FILE" || true)
how_style="$how_style_underscore$how_style_sentence"
if [[ -n "$how_style" ]]; then
  fail "HOW-style test name detected:"
  [[ -n "$how_style_underscore" ]] && echo "$how_style_underscore" | sed 's/^/    [underscore form] /'
  [[ -n "$how_style_sentence" ]]   && echo "$how_style_sentence" | sed 's/^/    [sentence form] /'
else
  pass "no HOW-style test name detected"
fi

# ---------------------------------------------------------------------------
# (b2) test body does not mock internal collaborator (XService)
# ---------------------------------------------------------------------------
echo "[b2] test body does not mock internal collaborator"
# Form A: explicit mock/patch/spy targeting XService by name
mock_internal=$(grep -niE 'mock[^(]*\(.*XService|jest\.mock\([^)]*XService|patch\([^)]*XService|spyOn\([^)]*XService|Mock\(\s*spec\s*=\s*XService' "$TEST_FILE" || true)
if [[ -n "$mock_internal" ]]; then
  fail "XService directly mocked / patched / spied:"
  echo "$mock_internal" | sed 's/^/    /'
else
  pass "XService not directly mocked"
fi

# Form B: class-extension fake (FakeXService extends XService) and lowercase instance spy
class_fake=$(grep -niE 'class\s+[A-Z][A-Za-z0-9]*XService\s+extends\s+XService|spyOn\(\s*[xX]Service\b' "$TEST_FILE" || true)
if [[ -n "$class_fake" ]]; then
  fail "internal collaborator faked via class extension or lowercase spy:"
  echo "$class_fake" | sed 's/^/    /'
else
  pass "no class-extension fake / lowercase spy of XService"
fi

# ---------------------------------------------------------------------------
# (c) review-agent green_proof 4 fields complete (if review report provided)
# ---------------------------------------------------------------------------
echo "[c] green_proof structural completeness"
if [[ -z "$REVIEW_REPORT" ]]; then
  pass "(skipped — no review report provided)"
elif [[ ! -f "$REVIEW_REPORT" ]]; then
  fail "review report not found: $REVIEW_REPORT"
else
  for field in test_command exit_code output_tail tests_correspondence; do
    if grep -q "$field" "$REVIEW_REPORT"; then
      pass "green_proof.$field present in review report"
    else
      fail "green_proof.$field missing from review report"
    fi
  done
  # exit_code must be 0
  if grep -qE 'exit_code["[:space:]:]+0' "$REVIEW_REPORT"; then
    pass "green_proof.exit_code = 0"
  else
    fail "green_proof.exit_code != 0 (or not parseable)"
  fi
  # tests_correspondence must not be "n/a" (this is not cosmetic-only path)
  if grep -qE 'tests_correspondence["[:space:]:]+["\x27]?n/a' "$REVIEW_REPORT"; then
    fail 'tests_correspondence is "n/a" (only cosmetic-only path may use this)'
  else
    pass "tests_correspondence is not n/a"
  fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo
if (( fail_count == 0 )); then
  echo "ALL ACCEPTANCE CRITERIA MET"
  exit 0
else
  echo "FAIL: $fail_count criterion(criteria) failed"
  exit 1
fi
