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

## Slide Layout Registry

對標 guizang S01-S22；由 `book/scripts/validate-swiss-deck.mjs` LOCK_LIST 機械驗證。三 preset（紙 / swiss / google-design）的 `slide-cores/` 必須對齊以下 22 layout 命名與用途；任何不在 lock list 內的 layout 名為 hard fail。

`required-section-count` 指 layout 內必填語意區塊（heading / body / caption / cell …）下限；`SVG-allowed-types` 為該 layout 內可嵌入的 SVG 圖表類型 slug（對應 `book/references/diagram-types/type-{slug}.md` 13 個 status=complete diagram-type 之一：`architecture / flowchart / sequence / state / er / timeline / swimlane / quadrant / nested / tree / layers / venn / pyramid`）。`none` = 禁止嵌入 SVG（image-heavy 或純排版）；`optional` = 可嵌入但無語意必選 type。

| layout-name | use-case | required-section-count | SVG-allowed-types |
| --- | --- | --- | --- |
| `title` | Deck cover：品牌 / 主題 / 講者 | ≥ 3（kicker / title / metadata） | none |
| `section` | 章節間隔頁：粗體標題 + 可選編號 | ≥ 1 | none |
| `content-bullets` | H2 + 3-7 條 bullet 列表 | ≥ 4（heading + 3 bullets） | architecture / flowchart |
| `quote` | 抽引句 + 署名 | 2 | none |
| `data` | 單一主導數字 + context | 2-3 | quadrant |
| `kpi-grid` | 4-6 格 KPI 數字矩陣 | 4-6 | none |
| `timeline` | 水平里程碑軸 | 5-7 | timeline |
| `process` | 連續 N 步流程 | 5 | flowchart |
| `testimonial` | 人像 + 引述 + 署名 | 3 | none（image-heavy） |
| `agenda` | 1-N 編號議程 | 4-8 | none |
| `stat-hero` | 超大數字 + supporting copy | 2 | none |
| `icon-grid` | 4 / 6 / 9 格 icon + 標題 | 4-9 | none（icons 為 mono primitives，非 diagram-type） |
| `table-heavy` | 對照表 + zebra row | 1（table） | none |
| `before-after` | 水平左右對比 | 2 | optional |
| `divider` | 章節分隔 title only | 1 | none |
| `closing` | Thank-you / 聯絡 / next-step | 2-3 | none |
| `toc` | 全 deck 目錄 | ≥ 4 | none |
| `two-column` | 左右等寬雙欄 | 2 | optional |
| `image-full` | 滿版圖 + caption overlay | 2 | none |
| `comparison` | 2×2 quadrant 或 side-by-side | 3-4 | quadrant / venn |
| `quote-stack` | 3 條堆疊引述 callout | 3-6 | none |
| `breakout` | 重點 insight 強調 callout box | 1-2 | optional |
