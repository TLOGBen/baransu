#!/usr/bin/env bash
# checks.sh — look at an encoded film the way a motion director would. ffmpeg only.
#
#   checks.sh contact out/final.mp4            → out/contact.png   2 frames/s, 6 across: the whole film at a glance
#   checks.sh strip   out/final.mp4 4.2 [12]   → out/strip.png     12 consecutive frames from 4.2s: pops and overlaps
#   checks.sh phone   out/final.mp4            → out/phone.png     360px wide, 1 frame/s: does it read on a phone?
#   checks.sh loop    out/final.mp4            → out/loop_check.mp4 played twice back to back: watch the seam
#   checks.sh probe   out/final.mp4            → duration, fps, size, audio streams
#   checks.sh refs    ref.mp4 [0.5]            → refs/frames/0001.png… one frame per 0.5 s + refs/tile.png: read a reference before copying its grammar
#   checks.sh audio   out/final.mp4            → audio.wav + waveform.png: the mix alone — every cut a peak? does the ending resolve?
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
  audio)   ffmpeg -v error -y -i "$in" -vn -ac 2 -ar 48000 "$out/audio.wav"; ffmpeg -v error -y -i "$out/audio.wav" -filter_complex "showwavespic=s=1600x240:colors=#2B45F0|#9A9890:split_channels=1" -frames:v 1 "$out/waveform.png"; echo "$out/waveform.png" ;;
  refs)    every=${3:-0.5}; mkdir -p "$out/refs/frames"; ffmpeg -v error -y -i "$in" -vf "fps=1/$every,scale=480:-1" "$out/refs/frames/%04d.png"
           n=$(ls "$out/refs/frames" | wc -l); ffmpeg -v error -y -framerate 1 -i "$out/refs/frames/%04d.png" -vf "scale=240:-1,tile=8x$(( (n+7)/8 ))" -frames:v 1 "$out/refs/tile.png"; echo "$out/refs/tile.png ($n frames)" ;;
  *) echo "unknown check: $cmd" >&2; exit 2 ;;
esac
