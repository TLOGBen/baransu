#!/usr/bin/env bash
# Test suite for TASK-hooks-04: hook registration in user-level
# ~/.claude/settings.json + plugin.json invariant (INV-1).
#
# Asserts (7 checks):
#   1) ~/.claude/settings.json exists.
#   2) jq '.hooks' returns a non-empty object.
#   3) UserPromptSubmit hook command path contains user-prompt-submit.py.
#   4) PostToolUse hook command path contains post-tool-use.py.
#   5) Stop hook command path contains stop.py.
#   6) INV-1: plugins/baransu/.claude-plugin/plugin.json contains no "hooks" field.
#   7) A timestamped backup ~/.claude/settings.json.bak.* exists.
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SETTINGS="$HOME/.claude/settings.json"
PLUGIN_JSON="$WORKTREE_ROOT/plugins/baransu/.claude-plugin/plugin.json"

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

command -v jq >/dev/null 2>&1 || { echo "FAIL: jq not installed" >&2; exit 1; }

# -------------------------------------------------------------------------
# A1: settings.json exists
# -------------------------------------------------------------------------
if [ -f "$SETTINGS" ]; then
  ok "A1 settings.json exists at $SETTINGS"
else
  bad "A1 settings.json missing at $SETTINGS"
fi

# -------------------------------------------------------------------------
# A2: .hooks is a non-empty object
# -------------------------------------------------------------------------
if [ -f "$SETTINGS" ]; then
  if jq -e '(.hooks // {}) | type == "object" and (length > 0)' "$SETTINGS" >/dev/null 2>&1; then
    ok "A2 settings.json .hooks is a non-empty object"
  else
    bad "A2 settings.json .hooks is missing or empty"
  fi
else
  bad "A2 skipped (settings.json missing)"
fi

# -------------------------------------------------------------------------
# A3: UserPromptSubmit -> ...user-prompt-submit.py
# -------------------------------------------------------------------------
if [ -f "$SETTINGS" ]; then
  if jq -r '.hooks.UserPromptSubmit[]?.hooks[]?.command // empty' "$SETTINGS" \
       | grep -qF 'user-prompt-submit.py'; then
    ok "A3 UserPromptSubmit -> user-prompt-submit.py registered"
  else
    bad "A3 UserPromptSubmit hook missing or path lacks user-prompt-submit.py"
  fi
else
  bad "A3 skipped (settings.json missing)"
fi

# -------------------------------------------------------------------------
# A4: PostToolUse -> ...post-tool-use.py
# -------------------------------------------------------------------------
if [ -f "$SETTINGS" ]; then
  if jq -r '.hooks.PostToolUse[]?.hooks[]?.command // empty' "$SETTINGS" \
       | grep -qF 'post-tool-use.py'; then
    ok "A4 PostToolUse -> post-tool-use.py registered"
  else
    bad "A4 PostToolUse hook missing or path lacks post-tool-use.py"
  fi
else
  bad "A4 skipped (settings.json missing)"
fi

# -------------------------------------------------------------------------
# A5: Stop -> ...stop.py
# -------------------------------------------------------------------------
if [ -f "$SETTINGS" ]; then
  if jq -r '.hooks.Stop[]?.hooks[]?.command // empty' "$SETTINGS" \
       | grep -qF 'stop.py'; then
    ok "A5 Stop -> stop.py registered"
  else
    bad "A5 Stop hook missing or path lacks stop.py"
  fi
else
  bad "A5 skipped (settings.json missing)"
fi

# -------------------------------------------------------------------------
# A6: INV-1 plugin.json must NOT contain "hooks"
# -------------------------------------------------------------------------
if [ -f "$PLUGIN_JSON" ]; then
  if grep -qF '"hooks"' "$PLUGIN_JSON"; then
    bad "A6 INV-1 violated: plugin.json contains \"hooks\" field"
  else
    ok "A6 INV-1 holds: plugin.json has no \"hooks\" field"
  fi
else
  bad "A6 plugin.json not found at $PLUGIN_JSON"
fi

# -------------------------------------------------------------------------
# A7: timestamped backup exists
# -------------------------------------------------------------------------
shopt -s nullglob
BACKUPS=( "$HOME/.claude/settings.json.bak."* )
shopt -u nullglob
if [ "${#BACKUPS[@]}" -gt 0 ]; then
  ok "A7 backup present (${#BACKUPS[@]} file(s); newest: $(basename "${BACKUPS[-1]}"))"
else
  bad "A7 no backup matching ~/.claude/settings.json.bak.*"
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
