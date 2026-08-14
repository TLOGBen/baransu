#!/usr/bin/env bash
# Tests for TASK-automation-02: dual-mode orchestration interface references
# for review / learn / evolve (REQ-004 Scenario 3 / 4).
#
# Asserts (structural, behavior-level checks stay with spec review):
#   T1  references/orchestration-interface.md exists for each of the 3 skills
#   T2  depth-invariant sentence appears >= 2 times per reference file
#       (once in the current-adapter section, once in the Workflow adapter)
#   T3  each SKILL.md links the reference file directly (one level deep)
#   T4  the SKILL.md pointer block is <= 10 lines (heading included)
#
# T5 (guarded zero-diff-vs-HEAD checks on the retired execution pipeline's
# Phase 1 failure_count loop, Goal-Alignment Filter, and failure-escalation
# sections) was retired in v4.0.0: the large-band pipeline skill and both
# guarded reference files were deleted, so the sections it protected no longer
# exist. That same skill also leaves the T1-T4 loop, which now covers the
# three surviving orchestration-interface holders.

set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILLS_DIR="$ROOT/plugins/baransu/skills"

DEPTH_SENTENCE="agents must not invoke skills or dispatch further subagents"

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
# T1 + T2 + T3 + T4 per skill
# ---------------------------------------------------------------------------
for skill in review learn evolve; do
  REF="$SKILLS_DIR/$skill/references/orchestration-interface.md"
  SKILL_MD="$SKILLS_DIR/$skill/SKILL.md"

  echo "T1[$skill]: references/orchestration-interface.md exists..."
  if [ -f "$REF" ]; then
    pass "T1[$skill]: reference file exists"
  else
    fail "T1[$skill]: $REF is missing"
    continue
  fi

  echo "T2[$skill]: depth-invariant sentence appears >= 2 times..."
  COUNT=$(grep -c "$DEPTH_SENTENCE" "$REF" 2>/dev/null || echo 0)
  if [ "$COUNT" -ge 2 ]; then
    pass "T2[$skill]: depth sentence count = $COUNT (>= 2)"
  else
    fail "T2[$skill]: depth sentence count = $COUNT (expected >= 2)" \
         "Sentence: '$DEPTH_SENTENCE' must appear in BOTH adapter sections"
  fi

  echo "T3[$skill]: SKILL.md links references/orchestration-interface.md..."
  if grep -q "references/orchestration-interface.md" "$SKILL_MD"; then
    pass "T3[$skill]: SKILL.md pointer link present"
  else
    fail "T3[$skill]: SKILL.md has no link to references/orchestration-interface.md"
  fi

  echo "T4[$skill]: pointer block in SKILL.md is <= 10 lines..."
  BLOCK=$(awk '/^#+ Orchestration [Ii]nterface/{found=1; print; next}
               found && (/^#/ || /^---/){exit}
               found{print}' "$SKILL_MD")
  if [ -z "$BLOCK" ]; then
    fail "T4[$skill]: no 'Orchestration Interface' heading block found in SKILL.md"
  else
    LINES=$(printf '%s\n' "$BLOCK" | wc -l)
    if [ "$LINES" -le 10 ]; then
      pass "T4[$skill]: pointer block = $LINES lines (<= 10)"
    else
      fail "T4[$skill]: pointer block = $LINES lines (> 10)"
    fi
  fi
done

# ---------------------------------------------------------------------------
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
  printf 'Failed: %s\n' "${FAILED_TESTS[@]}"
  exit 1
fi
exit 0
