# Beat grid and sound — score it to the picture

Technique reference for sound. Phase 1 measures a supplied track (the picture's timing hangs off its grid); Phase 2 cuts on beats and changes layout on bars; Phase 5 scores, mixes, syncs and measures (`5-post.md` § 2).

Sound is where "AI video" starts feeling like a film. Two paths: if a track is supplied, measure it; if not, synthesize on the same timeline as the picture. Either way the picture and the sound share one grid, and the model, which cannot listen, checks the result by measuring the decoded audio.

## Measure a supplied track

```
python3 scripts/motion/beats.py song.wav --out beats.json [--bpm 120] [--start 12.4 --dur 15]
```

Writes `{ bpm, beat, start, duration, beats, downbeats, hits }` (numpy + ffmpeg only). The animation reads this file:

| Field | Put here |
|---|---|
| `beats` | small state changes (a toggle flips, a card enters) |
| `downbeats` | big moments: scene cuts, the hook, the logo lockup |
| `hits` | SFX — the strongest onsets, which are not always on the grid |

Start the film on a downbeat (`--start` at the chosen downbeat). Pass a `--bpm` hint when the song's tempo is known; the estimator then searches ±4 bpm around it and does not pick a half- or double-time grid. A royalty-free track near 120 bpm (0.5 s per beat, 2 s per bar) is the easiest to cut to: 7–8 bars is a 14–16 s piece.

**Limits of the estimator.** `beats.py` is numpy-only autocorrelation: solid on a steady electronic or pop track, weaker on a drifting tempo (live drums, rubato). On those, pass `--bpm` and `--start` from a known downbeat, analyse a 15 s window with `--dur`, and read `beats.png` to confirm the grid lands on the kicks before building to it. With supplied music, listen to (or measure) the detected beats before aligning the whole film to them.

## The grid in the film

`Motion.beatGrid(bpm)` gives `at(n)`, `index(t)`, `phase(t)`, `pulse(t)`, `isDown(n)`, so visuals can be written in beats rather than seconds.

- **Frames per beat** = fps × 60 / BPM (120 BPM at 24 fps = 12 frames). At 128 BPM and 30 fps it is 14.06: compute every beat from time (`n × 60 / BPM`) and round each one; adding a rounded 14 again and again drifts 2 frames off the music after 32 beats.
- **Cut on the beat, change the layout on the bar** (every 4 beats). Changing everything on every beat wears the viewer out.
- Place each click on a beat (`GRID.at(n)`); land transitions and camera settles on beats or downbeats.

## Synthesize when there is no track

Compose in code at the film's tempo: a pulse lead, a triangle bass, noise drums, chords on bar lines. The point is not musical ambition; it is that every cut lands exactly on a beat the picture already knows. Keep the mix below the SFX and cut it hard on the last downbeat. Synthesize; no samples, no downloads, nothing to license (or use assets the user is licensed to publish).

Two beds are ready to run for any film (they only need Node, no canvas):

```
node scripts/hand-drawn/scripts/music.mjs out/bed.wav --bpm 120 --dur 15 [--quiet 6.0-8.5] [--end 14.6]   # ukulele strums + bell motif + shaker + soft kick
node scripts/hand-drawn/scripts/chiptune.mjs out/bed.wav …                                               # a game score with sections on absolute times
node scripts/motion/sfx.mjs out/cues.json out/mix.wav --bed out/bed.wav --bed-gain 0.6
```

Pass the same `--bpm` the picture uses (`Motion.beatGrid(bpm)`); `--quiet a-b` holds one soft chord through a serious beat, `--end` lands the final strum — put the logo lockup's spring start at `--end` so the logo lands *on* the resolve, not after it. For a different mood write a sibling of `music.mjs` (same shape: oscillators and noise on a beat grid, written as WAV) rather than reaching for samples. `references/motion/hand-drawn/sound.md` describes both scripts.

**Score from frame numbers.** One prompt can name every event by frame (`pinch bloops at 112, 113, 114`, `merge blups at 319`) and the bed by bars (`120 BPM, four 3/4 bars of 90 frames starting on frame 67`); a pad can follow a light's flicker, pour bloops can rise through a pentatonic scale, a landing can be pitched by its squash. A few well-placed sounds are enough for a sample: a click at the selection, a soft movement cue, a restrained tone when a view settles.

## UI sounds from the picture's timeline

```
node scripts/motion/render.mjs beats --html index.html --beats beats.json   # also writes out/cues.json from window.timeline()
node scripts/motion/sfx.mjs out/cues.json out/mix.wav [--bed song.wav --bed-gain 0.8] [--loop]
node scripts/motion/render.mjs full --html index.html --audio out/mix.wav
```

Cues come from the picture: `window.timeline()` lists `{t, type}` for every click, swap and impact, so sound and visuals cannot drift apart. `sfx.mjs` synthesizes each type (`click tick key pop press release toggle whoosh impact riser chime success`), places each sound so its *measured peak* lands on the cue (that is where the ear hears the hit; placing the file start there reads as late), wraps tails past the end to the start with `--loop`, and trims the mix toward −14 LUFS with a −1 dBFS ceiling.

Rules that survived real films:

- vary `gain` and type across repeats so eight clicks do not sound pasted
- no continuous "pencil scratch" bed under drawing animation; it fights everything
- every hit in the picture gets a sound; a cut with no sound reads as a mistake
- keep individual SFX at 0.3–0.6 so the first mix does not clip against the bed
- duck the bed 3–4 dB under the biggest hit
- sound derived from the picture can carry distance and pan; sound travels at 343 m/s, so far events are heard late (`chapters.md`)

## Sync and measurement

**When the sound lands.** Default: a hit's peak lands **one frame after** its visual event — write each cue in `window.timeline()` at `t + 1 / fps` (`sfx.mjs` puts the measured peak on the cue). Light reaches us before sound, and a sound that arrives before its picture feels wrong sooner than one slightly late (broadcast sync tolerances allow more audio lag than audio lead); the published loops that held up all placed every hit, and the bed's kicks, one frame after the picture. The exception that survived earlier films: when the visual event is a slow approach to a contact (a cursor easing onto a button), cueing ~0.03 s before the contact frame read as synced, because the eye anticipates the touch. A cue that lands late after the event reads as broken in both cases.

**The picture works muted first.** Feeds play video silent until someone taps; the story must read without sound.

**Measure, do not listen.** Every sound fix in the published loops came from measuring the decoded audio. On the encoded master (`checks.sh audio` gives the WAV and a waveform):

| Measure | Target | When it is off |
|---|---|---|
| each hit's first waveform peak | on frame + 1, to the sample | a tone that starts at phase 0 or passes through a waveshaper peaks 2–11 ms late: start tones in **cosine phase** with a 0.5–1 ms attack, so the attack ends on a crest at exactly `(frame + 1) × samples per frame`; give a kick a 3 ms transient (its level falls to 65 % within 3 ms) so its first lobe is its largest |
| each hit over the bed | 3–6 dB louder (K-weighted, first 60 ms of the hit minus the bed) | trim the hit bus, then each hit; raise the quiet ones |
| loudness | about −14 LUFS integrated (a common target for social and web video) | `sfx.mjs` uses an RMS stand-in; when exactness matters, finish with `ffmpeg -af loudnorm=I=-14:TP=-1.5` (or `TP=-1`) |
| loudness in the **phone band** (200 Hz–6 kHz) | close to the full-band figure | a mix with most of its energy under 60 Hz (one first mix: 80 % under 60 Hz, 3.5 % in 150 Hz–6 kHz) plays as nothing on a phone speaker: raise bass notes an octave, shorten the kick (~80 ms) with a ~190 Hz knock, brighten and raise the pad |
| true peak after encoding | under −1 dBTP on the **decoded** MP4 | AAC lifts the peak (−1.3 → −0.4 dBTP in one loop): limit the WAV to about −2.2 dBTP |
| limiter gain reduction | under ~1.5 dB | partials that crest on the same sample get squashed: put even harmonics out of phase with the kick, or lower what sits under the big hit |
| DC offset | zero | subtract each channel's loop mean |
| spectrum | nothing above ~8 kHz for UI and metallic tings; mono-safe | low-pass the bright partials; check the mono fold-down |

Render the audio twice and keep the second pass when the synth has any warm-up state (a gain node that starts at full volume, a compressor that adds delay). Check the seam: no click where the loop wraps; a 48 kHz stereo WAV as the master.

```
# music + effects, mixed, normalized, muxed under the picture (when not using sfx.mjs's own mix)
ffmpeg -i out/anim.mp4 -i music.wav -i sfx.wav -filter_complex "[1:a][2:a]amix=inputs=2:duration=first,loudnorm=I=-14:TP=-1:LRA=11[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/final.mp4
```

The AAC padding at a loop seam is handled in `finishing.md` § Loops.
