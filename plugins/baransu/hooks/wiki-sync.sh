#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
[ -z "$PROJECT_DIR" ] && exit 0
[ -d "$PROJECT_DIR/.claude/wiki" ] || exit 0

READ_INDEX="$PROJECT_DIR/.claude/read/index.md"
WIKI_LOG="$PROJECT_DIR/.claude/wiki/log.md"
WIKI_SCHEMA="$PROJECT_DIR/.claude/wiki/wiki-schema.md"

[ -f "$READ_INDEX" ] || exit 0

# Extract slugs from read/index.md (col 2, skip header + separator rows)
# gsub spaces BEFORE checking for separator pattern — critical ordering
read_slugs=$(awk -F'|' 'NR>2{gsub(/ /,"",$3); if($3~/^[-]+$/ || $3=="") next; print $3}' "$READ_INDEX")

# Extract already-processed slugs from wiki/log.md
if [ -f "$WIKI_LOG" ]; then
    done_slugs=$(grep -oP '(?<=sync \| )\S+' "$WIKI_LOG" 2>/dev/null || true)
else
    done_slugs=""
fi

# Compute diff: slugs in read_slugs but not in done_slugs
new_slugs=$(comm -23 <(echo "$read_slugs" | sort) <(echo "$done_slugs" | sort))
[ -z "$new_slugs" ] && exit 0

# Build prompt for claude -p
PROMPT="請根據以下 wiki-schema.md 的協議，對新 slug 更新 wiki/index.md 並追加 wiki/log.md 紀錄。

wiki-schema.md 路徑：$WIKI_SCHEMA
專案根目錄：$PROJECT_DIR

新 slug 清單：
$new_slugs

步驟：
1. 讀取 $WIKI_SCHEMA 了解維護協議
2. 對每個新 slug：
   - 若 $PROJECT_DIR/.claude/learn/digests/ 下有對應的 digest 檔案，內容來源欄位使用 digest:learn/digests/{檔名}
   - 否則從 $PROJECT_DIR/.claude/read/material/{slug}/index.md 提取第一個 # 標題，內容來源欄位使用 stub:read/{slug}
   - 在 $PROJECT_DIR/.claude/wiki/index.md 末尾加入 4 欄 markdown 表格行
   - 在 $PROJECT_DIR/.claude/wiki/log.md 追加 ## [$(date -u +%Y-%m-%dT%H:%M:%SZ)] sync | {slug}
3. 每個 slug 獨立處理，不批次，確保每個 slug 都有對應的 log 紀錄"

claude -p --dangerously-skip-permissions "$PROMPT"
