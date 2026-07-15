## Contents

- §4.1 Color tokens (SVG roles)
- §4.2 Required `<defs>` fragment (the fixed marker vocabulary)
- §4.3 Marker defs (arrows use a chevron `<path>`, three fixed ids)
- §4.4 Two-layer paper-mask (node background and canvas base)
- §4.5 Type tag (top-left of node, 7px Geist Mono uppercase)
- §4.6 Legend strip (~60px at the bottom of the viewBox)
- §4.7 Anti-slop precision constraints
- §4.7b Node-role vocabulary + annotation primitive (7 roles, margins-only aside)
- §4.8 Embedded font calibration (scale ≈ 0.47 after embedding in A4)
- §4.9 17-type chart routing decision tree (first-match)
- §4.10 17-type selection table (v1 ref skeleton + status disclosure)
- §4.11 Maintained-diagram lifecycle (trio contract)

# SVG Rendering Rules — Stage 3 §4

Read this file only when the long-form HTML contains a `<figure class="diagram">` block (a Stage 2A flagged section).

> **Token naming**: this spec uses v1.3 baransu canonical token names. The hex-value column lists the Kami preset defaults as a reference; at implementation time you should resolve the preset's actual hex from `{project_root}/tokens.css` (swiss `--paper` = `#fafaf8`, google-design `--paper` = `#FEF7FF`, etc.).

> Upstream anchors re-verified at tw93/Kami@5cd7c8e (2026-06-10): diagrams.md L49 / L79 / L86 unchanged.

## §4.1 Color tokens (SVG roles)

All SVG fill / stroke **must not use `rgba()`** — always use a solid hex token:

| SVG role | Canonical variable | Kami hex default |
|----------|---------------|--------------|
| Canvas background | `--paper` | `#f5f4ed` |
| Standard node fill | `--surface` | `#faf9f5` |
| Standard node stroke / primary text | `--ink` | `#141413` |
| Focal node fill | `--brand-tint` | `#EEF2F7` |
| Focal node stroke | `--accent` | `#1B365D` |
| Standard arrow / secondary text | `--text-muted` | `#504e49` |

> `rgba()` inside CSS `box-shadow` is not restricted (it is not an SVG attribute).

## §4.2 Required `<defs>` fragment (the fixed marker vocabulary)

