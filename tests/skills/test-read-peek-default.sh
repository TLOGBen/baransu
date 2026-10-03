#!/usr/bin/env bash
# Structural test for /read's peek-by-default contract (6.2.0)
# Pins the four Surface Inventory rows of the peek/save contract:
#   test_read_peek_writes_nothing      — peek touches nothing under .claude/read/
#   test_read_save_pipeline_unchanged  — save mode's Stage 3 body is byte-identical to 6.1.1
#   test_learn_calls_read_with_save    — every /learn call into /read carries --save
#   test_read_peek_report_format       — the peek report and frontmatter constants, verbatim

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
READ_DIR="${REPO_ROOT}/plugins/baransu/skills/read"
SKILL="${READ_DIR}/SKILL.md"
LEARN_DIR="${REPO_ROOT}/plugins/baransu/skills/learn"

failures=0
fail() { echo "FAIL: $1" >&2; failures=$((failures + 1)); }
pass() { echo "PASS: $1"; }
has() { grep -qF -- "$2" "$1"; }

[[ -f "${SKILL}" ]] || { echo "FATAL: ${SKILL} not found" >&2; exit 2; }

# ---------------------------------------------------------------
# test_read_peek_writes_nothing
# ---------------------------------------------------------------
if has "${SKILL}" '- peek: `$READ_ROOT=$(mktemp -d)` — a per-run scratch directory outside `.claude/read/`. A peek run MUST NOT create, modify, or delete any path under `.claude/read/`, and it downloads no images.'; then
  pass "peek_writes_nothing: peek READ_ROOT is a scratch dir with the no-touch rule"
else
  fail "peek_writes_nothing: Mode section lost the peek scratch-dir / no-touch rule"
fi

if has "${SKILL}" '3. Delete the run'"'"'s scratch: `rm -rf "$READ_ROOT"`.'; then
  pass "peek_writes_nothing: Peek finish deletes the scratch"
else
  fail "peek_writes_nothing: Peek finish no longer deletes the scratch"
fi

if has "${SKILL}" 'Peek mode skips this section: download nothing'; then
  pass "peek_writes_nothing: image handling is skipped in peek"
else
  fail "peek_writes_nothing: image handling no longer skipped in peek"
fi

# No acquisition/conversion reference may hard-code the archive raw path:
# a lane that writes .claude/read/raw/ directly would leak peek runs into the archive.
LEAKS=$(grep -rnF '.claude/read/raw' "${READ_DIR}/references/acquisition" "${READ_DIR}/references/conversion" || true)
if [[ -z "${LEAKS}" ]]; then
  pass "peek_writes_nothing: no lane hard-codes .claude/read/raw"
else
  fail "peek_writes_nothing: lane writes the archive path directly:"$'\n'"${LEAKS}"
fi

if grep -nE '\.claude/read/raw/\{slug\}/index\.\{ext\}' "${SKILL}" | grep -qv 'Stage 3'; then
  fail "peek_writes_nothing: After Acquire / Stage 2 still write .claude/read/raw directly"
else
  pass "peek_writes_nothing: After Acquire / Stage 2 write under \$READ_ROOT"
fi

# F1: every /tmp intermediate lives under $READ_ROOT in peek, so rm -rf removes it
if has "${SKILL}" 'In peek mode every `/tmp/{slug}-*` intermediate that this file or its references name (`-fetch.html`, `-fetch.md`, `-convert.md`) is written under `$READ_ROOT` instead'; then
  pass "peek_writes_nothing: /tmp intermediates move under \$READ_ROOT in peek"
else
  fail "peek_writes_nothing: peek /tmp intermediates are not confined to \$READ_ROOT"
fi
if has "${SKILL}" '1. Read `$READ_ROOT/{slug}-convert.md` into the conversation'; then
  pass "peek_writes_nothing: Peek finish reads the scratch copy"
else
  fail "peek_writes_nothing: Peek finish reads a path outside \$READ_ROOT"
fi

