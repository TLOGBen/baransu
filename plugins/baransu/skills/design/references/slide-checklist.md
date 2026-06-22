## Contents

- P0 sub-prefix legend
- P0-S-01：swiss prose must not use italics
- P0-S-02：swiss CSS attributes must not hardcode `oklch()`
- P0-A-01：chevron marker must use `<polygon>`, not a `<path>` simulation
- P0-A-02：top-level node `<rect>` width must be ∈ {128, 144, 160}
- P0-A-03：at most 2 focal nodes per SVG
- P0-A-04：large type must use the dual-constraint height cap `font-size: min(Xvw, Yvh)` with Y ≥ X × 1.6
- P0-B-01：plugin.json `version` must be bumped on every release
- P1-01：dropcap `font-size` must be ∈ [4.0em, 5.0em]
- P1-02：prose straight quotes `"` / `'` must be curled
- P1-03：lead paragraph missing `text-wrap: pretty`
- P1-04：portrait `<img>` missing `object-position: center 35%`
- P2-01：top-level node coordinates violate multiple-of-4
- P2-02：chevron marker `<defs>` duplicated across the 13 diagram-types
- P2-03：slide-core layout name not in the 22-lock-list
- P2-04：en variant HTML contains a CJK font stack
- P3-01：SKILL.md contains a fractional heading
- P3-02：chevron marker `fill` takes a value other than `"none"` or `"currentColor"`
- future-trigger observation items

# slide-checklist.md

> Lint rules for `/design` slide + long-form output. Each entry uses a three-column structure: **Symptom → Root cause → Fix**, with a `source:` metadata line. Audience: `check.py` lint source, slide-core authors, and preset reviewers.

## P0 sub-prefix legend

P0 entries split into three prefix classes by "enforcement scope". `check.py` / sanity scripts map trigger conditions by prefix:

- **P0-S-\*** — Swiss-locked invariants: enforced only under the `swiss` preset (skipped in kami / google modes). Examples: no italics, oklch not allowed in an attribute.
- **P0-A-\*** — All-preset universal: enforced across all three presets — kami / swiss / google-design. Examples: focal cap 2 / chevron marker / multiple-of-4 coordinates.
- **P0-B-\*** — Baransu plugin self-discipline: targets baransu's own release discipline (plugin.json / SKILL.md / CLAUDE.md invariants); not enforced against external user slide output, but enforced on PRs within the baransu repo.

P1 / P2 / P3 carry no sub-prefix; they are distinguished only by severity (P1 fail; P2 soft-warning; P3 advisory).

---

## P0-S-01：swiss prose must not use italics

### Symptom
Under the swiss preset, the long-form / slide HTML body contains `<em>` / `<i>` / `font-style: italic`, causing the type to be rendered by the browser as "faux italic", breaking Swiss baseline grid alignment and contradicting the design intent of grotesque fonts like Inter / Söhne.

### Root cause
The author carries over the general web-emphasis instinct, equating semantic emphasis with visual italics; Swiss invariant #10 states explicitly: emphasis goes through weight / spacing / accent color, not italic. The italic glyph set of fonts like Inter actually breaks KPI alignment in numeric tabular scenarios.

### Fix
Remove all `<em>` / `<i>` / `font-style: italic` declarations from slide-core / long-form templates; use `<strong>` + the `--swiss-weight-emphasis` token, or a `letter-spacing` tweak, instead. `check.py` adds an `<em>|<i\b|font-style:\s*italic` regex detection in the `preset == swiss` context; a hit fails.

source: kami-spec-L86

---

## P0-S-02：swiss CSS attributes must not hardcode `oklch()`

### Symptom
swiss preset slide-core / long-form HTML inlines `style="color: oklch(...)"` or the SVG attribute `fill="oklch(...)"`, causing Safari < 15.4 / some print pipelines to render it as black or transparent, fully voiding the preset accent.

### Root cause
The author copies oklch values directly from `tokens.css` and stuffs them into an attribute, ignoring the parser-level split between an attribute literal and a CSS property — attributes go through the SVG presentation parser, whose oklch support lags far behind CSS. TASK-shared-02 already drew the line: oklch may exist only in a CSS variable or stylesheet, and **must not** enter an attribute.

