#!/usr/bin/env bash
# check-invariants.sh — verify the 6 KD invariants, 5 auto-fix safety
# edges, and 3 INV-7 partition lint sub-checks declared by the self-healing
# harness spec (REQ-005 / REQ-006 / INV-1..7).
#
# Output: exactly 14 lines, one per invariant + edge + INV-7 sub-check:
#   PASS|FAIL: INV-1 <description>
#   PASS|FAIL: INV-2 <description>
#   PASS|FAIL: INV-3 <description>
#   PASS|FAIL: INV-4 <description>
#   PASS|FAIL: INV-5 <description>
#   PASS|FAIL: INV-6 <description>
#   PASS|FAIL: EDGE-1 <description>
#   PASS|FAIL: EDGE-2 <description>
#   PASS|FAIL: EDGE-3 <description>
#   PASS|FAIL: EDGE-4 <description>
#   PASS|FAIL: EDGE-5 <description>
#   PASS|FAIL: INV-7a <description>
#   PASS|FAIL: INV-7b <description>
#   PASS|FAIL: INV-7c <description>
# Followed by a one-line summary.
#
# Exit codes:
#   0 — all 14 PASS
#   1 — at least one FAIL
#   2 — structural error (missing required tool / file)
#
# Read-only diagnostic — does NOT modify any file. Idempotent; safe for
# cron / CI / manual invocation.
#
# Configurable inputs (env vars):
#   BARANSU_ROOT              — repo root (default: `git rev-parse --show-toplevel`)
#   BARANSU_USER_SETTINGS     — path to user-level settings.json
#                               (default: `$HOME/.claude/settings.json`)
#                               Note: this file is host-level, not under
#                               BARANSU_ROOT, so it is checked separately.
#
# Manual smoke test (negative case — invariant deliberately broken):
#   1. Edit .gitignore and remove the `.claude/harness/` line.
#   2. Run this script — expect `FAIL: EDGE-1 ...` + exit 1.
#   3. Restore the line; re-run — expect all 14 PASS + exit 0.

# Note: NOT using `set -e` — we want every check to run even if earlier
# checks emit non-zero exits. We do use `set -u` for undefined-var safety.
set -u
set -o pipefail

# ------------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------------
if [ -z "${BARANSU_ROOT:-}" ]; then
  if BARANSU_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
    :
  else
    echo "ERROR: BARANSU_ROOT not set and not inside a git repo" >&2
    exit 2
  fi
fi

USER_SETTINGS="${BARANSU_USER_SETTINGS:-$HOME/.claude/settings.json}"

# Required tools.
for tool in jq grep find; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "ERROR: required tool '$tool' not found in PATH" >&2
    exit 2
  fi
done

PASS_COUNT=0
FAIL_COUNT=0

