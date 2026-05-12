#!/usr/bin/env bash
# swiss-smoke-test.sh — REQ-003 Scenario 2 smoke
#
# Stage 1: validate-output.ts on swiss-positive.html (must pass)
# Stage 2: if html2pptx deps installed, generate .pptx and verify it's a
#          valid zipfile containing PowerPoint's required parts.
#          If deps absent, exit 0 silently (Stage 1 alone is sufficient).
#
# Exit: 0 = pass | 1 = validator/pptx fail | 2 = usage error

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
FIXTURE="$HERE/validate-fixtures/swiss-positive.html"
OUT_PPTX="${SWISS_SMOKE_OUT:-/tmp/swiss-smoke.pptx}"

[[ -f "$FIXTURE" ]] || { echo "fixture missing: $FIXTURE" >&2; exit 2; }

# Stage 1
( cd "$HERE" && npx tsx validate-output.ts "$FIXTURE" ) || exit 1

# Stage 2 — only if deps present
node -e "require.resolve('pptxgenjs', { paths: ['$HERE'] }); require.resolve('playwright', { paths: ['$HERE'] })" 2>/dev/null || exit 0

rm -f "$OUT_PPTX"
( cd "$HERE" && node html2pptx.js "$FIXTURE" "$OUT_PPTX" ) || exit 1
[[ -f "$OUT_PPTX" ]] || exit 1

python3 - "$OUT_PPTX" <<'PY' || exit 1
import sys, zipfile
path = sys.argv[1]
if not zipfile.is_zipfile(path):
    sys.exit(1)
with zipfile.ZipFile(path) as z:
    names = set(z.namelist())
required = {"ppt/presentation.xml", "[Content_Types].xml"}
if required - names:
    sys.exit(1)
PY

echo "swiss-smoke-test: PASS"
