#!/usr/bin/env bash
# Test suite for the CLAUDE.md Skills table after the v2 slim-down (16 -> 12).
#
# Asserts (4 check groups):
#   B1) Project root CLAUDE.md exists.
#   B2) Skills table contains exactly 12 rows (count of "| `/" lines).
#   B3) Removed skills are absent from the table: /dev, /grade, /triage, /bridge.
#   B4) The 12 surviving skill names are present.
#   B5) Each surviving skill row has a non-empty "When to invoke" description column.
#   B6) The 12 skill descriptions match the baseline
#       (regenerated post-slim and persisted alongside this script).
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CLAUDE_MD="$WORKTREE_ROOT/CLAUDE.md"
BASELINE="$(dirname "$0")/claude-md-skills-baseline.txt"

PASS_COUNT=0
FAIL_COUNT=0
FAIL_DETAILS=""

ok() {
  echo "PASS: $*"
  PASS_COUNT=$((PASS_COUNT + 1))
}

bad() {
  echo "FAIL: $*" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
  FAIL_DETAILS="${FAIL_DETAILS}\n  - $*"
}

# Extract the Skills table block (lines starting with "| `/").
extract_skill_rows() {
  grep -E '^\| `/' "$CLAUDE_MD" || true
}

# -------------------------------------------------------------------------
# B1: CLAUDE.md exists
# -------------------------------------------------------------------------
if [ -f "$CLAUDE_MD" ]; then
  ok "B1 CLAUDE.md exists at $CLAUDE_MD"
else
  bad "B1 CLAUDE.md missing at $CLAUDE_MD"
  echo
  echo "----------------------------------------"
  echo "Tests: $PASS_COUNT/1 passed"
  echo -e "Failures:$FAIL_DETAILS" >&2
  exit 1
fi

# -------------------------------------------------------------------------
# B2: Skills table has 12 rows
# -------------------------------------------------------------------------
ROW_COUNT=$(extract_skill_rows | wc -l | tr -d ' ')
if [ "$ROW_COUNT" -eq 12 ]; then
  ok "B2 Skills table has 12 rows"
else
  bad "B2 Skills table row count is $ROW_COUNT, expected 12"
fi

# -------------------------------------------------------------------------
# B3: removed skills are absent from the table
# -------------------------------------------------------------------------
REMOVED_SKILLS=(dev grade triage bridge)
for s in "${REMOVED_SKILLS[@]}"; do
  if extract_skill_rows | grep -qF "\`/$s\`"; then
    bad "B3 removed skill /$s still present in Skills table"
  else
    ok "B3 removed skill /$s absent from Skills table"
  fi
done

# -------------------------------------------------------------------------
# B4: 12 surviving skill names present
# -------------------------------------------------------------------------
SURVIVING_SKILLS=(think review analyze execute write ship hunt read design learn book codex-skill-transfer)
for s in "${SURVIVING_SKILLS[@]}"; do
  if extract_skill_rows | grep -qF "\`/$s\`"; then
    ok "B4 surviving skill /$s present"
  else
    bad "B4 surviving skill /$s missing from Skills table"
  fi
done

# -------------------------------------------------------------------------
# B5: each surviving skill has a non-empty description column
# -------------------------------------------------------------------------
for s in "${SURVIVING_SKILLS[@]}"; do
  ROW=$(extract_skill_rows | grep -F "\`/$s\`" || true)
  if [ -z "$ROW" ]; then
    bad "B5 row for /$s not found (cannot check description)"
    continue
  fi
  # Row format: | `/name` | description |
  # Extract second column.
  DESC=$(echo "$ROW" | awk -F'|' '{print $3}' | sed 's/^ *//; s/ *$//')
  if [ -n "$DESC" ]; then
    ok "B5 /$s has non-empty description: ${DESC:0:60}..."
  else
    bad "B5 /$s description column is empty"
  fi
done

# -------------------------------------------------------------------------
# B6: 12 skill descriptions match the regenerated baseline
# -------------------------------------------------------------------------
if [ ! -f "$BASELINE" ]; then
  bad "B6 baseline file missing at $BASELINE (cannot verify descriptions)"
else
  BASELINE_ROWS=$(grep -cE '^\| `/' "$BASELINE" | tr -d ' ')
  if [ "$BASELINE_ROWS" -eq 12 ]; then
    ok "B6 baseline has 12 rows"
  else
    bad "B6 baseline row count is $BASELINE_ROWS, expected 12"
  fi
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    SKILL_NAME=$(echo "$line" | awk -F'|' '{print $2}' | sed 's/^ *//; s/ *$//')
    EXPECTED_DESC=$(echo "$line" | awk -F'|' '{print $3}' | sed 's/^ *//; s/ *$//')
    ACTUAL_ROW=$(extract_skill_rows | grep -F "$SKILL_NAME |" || true)
    if [ -z "$ACTUAL_ROW" ]; then
      bad "B6 baseline row for $SKILL_NAME not found in current CLAUDE.md"
      continue
    fi
    ACTUAL_DESC=$(echo "$ACTUAL_ROW" | awk -F'|' '{print $3}' | sed 's/^ *//; s/ *$//')
    if [ "$ACTUAL_DESC" = "$EXPECTED_DESC" ]; then
      ok "B6 $SKILL_NAME description matches baseline"
    else
      bad "B6 $SKILL_NAME description DIFFERS from baseline"
      bad "    expected: $EXPECTED_DESC"
      bad "    actual:   $ACTUAL_DESC"
    fi
  done < "$BASELINE"
fi

# -------------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------------
TOTAL=$((PASS_COUNT + FAIL_COUNT))
echo
echo "----------------------------------------"
echo "Tests: $PASS_COUNT/$TOTAL passed"
if [ $FAIL_COUNT -gt 0 ]; then
  echo -e "Failures:$FAIL_DETAILS" >&2
  exit 1
fi
exit 0
