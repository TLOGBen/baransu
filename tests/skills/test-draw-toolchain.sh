#!/usr/bin/env bash
# /draw motion toolchain, behavioural layer: render the bundled seek(t) template
# through Playwright + ffmpeg and prove the contract the skill promises —
#   T1 render.mjs hash   → DETERMINISTIC (same t, same pixels)
#   T2 render.mjs contact → <slug>.contact.png + cues.json from window.timeline()
#   T3 render.mjs full --sub 2 with the sfx mix → an H.264/AAC <slug>.mp4 of the right length
#   T4 verify-page.mjs on the component example → no console errors, no horizontal scroll
#   T6-T8, T17 output names derive from --html (paper-plane.film.html → paper-plane.*); --name and --out-file override
#   T6b-T6e the primary format (--primary, the page's timeline().primary, --format alone, else 9:16) is unsuffixed, siblings suffixed
#   T9c checks.sh names every output for its input file, so master and siblings never overwrite each other
#   T11-T16 perf-check.mjs → template PASS (loop stops at rest), a blocked page FAILs on the
#           hard deadline, a non-D3D11 renderer on Windows is NOT-EVIDENCE whatever --backend says,
#           and NOT-EVIDENCE outranks a FAIL row in RESULT
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
# Same resolver the scripts use (browser.mjs): a bare import() of an absolute C:/ path fails on Windows.
(cd "$SKILL/scripts/motion" && node --input-type=module -e "import { loadPlaywright, chromiumPath, launchChromium } from './browser.mjs'; const pw = await loadPlaywright(); if (!pw) process.exit(3); const b = await launchChromium(pw, { executablePath: chromiumPath() }); await b.close();") >/dev/null 2>&1 || skip "playwright chromium not launchable"

PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); echo "  PASS: $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL: $1"; [ -n "${2:-}" ] && echo "        $2"; }

# The component example.
EX="$SKILL/assets/motion/component-example.html"
cp "$SKILL/assets/motion/seek-template.html" "$W/paper-plane.film.html"; cp "$SKILL/assets/motion/motion.js" "$W/"
cd "$W"
R="$SKILL/scripts/motion/render.mjs"

if out=$(node "$R" hash --html paper-plane.film.html --t 4.5 --out out 2>&1) && echo "$out" | grep -q DETERMINISTIC; then ok "T1 hash is deterministic"; else bad "T1 hash" "$out"; fi
if out=$(node "$R" contact --html paper-plane.film.html --out out 2>&1) && [ -s out/paper-plane.contact.png ] && [ -s out/cues.json ]; then ok "T2 contact sheet named from the film (paper-plane.contact.png) + cues.json"; else bad "T2 contact" "$out"; fi
if out=$(node "$SKILL/scripts/motion/sfx.mjs" out/cues.json out/mix.wav 2>&1) && [ -s out/mix.wav ]; then ok "T3a sfx mix"; else bad "T3a sfx" "$out"; fi
if out=$(node "$R" full --html paper-plane.film.html --dur 2 --fps 24 --sub 2 --audio out/mix.wav --out out 2>&1) && [ -s out/paper-plane.mp4 ] && [ ! -e out/final.mp4 ]; then
  probe=$(ffprobe -v error -show_entries stream=codec_name -show_entries format=duration -of csv=p=0 out/paper-plane.mp4 | tr '\n' ' ')
  if echo "$probe" | grep -q h264 && echo "$probe" | grep -q aac && echo "$probe" | grep -qE "(^| )2\.0"; then ok "T3b full render paper-plane.mp4 h264+aac 2.0s ($probe)"; else bad "T3b probe" "$probe"; fi
else bad "T3b full render" "$out"; fi
if out=$(node "$SKILL/scripts/motion/verify-page.mjs" "$EX" --out shots 2>&1); then
  if echo "$out" | grep -q '"errors": \[\]' && ! echo "$out" | grep -q '"hscroll": true'; then ok "T4 component example verifies clean"; else bad "T4 verify-page report" "$out"; fi
else bad "T4 verify-page exit" "$out"; fi

if out=$(node "$R" hash --html paper-plane.film.html --t 4.5 --format 1:1 --out out11 2>&1) && echo "$out" | grep -q DETERMINISTIC && out=$(node "$R" stills --html paper-plane.film.html --at 0.6,4.9 --format 16:9 --primary 9:16 --out out169 2>&1) && [ -s out169/paper-plane-16x9.stills.png ] && [ ! -e out169/paper-plane.stills.png ]; then
  w=$(ffprobe -v error -show_entries stream=width -of csv=p=0 out169/paper-plane-16x9.stills.png)
  if [ "$w" = "640" ]; then ok "T6 one timeline, three formats (1:1 hash deterministic; a 16:9 sibling of a 9:16 primary is suffixed: paper-plane-16x9.stills.png tile 2×320)"; else bad "T6 stills width" "$w"; fi
