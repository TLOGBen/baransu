#!/usr/bin/env bash
# bridge-replay — /baransu:bridge skill execution carrier.
#
# Compares two skill versions (v1 = main HEAD, v2 = target branch HEAD)
# head-to-head against a corpus of historical prompts pulled from
# .claude/harness/telemetry.jsonl (terminal_state == "completed"). Both
# versions are scored with the same 5-dim rubric (reused via grade-collector;
# scoring itself is delegated to a SKILL_RUNNER seam so the heavy invocation
# can be swapped for tests). Aggregate Δ = score_v2 - score_v1; the gate
# decides pass / fail / inconclusive.
#
# Spec trace: REQ-005 Scenarios 1-4, INT-8, INT-9a, INT-9b, KD#3, KD#4, KD#6.
#
# Behaviour:
#   * Worktree lives under `mktemp -d /tmp/baransu-bridge-XXXXXX` — never
#     inside the main repo working tree.
#   * `trap cleanup EXIT INT TERM` performs `git worktree remove --force`
#     plus `rm -rf` on the tmpdir. SIGINT and normal EXIT share the same
#     code path (per ctx.md constraint).
#   * Δ ≤ -0.15 → fail (exit 1) + print top-N degraded prompts.
#   * |Δ| < 0.15 → pass (exit 0).
#   * corpus < N → inconclusive (exit 2). Trap still cleans the worktree
#     even if it was never created.
#   * Trust check: target branch tip commit author email must match
#     `git config user.email` unless `--allow-untrusted` is given.
#
# Test seam: env var SKILL_RUNNER points to a command. The script invokes
#   "$SKILL_RUNNER <version> <prompt_text>"
# and parses a single float from stdout as the score. Default runner is the
# placeholder `bridge-default-runner` which exits non-zero (real wiring is
# beyond this task's scope; only the seam contract is locked here).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------

target_branch=""
skill_name=""
corpus_size=50
allow_untrusted=0

usage() {
  cat <<'USAGE'
Usage: bridge-replay.sh --target-branch <branch> --skill <name>
                        [--corpus-size N] [--allow-untrusted]

  --target-branch <branch>  Target branch (v2) to head-to-head against current main HEAD (v1).
  --skill <name>            Skill name to score (passed to SKILL_RUNNER).
  --corpus-size N           Minimum corpus rows for a conclusive run (default 50).
  --allow-untrusted         Skip trust check (target branch author != user.email).

Env:
  SKILL_RUNNER              Override the skill scoring command (test seam).

Exit codes:
  0  pass
  1  fail (Δ ≤ -0.15)
  2  inconclusive (corpus < N) or other refusal
  >2 setup / git error
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-branch) target_branch="${2:-}"; shift 2 ;;
    --skill)         skill_name="${2:-}"; shift 2 ;;
    --corpus-size)   corpus_size="${2:-}"; shift 2 ;;
    --allow-untrusted) allow_untrusted=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown flag: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$target_branch" ]] || { echo "missing --target-branch" >&2; exit 2; }
[[ -n "$skill_name"    ]] || { echo "missing --skill"         >&2; exit 2; }

# ---------------------------------------------------------------------------
# Trap & cleanup (Stage 0 — register before any side effect)
# ---------------------------------------------------------------------------

tmpdir=""
report_path=""
final_exit=0

cleanup() {
  local code=$?
  # Allow override: subcommands that completed normally already set
  # `final_exit` via `exit_with`. If we're here from EXIT after a successful
  # `exit N`, $? is N. From INT/TERM, $? is 130/143; we want non-zero.
  if [[ -n "$tmpdir" && -d "$tmpdir" ]]; then
    git worktree remove --force "$tmpdir" >/dev/null 2>&1 || true
    rm -rf "$tmpdir"
  fi
  trap - EXIT INT TERM
  exit "$code"
}
trap cleanup EXIT INT TERM

die() {
  echo "$*" >&2
  exit "${2:-2}"
}

# ---------------------------------------------------------------------------
# Stage 0a — corpus check (must come before worktree creation; INT-9b path
# exits here without ever creating a worktree, but trap still runs).
# ---------------------------------------------------------------------------

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$repo_root" ]] || die "not inside a git repo" 3

telemetry="$repo_root/.claude/harness/telemetry.jsonl"
prompts_file="$(mktemp -t bridge-prompts.XXXXXX)"
trap_extra() { rm -f "$prompts_file"; }

# Extract completed prompts (one JSON-encoded prompt_text per line).
if [[ -f "$telemetry" ]]; then
  jq -r 'select(.terminal_state == "completed") | .prompt_text' \
     "$telemetry" >"$prompts_file" || true
fi

prompts_count=$(wc -l <"$prompts_file" | tr -d ' ')
prompts_count=${prompts_count:-0}

if (( prompts_count < corpus_size )); then
  echo "inconclusive: corpus=${prompts_count} < required=${corpus_size}" >&2
  echo "  refusing to declare pass/fail with insufficient sample." >&2
  rm -f "$prompts_file"
  exit 2
fi

# ---------------------------------------------------------------------------
# Stage 0b — trust check (REQ-005 / S-F3 RCE guard).
# ---------------------------------------------------------------------------

if (( allow_untrusted == 0 )); then
  user_email="$(git -C "$repo_root" config user.email 2>/dev/null || true)"
  branch_email="$(git -C "$repo_root" log -1 --format='%ae' "$target_branch" 2>/dev/null || true)"
  if [[ -z "$branch_email" ]]; then
    rm -f "$prompts_file"
    die "trust check: cannot read author email for $target_branch" 4
  fi
  if [[ "$user_email" != "$branch_email" ]]; then
    rm -f "$prompts_file"
    die "trust check: target branch author '$branch_email' != user.email '$user_email'. Pass --allow-untrusted to override." 5
  fi
