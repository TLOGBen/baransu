#!/usr/bin/env bash
# seal-guard — Stop hook: block session stop when a user-facing surface was
# touched this session and no /baransu:seal record exists.
#
# Default mode is BLOCKING (user decision 2026-07-19, KD5 mechanism anchor).
# Degrade switches (env):
#   SEAL_GUARD=log   → detect + append telemetry, never block
#   SEAL_GUARD=off   → detect + append telemetry, never block, fully silent
# Telemetry (.claude/harness/seal-guard.jsonl) is appended in EVERY mode so the
# monthly review keeps its miss-rate data even when blocking is degraded.
#
# Exit contract: 0 = allow stop; 2 = block stop (stderr fed back to Claude).
# Any detection failure degrades to exit 0 — a heuristic guard must never wedge
# a session on its own bugs. False blocks are the expensive failure mode here;
# the surface heuristic is deliberately conservative (misses acceptable).
set -u

# --- loop protection (official Stop-hook contract) -------------------------
# stdin JSON carries `stop_hook_active: true` when Claude Code is already
# continuing as a result of a stop hook. Blocking again would loop; exit 0.
# (Claude Code additionally force-releases after 8 consecutive blocks.)
INPUT="$(cat 2>/dev/null || true)"
if printf '%s' "$INPUT" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

MODE="${SEAL_GUARD:-block}"

# --- early exits ------------------------------------------------------------
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
ROOT="$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null)" || exit 0
[ -n "$ROOT" ] || exit 0

# Only uncommitted changes count: a session that already committed its work is
# past this guard's window (conservative by design — misses acceptable).
DIFF="$(git -C "$ROOT" diff HEAD --unified=0 2>/dev/null || true)"
[ -n "$DIFF" ] || exit 0

# --- user-facing surface heuristic (tunable) --------------------------------
# Added lines only; source dirs only; test paths excluded to cut false blocks.
PATTERNS="${SEAL_GUARD_PATTERNS:-println!|eprintln!|console\.(log|error|warn)|printf\(|(^|[^[:alnum:]_])print\(}"
TOUCHED="$(printf '%s\n' "$DIFF" \
  | awk '/^\+\+\+ b\//{f=substr($0,7)} /^\+[^+]/{print f "\t" $0}' \
  | grep -E "^(src|app|lib|bin|cli|ui)/" \
  | grep -Ev "^[^\t]*(test|spec)[^\t]*\t" \
  | grep -E "$PATTERNS" 2>/dev/null || true)"
[ -n "$TOUCHED" ] || exit 0

# --- seal evidence ----------------------------------------------------------
HARNESS="$ROOT/.claude/harness"
TODAY="$(date +%F)"
if [ -f "$HARNESS/seal-log.jsonl" ] && grep -q "$TODAY" "$HARNESS/seal-log.jsonl" 2>/dev/null; then
  exit 0
fi
if git -C "$ROOT" log -1 --format=%B 2>/dev/null | grep -q '^SEAL:'; then
  exit 0
fi

# --- miss: telemetry in every mode -------------------------------------------
mkdir -p "$HARNESS" 2>/dev/null || exit 0
N_SURFACES="$(printf '%s\n' "$TOUCHED" | wc -l | tr -d ' ')"
SAFE_ROOT=${ROOT//\\/\\\\}; SAFE_ROOT=${SAFE_ROOT//\"/\\\"}
printf '{"ts":"%s","event":"seal-miss","mode":"%s","repo":"%s","surfaces":%s}\n' \
  "$(date -Is)" "$MODE" "$SAFE_ROOT" "$N_SURFACES" >> "$HARNESS/seal-guard.jsonl" 2>/dev/null || true

# --- verdict -----------------------------------------------------------------
case "$MODE" in
  off|log)
    exit 0
    ;;
  *)
    echo "偵測到 user-facing 變更尚未 /baransu:seal——請執行 seal 收尾（單次窄域驗收＋直接修正權），或設 SEAL_GUARD=log 降級為僅記錄。" >&2
    exit 2
    ;;
esac
