#!/usr/bin/env bash
# Tests for TASK-automation-02: dual-mode orchestration interface references
# for review / execute / learn (REQ-004 Scenario 3 / 4).
#
# Asserts (structural, behavior-level checks stay with spec review):
#   T1  references/orchestration-interface.md exists for each of the 3 skills
#   T2  depth-invariant sentence appears >= 2 times per reference file
#       (once in the current-adapter section, once in the Workflow adapter)
#   T3  each SKILL.md links the reference file directly (one level deep)
#   T4  the SKILL.md pointer block is <= 10 lines (heading included)
#   T5  execute/SKILL.md Goal-Alignment Filter + failure_count sections are
#       byte-identical to HEAD (pointer insertion must not touch them)

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
for skill in review execute learn; do
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
# T5: execute/SKILL.md guarded sections — zero diff vs HEAD
#     (a) Phase 2 failure_count loop   (b) Goal-Alignment Filter
#     (c) Failure escalation logic (failure_count accounting)
# ---------------------------------------------------------------------------
EXEC_REL="plugins/baransu/skills/execute/SKILL.md"
EXEC_MD="$ROOT/$EXEC_REL"

extract_phase2()  { awk '/^\*\*Phase 2 — Impl\*\*/{found=1} found && /^\*\*Phase 3 — Review\*\*/{exit} found{print}'; }
extract_filter()  { awk '/^\*\*Goal-Alignment Filter\*\*/{found=1} found && /^\*\*Failure escalation logic\*\*/{exit} found{print}'; }
extract_escal()   { awk '/^\*\*Failure escalation logic\*\*/{found=1} found && /^\*\*Composite /{exit} found{print}'; }

if git -C "$ROOT" show "HEAD:$EXEC_REL" > /tmp/exec-head.$$ 2>/dev/null; then
  for section in phase2 filter escal; do
    case "$section" in
      phase2) LABEL="Phase 2 failure_count loop";    EXTRACT=extract_phase2 ;;
      filter) LABEL="Goal-Alignment Filter section"; EXTRACT=extract_filter ;;
      escal)  LABEL="Failure escalation (failure_count) section"; EXTRACT=extract_escal ;;
    esac
    echo "T5[$section]: execute/SKILL.md $LABEL zero diff vs HEAD..."
    HEAD_SEC=$("$EXTRACT" < /tmp/exec-head.$$)
    WORK_SEC=$("$EXTRACT" < "$EXEC_MD")
    if [ -z "$WORK_SEC" ]; then
      fail "T5[$section]: $LABEL not found in working copy of execute/SKILL.md"
    elif [ "$HEAD_SEC" = "$WORK_SEC" ]; then
      pass "T5[$section]: $LABEL unchanged"
    else
      fail "T5[$section]: $LABEL differs from HEAD" \
           "Pointer-section insertion must not touch this section"
    fi
  done
  rm -f /tmp/exec-head.$$
else
  fail "T5: cannot read $EXEC_REL from git HEAD"
fi

# ---------------------------------------------------------------------------
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
  printf 'Failed: %s\n' "${FAILED_TESTS[@]}"
  exit 1
fi
exit 0
