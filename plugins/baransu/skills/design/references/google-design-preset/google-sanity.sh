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

# ── schemas existence (REQ-002 Scenario 1) ──
# TODO: add long-doc + slides once their schema md files land.
echo "── schemas existence ──"
schema_dir="$SCRIPT_DIR/schemas"
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

echo ""
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
