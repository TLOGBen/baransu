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

# Locate check.py — try plugin source first, fallback to the plugin cache.
# The cache candidates are version-agnostic globs (the cache path embeds the
# plugin version, which changes on every release — never hardcode it).
CHECK_PY=""
# 1) Direct candidates: this script inside the plugin source tree, or a
#    project root that sits next to a plugins/ checkout.
for candidate in \
  "$SCRIPT_DIR/../../scripts/check.py" \
  "$SCRIPT_DIR/../plugins/baransu/skills/design/scripts/check.py"; do
  if [ -f "$candidate" ]; then
    CHECK_PY="$candidate"
    break
  fi
done

# 2) Plugin cache: the glob may match SEVERAL cached versions — pick the
#    NEWEST (ls -v natural-sorts the version segment ascending; take the
#    last). A plain for-loop expands lexicographically and would pin the
#    OLDEST cached engine, silently ignoring lint fixes shipped since.
if [ -z "$CHECK_PY" ]; then
  for glob in \
    "$HOME/.claude/plugins/cache/baransu/baransu/*/skills/design/scripts/check.py" \
    "$HOME/.claude/plugins/cache/baransu/*/skills/design/scripts/check.py"; do
    # shellcheck disable=SC2086 — glob must expand
    newest="$(ls -v $glob 2>/dev/null | tail -1 || true)"
    if [ -n "$newest" ] && [ -f "$newest" ]; then
      CHECK_PY="$newest"
      break
    fi
  done
fi

# 3) Last resort: git root of the CHECKED project. This only ever hits when
#    the audited project IS the baransu repo itself — a dead path in real
#    deployments (rev-parse runs in the user project's cwd), kept only as a
#    final fallback for in-repo dogfooding.
if [ -z "$CHECK_PY" ]; then
  candidate="$(git rev-parse --show-toplevel 2>/dev/null)/plugins/baransu/skills/design/scripts/check.py"
  if [ -f "$candidate" ]; then
    CHECK_PY="$candidate"
  fi
fi

if [ -z "$CHECK_PY" ]; then
  echo "❌ Cannot locate check.py for Kami sanity check." >&2
  echo "   Tried: ../plugins/baransu/, project root, ~/.claude/plugins/cache/baransu/*/" >&2
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
  file_count=0
  for f in "$TARGET"/DESIGN.md "$TARGET"/design-cores/*.html "$TARGET"/slide-cores/*.html; do
    if [ -f "$f" ]; then
      file_count=$((file_count + 1))
      # Quiet on pass (one summary line below instead of N duplicates);
      # violations print in full.
      out="$(python3 "$CHECK_PY" "$f" 2>&1)" || { printf '%s\n' "$out"; exit_code=1; }
    fi
  done
  if [ "$exit_code" = "0" ]; then
    echo "OK  Kami per-file lint (${file_count} file(s), no violations)"
  fi
else
  python3 "$CHECK_PY" "$TARGET" || exit_code=1
  exit_code="${exit_code:-0}"
fi

# ── schemas existence (REQ-002 Scenario 1) ──
# TODO: add long-doc + slides once their schema md files land.
echo ""
echo "── schemas existence ──"
schema_dir="$SCRIPT_DIR/schemas"
if [ ! -d "$schema_dir" ]; then
  # The preset-apply flow copies only the 5-artifact set + this script to the
  # project root — schemas/ never deploys there. Skip, don't FAIL.
  echo "SKIP schemas existence（schemas/ 未部署於此位置 — 僅 plugin 原始碼內檢查）"
else
  sx_fail=0
  for s in resume portfolio one-pager letter equity-report changelog; do
    if [ ! -f "$schema_dir/$s.md" ]; then
      echo "FAIL schemas existence: missing $schema_dir/$s.md" >&2
      sx_fail=1
      exit_code=1
      break
    fi
  done
  if [ "$sx_fail" = "0" ]; then
    echo "OK  schemas existence (6 new doc-types present)"
  fi
fi

# ── object-position lint (REQ-002 Scenario 3 / B5) ──
echo ""
echo "── object-position lint ──"
op_fail=0
for f in design-cores/resume.html design-cores/resume-en.html \
         design-cores/portfolio.html design-cores/portfolio-en.html; do
  full="$SCRIPT_DIR/$f"
  test -f "$full" || continue
  if ! grep -q "object-position: center 35%" "$full"; then
    echo "FAIL object-position lint: $f missing 'object-position: center 35%'" >&2
    op_fail=1
    exit_code=1
    break
  fi
done
if [ "$op_fail" = "0" ]; then
  echo "OK  object-position lint (portrait schemas compliant)"
fi

# ── editorial-sanity (REQ-004) ──
EDITORIAL_SH="$SCRIPT_DIR/../editorial-sanity.sh"
if [ -f "$EDITORIAL_SH" ]; then
  LONG_FORM="$SCRIPT_DIR/design-cores/long-form.html"
  if [ -f "$LONG_FORM" ]; then
    echo ""
    echo "── editorial-sanity ──"
    bash "$EDITORIAL_SH" "$LONG_FORM" || exit_code=1
  fi
fi

# ── validate-swiss-deck (REQ-003 Scenario 2 / B8) ──
VALIDATE_DECK="$SCRIPT_DIR/../../../book/scripts/validate-swiss-deck.mjs"
SLIDE_CORES="$SCRIPT_DIR/slide-cores"
if [ -f "$VALIDATE_DECK" ] && [ -d "$SLIDE_CORES" ]; then
  echo ""
  echo "── validate-swiss-deck ──"
  node "$VALIDATE_DECK" "$SLIDE_CORES" || exit_code=1
fi

if [ "${exit_code:-0}" = "0" ]; then
  echo ""
  echo "✅ Kami 十不變量 + editorial-sanity pass"
else
  echo ""
  echo "❌ Kami sanity FAIL — 詳見上方輸出" >&2
fi
exit "${exit_code:-0}"
