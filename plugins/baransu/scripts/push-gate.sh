#!/usr/bin/env bash
# push-gate.sh — 5-黑閘門 deterministic 推送閘門 (TASK-enforcement-01)
#
# Inline-executes 4 gates against an auto-fix worktree before /triage emits
# `git push`. Any gate hit aborts with exit 1 and stdout `escalate=<enum>`;
# happy path exits 0.
#
# Gate order (FIXED, short-circuit on first hit):
#   3a. denylist  — 9 hardcoded glob rules vs HEAD~1..HEAD diff
#   3b. preflight — paths starting with `/` or `~/.claude/`
#   4.  attempt cap K=3 — fails-for-cluster_id in attempt_history
#   5.  daily quota=5 — state.json daily_push_count + daily_push_date
#
# CLI: push-gate.sh <cluster_id> <worktree_path> <state_json_path> <telemetry_jsonl_path>
# Exit codes:
#   0 — all gates pass (auto-fix may proceed; daily_push_count incremented)
#   1 — gate deny; stdout has `escalate=<requires_human|escalate_human|daily_quota_exceeded>`
#   2 — structural error (missing/unreadable input)
#
# This script writes ONLY the triage partition keys
# (daily_push_count / daily_push_date / last_triage_run_at).
# It MUST NOT touch grade-partition keys — read-merge-write via `jq '. + {…}'`
# preserves them byte-identical (forward-compat for unknown future keys too).
# INV-7c grep lint enforces partition isolation.
#
# Reproducibility: BARANSU_HARNESS_FAKE_NOW overrides "today" for tests.

set -uo pipefail
shopt -s globstar extglob

# ---------------------------------------------------------------------------
# Arg parse + structural validation (exit 2 on missing input)
# ---------------------------------------------------------------------------

