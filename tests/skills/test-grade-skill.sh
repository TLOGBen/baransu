#!/usr/bin/env bash
# Structural test for /grade SKILL.md
# Asserts presence of frontmatter, stages, 5 dim names, rubric table,
# equal-weight bootstrap, tune trigger ≥ 50, completed-only filter,
# and references to grade-collector and harness-reaper.

set -u

# Resolve repo root (worktree root) regardless of where this is invoked.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

SKILL_PATH="${REPO_ROOT}/plugins/baransu/skills/grade/SKILL.md"

failures=0
fail() {
  echo "FAIL: $1" >&2
  failures=$((failures + 1))
}
pass() {
  echo "PASS: $1"
}

# 1. SKILL.md exists
if [[ ! -f "${SKILL_PATH}" ]]; then
  fail "1. SKILL.md does not exist at ${SKILL_PATH}"
  echo ""
  echo "Total failures: ${failures}"
  exit 1
fi
pass "1. SKILL.md exists"

# Extract frontmatter (between first two '---' lines).
frontmatter="$(awk '/^---$/{c++; next} c==1{print}' "${SKILL_PATH}")"

# 2. Frontmatter contains `name:` and a `description:` with ≥ 3 trigger phrases.
if echo "${frontmatter}" | grep -qE '^name:[[:space:]]*\S'; then
  pass "2a. frontmatter has name field"
else
  fail "2a. frontmatter missing name: field"
fi

if echo "${frontmatter}" | grep -qE '^description:[[:space:]]*\S'; then
  pass "2b. frontmatter has description field"
else
  fail "2b. frontmatter missing description: field"
fi

trigger_hits=0
for phrase in "打分" "grade" "評分" "評估 skill" "rubric"; do
  if echo "${frontmatter}" | grep -qF "${phrase}"; then
    trigger_hits=$((trigger_hits + 1))
  fi
done
if [[ ${trigger_hits} -ge 3 ]]; then
  pass "2c. description contains ${trigger_hits} trigger phrases (≥ 3)"
else
  fail "2c. description has only ${trigger_hits} trigger phrases (need ≥ 3)"
fi

# 3. SKILL body has Stage 0/1/2/3/4 sections.
for stage_num in 0 1 2 3 4; do
  if grep -qE "Stage[[:space:]]+${stage_num}" "${SKILL_PATH}"; then
    pass "3.${stage_num} Stage ${stage_num} section present"
  else
    fail "3.${stage_num} Stage ${stage_num} section missing"
  fi
done

# 4. The 5 baransu-native dim names appear.
for dim in outcome_quality iteration_velocity scope_blast human_override_rate failure_recurrence; do
  if grep -qF "${dim}" "${SKILL_PATH}"; then
    pass "4. dim name '${dim}' present"
  else
    fail "4. dim name '${dim}' missing"
  fi
done

# 5. The 5-dim rubric table is present with at least 4 columns.
# Detect a markdown table row that contains all 5 column headers (dim / 意義 / telemetry 來源 / 推導規則).
if grep -E '^\|.*dim.*\|.*意義.*\|.*telemetry.*\|.*推導規則' "${SKILL_PATH}" >/dev/null; then
  pass "5. rubric table header (≥ 4 columns: dim / 意義 / telemetry / 推導規則) present"
else
  fail "5. rubric table header (dim / 意義 / telemetry / 推導規則) not found"
fi

# 6. Equal-weight bootstrap clause: grep `1/5` OR `0.2` OR `equal[_ -]weight`.
if grep -qE '1/5|0\.2|equal[_ -]weight' "${SKILL_PATH}"; then
  pass "6. equal-weight bootstrap clause present"
else
  fail "6. equal-weight bootstrap clause missing"
fi

# 7. Tune trigger ≥ 50: grep `>= 50` OR `≥ 50`.
if grep -qE '>= 50|≥ 50' "${SKILL_PATH}"; then
  pass "7. tune trigger ≥ 50 clause present"
else
  fail "7. tune trigger ≥ 50 clause missing"
fi

# 8. completed-only filter: grep `terminal_state` AND `completed`.
if grep -qF "terminal_state" "${SKILL_PATH}" && grep -qF "completed" "${SKILL_PATH}"; then
  pass "8. completed-only filter (terminal_state + completed) present"
else
  fail "8. completed-only filter missing (need both terminal_state and completed)"
fi

# 9. Reference to grade-collector script.
if grep -qF "grade-collector" "${SKILL_PATH}"; then
  pass "9. grade-collector reference present"
else
  fail "9. grade-collector reference missing"
fi

# 10. Reference to harness-reaper Stage 0 invocation.
if grep -qE 'harness-reaper|staleness' "${SKILL_PATH}"; then
  pass "10. harness-reaper / staleness reference present"
else
  fail "10. harness-reaper / staleness reference missing"
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
