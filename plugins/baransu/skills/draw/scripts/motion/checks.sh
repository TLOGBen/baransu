#!/usr/bin/env bash
# checks.sh — look at an encoded film the way a motion director would. ffmpeg only.
#
# Every output is named for the input file: <base> is its name without the extension, so the master
# out/<slug>.mp4 gives out/check/<slug>.contact.png and the sibling out/<slug>-9x16.mp4 gives
# out/check/<slug>-9x16.contact.png — checking the master and each sibling never overwrites one sheet with another,
# and the check/ folder keeps them apart from render.mjs's dailies of the page (out/<slug>.contact.png, .phone.png).
#
#   checks.sh contact out/<slug>.mp4          → out/check/<slug>.contact.png      2 frames/s, 6 across: the whole film at a glance
#   checks.sh strip   out/<slug>.mp4 4.2 [12] → out/check/<slug>.strip-4.2.png    12 consecutive frames from 4.2s: pops and overlaps
#   checks.sh phone   out/<slug>.mp4          → out/check/<slug>.phone.png        360px wide, 1 frame/s: does it read on a phone?
#   checks.sh loop    out/<slug>.mp4          → out/check/<slug>.loop_check.mp4   played twice back to back: watch the seam
#   checks.sh probe   out/<slug>.mp4          → duration, fps, size, audio streams
#   checks.sh refs    ref.mp4 [0.5]           → refs/<base>/frames/0001.png… one frame per 0.5 s + refs/<base>/tile.png: read a reference before copying its grammar
#   checks.sh audio   out/<slug>.mp4          → out/check/<slug>.audio.wav + out/check/<slug>.waveform.png: the mix alone — every cut a peak? does the ending resolve?
#
# Outputs land in check/ beside the input (refs/ beside the input for refs) unless OUT=dir is set.
set -euo pipefail
cmd=${1:-}; in=${2:-}
[ -n "$cmd" ] && [ -f "$in" ] || { sed -n '2,17p' "$0"; exit 2; }
if [ "$cmd" = refs ]; then out=${OUT:-$(dirname "$in")}; else out=${OUT:-$(dirname "$in")/check}; fi
base=$(basename "$in"); base=${base%.*}
o="$out/$base"
mkdir -p "$out"
case "$cmd" in
  contact) ffmpeg -v error -y -i "$in" -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 "$o.contact.png"; echo "$o.contact.png" ;;
  strip)   t=${3:?time}; n=${4:-12}; ffmpeg -v error -y -ss "$t" -i "$in" -vf "scale=320:-1,tile=${n}x1" -frames:v 1 "$o.strip-$t.png"; echo "$o.strip-$t.png" ;;
  phone)   ffmpeg -v error -y -i "$in" -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 "$o.phone.png"; echo "$o.phone.png" ;;
  loop)    ffmpeg -v error -y -stream_loop 1 -i "$in" -c copy "$o.loop_check.mp4"; echo "$o.loop_check.mp4" ;;
  probe)   ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate -of default=nw=1 "$in" ;;
  audio)   ffmpeg -v error -y -i "$in" -vn -ac 2 -ar 48000 "$o.audio.wav"; ffmpeg -v error -y -i "$o.audio.wav" -filter_complex "showwavespic=s=1600x240:colors=#2B45F0|#9A9890:split_channels=1" -frames:v 1 "$o.waveform.png"; echo "$o.waveform.png" ;;
  refs)    every=${3:-0.5}; r="$out/refs/$base"; rm -rf "$r/frames"; mkdir -p "$r/frames"; ffmpeg -v error -y -i "$in" -vf "fps=1/$every,scale=480:-1" "$r/frames/%04d.png"
           n=$(ls "$r/frames" | wc -l); ffmpeg -v error -y -framerate 1 -i "$r/frames/%04d.png" -vf "scale=240:-1,tile=8x$(( (n+7)/8 ))" -frames:v 1 "$r/tile.png"; echo "$r/tile.png ($n frames)" ;;
  *) echo "unknown check: $cmd" >&2; exit 2 ;;
esac
