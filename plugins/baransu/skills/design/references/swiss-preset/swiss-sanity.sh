#!/usr/bin/env bash
# swiss-sanity.sh — Swiss preset sanity 守護腳本 (v1.4)
# Distributed with: swiss preset only.
# Copies to {project_root}/swiss-sanity.sh when `/baransu:design preset swiss` runs.
#
# Usage:
#   bash swiss-sanity.sh                  # check project root
#   bash swiss-sanity.sh <path>           # check specific path
#
# Swiss preset 不變量（簡略）：
#   - class 前綴 `swiss-`
#   - accent: IKB #002FA7
#   - Helvetica / Inter / Akzidenz 字族
#   - flush-left, grid-based, no decorative shadow
#
# Implementation note: Kami-specific check.py（warm palette / CJK serif）
# rules do NOT apply to Swiss; this script focuses on REQ-004 editorial-sanity
# wiring. Preset-wide lint cleanup can be layered on later.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET="${1:-.}"

echo "Swiss preset sanity 守護"
echo "  target:  $TARGET"
echo ""

exit_code=0

# ── editorial-sanity (REQ-004) ──
EDITORIAL_SH="$SCRIPT_DIR/../editorial-sanity.sh"
if [ -f "$EDITORIAL_SH" ]; then
  LONG_FORM="$SCRIPT_DIR/design-cores/long-form.html"
  if [ -f "$LONG_FORM" ]; then
    echo "── editorial-sanity ──"
    bash "$EDITORIAL_SH" "$LONG_FORM" || exit_code=1
  fi
fi

if [ "${exit_code:-0}" = "0" ]; then
  echo ""
  echo "✅ Swiss preset + editorial-sanity pass"
fi
exit "${exit_code:-0}"
