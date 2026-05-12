# Design System: Swiss (IKB)

## 1. Visual Theme & Atmosphere

**哲學**：Swiss International Style——高級灰白底紙上，單一高飽和強調色（IKB ink）。介面像 Müller-Brockmann 的網格圖：克制、精準、留白即構圖。

Swiss 不變量（從 Kami 可移植集合 + Swiss-specific）：
1. 背景不用純白，用中性 off-white 紙感 `--paper: #fafaf8`
2. Accent 唯一 IKB 墨藍 `--accent: #002FA7`，全頁只此一個彩色
3. 中性灰限定真中性（無冷無暖偏調）；禁高飽和 neutral
4. 純 sans-serif 字族：`'Inter', 'Helvetica Neue', 'Noto Sans TC', sans-serif`（無 serif 字串）
5. Heading weight 上限 700，預設 500——禁用 800/900
6. 行高：headline 1.10–1.30 / 密排 1.40–1.45 / 閱讀 1.50–1.55
7. 字距：title −0.01em（緊收）；body 0；label/cap +0.04em
8. Tag 背景只用 solid hex（禁 rgba，WeasyPrint 渲染 bug）
9. 深度只用 ring/whisper 陰影，禁硬邊陰影
10. 禁 italics（模板與 demo 均適用）

**密度**：克制。留白是結構元素，網格與對齊是主導語法。

**氛圍**：包浩斯、Helvetica、IKB ultramarine——機能美學，無裝飾。

---

## 2. Color Palette & Roles

| Token Name | Hex | Role |
|------------|-----|------|
| `--paper` | `#fafaf8` | 主背景（Primary background；中性 off-white） |
| `--surface` | `#f2f2ef` | 卡片、面板背景（Card / panel surface） |
| `--surface-strong` | `#e6e5e0` | 按鈕、互動表面（Button / interactive surface） |
| `--dark-surface` | `#1a1a1a` | 深色容器（Dark container） |
| `--deep-dark` | `#0a0a0a` | 深色頁面背景（Dark page background） |
| `--ink` | `#0a0a0a` | 主要文字 alias / 結構墨色（Structural ink） |
| `--accent` | `#002FA7` | IKB ultramarine——唯一強調色（≤5% 表面） |
| `--accent-on` | `#ffffff` | accent 之上文字 / icon 色 |
| `--text-primary` | `#0a0a0a` | 主要文字（Body & heading） |
| `--text-secondary` | `#3a3a3a` | 次要文字、表格標頭 |
| `--text-muted` | `#5c5c5c` | 第三層文字、caption |
| `--text-faint` | `#8a8a8a` | metadata、placeholder |
| `--border` | `--paper` | 主要邊框、分隔線 |
| `--border-soft` | `--surface` | 次要邊框、表格行線 |

**用色原則**：
- 背景層次：`--paper` → `--surface`（卡片浮在底色上）
- 文字層次：`--text-primary` → `--text-secondary` → `--text-muted` → `--text-faint`
- 互動表面：`--surface-strong`；hover/focus 時用 ring 陰影傳達狀態
- 主色 `--accent` 用於 CTA、section bar、focus ring，佔比控制在 ≤5% 表面
- 禁用純白背景；`--accent-on` 為 accent 上的反白文字，僅限該情境使用

**Accent 單色原則**：IKB 為設計主軸，全頁只此一個高飽和色；其餘層次以中性灰調達成。

---

## 3. Typography Rules

**英文 / 中文字型堆疊**（單一 stack，sans-serif only）：
```css
--font-sans: 'Inter', 'Helvetica Neue', 'Noto Sans TC', sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, Monaco, monospace;
```

**字級層次**（螢幕 px；印刷以 pt × 1.33 換算）：

| Role | Size | Weight | Line Height | Tracking |
|------|------|--------|-------------|----------|
| Display | 56px | 500 | 1.10 | −0.02em |
| H1 | 36px | 500 | 1.15 | −0.01em |
| H2 | 24px | 500 | 1.25 | −0.01em |
| H3 | 20px | 500 | 1.30 | 0 |
| Body Lead | 17px | 400 | 1.55 | 0 |
| Body | 15px | 400 | 1.55 | 0 |
| Body Dense | 13px | 400 | 1.42 | 0 |
| Caption / Label | 12px | 500 | 1.45 | +0.04em |
| Code | 13px (mono) | 400 | 1.55 | 0 |

**字型規則**：
- **Heading weight 預設 500**，上限 700——禁用 800/900
- 標題不用 all-caps；不用 italics（Kami 可移植 invariant）
- `--font-sans` 為唯一字族 stack；字串中嚴禁出現 `serif` 以外的 generic 標記（sans-serif fallback 為允許的關鍵字 token，但 serif 不得出現於前綴名單）
- 中英文混排：Inter 為英文主字、Noto Sans TC 涵蓋中文；皆 sans-serif
- 字距規則：headline 緊收（−0.01em ~ −0.02em），caption 放鬆（+0.04em）

