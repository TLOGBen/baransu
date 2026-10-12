# Finishing — loops, export, platform limits

Technique reference for the last mile of Phase 5 (`5-post.md` § 4): a loop with no seam in picture or sound, exports that survive the platform, the poster. Sound sync and loudness are in `beat-grid.md` § Sync and measurement; the motion-blur look is chosen in `pipeline.md` § Motion blur; the export review is `review.md` § Review the export.

## Loops

- **Render frames 0 to N − 1, never N.** Frame N is frame 0 again; showing it twice is the hiccup at the seam.
- **The last frame equals the first**, position and velocity included, cursor included (`springs.md` § `loopT`): every `track()` ends on its starting value with enough time to settle.
- **Drive every loop from `phase = frame / N` with whole cycles**: a square turns exactly 90° per loop, a wave completes exactly two cycles, all noise is periodic in the loop length. For organic drift, sample noise **along a circle** (`noise(cos(2π·phase)·r, sin(2π·phase)·r)`), so it returns to where it started.
- **Run a motion through frame 0.** A wobble or a settle that continues across the seam (one loop's 3-bounce wobble at 14 % ran straight through frame 0) hides it better than a hold that waits for it.
- **Frame 0 is a finished composition**: it is on screen while a GIF loads and as the poster.
- **The codec pads the audio.** AAC adds about 16 ms of padding past the video, so the file starts on a hard step and a looping player stops the sound hard at the end, plays the padding as silence and restarts hard. Keep the seamless WAV as the master (and for a post that loops twice in the file); for a single-loop MP4, add a 2 ms raised-cosine fade to the first and last ~96 samples only. `sfx.mjs --loop` wraps tails past the end to the start.
- **Anything that marks one member of a repeated set completes whole cycles too.** A ring of 12 identical dots turning 1/12 of a turn per loop looks seamless, because each dot lands where its neighbour started; give one dot the accent and it jumps a slot at the seam. Turn the ring a full turn (or move the accent with it).
- **Text never straddles the seam**: it enters after frame 0 and leaves before the end, so the seam falls in a gap, not mid-read.
- **Start from `assets/motion/loop-template.html`**: phase-driven whole cycles, `loopNoise()` (noise along a circle), `wrappedSpring()` (a settle evaluated across the wrap so it rings through frame 0), and `?seam=1`, which draws frame N − 1 beside frame 0.
- **Check the seam on stills before any render**: `render.mjs stills --at <DUR − 1/fps>,0,<1/fps>` must read as three consecutive frames. Then, on the master, `checks.sh loop` (or `ffmpeg -stream_loop 2 -i out/anim.mp4 -c copy out/loop_check.mp4`) plays it three times back to back; watch and listen at the seam.

## Export

```
# MP4 for a post: H.264 High, yuv420p, plays at once
ffmpeg -framerate 24 -i out/frames/%04d.png -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 18 -movflags +faststart out/anim.mp4

# GIF: one palette for the whole clip (no colour flicker between frames), 1200 px wide
ffmpeg -framerate 24 -i out/frames/%04d.png -vf "scale=1200:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 out/anim.gif
```

`render.mjs full` already encodes H.264 yuv420p CRF 16 with `+faststart`; the commands above are for frames rendered elsewhere or a GIF. MP4 for posts; GIF for articles and inline loops, only when asked.

**The GIF timing trap.** GIF delays are stored in hundredths of a second, so a 24 fps frame (41.7 ms) cannot be stored exactly; rounding every frame to 40 ms runs the loop 4 % fast and off the beat grid. Alternate: five frames at 40 ms, then one at 50 ms, which keeps a 6-second loop at exactly 6.00 s. GIFs have no gradients that survive: flat colours, or a dithered palette.

**The poster.** `out/poster.png` is the last frame (or the strongest key, when the last frame is an end card that does not represent the film); it must stand alone.

## Platform limits

X, as of 2026-10 (platform limits change; check its media docs before shipping):

| Spec | GIF | Video |
|---|---|---|
| size / length | 15 MB | 140 s without a paid tier |
| frame size | up to 1280 × 1080 | 1920 × 1080 for 16:9 |
| frames and speed | at most 350 frames (about 14.5 s at 24 fps; a 4–6 s loop is 96–144 frames) | up to 60 fps |
| format | one palette, loop forever | H.264 High, yuv420p, AAC |
| a sensible default | 1200 px wide, 24 fps | CRF 18, faststart |

Common canvases: 1920 × 1080 (16:9), 1080 × 1080 (1:1), 1080 × 1350 (4:5), 1080 × 1920 (9:16); X accepts 1:3 to 3:1 (`pipeline.md` § Formats). Platform UI covers the safe margins (`L.safe`).
