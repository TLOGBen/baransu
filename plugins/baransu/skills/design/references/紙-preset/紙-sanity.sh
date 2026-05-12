#!/usr/bin/env bash
# 紙-sanity.sh — Kami 十不變量守護腳本 (v1.3)
# Distributed with: 紙 preset only (not 紙/google/swiss generic)
# Copies to {project_root}/紙-sanity.sh when `/baransu:design preset 紙` runs.
#
# Usage:
#   bash 紙-sanity.sh                  # check project root
#   bash 紙-sanity.sh <path>           # check specific path
#
# Kami 十不變量檢查 (legacy v1.2 lint rules)：
#   #1 禁用純白背景       #6 墨藍主色 (#1B365D 或感知等價)
#   #2 暖調限定           #7 羊皮紙底色 (#f5f4ed 或感知等價暖紙)
#   #3 襯線層次           #8 中文字型 (含中文時須有 CJK serif stack)
#   #4 無硬陰影           #9 AI 提示完整性
#   #5 禁用 rgba in palette (shadows OK)  #10 九段俱全
#
# Implementation: invokes check.py in legacy per-file mode with Kami warm-serif rules.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Locate check.py — try plugin source first, fallback to system search
CHECK_PY=""
for candidate in \
  "$HOME/.claude/plugins/cache/baransu/baransu/1.3.0/skills/design/scripts/check.py" \
  "$SCRIPT_DIR/../plugins/baransu/skills/design/scripts/check.py" \
  "$(git rev-parse --show-toplevel 2>/dev/null)/plugins/baransu/skills/design/scripts/check.py"; do
  if [ -f "$candidate" ]; then
    CHECK_PY="$candidate"
    break
  fi
done

if [ -z "$CHECK_PY" ]; then
  echo "❌ Cannot locate check.py for Kami sanity check." >&2
  echo "   Tried: ~/.claude/plugins/cache/baransu/baransu/1.3.0/, ../plugins/baransu/, project root" >&2
  exit 2
fi

TARGET="${1:-.}"

echo "Kami 十不變量 sanity 守護"
echo "  target:  $TARGET"
echo "  engine:  $CHECK_PY (legacy per-file mode)"
echo ""

# Force legacy mode by passing a specific file/dir (not a project root with tokens.css + DESIGN.md).
# If user passes project root, manually iterate over component files in design-cores/ + DESIGN.md.
if [ -f "$TARGET/tokens.css" ] && [ -f "$TARGET/DESIGN.md" ]; then
  echo "→ Running on design-cores/ + DESIGN.md individually (avoiding project-root mode)..."
  exit_code=0
  for f in "$TARGET"/DESIGN.md "$TARGET"/design-cores/*.html "$TARGET"/slide-cores/*.html; do
    if [ -f "$f" ]; then
      python3 "$CHECK_PY" "$f" || exit_code=1
    fi
  done
  if [ "$exit_code" = "0" ]; then
    echo ""
    echo "✅ Kami 十不變量 sanity pass"
  fi
  exit "$exit_code"
else
  python3 "$CHECK_PY" "$TARGET"
fi
