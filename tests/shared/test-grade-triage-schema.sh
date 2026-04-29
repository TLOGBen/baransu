#!/usr/bin/env bash
# Structural test for plugins/baransu/skills/_shared/grade-triage-schema.md
# Asserts:
#   1) file exists
#   2) 5 baransu-native dim names appear in the doc
#   3) equal-weight literal (1/5 or 0.2 or "equal weight") appears
#   4) tune-trigger threshold (>= 50 or ≥ 50) appears
#   5) quality enum 4 values appear (excellent / good / acceptable / poor)
#   6) escalate enum 3 values appear (false / requires_human / daily_quota_exceeded)
#   7) every fenced ```json block in the doc is jq-parseable; at least 2 blocks present
#      (one grade.jsonl row + one triage.jsonl row)
#
# Exit 0 on full pass; non-zero (and prints reason) on any failure.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DOC="$WORKTREE_ROOT/plugins/baransu/skills/_shared/grade-triage-schema.md"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

# (1) file exists
[ -f "$DOC" ] || fail "schema doc not found: $DOC"

# (2) 5 baransu-native dim names
DIM_NAMES=(
  "outcome_quality"
  "iteration_velocity"
  "scope_blast"
  "human_override_rate"
  "failure_recurrence"
)
for d in "${DIM_NAMES[@]}"; do
  grep -q "$d" "$DOC" || fail "missing dim name: $d"
done

# (3) equal-weight literal (any of 1/5, 0.2, or "equal weight" — case-insensitive)
if ! grep -Eq '1/5|0\.2|[Ee]qual[ -]?[Ww]eight' "$DOC"; then
  fail "missing equal-weight literal (1/5 or 0.2 or 'equal weight')"
fi

# (4) tune-trigger threshold (≥ 50 or >= 50)
if ! grep -Eq '≥[[:space:]]*50|>=[[:space:]]*50' "$DOC"; then
  fail "missing tune-trigger threshold (≥ 50 or >= 50)"
fi

# (5) quality enum 4 values
for q in excellent good acceptable poor; do
  grep -q "$q" "$DOC" || fail "missing quality enum value: $q"
done

# (6) escalate enum 3 values
for e in "false" "requires_human" "daily_quota_exceeded"; do
  grep -q "$e" "$DOC" || fail "missing escalate enum value: $e"
done

# (7) every fenced ```json block is jq-parseable; at least 2 blocks present
if ! command -v jq >/dev/null 2>&1; then
  fail "jq not installed; cannot validate JSON examples"
fi

# Extract all fenced ```json blocks into a tab-delimited stream
# (one block per line, with literal-newline characters replaced by space —
# JSONL rows are single-line so this is fine)
BLOCK_COUNT=0
while IFS= read -r BLOCK; do
  [ -n "$BLOCK" ] || continue
  BLOCK_COUNT=$((BLOCK_COUNT + 1))
  echo "$BLOCK" | jq . >/dev/null 2>&1 \
    || fail "fenced \`\`\`json block #$BLOCK_COUNT is not valid JSON: $BLOCK"
done < <(awk '
  /^```json$/ { in_block=1; buf=""; next }
  /^```$/ {
    if (in_block) {
      print buf
      in_block=0
      buf=""
    }
    next
  }
  in_block {
    if (buf == "") { buf = $0 } else { buf = buf " " $0 }
  }
' "$DOC")

if [ "$BLOCK_COUNT" -lt 2 ]; then
  fail "expected at least 2 fenced \`\`\`json blocks (grade + triage examples); found $BLOCK_COUNT"
fi

echo "PASS: grade-triage-schema.md structural checks (file + 5 dims + equal-weight + ≥50 + quality enum + escalate enum + $BLOCK_COUNT jq-parseable JSON blocks)"
exit 0
