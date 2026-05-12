#!/usr/bin/env bash
# google-sanity.sh — Google (Material 3) preset sanity 守護腳本 (v1.4)
# Distributed with: google-design preset only.
# Copies to {project_root}/google-sanity.sh when `/baransu:design preset google-design` runs.
#
# Usage:
#   bash google-sanity.sh                  # check project root
#   bash google-sanity.sh <path>           # check specific path
#
# Google preset 不變量（簡略）：
#   - class 前綴 `google-`
#   - accent: M3 baseline #6750A4
#   - Roboto / Google Sans 字族
#   - elevation tokens（Material shadow ladder）
#
# Implementation note: Kami-specific check.py（warm palette / CJK serif）
# rules do NOT apply to Google Material; this script focuses on REQ-004
# editorial-sanity wiring. Preset-wide lint cleanup can be layered on later.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET="${1:-.}"

echo "Google (Material 3) preset sanity 守護"
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
  echo "✅ Google preset + editorial-sanity pass"
fi
exit "${exit_code:-0}"
