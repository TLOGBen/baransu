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

if out=$(node "$R" hash --html index.html --t 4.5 --format 1:1 --out out11 2>&1) && echo "$out" | grep -q DETERMINISTIC && out=$(node "$R" stills --html index.html --at 0.6,4.9 --format 16:9 --out out169 2>&1) && [ -s out169/stills.png ]; then
  w=$(ffprobe -v error -show_entries stream=width -of csv=p=0 out169/stills.png)
  if [ "$w" = "640" ]; then ok "T6 one timeline, three formats (1:1 hash deterministic, 16:9 stills tile 2×320)"; else bad "T6 stills width" "$w"; fi
else bad "T6 formats" "$out"; fi
if out=$(node "$R" contact --html index.html --dur 1 --all --safe --out outs 2>&1) && [ -s outs/contact-9x16.png ] && [ -s outs/contact-1x1.png ] && [ -s outs/contact-16x9.png ]; then ok "T6b a contact sheet per format with the safe area drawn"; else bad "T6b contact --all --safe" "$out"; fi
if out=$(node "$R" animatic --html index.html --dur 1 --out outa 2>&1) && [ -s outa/animatic.mp4 ] && ffprobe -v error -show_entries stream=width,r_frame_rate -of csv=p=0 outa/animatic.mp4 | grep -q '540,24/1'; then ok "T7 animatic is 24 fps at half size"; else bad "T7 animatic" "$out"; fi
if out=$(node "$R" full --html index.html --from 0.5 --to 1 --sub 1 --fps 12 --out outc 2>&1) && [ -s outc/part-0.50-1.00.mp4 ] && echo "$out" | grep -q 'join chunks'; then ok "T8 chunked render names the part and prints the concat"; else bad "T8 chunk" "$out"; fi
if out=$(bash "$SKILL/scripts/motion/checks.sh" refs outc/part-0.50-1.00.mp4 0.25 2>&1) && [ -s outc/refs/tile.png ]; then ok "T9 checks.sh refs extracts reference frames"; else bad "T9 refs" "$out"; fi
if out=$(bash "$SKILL/scripts/motion/checks.sh" audio out/final.mp4 2>&1) && [ -s out/audio.wav ] && [ -s out/waveform.png ]; then ok "T9b checks.sh audio writes the mix alone and its waveform"; else bad "T9b audio" "$out"; fi
if out=$(node "$SKILL/scripts/motion/grab.mjs" "file://$SKILL/assets/motion/explainer-template.html" --out grab --wait 200 2>&1) && [ -s grab/manifest.json ] && [ -s grab/shot-9x16.png ] && python3 -c "import json,sys; m=json.load(open('grab/manifest.json')); sys.exit(0 if m['title'] and m['body']['fontFamily'] else 1)"; then ok "T10 grab.mjs writes screenshots and a manifest with computed type"; else bad "T10 grab" "$out"; fi

cp "$SKILL/assets/diagram/template-seek.html" "$W/flow.seek.html"
if out=$(node "$R" hash --html flow.seek.html --selector svg --w 1200 --h 750 --t 2.0 --out out-seek 2>&1) && echo "$out" | grep -q DETERMINISTIC; then ok "T5 seek-overlay diagram renders deterministically through the same pipeline"; else bad "T5 seek hash" "$out"; fi

echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
