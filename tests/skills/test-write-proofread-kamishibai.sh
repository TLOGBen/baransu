#!/usr/bin/env bash
# Pinning test for the /write Proofread route after it was rerouted through
# `kamishibai render` (F8d).
#
# What is actually at risk here is not prose quality — it is four constants an
# agent retypes by hand every run:
#   * the six-column header, which kamishibai freezes upstream (S4 FINDINGS_HEAD)
#     and downstream comparison/counting keys on;
#   * the three badge class names, whose typo mode is *silent* (unstyled plain
#     text, no error anywhere);
#   * the /book red line, which must survive the reroute word for word;
#   * the write target plus its timestamp collision scheme, which is the only
#     thing standing between a second proofread and a destroyed first report.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SPEC_PATH="${REPO_ROOT}/plugins/baransu/skills/write/references/proofread.md"
SKILL_PATH="${REPO_ROOT}/plugins/baransu/skills/write/SKILL.md"

failures=0
fail() { echo "FAIL: $1" >&2; failures=$((failures + 1)); }
pass() { echo "PASS: $1"; }

for f in "${SPEC_PATH}" "${SKILL_PATH}"; do
  if [[ ! -f "${f}" ]]; then
    echo "FATAL: not found: ${f}" >&2
    exit 2
  fi
done

# ---------------------------------------------------------------
# Block A — the six-column header (verbatim, and the 「／」 form is gone)
# ---------------------------------------------------------------

HEADER='| 頁數 | 段落上下文 | 原文內容 | 錯誤類型 | 建議修正 | 修改原因 |'

if grep -qF "${HEADER}" "${SPEC_PATH}"; then
  pass "A1. proofread.md carries the six-column header verbatim"
else
  fail "A1. proofread.md missing the verbatim six-column header row"
fi

if grep -qF '段落／上下文' "${SPEC_PATH}"; then
  fail "A2. proofread.md still uses the 「段落／上下文」 form (upstream anchor has no ／)"
else
  pass "A2. proofread.md carries no 「段落／上下文」 form anywhere"
fi

if grep -qF '段落上下文' "${SKILL_PATH}"; then
  pass "A3. SKILL.md restates the header with the migrated column name"
else
  fail "A3. SKILL.md does not carry the migrated 段落上下文 column name"
fi

# ---------------------------------------------------------------
# Block B — the three badge class names (verbatim constants)
# ---------------------------------------------------------------

for pair in '錯別字:badge badge-typo' '用語不妥:badge badge-diction' '語句不通順:badge badge-flow'; do
  label="${pair%%:*}"
  klass="${pair#*:}"
  if grep -qF "${klass}" "${SPEC_PATH}"; then
    pass "B. proofread.md pins the badge class for ${label}: ${klass}"
  else
    fail "B. proofread.md missing the verbatim badge class for ${label}: ${klass}"
  fi
done

# All three must sit on the same line as their label, or the constants table has
# drifted into a list of class names nobody can map back to a 錯誤類型.
if grep -qF '| 錯別字 | `badge badge-typo` |' "${SPEC_PATH}" \
  && grep -qF '| 用語不妥 | `badge badge-diction` |' "${SPEC_PATH}" \
  && grep -qF '| 語句不通順 | `badge badge-flow` |' "${SPEC_PATH}"; then
  pass "B4. the three classes are mapped to their labels in one constants table"
else
  fail "B4. badge constants table missing or unmapped from the 錯誤類型 labels"
fi

# ---------------------------------------------------------------
# Block C — the /book red line survives the reroute
# ---------------------------------------------------------------

RED_LINE='a proofreading table is analysis output (which /book'"'"'s "no LLM commentary" red line forbids)'

if grep -qF "${RED_LINE}" "${SPEC_PATH}"; then
  pass "C1. proofread.md keeps the /book red-line sentence verbatim"
else
  fail "C1. proofread.md lost the verbatim /book red-line sentence"
fi

# The reroute is only legal because `kamishibai render` is not that pipeline —
# the clarification must be written down, or a later reader reads C1 as a ban on
# the very route this spec now prescribes.
if grep -qF 'is not the /book pipeline' "${SPEC_PATH}"; then
  pass "C2. proofread.md states that kamishibai render is not the /book pipeline"
else
  fail "C2. proofread.md missing the clarification that kamishibai render is not /book"
fi

if grep -qF 'never routes through the /book pipeline' "${SKILL_PATH}"; then
  pass "C3. SKILL.md keeps the never-routes-through-/book constraint literal"