if (( $# < 4 )); then
  echo "push-gate.sh: missing required args" >&2
  echo "usage: push-gate.sh <cluster_id> <worktree_path> <state_json_path> <telemetry_jsonl_path>" >&2
  exit 2
fi

cluster_id="$1"
worktree_path="$2"
state_json_path="$3"
telemetry_jsonl_path="$4"

if [[ ! -d "$worktree_path" ]]; then
  echo "push-gate.sh: worktree path not a directory: $worktree_path" >&2
  exit 2
fi

if [[ ! -f "$state_json_path" ]]; then
  echo "push-gate.sh: state.json not found: $state_json_path" >&2
  exit 2
fi

# Verify state.json is parseable JSON; jq exit non-zero -> structural error.
if ! jq -e . "$state_json_path" >/dev/null 2>&1; then
  echo "push-gate.sh: state.json unreadable / invalid JSON: $state_json_path" >&2
  exit 2
fi

# telemetry.jsonl: empty file is allowed (no fails); missing file is structural.
if [[ ! -f "$telemetry_jsonl_path" ]]; then
  echo "push-gate.sh: telemetry.jsonl not found: $telemetry_jsonl_path" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Gate 3a — denylist (9 hardcoded globs)
# ---------------------------------------------------------------------------
# Capture the diff. Any failure to invoke git is itself a structural error.
diff_paths_raw="$(git -C "$worktree_path" diff --name-only HEAD~1 HEAD 2>/dev/null)"
diff_rc=$?
if (( diff_rc != 0 )); then
  echo "push-gate.sh: git diff HEAD~1 HEAD failed (rc=$diff_rc) in $worktree_path" >&2
  exit 2
fi

# Iterate paths line by line. Empty diff is fine (loop body just won't run).
# We use bash extglob/globstar pattern matching via `[[ … == … ]]`.
# Glob #2/#3/#5 use ** which requires globstar (set above).
denylist_hit=""
preflight_hit=""
while IFS= read -r p; do
  [[ -z "$p" ]] && continue

  # Gate 3b is checked alongside 3a so both lists are scanned in a single
  # pass, but 3a takes priority — we only set preflight_hit when no
  # denylist match was found for this path.
  if [[ "$p" == .github/** ]] \
     || [[ "$p" == **/plugin.json ]] \
     || [[ "$p" == **/marketplace.json ]] \
     || [[ "$p" == .gitignore ]] || [[ "$p" == **/.gitignore ]] \
     || [[ "$p" == **/scripts/** ]] \
     || [[ "$p" == plugins/baransu/hooks/** ]] \
     || [[ "$p" == plugins/baransu/agents/** ]] \
     || [[ "$p" == .git/** ]] \
     || [[ "$p" == .claude/settings*.json ]] || [[ "$p" == **/.claude/settings*.json ]]; then
    denylist_hit="$p"
    break
  fi

  # Gate 3b — absolute-path preflight (record but continue scanning so
  # denylist still gets a chance on later paths). However, since 3a
  # short-circuits before 3b, we only act on preflight after the denylist
  # loop confirms no hit.
  if [[ -z "$preflight_hit" ]]; then
    if [[ "$p" == /* ]] || [[ "$p" == "~/.claude/"* ]] || [[ "$p" == "~/.claude/" ]]; then
      preflight_hit="$p"
    fi
  fi
done <<< "$diff_paths_raw"

if [[ -n "$denylist_hit" ]]; then
  echo "escalate=requires_human"
  echo "denylist hit: $denylist_hit" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Gate 3b — absolute-path preflight
# ---------------------------------------------------------------------------
if [[ -n "$preflight_hit" ]]; then
  echo "escalate=requires_human"
  echo "preflight hit: $preflight_hit" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Gate 4 — attempt cap K=3
# Count attempt_history entries with cluster_id == $cluster_id AND result == "fail"
# across all telemetry rows.
# ---------------------------------------------------------------------------
fail_count=0
if [[ -s "$telemetry_jsonl_path" ]]; then
  fail_count="$(jq -s --arg c "$cluster_id" \
    'map(.attempt_history[]? | select(.cluster_id == $c and .result == "fail")) | length' \
    "$telemetry_jsonl_path" 2>/dev/null)"
  if [[ -z "$fail_count" || ! "$fail_count" =~ ^[0-9]+$ ]]; then
    echo "push-gate.sh: telemetry.jsonl unreadable / invalid: $telemetry_jsonl_path" >&2
    exit 2
  fi
fi

if (( fail_count >= 3 )); then
  echo "escalate=escalate_human"
  echo "attempt cap hit: cluster=$cluster_id fail_count=$fail_count" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Gate 5 — daily quota=5
# Read state.json; if date != today, reset count=0+date=today (read-merge-write
# atomic via `jq '. + {…}'` to preserve unknown keys); else if count >= 5 abort.
# Happy path: increment count, write last_triage_run_at, write back.
# ---------------------------------------------------------------------------
if [[ -n "${BARANSU_HARNESS_FAKE_NOW:-}" ]]; then
  today="$BARANSU_HARNESS_FAKE_NOW"
else
  today="$(date +%Y-%m-%d)"
fi

stored_date="$(jq -r '.daily_push_date // ""' "$state_json_path")"
stored_count="$(jq -r '.daily_push_count // 0' "$state_json_path")"

if [[ "$stored_date" != "$today" ]]; then
  # Reset path: write count=0, date=today, but preserve all other keys
  # (including the entire grade partition) byte-identical.
  tmp_state="${state_json_path}.tmp.$$"
  jq --arg today "$today" \
    '. + {daily_push_count: 0, daily_push_date: $today}' \
    "$state_json_path" >"$tmp_state" || {
      rm -f "$tmp_state"
      echo "push-gate.sh: failed to rewrite state.json (reset path)" >&2
      exit 2
    }
  mv "$tmp_state" "$state_json_path"
  stored_count=0
fi

if (( stored_count >= 5 )); then
  echo "escalate=daily_quota_exceeded"
  echo "daily quota hit: count=$stored_count today=$today" >&2
  exit 1
fi

# Happy path: increment count, stamp last_triage_run_at, write back.
new_count=$((stored_count + 1))
now_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
tmp_state="${state_json_path}.tmp.$$"
jq --argjson n "$new_count" --arg today "$today" --arg ts "$now_iso" \
  '. + {daily_push_count: $n, daily_push_date: $today, last_triage_run_at: $ts}' \
  "$state_json_path" >"$tmp_state" || {
    rm -f "$tmp_state"
    echo "push-gate.sh: failed to rewrite state.json (happy path)" >&2
    exit 2
  }
mv "$tmp_state" "$state_json_path"

exit 0
