# Typography Discipline — Weight Ladder, Size Floors, Text-Adaptation Sweeps

These are weak-moment levers and pre-ship sweeps for type: they INFORM the committed
direction (per `aesthetics-foundation.md`'s meta-rules — theory serves the weak moment,
never overrides a working intuition), they never override it. Two floors never move:
legibility contrast, and the reader's ability to finish a line.

## 1. Size-inverse weight ladder

Perceived blackness grows with size. Large type holds presence with LESS weight; small
type needs MORE weight to stay legible. Weight therefore runs INVERSELY to size — the
ladder is an optical-compensation rule, not a style preference. A bold display headline
over-inks and shouts (upstream-observed: the guizang Swiss system treats a bold hero as
an instant style break); a light caption under-inks and vanishes at reading distance.
— Itten:明暗對比（value carries legibility, at every size）

### The ladder (bands over our perfect-fourth scale roles)

Bands are expressed against the roles of the perfect-fourth scale in
`canonical-tokens.md §Modular Scale` — re-derive from the committed face's actual
weights, never copy numbers across faces:

| Scale role | Weight band | Rationale |
|---|---|---|
| display / hero (`--font-display` sizes above H1) | the lightest weight the committed face sanctions (often 200–300) | size already carries the hierarchy; weight would double-claim it |
| H1–H2 | light-to-regular (300–400) | headline presence from scale, ink stays quiet |
| H3 / body | regular (400) | the reading baseline — the ladder's fixed midpoint |
| captions / labels / micro (at or below the scale's smallest step) | medium-to-semibold (500–600), the HEAVIEST tier | small strokes thin out optically; added weight restores them |

### Two testable invariants (the ladder's enforcement form)

1. **Per-view monotonicity** — within one view, a smaller text role never carries a
   lighter weight than a larger role. Scan any rendered view top-down: as size steps
   down, weight may only hold or rise.
2. **Small-text floor** — body-size-and-below never drops below regular (400). Light
   weights on small text are simultaneously small AND thin — unreadable at reading
   distance and on projection. This floor is absolute; the ladder above it is advisory.

### Two mirrored anti-patterns

- **bold giant display** — an over-committed weight where size already carries the
  hierarchy: the hero shouts, and every headline below it must escalate to compete.
- **light small caption** — the mirror image: a sub-body role set light "for elegance"
  that under-inks into invisibility exactly where readers already strain.

### Sanctioned exception — contrast dictates

Light text over a mid-luminance accent fill loses stroke contrast; there, weight goes UP
regardless of the ladder. The legibility floor beats the ladder: the ladder INFORMS,
contrast DICTATES. — Itten:明暗對比

### Preset-context scoping

The ladder is strongest in single-sans systems (swiss-like), where weight is the face's
main expressive axis. In serif editorial systems (kami-like) the same inverse principle
expresses through the face's optical sizing — a display cut is already lighter-drawn —
not through pushing numeric weight down to 200. Kami's own sanity rule caps heading
weight at 500; the ladder is compatible by construction, because it only ever pushes
display weight DOWN, never up. No preset conflict can arise.

### Emphasis inside a light display line

Emphasis inside a light display line is carried by style (italic where the preset allows
it) or by structure (isolation, scale), never by painting accent color on an accent
background — that trades one hierarchy violation for a contrast violation.

## 2. Size floors and the overflow-resolution order

### Role-based floors

Floors attach to text ROLES, not to individual elements — an element inherits the floor
of the role it plays. Tie each floor to the preset's smallest scale steps:

| Text role | Floor |
|---|---|
| primary body | the scale's body step — never below it |
| secondary description (card blurbs, list items, captions) | one scale step below body, and no lower |
| micro-meta (kickers, mono labels, axis labels) | the scale's smallest step — the absolute bottom of the system |

### Overflow resolution order

When content overflows its slot, resolve in this order:

1. **Cut the copy** — tighten the sentence first; overflow is usually a writing problem.
2. **Split the container/page** — give the content more room.
3. **Switch to a better-fitting layout** — the slot was the wrong shape.

Shrinking type below the floor is never a fix. WHY: authors cheat the floor precisely in
footnote-ish places (captions, KPI footnotes, timeline notes) — which is where readers
already strain, so the cheat lands on the weakest reading moment.

## 3. Text-adaptation gotcha trio (pre-ship sweeps)

Concrete IF-THEN rules for regressions the source never betrays — they surface only once
the page is rendered. Sources: the Waza `/ui` gotcha table and observed failure modes.

1. **Localized-text overflow** — IF a component ships with English-fitted fixed slots
   (buttons, tabs, nav, compact cards) THEN exercise those slots with worst-case long words and the longest
   translated strings expected in shipped locales — at desktop AND narrow-mobile
   widths — before handing off. WHY: upstream-observed — the English
   build fits, the localized build overflows the slot.
2. **Ellipsis-truncation ban** — IF text must fit a fixed-width slot THEN make it fit by
   construction — shorten the value's format, cut lists at whole-item boundaries, trim to
   a clean edge with no dangling glyph; never lean on `…` tail-truncation, and a metric
   or label footer may never end in an ellipsis. WHY:
   an ellipsis in a metric hides the datum the element exists to show.
3. **Orphan-line sweep** — IF any user-visible text block's last line holds a lone
   orphan word (objective flag: last line under ~13% of the block's widest line) THEN
   fix by tightening the COPY — never by shrinking type, and never by a `max-width` cap
   narrower than the container (a cap wraps every line early and reads as a premature
   break). Finding ONE instance escalates to sweeping the whole document: treat it as a
   class symptom, not a point defect. WHY: an orphan exists only in the
   rendered wrap — the source never shows it — so one caught instance implies
   unswept siblings.

### CJK typography block

Companion IF-THENs, consistent with the `aesthetics-foundation.md` §4 CJK wiring row —
reuse its line-height split (screen reading 1.7–1.8 vs print 1.50–1.55; the preset
context decides), do NOT introduce a third stance:

- IF the interface mixes CJK with Latin THEN order the font stack Latin-face-first with
  the CJK face after it (Latin runs get the Latin face; Han glyphs fall through), and
  tag runs with `lang="zh"` / `lang="ja"` / `lang="en"` so font selection and
  line-breaking resolve per language. WHY: an unordered stack renders Latin in the CJK
  face's Latin glyphs — subtly wrong everywhere.
- IF a serif reading mode exists THEN pair an explicit CJK serif fallback after the
  Latin serif — otherwise CJK silently drops to a sans and the reading mode splits into
  two voices. — Tschichold:字體即立場
- IF applying display tracking THEN scope negative letter-spacing to Latin runs only —
  never on CJK glyphs (tightened Hanzi reads as a rendering bug, not a style).