else
  fail "C3. SKILL.md lost the never-routes-through-/book constraint"
fi

if grep -qF 'No validate-output.ts' "${SPEC_PATH}"; then
  pass "C4. proofread.md keeps the No validate-output.ts clause"
else
  fail "C4. proofread.md lost the No validate-output.ts clause"
fi

# ---------------------------------------------------------------
# Block D — the render command form
# ---------------------------------------------------------------

if grep -qF 'kamishibai render <語料.md> -t kami/long-form -o .claude/write/錯字修改.html' "${SPEC_PATH}"; then
  pass "D1. proofread.md pins the render command form verbatim"
else
  fail "D1. proofread.md missing the verbatim render command form"
fi

if grep -qF 'kamishibai lint' "${SPEC_PATH}"; then
  pass "D2. proofread.md requires a lint pass on the artifact"
else
  fail "D2. proofread.md does not verify the artifact with kamishibai lint"
fi

# D2b. The stop clause, pinned positively. D3 below only forbids the retired
# hand-render path; without this the spec could drop the instruction to STOP
# when the CLI is missing and still pass D3 by saying nothing at all — and
# "say nothing" is exactly how an agent improvises its own fallback.
if grep -qF 'If the `kamishibai` CLI is unavailable, say so and stop' "${SPEC_PATH}" \
  && grep -qF 'do not fall back to hand-writing the HTML' "${SPEC_PATH}"; then
  pass "D2b. proofread.md pins the stop-on-missing-CLI clause"
else
  fail "D2b. proofread.md lost the stop-on-missing-CLI clause (no fallback to hand-writing)"
fi

# The retired route must not linger as an alternative: a tokens.css fallback
# next to a render command is an invitation to hand-write the HTML again.
if grep -qF 'tokens.css' "${SPEC_PATH}"; then
  fail "D3. proofread.md still offers the retired tokens.css hand-render path"
else
  pass "D3. proofread.md no longer offers the retired tokens.css hand-render path"
fi

if grep -qF 'kamishibai render' "${SKILL_PATH}"; then
  pass "D4. SKILL.md Stage 4 names the render command"
else
  fail "D4. SKILL.md Stage 4 does not name the render command"
fi

# ---------------------------------------------------------------
# Block E — write target and the timestamp collision scheme
# ---------------------------------------------------------------

if grep -qF '.claude/write/錯字修改.html' "${SPEC_PATH}" \
  && grep -qF '.claude/write/錯字修改.html' "${SKILL_PATH}"; then
  pass "E1. both files name the write target"
else
  fail "E1. write target missing from proofread.md or SKILL.md"
fi

if grep -qF '錯字修改-<YYYYMMDD-HHMMSS>.html' "${SPEC_PATH}" \
  && grep -qF '錯字修改-<YYYYMMDD-HHMMSS>.html' "${SKILL_PATH}"; then
  pass "E2. both files pin the timestamp collision filename"
else
  fail "E2. timestamp collision filename missing from proofread.md or SKILL.md"
fi

# The semantics, not just the filename: an existing report is never clobbered.
if grep -qF 'do NOT silently clobber it' "${SPEC_PATH}"; then
  pass "E3. proofread.md keeps the do-not-clobber semantics"
else
  fail "E3. proofread.md lost the do-not-clobber semantics"
fi

# E4. **Position**, not mere presence. A collision guard written *after* the
# render command is a guard that runs after the file is already overwritten —
# the destroyed report cannot be un-destroyed by a later paragraph. So compare
# line numbers: the guard must appear strictly before, or on the same line as,
# the first line carrying the `-o` target. Existence-only greps (E2/E3) are
# blind to this, which is why the failure it guards against survived them once.
guard_line="$(grep -nF 'do NOT silently clobber it' "${SPEC_PATH}" | head -1 | cut -d: -f1)"
render_line="$(grep -nF -e '-o .claude/write/錯字修改.html' "${SPEC_PATH}" | head -1 | cut -d: -f1)"
if [[ -z "${guard_line}" || -z "${render_line}" ]]; then
  fail "E4. cannot compare positions — guard line or render line not found (guard='${guard_line}' render='${render_line}')"
elif (( guard_line <= render_line )); then
  pass "E4. collision guard (line ${guard_line}) precedes the render command (line ${render_line})"
else
  fail "E4. collision guard (line ${guard_line}) comes AFTER the render command (line ${render_line}) — it would run only once the earlier report is already overwritten"
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
