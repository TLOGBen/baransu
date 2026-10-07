#!/usr/bin/env bash
# checks.sh — look at an encoded film the way a motion director would. ffmpeg only.
#
#   checks.sh contact out/final.mp4            → out/contact.png   2 frames/s, 6 across: the whole film at a glance
#   checks.sh strip   out/final.mp4 4.2 [12]   → out/strip.png     12 consecutive frames from 4.2s: pops and overlaps
#   checks.sh phone   out/final.mp4            → out/phone.png     360px wide, 1 frame/s: does it read on a phone?
#   checks.sh loop    out/final.mp4            → out/loop_check.mp4 played twice back to back: watch the seam
#   checks.sh probe   out/final.mp4            → duration, fps, size, audio streams
#
# Every output lands next to the input unless OUT=dir is set.
set -euo pipefail
cmd=${1:-}; in=${2:-}
[ -n "$cmd" ] && [ -f "$in" ] || { sed -n '2,12p' "$0"; exit 2; }
out=${OUT:-$(dirname "$in")}
mkdir -p "$out"
case "$cmd" in
  contact) ffmpeg -v error -y -i "$in" -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 "$out/contact.png"; echo "$out/contact.png" ;;
  strip)   t=${3:?time}; n=${4:-12}; ffmpeg -v error -y -ss "$t" -i "$in" -vf "scale=320:-1,tile=${n}x1" -frames:v 1 "$out/strip.png"; echo "$out/strip.png" ;;
  phone)   ffmpeg -v error -y -i "$in" -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 "$out/phone.png"; echo "$out/phone.png" ;;
  loop)    ffmpeg -v error -y -stream_loop 1 -i "$in" -c copy "$out/loop_check.mp4"; echo "$out/loop_check.mp4" ;;
  probe)   ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate -of default=nw=1 "$in" ;;
  *) echo "unknown check: $cmd" >&2; exit 2 ;;
esac
