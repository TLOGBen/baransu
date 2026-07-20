#!/usr/bin/env bash
# seal-guard hook behavioral suite:
#   G1) script passes bash -n syntax check
#   G2) stop_hook_active=true → exit 0 (loop protection, no telemetry)
#   G3) non-git cwd → exit 0
#   G4) clean worktree → exit 0
#   G5) user-facing diff + no seal evidence → exit 2, 繁中 stderr instruction,
#       one valid-JSON telemetry line with mode "block"
#   G6) SEAL_GUARD=log same state → exit 0, telemetry line mode "log"
#   G7) same-day seal-log.jsonl evidence → exit 0, no new telemetry line
#   G8) hooks.json valid JSON, registers Stop → seal-guard.sh via ${CLAUDE_PLUGIN_ROOT}
#   G11) Codex runtime miss → exit 0 + structured continue:false JSON
#   G12) Codex runtime defaults telemetry to ~/.codex, never ~/.claude
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$REPO_ROOT/plugins/baransu/hooks/seal-guard.sh"
HOOKS_JSON="$REPO_ROOT/plugins/baransu/hooks/hooks.json"
PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

mkrepo() { # fresh git repo with one committed rust-ish file
  local d; d="$(mktemp -d)"
  git -C "$d" init -q -b main
  git -C "$d" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
  mkdir -p "$d/src"
  printf 'fn main() {}\n' > "$d/src/main.rs"
  git -C "$d" add -A && git -C "$d" -c user.email=t@t -c user.name=t commit -qm base
  echo "$d"
}
touch_surface() { printf 'fn f() { println!("hi user"); }\n' >> "$1/src/main.rs"; }

# G1
if bash -n "$HOOK" 2>/dev/null; then ok "G1 seal-guard.sh syntax clean"; else bad "G1 syntax error"; fi

# G2
R="$(mkrepo)"; touch_surface "$R"
T="$(mktemp -d)"
printf '{"hook_event_name":"Stop","stop_hook_active": true}' \
  | CLAUDE_PROJECT_DIR="$R" BARANSU_TELEMETRY_DIR="$T" bash "$HOOK"; rc=$?
if [ "$rc" -eq 0 ] && [ -z "$(find "$T" -name 'seal-guard-*.jsonl' 2>/dev/null)" ]; then
  ok "G2 stop_hook_active=true exits 0 without telemetry"
else bad "G2 loop-protection path (rc=$rc)"; fi
rm -rf "$R" "$T"

# G3
D="$(mktemp -d)"
printf '{"stop_hook_active": false}' | CLAUDE_PROJECT_DIR="$D" bash "$HOOK"; rc=$?
if [ "$rc" -eq 0 ]; then ok "G3 non-git cwd exits 0"; else bad "G3 rc=$rc"; fi
rm -rf "$D"

# G4
R="$(mkrepo)"
printf '{"stop_hook_active": false}' | CLAUDE_PROJECT_DIR="$R" bash "$HOOK"; rc=$?
if [ "$rc" -eq 0 ]; then ok "G4 clean worktree exits 0"; else bad "G4 rc=$rc"; fi
rm -rf "$R"

# G5
R="$(mkrepo)"; touch_surface "$R"
T="$(mktemp -d)"
ERR="$(printf '{"stop_hook_active": false}' | CLAUDE_PROJECT_DIR="$R" BARANSU_TELEMETRY_DIR="$T" bash "$HOOK" 2>&1 >/dev/null)"; rc=$?
LINE="$(tail -1 "$T/$(basename "$R")/seal-guard-$(date +%Y-%m).jsonl" 2>/dev/null)"
if [ "$rc" -eq 2 ] \
   && printf '%s' "$ERR" | grep -q "baransu:seal" \
   && printf '%s' "$ERR" | grep -q "SEAL_GUARD=log" \
   && printf '%s' "$LINE" | python3 -c 'import json,sys; d=json.loads(sys.stdin.read()); assert d["mode"]=="block" and d["event"]=="seal-miss"' 2>/dev/null; then
  ok "G5 blocking path: exit 2 + 繁中 instruction + block-mode telemetry"
else bad "G5 blocking path (rc=$rc, err=$ERR, line=$LINE)"; fi
rm -rf "$R" "$T"

# G6
R="$(mkrepo)"; touch_surface "$R"
T="$(mktemp -d)"
printf '{"stop_hook_active": false}' | CLAUDE_PROJECT_DIR="$R" BARANSU_TELEMETRY_DIR="$T" SEAL_GUARD=log bash "$HOOK"; rc=$?
LINE="$(tail -1 "$T/$(basename "$R")/seal-guard-$(date +%Y-%m).jsonl" 2>/dev/null)"
if [ "$rc" -eq 0 ] \
   && printf '%s' "$LINE" | python3 -c 'import json,sys; d=json.loads(sys.stdin.read()); assert d["mode"]=="log"' 2>/dev/null; then
  ok "G6 SEAL_GUARD=log degrades to exit 0 with log-mode telemetry"