---

## 4. Component Stylings

**陰影系統**（兩種，無其他）：
- **Ring**：`box-shadow: 0 0 0 1px var(--border)` — 靜態邊框感
- **Whisper**：`box-shadow: 0 4px 24px var(--surface-strong)` — hover 浮起感（solid token 版本，避免 rgba）
- 禁用硬邊陰影（無 blur 或 blur < 4px 的 drop shadow）

**Button（按鈕）**：
- Primary：`--accent` 填色，`--accent-on` 文字，border-radius `4px`，padding `8px 16px`
- Secondary：`--surface-strong` 背景，`--text-primary` 文字
- Hover：Primary 加 ring `0 0 0 1px var(--accent)`；Secondary 加 whisper 陰影
- Disabled：整體透明度降至 40%，cursor not-allowed
- 字型 13px sans，weight 500，無 italics

**Card（卡片）**：
```css
background: var(--surface);
border: 1px solid var(--border);
border-radius: 4px;
padding: 20px 24px;
```
Hover：加 whisper shadow `0 4px 24px var(--surface-strong)`

**Input（輸入框）**：
- 靜態：ring shadow（`0 0 0 1px var(--border)`），border-radius `2px`
- Focus：ring 換成 `0 0 0 2px var(--accent)`
- 背景：`--paper`；佔位符：`--text-faint`

**Tag / Badge**（solid hex 背景，禁 rgba）：
```css
background: var(--surface-strong);
color: var(--accent);
font-size: 11px; font-weight: 500;
padding: 2px 8px;
border-radius: 2px;
letter-spacing: 0.04em;
text-transform: uppercase;
```

**Section Title**（accent left bar，Swiss 簽名元件）：
```css
font-size: 18px; font-weight: 500;
color: var(--text-primary);
border-left: 3px solid var(--accent);
padding-left: 12px;
margin: 32px 0 16px 0;
letter-spacing: -0.01em;
```

**Quote（引言）**：
```css
border-left: 2px solid var(--accent);
padding: 8px 0 8px 16px;
color: var(--text-secondary);
line-height: 1.55;
```

**Code block**：`--surface` 背景，`1px solid var(--border)` 邊框，`4px` radius，mono 字型

---

## 5. Layout & Spacing

**間距單位**：4px 基底（4 / 8 / 12 / 20 / 32 / 56 / 96 px——對應 token scale）

**Border Radius Scale**：`0px → 2px → 4px（預設）→ 8px → 12px → 16px → 24px（hero）`

**網格**：12 欄，column gutter 24px，page margin 56px（桌機）/ 16px（手機）

**對齊哲學**（Swiss 核心）：
- 一切都向 baseline grid 對齊
- 標題、副標題、body 對齊到同一網格線
- `cover-title-align: left` / `section-title-align: left`——封面與小節都 flush-left

**留白哲學**：
- 內容區塊間距至少 32px
- 標題與下方內容間距：16px；與上方區塊間距：56px
- 卡片內 padding：20–24px

**響應式斷點**：
- Mobile：< 640px
- Tablet：640–1024px
- Desktop：> 1024px

**最大寬度**：閱讀欄位最大 720px；全版面容器最大 1200px

---

## 6. Iconography & Imagery

**圖示風格**：
- 線條型（outline），stroke-width 1.5–2px
- 直角端點（square / round 二選一，全站一致；預設 round linecap / linejoin）
- 尺寸：16px / 20px / 24px 三種標準尺寸
- 顏色繼承文字色（currentColor），特殊強調才用 `--accent`

**圖片處理原則**：
- 偏好幾何抽象、網格構成、單色高對比攝影
- Hero 圖可疊加 `--accent` 半透明遮罩或網格 overlay（但實作以 solid hex 完成，避免 rgba）
- 人物圖像避免商業 stock photo；偏向紀實或構成主義風格
- SVG 插圖優先於位圖，採嚴格幾何結構
- Data chart 色序：`#002FA7` → `#3a3a3a` → `#5c5c5c` → `#8a8a8a` → `#d9d9d4` → `#f2f2ef`

---

## 7. Motion & Animation

**過渡時間**：
- Micro-interaction（hover、focus）：120ms
- 狀態切換（顯示/隱藏、展開/收折）：200ms
- 頁面層級過渡：320ms

**Easing 曲線**：
- 標準：`ease-out`
- 機械感（Swiss 嚴格）：`cubic-bezier(0.4, 0.0, 0.2, 1)`——Material standard，無 overshoot

**動畫限制**：
- 不使用裝飾性循環動畫；Swiss 偏好靜態構成
- 尊重 `prefers-reduced-motion`：所有動畫在此媒體查詢下降至 0ms
- 避免大範圍平移；優先使用 opacity 與 1–2px 的位移

---

## 8. Do / Don't

