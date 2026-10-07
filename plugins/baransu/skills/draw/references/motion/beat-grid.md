# Sound — score it to the beat

Sound is where "AI video" starts feeling like a film. Two paths: if a track is supplied, measure it; if not, synthesize on the same timeline as the picture. Either way the picture and the sound share one grid.

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

In the film, `Motion.beatGrid(bpm)` gives `at(n)`, `index(t)`, `phase(t)`, `pulse(t)`, `isDown(n)` so visuals can be written in beats rather than seconds.

## Synthesize when there is no track

Compose in code at the film's tempo: a pulse lead, a triangle bass, noise drums, chords on bar lines. The point is not musical ambition; it is that every cut lands exactly on a beat the picture already knows. Keep the mix below the SFX and cut it hard on the last downbeat.

For hand-drawn pieces, `scripts/hand-drawn/scripts/music.mjs` (an original ukulele bed) and `chiptune.mjs` (a game score with sections placed on absolute times) are ready to run; see `references/motion/hand-drawn/sound.md`.

## UI sounds from the picture's timeline

```
node scripts/motion/render.mjs beats --html index.html --beats beats.json   # also writes out/cues.json from window.timeline()
node scripts/motion/sfx.mjs out/cues.json out/mix.wav [--bed song.wav --bed-gain 0.8] [--loop]
node scripts/motion/render.mjs full --html index.html --audio out/mix.wav
```

Cues come from the picture: `window.timeline()` lists `{t, type}` for every click, swap and impact, so sound and visuals cannot drift apart. `sfx.mjs` synthesizes each type (`click tick key pop press release toggle whoosh impact riser chime success`), places each sound so its *measured peak* lands on the cue (that is where the ear hears the hit; placing the file start there reads as late), wraps tails past the end to the start with `--loop`, and trims the mix toward −14 LUFS with a −1 dBFS ceiling.

Rules that survived real films:

- a cue ~0.03 s before the visual contact reads as synced; late reads as broken
- vary `gain` and type across repeats so eight clicks do not sound pasted
- no continuous "pencil scratch" bed under drawing animation; it fights everything
- every hit in the picture gets a sound; a cut with no sound reads as a mistake
- keep individual SFX at 0.3–0.6 so the first mix does not clip against the bed

Loudness target −14 LUFS for social platforms; `sfx.mjs` uses an RMS stand-in, so when exactness matters finish with `ffmpeg -af loudnorm=I=-14:TP=-1.5`.
