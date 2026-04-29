#!/usr/bin/env bash
# Structural test for /triage SKILL.md Stage 4.2 — push-gate.sh call
# (TASK-enforcement-03).
#
# After the enforcement-03 rewrite, Stage 4.2 stops describing the 5 gates
# in prose and instead instructs the caller to invoke the deterministic
# bash gate script:
#
#     bash plugins/baransu/scripts/push-gate.sh \
#         <cluster_id> <worktree> <state> <telemetry>
#
# The asserts below verify that the new contract is in place:
#   1. Stage 4.2 H3 heading present
#   2. literal `push-gate.sh` reference inside the 4.2 region
#   3. CLI signature includes <cluster_id>, <worktree>, <state>, <telemetry>
#      argument tokens
#   4. exit code -> escalate enum mapping table present:
#        exit 0 -> git push allowed
#        exit 1 -> escalate=requires_human / escalate_human / daily_quota_exceeded
#        exit 2 -> structural error / abort
#   5. BARANSU_HARNESS_FAKE_NOW reproducibility hook present
#   6. EDGE-3 / EDGE-4 / EDGE-5 case descriptions ALIGN to "invoke
#      push-gate.sh + observe exit code" (rather than prose comparison).
#   7. Stage 4.2 must NOT carry the prose-level "依序檢查 5 gates" listing
#      (those internals have been rebased to push-gate.sh itself).

set -u

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

# Pre-check: SKILL.md exists.
if [[ ! -f "${SKILL_PATH}" ]]; then
  fail "0. SKILL.md does not exist at ${SKILL_PATH}"
  echo ""
  echo "Total failures: ${failures}"
  exit 1
fi

# Extract Stage 4.2 region: from `### 4.2 ` to next `### 4.[3-9] ` or `## ` heading.
region="$(awk '
  /^### 4\.2[[:space:]]/ { in_region = 1; print; next }
  in_region && /^### 4\.[3-9][[:space:]]/ { exit }
  in_region && /^## / { exit }
  in_region { print }
' "${SKILL_PATH}")"

if [[ -z "${region}" ]]; then
  fail "region. Stage 4.2 region (anchored at '### 4.2 ') is empty"
  region=""
fi

# 1. Stage 4.2 H3 heading present.
if grep -qE '^### 4\.2[[:space:]]' "${SKILL_PATH}"; then
  pass "1. Stage 4.2 H3 heading present"
else
  fail "1. Stage 4.2 H3 heading missing"
fi

# 2. literal `push-gate.sh` reference.
if echo "${region}" | grep -qF 'push-gate.sh'; then
  pass "2. literal 'push-gate.sh' present in Stage 4.2 region"
else
  fail "2. 'push-gate.sh' literal missing — Stage 4.2 must invoke the gate script"
fi

# 3. CLI signature args present.
for arg_token in '<cluster_id>' '<worktree' '<state' '<telemetry'; do
  if echo "${region}" | grep -qF "${arg_token}"; then
    pass "3.${arg_token} CLI arg token '${arg_token}' documented"
  else
    fail "3.${arg_token} CLI arg token '${arg_token}' missing"
  fi
done

# 4. Exit code -> escalate enum mapping table:
#    exit 0 (happy / git push allowed),
#    exit 1 (escalate=requires_human / escalate_human / daily_quota_exceeded),
#    exit 2 (structural error / abort).
if echo "${region}" | grep -qE 'exit (code )?0' \
   && echo "${region}" | grep -qiE 'git push|push allowed|allow.*push|happy'; then
  pass "4a. exit 0 mapping (git push / happy) documented"
else
  fail "4a. exit 0 mapping missing (need 'exit 0' AND ('git push' / 'push allowed' / 'happy'))"
fi

if echo "${region}" | grep -qE 'exit (code )?1' \
   && echo "${region}" | grep -qF 'escalate=' \
   && echo "${region}" | grep -qF 'requires_human' \
   && echo "${region}" | grep -qF 'escalate_human' \
   && echo "${region}" | grep -qF 'daily_quota_exceeded'; then
  pass "4b. exit 1 -> escalate enum mapping (3 enums) documented"
else
  fail "4b. exit 1 enum mapping missing (need 'exit 1' AND 'escalate=' AND all of 'requires_human' / 'escalate_human' / 'daily_quota_exceeded')"
fi

if echo "${region}" | grep -qE 'exit (code )?2' \
   && echo "${region}" | grep -qiE 'structural|abort|stderr'; then
  pass "4c. exit 2 mapping (structural error / abort) documented"
else
  fail "4c. exit 2 mapping missing (need 'exit 2' AND 'structural'/'abort'/'stderr')"
fi

# 5. BARANSU_HARNESS_FAKE_NOW reproducibility env var.
if echo "${region}" | grep -qF 'BARANSU_HARNESS_FAKE_NOW'; then
  pass "5. 'BARANSU_HARNESS_FAKE_NOW' env var documented"
else
  fail "5. 'BARANSU_HARNESS_FAKE_NOW' env var missing"
fi

# 6. EDGE-3 / EDGE-4 / EDGE-5 case descriptions aligned to "invoke
#    push-gate.sh + observe exit code".
for edge in EDGE-3 EDGE-4 EDGE-5; do
  if echo "${region}" | grep -qF "${edge}"; then
    pass "6.${edge}a token '${edge}' present"
  else
    fail "6.${edge}a token '${edge}' missing"
  fi
done

# Each EDGE-X case region (between its bullet and next blank line / next EDGE)
# should mention exit-code-based observation (exit 0/1/2) so the description
# ties to push-gate.sh contract rather than prose comparison.
edge_section="$(echo "${region}" | awk '/EDGE-[345]/,/^$/')"
if echo "${edge_section}" | grep -qE 'exit (code )?[012]'; then
  pass "6b. EDGE-3/4/5 cases reference exit-code observation (push-gate.sh contract)"
else
  fail "6b. EDGE-3/4/5 cases do not reference 'exit 0/1/2' — should align to push-gate.sh observation"
fi

# 7. Stage 4.2 region must NOT carry the prose-level "依序" + 5 gates listing
#    (rebased to push-gate.sh internals). We treat presence of *both* the
#    "依序" / "in order" sequencing language *and* the explicit 5 gate names
#    inline as a regression to the old contract.
has_in_order=0
if echo "${region}" | grep -qE '依序|in order|按順序|sequential.*gate'; then
  has_in_order=1
fi
gate_keywords_inside=0
for kw in 'gitignore' 'redaction' 'denylist' 'attempt cap' 'daily.*quota'; do
  if echo "${region}" | grep -qiE "${kw}"; then
    gate_keywords_inside=$((gate_keywords_inside + 1))
  fi
done

if (( has_in_order == 1 )) && (( gate_keywords_inside >= 4 )); then
  fail "7. Stage 4.2 still lists prose-level '依序 5 gates' breakdown (must rebase to push-gate.sh internals)"
else
  pass "7. Stage 4.2 does not carry the prose-level '依序 5 gates' breakdown"
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
