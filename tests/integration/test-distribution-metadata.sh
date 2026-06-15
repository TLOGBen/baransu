#!/usr/bin/env bash
# Test suite for TASK-distribution-01: release metadata reflects 13 skills @ 2.1.0.
#
# Asserts (behavioral, against release surfaces only):
#   D1) plugin.json version is semver with major >= 2 (not pinned to a string)
#   D2) plugin.json description describes fourteen skills (no "16"/"sixteen")
#   D3) plugin.json keywords contain none of: dev, tdd, harness, grade, triage, bridge
#   D4) marketplace.json plugin description synced (no "16"/"sixteen");
#       metadata.version identical to plugin.json version
#   D5) marketplace.json tags contain none of: dev, tdd, harness, grade, triage, bridge
#   D6) CLAUDE.md has no "sixteen" / "self-healing harness" wording
#   D7) CLAUDE.md skills table has exactly 13 rows; no removed-skill rows
#   D8) CLAUDE.md keeps the cross-skill anti-patterns pointer (rules/anti-patterns.md)
#   D9) README has no functional reference to removed skills
#       (word-boundary scan: \bgrade\b|\btriage\b|\bbridge\b|`/dev`|baransu:dev)
#
# (D10 — release-notes-draft gate for the 2.1.0 slim release — was retired
# after shipping; it asserted a transient untracked .claude/execute/ artifact.)
#
# Exit 0 on all pass; non-zero on any fail.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLUGIN_JSON="$WORKTREE_ROOT/plugins/baransu/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$WORKTREE_ROOT/.claude-plugin/marketplace.json"
CLAUDE_MD="$WORKTREE_ROOT/CLAUDE.md"
README_MD="$WORKTREE_ROOT/README.md"

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
# Not pinned to an exact string (that broke at every bump); assert semver
# shape and major >= 2. Cross-manifest equality is owned by
# scripts/verify-skills.py (three-face check), not duplicated here.
PLUGIN_VERSION=$(python3 -c "import json;print(json.load(open('$PLUGIN_JSON'))['version'])" 2>/dev/null)
if echo "$PLUGIN_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  MAJOR=${PLUGIN_VERSION%%.*}
  if [ "$MAJOR" -ge 2 ]; then
    ok "D1 plugin.json version is semver and >= 2.x ($PLUGIN_VERSION)"
  else
    bad "D1 plugin.json version major < 2: '$PLUGIN_VERSION'"
  fi
else
  bad "D1 plugin.json version is not semver: '$PLUGIN_VERSION'"
fi

# --- D2: plugin.json description ---
PLUGIN_DESC=$(python3 -c "import json;print(json.load(open('$PLUGIN_JSON'))['description'])" 2>/dev/null)
if echo "$PLUGIN_DESC" | grep -qiE '\b16\b|sixteen'; then
  bad "D2 plugin.json description still says 16/sixteen: $PLUGIN_DESC"
elif echo "$PLUGIN_DESC" | grep -qiE '\b14\b|fourteen'; then
  ok "D2 plugin.json description describes fourteen skills"
else
  bad "D2 plugin.json description does not mention fourteen/14: $PLUGIN_DESC"
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
if [ "$ROW_COUNT" -eq 14 ]; then
  ok "D7a CLAUDE.md skills table has 14 rows"
else
  bad "D7a CLAUDE.md skills table has $ROW_COUNT rows, expected 14"
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

echo ""
echo "=== test-distribution-metadata: $PASS_COUNT passed, $FAIL_COUNT failed ==="
[ "$FAIL_COUNT" -eq 0 ] || exit 1
exit 0
