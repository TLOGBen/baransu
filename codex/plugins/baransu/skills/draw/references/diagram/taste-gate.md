# Taste gate — run before producing any diagram

The upstream pre-output checklist (diagram-design SKILL.md §4 universal anti-patterns and §9 taste gate, MIT), with paths pointed at this skill. Every type reference, import guide and `output-spec.md` that says "the SKILL.md §9 taste gate" means this file. Run it on the finished HTML before the completion report; one failing row is a fix, not a note.

## Universal anti-patterns (§4)

These mark a generated schematic of any type:

| Anti-pattern | Why it fails |
|---|---|
| Dark mode + cyan/purple glow | Looks "technical" without design decisions |
| JetBrains Mono as blanket "dev" font | Mono is for technical content — ports, commands, URLs. Names go in Geist sans. |
| Identical boxes for every node | Erases hierarchy |
| Legend floating inside the diagram area | Collides with nodes |
| Arrow labels with no masking rect | Bleeds through the line |
| Vertical `writing-mode` text on arrows | Unreadable |
| 3 equal-width summary cards as default | Generic grid — vary widths |
| Shadow on any element | Shadows are out. Borders are in. |
| `rounded-2xl` on boxes | Max radius 6–10px or none |
| Accent on every "important" node | The accent is 1–2 editorial focal points, not a signaling system |
| Reproducing Mermaid's renderer layout | Imports automatic spacing and routing instead of making an editorial layout |
| Any breach of the six connector rules | Automatic fail: diagonal slants, labels touching their stroke, masks clipped by a later node, overlapping paths, shared attach points, transit behind a non-endpoint box |

Type-specific anti-patterns live in each type reference.

## Pre-output checklist (§9)

**Type fit:**

- [ ] If behavior matters, did I choose one semantic pattern before the visual type and load `semantic-patterns.md`?
- [ ] Right visual type for the layout (`README.md` visual-type table)?
- [ ] Stated type, pattern, size preset, and planned cuts before drawing — confirmed, or assumptions noted?
- [ ] Would a table / paragraph do the same job? (If yes — don't draw.)
- [ ] Loaded the matching type reference?
- [ ] If this is an import — format, size, detail level, and audience set? `viewBox` and type ramp match the size preset (`output-spec.md` §6)?
- [ ] If this is an import — fidelity ledger ready to report?

**Remove test:**

- [ ] Can I remove any node? (Would a reader still understand?)
- [ ] Can I merge any two nodes? (Do they always travel together?)
- [ ] Can I remove any arrow? (Is the relationship obvious from layout?)
- [ ] Can I remove any label? (Does color or shape already signal it?)

**Signal:**

- [ ] Accent used on ≤ 2 elements? If more, which actually deserve focal status?
- [ ] Legend covers every type used — and nothing extra?
- [ ] Within the type's complexity budget (`layout-budget.md`)?

**Technical:**

- [ ] Diagram `<svg>` has `role="img"` and `aria-labelledby` resolving to its `<title>` and `<desc>`?
- [ ] `<title>` is the first child of `<svg>` (before `<defs>`) and both `<title>` and `<desc>` are filled in?
- [ ] `<title>` / `<desc>` IDs are prefixed for this diagram and variant — never bare `title` / `desc`?
- [ ] Arrows drawn before boxes?
- [ ] Connector rule 1: off-axis connectors are `r=8` elbows, no diagonal slants?
- [ ] Connector rule 2: a visible 6 to 10px gap between every label mask and its connector?
- [ ] Connector rule 3: no overlapping or stacked connectors; bridge/hop at crossings?
- [ ] Connector rule 4: a distinct attach point per connector on a shared edge, 12px or more apart, none hiding another?
- [ ] Connector rule 5: no transit behind a non-endpoint box, except the unavoidable case (dashed, label at the visible end)?
- [ ] Connector rule 6: no label mask overlapping a node drawn after it? (`python3 scripts/diagram/repo/verify-geometry.py <file>`)
- [ ] Every arrow label has an opaque paper-colored rect behind it?
- [ ] Legend is a horizontal bottom strip, not floating?
- [ ] No vertical `writing-mode` text?
- [ ] `viewBox` expanded for the legend strip (~60px)?
- [ ] `min-width` equals the viewBox width, and the SVG sits in a local `overflow-x: auto` wrapper (`output-spec.md`)?
- [ ] Node origins, dimensions, gaps, padding on the 4px grid; type sizes on the role ramp?
- [ ] `python3 scripts/diagram/self_check.py <file>` passed? (Accessible-SVG contract, single-file safety, motion basics.)
- [ ] If animated with the upstream modes: the complete static/no-JS frame works, reduced motion hides/disables playback, the controller is copied verbatim from `assets/diagram/template-motion.html`, and `python3 scripts/diagram/repo/verify-motion.py <file>` passes. If a seek overlay: `seek_split.py` twin passes, `verify-page.mjs` clean, `render.mjs hash` deterministic (`seek-overlay.md`).

**Typography:**

- [ ] Brand match uses exact public families/weights, verified via `getComputedStyle`; fallbacks disclosed?
- [ ] Human-readable names in Geist sans, not Geist Mono?
- [ ] Technical sublabels (ports, commands, URLs) in Geist Mono?
- [ ] Page title in Instrument Serif?
- [ ] Annotation callouts (if any) in italic Instrument Serif (`primitive-annotation.md`)?
- [ ] No JetBrains Mono anywhere?