else bad "T6 formats" "$out"; fi
# --all: the primary (9:16 by default) unsuffixed, the two siblings suffixed, no suffixed copy of the primary.
if out=$(node "$R" contact --html paper-plane.film.html --dur 1 --all --safe --out outs 2>&1) && [ -s outs/paper-plane.contact.png ] && [ -s outs/paper-plane-1x1.contact.png ] && [ -s outs/paper-plane-16x9.contact.png ] && [ ! -e outs/paper-plane-9x16.contact.png ] \
   && w=$(ffprobe -v error -show_entries stream=width,height -of csv=p=0 outs/paper-plane.contact.png) && [ "$w" = "1620,480" ]; then ok "T6b a contact sheet per format with the safe area drawn: the 9:16 primary unsuffixed (paper-plane.contact.png, 9:16 tiles), siblings paper-plane-1x1 / -16x9"; else bad "T6b contact --all --safe" "$out ${w:-}"; fi
# A 16:9 film: --format 16:9 alone makes 16:9 the primary (unsuffixed), and --all --primary 16:9 suffixes 9:16 instead.
if out=$(node "$R" contact --html paper-plane.film.html --dur 1 --format 16:9 --out out16 2>&1) && [ -s out16/paper-plane.contact.png ] && [ ! -e out16/paper-plane-16x9.contact.png ] \
   && out=$(node "$R" contact --html paper-plane.film.html --dur 1 --all --primary 16:9 --out out16all 2>&1) && [ -s out16all/paper-plane.contact.png ] && [ -s out16all/paper-plane-9x16.contact.png ] && [ -s out16all/paper-plane-1x1.contact.png ] && [ ! -e out16all/paper-plane-16x9.contact.png ] \
   && w=$(ffprobe -v error -show_entries stream=width,height -of csv=p=0 out16all/paper-plane.contact.png) && [ "$w" = "1620,152" ]; then ok "T6c a 16:9 primary (--format 16:9 alone, or --all --primary 16:9) is written unsuffixed with 16:9 tiles; 9:16 becomes the -9x16 sibling"; else bad "T6c 16:9 primary" "$out ${w:-}"; fi
# A page that declares its primary in window.timeline(): no flag needed, the run renders that format unsuffixed.
sed "s/duration: DUR, format: F,/duration: DUR, primary: '16:9', format: F,/" paper-plane.film.html > wide.film.html
if grep -q "primary: '16:9'" wide.film.html && out=$(node "$R" stills --html wide.film.html --at 0.6 --out outdecl 2>&1) && [ -s outdecl/wide.stills.png ] && echo "$out" | grep -q 'primary format 16:9 (declared by the page)' \
   && w=$(ffprobe -v error -show_entries stream=width,height -of csv=p=0 outdecl/wide.stills.png) && [ "$w" = "320,180" ] \
   && out=$(node "$R" stills --html wide.film.html --at 0.6 --format 9:16 --out outdecl 2>&1) && [ -s outdecl/wide-9x16.stills.png ]; then ok "T6d a page declaring primary '16:9' renders 16:9 unsuffixed (wide.stills.png 320×180) and its 9:16 sibling as wide-9x16.stills.png"; else bad "T6d declared primary" "$out ${w:-}"; fi
out=$(node "$R" still --html paper-plane.film.html --primary 2:1 --out outbad 2>&1); rc=$?
if [ "$rc" -eq 2 ] && echo "$out" | grep -q 'unknown --primary'; then ok "T6e an unknown --primary is refused"; else bad "T6e --primary validation (rc=$rc)" "$out"; fi
if out=$(node "$R" animatic --html paper-plane.film.html --dur 1 --name glider --out outa 2>&1) && [ -s outa/glider.animatic.mp4 ] && ffprobe -v error -show_entries stream=width,r_frame_rate -of csv=p=0 outa/glider.animatic.mp4 | grep -q '540,24/1'; then ok "T7 animatic is 24 fps at half size; --name replaces the slug (glider.animatic.mp4)"; else bad "T7 animatic" "$out"; fi
if out=$(node "$R" full --html paper-plane.film.html --from 0.5 --to 1 --sub 1 --fps 12 --out outc 2>&1) && [ -s outc/paper-plane.part-0.50-1.00.mp4 ] && join=$(echo "$out" | sed -n 's/^join chunks: //p') && echo "$join" | grep -q '^cd outc && .*paper-plane\.part-\*\.mp4.* paper-plane\.mp4$' \
   && cp out/mix.wav outc/ && jo=$( (eval "$join") 2>&1) && [ -s outc/paper-plane.mp4 ]; then ok "T8 chunked render names the part (paper-plane.part-0.50-1.00.mp4) and its printed concat joins into paper-plane.mp4"; else bad "T8 chunk" "$out ${jo:-}"; fi