The fragment below is the **complete three-id vocabulary**. Prepend to each SVG **only the marker ids that SVG actually references** via `marker-end` — GATE-D (marker-integrity) fails any unused marker definition, so blindly prepending all three to a diagram that never uses e.g. `arrow-link` is a guaranteed GATE FAIL (the repo's `validate-fixtures/unused-marker-def.html` negative fixture asserts exactly this).

```svg
<defs>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
  </pattern>
  <!-- Chevron (stroked, non-filled) — WeasyPrint does not support marker orient="auto",
       always hand-draw the chevron with a path stroke instead of a filled polygon. -->
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M2 1 L8 5 L2 9" fill="none" stroke="#504e49"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="arrow-accent" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M2 1 L8 5 L2 9" fill="none" stroke="#1B365D"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="arrow-link" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M2 1 L8 5 L2 9" fill="none" stroke="#2D5A8A"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

## §4.3 Marker defs (arrows use a chevron `<path>`, three fixed ids)

**Rule**: every SVG that contains arrows takes its marker definitions from the following fixed three-id vocabulary — define inside `<defs>` **only the ids the diagram actually references** via `marker-end="url(#…)"` (defs ↔ refs must be bijective; GATE-D fails both dangling references and unused definitions); the arrow geometry **must always use a stroked chevron path** (`d="M2 1 L8 5 L2 9"`, `fill="none"`, `stroke-linecap="round"`) — no filled polygon, and no hand-drawn arrow path.

| Marker id | Use | stroke |
|-----------|----------|--------|
| `arrow` | default (general / internal flow, muted) | `#504e49` (`--text-muted`) |
| `arrow-accent` | focal / main flow (accent color) | `#1B365D` (`--accent`) |
| `arrow-link` | external / API call / cross-boundary | `#2D5A8A` (`--brand-light`) |

**Fixed marker attributes**: `markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"`; the chevron path is fixed at `d="M2 1 L8 5 L2 9"`, `stroke-width="1.5"`, `stroke-linecap="round"`, `stroke-linejoin="round"`, `fill="none"`.

**Id scoping**: the three ids are a per-SVG vocabulary, not document-global names — `url(#…)` resolves document-wide, so when one document carries multiple arrow-bearing SVGs, suffix the ids per section (`arrow-s2`, `arrow-accent-s2`, …) to keep DOM ids unique; the gates are id-name-agnostic and check defs ↔ refs bijectivity per SVG.

**Why**: WeasyPrint / most static PDF renderers handle `<marker orient="auto">` rotation + `<polygon fill>` inconsistently, producing flipped arrows or missing fills; switching to a stroked chevron path aligns across every print pipeline. The chevron (line-drawn, not solid) also aligns directly with Kami `references/diagrams.md` L86 and is one of Kami's visual signatures. The three semantic tiers (general / focal / external) are what let the SVG layer align with the two specs "focal nodes ≤ 2" and "cross-system calls".

**SVG reference example**:

```svg
<line x1="120" y1="80" x2="240" y2="80"
      stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
<line x1="120" y1="120" x2="240" y2="120"
      stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
```

## §4.4 Two-layer paper-mask (node background and canvas base)

**Rule**: every SVG stacks two mask layers **in order** after `<defs>`, then starts drawing nodes and arrows:

```svg
<!-- Layer 1（必選）：全幅 paper fill -->
<rect width="100%" height="100%" fill="#f5f4ed"/>
<!-- Layer 2（可選）：dotted pattern overlay -->
<rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>
```

- Layer 1 (**mandatory**): full-width `<rect width="100%" height="100%" fill="{paper-token}"/>`, where paper-token uses `--paper`
- Layer 2 (**optional**): full-width `<rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>`, used only for long-form / single-page hero diagrams; omit it for product pages or card embeds to avoid the pattern stacking into noise
- **No third layer**: the v1 spec explicitly forbids stacking a third mask layer (e.g. vignette, tint wash); Unknown #3 is deferred until after v1 dogfood to decide whether to upgrade

**Why**: the two-layer structure gives the SVG an opaque background "before any line is drawn", preventing z-order chaos when arrow lines cross a node fill; three or more layers composite with the external background once embedded in a PDF, producing a grayscale shift.

## §4.5 Type tag (top-left of node, 7px Geist Mono uppercase)

**Rule**: place a 7px uppercase small label at the top-left corner of each node, marking the node category (e.g. `API`, `DB`, `EXT`, `CACHE`, `UI`), with a 0.8 stroke hairline frame, using the Geist Mono font and 0.08em letter-spacing.

```svg
<!-- 矩形 tag 細框（rx=2，非 pill；0.8 stroke） -->
<rect x="X+8" y="Y+6" width="28" height="12" rx="2"
      fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
<text x="X+22" y="Y+15" fill="#141413" font-size="7"
      font-family="'Geist Mono', monospace" text-anchor="middle"
      letter-spacing="0.08em">API</text>
```

**Why**: a node's main text (Geist sans) carries the human-readable name, while the type tag (Geist Mono) carries the visual index for "which category of component is this"; splitting them into two font layers preserves a scan path even in low-information-density diagrams.

## §4.6 Legend strip (~60px at the bottom of the viewBox)

**Rule**: after the main nodes and arrows are drawn, every SVG reserves about 60px of height at the bottom of the viewBox for a hairline `<line>` + a horizontal row of legend items (each item one mini swatch + label), covering every node type and arrow type that actually appears in the diagram:

```svg
<!-- Hairline 分隔線 -->
<line x1="30" y1="LEGEND_Y-8" x2="VIEWBOX_W-30" y2="LEGEND_Y-8"
      stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
<!-- LEGEND 標題 -->
<text x="30" y="LEGEND_Y+8" fill="#504e49" font-size="8"
      font-family="'Geist Mono', monospace" letter-spacing="0.14em">LEGEND</text>
<!-- Items — 水平排列，~160px 間距，每項一個 swatch + label -->
```

- **Exception**: when the SVG `viewBox` **height** < 400px (card embed, small / short diagram) the legend strip may be omitted and replaced by an explanation in the body text — height is the axis GATE-C keys on (`validate-output.ts` SKIPs GATE-C when viewBox height < 400, and only then), so the spec and the gate share one axis

**Why**: placing the legend outside the diagram (rather than between the nodes) reserves the central area for structural information; the hairline separator makes the legend visually belong to a "footnote zone" rather than part of the diagram, preventing readers from mistaking a swatch for a node.

## §4.7 Anti-slop precision constraints

- All `<rect>`/`<line>`/`<circle>` positional geometry — x/y/width/height, line endpoints, circle centers — must be **multiples of 4**; text baselines and stroke-widths are exempt (only shape placement carries the 4px grid)
- Node-width whitelist is **3 sizes** (aligned with Kami `references/diagrams.md` L79): {`128`, `144`, `160`}; a single SVG uses at most 2 of them at a time — mixing 3 is an anti-slop fail
  - **Exception**: viewBox width < **360px** (card embed / small diagram) may compress to **2 sizes** (recommended {128, 144} or {128, 160}), still keeping a 2-size rhythm, and **must not** custom-craft individual widths outside the whitelist
- Node height: **32** (pill) / **64** (standard)
- Focal nodes are marked with the `data-role="focal"` attribute (**not** a class); each SVG has at most **2** `data-role="focal"` nodes; focal nodes visually use a `--accent` (`#1B365D`) stroke + **`#EEF2F7` fill** (aligned with Kami `diagrams.md` L49, **not** `--surface-strong`) + `marker-end="url(#arrow-accent)"`
- `<text y>` ≥ font-size × 1.2 (prevents the text top from being clipped)
- The arrow endpoint lands exactly on the node edge (the marker `refX="8"` auto-aligns the chevron tip)
- A focal node must correspond to the element emphasized with `<span class="hl">` in the caption; a mismatch between focal and caption emphasis is an anti-slop fail (aligned with the Kami `diagrams.md` anti-slop table)

**Additional AI-slop failures** (— tw93/Kami `diagrams.md` §7, MIT; only rows not already covered by the constraints above):

| Slop pattern | Fix |
|--------------|-----|
| ring/cycle diagram with a large empty center | put the subject (or the one summary stat) in the center, or use a linear flow instead |
| cycle drawn twice — a dashed ring AND directed arcs carrying the same loop | one loop representation only |
| roadmap furniture (30/60/90 markers, owners, milestones) inside an architecture diagram | timeline content routes to the timeline type (§4.9); an architecture diagram carries structure only |
| future/planned capability drawn at shipped visual weight | draw future state dashed at reduced opacity, never focal, never load-bearing on the main path |
| multi-accent diagram while the caption names a single focal | migrate to one focal + neutrals matching the caption's `<span class="hl">` emphasis |
| crowded diagram "fixed" by scaling everything down globally | fix at module level — split, drop, or re-group nodes; never global scaling |

## §4.7b Node-role vocabulary + annotation primitive

Source: cathrynlavery/diagram-design `style-guide.md` + `primitive-annotation.md` (MIT), re-expressed onto baransu canonical tokens.

Beyond focal vs standard (§4.7), a node may take one of seven semantic roles — each maps to exactly one treatment, so a style difference always reads as a meaning difference, never as decoration:

| Role | Treatment |
|------|-----------|
| focal | `--accent` stroke + `#EEF2F7` fill (§4.7 rules unchanged; ≤2 per SVG) |
| backend / service | standard fill (`--surface`), `--ink` stroke |
| store / database | standard fill + `DB` type tag (§4.5) |
| external | `--text-muted` stroke + `arrow-link` connectors (§4.3) |
| input / source | standard treatment, placed at the flow origin |
| optional | dashed stroke `stroke-dasharray="4,3"` |
| security boundary | dashed stroke `stroke-dasharray="4,4"`, container outline only, never filled |

**Annotation primitive** — for judgment/caveat copy that would otherwise bloat a node: a serif aside set in the margin + a dashed leader line (`stroke-dasharray="4,3"`) ending in a small landing dot (`r="2"`) at the referenced element. Margins only — the aside never sits over nodes or connectors — and max 2 per diagram. The upstream face is italic serif; under a preset whose DESIGN.md bans italics (e.g. Kami §8), keep the serif aside at regular style — the dashed leader + landing dot is the primitive's identity, not the slant.

## §4.8 Embedded font calibration (scale ≈ 0.47 after embedding in A4)

| Role | Font size |
|------|--------|
| H2 / focal node | 24 |
| Body / standard text | 22-24 |
| H3 / sub-label | 18-20 |
| Caption | 15-16 |
| Mono tag | 14 |

## §4.9 17-type chart routing decision tree (first-match)

Find the first matching item top-to-bottom by data shape. **Ordering rule**: the 10 structural rows are listed first, ahead of the 7 statistical rows, so that content matching both a structural data shape and a statistical one (e.g. an architecture diagram that happens to carry an axis) always resolves to the structural type first — first-match top-to-bottom means row position *is* priority, so this ordering is what implements design.md's 既有型態優先 (existing-type-priority) tie-break rule, not just a stated intention.

| Data shape | Chosen chart |
|---------|---------|
| 2×2 strategic positioning | Quadrant |
| Accountable owners + invocation / escalation routing | Org Chart |
| Hierarchical data depth ≥ 2 | Tree |
| Process with decision branches | Flowchart |
| Cross-role process ≥ 3 actors | Swimlane |
| 2-3 cluster sets overlapping | Venn |
| Full-system panorama ≥ 10 blocks (multi-layer platform / governance map) | Architecture Board |
| Code entities with fields/methods + inheritance/composition | Class |
| System components + connections | Architecture |
| Timeline + milestones | Timeline |
| OHLC / per-day price | Statistical |
| +/- contributions summing | Statistical |
| One series, sums to ~100%, items ≤ 6 | Statistical |
| One series, sums to ~100%, items ≥ 7 | Statistical |
| Two or more time series | Statistical |
| One time series, dominated by large changes | Statistical |
| Multi-category snapshot at one time, 2+ series | Statistical |

> **Statistical wiring**: all 7 rows below the structural block resolve to the same **Statistical** type (§4.10 `statistical` row, `references/diagram-types/type-statistical.md`). The original per-shape hint (Candlestick / Waterfall / Donut / Horizontal Bar / Line / Bar / Grouped Bar) stays in the Data shape column for human/generation context — it does not change which reference file loads; `type-statistical.md`'s axis/legend/data-point conventions cover all 7 shapes.

> When nothing matches → fall back to **Architecture** (the general-purpose type).

## §4.10 17-type selection table (v1 ref skeleton + status disclosure)

Each section containing a diagram looks up the corresponding ref from this table per Layer 2. The Status column always aligns with each ref's frontmatter (fact-synced, binary-verifiable via `grep '^status:' references/diagram-types/type-*.md`): `complete` means the ref contains directly reusable SVG example HTML marked `example: inline` and the renderer should reuse that skeleton; `ref-only` means only the ref spec exists and the example HTML is still pending (the renderer falls back to generic SVG primitives). All 17 types currently have frontmatter that is **entirely `status: complete` + `example: inline`**, and this table aligns with that; the `ref-only` row only carries reserved semantics for future new types not yet shipping an example.

| Type | Best for | Reference | Status |
|------|----------|-----------|--------|
| architecture | system overview / data-flow / integration map / infra topology / components + connections | `references/diagram-types/type-architecture.md` | `status: complete` |
| flowchart | decision logic / algorithm steps / "Should I…?" branches / onboarding routing / support-triage | `references/diagram-types/type-flowchart.md` | `status: complete` |
| sequence | request/response flow / protocol handshake / multi-actor interaction / API call trace / incident reconstruction | `references/diagram-types/type-sequence.md` | `status: complete` |
| state | finite-state logic / order status / auth state / connection lifecycle / form wizard | `references/diagram-types/type-state.md` | `status: complete` |
| er | database schema / API resource relationships / domain model / aggregate boundary / cross-service ownership | `references/diagram-types/type-er.md` | `status: complete` |
| timeline | release history / project milestone / incident timeline / roadmap / changelog | `references/diagram-types/type-timeline.md` | `status: complete` |
| swimlane | cross-functional process / RACI flow / vendor handoff / multi-team workflow / cross-team responsibility | `references/diagram-types/type-swimlane.md` | `status: complete` |
| quadrant | prioritization (Impact × Effort) / positioning map / portfolio map / 2×2 decision / scenario planning | `references/diagram-types/type-quadrant.md` | `status: complete` |
| nested | expressing hierarchy via containment / scope boundary / CLAUDE.md cascade / trust zone / blast radius | `references/diagram-types/type-nested.md` | `status: complete` |
| tree | module hierarchy / dependency tree / taxonomy / file tree / decision breakdown / skill tree | `references/diagram-types/type-tree.md` | `status: complete` |
| layers | OSI model / CSS cascade / context hierarchy / tech stack / abstraction layer / memory hierarchy | `references/diagram-types/type-layers.md` | `status: complete` |
| venn | concept intersection / shared attributes across categories / ikigai-style frame / positioning sweet spot | `references/diagram-types/type-venn.md` | `status: complete` |
| pyramid | hierarchy of needs / prioritization rank / value pyramid / conversion funnel / content importance | `references/diagram-types/type-pyramid.md` | `status: complete` |
| org-chart | accountable ownership / who-owns-what routing / invocation + escalation paths / coverage-gap map / agent-team responsibility | `references/diagram-types/type-org-chart.md` | `status: complete` |
| class | code entity structure / fields + methods compartments / inheritance + composition relations / interface contracts / module API surface | `references/diagram-types/type-class.md` | `status: complete` |
| architecture-board | full-system panorama / multi-layer platform map / control plane + governance + roadmap in one view / owner map / report-scale board (10–25 blocks) | `references/diagram-types/type-architecture-board.md` | `status: complete` |
| statistical | time-series trend / candlestick / waterfall / donut / horizontal-bar ranking / bar / grouped-bar comparison — any section with an axis, a legend, and multiple data points | `references/diagram-types/type-statistical.md` | `status: complete` |

> **Fallback (triggered by ref-only types only)**: if and only if some type's frontmatter is still `status: ref-only` (none of the 17 types are currently in this state, so no type takes this path right now), the renderer falls back to generic SVG primitives (the marker / paper-mask / type tag / legend strip specs still apply) and flags `degraded-type: <type-name>` in the Stage 4 completion report to signal that example HTML needs to be added. A `status: complete` type always reuses that ref's `example: inline` SVG skeleton and must not be downgraded to generic primitives.

> **Forward note**: when v2-N adds a dark/full variant or a new SVG primitive, it must follow the hex shape contract in `design-token-resolver.md` (`^#[0-9a-fA-F]{3,8}$`) and must not open a separate sink.

## §4.11 Maintained-diagram lifecycle (trio contract)

When the diagram's destination is the **user's repository** (a README hero, a docs-site figure, or an update to an existing in-repo diagram) rather than `.codex/book/`, every per-type rule above still applies — but the artifact gains a lifecycle: the source HTML, the exported PNG, and the intent file move together as one trio. Read `references/diagram-types/maintained-diagrams.md` before redrawing any such diagram; never redraw from memory alone.
