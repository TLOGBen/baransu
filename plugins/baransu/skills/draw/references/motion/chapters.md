# Long form — chapters, guides, and subagents

A 2-minute music video or a 5-minute history film is not one `seek(t)` scene; it is a dozen chapters that must look like one film. Two published productions show the pattern that holds up: a shared guide written *before* the chapters, one file per chapter, and a renderer that treats the film as chunks.

## The shape

```
film/
  ANIMATION_GUIDE.md      the style bible every chapter obeys — written first, by the lead
  STORYBOARD.md           every chapter: time range, beats, reads, transitions, sound cues
  src/core.js             palette, paper, camera, easing, the shared primitives
  src/timeline.js         chapter boundaries, loops, the transition vocabulary
  src/ch/c01_*.js …       one file per chapter, each a function of local time
  data/timings.json       narration or lyric timestamps, so beats lock to words
  web/events.js           derives sound cues from the picture (each hit, with distance and pan)
  tools/render.mjs        headless Chromium → ffmpeg in resumable chunks
  tools/mix.py            score + sound design + narration → mix
```

## ANIMATION_GUIDE.md before any chapter

The guide carries what a chapter author (a subagent, or you in the next session) cannot infer from one chapter: the palette and paper, the character or type system and its identity lock, the camera language, the transition vocabulary and when each is allowed, the exposure (ones / twos / holds), the line-weight ladder, what is banned. Paste the style bible verbatim at the top of every chapter file as a comment; it stops the look drifting between sessions.

The published music video wrote the guide *and then* the storyboard after a first generation, then split nine chapters across subagents in parallel. Ask for both files by name in the brief.

## Chapters as subagents

Each chapter is an independent function of local time with no shared mutable state, which is exactly what makes it safe to hand to a separate agent. The lead owns: the guide, the storyboard, `core.js`, the cut list, and the final review. A chapter agent owns one `src/ch/cNN_*.js` and must: read the guide, use only `core.js` primitives, start and end on the transition the storyboard assigns, render its own contact sheet and strip before handing back, and report what it could not fit. The lead reviews every chapter's sheet against the guide before stitching; a chapter that invents a new transition or palette is sent back, not patched.

## Narration and lyrics

Lock beats to word timestamps (`data/timings.json`), never to a stopwatch; the start time of the word that names the thing is where the thing appears. Lyrics are not text on screen by default: act the meaning. When text *is* the design (kinetic captions), decide per section whether it goes huge or sits like subtitles, and leave composition room for it.

## Rendering long pieces

- Render in resumable chunks (10 s each): `render.mjs full --from 10 --to 20` per chunk, finished chunks are kept, a crash costs one chunk; `ffmpeg -f concat` joins the parts with the mix at the end (the command is printed after each chunk).
- Several page workers in parallel; frames are pure functions of time so order does not matter.
- Sound derived from the picture: each gun / click / footstep becomes a cue with distance and pan; sound travels at 343 m/s, so far events are heard late.
- A painterly finish (grain, vignette, letterbox, a filter blended over the frame) applied once in post, not per element.
- Software WebGL on a headless box runs around 1–2 s per 1080p frame; budget the full render accordingly and iterate on strips.

Attribution: the chapter/guide/subagent structure is described from `JohnHeibel/PDoomVideo` (ISC); the chunked renderer, picture-derived sound and narration timing from the public description of `WinterArc21/Battle-of-Austerlitz-Film` (no license granted, so nothing from it is copied — only the pattern is described).
