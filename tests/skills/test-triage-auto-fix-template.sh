#!/usr/bin/env bash
# Structural test for /triage SKILL.md Stage 4.1 — auto-fix renderer call
# (TASK-enforcement-03).
#
# After the enforcement-03 rewrite, Stage 4.1 stops embedding prose-level
# escape/truncate rules and instead instructs the caller to invoke the
# deterministic Python renderer:
#
#     python3 plugins/baransu/scripts/render-auto-fix-prompt.py \
#         <cluster_id> <evidence_bundle.json>
#
# The asserts below verify that the new contract is in place:
#   1. Stage 4.1 H3 heading present
#   2. literal `render-auto-fix-prompt.py` reference inside the 4.1 region
#   3. CLI signature mentions `<cluster_id>` and `<evidence_bundle` (or the
#      `evidence_bundle.json` filename)
#   4. stdout-as-prompt-for-/dev contract documented
#   5. sha256 reproducibility wording present (INT-12 byte-identical)
#   6. Stage 4.1 region does NOT carry prose-level marker forgery /
#      control-char / 200/600 truncate rules (those have been rebased to
#      the renderer's docstring — leaving them here would be a regression
#      to the old contract).

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

# 1. Stage 4.1 H3 heading present (anchor for the region).
if grep -qE '^### 4\.1[[:space:]]' "${SKILL_PATH}"; then
  pass "1. Stage 4.1 H3 heading present"
else
  fail "1. Stage 4.1 H3 heading missing"
fi

# Extract Stage 4.1 region: from `### 4.1 ` to next `### 4.[2-9] ` or `## ` heading.
region="$(awk '
  /^### 4\.1[[:space:]]/ { in_region = 1; print; next }
  in_region && /^### 4\.[2-9][[:space:]]/ { exit }
  in_region && /^## / { exit }
  in_region { print }
' "${SKILL_PATH}")"

if [[ -z "${region}" ]]; then
  fail "region. Stage 4.1 region (anchored at '### 4.1 ') is empty — Stage 4.1 not in place"
  region=""
fi

# 2. Literal renderer script reference: `render-auto-fix-prompt.py`.
if echo "${region}" | grep -qF 'render-auto-fix-prompt.py'; then
  pass "2. literal 'render-auto-fix-prompt.py' present in Stage 4.1 region"
else
  fail "2. 'render-auto-fix-prompt.py' literal missing — Stage 4.1 must invoke the renderer script"
fi

# 3. CLI signature: `<cluster_id>` and either `<evidence_bundle` or
#    `evidence_bundle.json` documented as args.
if echo "${region}" | grep -qF '<cluster_id>'; then
  pass "3a. CLI arg '<cluster_id>' documented"
else
  fail "3a. CLI arg '<cluster_id>' missing"
fi
if echo "${region}" | grep -qE '<evidence_bundle|evidence_bundle\.json'; then
  pass "3b. CLI arg 'evidence_bundle' (or 'evidence_bundle.json') documented"
else
  fail "3b. CLI arg 'evidence_bundle' / 'evidence_bundle.json' missing"
fi

# 4. stdout-as-prompt-for-/dev contract.
if echo "${region}" | grep -qF '/dev' \
   && echo "${region}" | grep -qiE 'stdout'; then
  pass "4. stdout->/dev prompt contract documented"
else
  fail "4. stdout->/dev prompt contract missing (need both 'stdout' and '/dev')"
fi

# 5. sha256 reproducibility wording (INT-12 byte-identical contract).
if echo "${region}" | grep -qiF 'sha256' \
   && echo "${region}" | grep -qE 'reproducib|byte-stable|byte-identical|byte-for-byte'; then
  pass "5. sha256 + reproducibility wording present (INT-12)"
else
  fail "5. sha256 reproducibility wording missing (need 'sha256' AND one of 'reproducib*' / 'byte-stable' / 'byte-identical' / 'byte-for-byte')"
fi

# 6. Stage 4.1 region must NOT carry prose-level rules that have been
#    rebased to the renderer docstring. Specifically:
#      - per-line cap '200' character spec (was prose-level, now in renderer)
#      - total cap '600' character spec
#      - control-char escape rule (was prose, e.g. '\\x00' or '控制字元')
#      - marker-forgery escape rule (was prose, e.g. '[BEGIN_untrusted-excerpt]'
#        or '[END_untrusted-excerpt]' literal escape mapping)
#    We assert these prose-level details no longer live inside Stage 4.1.

if echo "${region}" | grep -qE '<= ?200|≤ ?200|200 ?(chars|characters|字元)'; then
  fail "6a. prose-level '200 chars' per-line cap still in Stage 4.1 (must rebase to renderer docstring)"
else
  pass "6a. prose-level '200 chars' per-line cap not in Stage 4.1 region"
fi

if echo "${region}" | grep -qE '<= ?600|≤ ?600|600 ?(chars|characters|字元)'; then
  fail "6b. prose-level '600 chars' total cap still in Stage 4.1 (must rebase to renderer docstring)"
else
  pass "6b. prose-level '600 chars' total cap not in Stage 4.1 region"
fi

if echo "${region}" | grep -qE '\\x00|控制字元|control char'; then
  fail "6c. prose-level control-char escape rule still in Stage 4.1 (must rebase to renderer)"
else
  pass "6c. prose-level control-char escape rule not in Stage 4.1 region"
fi

if echo "${region}" | grep -qF '[BEGIN_untrusted-excerpt]' \
   || echo "${region}" | grep -qF '[END_untrusted-excerpt]'; then
  fail "6d. prose-level marker-forgery escape mapping still in Stage 4.1 (must rebase to renderer)"
else
  pass "6d. prose-level marker-forgery escape mapping not in Stage 4.1 region"
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
