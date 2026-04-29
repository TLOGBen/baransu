#!/usr/bin/env bash
# Structural test for /grade tune-trigger end-to-end (TASK-skills-grade-02).
#
# Asserts:
#   1. SKILL.md Stage 4 mentions a user-facing report line containing
#      "目前 completed row 累積：N" or "completed row 累積" + tune trigger markers
#      (tune_review_due / tune trigger / due / not yet phrasing).
#   2. SKILL.md describes the `--tune-acknowledged` flag, including reset /
#      clear semantics on `tune_review_due_since`.
#   3. SKILL.md references `state.json` `tune_review_due_since` field
#      (both terms must co-occur).
#   4. _shared/state-json-schema.md lists `tune_review_due_since` and
#      `cumulative_completed_count` as recognized state.json fields in the
#      authoritative schema (not just forward-compat).
#   5. grade-collector.py source emits the `tune_review_due` symbol.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

SKILL_PATH="${REPO_ROOT}/plugins/baransu/skills/grade/SKILL.md"
SCHEMA_PATH="${REPO_ROOT}/plugins/baransu/skills/_shared/state-json-schema.md"
COLLECTOR_PATH="${REPO_ROOT}/plugins/baransu/scripts/grade-collector.py"

failures=0
fail() {
  echo "FAIL: $1" >&2
  failures=$((failures + 1))
}
pass() {
  echo "PASS: $1"
}

# Sanity: required files exist.
for path in "${SKILL_PATH}" "${SCHEMA_PATH}" "${COLLECTOR_PATH}"; do
  if [[ ! -f "${path}" ]]; then
    fail "required file missing: ${path}"
  fi
done
if [[ ${failures} -gt 0 ]]; then
  echo ""
  echo "Total failures: ${failures}"
  exit 1
fi

# ---------------------------------------------------------------------------
# 1. Stage 4 user-facing report mentions the cumulative completed row count
#    AND a tune trigger marker.
# ---------------------------------------------------------------------------

# Extract the Stage 4 section (from "Stage 4" heading up to next H2/H3 or EOF).
stage4_block="$(awk '
  /^## Stage 4/ {flag=1; print; next}
  flag && /^## / && !/^## Stage 4/ {flag=0}
  flag {print}
' "${SKILL_PATH}")"

if [[ -z "${stage4_block}" ]]; then
  fail "1. Stage 4 section not found in SKILL.md"
else
  # Cumulative completed row count phrasing — Chinese OR English equivalent.
  if echo "${stage4_block}" | grep -qE '目前 completed row 累積|completed row 累積|cumulative completed (row )?count'; then
    pass "1a. Stage 4 references cumulative completed row count (Chinese or English)"
  else
    fail "1a. Stage 4 missing 'completed row 累積' / cumulative completed count phrasing"
  fi

  # Tune trigger marker — at least one of these must appear in Stage 4.
  if echo "${stage4_block}" | grep -qE 'tune_review_due|tune trigger|due / not yet|due/not yet|not_yet'; then
    pass "1b. Stage 4 references tune trigger status marker"
  else
    fail "1b. Stage 4 missing tune trigger marker (tune_review_due / tune trigger / due / not yet)"
  fi
fi

# ---------------------------------------------------------------------------
# 2. SKILL.md describes `--tune-acknowledged` flag with reset semantics.
# ---------------------------------------------------------------------------

if grep -qF -- '--tune-acknowledged' "${SKILL_PATH}"; then
  pass "2a. SKILL.md mentions --tune-acknowledged flag"
else
  fail "2a. SKILL.md missing --tune-acknowledged flag"
fi

# Reset / clear semantics for tune_review_due_since must co-occur with the flag.
# Pull the surrounding context (5 lines after each match) and check the language.
ack_context="$(grep -n -A 5 -- '--tune-acknowledged' "${SKILL_PATH}" || true)"
if echo "${ack_context}" | grep -qE 'reset|清|null|clear' && \
   echo "${ack_context}" | grep -qF 'tune_review_due_since'; then
  pass "2b. --tune-acknowledged context describes reset/clear of tune_review_due_since"
else
  fail "2b. --tune-acknowledged context missing reset/clear language for tune_review_due_since"
fi

# ---------------------------------------------------------------------------
# 3. SKILL.md references state.json AND tune_review_due_since.
# ---------------------------------------------------------------------------

if grep -qF 'state.json' "${SKILL_PATH}" && grep -qF 'tune_review_due_since' "${SKILL_PATH}"; then
  pass "3. SKILL.md references both state.json and tune_review_due_since"
else
  fail "3. SKILL.md missing state.json + tune_review_due_since pairing"
fi

# ---------------------------------------------------------------------------
# 4. state-json-schema.md lists tune_review_due_since AND
#    cumulative_completed_count as authoritative fields (not just forward-compat).
#
#    Heuristic: both symbols must appear in the file, and at least one
#    occurrence of each must live OUTSIDE the "Forward-compat" section.
# ---------------------------------------------------------------------------

if ! grep -qF 'tune_review_due_since' "${SCHEMA_PATH}"; then
  fail "4a. tune_review_due_since absent from state-json-schema.md"
else
  pass "4a. tune_review_due_since present in state-json-schema.md"
fi

if ! grep -qF 'cumulative_completed_count' "${SCHEMA_PATH}"; then
  fail "4b. cumulative_completed_count absent from state-json-schema.md"
else
  pass "4b. cumulative_completed_count present in state-json-schema.md"
fi

# Strip the "Forward-compat" section (until next H2 or EOF) and ensure both
# symbols still appear in the remainder (= the authoritative portion).
non_fwd_compat="$(awk '
  /^## .*[Ff]orward-compat/ {skip=1; next}
  skip && /^## / && !/^## .*[Ff]orward-compat/ {skip=0}
  !skip {print}
' "${SCHEMA_PATH}")"

if echo "${non_fwd_compat}" | grep -qF 'tune_review_due_since'; then
  pass "4c. tune_review_due_since defined outside Forward-compat (authoritative)"
else
  fail "4c. tune_review_due_since only appears in Forward-compat section"
fi

if echo "${non_fwd_compat}" | grep -qF 'cumulative_completed_count'; then
  pass "4d. cumulative_completed_count defined outside Forward-compat (authoritative)"
else
  fail "4d. cumulative_completed_count only appears in Forward-compat section"
fi

# ---------------------------------------------------------------------------
# 5. grade-collector.py source emits tune_review_due symbol.
# ---------------------------------------------------------------------------

if grep -qF 'tune_review_due' "${COLLECTOR_PATH}"; then
  pass "5. grade-collector.py emits tune_review_due symbol"
else
  fail "5. grade-collector.py missing tune_review_due symbol"
fi

echo ""
echo "Total failures: ${failures}"
if [[ ${failures} -gt 0 ]]; then
  exit 1
fi
exit 0
