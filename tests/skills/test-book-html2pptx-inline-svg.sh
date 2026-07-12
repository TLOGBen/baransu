#!/usr/bin/env bash
# Standing regression: html2pptx.js must survive inline SVG in a slide.
#
# Promoted from the pre-v2.9.0 field-smoke gate. Defect class guarded:
# SVGAnimatedString CRASH — on SVG elements `el.className` is an
# SVGAnimatedString (an object: always truthy, has no .includes), so any
# `el.className.includes(...)` read inside the page.evaluate extraction
# throws "el.className.includes is not a function" on the first inline-SVG
# child and aborts the whole deck render. The fix reads the class via
# `el.getAttribute('class')` (see the NOTE in html2pptx.js).
#
# Two layers, so the gate still bites in a fresh dep-less checkout:
#   T1 (always on, zero deps): static guard — no non-comment `.className`
#      read may exist in html2pptx.js. Deterministic, hermetic.
#   T2/T3 (behavioral, dep-gated): drive html2pptx.js through real fixtures.
#      T2: validate-fixtures/swiss-positive.html — the shipped fixture that
#          CONTAINS inline SVG (html2pptx-behavior.html, the rules-2/3 probe,
#          has none; fixtures are reused, never duplicated) — must render to
#          a valid .pptx with exit 0.
#      T3: validate-fixtures/html2pptx-behavior.html — must fail GRACEFULLY
#          with its designed rule-2/3 validation errors, not a JS crash.
#
# Hermetic-or-skip: T2/T3 need node + playwright + pptxgenjs + a downloaded
# chromium browser, resolvable from skills/book/scripts (same detection as
# swiss-smoke-test.sh). If anything is missing, SKIP the behavioral layer
# with a loud one-line reason and exit 0 — never fail spuriously, never
# download anything inside make test.

set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPTS_DIR="$ROOT/plugins/baransu/skills/book/scripts"
HTML2PPTX="$SCRIPTS_DIR/html2pptx.js"
SVG_FIXTURE="$SCRIPTS_DIR/validate-fixtures/swiss-positive.html"
BEHAVIOR_FIXTURE="$SCRIPTS_DIR/validate-fixtures/html2pptx-behavior.html"

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() {
  FAIL=$((FAIL + 1))
  echo "  FAIL: $1" >&2
  if [ -n "${2:-}" ]; then echo "        $2" >&2; fi
}

# --- structural preconditions (real failures, not skips) ---
for f in "$HTML2PPTX" "$SVG_FIXTURE" "$BEHAVIOR_FIXTURE"; do
  if [ ! -f "$f" ]; then
    echo "FAIL: shipped asset missing: $f (html2pptx pipeline no longer distributable)" >&2
    exit 1
  fi
done

# ---------------------------------------------------------------------------
# T1: static guard — no non-comment `.className` read in html2pptx.js.
# The fixed code documents the hazard in // comments (which legitimately
# contain the string), so comment lines are stripped before matching.
# ---------------------------------------------------------------------------
echo "T1: html2pptx.js has no non-comment .className read (SVGAnimatedString crash class)..."
CLASSNAME_HITS="$(grep -vE '^[[:space:]]*//' "$HTML2PPTX" | grep -n '\.className' || true)"
if [ -z "$CLASSNAME_HITS" ]; then
  pass "T1 no .className read outside comments (class access stays on getAttribute('class'))"
else
  fail "T1 SVGAnimatedString crash class reintroduced: html2pptx.js reads .className in code" \
       "On SVG elements className is an object without .includes — the read crashes the deck render. Use el.getAttribute('class'). Hits: $CLASSNAME_HITS"
fi

# ---------------------------------------------------------------------------
# Behavioral layer dep gate (mirrors swiss-smoke-test.sh Stage 2 detection,
# plus a browser-binary probe so a bare `npm install playwright` without
# `playwright install chromium` still skips instead of failing spuriously).
# ---------------------------------------------------------------------------
BEHAVIORAL=1
if ! command -v node >/dev/null 2>&1; then
  BEHAVIORAL=0
  echo "SKIP test-book-html2pptx-inline-svg behavioral layer: node not on PATH — static T1 guard still enforced"