if out=$(bash "$SKILL/scripts/motion/checks.sh" refs outc/paper-plane.part-0.50-1.00.mp4 0.25 2>&1) && [ -s outc/refs/paper-plane.part-0.50-1.00/tile.png ]; then ok "T9 checks.sh refs extracts reference frames into refs/<base>/"; else bad "T9 refs" "$out"; fi
if out=$(bash "$SKILL/scripts/motion/checks.sh" audio out/paper-plane.mp4 2>&1) && [ -s out/check/paper-plane.audio.wav ] && [ -s out/check/paper-plane.waveform.png ] && [ ! -e out/audio.wav ]; then ok "T9b checks.sh audio writes the mix alone and its waveform named for the film (check/paper-plane.audio.wav, .waveform.png)"; else bad "T9b audio" "$out"; fi
# The master and a sibling checked into one folder: each sheet is named for its input, none overwrites another,
# and the encoded-file checks land in out/check/, so they never replace render.mjs's dailies of the page.
cp out/paper-plane.mp4 out/paper-plane-1x1.mp4
printf 'dailies' > out/paper-plane.contact.png
C="$SKILL/scripts/motion/checks.sh"
if out=$( { bash "$C" contact out/paper-plane.mp4 && bash "$C" contact out/paper-plane-1x1.mp4 && bash "$C" phone out/paper-plane-1x1.mp4 && bash "$C" strip out/paper-plane-1x1.mp4 0.5 4 && bash "$C" loop out/paper-plane-1x1.mp4; } 2>&1) \
   && [ -s out/check/paper-plane.contact.png ] && [ -s out/check/paper-plane-1x1.contact.png ] && [ -s out/check/paper-plane-1x1.phone.png ] && [ -s out/check/paper-plane-1x1.strip-0.5.png ] && [ -s out/check/paper-plane-1x1.loop_check.mp4 ] \
   && [ "$(cat out/paper-plane.contact.png)" = dailies ] \
   && [ ! -e out/check/contact.png ] && [ ! -e out/check/phone.png ] && [ ! -e out/check/strip.png ] && [ ! -e out/check/loop_check.mp4 ]; then ok "T9c checks.sh names every output for its input in out/check/ (paper-plane.contact.png beside paper-plane-1x1.contact.png, .phone, .strip-0.5, .loop_check) and leaves the dailies sheet alone"; else bad "T9c checks.sh names" "$out"; fi
# node builds the file:// URL: "file://$SKILL" is file:///c/Users/... under Git Bash, which Chromium cannot open.
TPL_URL=$(node -e "console.log(require('url').pathToFileURL(process.argv[1]).href)" "$EX")
if out=$(node "$SKILL/scripts/motion/grab.mjs" "$TPL_URL" --out grab --wait 200 2>&1) && [ -s grab/manifest.json ] && [ -s grab/shot-9x16.png ] && python3 -c "import json,sys; m=json.load(open('grab/manifest.json')); sys.exit(0 if m['title'] and m['body']['fontFamily'] else 1)"; then ok "T10 grab.mjs writes screenshots and a manifest with computed type"; else bad "T10 grab" "$out"; fi

cp "$SKILL/assets/diagram/template-seek.html" "$W/flow.seek.html"
if out=$(node "$R" hash --html flow.seek.html --selector svg --w 1200 --h 750 --t 2.0 --out out-seek 2>&1) && echo "$out" | grep -q DETERMINISTIC; then ok "T5 seek-overlay diagram renders deterministically through the same pipeline"; else bad "T5 seek hash" "$out"; fi

