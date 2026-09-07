#!/usr/bin/env bash
# Tests for plugins/baransu/skills/book/SKILL.md Stage 0 (format flag parsing)
# Coverage (TASK-skill-01 retry): invalid --format guard must be present in Stage 0
#
# Strategy: extract the "## Stage 0" section (up to the next H2) and check its
# content. The guard lives in Stage 0 §2 「--format 旗標解析」; the old anchor
# "### 0." now matches Stage 2A's Fact-Verification block instead, and the old
# absolute path broke under worktrees — both fixed here (v2.1.0 doc-debt).

set -u

SKILL_MD="$(cd "$(dirname "$0")/../.." && pwd)/plugins/baransu/skills/book/SKILL.md"

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

# Extract the Stage 0 section: from "## Stage 0" up to (but not including) the next "## " heading
SECTION_0=$(awk '/^## Stage 0/{found=1; print; next} found && /^## /{exit} found{print}' "$SKILL_MD")

echo "--- Extracted §0 block ---"
echo "$SECTION_0"
echo "--------------------------"

# ---------------------------------------------------------------------------
# T1: §0 contains text about invalid --format values
# Must mention "不合法" (illegal) or equivalent wording
# ---------------------------------------------------------------------------
echo "T1: Stage 0 §0 contains invalid --format guard text (不合法 or similar)..."
if echo "$SECTION_0" | grep -qE "不合法|invalid.*format|format.*invalid|非法"; then
  pass "T1: §0 contains invalid --format guard (不合法/invalid)"
else
  fail "T1: §0 is MISSING the invalid --format guard" \
       "Expected text about invalid format values (e.g. '不合法') in §0 specifically"
fi

# ---------------------------------------------------------------------------
# T2: §0 invalid-format guard mentions stopping before install-deps.ts
# Must specifically mention stopping, not calling install-deps.ts, or exit
# ---------------------------------------------------------------------------
echo "T2: Stage 0 §0 invalid-format guard mentions stopping before install-deps.ts..."
if echo "$SECTION_0" | grep -qE "停止|不呼叫.*install-deps|install-deps.*不呼叫|exit"; then
  pass "T2: §0 invalid-format guard mentions stopping"
else
  fail "T2: §0 invalid-format guard does not mention stopping" \
       "Expected 停止/不呼叫 install-deps/exit in §0"
fi

# ---------------------------------------------------------------------------
# T3: §0 still lists supported values: html, pdf, ppt, all
# (Existing checklist item must survive the edit)
# ---------------------------------------------------------------------------
echo "T3: Stage 0 §0 still lists supported values html/pdf/ppt/all..."
if echo "$SECTION_0" | grep -qE "html.*pdf.*ppt.*all|html \| pdf \| ppt \| all"; then
  pass "T3: §0 still lists html/pdf/ppt/all"
else
  fail "T3: §0 is missing supported values list" \
       "Expected 'html | pdf | ppt | all' in §0"
fi

# ---------------------------------------------------------------------------
# T4: §0 still has the default = html line
# (Existing checklist item must survive the edit)
# ---------------------------------------------------------------------------
echo "T4: Stage 0 §0 still has default=html..."
if echo "$SECTION_0" | grep -qE "預設.*html|default.*html|html.*預設"; then
  pass "T4: §0 still has default=html"
else
  fail "T4: §0 is missing default=html" \
       "Expected default html specification in §0"
fi

# ---------------------------------------------------------------------------
# T5: §0 still sets \$FORMAT variable
# (Existing checklist item must survive the edit)
# ---------------------------------------------------------------------------
echo "T5: Stage 0 §0 still sets \$FORMAT..."
if echo "$SECTION_0" | grep -qE '\$FORMAT'; then
  pass "T5: §0 still sets \$FORMAT"
else
  fail "T5: §0 is missing \$FORMAT setting" \
       "Expected \$FORMAT assignment in §0"
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
