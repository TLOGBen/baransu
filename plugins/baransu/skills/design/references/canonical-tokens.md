## Contents

- Surface (5)
- Accent (2)
- Text hierarchy (5)
- Border (2)
- Font (3)
- Modular Scale — Perfect Fourth (`r = 1.333`)
- Shadow (2)
- Spacing — 4pt grid (7)
- Radius (7)
- Layout (3)
- Semantic (2)
- tokens.css first line is the preset identifier comment
- v1.2 → v1.3 banned naming list
- Slide Layout Registry

# Canonical Token Schema (v1.3)

The baransu design system uses a fixed vocabulary of CSS custom-property names that **every** preset's `tokens.css` must define. HTML skeletons (design-cores/, slide-cores/) consume tokens by these canonical names only — preset-specific token names (e.g. Material `--md-*`, v1.2 `--brand`/`--parchment`) MUST be wrapped as internal aliases that resolve to canonical names.

`scripts/check.py` enforces this schema; gen mode derives values for these 36 names from the interview answers.

## Surface (5)
`--paper` page background • `--surface` card • `--surface-strong` interactive surface • `--dark-surface` dark container • `--deep-dark` dark page

## Accent (2)
`--accent` primary accent (sole chromatic, ≤5% surface) • `--accent-on` foreground on accent fills

## Text hierarchy (5)
`--ink` structural ink alias • `--text-primary` body & heading • `--text-secondary` table headers, secondary • `--text-muted` captions, tertiary • `--text-faint` metadata, placeholder

## Border (2)
`--border` primary divider • `--border-soft` row separator

## Font (3)
`--font-sans` • `--font-serif` (sans alias in sans-only presets) • `--font-mono`

## Modular Scale — Perfect Fourth (`r = 1.333`)

All three presets type-scale on the perfect fourth (`r = 4/3 ≈ 1.333`), the
typographic golden mean for editorial and Swiss-discipline layouts.
v1.2 used a minor third (`r = 1.2`) which collapsed the H1 → body span to
2.0× and left H2 / H3 visually adjacent (1.20×); v1.3 widens to 2.37× and
restores headline hierarchy.

Computation (anchor on `body = 16px`):

| Role | Formula           | Computed | Rounded | rem      |
| ---- | ----------------- | -------- | ------- | -------- |
| body | `r^0 · 16`        | 16.00    | 16      | 1rem     |
| H3   | `r^1 · 16`        | 21.33    | 21      | 1.3125rem|
| H2   | `r^2 · 16`        | 28.43    | 28      | 1.75rem  |
| H1   | `r^3 · 16`        | 37.90    | 38      | 2.375rem |

Tolerance: integer rounding may drift; gate is `h1:body ≈ 2.37 ± 0.05` and
`h2:h3 ≈ 1.333 ± 0.02`. Presets whose body deviates (e.g. 15 / 14px) must
re-derive from their own anchor — never copy raw numbers across presets.

**Banned ratios (v1.2 residue, MUST NOT appear in any preset tokens.css)**:
`× 2.2` (old H1:body), `× 1.24` (old H2:H3), `× 1.2` minor-third chain.

## Shadow (2)
`--shadow-ring` (`0 0 0 1px var(--border)`) • `--shadow-whisper` (elevated hover)

## Spacing — 4pt grid (7)
`--space-xs` `--space-sm` `--space-md` `--space-lg` `--space-xl` `--space-2xl` `--space-3xl`

## Radius (7)
`--radius-xs` `--radius-sm` `--radius-md` `--radius-lg` `--radius-xl` `--radius-2xl` `--radius-hero`

## Layout (3)
`--cover-title-align` (`center` or `left`) • `--grid-columns` (default 12) • `--grid-gutter`

## Semantic (2)
`--delta-up` (metric positive) • `--delta-down` (metric negative)

## tokens.css first line is the preset identifier comment

Format: `/* preset: <slug> */` (slug is `kami` / `google-design` / `swiss` / gen-slug).
Parsed by `scripts/check.py` and `/baransu:book` GATE-F.

## v1.2 → v1.3 banned naming list

The following v1.2 token names are dropped in v1.3; tokens.css MUST NOT define them and DESIGN.md prose MUST NOT reference them:

`--brand` / `--brand-light` / `--brand-tint` / `--brand-tint-strong` / `--parchment` / `--ivory` / `--olive` / `--warm-sand` / `--stone` / `--near-black` / `--dark-warm` / `--charcoal` / `--sans` / `--serif` / `--mono`

## Slide Layout Registry

Benchmarked against guizang S01-S22; mechanically verified by the `book/scripts/validate-swiss-deck.mjs` LOCK_LIST. The `slide-cores/` of all three presets (paper / swiss / google-design) must align with the following 22 layout names and use-cases; any layout name not in the lock list is a hard fail.

`required-section-count` is the lower bound of required semantic blocks (heading / body / caption / cell …) within a layout; `SVG-allowed-types` is the SVG chart-type slug that may be embedded in that layout (one of the 13 status=complete diagram-types corresponding to `book/references/diagram-types/type-{slug}.md`: `architecture / flowchart / sequence / state / er / timeline / swimlane / quadrant / nested / tree / layers / venn / pyramid`). `none` = SVG embedding forbidden (image-heavy or pure layout); `optional` = embeddable but no semantically required type.

| layout-name | use-case | required-section-count | SVG-allowed-types |
| --- | --- | --- | --- |
| `title` | Deck cover: brand / theme / speaker | ≥ 3 (kicker / title / metadata) | none |
| `section` | Section-break page: bold title + optional number | ≥ 1 | none |
| `content-bullets` | H2 + 3-7 bullet list | ≥ 4 (heading + 3 bullets) | architecture / flowchart |
| `quote` | Pull quote + attribution | 2 | none |
| `data` | Single dominant figure + context | 2-3 | quadrant |
| `kpi-grid` | 4-6 cell KPI number matrix | 4-6 | none |
| `timeline` | Horizontal milestone axis | 5-7 | timeline |
| `process` | Sequential N-step flow | 5 | flowchart |
| `testimonial` | Portrait + quote + attribution | 3 | none (image-heavy) |
| `agenda` | 1-N numbered agenda | 4-8 | none |
| `stat-hero` | Oversized figure + supporting copy | 2 | none |
| `icon-grid` | 4 / 6 / 9 cell icon + title | 4-9 | none (icons are mono primitives, not a diagram-type) |
| `table-heavy` | Comparison table + zebra row | 1 (table) | none |
| `before-after` | Horizontal left/right comparison | 2 | optional |
| `divider` | Section separator, title only | 1 | none |
| `closing` | Thank-you / contact / next-step | 2-3 | none |
| `toc` | Full-deck table of contents | ≥ 4 | none |
| `two-column` | Equal-width two-column layout | 2 | optional |
| `image-full` | Full-bleed image + caption overlay | 2 | none |
| `comparison` | 2×2 quadrant or side-by-side | 3-4 | quadrant / venn |
| `quote-stack` | 3 stacked quote callouts | 3-6 | none |
| `breakout` | Key insight emphasis callout box | 1-2 | optional |
