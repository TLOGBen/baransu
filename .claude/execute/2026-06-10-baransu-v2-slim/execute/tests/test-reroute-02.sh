#!/usr/bin/env bash
# TASK-reroute-02 Red/Green gate — 七處交接與錨點改道斷言
# exit 0 = all pass (GREEN), exit 1 = at least one assertion failed (RED)
set -u
ROOT="/home/vakarve/projects/baransu/.claude/worktrees/learn-waza-research"
cd "$ROOT" || exit 2

PASS=0
FAIL=0
ok()  { PASS=$((PASS+1)); echo "  ok   - $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL - $1"; }

THINK="plugins/baransu/skills/think/SKILL.md"
HUNT="plugins/baransu/skills/hunt/SKILL.md"
REVIEW="plugins/baransu/skills/review/SKILL.md"
SHIP="plugins/baransu/skills/ship/SKILL.md"
RAGENT="plugins/baransu/agents/review-agent.md"
CST="plugins/baransu/skills/codex-skill-transfer/SKILL.md"
TPY="plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py"

echo "[1] plugins/ 零 word-boundary baransu:dev / .claude/dev 功能性引用"
if grep -rqE '\bbaransu:dev\b' plugins/; then bad "plugins/ 仍含 baransu:dev"; else ok "無 baransu:dev"; fi
if grep -rqE '\.claude/dev\b' plugins/; then bad "plugins/ 仍含 .claude/dev"; else ok "無 .claude/dev"; fi
if grep -rqF 'dev/SKILL.md' plugins/; then bad "plugins/ 仍含 dev/SKILL.md 錨點"; else ok "無 dev/SKILL.md 錨點"; fi

echo "[2] 七目標檔內零 /dev 與 word-boundary dev 殘留"
for f in "$THINK" "$HUNT" "$REVIEW" "$SHIP" "$RAGENT" "$CST" "$TPY"; do
  HITS=$(grep -nE '(^|[^a-zA-Z0-9_.])/dev\b|\bdev\b' "$f" | grep -v '/dev/null')
  if [ -n "$HITS" ]; then
    bad "$f 仍含 dev 引用: $(echo "$HITS" | head -2 | tr '\n' ' ')"
  else
    ok "$f 無 dev 殘留"
  fi
done

echo "[3] 改道語式落地"
PHRASE='直接實作，依 _shared/tdd.md 紀律自建紅綠 task list'
if grep -qF "$PHRASE" "$THINK"; then ok "think Stage G 含改道語式"; else bad "think 缺改道語式"; fi
if grep -E '^G\. Approval' "$THINK" | grep -q 'tdd\.md'; then ok "think :175 stage 總覽改道"; else bad "think stage 總覽未改道"; fi
if grep -qF "$PHRASE" "$HUNT"; then ok "hunt 含改道語式"; else bad "hunt 缺改道語式"; fi
if grep -qF '/baransu:execute 或依 tdd.md 的直接實作' "$REVIEW"; then ok "review :210 固定語式"; else bad "review 缺固定語式"; fi

echo "[4] ship 歸檔通道：dev 移除、其餘四目錄不變"
if grep -q 'find \.claude/tmp \.claude/analyze \.claude/execute \.claude/think -maxdepth' "$SHIP"; then ok "ship find 清單正確"; else bad "ship find 清單不符"; fi
for d in tmp analyze execute think; do
  if grep -q "\.claude/$d" "$SHIP" || grep -qE "\`$d\`" "$SHIP"; then ok "ship 保留 $d 通道"; else bad "ship 遺失 $d 通道"; fi
done

echo "[5] review-agent cosmetic 錨點改掛 tdd.md §7.1，四分類不變"
if grep -q '_shared/tdd\.md' "$RAGENT" && grep -q '§7\.1' "$RAGENT"; then ok "錨點已掛 tdd.md §7.1"; else bad "錨點未掛 tdd.md §7.1"; fi
for c in 'comment edits' 'dead import removal' 'identifier rename with no behavior change' 'pure formatting'; do
  if grep -qF "$c" "$RAGENT"; then ok "四分類保留: $c"; else bad "四分類遺失: $c"; fi
done

echo "[6] codex-skill-transfer 兩處換存活例子"
if grep -qE 'grade-collector\.py|health_check\.py' "$CST"; then bad "SKILL.md:116 仍舉被裁例子"; else ok "SKILL.md 無被裁例子"; fi
if grep -q 'grade/triage/dev/bridge' "$TPY"; then bad "transfer.py:819 仍含 grade/triage/dev/bridge"; else ok "transfer.py 無被裁引用"; fi
if grep -q 'tdd\.md cited by' "$TPY"; then ok "transfer.py 保留 tdd.md 舉例（換存活引用者）"; else bad "transfer.py tdd.md 舉例遺失"; fi

echo "[7] execute/SKILL.md 零 diff"
if git diff --quiet -- plugins/baransu/skills/execute/SKILL.md; then ok "execute/SKILL.md 零 diff"; else bad "execute/SKILL.md 有 diff"; fi

echo
echo "passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
