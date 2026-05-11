#!/usr/bin/env bash
# Tests for plugins/baransu/skills/book/scripts/install-deps.ts
# Coverage (TASK-scripts-01): format-aware CLI parameter handling
#
# Test strategy:
# - T1/T2: Invalid --format produces specific validation error BEFORE dependency checks
# - T3: Source code contains --format parsing logic
# - T4: Source code contains success message with format placeholder
# - T5/T6: Source code contains WeasyPrint handling for pdf/all
# - T7/T8: Source code contains playwright/pptxgenjs handling for ppt/all

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
INSTALL_DEPS="$SCRIPT_DIR/plugins/baransu/skills/book/scripts/install-deps.ts"

PASS=0
FAIL=0
FAILED_TESTS=()

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() {
  FAIL=$((FAIL + 1))
  FAILED_TESTS+=("$1")
  echo "  FAIL: $1"
  if [ -n "${2:-}" ]; then echo "        $2"; fi
}

# ---------------------------------------------------------------------------
# T1: Invalid --format must exit non-zero AND produce error BEFORE dep checks
#
# Key behavior: format validation must happen BEFORE markitdown/browser-use checks.
# The invalid-format error must appear in stderr/stdout WITHOUT any mention of
# "markitdown OK" or dep-install output, confirming early exit.
# ---------------------------------------------------------------------------
echo "T1: invalid --format exits non-zero with early format validation error..."
output=$(npx tsx "$INSTALL_DEPS" --format gif 2>&1 || true)
exit_code=0
npx tsx "$INSTALL_DEPS" --format gif >/dev/null 2>&1 && exit_code=0 || exit_code=$?
if [ "$exit_code" -eq 0 ]; then
  fail "T1: --format gif should exit non-zero but exited 0"
else
  # Check that the error is about format (not about markitdown), meaning validation
  # happened before dependency checks. The error must contain the invalid value OR
  # a list of valid values.
  if echo "$output" | grep -qiE "gif|invalid.*format|format.*invalid|valid.*format|html.*pdf.*ppt|pdf.*ppt.*all"; then
    # Check that it did NOT reach dependency check output
    if echo "$output" | grep -q "markitdown OK"; then
      fail "T1: format validation happened AFTER markitdown check (should be before)" "output: $output"
    else
      pass "T1: --format gif exits non-zero with format error before dep checks"
    fi
  else
    fail "T1: error message does not mention format validation" "output: $output"
  fi
fi

# ---------------------------------------------------------------------------
# T2: Invalid --format error message lists valid values (html, pdf, ppt, all)
# ---------------------------------------------------------------------------
echo "T2: invalid --format error message contains all valid format values..."
output=$(npx tsx "$INSTALL_DEPS" --format gif 2>&1 || true)
if echo "$output" | grep -qE "html" && echo "$output" | grep -qE "pdf" && \
   echo "$output" | grep -qE "ppt" && echo "$output" | grep -qE "all"; then
  pass "T2: error message lists html, pdf, ppt, all"
else
  fail "T2: error message does not list all valid formats (html, pdf, ppt, all)" "output: $output"
fi

# ---------------------------------------------------------------------------
# T3: Source contains --format argument parsing
# ---------------------------------------------------------------------------
echo "T3: source contains --format argument parsing..."
if grep -q "\-\-format" "$INSTALL_DEPS"; then
  pass "T3: source contains '--format' argument parsing"
else
  fail "T3: source does NOT contain '--format' argument parsing"
fi

# ---------------------------------------------------------------------------
# T4: Source contains success message with format placeholder
# ---------------------------------------------------------------------------
echo "T4: source contains success message with format placeholder..."
if grep -q "依賴已就緒" "$INSTALL_DEPS" || grep -q "format:" "$INSTALL_DEPS"; then
  pass "T4: source contains success message with format reference"
else
  fail "T4: source does NOT contain success message with format reference"
fi

# ---------------------------------------------------------------------------
# T5: Source contains WeasyPrint handling (for pdf/all)
# ---------------------------------------------------------------------------
echo "T5: source contains WeasyPrint dependency handling..."
if grep -qi "weasyprint" "$INSTALL_DEPS"; then
  pass "T5: source contains WeasyPrint handling"
else
  fail "T5: source does NOT contain WeasyPrint handling"
fi

# ---------------------------------------------------------------------------
# T6: WeasyPrint failure message contains manual install command
# ---------------------------------------------------------------------------
echo "T6: source contains WeasyPrint manual install command (pip install weasyprint)..."
if grep -q "pip install weasyprint" "$INSTALL_DEPS"; then
  pass "T6: source contains 'pip install weasyprint' in error handling"
else
  fail "T6: source does NOT contain 'pip install weasyprint' manual install command"
fi

# ---------------------------------------------------------------------------
# T7: Source contains playwright handling (for ppt/all)
# ---------------------------------------------------------------------------
echo "T7: source contains playwright dependency handling..."
if grep -qi "playwright" "$INSTALL_DEPS"; then
  pass "T7: source contains playwright handling"
else
  fail "T7: source does NOT contain playwright handling"
fi

# ---------------------------------------------------------------------------
# T8: Source contains pptxgenjs handling (for ppt/all)
# ---------------------------------------------------------------------------
echo "T8: source contains pptxgenjs dependency handling..."
if grep -qi "pptxgenjs" "$INSTALL_DEPS"; then
  pass "T8: source contains pptxgenjs handling"
else
  fail "T8: source does NOT contain pptxgenjs handling"
fi

# ---------------------------------------------------------------------------
# T9: Source validates format against allowed list (html|pdf|ppt|all)
# ---------------------------------------------------------------------------
echo "T9: source validates format against allowed list..."
if grep -qE "html.*pdf.*ppt.*all|pdf.*ppt.*html|VALID_FORMATS|validFormats|allowedFormats" "$INSTALL_DEPS"; then
  pass "T9: source contains format allowed-list validation"
else
  fail "T9: source does NOT contain format allowed-list validation"
fi

# ---------------------------------------------------------------------------
# T10: Source has default format = 'html' when flag absent
# ---------------------------------------------------------------------------
echo "T10: source has default format = 'html'..."
if grep -qE "\"html\"|'html'" "$INSTALL_DEPS" && grep -qi "default\|format.*html\|html.*default" "$INSTALL_DEPS"; then
  pass "T10: source contains default format 'html'"
else
  fail "T10: source does NOT appear to set default format to 'html'"
fi

# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
  echo "Failed tests:"
  for t in "${FAILED_TESTS[@]}"; do echo "  - $t"; done
  exit 1
fi
exit 0