P="$SKILL/scripts/motion/perf-check.mjs"
if out=$(node --check "$P" 2>&1) && out=$(node --check "$SKILL/scripts/motion/doctor.mjs" 2>&1); then ok "T11 perf-check.mjs and doctor.mjs parse"; else bad "T11 syntax" "$out"; fi
# --out-file names one output exactly; with --all it is refused before any browser starts (exit 2).
out=$(node "$R" full --html paper-plane.film.html --all --out-file outx/x.mp4 2>&1); rc=$?
if [ "$rc" -eq 2 ] && echo "$out" | grep -q 'out-file' && [ ! -e outx/x.mp4 ]; then ok "T17 --out-file with --all is refused before launch"; else bad "T17 --out-file refusal (rc=$rc)" "$out"; fi
# Template PASS: auto backend (ANGLE D3D11 on Windows, SwiftShader elsewhere); every budget row passes or skips.
if out=$(node "$P" "$EX" --timeout 90 2>&1) && echo "$out" | grep -q '^RESULT: PASS' && echo "$out" | grep -q '^PASS raf #1' && echo "$out" | grep -q '^PASS rest'; then ok "T12 perf-check passes the component example (raf per figure, rest)"; else bad "T12 perf-check example" "$(echo "$out" | grep -E '^(FAIL|NOT-EVIDENCE|RESULT)')"; fi
# A page that never yields: the hard deadline kills the browser and reports FAIL well inside the caller's patience.
printf '<!doctype html><meta charset=utf-8><title>block</title><figure class=fig>x</figure><script>for(;;){}</script>\n' > "$W/block.html"
s=$(date +%s); out=$(node "$P" "$W/block.html" --timeout 15 2>&1); rc=$?; el=$(( $(date +%s) - s ))
if [ "$rc" -eq 1 ] && [ "$el" -le 25 ] && echo "$out" | grep -q '^RESULT: FAIL' && echo "$out" | grep -q '^FAIL deadline'; then ok "T13 a blocked page fails on the hard deadline in ${el}s"; else bad "T13 perf-check deadline (rc=$rc, ${el}s)" "$(echo "$out" | grep -E '^(FAIL|PASS|RESULT)')"; fi
# Windows d3d11: a renderer that is not D3D11 (here forced to SwiftShader) is NOT-EVIDENCE and exits non-zero.
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*)
  printf '<!doctype html><meta charset=utf-8><title>gl</title><figure class=fig><canvas></canvas></figure><script>document.querySelector("canvas").getContext("webgl")</script>\n' > "$W/gl.html"
  out=$(node "$P" "$W/gl.html" --backend d3d11 --chrome-arg --use-angle=swiftshader --timeout 40 2>&1); rc=$?
  if [ "$rc" -ne 0 ] && echo "$out" | grep -q '^NOT-EVIDENCE renderer' && echo "$out" | grep -q '^RESULT: NOT-EVIDENCE'; then ok "T14 a non-D3D11 renderer on Windows d3d11 is NOT-EVIDENCE"; else bad "T14 perf-check renderer (rc=$rc)" "$(echo "$out" | grep -E '^(FAIL|NOT-EVIDENCE|PASS renderer|RESULT)')"; fi
  # Windows, any --backend: --backend swiftshader is never evidence for Windows Chrome, so it cannot PASS.
  out=$(node "$P" "$W/gl.html" --backend swiftshader --timeout 40 2>&1); rc=$?
  if [ "$rc" -ne 0 ] && echo "$out" | grep -q '^NOT-EVIDENCE renderer' && echo "$out" | grep -q '^RESULT: NOT-EVIDENCE'; then ok "T15 --backend swiftshader on Windows is NOT-EVIDENCE"; else bad "T15 perf-check swiftshader on Windows (rc=$rc)" "$(echo "$out" | grep -E '^(FAIL|NOT-EVIDENCE|SKIP renderer|PASS renderer|RESULT)')"; fi
  # Windows: a fallback renderer that also trips a FAIL row is still NOT-EVIDENCE, never a FAIL to fix.
  printf '<!doctype html><meta charset=utf-8><title>blockgl</title><figure class=fig><canvas></canvas></figure><script>document.querySelector("canvas").getContext("webgl");for(;;){}</script>\n' > "$W/block-gl.html"
  out=$(node "$P" "$W/block-gl.html" --backend swiftshader --timeout 15 2>&1); rc=$?
  if [ "$rc" -ne 0 ] && echo "$out" | grep -q '^FAIL deadline' && echo "$out" | grep -q '^NOT-EVIDENCE renderer' && echo "$out" | grep -q '^RESULT: NOT-EVIDENCE'; then ok "T16 a FAIL row under a non-D3D11 renderer on Windows still reads NOT-EVIDENCE"; else bad "T16 perf-check NOT-EVIDENCE over FAIL (rc=$rc)" "$(echo "$out" | grep -E '^(FAIL|NOT-EVIDENCE|PASS renderer|RESULT)')"; fi ;;
esac

echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
