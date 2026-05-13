#!/usr/bin/env bash
# editorial-sanity.sh — REQ-004 mechanical gate
# Three checks per design-core HTML:
#   1. text-wrap: pretty present (REQ-004 Scenario 1 / B11)
#   2. .{preset}-dropcap class font-size ∈ [4.0em, 5.0em] ≈ 3-line drop (Scenario 2)
#   3. prose straight-quote count = 0 via HTMLParser (Scenario 3 / B12)
#
# Usage:
#   bash editorial-sanity.sh <design-core-file.html>
#
# Exit codes:
#   0 — all three checks pass
#   1 — at least one check failed
#   2 — structural error (missing arg, file not found, unrecognized preset)

set -euo pipefail

FILE="${1:?missing file path — usage: bash editorial-sanity.sh <design-core-file.html>}"
test -f "$FILE" || { echo "FAIL editorial-sanity: file not found: $FILE" >&2; exit 2; }

# Detect preset prefix (kami / swiss / google)
prefix=""
if grep -q "kami-body\|kami-paper-body" "$FILE" 2>/dev/null; then
  prefix="kami"
elif grep -q "swiss-body" "$FILE" 2>/dev/null; then
  prefix="swiss"
elif grep -q "google-body" "$FILE" 2>/dev/null; then
  prefix="google"
else
  echo "FAIL editorial-sanity: no recognized preset prefix (kami/swiss/google) in $FILE" >&2
  exit 2
fi

echo "→ editorial-sanity ($prefix) — $FILE"

# ─────────────────────────────────────────────────────────────
# Check 1: text-wrap: pretty present
# ─────────────────────────────────────────────────────────────
if ! grep -E "text-wrap:\s*pretty" "$FILE" > /dev/null; then
  echo "FAIL editorial-sanity Check 1 (text-wrap pretty): not found in $FILE" >&2
  exit 1
fi
echo "OK  editorial-sanity Check 1 (text-wrap: pretty present)"

# ─────────────────────────────────────────────────────────────
# Check 2: .{prefix}-dropcap class with font-size ∈ [4.0em, 5.0em]
# ─────────────────────────────────────────────────────────────
if ! grep -E "\.${prefix}-dropcap\s*\{" "$FILE" > /dev/null; then
  echo "FAIL editorial-sanity Check 2 (.${prefix}-dropcap class): not defined in $FILE" >&2
  exit 1
fi

# Extract font-size from the dropcap rule. Handles both single-line
# (`.foo-dropcap { font-size: 4.65em; ... }`) and multi-line rule bodies.
fontsize=$(awk -v p="${prefix}-dropcap" '
  # Same-line rule: matches selector AND font-size on one line.
  $0 ~ "\\."p"[[:space:]]*\\{" && /font-size:/ { print; exit }
  # Multi-line rule: enter block, scan until closing brace.
  $0 ~ "\\."p"[[:space:]]*\\{" && !/\}/ { in_block=1; next }
  in_block && /font-size:/ { print; in_block=0; exit }
  in_block && /\}/ { in_block=0 }
' "$FILE" | sed -nE 's/.*font-size:[[:space:]]*([0-9]+\.?[0-9]*)em.*/\1/p' | head -1)

if [ -z "$fontsize" ]; then
  echo "FAIL editorial-sanity Check 2 (.${prefix}-dropcap font-size): could not parse em value" >&2
  exit 1
fi

# Float comparison: 4.0 ≤ fs ≤ 5.0
ok=$(awk -v fs="$fontsize" 'BEGIN { print (fs >= 4.0 && fs <= 5.0) ? "1" : "0" }')
if [ "$ok" != "1" ]; then
  echo "FAIL editorial-sanity Check 2 (.${prefix}-dropcap font-size ${fontsize}em outside 3-line drop range 4.0–5.0em)" >&2
  exit 1
fi
echo "OK  editorial-sanity Check 2 (.${prefix}-dropcap font-size=${fontsize}em ≈ 3-line drop)"

# ─────────────────────────────────────────────────────────────
# Check 3: prose straight-quote count = 0 (HTMLParser excludes attrs + code/pre/script/style)
# ─────────────────────────────────────────────────────────────
straight_count=$(python3 - "$FILE" <<'PY'
from html.parser import HTMLParser
import sys

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_skip = 0
        self.count = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('code', 'pre', 'script', 'style'):
            self.in_skip += 1
    def handle_endtag(self, tag):
        if tag in ('code', 'pre', 'script', 'style') and self.in_skip > 0:
            self.in_skip -= 1
    def handle_data(self, data):
        if self.in_skip == 0:
            self.count += data.count('"')

p = P()
with open(sys.argv[1], encoding='utf-8') as f:
    p.feed(f.read())
print(p.count)
PY
)

if [ "$straight_count" -ne 0 ]; then
  echo "FAIL editorial-sanity Check 3 (curly quotes): found $straight_count straight \" in prose of $FILE" >&2
  exit 1
fi
echo "OK  editorial-sanity Check 3 (prose straight-quote count=0)"

echo "PASS editorial-sanity all 3 checks for $FILE"
exit 0
