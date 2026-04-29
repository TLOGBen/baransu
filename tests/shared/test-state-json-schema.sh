#!/usr/bin/env bash
# Structural test for plugins/baransu/skills/_shared/state-json-schema.md
# + initial .claude/harness/state.json
# Asserts:
#   1) schema doc exists
#   2) doc names all 4 required fields
#      (daily_push_count / daily_push_date / last_grade_run_at / last_triage_run_at)
#   3) doc explicitly mentions daily quota = 5 (KD#5)
#   4) doc describes daily reset (daily_push_date != today -> counter resets to 0)
#   5) .claude/harness/state.json exists and is valid JSON (jq parseable)
#   6) initial state.json: daily_push_count == 0
#      AND daily_push_date == today's date (YYYY-MM-DD)
#   7) §4 partition contract anchors present:
#        - 'grade owns' literal
#        - 'triage owns' literal
#        - '跨 partition' literal (cross-partition prohibition)
#        - 'read-merge-write' literal
#   8) writer attribution corrected:
#        - 'auto-fix investigator subagent' count == 0 in schema doc
#        - '/triage 自動修補子流程' literal present
#
# Exit 0 on full pass; non-zero (and prints reason) on any failure.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DOC="$WORKTREE_ROOT/plugins/baransu/skills/_shared/state-json-schema.md"
STATE_JSON="$WORKTREE_ROOT/.claude/harness/state.json"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

# (1) schema doc exists
[ -f "$DOC" ] || fail "schema doc not found: $DOC"

# (2) all 4 required field names appear
REQUIRED_FIELDS=(
  "daily_push_count"
  "daily_push_date"
  "last_grade_run_at"
  "last_triage_run_at"
)
for f in "${REQUIRED_FIELDS[@]}"; do
  grep -q "$f" "$DOC" || fail "missing required field: $f"
done

# (3) daily quota = 5 literal
# Accept any of: "quota = 5", "quota=5", "daily_push.*5", or "daily quota.*5"
if ! grep -Eq 'quota[[:space:]]*=[[:space:]]*5|daily[[:space:]_]*push[^[:space:]]*[^a-zA-Z]+5|daily[[:space:]]*quota[^a-zA-Z0-9]+.*5' "$DOC"; then
  fail "missing daily quota = 5 literal (expected one of: 'quota = 5', 'daily_push... 5', 'daily quota ... 5')"
fi

# (4) daily reset clause: daily_push_date != today -> counter reset to 0
# Look for the reset semantics: presence of a clause that mentions
# both "reset" (or 重設) and the inequality "!= today" (or "≠ today" / "不同" + today)
if ! grep -Eq 'reset|重設|重置' "$DOC"; then
  fail "missing daily reset keyword (reset / 重設 / 重置)"
fi
if ! grep -Eq '≠[[:space:]]*(today|今日)|!=[[:space:]]*(today|今日)|not[[:space:]]+(equal|match).*today|不等於.*今日|不同.*今日' "$DOC"; then
  fail "missing daily reset condition (daily_push_date ≠ today)"
fi

# (5) state.json exists and is valid JSON
[ -f "$STATE_JSON" ] || fail "initial state.json not found: $STATE_JSON"
if ! command -v jq >/dev/null 2>&1; then
  fail "jq not installed; cannot validate state.json"
fi
jq -e . "$STATE_JSON" >/dev/null 2>&1 || fail "state.json is not valid JSON: $STATE_JSON"

# (6) initial state.json: daily_push_count == 0 AND daily_push_date == today
COUNT="$(jq -r '.daily_push_count' "$STATE_JSON")"
DATE="$(jq -r '.daily_push_date' "$STATE_JSON")"
TODAY="$(date +%Y-%m-%d)"

[ "$COUNT" = "0" ] || fail "initial state.json daily_push_count must be 0; got: $COUNT"
[ "$DATE" = "$TODAY" ] || fail "initial state.json daily_push_date must be today ($TODAY); got: $DATE"

# (7) §4 partition contract anchors
# These four literal anchors document the new partition contract:
#   - grade owns / triage owns: the partition table headers/rows
#   - 跨 partition: cross-partition write prohibition clause
#   - read-merge-write: writer atomic contract (read full -> modify own -> rename)
grep -q 'grade owns' "$DOC" || fail "schema §4 missing 'grade owns' partition anchor"
grep -q 'triage owns' "$DOC" || fail "schema §4 missing 'triage owns' partition anchor"
grep -q '跨 partition' "$DOC" || fail "schema §4 missing '跨 partition' (cross-partition prohibition) anchor"
grep -q 'read-merge-write' "$DOC" || fail "schema §4 missing 'read-merge-write' atomic contract anchor"

# (8) writer attribution correction (REQ-006 Scenario 2 + KD#1 alignment)
# The triage-partition fields must NOT credit the read-only investigator
# subagent as their writer; the new attribution names the /triage auto-fix
# sub-flow running inside an isolated worktree.
WRONG_WRITER_HITS="$(grep -c 'auto-fix investigator subagent' "$DOC" || true)"
[ "$WRONG_WRITER_HITS" = "0" ] || fail "schema doc must not contain 'auto-fix investigator subagent' (KD#1 read-only invariant); hits=$WRONG_WRITER_HITS"
grep -q '/triage 自動修補子流程' "$DOC" || fail "schema doc missing '/triage 自動修補子流程' writer attribution literal"

echo "PASS: state-json-schema.md + state.json structural checks (doc 4 fields + quota=5 + reset clause + valid JSON + counter=0 + date=$TODAY + partition anchors + writer attribution)"
exit 0