### Fix
Route all color attributes through a CSS class or `var(--token-name)` instead (and that token may use oklch internally); change SVG `fill` / `stroke` attributes to `currentColor` or a named class. `check.py` adds a `(style|fill|stroke)=["'][^"']*oklch\(` regex; a hit fails P0-S-02.

source: dogfood-v1.3-handoff

---

## P0-A-01：chevron marker must use `<polygon>`, not a `<path>` simulation

### Symptom
SVG chevron / arrow markers inside diagram-types/*.md use `<path d="M..."/>` to draw the triangle, causing marker units to misalign in size across different SVG renderers (Chromium vs WebKit vs Inkscape print) and leaving stroke-linejoin rounded corners.

### Root cause
The author takes "marker = arbitrary vector" as the premise, not understanding that `<polygon points="0,0 10,5 0,10"/>` is the standard form of a marker: explicit vertices, no control point, and correctly rotatable by marker-orient. Kami spec L86 states explicitly: chevron marker = polygon-three-points; a path simulation always fails.

### Fix
In all 13 `references/diagram-types/*.md` example SVGs, replace the chevron `<path>` with `<polygon points="0,0 10,5 0,10" fill="currentColor"/>`, and set `markerUnits="strokeWidth"` `orient="auto"` on the `<marker>`. `validate-output.ts` GATE-J already covers this; `check.py` adds a `<marker[^>]*>\s*<path` regex detection.

source: kami-spec-L86

---

## P0-A-02：top-level node `<rect>` width must be ∈ {128, 144, 160}

### Symptom
The outermost node (focal / hub node) inside a diagram SVG takes a `<rect width="..."/>` value like 130 / 150 / 175, causing inconsistent alignment across the 13 diagram-types; when multiple diagrams sit side by side, the hub node's visual weight jitters.

### Root cause
The author sets width by "looks about right", without aligning to the baseline grid multiple-of-4 whitelist; TASK-svg-05 GATE-J locks top-level node width to three tiers {128, 144, 160} (small / medium / large), corresponding to multiple-of-4 × golden-ratio approximation. Arbitrary values break cross-diagram visual rhythm.

### Fix
In all diagram-types/*.md, change every top-level node `<rect width>` to one of 128 / 144 / 160; focal node defaults to 144. `validate-output.ts` GATE-J is already implemented; `check.py` adds a check that parses the SVG and compares top-level rect width against the whitelist, failing when it is not in the set.

source: huashu-incident-2026-04-20

---

## P0-A-03：at most 2 focal nodes per SVG

### Symptom
The number of nodes marked with the `--focal-fill` token or `class="focal"` inside a diagram SVG is > 2, dispersing the visual focus, collapsing Kami's "deterministic visual center of gravity" principle, and leaving the reader unable to locate the main axis within 3 seconds.

### Root cause
The author marks every important node as focal, not understanding that focal = a sticky point for the visual center of gravity, which should correspond to "at most two narrative throughlines"; the shared TASK-svg-01..04 invariant: focal cap 2, beyond which it becomes the "mark everything = mark nothing" anti-pattern.

### Fix
Re-examine focal annotations in the diagram-types/*.md example SVGs, using at most 2 focal class / token uses per diagram; demote other important nodes to the `secondary` class (which automatically lowers contrast one level). `check.py` counts occurrences of `class="[^"]*focal[^"]*"`; > 2 fails P0-A-03.

source: kami-spec-L86

---

## P0-A-04：large type must use the dual-constraint height cap `font-size: min(Xvw, Yvh)` with Y ≥ X × 1.6

### Symptom
slide-core large type (`h-hero` / `h-xl` / `big-num` / `sub`, etc.) sets the size with a single `vw` only, e.g. `font-size: 11vw`. On a standard 16:9 screen 11vw = 19.6vh, gets clipped by the viewport height, and actually renders about 20% smaller than the design value; switch to a portrait or non-16:9 ratio screen and it overflows and breaks the layout instead. This is a reproducible bug, not a subjective preference.

### Root cause
The viewport ratio 1vw : 1vh ≈ 1.78 (under 16:9, 100vw : 56.25vh). Large type that gives only `vw` and no `vh` cap is implicitly clipped by viewport height on a standard 16:9 screen: with `min(7vw, 10vh)`, 7vw = 12.46vh and gets clipped by the smaller 10vh, shrinking about 20%. The `vh` cap must therefore leave enough headroom — `Y ≥ X × 1.6` — so that on a 16:9 screen it does not become the clipper in turn. digests/12 §4 lists this as the slide-layout's "most easily tripped" reproducible defect (drawn from the P15/P20/P22 lessons).

### Fix
Write all large type as `font-size: min(Xvw, Yvh)` with `Y ≥ X × 1.6`. guizang quick-reference values (directly applicable): h-hero manifesto `min(11.6vw, 19vh)`; h-xl section `min(7vw, 12vh)`~`min(7.4vw, 13vh)`; big-num large-number KPI `min(8.4vw, 14vh)`; sub subtitle `min(7.6vw, 13vh)`; mid-num medium-number `min(4.6vw, 8.5vh)`~`min(5.6vw, 10vh)`. Also hold the presentation minimum-font-size floors: body / main explanation ≥18px, card description / list / caption ≥16px, meta / kicker / chart label ≥14px; when it does not fit, first cut copy / split the page / change the layout — do not squeeze the font size. Detection mechanism: `check.py` can add inline-style / `<style>` detection for `font-size:\s*\d+(\.\d+)?vw` (without a co-declared `min(... vh)`) (proposed tooling, not yet implemented); until it lands, manually grep `vw` font-size declarations + visually confirm each one carries a `vh` cap with Y/X ≥ 1.6, and do not assume a ready-made script exists to run.

source: guizang-ppt-§4

---

## P0-B-01：plugin.json `version` must be bumped on every release

### Symptom
A baransu repo PR contains a `plugins/baransu/skills/**` or `plugins/baransu/agents/**` diff, but the `version` field of `plugins/baransu/.claude-plugin/plugin.json` is untouched, so the user's local plugin cache does not invalidate and the new SKILL.md never takes effect.

### Root cause
The Claude Code plugin load mechanism judges cache validity by the plugin.json version; missing the bump = equivalent to not releasing. CLAUDE.md non-obvious invariants lists this item explicitly; historically v0.3.x → v0.4.0 rolled back several times because of it.

### Fix
Confirm manually at PR wrap-up: if `plugins/baransu/skills/**` or `plugins/baransu/agents/**` has a diff, the plugin.json `version` must be bumped (CLAUDE.md non-obvious invariant). The automated gate (`check-plugin-version-bump.sh`, which parses the git diff and exits 1 if not bumped) is proposed tooling (not yet implemented); until it lands, gate it manually in PR review, and do not assume this script already runs in CI.

source: dogfood-v1.3-handoff

---

## P1-01：dropcap `font-size` must be ∈ [4.0em, 5.0em]

### Symptom
The long-form first-paragraph dropcap style sets `font-size` to 3.5em / 6em / 2.8em, so the dropcap height does not align to the three-line baseline and visually "floats" or "sinks".

### Root cause
The author sets it large or small by print-magazine instinct, without matching the baseline math of line-height × 3 lines; editorial-sanity Check 2 already locks the dropcap into the 4.0–5.0em range (corresponding to the line-height 1.5 × 3 lines ≈ 4.5em median).

### Fix
The all-preset typography.css dropcap rule hardcodes `font-size: clamp(4.0em, 4.5em, 5.0em)`; editorial-sanity adds dropcap font-size parsing + range checking, failing P1-01 when out of range.

source: dogfood-v1.3-handoff

---

## P1-02：prose straight quotes `"` / `'` must be curled

### Symptom
The long-form / slide HTML article body contains straight quotes `"abc"` / `'xyz'` (not inside an HTML attribute), breaking the typographic look and clashing with the curly-quote glyph of the typography font.

### Root cause
The author pastes the source from a markdown editor / Slack without running a smart-quote conversion; HTML attributes (like `class="..."`) must use straight quotes as a syntactic necessity, but prose segments must use typographic curly quotes. editorial-sanity Check 3 already lists this.

### Fix
Add a prose-only smart-quote conversion to the build pipeline (skipping `<code>` / `<pre>` / HTML attributes); the regex uses a DOM walker rather than plain string replacement to avoid contaminating code blocks. editorial-sanity counts `["']` inside `<p>` / `<li>` text content; > 0 fails P1-02.

source: kami-spec-L86

---

## P1-03：lead paragraph missing `text-wrap: pretty`

### Symptom
The last line of the long-form first paragraph (lead paragraph) shows a widow / orphan (a single word or an extremely short trailing line), interrupting the reading flow; it is especially jarring when multiple presets are compared side by side.

### Root cause
The typography template does not apply `text-wrap: pretty` to the lead paragraph; that property makes the browser prioritize avoiding widows / orphans when wrapping, but Safari < 17.4 does not support it, so many authors choose to omit it. The kami spec stance: apply it whenever possible — for unsupporting browsers the fallback degrades naturally and harmlessly.

### Fix
The all-preset typography.css adds `text-wrap: pretty` to `.lead` and `article > p:first-of-type`; editorial-sanity parses the stylesheet and reports a warning when the lead paragraph rule lacks this property (provisionally listed as a cosmetic warning in v1.4; in v1.5, promoted to P0 depending on Safari 17.4 adoption).

source: dogfood-v1.3-handoff

---

## P1-04：portrait `<img>` missing `object-position: center 35%`

### Symptom
A long-form / slide portrait photo renders with the default `object-position: center center` in the `content-2col` / `compare` / `cover` layout, leaving too much headroom above the head or cropping the chin.

### Root cause
The author does not set object-position separately for portrait photos; a face's visual center of gravity sits at the "upper 1/3" (about 35%), and center center effectively pushes the focus below the tip of the nose. schemas sanity Check B already requires all `<img>` to use 35% when `role="portrait"` or the alt contains a person hint.

### Fix
slide-core / long-form templates hardcode `object-position: center 35%` for the `img.portrait` / `[role="portrait"]` rule; schemas sanity fails P1-04 when a portrait-class img lacks this declaration.

source: kami-spec-L86

---

## P2-01：top-level node coordinates violate multiple-of-4

### Symptom
A top-level node inside a diagram SVG takes `<rect x="..." y="...">` values like 17 / 33 / 51 — not enough to break the layout, but inconsistent with the baseline grid multiple-of-4 convention, causing rhythm jitter when multiple diagrams sit side by side.

### Root cause
The author exports from a manually dragged Figma position without snap-to-grid 4px; TASK-svg-05 GATE-J softly requires top-level coordinates to satisfy % 4 == 0, and a violation only reports a warning (not a P0 fail, since it does not affect function).

### Fix
The currently executable detection is: `check.py` runs a `% 4 != 0` detection on top-level rect x / y, raising a P2-01 soft warning on a hit. The auto-rounding tool (`svg-snap-grid.mjs`) is proposed tooling (not yet implemented); until it lands, align manually with snap-to-grid 4px, and do not assume a ready-made script exists to run on this basis.

source: huashu-incident-2026-04-20

---

## P2-02：chevron marker `<defs>` duplicated across the 13 diagram-types

### Symptom
The 13 `references/diagram-types/*.md` example SVGs each inline `<defs><marker id="chevron">...</marker></defs>`, totaling 13 near-identical marker definitions scattered across files, so later edits to the marker style require changing 13 places.

### Root cause
The author inlines the marker in each file for the convenience of single-file independent rendering, ignoring that the marker is a cross-diagram shared asset that ideally should be hoisted to a single shared `<defs>` source for single-point maintenance.

### Fix
Observation item (observed; proposed tooling not yet implemented): in the future the canonical chevron / dot / arrow marker definitions can be centralized into a single shared `<defs>` block that all 13 diagram-types/*.md reference. The currently executable detection is: `check.py` counts occurrences of the chevron marker `<polygon points="0,0 10,5 0,10"/>` literal across files; > 1 raises a P2-02 hoist-suggestion warning (soft). Until a shared source lands, do not create new files on this basis.

source: dogfood-v1.3-handoff

---

## P2-03：slide-core layout name not in the 22-lock-list

### Symptom
The slide-core HTML `data-layout="..."` takes a self-invented name like `hero-split` / `triple-column` that is not in the swiss preset's 22 locked layout whitelist, so `validate-swiss-deck.mjs` cannot apply the corresponding grid CSS and the entire slide falls back to the fallback style.

### Root cause
The author freely names the layout in PPT-thinking, without aligning to the swiss preset's 22 canonical layouts; the authoritative list lives in `references/canonical-tokens.md` §Slide Layout Registry (22 entries, mapped to guizang S01-S22), not re-copied in this file to avoid dual source-of-truth drift. The `LOCK_LIST` mechanical validation in `book/scripts/validate-swiss-deck.mjs` fails any unknown layout.

### Fix
At the slide-core generation stage, the `data-layout` value must come from the 22-layout lock list in `references/canonical-tokens.md` §Slide Layout Registry; if not in it, fail. The existing validation mechanism is `book/scripts/validate-swiss-deck.mjs` (`LOCK_LIST` mechanical comparison); `check.py` can add a synchronized check.

source: kami-spec-L86

---

## P2-04：en variant HTML contains a CJK font stack

### Symptom
The long-form / slide HTML produced by `--locale en` has a `font-family` containing CJK font names like `"Noto Sans TC"` / `"PingFang TC"` / `"思源黑體"`, causing English paragraphs to fall back to a CJK font's Latin glyphs, with line / letter spacing inconsistent with the Inter / Söhne design intent.

### Root cause
The author reuses the zh variant's font stack without splitting by locale; TASK-schemas-04 states explicitly that the en / zh variants must each have their own font stack: en uses Inter / Söhne / system-ui, zh uses Noto Sans TC / PingFang TC.

### Fix
typography.css splits the font-family into two segments, `:lang(en)` and `:lang(zh)`; at build time, validate for the `--locale en` output that the stylesheet's `font-family` contains no CJK font name (whitelist comparison). schemas sanity adds a locale × font-family cross-check, failing P2-04 on a hit.

source: dogfood-v1.3-handoff

---

## P3-01：SKILL.md contains a fractional heading

### Symptom
A baransu skill SKILL.md contains fractional-numbered headings like `### 0.5 Pre-flight` / `### 2.5 Cleanup`, scrambling outline / TOC tool ordering and making markdown lint complain about the heading sequence.

### Root cause
The author uses fractional numbering "to insert a section without touching the existing 1 / 2 / 3 numbering"; the M3 cosmetic stance: heading numbering should be consecutive integers, and inserting a section requires renumbering the subsequent headings or switching to `#### a`.

### Fix
SKILL.md lint adds a `^### \d+\.\d+` regex detection; a hit raises a P3-01 advisory (does not block merge, but the PR message prompts a renumber). In v1.5, promoted to P2 depending on prevalence.

source: dogfood-v1.3-handoff

---

## P3-02：chevron marker `fill` takes a value other than `"none"` or `"currentColor"`

### Symptom
An SVG `<marker id="chevron">` contains `<polygon fill="black"/>` or `fill="#000"`, causing the print pipeline (especially PDF/A mode) to render a solid square when the marker stroke and fill are the same color.

### Root cause
The author treats the marker as a solid element and sets a fill; kami spec convention: chevron marker `fill="currentColor"` pairs with an outer `<path stroke="currentColor" marker-end="url(#chevron)"/>`, letting the stroke color determine the marker color. `fill="none"` applies to a hollow marker (uncommon).

### Fix
Standardize the diagram-types/*.md example SVG marker polygon fill to `"currentColor"`; the hollow-chevron exception uses `"none"`. `check.py` raises a P3-02 advisory when the marker polygon fill is neither `currentColor` nor `none`.

source: kami-spec-L86

---

## future-trigger observation items

Each time a `/design preset` dogfood run completes, write the top-5 warnings that `check.py` surfaced into this section's "observation items"; a warning appearing in 3 consecutive releases is automatically evaluated for promotion to P2 or P1. Currently under observation:

- `<figure>` missing `<figcaption>` (outside the image_slot layout)
- KPI tile count inside `kpi-grid` < 3 or > 6
- SVG `viewBox` missing, or its ratio does not match the slot
- `<aside>` footnote font-size floor
- whether the long-form bullets cap should be promoted to P0
