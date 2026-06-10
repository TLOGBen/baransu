#!/usr/bin/env bash
# Test suite for TASK-distribution-01: release metadata reflects 12 skills @ 2.0.0.
#
# Asserts (behavioral, against release surfaces only):
#   D1) plugin.json version == 2.0.0
#   D2) plugin.json description describes twelve skills (no "16"/"sixteen")
#   D3) plugin.json keywords contain none of: dev, tdd, harness, grade, triage, bridge
#   D4) marketplace.json plugin description synced (no "16"/"sixteen");
#       metadata.version identical to plugin.json version
#   D5) marketplace.json tags contain none of: dev, tdd, harness, grade, triage, bridge
#   D6) CLAUDE.md has no "sixteen" / "self-healing harness" wording
#   D7) CLAUDE.md skills table has exactly 12 rows; no /dev /grade /triage /bridge rows
#   D8) CLAUDE.md keeps the cross-skill anti-patterns pointer (rules/anti-patterns.md)
#   D9) README has no functional reference to removed skills
#       (word-boundary scan: \bgrade\b|\btriage\b|\bbridge\b|`/dev`|baransu:dev)
#   D10) release-notes-draft.md exists with the three mandated sections:
#        16→12 list + settings.json hook-removal instruction,
#        gate-semantics downgrade (discipline-suggested),
#        new governance assets (loop-contract.md, anti-patterns.md, verify-skills.py)
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLUGIN_JSON="$WORKTREE_ROOT/plugins/baransu/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$WORKTREE_ROOT/.claude-plugin/marketplace.json"
CLAUDE_MD="$WORKTREE_ROOT/CLAUDE.md"
README_MD="$WORKTREE_ROOT/README.md"
RELEASE_NOTES="$WORKTREE_ROOT/.claude/execute/2026-06-10-baransu-v2-slim/execute/release-notes-draft.md"

PASS_COUNT=0
FAIL_COUNT=0

ok() {
  echo "PASS: $*"
  PASS_COUNT=$((PASS_COUNT + 1))
}