report() {
  # report PASS|FAIL ID description
  local status=$1
  local id=$2
  local msg=$3
  echo "${status}: ${id} ${msg}"
  if [ "$status" = "PASS" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# ------------------------------------------------------------------------
# INV-1 — hooks registered at user-level, NOT in plugin.json
#
#   Sub-asserts (all must hold):
#     1a. ~/.claude/settings.json exists and contains UserPromptSubmit.
#     1b. ~/.claude/settings.json contains PostToolUse.
#     1c. plugin.json contains no `"hooks"` field (grep miss).
# ------------------------------------------------------------------------
check_inv1() {
  local plugin_json="$BARANSU_ROOT/plugins/baransu/.claude-plugin/plugin.json"
  if [ ! -f "$USER_SETTINGS" ]; then
    report FAIL "INV-1" "user settings.json missing at $USER_SETTINGS"
    return
  fi
  if [ ! -f "$plugin_json" ]; then
    report FAIL "INV-1" "plugin.json missing at $plugin_json"
    return
  fi
  if ! jq -e '.hooks.UserPromptSubmit' "$USER_SETTINGS" >/dev/null 2>&1; then
    report FAIL "INV-1" "UserPromptSubmit hook not registered in user settings.json"
    return
  fi
  if ! jq -e '.hooks.PostToolUse' "$USER_SETTINGS" >/dev/null 2>&1; then
    report FAIL "INV-1" "PostToolUse hook not registered in user settings.json"
    return
  fi
  if grep -qF '"hooks"' "$plugin_json"; then
    report FAIL "INV-1" "plugin.json contains forbidden \"hooks\" field"
    return
  fi
  report PASS "INV-1" "hooks registered at user-level only (UserPromptSubmit + PostToolUse); plugin.json has no hooks field"
}

# ------------------------------------------------------------------------
# INV-2 — total skill count = 14 (11 existing + 3 new).
#
#   Sub-asserts:
#     2a. plugins/baransu/skills/ has 14 first-level dirs (excluding _shared).
#     2b. CLAUDE.md skill table has 14 rows starting with `| \`/`.
# ------------------------------------------------------------------------
check_inv2() {
  local skills_dir="$BARANSU_ROOT/plugins/baransu/skills"
  local claude_md="$BARANSU_ROOT/CLAUDE.md"
  if [ ! -d "$skills_dir" ]; then
    report FAIL "INV-2" "skills directory missing at $skills_dir"
    return
  fi
  if [ ! -f "$claude_md" ]; then
    report FAIL "INV-2" "CLAUDE.md missing at $claude_md"
    return
  fi
  # Count user-facing skill dirs (exclude _shared meta-dir).
  local dir_count
  dir_count=$(find "$skills_dir" -mindepth 1 -maxdepth 1 -type d \
                ! -name '_shared' | wc -l | tr -d ' ')
  if [ "$dir_count" -ne 14 ]; then
    report FAIL "INV-2" "skills/ has $dir_count user-facing dirs (expected 14)"
    return
  fi
  local row_count
  row_count=$(grep -cE '^\| `/' "$claude_md" || true)
  if [ "$row_count" -ne 14 ]; then
    report FAIL "INV-2" "CLAUDE.md skill table has $row_count rows (expected 14)"
    return
  fi
  report PASS "INV-2" "14 skill directories and 14 CLAUDE.md table rows"
}

# ------------------------------------------------------------------------
# INV-3 — telemetry.jsonl row has 7 expected top-level keys.
#
#   Pre-condition handling: telemetry.jsonl lives under `.claude/harness/`,
#   which is gitignored — a fresh worktree or CI checkout will not have
#   it. Per ctx.md spec the implementation may treat absent/empty file
#   as vacuously true (no rows ⇒ no rows to violate the schema). We
#   report PASS with an explicit "no rows yet" note in that case so the
#   summary stays at 11 PASS for a green tree.
# ------------------------------------------------------------------------
check_inv3() {
  local telemetry="$BARANSU_ROOT/.claude/harness/telemetry.jsonl"
  if [ ! -s "$telemetry" ]; then
    report PASS "INV-3" "telemetry.jsonl absent or empty at $telemetry — vacuously true (no rows to violate schema)"
    return
  fi
  if ! tail -1 "$telemetry" \
       | jq -e 'has("session_id") and has("terminal_state")
                and has("prompt_text") and has("skill_outcome")
                and has("commit_hash") and has("diff_summary_redacted")
                and has("attempt_history")' >/dev/null 2>&1; then
    report FAIL "INV-3" "telemetry.jsonl tail row missing one or more of 7 expected keys"
    return
  fi
  report PASS "INV-3" "telemetry.jsonl tail row has all 7 expected keys"
}

# ------------------------------------------------------------------------
# INV-4 — rubric is equal-weight bootstrap (1/5 each, 5 dims) +
#         tune trigger ≥ 50 documented.
#
#   Sub-asserts:
#     4a. grade-collector.py grep `1/5` or `0.2` or `equal_weight`.
#     4b. all 5 dim names appear in grade-triage-schema.md.
#     4c. /grade SKILL.md mentions `>= 50` or `≥ 50` tune trigger.
# ------------------------------------------------------------------------
check_inv4() {
  local collector="$BARANSU_ROOT/plugins/baransu/scripts/grade-collector.py"
  local schema="$BARANSU_ROOT/plugins/baransu/skills/_shared/grade-triage-schema.md"
  local grade_skill="$BARANSU_ROOT/plugins/baransu/skills/grade/SKILL.md"
  if [ ! -f "$collector" ]; then
    report FAIL "INV-4" "grade-collector.py missing at $collector"
    return
  fi
  if [ ! -f "$schema" ]; then
    report FAIL "INV-4" "grade-triage-schema.md missing at $schema"
    return
  fi
  if [ ! -f "$grade_skill" ]; then
    report FAIL "INV-4" "/grade SKILL.md missing at $grade_skill"
    return
  fi
  if ! grep -qE '1/5|0\.2|equal[_ -]weight|equal weight' "$collector"; then
    report FAIL "INV-4" "grade-collector.py lacks equal-weight literal (1/5 / 0.2 / equal_weight)"
    return
  fi
  for dim in outcome_quality iteration_velocity scope_blast \
             human_override_rate failure_recurrence; do
    if ! grep -qF "$dim" "$schema"; then
      report FAIL "INV-4" "rubric dim '$dim' not found in grade-triage-schema.md"
      return
    fi
  done
  if ! grep -qE '>= 50|≥ 50' "$grade_skill"; then
    report FAIL "INV-4" "/grade SKILL.md lacks tune trigger '>= 50' or '≥ 50'"
    return
  fi
  report PASS "INV-4" "equal-weight bootstrap (1/5 each, 5 dims) + tune trigger ≥ 50 documented"
}

# ------------------------------------------------------------------------
# INV-5 — auto-fix isolated worktree (mktemp + main repo never touched).
#
#   Sub-asserts (grep-based per ctx.md spec — dry-run mock not feasible
#   inside read-only diagnostic):
#     5a. /triage SKILL.md grep `mktemp` (worktree creation).
#     5b. /triage SKILL.md grep `baransu-harness` (namespace).
#     5c. /triage SKILL.md grep `主 repo working tree` 或 `never touch`
#         語意（中文「永不被 touch」或英文 "never touched"）.
# ------------------------------------------------------------------------
check_inv5() {
  local triage_skill="$BARANSU_ROOT/plugins/baransu/skills/triage/SKILL.md"
  if [ ! -f "$triage_skill" ]; then
    report FAIL "INV-5" "/triage SKILL.md missing at $triage_skill"
    return
  fi
  if ! grep -qF 'mktemp' "$triage_skill"; then
    report FAIL "INV-5" "/triage SKILL.md lacks mktemp pattern (auto-fix worktree)"
    return
  fi
  if ! grep -qF 'baransu-harness' "$triage_skill"; then
    report FAIL "INV-5" "/triage SKILL.md lacks baransu-harness namespace"
    return
  fi
  if ! grep -qE '主 repo working tree.*(永不|不被)|never touch' "$triage_skill"; then
    report FAIL "INV-5" "/triage SKILL.md lacks 'main repo working tree never touched' assertion"
    return
  fi
  report PASS "INV-5" "auto-fix isolated worktree documented (mktemp + baransu-harness + main repo never touched)"
}

# ------------------------------------------------------------------------
# INV-6 — five safety boundaries (EDGE-1..5) framing exists.
#
# This invariant is an umbrella over EDGE-1..5; the granular checks live
# in check_edge_*. INV-6 confirms the high-level framing exists in
# /triage SKILL.md (the doc that describes the auto-fix pipeline). We
# look for either:
#   - the `5-black` / `5 黑` / `KD#5` framing string, OR
#   - at least the 3 push-gate edges /triage owns (EDGE-3, EDGE-4, EDGE-5).
# Removing the framing or any of the three push-gate edges would trip
# this check.
# ------------------------------------------------------------------------
check_inv6() {
  local triage_skill="$BARANSU_ROOT/plugins/baransu/skills/triage/SKILL.md"
  if [ ! -f "$triage_skill" ]; then
    report FAIL "INV-6" "/triage SKILL.md missing at $triage_skill"
    return
  fi
  if ! grep -qE '5-black|5 黑|KD#5' "$triage_skill"; then
    report FAIL "INV-6" "/triage SKILL.md lacks 5-black / 5 黑 / KD#5 framing"
    return
  fi
  for n in 3 4 5; do
    if ! grep -qE "EDGE-$n" "$triage_skill"; then
      report FAIL "INV-6" "/triage SKILL.md missing EDGE-$n push-gate reference"
      return
    fi
  done
  report PASS "INV-6" "/triage SKILL.md frames 5-black safety boundaries with EDGE-3/4/5 push gates"
}

# ------------------------------------------------------------------------
# EDGE-1 — .gitignore contains `.claude/harness/`.
# ------------------------------------------------------------------------
check_edge1() {
  local gi="$BARANSU_ROOT/.gitignore"
  if [ ! -f "$gi" ]; then
    report FAIL "EDGE-1" ".gitignore missing at $gi"
    return
  fi
  if ! grep -qF '.claude/harness/' "$gi"; then
    report FAIL "EDGE-1" ".gitignore lacks '.claude/harness/' rule"
    return
  fi
  report PASS "EDGE-1" ".gitignore contains '.claude/harness/' rule"
}

# ------------------------------------------------------------------------
# EDGE-2 — PostToolUse hook redaction list covers 5 path patterns.
# ------------------------------------------------------------------------
check_edge2() {
  local hook="$BARANSU_ROOT/plugins/baransu/hooks/post-tool-use.py"
  if [ ! -f "$hook" ]; then
    report FAIL "EDGE-2" "post-tool-use.py missing at $hook"
    return
  fi
  local missing=""
  for pat in '.env' 'secret' 'credential' '.pem' '.key'; do
    if ! grep -qF "$pat" "$hook"; then
      missing="${missing} $pat"
    fi
  done
  if [ -n "$missing" ]; then
    report FAIL "EDGE-2" "post-tool-use.py redaction missing patterns:$missing"
    return
  fi
  report PASS "EDGE-2" "post-tool-use.py redaction covers 5 patterns (.env, secret, credential, .pem, .key)"
}

# ------------------------------------------------------------------------
# EDGE-3 — /triage push denylist covers 5 paths.
#
# Note: the authoritative location of the 5 denylist literals moved from
# `/triage SKILL.md` to `plugins/baransu/scripts/push-gate.sh` when the
# enforcement layer landed (TASK-enforcement-01 / commit bcaedde). The
# SKILL.md now defers to push-gate.sh for the literal list. We grep the
# script directly so the check tracks the actual source of truth.
# ------------------------------------------------------------------------
check_edge3() {
  local push_gate="$BARANSU_ROOT/plugins/baransu/scripts/push-gate.sh"
  if [ ! -f "$push_gate" ]; then
    report FAIL "EDGE-3" "push-gate.sh missing at $push_gate"
    return
  fi
  local missing=""
  for pat in '.github/' 'plugin.json' 'marketplace.json' '.gitignore' 'scripts/'; do
    if ! grep -qF "$pat" "$push_gate"; then
      missing="${missing} $pat"
    fi
  done
  if [ -n "$missing" ]; then
    report FAIL "EDGE-3" "push-gate.sh denylist missing paths:$missing"
    return
  fi
  report PASS "EDGE-3" "push-gate.sh push denylist covers 5 paths (.github/, plugin.json, marketplace.json, .gitignore, scripts/)"
}

# ------------------------------------------------------------------------
# EDGE-4 — attempt cap K=3 + attempt_history documented in /triage.
# ------------------------------------------------------------------------
check_edge4() {
  local triage_skill="$BARANSU_ROOT/plugins/baransu/skills/triage/SKILL.md"
  if [ ! -f "$triage_skill" ]; then
    report FAIL "EDGE-4" "/triage SKILL.md missing at $triage_skill"
    return
  fi
  if ! grep -qE 'K=3|attempt cap.*3|cap \(K=3\)' "$triage_skill"; then
    report FAIL "EDGE-4" "/triage SKILL.md lacks attempt cap K=3 declaration"
    return
  fi
  if ! grep -qF 'attempt_history' "$triage_skill"; then
    report FAIL "EDGE-4" "/triage SKILL.md lacks attempt_history reference"
    return
  fi
  report PASS "EDGE-4" "/triage SKILL.md declares attempt cap K=3 with attempt_history accumulation"
}

# ------------------------------------------------------------------------
# EDGE-5 — daily push quota = 5 documented in /triage SKILL.md AND
#          in state-json-schema.md.
# ------------------------------------------------------------------------
check_edge5() {
  local triage_skill="$BARANSU_ROOT/plugins/baransu/skills/triage/SKILL.md"
  local state_schema="$BARANSU_ROOT/plugins/baransu/skills/_shared/state-json-schema.md"
  if [ ! -f "$triage_skill" ]; then
    report FAIL "EDGE-5" "/triage SKILL.md missing at $triage_skill"
    return
  fi
  if [ ! -f "$state_schema" ]; then
    report FAIL "EDGE-5" "state-json-schema.md missing at $state_schema"
    return
  fi
  if ! grep -qE 'daily_push.*5|daily quota.*5|daily push quota.*5' "$triage_skill"; then
    report FAIL "EDGE-5" "/triage SKILL.md lacks daily quota = 5 declaration"
    return
  fi
  if ! grep -qE 'daily quota = 5|daily_push_count >= 5|quota = 5' "$state_schema"; then
    report FAIL "EDGE-5" "state-json-schema.md lacks daily quota = 5 declaration"
    return
  fi
  report PASS "EDGE-5" "daily push quota = 5 declared in /triage SKILL.md and state-json-schema.md"
}

# ------------------------------------------------------------------------
# INV-7 — state.json partition contract (REQ-005).
#
# Three sub-checks (a/b/c) verify the explicit partition rule:
#   grade owns:  last_grade_run_at, cumulative_completed_count, tune_review_due_since
#   triage owns: daily_push_count, daily_push_date, last_triage_run_at
#
# - INV-7a: schema doc carries both `grade owns` and `triage owns` literals.
# - INV-7b: grade-collector.py does NOT mutate any triage-partition key.
#           Stricter regex matches subscript assignment form (e.g.
#           `state["daily_push_count"] = X`) but NOT dict-literal references
#           or frozenset references that legitimately name those keys.
# - INV-7c: push-gate.sh does NOT mutate any grade-partition key. Matches
#           jq-style `.last_grade_run_at = "..."` and shell variable
#           `.last_grade_run_at=...` patterns; pure read access (`.X` with
#           no `=`) is fine.
#
# Cross-partition writes are forbidden (KD#1 + REQ-005). This grep lint
# catches violations; CI / cron rejects on exit non-zero.
# ------------------------------------------------------------------------
check_inv7a() {
  local schema="$BARANSU_ROOT/plugins/baransu/skills/_shared/state-json-schema.md"
  if [ ! -f "$schema" ]; then
    report FAIL "INV-7a" "state-json-schema.md missing at $schema"
    return
  fi
  if ! grep -qF 'grade owns' "$schema"; then
    report FAIL "INV-7a" "state-json-schema.md lacks 'grade owns' partition literal"
    return
  fi
  if ! grep -qF 'triage owns' "$schema"; then
    report FAIL "INV-7a" "state-json-schema.md lacks 'triage owns' partition literal"
    return
  fi
  report PASS "INV-7a" "state-json-schema.md declares partition table ('grade owns' + 'triage owns')"
}

check_inv7b() {
  local collector="$BARANSU_ROOT/plugins/baransu/scripts/grade-collector.py"
  if [ ! -f "$collector" ]; then
    report FAIL "INV-7b" "grade-collector.py missing at $collector"
    return
  fi
  # Stricter regex: subscript assignment form only. Matches
  #   state["daily_push_count"] = 0
  # but NOT dict-literal references like `"daily_push_count": 0`
  # nor frozenset references like `{"daily_push_count", ...}`.
  if grep -qE '\[[[:space:]]*["'"'"'](daily_push_count|daily_push_date|last_triage_run_at)["'"'"'][[:space:]]*\][[:space:]]*=' "$collector"; then
    local hit
    hit=$(grep -nE '\[[[:space:]]*["'"'"'](daily_push_count|daily_push_date|last_triage_run_at)["'"'"'][[:space:]]*\][[:space:]]*=' "$collector" | head -1)
    report FAIL "INV-7b" "grade-collector.py mutates triage-partition key (cross-partition write): $hit"
    return
  fi
  report PASS "INV-7b" "grade-collector.py does not mutate triage-partition keys"
}

check_inv7c() {
  local push_gate="$BARANSU_ROOT/plugins/baransu/scripts/push-gate.sh"
  if [ ! -f "$push_gate" ]; then
    report FAIL "INV-7c" "push-gate.sh missing at $push_gate"
    return
  fi
  # Match jq-style mutation `.last_grade_run_at = "..."` (with optional
  # whitespace before `=`). Pure read access `.X` (no `=`) is allowed.
  if grep -qE '\.(last_grade_run_at|cumulative_completed_count|tune_review_due_since)[[:space:]]*=' "$push_gate"; then
    local hit
    hit=$(grep -nE '\.(last_grade_run_at|cumulative_completed_count|tune_review_due_since)[[:space:]]*=' "$push_gate" | head -1)
    report FAIL "INV-7c" "push-gate.sh mutates grade-partition key (cross-partition write): $hit"
    return
  fi
  report PASS "INV-7c" "push-gate.sh does not mutate grade-partition keys"
}

# ------------------------------------------------------------------------
# Run all 14 checks (deterministic order — INV-1..6, EDGE-1..5, INV-7a..c).
# ------------------------------------------------------------------------
check_inv1
check_inv2
check_inv3
check_inv4
check_inv5
check_inv6
check_edge1
check_edge2
check_edge3
check_edge4
check_edge5
check_inv7a
check_inv7b
check_inv7c

echo
echo "Summary: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL (expected 14 PASS)"

if [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi
exit 0
