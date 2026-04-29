#!/usr/bin/env bash
# Structural test for /triage SKILL.md Stage 4.2 — auto-fix push five-gate
# pipeline (TASK-skills-triage-03).
#
# Asserts the 5 push gates are documented in order, denylist paths are
# enumerated, EDGE-3/4/5 cases are described, INT-7 reproducibility hook
# (BARANSU_HARNESS_FAKE_NOW) is present, escalate enum values are mentioned,
# and the attempt_history mutation contract (telemetry.jsonl as authority,
# flock + atomic write) is referenced.

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

# Pre-check: SKILL.md exists.
if [[ ! -f "${SKILL_PATH}" ]]; then
  fail "0. SKILL.md does not exist at ${SKILL_PATH}"
  echo ""
  echo "Total failures: ${failures}"
  exit 1
fi

# Extract the Stage 4.2 region: everything from `### 4.2 ` up to the next
# `### 4.[3-9]` heading or `## ` heading (whichever first).
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

# 1. Section heading: `### 4.2` followed by something + 'push 閘門' or 'push gates'.
if grep -qE '^### 4\.2[[:space:]].*(push 閘門|push gates|push 五黑|five-gate push)' "${SKILL_PATH}"; then
  pass "1. Stage 4.2 heading present with push-gate keyword"
else
  fail "1. Stage 4.2 heading missing or lacks 'push 閘門' / 'push gates' keyword"
fi

# 2. 5 gates listed in order — grep for each keyword in the 4.2 region.
gate_keywords=('gitignore' 'redaction' 'denylist' 'attempt cap|K=3' 'daily quota|daily push.*5')
gate_labels=('gitignore' 'redaction' 'denylist' 'attempt cap / K=3' 'daily quota / daily push 5')
gate_idx=0
all_gates_found=1
for kw in "${gate_keywords[@]}"; do
  if echo "${region}" | grep -qiE "${kw}"; then
    pass "2.$((gate_idx + 1)) gate keyword '${gate_labels[$gate_idx]}' present"
  else
    fail "2.$((gate_idx + 1)) gate keyword '${gate_labels[$gate_idx]}' missing"
    all_gates_found=0
  fi
  gate_idx=$((gate_idx + 1))
done

# 3. Denylist 5 paths: `.github/`, `plugin.json`, `marketplace.json`, `.gitignore`, `scripts/`.
denylist_paths=('.github/' 'plugin.json' 'marketplace.json' '.gitignore' 'scripts/')
deny_idx=0
for p in "${denylist_paths[@]}"; do
  if echo "${region}" | grep -qF "${p}"; then
    pass "3.$((deny_idx + 1)) denylist path '${p}' enumerated"
  else
    fail "3.$((deny_idx + 1)) denylist path '${p}' missing"
  fi
  deny_idx=$((deny_idx + 1))
done

# 4. Gate ordering described: 1->2->3->4->5 sequence reference.
if echo "${region}" | grep -qE '1[^0-9].*2[^0-9].*3[^0-9].*4[^0-9].*5' \
   || echo "${region}" | grep -qE '依序|in order|sequential|按順序|按序'; then
  pass "4. gate ordering (1->2->3->4->5 / 依序) described"
else
  fail "4. gate ordering not described (need '依序' / 'in order' / '1...2...3...4...5')"
fi

# 5. EDGE-3 case described: mock /dev touches marketplace.json -> abort.
if echo "${region}" | grep -qE 'EDGE-3' \
   && echo "${region}" | grep -qF 'marketplace.json'; then
  pass "5. EDGE-3 case (marketplace.json -> abort) described"
else
  fail "5. EDGE-3 case missing (need 'EDGE-3' AND 'marketplace.json' near each other)"
fi

# 6. EDGE-4 case described: 3rd consecutive cluster fail -> escalate_human.
if echo "${region}" | grep -qE 'EDGE-4' \
   && echo "${region}" | grep -qE 'escalate_human'; then
  pass "6. EDGE-4 case (3rd fail -> escalate_human) described"
else
  fail "6. EDGE-4 case missing (need 'EDGE-4' AND 'escalate_human')"
fi

# 7. EDGE-5 case described: 6th push of day -> daily_quota_exceeded.
if echo "${region}" | grep -qE 'EDGE-5' \
   && echo "${region}" | grep -qF 'daily_quota_exceeded'; then
  pass "7. EDGE-5 case (6th push -> daily_quota_exceeded) described"
else
  fail "7. EDGE-5 case missing (need 'EDGE-5' AND 'daily_quota_exceeded')"
fi

# 8. INT-7 reproducibility: BARANSU_HARNESS_FAKE_NOW.
if echo "${region}" | grep -qF 'BARANSU_HARNESS_FAKE_NOW'; then
  pass "8. INT-7 reproducibility hook 'BARANSU_HARNESS_FAKE_NOW' present"
else
  fail "8. 'BARANSU_HARNESS_FAKE_NOW' env var missing (INT-7 reproducibility)"
fi

# 9. Escalate enum values: requires_human, escalate_human, daily_quota_exceeded.
escalate_values=('requires_human' 'escalate_human' 'daily_quota_exceeded')
esc_idx=0
for v in "${escalate_values[@]}"; do
  if echo "${region}" | grep -qF "${v}"; then
    pass "9.$((esc_idx + 1)) escalate enum '${v}' mentioned"
  else
    fail "9.$((esc_idx + 1)) escalate enum '${v}' missing"
  fi
  esc_idx=$((esc_idx + 1))
done

# 10. attempt_history mutation contract: telemetry.jsonl authority + append element +
#     flock + atomic write referenced.
contract_ok=1
if echo "${region}" | grep -qF 'attempt_history'; then
  pass "10a. 'attempt_history' referenced"
else
  fail "10a. 'attempt_history' not referenced"
  contract_ok=0
fi

if echo "${region}" | grep -qF 'telemetry.jsonl'; then
  pass "10b. 'telemetry.jsonl' referenced as authority"
else
  fail "10b. 'telemetry.jsonl' not referenced"
  contract_ok=0
fi

if echo "${region}" | grep -qiE 'append.*element|append a'; then
  pass "10c. 'append element' contract referenced"
else
  fail "10c. 'append element' contract not referenced"
  contract_ok=0
fi

if echo "${region}" | grep -qiE 'flock'; then
  pass "10d. 'flock' concurrency-protection referenced"
else
  fail "10d. 'flock' not referenced"
  contract_ok=0
fi

if echo "${region}" | grep -qiE 'atomic.*(rename|write)|temp.*rename'; then
  pass "10e. 'atomic temp+rename write' referenced"
else
  fail "10e. atomic temp+rename write not referenced"
  contract_ok=0
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