# F2: lanes download images only in save mode
UNGATED=$(grep -rn 'download relevant images' "${READ_DIR}/references/acquisition" | grep -vF 'Save mode only:' || true)
if [[ -z "${UNGATED}" ]]; then
  pass "peek_writes_nothing: lane image downloads are save-mode only"
else
  fail "peek_writes_nothing: lane downloads images without a save-mode gate:"$'\n'"${UNGATED}"
fi

# F5: no lane hands off to Stage 3 / Organize unconditionally
UNCOND=$(grep -rnF 'Stage 2/3 pipeline' "${READ_DIR}/references" || true)
UNCOND+=$(grep -rn 'Organize pipeline' "${READ_DIR}/references" | grep -vF 'Organize runs in save mode only' || true)
if [[ -z "${UNCOND}" ]]; then
  pass "peek_writes_nothing: every lane hand-off is mode-aware"
else
  fail "peek_writes_nothing: lane hands off to Organize unconditionally:"$'\n'"${UNCOND}"
fi

# F3: a failed peek conversion never prints the success report
if has "${SKILL}" 'after §3 it reports exactly `{slug}: markitdown 轉換失敗（未存檔）` and nothing else for that item.' \
   && has "${SKILL}" 'in peek mode go to Peek finish §3 and close with the failure report there — never §4.'; then
  pass "peek_writes_nothing: failed peek conversion reports the failure line only"
else
  fail "peek_writes_nothing: failed peek conversion can fall through to the success report"
fi

# ---------------------------------------------------------------
# test_read_save_pipeline_unchanged
# Stage 3 §1–§7 body (heading excluded, up to ## Constraints) as shipped in 6.1.1.
# ---------------------------------------------------------------
STAGE3_SHA="23cd04ce1a5edbabf7447aba8833d50a882b4ea854b62d0e54a83dcd2a4ccedb"
ACTUAL_SHA=$(awk '/^## Stage 3 — Organize/{f=1;next} /^## Constraints/{f=0} f' "${SKILL}" | tr -d '\r' | sha256sum | awk '{print $1}')
if [[ "${ACTUAL_SHA}" == "${STAGE3_SHA}" ]]; then
  pass "save_pipeline_unchanged: Stage 3 body byte-identical to 6.1.1"
else
  fail "save_pipeline_unchanged: Stage 3 body drifted (sha ${ACTUAL_SHA})"
fi

if has "${SKILL}" '## Stage 3 — Organize (save mode only)'; then
  pass "save_pipeline_unchanged: Stage 3 gated to save mode"
else
  fail "save_pipeline_unchanged: Stage 3 heading lost its save-mode gate"
fi

if has "${SKILL}" '- **save** when the arguments contain `--save`, or the user'"'"'s request contains a save trigger: 存下來｜存檔｜離線保存｜存成離線｜保存下來｜archive.'; then
  pass "save_pipeline_unchanged: save triggers verbatim"
else
  fail "save_pipeline_unchanged: save trigger list drifted from the contract constant"
fi

# ---------------------------------------------------------------
# test_learn_calls_read_with_save
# Every backticked /read invocation in /learn must carry --save, except the
# `/read --{lane}` form, which /learn names only to say lanes do NOT call it.
# ---------------------------------------------------------------
BARE=$(grep -rnoE '`/read [^`]*`' "${LEARN_DIR}" | grep -vF -- '--save' | grep -vF -- '--{lane}' || true)
# Bare forms that hand the user (or the pipeline) a save-less /read: `/read` capture,
# `/read` route, a hint telling the user to run /read, or the → /read routing cue.
BARE+=$(grep -rnoE '`/read` (capture|route)|跑 /read」|補充 /read 資料|→ /read\)' "${LEARN_DIR}" || true)
if [[ -z "${BARE}" ]]; then
  pass "learn_calls_read_with_save: every /learn → /read call carries --save"
else
  fail "learn_calls_read_with_save: /read call without --save:"$'\n'"${BARE}"
fi

