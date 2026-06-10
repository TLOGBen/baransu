#!/usr/bin/env bash
# TASK-contract-02 Red/Green gate — 事件型四技能（think/write/book/review）Outcome Contract 四行頭
# exit 0 = all pass (GREEN), exit 1 = at least one assertion failed (RED)
set -u
ROOT="/home/vakarve/projects/baransu/.claude/worktrees/learn-waza-research"
cd "$ROOT" || exit 2

PASS=0
FAIL=0
ok()  { PASS=$((PASS+1)); echo "  ok   - $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL - $1"; }

SKILLS_DIR="plugins/baransu/skills"
FILES=(think write book review)

# 提取契約區塊（## Outcome Contract 起、下一個 ## 或 --- 前）
contract_block() {
  awk '/^## Outcome Contract$/{flag=1; next} flag && (/^## /||/^---$/){exit} flag' "$1"
}

echo "[1] 四檔各含恰一個 ## Outcome Contract，且為檔內第一個 H2（frontmatter 後、原第一個 H2 前）"
for s in "${FILES[@]}"; do
  f="$SKILLS_DIR/$s/SKILL.md"
  N=$(grep -c '^## Outcome Contract$' "$f")
  if [ "$N" -ne 1 ]; then bad "$s: ## Outcome Contract 出現 $N 次（須恰 1）"; continue; fi
  FIRST_H2=$(grep -m1 '^## ' "$f")
  if [ "$FIRST_H2" = "## Outcome Contract" ]; then ok "$s: 契約頭為第一個 H2"; else bad "$s: 第一個 H2 是「$FIRST_H2」非契約頭"; fi
done

echo "[2] 契約四行齊備且非空（Outcome / Done when / Evidence / Output）"
for s in "${FILES[@]}"; do
  f="$SKILLS_DIR/$s/SKILL.md"
  BLOCK=$(contract_block "$f")
  for k in 'Outcome' 'Done when' 'Evidence' 'Output'; do
    if echo "$BLOCK" | grep -qE "^- \*\*$k\*\*[:：] *[^ ]"; then
      ok "$s: $k 行非空"
    else
      bad "$s: $k 行缺失或為空"
    fi
  done
done

echo "[3] Done when 採事件型/混合型指定表述"
TB=$(contract_block "$SKILLS_DIR/think/SKILL.md"  | grep '^- \*\*Done when\*\*' || true)
WB=$(contract_block "$SKILLS_DIR/write/SKILL.md"  | grep '^- \*\*Done when\*\*' || true)
BB=$(contract_block "$SKILLS_DIR/book/SKILL.md"   | grep '^- \*\*Done when\*\*' || true)
RB=$(contract_block "$SKILLS_DIR/review/SKILL.md" | grep '^- \*\*Done when\*\*' || true)
echo "$TB" | grep -q 'Stage G' && echo "$TB" | grep -q '批准' \
  && ok "think: Stage G 四選項閘批准事件型" || bad "think: Done when 未含 Stage G 批准事件"
echo "$WB" | grep -q 'Before/After' && echo "$WB" | grep -q 'rules 5/7/8' && echo "$WB" | grep -q '禁對仗' \
  && ok "write: Before/After＋rules 5/7/8 anti-AI 味 floor 混合型" || bad "write: Done when 未含 Before/After 或 rules 5/7/8（禁對仗/禁排比/禁名詞化）硬規則"
echo "$BB" | grep -q 'validate-output\.ts' \
  && ok "book: 錨定 validate-output.ts 閘" || bad "book: Done when 未錨定 validate-output.ts"
echo "$RB" | grep -q 'sign-off receipt' && echo "$RB" | grep -qi 'hard-stops sweep' \
  && ok "review: 八欄 receipt＋hard-stops sweep 混合型" || bad "review: Done when 未含 receipt/sweep"
echo "$RB" | grep -q '八欄' \
  && ok "review: 明示八欄" || bad "review: Done when 未明示八欄"

echo "[4] 禁止空殼條件（「輸出存在」類）"
for s in "${FILES[@]}"; do
  f="$SKILLS_DIR/$s/SKILL.md"
  DW=$(contract_block "$f" | grep '^- \*\*Done when\*\*' || true)
  if echo "$DW" | grep -q '輸出存在'; then bad "$s: Done when 為空殼條件"; else ok "$s: 無空殼條件"; fi
done

echo "[5] 既有正文零刪改（git diff 刪除行數 = 0）"
for s in "${FILES[@]}"; do
  f="$SKILLS_DIR/$s/SKILL.md"
  DEL=$(git diff --numstat -- "$f" | awk '{print $2}')
  DEL=${DEL:-0}
  if [ "$DEL" -eq 0 ]; then ok "$s: 零刪改 (deletions=$DEL)"; else bad "$s: 有刪改 (deletions=$DEL)"; fi
done

echo "[6] frontmatter 結構未動（首行 --- 且閉合 --- 在契約頭之前）"
for s in "${FILES[@]}"; do
  f="$SKILLS_DIR/$s/SKILL.md"
  if [ "$(head -1 "$f")" != "---" ]; then bad "$s: 首行非 frontmatter ---"; continue; fi
  FM_CLOSE=$(grep -n '^---$' "$f" | sed -n '2p' | cut -d: -f1)
  OC_LINE=$(grep -n '^## Outcome Contract$' "$f" | head -1 | cut -d: -f1)
  if [ -n "$FM_CLOSE" ] && [ -n "$OC_LINE" ] && [ "$OC_LINE" -gt "$FM_CLOSE" ]; then
    ok "$s: 契約頭位於 frontmatter 之後"
  else
    bad "$s: 契約頭位置與 frontmatter 關係異常 (fm_close=$FM_CLOSE oc=$OC_LINE)"
  fi
done

echo
echo "passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
