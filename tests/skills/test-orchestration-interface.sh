#!/usr/bin/env bash
# Tests for TASK-automation-02: dual-mode orchestration interface references
# for review / analyze (execution pipeline) / learn / evolve (REQ-004 Scenario 3 / 4).
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
for skill in review analyze learn evolve; do
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
# T5: execution-pipeline guarded sections — zero diff vs HEAD
#     (a) Phase 1 failure_count loop   (b) Goal-Alignment Filter (reference file)
#     (c) Failure escalation logic (failure_count accounting)
#     Bootstrap rule: a guarded file absent from HEAD (first commit after the
#     analyze+execute merge) passes with a bootstrap note; from the next commit
#     on, any drift in these sections fails.
# ---------------------------------------------------------------------------
PIPE_REL="plugins/baransu/skills/analyze/references/execution-pipeline.md"
FILT_REL="plugins/baransu/skills/analyze/references/goal-alignment-filter.md"

extract_phase1()  { awk '/^\*\*Phase 1 — Impl\*\*/{found=1} found && /^\*\*Phase 2 — Review\*\*/{exit} found{print}'; }
extract_filter()  { awk '/^\*\*Goal-Alignment Filter\*\*/{found=1} found{print}'; }
extract_escal()   { awk '/^\*\*Failure escalation\*\*/{found=1} found && /^### 4c/{exit} found{print}'; }

check_guarded() {
  local section="$1" rel="$2" extract="$3" label="$4"
  local work="$ROOT/$rel"
  echo "T5[$section]: $label zero diff vs HEAD..."
  if [ ! -f "$work" ]; then
    fail "T5[$section]: $rel missing from working tree"
    return
  fi
  if git -C "$ROOT" show "HEAD:$rel" > /tmp/guard-head.$$ 2>/dev/null; then
    local head_sec work_sec
    head_sec=$("$extract" < /tmp/guard-head.$$)
    work_sec=$("$extract" < "$work")
    rm -f /tmp/guard-head.$$
    if [ -z "$work_sec" ]; then
      fail "T5[$section]: $label not found in working copy of $rel"
    elif [ "$head_sec" = "$work_sec" ]; then
      pass "T5[$section]: $label unchanged"
    else
      fail "T5[$section]: $label differs from HEAD" \
           "Edits must not touch this guarded section without review"
    fi
  else
    pass "T5[$section]: $rel not in HEAD yet (bootstrap — guarded from next commit)"
  fi
}

check_guarded phase1 "$PIPE_REL" extract_phase1 "Phase 1 failure_count loop"
check_guarded filter "$FILT_REL" extract_filter "Goal-Alignment Filter section"
check_guarded escal  "$PIPE_REL" extract_escal  "Failure escalation (failure_count) section"

# ---------------------------------------------------------------------------
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
  printf 'Failed: %s\n' "${FAILED_TESTS[@]}"
  exit 1
fi
exit 0