else bad "G6 log mode (rc=$rc, line=$LINE)"; fi
rm -rf "$R" "$T"

# G7
R="$(mkrepo)"; touch_surface "$R"
T="$(mktemp -d)"; mkdir -p "$T/$(basename "$R")"
printf '{"ts":"%sT00:00:00","skill":"seal","result":"pass"}\n' "$(date +%F)" > "$T/$(basename "$R")/seal-log-$(date +%Y-%m).jsonl"
printf '{"stop_hook_active": false}' | CLAUDE_PROJECT_DIR="$R" BARANSU_TELEMETRY_DIR="$T" bash "$HOOK"; rc=$?
if [ "$rc" -eq 0 ] && [ -z "$(find "$T" -name 'seal-guard-*.jsonl' 2>/dev/null)" ]; then
  ok "G7 same-day seal evidence exits 0 without telemetry"
else bad "G7 seal evidence path (rc=$rc)"; fi
rm -rf "$R" "$T"

# G8
if python3 - "$HOOKS_JSON" <<'EOF' 2>/dev/null
import json, sys
d = json.load(open(sys.argv[1]))
stop = d["hooks"]["Stop"]
cmd = stop[0]["hooks"][0]["command"]
assert "seal-guard.sh" in cmd and "${CLAUDE_PLUGIN_ROOT}" in cmd
assert stop[0]["hooks"][0]["type"] == "command"
EOF
then ok "G8 hooks.json registers Stop → seal-guard.sh via CLAUDE_PLUGIN_ROOT"
else bad "G8 hooks.json registration"; fi

# G9 — producer side: seal SKILL.md must instruct writing the evidence file the hook reads
if grep -q 'seal-log-{YYYY-MM}\.jsonl' "$REPO_ROOT/plugins/baransu/skills/seal/SKILL.md"; then
  ok "G9 seal SKILL.md contains seal-log.jsonl write instruction (producer side pinned)"
else bad "G9 seal SKILL.md lacks seal-log.jsonl instruction — hook evidence chain dangling"; fi

# G10 — SEAL_GUARD=off still appends telemetry and exits 0
R="$(mkrepo)"; touch_surface "$R"
T="$(mktemp -d)"
printf '{"stop_hook_active": false}' | CLAUDE_PROJECT_DIR="$R" BARANSU_TELEMETRY_DIR="$T" SEAL_GUARD=off bash "$HOOK"; rc=$?
if [ "$rc" -eq 0 ] && grep -q '"mode":"off"' "$T/$(basename "$R")/seal-guard-$(date +%Y-%m).jsonl" 2>/dev/null; then
  ok "G10 SEAL_GUARD=off appends jsonl and exits 0"
else bad "G10 off-mode telemetry path (rc=$rc)"; fi
rm -rf "$R" "$T"

# G11 — Codex Stop hooks block with structured JSON, not Claude's exit-2 contract
R="$(mkrepo)"; touch_surface "$R"
T="$(mktemp -d)"
OUT="$(printf '{"hook_event_name":"Stop"}' \
  | PLUGIN_ROOT="$REPO_ROOT/plugins/baransu" CLAUDE_PROJECT_DIR="$R" \
    BARANSU_TELEMETRY_DIR="$T" bash "$HOOK" 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] \
   && printf '%s' "$OUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["continue"] is False; assert "baransu:seal" in d["stopReason"]; assert d["systemMessage"] == d["stopReason"]' 2>/dev/null; then
  ok "G11 Codex miss returns continue:false JSON and exits 0"
else bad "G11 Codex blocking contract (rc=$rc, out=$OUT)"; fi
rm -rf "$R" "$T"

# G12 — no override: Codex consumer and /seal producer share ~/.codex root
R="$(mkrepo)"; touch_surface "$R"
H="$(mktemp -d)"
printf '{"hook_event_name":"Stop"}' \
  | HOME="$H" PLUGIN_ROOT="$REPO_ROOT/plugins/baransu" CLAUDE_PROJECT_DIR="$R" \
    SEAL_GUARD=log bash "$HOOK" >/dev/null 2>&1; rc=$?
if [ "$rc" -eq 0 ] \
   && [ -f "$H/.codex/baransu/telemetry/$(basename "$R")/seal-guard-$(date +%Y-%m).jsonl" ] \
   && [ ! -e "$H/.claude/baransu/telemetry" ]; then
  ok "G12 Codex default telemetry root is ~/.codex only"
else bad "G12 Codex telemetry root (rc=$rc)"; fi
rm -rf "$R" "$H"

echo ""
echo "=== test-seal-guard-hook: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