**Do**：
- ✅ 使用中性 off-white（`--paper: #fafaf8`）作為主背景
- ✅ IKB ultramarine（`--accent: #002FA7`）作為唯一強調色，表面佔比 ≤5%
- ✅ 採用 Inter / Helvetica Neue / Noto Sans TC 的 sans-serif 字型堆疊
- ✅ Heading weight 預設 500，上限 700
- ✅ Ring 或 whisper 陰影（whisper 走 solid token 版本）
- ✅ Body 行高 1.5–1.55，headline 行高 1.10–1.30
- ✅ Tag 背景用 solid hex（透過 `var(--surface-strong)`），不用 rgba
- ✅ Section title 用 3px accent left bar
- ✅ 一切向 baseline grid 對齊，flush-left

**Don't**：
- ❌ 禁用純白背景
- ❌ 禁用第二個高飽和色——accent 唯一原則
- ❌ 禁用硬邊陰影（blur < 4px 的 drop shadow）
- ❌ 禁在 tag/badge 背景使用 rgba（WeasyPrint bug）
- ❌ 不使用 weight ≥ 800 做 heading
- ❌ 不使用 italics（模板與 demo 均禁用）
- ❌ 不引入 serif 字族——本 preset 為純 sans-serif
- ❌ 不使用裝飾性循環動畫
- ❌ 不使用置中對齊作為預設排版策略——Swiss 偏好 flush-left

---

## 9. AI Prompt Guide

以下提示詞可在全新 AI 對話中重現本設計系統的視覺語言：

> Design a UI using the Swiss IKB design system. Background: neutral off-white `var(--paper)` (token; hex `#fafaf8`); card surfaces: `var(--surface)`; interactive surfaces: `var(--surface-strong)`. Primary accent: International Klein Blue `var(--accent)` (token; hex `#002FA7`) — the only chromatic color, ≤5% surface area, paired with `var(--accent-on)` for foreground on filled regions. Text hierarchy: `var(--text-primary)` → `var(--text-secondary)` → `var(--text-muted)` → `var(--text-faint)`. Typography: `'Inter', 'Helvetica Neue', 'Noto Sans TC', sans-serif` — sans-serif only, no serif anywhere. Heading weight 500, body weight 400, headings tracked −0.01em, captions +0.04em. Line-height: headlines 1.10–1.30, body 1.50–1.55. Shadows: ring (`0 0 0 1px var(--border)`) for static; whisper (`0 4px 24px var(--surface-strong)`) for hover — solid tokens only, no rgba. Tags use solid hex via `var(--surface-strong)`. Section titles use a 3px accent left bar. All alignment flush-left to a 12-column baseline grid. No italics, no decoration, no second accent. The aesthetic is Swiss International Style — Müller-Brockmann grids, IKB ultramarine, function over ornament.

### (a) 焦點節點上限

每一頁、每一張投影片，焦點節點上限為 **1–2 個**：
- 主焦點（1 個必有）：以 `--accent: #002FA7`（IKB）染色——通常是 H1、3px accent left bar、或唯一 CTA。
- 次焦點（0–1 個，可選）：以「網格佔位」或「字級對比」承擔，不可再用 accent。Swiss 構成的張力來自 grid 與 negative space，不是色彩堆疊。

### (b) accent hex 設計理據

主 accent `#002FA7`（International Klein Blue / IKB）拆解：

| Space | Coordinates | 設計意圖 |
|-------|-------------|----------|
| HEX | `#002FA7` | 主規格；WeasyPrint print pipeline 以此為準 |
| HSL | `H 223°, S 100%, L 33%` | 高飽和深藍——對齊 Yves Klein 1960 年代專利配方 IKB-79 的螢幕近似；S 100% 是 Swiss IKB 的簽名，低於 S 90% 就失去純粹感；L 33% 確保白底對比 > 7:1 |
| oklch（advisory） | `oklch(0.38 0.20 268)` | perceptual 等價；C 0.20 在 sRGB gamut 邊緣，是 IKB 飽和度的視覺極限 |

選色理由：IKB 是 Swiss International Style 的色票記憶錨點（Müller-Brockmann 海報、Bauhaus 教具）；任何「navy」「royal blue」「indigo」皆為退讓，會稀釋網格構成的視覺權威。

### (c) 我不是什麼（anti-patterns / allowed contradictions）

對齊本專案 root `DESIGN.md` 列出的 10 條 Swiss 不變量，從中挑出 5 條最常被違反的 anti-pattern：

- no second accent — 全頁只有 IKB 一個彩色；任何「狀態色」（success / warning / error）若需出現，亦受 ≤5% 預算限制
- no italics — 模板與 demo 均禁用，Swiss 排版無斜體傳統
- no serif — `font-family` 不可出現 serif 字串；CJK 用 Noto Sans TC，不混 Noto Serif
- no rgba background — Tag / surface 背景只用 solid hex token，WeasyPrint 渲染 rgba 有 bug
- no centered default — 預設對齊一律 flush-left；置中只用於極少數標題情境，非全頁排版策略
- no high-saturation neutral — 中性灰必須真中性（無冷無暖偏調），禁帶藍 / 帶綠灰
