# Maintained Diagrams — the Trio Contract

This file applies when a diagram lives in the USER's repository — a README
hero image, a docs-site figure, anything under `docs/architecture/` — and
will be redrawn over months by different hands (or the same hand with none
of today's context). Every per-type layout rule in this directory still
applies unchanged; the difference is lifecycle: the render is no longer
disposable — the diagram lives on as an editable source artifact bound to
the delivery contract below. This file is NOT
a diagram type — it is never routed to from §4.9/§4.10; the Render stage
reads it only when the output destination is the user's repository rather
than `.codex/book/` (see svg-rendering-rules §4.11).

## The three artifacts

A maintained diagram is three files that move together. Deliver all three,
or explicitly name which one is missing — never ship a partial trio
silently.

| Artifact | Contract |
|----------|----------|
| Source HTML | Self-contained: inline SVG + inline CSS, zero external fetches; the SVG carries `role="img"`, a `<title>`, and a `<desc>`. This is the file that gets edited — always. |
| Exported PNG | Regenerated from the source HTML EVERY time its content moves; never hand-edited, never resized, never patched in an image editor. A PNG that drifted from its HTML is a bug, not a shortcut. |
| Intent file | The redraw context that would otherwise die in the chat history: what is deliberately drawn, what is deliberately deferred, what visual direction to try next. If it is missing or stale, rebuilding it is part of the current task — not skippable. |

The trio exists because chat transcripts evaporate: when the only record
of what a figure was trying to say is a conversation log, the next editor
inherits pixels without reasoning — they copy yesterday's picture
faithfully while the system it depicts has already moved on.

## The intent file's four blocks

| Block | Holds | Never holds |
|-------|-------|-------------|
| Preserve | What is correctly drawn right now and must survive the next redraw | New ideas — an idea is not preserved until it is drawn |
| Proposed | Facts that are true but not yet drawn | Anything worded as though it were drawn already |
| Visual direction | Hierarchy / whitespace / line fixes to try on the next pass | Content changes disguised as styling notes |
| Sister boundaries | Scope owned by sibling diagrams, each named with its file path | Anything this diagram is itself responsible for drawing |

Keeping the four blocks separate is what protects a redraw from its two
recurring failure modes: drawing a proposal as though it had already
shipped (the figure then asserts a state the system never reached), and
letting a styling pass quietly widen its scope (visual notes smuggling in
new blocks).

## Evidence pass before redrawing

Before touching the source HTML, read in this fixed order:

1. The intent file (what did the last hand deliberately leave for you).
2. The current source HTML (what is actually drawn).
3. The shipped PNG, viewed at the size it actually renders (what readers
   really see).
4. The underlying facts — README, design docs, source files the diagram
   claims to depict.

Authority chain: **when the facts and the intent file disagree, the facts
win; when the intent file and recollection disagree, the intent file wins;
recollection on its own is NEVER sufficient grounds to redraw.** When step 4 contradicts
the intent file, updating the intent file is part of the same change — a
knowingly-stale intent file is worse than a missing one, because the next
hand will trust it.

## Maturity encoding

State on a maintained diagram uses the vocabulary the per-type files
already define — no new visual grammar:

- **Shipped** — standard node treatment.
- **In build** — the focal slot: the 1–2 `data-role="focal"` elements and
  "under construction" are the same budget, not two competing ones. What is
  being built IS the next intervention the reader must see first.
- **Future / planned** — dashed stroke at reduced opacity, never focal
  color, never load-bearing on the main path.
- **Undecided boundary** — a mono `TO-VERIFY` label at the uncertain edge.
- No dates, owners, or milestone furniture anywhere — except inside an
  architecture board's governance band, which is the one place that
  information is load-bearing (see `type-architecture-board.md`).

## Terminology sync

When the prose around the diagram renames an object (module, service,
band), the same change updates all of: the SVG `<text>` labels, the
`<title>`/`<desc>`, the intent file, the re-exported PNG, and any
cross-references in sibling docs. A diagram still showing the old name is a
bug, not a style preference — it actively teaches readers a name the
codebase no longer answers to.

## Export discipline

- Re-export from the source HTML headlessly (e.g. `chrome --headless
  --screenshot` or `rsvg-convert`) — never screenshot a browser window by
  hand.
- README / docs targets render at roughly 2400–3200px wide with a generous
  multiple-of-4 safe margin, so the PNG survives retina displays and README
  downscaling.
- The exported PNG is never scaled, cropped, or retouched by hand; and the
  diagram's content is never bent to appease an exporter quirk — fix the
  export command, not the drawing.

## Acceptance — three surfaces

A maintained-diagram change is accepted only after checking all three
surfaces, in order:

1. **Source HTML in a browser** — structure, no overlaps, arrows land on
   node edges.
2. **Exported PNG at 100%** — no clipping, no blank bands, no HTML→PNG
   rendering drift.
3. **In its published home** — the figure reads correctly inside the prose
   that hosts it (README section, docs page), at the width readers will
   actually meet it at.

Plus two freshness checks: the PNG's timestamp is newer than the source
HTML's, and the intent file reflects what was just drawn (the Proposed
block shrank or the Preserve block grew — one of the two must have moved).

## Anti-patterns

- **PNG edited instead of re-exported**
  - *Why fails*: the trio breaks silently — the HTML still claims to be the
    source of truth while the shipped pixels disagree; the next redraw
    starts from a stale picture and reproduces the divergence.
- **HTML previewed but the exported PNG never opened**
  - *Why fails*: HTML→PNG export has real drift (fonts, filters, viewport
    cuts); the reader only ever sees the PNG, so an unviewed PNG means the
    actual deliverable shipped unreviewed.
- **Prose renamed an object but the diagram didn't**
  - *Why fails*: the diagram now actively teaches a dead name; readers
    grep the codebase for a label that no longer exists and conclude the
    docs are unmaintained — one stale label taxes trust in every fresh one.
- **Redrawing from memory with the evidence pass skipped**
  - *Why fails*: memory reproduces the last picture, not the current
    system; the redraw silently reverts every fact that changed since the
    last session, and does it with confident-looking geometry.
