#!/usr/bin/env bash
# /draw motion toolchain, behavioural layer: render the bundled seek(t) template
# through Playwright + ffmpeg and prove the contract the skill promises —
#   T1 render.mjs hash   → DETERMINISTIC (same t, same pixels)
#   T2 render.mjs contact → contact.png + cues.json from window.timeline()
#   T3 render.mjs full --sub 2 with the sfx mix → an H.264/AAC mp4 of the right length
#   T4 verify-page.mjs on the explainer template → no console errors, no horizontal scroll
# SKIPs (exit 0 with a notice) when node, ffmpeg, or a launchable Playwright
# Chromium is absent — the static guards in tests/scripts/test_draw_skill.py
# still run. A present toolchain that fails is a real failure.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$ROOT/plugins/baransu/skills/draw"
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT

skip() { echo "SKIP test-draw-toolchain behavioral layer: $1"; exit 0; }
command -v node >/dev/null || skip "node not installed"
command -v ffmpeg >/dev/null || skip "ffmpeg not installed"
node -e "import('playwright').catch(()=>import(require('child_process').execSync('npm root -g').toString().trim()+'/playwright/index.mjs')).then(m=>{const pw=m.chromium?m:m.default;return pw.chromium.launch().then(b=>b.close())}).catch(e=>{console.error(e.message);process.exit(3)})" >/dev/null 2>&1 || skip "playwright chromium not launchable"

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "  PASS: $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL: $1"; [ -n "${2:-}" ] && echo "        $2"; }

cp "$SKILL/assets/motion/seek-template.html" "$W/index.html"; cp "$SKILL/assets/motion/motion.js" "$W/"
cd "$W"
R="$SKILL/scripts/motion/render.mjs"

if out=$(node "$R" hash --html index.html --t 4.5 --out out 2>&1) && echo "$out" | grep -q DETERMINISTIC; then ok "T1 hash is deterministic"; else bad "T1 hash" "$out"; fi
if out=$(node "$R" contact --html index.html --out out 2>&1) && [ -s out/contact.png ] && [ -s out/cues.json ]; then ok "T2 contact sheet + cues.json"; else bad "T2 contact" "$out"; fi
if out=$(node "$SKILL/scripts/motion/sfx.mjs" out/cues.json out/mix.wav 2>&1) && [ -s out/mix.wav ]; then ok "T3a sfx mix"; else bad "T3a sfx" "$out"; fi
if out=$(node "$R" full --html index.html --dur 2 --fps 24 --sub 2 --audio out/mix.wav --out out 2>&1) && [ -s out/final.mp4 ]; then
  probe=$(ffprobe -v error -show_entries stream=codec_name -show_entries format=duration -of csv=p=0 out/final.mp4 | tr '\n' ' ')
  if echo "$probe" | grep -q h264 && echo "$probe" | grep -q aac && echo "$probe" | grep -qE "(^| )2\.0"; then ok "T3b full render h264+aac 2.0s ($probe)"; else bad "T3b probe" "$probe"; fi
else bad "T3b full render" "$out"; fi
if out=$(node "$SKILL/scripts/motion/verify-page.mjs" "$SKILL/assets/motion/explainer-template.html" --out shots 2>&1); then
  if echo "$out" | grep -q '"errors": \[\]' && ! echo "$out" | grep -q '"hscroll": true'; then ok "T4 explainer template verifies clean"; else bad "T4 verify-page report" "$out"; fi
else bad "T4 verify-page exit" "$out"; fi

echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
