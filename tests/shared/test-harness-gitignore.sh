#!/usr/bin/env bash
# Structural test for TASK-shared-03: .claude/harness/ gitignore + directory.
# Asserts:
#   1) .gitignore contains a rule matching `.claude/harness/`
#   2) the comment "self-healing harness telemetry — local only" appears
#      within ±2 lines of that rule
#   3) `.claude/harness/` directory exists
#   4) probing `.claude/harness/probe.jsonl` does NOT show as untracked
#      in `git status --porcelain`
#
# Exit 0 on full pass; non-zero (and prints reason) on any failure.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GITIGNORE="$WORKTREE_ROOT/.gitignore"
HARNESS_DIR="$WORKTREE_ROOT/.claude/harness"
PROBE="$HARNESS_DIR/probe.jsonl"
COMMENT_TEXT="self-healing harness telemetry — local only"
RULE_PATTERN='\.claude/harness/'

fail() {
  echo "FAIL: $*" >&2
  # best-effort cleanup if probe was created before the failure
  [ -e "$PROBE" ] && rm -f "$PROBE"
  exit 1
}

# (1) .gitignore contains the rule
[ -f "$GITIGNORE" ] || fail ".gitignore not found at $GITIGNORE"
if ! grep -nE "$RULE_PATTERN" "$GITIGNORE" >/dev/null; then
  fail ".gitignore does not contain a rule matching .claude/harness/"
fi

# (2) comment within ±2 lines of the rule
if ! grep -B 2 -A 2 -E "$RULE_PATTERN" "$GITIGNORE" \
    | grep -F -- "$COMMENT_TEXT" >/dev/null; then
  fail "expected comment '$COMMENT_TEXT' within ±2 lines of the .claude/harness/ rule"
fi

# (3) directory exists
[ -d "$HARNESS_DIR" ] || fail "directory not found: $HARNESS_DIR"

# (4) probe file is ignored by git
touch "$PROBE" || fail "could not create probe file at $PROBE"
STATUS_OUT="$(git -C "$WORKTREE_ROOT" status --porcelain -- "$PROBE" 2>/dev/null || true)"
if [ -n "$STATUS_OUT" ]; then
  rm -f "$PROBE"
  fail "git status lists probe as untracked/modified: $STATUS_OUT"
fi
rm -f "$PROBE"

echo "PASS: harness gitignore + directory checks (4/4)"
exit 0
