#!/usr/bin/env bash
# Structural test for /write SKILL.md
# Asserts the three light-mode additions:
#   1. Voice cue段：optional voice="..." parameter, anti-AI floor exempt, Generate ignores
#   2. Long input handling: mode-aware suppression for long input, rules 5/7/8 exempt
#   3. Rule tag examples include voice 套用 / Voice applied
# Also guards the invariants the light plan promised to preserve:
#   - Refine output format remains Before/After/修正說明 (no new sections)
#   - existing zh/en prefix behavior described as before

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SKILL_PATH="${REPO_ROOT}/plugins/baransu/skills/write/SKILL.md"

failures=0
fail() { echo "FAIL: $1" >&2; failures=$((failures + 1)); }
pass() { echo "PASS: $1"; }

if [[ ! -f "${SKILL_PATH}" ]]; then
  echo "FATAL: SKILL.md not found at ${SKILL_PATH}" >&2
  exit 2
fi

# ---------------------------------------------------------------
# Block A — Voice cue 段
# ---------------------------------------------------------------

# A1. Mention `voice="..."` parameter syntax
if grep -qE 'voice="' "${SKILL_PATH}"; then
  pass "A1. SKILL.md describes voice=\"...\" parameter"
else
  fail "A1. SKILL.md missing voice=\"...\" parameter description"
fi

# A2. Voice cue is explicitly optional (not 必選)
if grep -qE '(optional|可選|選擇性)' "${SKILL_PATH}" && grep -qE 'voice' "${SKILL_PATH}"; then
  pass "A2. voice cue described as optional"
else
  fail "A2. voice cue not explicitly described as optional"
fi

# A3. Voice cue does not override anti-AI 味 floor (rules 5/7/8)
if grep -qE 'voice.*(does not override|不覆蓋|不(會)?推翻).*(5|7|8)' "${SKILL_PATH}" \
   || grep -qE '(rules?|規則).*5.*7.*8.*(floor|底線|exempt|不受|不被)' "${SKILL_PATH}"; then
  pass "A3. voice cue exempts rules 5/7/8 (anti-AI floor)"
else
  fail "A3. SKILL.md missing voice ↔ rules 5/7/8 floor invariant"
fi

# A4. Voice cue ignored in Generate mode — must mention voice + Generate + ignored/忽略 on same line
if grep -qE '(voice.*Generate.*(ignored|忽略)|Generate.*voice.*(ignored|忽略))' "${SKILL_PATH}"; then
  pass "A4. voice cue handling in Generate mode is described"
else
  fail "A4. SKILL.md missing voice handling in Generate mode"
fi

# ---------------------------------------------------------------
# Block B — Long input handling (mode-aware suppression)
# ---------------------------------------------------------------

# B1. Long input handling section exists
if grep -qE '(Long input|長文輸入|long-form|long input handling)' "${SKILL_PATH}"; then
  pass "B1. Long input handling section present"
else
  fail "B1. SKILL.md missing Long input handling section"
fi

# B2. Suppression triggers on size threshold (paragraph or char/word count)
if grep -qE '(≥|>=)[[:space:]]*[0-9]+[[:space:]]*(段|paragraph)' "${SKILL_PATH}" \
   && grep -qE '(≥|>=)[[:space:]]*[0-9]+[[:space:]]*(字|character|word)' "${SKILL_PATH}"; then
  pass "B2. Suppression has both paragraph and char/word thresholds"
else
  fail "B2. SKILL.md missing suppression thresholds (paragraph + char/word)"
fi

# B3. Suppression behavior: change only most-impacted instance per rule
if grep -qE '(只改|only.*most|最(影響|高密度|集中))' "${SKILL_PATH}"; then
  pass "B3. Suppression changes only most-impacted instance"
else
  fail "B3. SKILL.md missing suppression behavior (most-impacted-only)"
fi

# B4. Rules 5/7/8 are exempt from suppression
if grep -qE '(5.*7.*8|5/7/8|rules?.*5.*7.*8).*(exempt|不受|不適用|apply.*every|每一處|every match)' "${SKILL_PATH}"; then
  pass "B4. Rules 5/7/8 exempt from suppression"
else
  fail "B4. SKILL.md missing rules 5/7/8 suppression exemption"
fi

# ---------------------------------------------------------------
# Block C — Rule tag examples include voice
# ---------------------------------------------------------------

# C1. zh rule tag examples include `voice 套用`
if grep -qE 'voice[[:space:]]*套用' "${SKILL_PATH}"; then
  pass "C1. zh rule tag list includes 'voice 套用'"
else
  fail "C1. SKILL.md zh rule tag list missing 'voice 套用'"
fi

# C2. en rule tag examples include `Voice applied`
if grep -qE 'Voice applied' "${SKILL_PATH}"; then
  pass "C2. en rule tag list includes 'Voice applied'"
else
  fail "C2. SKILL.md en rule tag list missing 'Voice applied'"
fi

# ---------------------------------------------------------------
# Block D — Backward compat invariants (light plan promise)
# ---------------------------------------------------------------

# D1. Refine output format remains Before/After/修正說明 (no new sections)
if grep -qE '\*\*Before:\*\*' "${SKILL_PATH}" \
   && grep -qE '\*\*After:\*\*' "${SKILL_PATH}" \
   && grep -qE '\*\*修正說明：\*\*' "${SKILL_PATH}"; then
  pass "D1. Refine output format Before/After/修正說明 preserved"
else
  fail "D1. SKILL.md changed Refine output format (Before/After/修正說明)"
fi

# D2. Refine output must NOT contain Voice 拆解 / Sample sections
#     (these belong to the heavy plan; light plan ships without them)
if grep -qE '\*\*Voice 拆解：?\*\*' "${SKILL_PATH}" \
   || grep -qE '\*\*Sample：?\*\*' "${SKILL_PATH}"; then
  fail "D2. SKILL.md unexpectedly contains Voice 拆解/Sample headers (heavy-plan leak)"
else
  pass "D2. SKILL.md does not introduce Voice 拆解/Sample headers"
fi

# D3. Existing zh/en prefix behavior preserved (auto-detect rule still mentions one CJK char)
if grep -qE '(any Chinese character|single Chinese character|one Unicode CJK)' "${SKILL_PATH}"; then
  pass "D3. Existing prefix auto-detection rule preserved"
else
  fail "D3. SKILL.md auto-detection rule appears modified or removed"
fi

# D4. Single-pass constraint preserved
if grep -qE 'Single-pass only' "${SKILL_PATH}"; then
  pass "D4. Single-pass constraint preserved"
else
  fail "D4. SKILL.md Single-pass constraint missing or modified"
fi

# ---------------------------------------------------------------

echo ""
if [[ ${failures} -eq 0 ]]; then
  echo "All structural assertions passed."
  exit 0
else
  echo "Total failures: ${failures}"
  exit 1
fi
