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
