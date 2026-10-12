# Phase 5 — Post (後製)

**Settles:** the seams executed, the sound scored and synced, the master rendered in every format, loops and exports finished, the encoded file reviewed, the deliverable packaged. **Produces:** `out/cues.json`, `out/mix.wav`, `out/final.mp4` (+ `final-1x1` / `final-16x9` or the brief's formats), `out/loop_check.mp4`, `out/poster.png`, GIF if asked, contact / strip / probe sheets of the encoded master, `README.md` with the render commands, the completion report. **Gate:** the encoded master passes its own review; the report names the files, the checks that ran, and the scores.

Post works on the encoded file, not the page. The picture was approved in Shoot; post adds what only exists at the end — the cut as a whole, the sound, the codec, the platform — and checks that nothing was lost on the way.

## Concepts

- **The picture works muted first.** Feeds play video silent until someone taps; the story must read without sound.
- **Sound lands one frame after its picture.** Light reaches us before sound; a sound that arrives early feels wrong sooner than one slightly late (`beat-grid.md` § Sync and measurement).
- **The model cannot listen, so it measures.** Every sound decision is checked on the decoded audio: peak positions, levels over the bed, loudness, phone-band energy, true peak after encoding.
- **Review the export, not the source.** The codec, the audio padding, the platform's limits and the loop seam only exist in the encoded file.
- **Every delivered format is reviewed on its own.** A reflowed 9:16 is a different film from the 16:9 master.

## Steps

### 1. Execute the seams

Draw every transition chosen in Draft as geometry (`transitions.md`): the outgoing scene first, the incoming inside the clip or offset the helper returns; durations from the beat (0.25–0.4 s for a wipe or whip, ~0.6 s for a camera push on `ui`), landing the end of the transition on a beat. Write J- and L-cuts as cue times in `window.timeline()`.

### 2. Score and sync the sound

`beat-grid.md` is the technique. In order:

1. Cues from the picture: `window.timeline()` lists `{t, type}` for every click, swap and impact, at the visual event's time **plus one frame**; `render.mjs beats` writes `out/cues.json`.
2. The bed: the measured track (Phase 1), or a synthesized bed at the film's tempo (`music.mjs`, `chiptune.mjs`).
3. The mix: `sfx.mjs out/cues.json out/mix.wav [--bed …] [--loop]`, about −14 LUFS.
4. Measure, do not listen: every hit's first waveform peak on frame + 1, hits 3–6 dB over the bed, phone-band loudness, limiter under ~1.5 dB, DC removed, true peak checked again on the decoded MP4.

### 3. Render the master

Only after Shoot's gate: `render.mjs full --fps 60 --sub 4 --audio out/mix.wav` (`--all` for the three formats from one timeline; `--from/--to` chunks for long pieces). A full render is an Authorization PAUSE under a non-interactive driver. Choose the motion-blur look (`pipeline.md` § Motion blur) before it.

### 4. Finish

`finishing.md`: render frames 0 to N − 1; a motion through frame 0; the AAC padding handled at the seam; MP4 for posts, GIF only when asked (one palette, the delay trap), within the platform's limits; `out/poster.png` from the last frame (or the strongest key).

### 5. Review the export

`review.md` § Review the export: `checks.sh contact|strip|loop|probe` on the encoded master; a contact sheet every second and around every scene boundary; duration, dimensions, frame rate and an audio stream present; the final three-second hold; phone size; once muted and once with sound; the loop seam on its own. Fix the three most important defects and repeat — **at most three passes**; log timestamped findings; never mark an unrun check as passed.

### 6. Package and report

- Both formats (or every delivered format) open with the expected size, duration and audio.
- `README.md` with the exact render commands, so anyone re-renders without the chat; the source without secrets or dependency folders; licence notes; for client work the producer's package (`commission.md` § 6).
- The completion report (`SKILL.md` § Completion report): the file, the lane, the checks that ran and their results, the scores and rounds, what the budget cut, one line on what would make it better.

## Gate checklist

- [ ] every seam drawn as its named transition; J / L-cuts in cue times
- [ ] cues on frame + 1; hits 3–6 dB over the bed; −14 LUFS; phone band checked; true peak under −1 dBTP on the decoded file
- [ ] full render after Shoot's gate; every delivered format rendered
- [ ] frames 0 to N − 1; the seam clean in picture and sound; exports within platform limits
- [ ] the encoded master reviewed (sheets, probe, hold, muted and with sound, loop), at most three fix passes, findings logged
- [ ] package and README; the report states only checks that ran
