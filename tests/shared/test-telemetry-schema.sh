#!/usr/bin/env bash
# Structural test for plugins/baransu/skills/_shared/telemetry-schema.md
# Asserts:
#   1) file exists
#   2) all 7 required field names appear in the doc
#   3) all 3 terminal_state enum values appear in the doc
#   4) the first fenced ```json block in the doc is jq-parseable
#
# Exit 0 on full pass; non-zero (and prints reason) on any failure.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DOC="$WORKTREE_ROOT/plugins/baransu/skills/_shared/telemetry-schema.md"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

# (1) file exists
[ -f "$DOC" ] || fail "schema doc not found: $DOC"

# (2) 7 required fields
REQUIRED_FIELDS=(
  "session_id"
  "terminal_state"
  "prompt_text"
  "skill_outcome"
  "commit_hash"
  "diff_summary_redacted"
  "attempt_history"
)
for f in "${REQUIRED_FIELDS[@]}"; do
  grep -q "$f" "$DOC" || fail "missing required field: $f"
done

# (3) 3 terminal_state enums
for e in completed aborted interrupted; do
  grep -q "$e" "$DOC" || fail "missing terminal_state enum: $e"
done

# (4) extract first fenced ```json block and pipe to jq
JSON_BLOCK="$(awk '
  /^```json$/ { in_block=1; next }
  /^```$/     { if (in_block) exit }
  in_block    { print }
' "$DOC")"

[ -n "$JSON_BLOCK" ] || fail "no fenced \`\`\`json block found in $DOC"

if ! command -v jq >/dev/null 2>&1; then
  fail "jq not installed; cannot validate JSON example"
fi

echo "$JSON_BLOCK" | jq . >/dev/null 2>&1 || fail "fenced \`\`\`json block is not valid JSON"

echo "PASS: telemetry-schema.md structural checks (file + 7 fields + 3 enums + jq example)"
exit 0
