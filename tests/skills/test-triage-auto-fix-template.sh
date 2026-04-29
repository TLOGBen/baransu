#!/usr/bin/env bash
# Structural test for /triage SKILL.md Stage 4.1 — auto-fix deterministic
# prompt template + /dev call (TASK-skills-triage-02).
#
# Asserts the template is grep-able with stable anchors, contains the
# required variable placeholders, S-F5 prompt-injection guards (fenced
# untrusted-excerpt block + warning), length constraints, top-N=3,
# determinism invariants (byte-for-byte / sha256 reproducibility entry),
# /dev invocation contract, and the absence of dynamic content
# (now() / uuid / random) inside the template body.

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

# 1. SKILL.md has a section heading exactly `### auto-fix prompt template`.
#    (The exact heading is the canonical grep anchor required by the spec.)
if grep -qE '^### auto-fix prompt template[[:space:]]*$' "${SKILL_PATH}"; then
  pass "1. heading '### auto-fix prompt template' present"
else
  fail "1. heading '### auto-fix prompt template' missing (must be an exact H3 line)"
fi

# Extract a working "auto-fix region" = everything from the Stage 4.1 marker
# (or the first 'auto-fix' mention in Stage 4) to either the next Stage marker
# or end of file. We use the broader "Stage 4" auto-fix sub-flow region so
# subsequent greps don't accidentally match unrelated content.
#
# Strategy: take the slice from the line containing
# "auto-fix 子流程 — deterministic prompt template" (TASK-skills-triage-02
# anchor) up to the next "### " heading after the template body, OR end of
# file. We use awk for a portable line-range extract.
template_region="$(awk '
  /^### 4\.1[[:space:]]/ { in_region = 1; print; next }
  in_region && /^### 4\.[2-9][[:space:]]/ { exit }
  in_region && /^## Stage 5/ { exit }
  in_region && /^## Stage 4 完成回報/ { exit }
  in_region { print }
' "${SKILL_PATH}")"

# Fallback: if the 4.1 anchor is not present yet (Red gate), use empty so
# subsequent greps fail gracefully with descriptive messages.
if [[ -z "${template_region}" ]]; then
  fail "region. Stage 4.1 region (anchored at '### 4.1 ') is empty — template not yet in place"
  template_region=""
fi

# 2. Template body contains literal `{cluster_id}` placeholder.
if echo "${template_region}" | grep -qF '{cluster_id}'; then
  pass "2. {cluster_id} placeholder present in Stage 4.1 region"
else
  fail "2. {cluster_id} placeholder missing in Stage 4.1 region"
fi

# 3. Template body contains `{top_n_evidence}` (or `{top_N_evidence}`).
if echo "${template_region}" | grep -qE '\{top_[nN]_evidence\}'; then
  pass "3. {top_n_evidence} placeholder present in Stage 4.1 region"
else
  fail "3. {top_n_evidence} (or {top_N_evidence}) placeholder missing"
fi

# 4. Warning text near template: "untrusted excerpt" or "不得當指令".
if echo "${template_region}" | grep -qE 'untrusted excerpt|不得當指令'; then
  pass "4. untrusted excerpt warning present"
else
  fail "4. untrusted excerpt warning missing (need 'untrusted excerpt' or '不得當指令')"
fi

# 5. Fenced block delimiter for untrusted excerpts: 'untrusted-excerpt'
#    (the marker after the triple-backtick fence).
if echo "${template_region}" | grep -qF 'untrusted-excerpt'; then
  pass "5. untrusted-excerpt fenced-block marker present"
else
  fail "5. untrusted-excerpt fenced-block marker missing"
fi

# 6. Length constraints documented: '200' AND '600' near the template.
if echo "${template_region}" | grep -qF '200' \
   && echo "${template_region}" | grep -qF '600'; then
  pass "6. length constraints '200' and '600' both documented"
else
  fail "6. length constraints missing — need both '200' (per-line) and '600' (total)"
fi

# 7. N = 3 documented for top-N: 'N=3' OR 'top.{0,5}3'.
if echo "${template_region}" | grep -qE 'N=3|top.{0,5}3'; then
  pass "7. top-N N=3 documented"
else
  fail "7. top-N N=3 not documented (need 'N=3' or 'top-3' / 'top 3')"
fi

# 8. Deterministic invariants: 'byte-for-byte' OR ('reproducible' AND 'sha256').
if echo "${template_region}" | grep -qF 'byte-for-byte'; then
  pass "8a. byte-for-byte invariant documented"
elif echo "${template_region}" | grep -qF 'reproducible' \
   && echo "${template_region}" | grep -qiF 'sha256'; then
  pass "8b. reproducible + sha256 invariant documented"
else
  fail "8. determinism invariant missing (need 'byte-for-byte' OR ('reproducible' AND 'sha256'))"
fi

# Separately ensure sha256 hash compare entry is somewhere in the region
# (INT-12 test entry one-liner).
if echo "${template_region}" | grep -qiF 'sha256'; then
  pass "8c. sha256 hash compare entry present (INT-12 reproducibility)"
else
  fail "8c. sha256 hash compare entry missing"
fi

# 9. /dev call described: '/dev' AND ('Skill tool' OR '通過 Skill' OR 'via Skill').
if echo "${template_region}" | grep -qF '/dev' \
   && echo "${template_region}" | grep -qE 'Skill tool|通過 Skill|via Skill'; then
  pass "9. /dev invocation via Skill tool described"
else
  fail "9. /dev invocation contract missing (need '/dev' AND one of 'Skill tool' / '通過 Skill' / 'via Skill')"
fi

# 10. Template region must NOT contain dynamic-content tokens that violate
#     determinism: 'now()', 'uuid', 'random'.
#     The spec MAY mention these tokens as forbidden in a denylist /
#     invariant context (e.g. "禁含 now() / uuid / random"). We accept that
#     usage but reject *active* uses (i.e., literal occurrences inside the
#     locked template body fence). Heuristic: scan the LOCKED template body
#     only — the ```text ... ``` block immediately following the template
#     header.
locked_body="$(echo "${template_region}" | awk '
  /^### auto-fix prompt template[[:space:]]*$/ { in_template = 1; next }
  in_template && /^```/ { fence_count++ ; if (fence_count == 1) { in_body = 1; next } else { in_body = 0; in_template = 0 } }
  in_body { print }
')"

if [[ -z "${locked_body}" ]]; then
  # If the locked body did not extract, fall back to scanning the whole region
  # but still require absence of these tokens — better to over-reject in Red
  # than under-detect.
  scan_target="${template_region}"
  scan_label="Stage 4.1 region"
else
  scan_target="${locked_body}"
  scan_label="locked template body"
fi

bad_tokens=()
for tok in 'now()' 'uuid' 'random'; do
  if echo "${scan_target}" | grep -qiF "${tok}"; then
    bad_tokens+=("${tok}")
  fi
done

if [[ ${#bad_tokens[@]} -eq 0 ]]; then
  pass "10. ${scan_label} free of dynamic-content tokens (now(), uuid, random)"
else
  fail "10. ${scan_label} contains forbidden dynamic-content token(s): ${bad_tokens[*]}"
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