elif ! node -e "require.resolve('pptxgenjs', { paths: ['$SCRIPTS_DIR'] }); require.resolve('playwright', { paths: ['$SCRIPTS_DIR'] })" 2>/dev/null; then
  BEHAVIORAL=0
  echo "SKIP test-book-html2pptx-inline-svg behavioral layer: pptxgenjs/playwright not installed under skills/book/scripts — static T1 guard still enforced"
elif ! (cd "$SCRIPTS_DIR" && node -e "const {chromium}=require('playwright'); require('fs').accessSync(chromium.executablePath())" 2>/dev/null); then
  BEHAVIORAL=0
  echo "SKIP test-book-html2pptx-inline-svg behavioral layer: playwright chromium browser not downloaded — static T1 guard still enforced"
fi

if [ "$BEHAVIORAL" = "1" ]; then
  TMP_DIR="$(mktemp -d)"
  trap 'rm -rf "$TMP_DIR"' EXIT

  # -------------------------------------------------------------------------
  # T2: inline-SVG fixture renders end-to-end. swiss-positive.html carries an
  # inline <svg>; with the old defect, document.querySelectorAll('*') hits the
  # SVG subtree and the render dies with "className.includes is not a function".
  # -------------------------------------------------------------------------
  echo "T2: html2pptx.js survives the inline-SVG fixture (swiss-positive.html)..."
  OUT_PPTX="$TMP_DIR/inline-svg.pptx"
  if T2_OUT="$(cd "$SCRIPTS_DIR" && node html2pptx.js "$SVG_FIXTURE" "$OUT_PPTX" 2>&1)"; then
    # The output must also be a structurally valid pptx zip.
    if python3 - "$OUT_PPTX" <<'PY'
import sys, zipfile
path = sys.argv[1]
if not zipfile.is_zipfile(path):
    sys.exit(1)
with zipfile.ZipFile(path) as z:
    names = set(z.namelist())
sys.exit(0 if {"ppt/presentation.xml", "[Content_Types].xml"} <= names else 1)
PY
    then
      pass "T2 inline-SVG slide rendered to a valid .pptx (no SVGAnimatedString crash)"
    else
      fail "T2 inline-SVG render produced an invalid .pptx (missing required PowerPoint parts)" \
           "Defect class: silent deck corruption after surviving the SVG walk"
    fi
  else
    fail "T2 SVGAnimatedString crash class: html2pptx.js aborted on an inline-SVG slide" \
         "$T2_OUT"
  fi

  # -------------------------------------------------------------------------
  # T3: the rules-2/3 probe fixture must fail with VALIDATION errors, not a
  # JS crash — the graceful-failure contract that separates author-fixable
  # slide errors from pipeline-killing exceptions.
  # -------------------------------------------------------------------------
  echo "T3: html2pptx.js rejects html2pptx-behavior.html gracefully (validation, not crash)..."
  T3_OUT="$(cd "$SCRIPTS_DIR" && node html2pptx.js "$BEHAVIOR_FIXTURE" "$TMP_DIR/behavior.pptx" 2>&1)"
  T3_EXIT=$?
  if [ "$T3_EXIT" -eq 0 ]; then
    fail "T3 rules-2/3 probe fixture unexpectedly rendered (validation gate for gradients / styled text elements is gone)"
  elif echo "$T3_OUT" | grep -q 'is not a function'; then
    fail "T3 SVGAnimatedString-style JS crash while processing the probe fixture (expected a validation error)" \
         "$T3_OUT"
  elif echo "$T3_OUT" | grep -qE 'gradients are not supported|not text elements'; then
    pass "T3 probe fixture rejected with its designed rule-2/3 validation errors"
  else
    fail "T3 probe fixture failed for an unrecognized reason (not the designed rule-2/3 validation errors)" \
         "$T3_OUT"
  fi
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