fi

# ---------------------------------------------------------------------------
# Stage 1 — worktree setup.
# ---------------------------------------------------------------------------

tmpdir="$(mktemp -d /tmp/baransu-bridge-XXXXXX)"
git -C "$repo_root" worktree add --quiet "$tmpdir" "$target_branch" >/dev/null 2>&1 || {
  rm -f "$prompts_file"
  die "git worktree add failed for $target_branch -> $tmpdir" 6
}

# ---------------------------------------------------------------------------
# Stage 2 — per-run report file.
# ---------------------------------------------------------------------------

ts="$(date -u +%Y%m%dT%H%M%SZ)"
safe_branch="$(printf '%s' "$target_branch" | tr '/' '-')"
report_path="$repo_root/.claude/harness/bridge-runs/bridge-${ts}-${safe_branch}.jsonl"
mkdir -p "$(dirname "$report_path")"

# ---------------------------------------------------------------------------
# Stage 3 — replay loop.
# ---------------------------------------------------------------------------

skill_runner="${SKILL_RUNNER:-${SCRIPT_DIR}/bridge-default-runner.sh}"

scores_v1=()
scores_v2=()
prompt_texts=()

while IFS= read -r prompt; do
  [[ -z "$prompt" ]] && continue
  # v1 score from main HEAD context — runner takes "v1 <prompt>".
  s1="$("$skill_runner" v1 "$prompt" 2>/dev/null || echo "")"
  s2="$("$skill_runner" v2 "$prompt" 2>/dev/null || echo "")"
  if [[ -z "$s1" || -z "$s2" ]]; then
    echo "warning: skill runner returned empty for prompt; skipping" >&2
    continue
  fi
  scores_v1+=("$s1")
  scores_v2+=("$s2")
  prompt_texts+=("$prompt")
done <"$prompts_file"

rm -f "$prompts_file"

n=${#scores_v1[@]}
if (( n < corpus_size )); then
  echo "inconclusive: usable scores=${n} < required=${corpus_size}" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Stage 4 — statistical gate (delegate to python helper for stable math).
# ---------------------------------------------------------------------------
#
# The math is intentionally simple (sum / mean / sort by per-prompt Δ), but
# python is more robust than bash for floats. We pipe NUL-separated triples
# (prompt, v1_score, v2_score) into a python -c heredoc.

# Build NUL-separated stream.
gate_input="$(mktemp -t bridge-gate.XXXXXX)"
{
  for ((i = 0; i < n; i++)); do
    printf '%s\t%s\t%s\n' "${prompt_texts[i]}" "${scores_v1[i]}" "${scores_v2[i]}"
  done
} >"$gate_input"

GATE_THRESHOLD=0.15 \
GATE_TS="$ts" \
GATE_TARGET="$target_branch" \
GATE_SKILL="$skill_name" \
GATE_CORPUS="$corpus_size" \
GATE_REPORT="$report_path" \
python3 - "$gate_input" <<'PY'
import json
import os
import sys

threshold = float(os.environ["GATE_THRESHOLD"])
ts = os.environ["GATE_TS"]
target = os.environ["GATE_TARGET"]
skill = os.environ["GATE_SKILL"]
corpus = int(os.environ["GATE_CORPUS"])
report_path = os.environ["GATE_REPORT"]

rows = []
with open(sys.argv[1], "r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        prompt, s1, s2 = line.split("\t", 2)
        try:
            v1 = float(s1)
            v2 = float(s2)
        except ValueError:
            continue
        rows.append({"prompt": prompt, "v1": v1, "v2": v2, "delta": v2 - v1})

n = len(rows)
mean_v1 = sum(r["v1"] for r in rows) / n
mean_v2 = sum(r["v2"] for r in rows) / n
agg_delta = mean_v2 - mean_v1

# Decision (signed Δ; design.md flow 2 step 8):
#   Δ ≤ -threshold → fail
#   else           → pass
if agg_delta <= -threshold:
    verdict = "fail"
elif agg_delta >= threshold:
    # v2 strictly better than v1 by >= threshold — still a pass but worth flagging.
    verdict = "pass"
else:
    verdict = "pass"

# top-N degraded prompts: most negative per-prompt Δ first.
worst = sorted(rows, key=lambda r: r["delta"])[:5]

# Stdout report (deterministic ordering).
print(f"[bridge] verdict={verdict} target={target} skill={skill} corpus={n}/{corpus}")
print(f"[bridge] mean_v1={mean_v1:.4f} mean_v2={mean_v2:.4f} aggregate_delta={agg_delta:+.4f} threshold=±{threshold}")
if verdict == "fail":
    print("[bridge] top-5 degraded prompts (most negative Δ first):")
    for i, r in enumerate(worst, 1):
        print(f"  {i}. Δ={r['delta']:+.4f}  v1={r['v1']:.4f}  v2={r['v2']:.4f}  prompt={r['prompt']!r}")
    print("[bridge] do NOT promote — investigate regression cohort.")
else:
    print("[bridge] no statistical regression; promote candidate is eligible.")

# Write per-run report.
report = {
    "started_at": ts,
    "target_branch": target,
    "skill": skill,
    "corpus_size_required": corpus,
    "corpus_size_used": n,
    "threshold": threshold,
    "mean_v1": mean_v1,
    "mean_v2": mean_v2,
    "aggregate_delta": agg_delta,
    "verdict": verdict,
    "rows": rows,
    "top_n_degraded": worst,
}
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(report, ensure_ascii=False, sort_keys=True))
    f.write("\n")

# Exit code: pass=0, fail=1.
sys.exit(0 if verdict == "pass" else 1)
PY

gate_rc=$?
rm -f "$gate_input"
exit "$gate_rc"
