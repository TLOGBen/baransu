# Canonical Token Schema (v1.3)

The baransu design system uses a fixed vocabulary of CSS custom-property names that **every** preset's `tokens.css` must define. HTML 骨架 (design-cores/, slide-cores/) consume tokens by these canonical names only — preset-specific token names (e.g. Material `--md-*`, v1.2 `--brand`/`--parchment`) MUST be wrapped as internal aliases that resolve to canonical names.

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
typographic 印刷學 golden mean for editorial and Swiss-discipline layouts.
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

## tokens.css 第一行為 preset 識別註解

格式：`/* preset: <slug> */`（slug 為 `kami` / `google-design` / `swiss` / gen-slug）。
由 `scripts/check.py` 與 `/baransu:book` GATE-F 解析。

## v1.2 → v1.3 命名禁用清單

下列 v1.2 token 命名在 v1.3 已捨棄；tokens.css 不得定義、DESIGN.md 內文不得引用：

`--brand` / `--brand-light` / `--brand-tint` / `--brand-tint-strong` / `--parchment` / `--ivory` / `--olive` / `--warm-sand` / `--stone` / `--near-black` / `--dark-warm` / `--charcoal` / `--sans` / `--serif` / `--mono`
