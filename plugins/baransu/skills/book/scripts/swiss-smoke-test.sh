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

# Stage 1b — negative fixtures (each MUST exit 1; success here means the
# expected-fail gate fired). TASK-svg-05 wires GATE-J + GATE-K.
NEG_FIXTURES=(
  "svg-node-width-fail.html"
  "svg-polygon-fail.html"
)
for neg in "${NEG_FIXTURES[@]}"; do
  neg_path="$HERE/validate-fixtures/$neg"
  [[ -f "$neg_path" ]] || { echo "negative fixture missing: $neg_path" >&2; exit 2; }
  if ( cd "$HERE" && npx tsx validate-output.ts "$neg_path" > /dev/null 2>&1 ); then
    echo "swiss-smoke-test: negative fixture '$neg' unexpectedly PASSED (expected exit 1)" >&2
    exit 1
  fi
done

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
