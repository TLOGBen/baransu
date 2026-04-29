#!/usr/bin/env bash
# Structural test for /triage SKILL.md Stage 4.3 — auto-fix worktree
# isolation with trap-protected mktemp (TASK-skills-triage-04).
#
# Asserts the Stage 4.3 region documents:
#   1. heading `### 4.3` containing both `worktree` and `mktemp` keywords
#   2. mktemp pattern with `baransu-harness` namespace (NOT baransu-bridge)
#   3. `git worktree add` invocation
#   4. `trap` with at least EXIT and INT (TERM ideally also)
#   5. cleanup order: `git worktree remove --force` BEFORE `rm -rf`
#   6. INV-5 invariant: `INV-5` token AND `git status --porcelain` one-liner
#   7. Reference to task-scripts-03 bridge-replay.sh as pattern reuse
#   8. "主 repo working tree" / "main repo working tree" never-touched note

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

# Extract the Stage 4.3 region: from `### 4.3 ` up to the next
# `### 4.[4-9]` heading or `## ` heading (whichever first).
region="$(awk '
  /^### 4\.3[[:space:]]/ { in_region = 1; print; next }
  in_region && /^### 4\.[4-9][[:space:]]/ { exit }
  in_region && /^## / { exit }
  in_region { print }
' "${SKILL_PATH}")"

if [[ -z "${region}" ]]; then
  fail "region. Stage 4.3 region (anchored at '### 4.3 ') is empty"
  region=""
fi

# 1. Heading `### 4.3` containing both `worktree` and `mktemp`.
if grep -qE '^### 4\.3[[:space:]].*worktree.*mktemp|^### 4\.3[[:space:]].*mktemp.*worktree' "${SKILL_PATH}"; then
  pass "1. Stage 4.3 heading present with 'worktree' AND 'mktemp' keywords"
else
  fail "1. Stage 4.3 heading missing or lacks both 'worktree' and 'mktemp' keywords"
fi

# 2. mktemp pattern with baransu-harness namespace.
if echo "${region}" | grep -qE 'mktemp.*baransu-harness'; then
  pass "2. mktemp pattern with 'baransu-harness' namespace present"
else
  fail "2. mktemp 'baransu-harness' namespace missing (must distinguish from baransu-bridge)"
fi

# 3. `git worktree add` mentioned.
if echo "${region}" | grep -qF 'git worktree add'; then
  pass "3. 'git worktree add' invocation referenced"
else
  fail "3. 'git worktree add' missing"
fi

# 4. `trap` with at least EXIT and INT (TERM ideally also).
if echo "${region}" | grep -qE 'trap[^A-Za-z0-9_].*EXIT' \
   && echo "${region}" | grep -qE 'trap[^A-Za-z0-9_].*INT|INT[^A-Za-z0-9_]'; then
  pass "4a. 'trap' with EXIT and INT referenced"
else
  fail "4a. trap with EXIT and INT not referenced"
fi
if echo "${region}" | grep -qE 'TERM'; then
  pass "4b. 'TERM' signal also covered (ideal)"
else
  fail "4b. 'TERM' signal not covered"
fi

# 5. Cleanup order: `git worktree remove --force` BEFORE `rm -rf` in the doc.
remove_line=$(echo "${region}" | grep -nF 'git worktree remove --force' | head -1 | cut -d: -f1)
rmrf_line=$(echo "${region}" | grep -nE 'rm -rf' | head -1 | cut -d: -f1)
if [[ -n "${remove_line}" && -n "${rmrf_line}" && ${remove_line} -lt ${rmrf_line} ]]; then
  pass "5. cleanup order correct: 'git worktree remove --force' (line ${remove_line}) before 'rm -rf' (line ${rmrf_line})"
else
  fail "5. cleanup order wrong or missing (remove_line='${remove_line}' rmrf_line='${rmrf_line}')"
fi

# 6. INV-5 invariant: `INV-5` token AND `git status --porcelain` one-liner.
if echo "${region}" | grep -qF 'INV-5'; then
  pass "6a. 'INV-5' invariant token referenced"
else
  fail "6a. 'INV-5' invariant token missing"
fi
if echo "${region}" | grep -qF 'git status --porcelain'; then
  pass "6b. 'git status --porcelain' verification one-liner referenced"
else
  fail "6b. 'git status --porcelain' missing"
fi

# 7. Reference to task-scripts-03 bridge-replay.sh as pattern reuse.
if echo "${region}" | grep -qF 'bridge-replay'; then
  pass "7. 'bridge-replay' pattern reuse reference present"
else
  fail "7. 'bridge-replay' reference missing"
fi

# 8. "主 repo working tree" or "main repo working tree" never-touched note.
if echo "${region}" | grep -qE '主 repo working tree|main repo working tree'; then
  pass "8. '主 repo working tree' / 'main repo working tree' phrasing present"
else
  fail "8. '主 repo working tree' / 'main repo working tree' phrasing missing"
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