for needle in 'Call `/read --save <url>`' 'Call `/read --save --topic "keyword"`' 'Stage 1 §1 `/read --save` route' \
              '(`/read --save` capture)' '可補充 /read --save 資料後繼續。' '請嘗試其他關鍵字或手動跑 /read --save」' \
              'Not for capturing raw offline Markdown only (→ /read --save)'; do
  if has "${LEARN_DIR}/SKILL.md" "${needle}"; then
    pass "learn_calls_read_with_save: ${needle}"
  else
    fail "learn_calls_read_with_save: missing ${needle}"
  fi
done

# The /learn routing cue in the skills table and in its regeneration baseline:
# a baseline left on the old cue brings `→ /read` back the next time the table is regenerated.
for f in "${REPO_ROOT}/CLAUDE.md" "${REPO_ROOT}/tests/integration/claude-md-skills-baseline.txt"; do
  if grep -F '| `/learn` |' "${f}" | grep -qF '| 只要離線原文不要筆記 → `/read --save` |'; then
    pass "learn_calls_read_with_save: /learn routing cue carries --save in ${f##*/}"
  else
    fail "learn_calls_read_with_save: /learn routing cue lost --save in ${f##*/}"
  fi
done

# ---------------------------------------------------------------
# test_read_peek_report_format
# ---------------------------------------------------------------
REPORT=$(awk '/^4\. Report, exactly:/{f=1;next} f&&/^```$/{n++; if(n==2) exit; next} f&&n==1' "${SKILL}" | tr -d '\r')
EXPECTED=$'📄 已讀取（未存檔）：{title}\n來源：{source_url 或 local:{path}}｜{N} 字\n要存成離線檔請加 --save'
if [[ "${REPORT}" == "${EXPECTED}" ]]; then
  pass "peek_report_format: single-item report verbatim"
else
  fail "peek_report_format: single-item report drifted:"$'\n'"${REPORT}"
fi

if has "${SKILL}" '`已讀取 {N} 筆（未存檔），失敗 {M} 筆；要存成離線檔請加 --save`'; then
  pass "peek_report_format: batch report verbatim"
else
  fail "peek_report_format: batch report drifted"
fi

if has "${SKILL}" 'The report never quotes the converted body.'; then
  pass "peek_report_format: report forbids quoting the body"
else
  fail "peek_report_format: report no longer forbids quoting the body"
fi

DESC=$(awk '/^description: >/{getline; sub(/^  /,""); print; exit}' "${SKILL}" | tr -d '\r')
EXPECTED_DESC="Reads any web page, file, or search result into the conversation as clean Markdown; keeps an offline copy under .claude/read/ only with --save or an explicit save request. Use when the user wants a page, PDF, or doc fetched, read, or converted. Trigger On '/read', '抓網頁', '看一下這篇', '轉成 markdown', '存下來', '存檔'. Not For digesting into notes (/learn) or browser-ready HTML (/book)."
if [[ "${DESC}" == "${EXPECTED_DESC}" ]]; then
  pass "peek_report_format: description verbatim"
else
  fail "peek_report_format: description drifted from the contract constant"
fi
DESC_LEN=$(printf '%s' "${DESC}" | python3 -c 'import sys; print(len(sys.stdin.buffer.read().decode("utf-8")))')
if (( DESC_LEN <= 441 )); then
  pass "peek_report_format: description ${DESC_LEN} chars ≤ 441"
else
  fail "peek_report_format: description ${DESC_LEN} chars > 441"
fi

if has "${SKILL}" "argument-hint: \"[URL | path | glob | --topic 'keyword' | --web 'keyword' | --gh 'keyword' | --x 'keyword' | --chrome | --clipboard] [--save] [--use-proxy]\""; then
  pass "peek_report_format: argument-hint verbatim"
else
  fail "peek_report_format: argument-hint drifted"
fi

echo
if (( failures > 0 )); then
  echo "test-read-peek-default: ${failures} failure(s)" >&2
  exit 1
fi
echo "test-read-peek-default: all passed"
