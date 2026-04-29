#!/usr/bin/env bash
# Structural test for /triage SKILL.md (skeleton version).
# Asserts presence of frontmatter trigger phrases, Stage 0..4 sections,
# explicit scope boundaries (no scoring / no direct code edits),
# references to triage-cluster script + investigator-agent + grade-triage-schema,
# Stage 4 auto-fix sub-flow placeholder/extension marker,
# triage.jsonl row schema field mentions,
# and the investigator read-only invariant.

set -u

# Resolve repo root (worktree root) regardless of where this is invoked.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

SKILL_PATH="${REPO_ROOT}/plugins/baransu/skills/triage/SKILL.md"

failures=0
fail() {
  echo "FAIL: $1" >&2
  failures=$((failures + 1))
}
pass() {
  echo "PASS: $1"
}

# 1. SKILL.md exists.
if [[ ! -f "${SKILL_PATH}" ]]; then
  fail "1. SKILL.md does not exist at ${SKILL_PATH}"
  echo ""
  echo "Total failures: ${failures}"
  exit 1
fi
pass "1. SKILL.md exists"

# Extract frontmatter (between first two '---' lines).
frontmatter="$(awk '/^---$/{c++; next} c==1{print}' "${SKILL_PATH}")"

# 2. Frontmatter description has ≥ 3 trigger phrases from the locked set.
trigger_hits=0
for phrase in "triage" "分流" "處理 poor verdict" "聚類" "cluster"; do
  if echo "${frontmatter}" | grep -qF "${phrase}"; then
    trigger_hits=$((trigger_hits + 1))
  fi
done
if [[ ${trigger_hits} -ge 3 ]]; then
  pass "2. description contains ${trigger_hits} trigger phrases (≥ 3)"
else
  fail "2. description has only ${trigger_hits} trigger phrases (need ≥ 3 of: triage / 分流 / 處理 poor verdict / 聚類 / cluster)"
fi

# 3. Stage 0/1/2/3/4 sections present.
for stage_num in 0 1 2 3 4; do
  if grep -qE "Stage[[:space:]]+${stage_num}" "${SKILL_PATH}"; then
    pass "3.${stage_num} Stage ${stage_num} section present"
  else
    fail "3.${stage_num} Stage ${stage_num} section missing"
  fi
done

# 4. Body has explicit scope boundaries:
#    "不打分（交給 /grade）" AND "不直接修 code".
# Accept English equivalent for the second clause: 'no direct code'.
if grep -qE '不打分.*grade|grade.*不打分' "${SKILL_PATH}"; then
  pass "4a. boundary: 不打分（交給 /grade）present"
else
  fail "4a. boundary 不打分（交給 /grade）missing"
fi

if grep -qE '不直接修 code|不直接修code|no direct code' "${SKILL_PATH}"; then
  pass "4b. boundary: 不直接修 code present"
else
  fail "4b. boundary 不直接修 code missing"
fi

# 5. References triage-cluster script.
if grep -qF "triage-cluster" "${SKILL_PATH}"; then
  pass "5. triage-cluster script reference present"
else
  fail "5. triage-cluster script reference missing"
fi

# 6. References investigator-agent.
if grep -qF "investigator" "${SKILL_PATH}"; then
  pass "6. investigator (-agent) reference present"
else
  fail "6. investigator-agent reference missing"
fi

# 7. References grade-triage-schema.md OR triage.jsonl.
if grep -qE 'grade-triage-schema|triage\.jsonl' "${SKILL_PATH}"; then
  pass "7. schema / triage.jsonl reference present"
else
  fail "7. neither grade-triage-schema nor triage.jsonl mentioned"
fi

# 8. Stage 4 auto-fix sub-flow placeholder marker (extension point for triage-02/03/04).
if grep -qE 'auto-fix|自動修補' "${SKILL_PATH}"; then
  pass "8. Stage 4 auto-fix / 自動修補 placeholder present"
else
  fail "8. Stage 4 auto-fix placeholder missing"
fi

# 9. Output schema mention: cluster_id, member_session_ids, evidence_bundle, escalate.
for field in cluster_id member_session_ids evidence_bundle escalate; do
  if grep -qF "${field}" "${SKILL_PATH}"; then
    pass "9. triage.jsonl field '${field}' mentioned"
  else
    fail "9. triage.jsonl field '${field}' missing"
  fi
done

# 10. KD#1 read-only invariant for investigator: grep `read-only` AND `investigator`.
if grep -qF "read-only" "${SKILL_PATH}" && grep -qF "investigator" "${SKILL_PATH}"; then
  pass "10. read-only invariant + investigator present"
else
  fail "10. read-only invariant for investigator missing (need both 'read-only' and 'investigator')"
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