bad() {
  echo "FAIL: $*" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

BANNED_TERMS="dev tdd harness grade triage bridge"

# --- D1: plugin.json version ---
PLUGIN_VERSION=$(python3 -c "import json;print(json.load(open('$PLUGIN_JSON'))['version'])" 2>/dev/null)
if [ "$PLUGIN_VERSION" = "2.0.0" ]; then
  ok "D1 plugin.json version is 2.0.0"
else
  bad "D1 plugin.json version is '$PLUGIN_VERSION', expected 2.0.0"
fi

# --- D2: plugin.json description ---
PLUGIN_DESC=$(python3 -c "import json;print(json.load(open('$PLUGIN_JSON'))['description'])" 2>/dev/null)
if echo "$PLUGIN_DESC" | grep -qiE '\b16\b|sixteen'; then
  bad "D2 plugin.json description still says 16/sixteen: $PLUGIN_DESC"
elif echo "$PLUGIN_DESC" | grep -qiE '\b12\b|twelve'; then
  ok "D2 plugin.json description describes twelve skills"
else
  bad "D2 plugin.json description does not mention twelve/12: $PLUGIN_DESC"
fi

# --- D3: plugin.json keywords ---
PLUGIN_KW=$(python3 -c "import json;print('\n'.join(json.load(open('$PLUGIN_JSON'))['keywords']))" 2>/dev/null)
D3_OK=1
for term in $BANNED_TERMS; do
  if echo "$PLUGIN_KW" | grep -qxF "$term"; then
    bad "D3 plugin.json keywords still contain '$term'"
    D3_OK=0
  fi
done
[ "$D3_OK" = "1" ] && ok "D3 plugin.json keywords clean of removed-asset terms"

# --- D4: marketplace.json description + version sync ---
MKT_DESC=$(python3 -c "import json;print(json.load(open('$MARKETPLACE_JSON'))['plugins'][0]['description'])" 2>/dev/null)
MKT_VERSION=$(python3 -c "import json;print(json.load(open('$MARKETPLACE_JSON'))['metadata']['version'])" 2>/dev/null)
if echo "$MKT_DESC" | grep -qiE '\b16\b|sixteen'; then
  bad "D4 marketplace.json plugin description still says 16/sixteen: $MKT_DESC"
elif [ "$MKT_VERSION" != "$PLUGIN_VERSION" ] || [ -z "$MKT_VERSION" ]; then
  bad "D4 marketplace.json metadata.version '$MKT_VERSION' != plugin.json version '$PLUGIN_VERSION'"
else
  ok "D4 marketplace.json description synced; version matches plugin.json"
fi

# --- D5: marketplace.json tags ---
MKT_TAGS=$(python3 -c "import json;print('\n'.join(json.load(open('$MARKETPLACE_JSON'))['plugins'][0]['tags']))" 2>/dev/null)
D5_OK=1
for term in $BANNED_TERMS; do
  if echo "$MKT_TAGS" | grep -qxF "$term"; then
    bad "D5 marketplace.json tags still contain '$term'"
    D5_OK=0
  fi
done
[ "$D5_OK" = "1" ] && ok "D5 marketplace.json tags clean of removed-asset terms"

# --- D6: CLAUDE.md harness wording ---
if grep -qiE 'sixteen|self-healing harness' "$CLAUDE_MD"; then
  bad "D6 CLAUDE.md still contains 'sixteen' or 'self-healing harness'"
else
  ok "D6 CLAUDE.md harness/sixteen wording removed"
fi

# --- D7: CLAUDE.md skills table ---
ROW_COUNT=$(grep -cE '^\| `/' "$CLAUDE_MD")
if [ "$ROW_COUNT" -eq 12 ]; then
  ok "D7a CLAUDE.md skills table has 12 rows"
else
  bad "D7a CLAUDE.md skills table has $ROW_COUNT rows, expected 12"
fi
if grep -E '^\| `/' "$CLAUDE_MD" | grep -qE '`/(dev|grade|triage|bridge)`'; then
  bad "D7b CLAUDE.md skills table still has /dev, /grade, /triage, or /bridge row"
else
  ok "D7b CLAUDE.md skills table has no removed-skill rows"
fi

# --- D8: anti-patterns pointer preserved ---
if grep -q 'rules/anti-patterns.md' "$CLAUDE_MD"; then
  ok "D8 CLAUDE.md keeps the anti-patterns pointer line"
else
  bad "D8 CLAUDE.md lost the rules/anti-patterns.md pointer line"
fi

# --- D9: README residue (word-boundary; homograph-safe) ---
README_HITS=$(grep -nE '\bgrade\b|\btriage\b|\bbridge\b|`/dev`|baransu:dev|\.claude/dev/' "$README_MD" || true)
if [ -n "$README_HITS" ]; then
  bad "D9 README still references removed assets:"$'\n'"$README_HITS"
else
  ok "D9 README clean of removed-asset references"
fi

# --- D10: release notes draft ---
if [ ! -f "$RELEASE_NOTES" ]; then
  bad "D10 release-notes-draft.md missing at $RELEASE_NOTES"
else
  D10_OK=1
  for needle in "settings.json" "discipline-suggested" "loop-contract.md" "anti-patterns.md" "verify-skills.py" "tdd.md"; do
    if ! grep -qF "$needle" "$RELEASE_NOTES"; then
      bad "D10 release-notes-draft.md missing required content: $needle"
      D10_OK=0
    fi
  done
  if ! grep -qE '16.*12|sixteen.*twelve' "$RELEASE_NOTES"; then
    bad "D10 release-notes-draft.md missing the 16→12 statement"
    D10_OK=0
  fi
  [ "$D10_OK" = "1" ] && ok "D10 release-notes-draft.md present with all three mandated sections"
fi

echo ""
echo "=== test-distribution-metadata: $PASS_COUNT passed, $FAIL_COUNT failed ==="
[ "$FAIL_COUNT" -eq 0 ] || exit 1
exit 0
