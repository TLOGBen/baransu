# Expression Axes — Background Texture & Motion Budget (optional, Gen Mode)

Two OPTIONAL expression axes for Gen Mode's DESIGN.md authoring. Both are content
guidance INSIDE the existing nine sections — texture lands in §1 Visual Theme and §6
Imagery; motion lands in §7 Motion & Animation. NO new DESIGN.md headings, NO new
tokens, NO validator surface. A preset or DESIGN.md that never mentions them keeps
today's behavior byte-for-byte; downstream consumers treat absence as the conservative
default (the same presence-enriches / absence-degrades pattern as book's §9 soft-read).
Both axes INFORM the committed direction, never dictate it — and the anti-generic
default is what you get by NOT choosing.

## 1. Background-texture axis (four rungs)

Each rung: when it is a legitimate choice, its WHY anchor, and its cost.

1. **flat** (DEFAULT — anti-generic through precision) — flat, near-neutral, slightly
   temperature-shifted surfaces on a two-plane ladder (page vs surface, about one
   lightness step apart, hairline low-alpha ring); separation by negative space, not
   borders or shadows. WHY: the official frontend-design skill's observation is that a
   minimal direction lives or dies on spacing/type precision, not surface effects — and
   two of the three named generic-AI looks are background treatments, so an unexamined
   non-flat background IS the AI fingerprint, not the cure for it. Cost: demands exact
   spacing and type discipline; there is no texture to hide sloppiness behind.
2. **paper-grain** — subtle material grain (the kami dot-noise family), sanctioned when
   the §3.1 material metaphor IS a paper/print material. WHY: texture must come from the
   design's own material world, not from atmosphere-seeking. — 原研哉:HAPTIC
   Cost: grain must stay below conscious notice; visible speckle reads as compression
   artifacts.
3. **structured-noise** — deliberate, low-amplitude noise/pattern fields; legitimate
   only for a committed maximal/brutalist direction, and named in DESIGN.md §8 Do/Don't
   with its tradeoff. WARNING: dense high-contrast angled fields are a vestibular risk,
   and any pattern behind data reads as value-scale noise — keep noise off charts
   entirely. Cost: every overlaid text block needs re-verified contrast.
4. **gradient** (highest generic risk) — the gradient accent is the named "template
   answer" of generic AI design; permitted ONLY when the brief pins it or the committed
   direction genuinely calls for it, with the tradeoff named in §8. Purple-to-blue on
   white stays a standing anti-pattern — the `aesthetics-foundation.md` §3.2 row already
   covers it; cross-reference it, do not restate. Cost: gradients date fast and fight
   the single-accent area budget.

### Cross-cutting rules (all rungs)

- Cream-parchment + terracotta and near-black + acid-accent are documented DEFAULT looks
  of the current generation — choosing them must be a choice, not a reflex. If the brief
  pins them, follow the brief; brief wording always wins.
- Texture never carries data meaning on charts, except as an explicit accessibility
  channel (a declared redundant encoding, not decoration).
- All rungs stay token-only / PDF-safe (per I3). A grain-opacity token was deliberately
  excluded from the capability set (PDF render risk — check.py records the exclusion),
  so texture is expressed through existing surface tokens plus SVG-side patterns, never
  through a new token.
- Emitted values stay hex; OKLCH remains derivation-space only (matching
  `aesthetics-foundation.md`).

### 決策規則（texture）

1. IF no texture rung was consciously chosen → author §1/§6 as **flat** and spend the
   effort on spacing and type precision instead. — Rams:Less but better
2. IF tempted toward grain or noise for "atmosphere" → trace it to the §3.1 material
   metaphor first; a texture with no material behind it is atmosphere-seeking and gets
   cut. — 原研哉:HAPTIC
3. IF a non-flat rung is chosen → name it and its tradeoff in DESIGN.md §8 Do/Don't, so
   the break is deliberate and reviewable, not ambient.
4. IF any texture would sit behind a chart or data table → remove it there; data
   surfaces are always flat (accessibility-channel encodings excepted).

## 2. Motion-budget axis (three rungs)

A WHERE / HOW-MUCH axis. The extreme→value lookup in `canonical-tokens.md §Extreme →
Value Lookup` remains the HOW-FAST authority for `--ease` / `--duration` /
`--stagger-step` VALUES — this axis never overrides those numbers; it decides where
motion is allowed to exist at all.

1. **none** — a legitimate, complete answer; static is not a deficiency. DEFAULT for
   document-like and data-dense surfaces, where any movement competes with reading.
2. **functional** (DEFAULT elsewhere) — motion only as state feedback: hover lift
   (slight lighten/outline), focus visibility, reduced-opacity hold while data reloads
   (no skeleton flash, no layout jump). Zero entrance, looped, or ambient animation on
   data marks.
3. **expressive** — one orchestrated signature moment (a page-load sequence OR a scroll
   reveal OR a hover system — exactly one of them, where the direction calls for it);
   everything else stays quiet. WHY: scattered micro-effects everywhere are a documented
   generic-AI tell; one landed moment out-performs many small ones.

### Budget rules (all rungs)

- Restraint is enforced by COUNT and PLACEMENT, never by timing tables — the timing
  numbers already live in the extreme→value lookup and do not move with this axis.
- `prefers-reduced-motion` support is a mandatory, unannounced floor at every rung above
  none.
- CSS animation stays progressive-enhancement only — PDF/PPT render the
  static final state (I3 restated verbatim as the hard boundary).
- Motion that groups elements is a grouping statement — things that move together read
  as one group (Gestalt:共同命運; cross-ref the `aesthetics-foundation.md` §4 motion
  row). Motion that decorates is garnish and gets cut.

### 決策規則（motion）

1. IF no motion rung was consciously chosen → author §7 as **functional** (or **none**
   for document-like surfaces); absence of a declaration is the conservative default,
   never an invitation to animate.
2. IF a second "signature moment" appears under **expressive** → cut the weaker one;
   the budget is exactly one. — Rams:盡可能少
3. IF an animation neither gives state feedback nor groups related elements → it is
   garnish; delete it before ship. — Gestalt:共同命運
4. IF tuning HOW-FAST → do not invent numbers here; read `--ease` / `--duration` /
   `--stagger-step` values off `canonical-tokens.md §Extreme → Value Lookup` and tune
   ±1 step to the 記憶點.
