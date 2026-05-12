# Design System: 紙 (Kami)

## 1. Visual Theme & Atmosphere

**哲學**：溫潤羊皮紙感。介面如一張好紙——有重量、有肌理、讓文字安靜地躺在上面。

Kami 十不變量（來自 CHEATSHEET.md canonical invariants）：
1. 背景不用純白，用暖調羊皮紙 `#f5f4ed`
2. Accent 唯一墨藍 `#1B365D`，全頁只此一個彩色
3. 中性灰限定暖調（黃棕底色），禁冷灰
4. 每頁只用一套 serif；`--sans` 永遠 alias `--serif`，不引入獨立 sans
5. Serif weight 鎖定 500——禁用 bold（700）做 heading
6. 行高：headline 1.1–1.3 / 密排 1.4–1.45 / 閱讀 1.5–1.55
7. 字距：中文 0.1–0.3pt；英文 body 0；label/cap +0.2–1pt
8. Tag 背景只用 solid hex（禁 rgba，WeasyPrint 渲染 bug）
9. 深度只用 ring/whisper 陰影，禁硬邊陰影
10. 禁 italics（模板與 demo 均適用）

**密度**：適中。留白是設計元素，不是空間浪費。段落間距寬鬆，讓閱讀有呼吸感。

**氛圍**：書房、工藝、手感印刷品。不是高科技冷峻，是紙墨溫度。

---

## 2. Color Palette & Roles

| Token Name | Hex | Role |
|------------|-----|------|
| `--parchment` | `#f5f4ed` | 主背景（Primary background） |
| `--ivory` | `#faf9f5` | 卡片、面板背景（Card / panel surface） |
| `--warm-sand` | `#e8e6dc` | 按鈕、互動表面（Button / interactive surface） |
| `--dark-surface` | `#30302e` | 深色容器（Dark container） |
| `--deep-dark` | `#141413` | 深色頁面背景（Dark page background） |
| `--brand` | `#1B365D` | 主色 / Accent（Ink-blue，唯一彩色，≤5% 表面） |
| `--brand-light` | `#2D5A8A` | 深色背景上的連結 / 亮版（Link on dark surface） |
| `--near-black` | `#141413` | 主要文字（Primary text） |
| `--dark-warm` | `#3d3d3a` | 次要文字、表格標頭（Secondary text / table header） |
| `--olive` | `#504e49` | 輔助文字、說明（Subtext / description） |
| `--stone` | `#6b6a64` | 第三層文字、metadata（Tertiary / metadata） |
| `--charcoal` | `#4d4c48` | 深色輔助文字（Dark muted，介於 olive 與 stone 之間） |
| `--border` | `#e8e6dc` | 主要邊框、分隔線（Primary border / divider） |
| `--border-soft` | `#e5e3d8` | 次要邊框、表格行線（Secondary border / row separator） |
| `--brand-tint` | `#EEF2F7` | Tag 背景最淺版（solid hex，0.08 rgba equivalent） |
| `--brand-tint-strong` | `#E4ECF5` | Tag 背景標準版（solid hex，0.18 rgba equivalent） |

**用色原則**：
- 背景層次：`--parchment` → `--ivory`（卡片浮在底色上）
- 文字層次：`--near-black` → `--dark-warm` → `--olive` → `--stone`
- 互動表面：`--warm-sand`；hover/focus 時用 ring 陰影傳達狀態
- 主色 `--brand` 用於 accent、CTA、section left bar，佔比控制在 ≤5% 表面
- 禁用純白 `#ffffff`；禁用純黑 `#000000`

**RGBA → Solid hex 換算**（WeasyPrint 相容，以羊皮紙底 + 墨藍為基底）：

| Alpha | Solid hex | 用途 |
|-------|-----------|------|
| 0.08 | `#EEF2F7` | 最淺 tag 背景（預設） |
| 0.14 | `#E4ECF5` | — |
| 0.22 | `#D0DCE9` | — |
| 0.30 | `#D6E1EE` | — |

---

## 3. Typography Rules

**英文字型堆疊**：
```css
--serif: Charter, Georgia, Palatino, "Times New Roman", serif;
--sans:  var(--serif);
--mono:  "JetBrains Mono", "SF Mono", "Fira Code", Consolas, Monaco, monospace;
```

**中文字型堆疊**：
```css
--serif: "TsangerJinKai02", "Source Han Serif SC", "Noto Serif CJK SC",
         "Songti SC", "STSong", Georgia, serif;
--sans:  var(--serif);
--mono:  "JetBrains Mono", "SF Mono", Consolas, "TsangerJinKai02",
         "Source Han Serif SC", monospace;
```

**日文字型堆疊**：
```css
--serif: "YuMincho", "Yu Mincho", "Hiragino Mincho ProN",
         "Noto Serif CJK JP", "Source Han Serif JP",
         "TsangerJinKai02", Georgia, serif;
--sans:  var(--serif);
```

**層次規則**（螢幕 px；印刷以 pt × 1.33 換算）：

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Display | 48px | 500 | 1.10 |
| H1 | 29px (≈22pt) | 500 | 1.20 |
| H2 | 21px (≈16pt) | 500 | 1.25 |
| H3 | 17px (≈13pt) | 500 | 1.30 |
| Body Lead | 15px | 400 | 1.55 |
| Body | 13px | 400 | 1.55 |
| Body Dense | 12px | 400 | 1.42 |
| Caption / Label | 12px | 400 / 600 (label) | 1.45 |
| Code | 12px (mono) | 400 | 1.60 |

**字型規則**：
- **Heading weight 鎖定 500**，禁用 700 bold——這是 invariant #5
- 標題不用 all-caps，不用 italics（invariant #10）
- `--sans` 永遠 alias `--serif`，不引入獨立 sans-serif 字族（invariant #4）
- 所有含 CJK 內容的字型宣告（header、footer、SVG label、code）必須包含 CJK fallback
- 中英文混排：中文字型在前，英文 Charter/Georgia 在後

---

## 4. Component Stylings

**陰影系統**（兩種，無其他）：
- **Ring**：`box-shadow: 0 0 0 1px var(--border)` — 靜態邊框感
- **Whisper**：`box-shadow: 0 4px 24px rgba(0,0,0,0.05)` — hover 浮起感
- 禁用硬邊陰影（無 blur 或 blur < 4px 的 drop shadow）

**Button（按鈕）**：
- Primary：`--brand` 填色，`--ivory` 文字，border-radius `8px`，padding `8px 14px`
- Secondary：`--warm-sand` 背景，`--dark-warm` 文字
- Hover：Primary 亮化至 `--brand-light`；Secondary 加 whisper 陰影
- Disabled：整體透明度降至 40%，cursor not-allowed
- 字型 12px sans（alias serif），無 italics

**Card（卡片）**：
```css
background: var(--ivory);
border: 0.5pt solid var(--border);
border-radius: 8px;
padding: 20px 24px;
```
Hover：加 whisper shadow `0 4px 24px rgba(0,0,0,0.05)`

**Input（輸入框）**：
- 靜態：ring shadow（`0 0 0 1px var(--border)`），border-radius `6px`
- Focus：ring 換成 `0 0 0 1px var(--brand)`
- 背景：`--ivory`；佔位符：`--stone`

**Tag / Badge**（solid hex 背景，禁 rgba）：
```css
background: #EEF2F7;           /* solid hex，非 rgba */
color: var(--brand);
font-size: 9pt; font-weight: 600;
padding: 1pt 5pt;
border-radius: 2pt;
letter-spacing: 0.4pt;
text-transform: uppercase;
```

**Section Title**（brand left bar，Kami 簽名元件）：
```css
font-size: 14pt; font-weight: 500;
color: var(--near-black);
border-left: 2.5pt solid var(--brand);
border-radius: 1.5pt;
padding-left: 8pt;
margin: 24pt 0 10pt 0;
```

**Quote（引言）**：
```css
border-left: 2pt solid var(--brand);
padding: 4pt 0 4pt 14pt;
color: var(--olive);
line-height: 1.55;
```

**Code block**：`--ivory` 背景，`0.5pt solid var(--border)` 邊框，`6pt` radius，mono 字型

---

## 5. Layout & Spacing

**間距單位**：4pt 基底（2–3 / 4–5 / 8–10 / 16–20 / 24–32 / 40–60 / 80–120 pt）

**Border Radius Scale**：`4pt → 6pt → 8pt（預設）→ 12pt → 16pt → 24pt → 32pt（hero）`

**網格**：12 欄，column gutter 24px，page margin 48px（桌機）/ 16px（手機）

**留白哲學**：
- 內容區塊間距至少 32px
- 標題與下方內容間距：16px；與上方區塊間距：48px
- 卡片內 padding：20–24px

**響應式斷點**：
- Mobile：< 640px
- Tablet：640–1024px
- Desktop：> 1024px

**最大寬度**：閱讀欄位最大 680px；全版面容器最大 1200px

---

## 6. Iconography & Imagery

**圖示風格**：
- 線條型（outline），stroke-width 1.5–2px
- 圓角端點（round linecap / linejoin）
- 尺寸：16px / 20px / 24px 三種標準尺寸
- 顏色繼承文字色（currentColor），特殊強調才用 `--brand`

**圖片處理原則**：
- 避免高飽和度攝影；優先使用低飽和度、暖調、有紙質感的視覺
- Hero 圖可套用暖色調濾鏡（warm overlay）與 `--parchment` 的漸層疊加
- 人物圖像避免過於商業化的 stock photo 風格
- SVG 插圖優先於位圖，風格採細線手繪或幾何簡約
- Data chart 色序：`#1B365D` → `#504e49` → `#6b6a64` → `#b8b7b0` → `#d4d3cd` → `#EEF2F7`

---

## 7. Motion & Animation

**過渡時間**：
- Micro-interaction（hover、focus）：150ms
- 狀態切換（顯示/隱藏、展開/收折）：250ms
- 頁面層級過渡：350ms

**Easing 曲線**：
- 標準：`ease-out`
- Spring 感（彈性展開）：`cubic-bezier(0.34, 1.56, 0.64, 1)`

**動畫限制**：
- 不使用純粹裝飾性的循環動畫
- 尊重 `prefers-reduced-motion`：所有動畫在此媒體查詢下降至 0ms
- 避免大範圍平移；優先使用 opacity + scale 的組合

---

## 8. Do / Don't

**Do**：
- ✅ 使用暖調羊皮紙色（`#f5f4ed`）作為主背景
- ✅ 墨藍（`#1B365D`）作為唯一強調色，表面佔比 ≤5%
- ✅ 採用 Charter / TsangerJinKai02 的 serif 字型堆疊
- ✅ Heading weight 用 500，不用 700/bold
- ✅ Ring（`0 0 0 1px var(--border)`）或 whisper（`0 4px 24px rgba(0,0,0,0.05)`）陰影
- ✅ Body 行高 1.5–1.55，headline 行高 1.1–1.3
- ✅ Tag 背景用 solid hex（`#EEF2F7`），不用 rgba
- ✅ `--sans: var(--serif)` 讓 sans alias serif，不引入獨立字族
- ✅ Section title 用 2.5pt brand left bar 作為 Kami 簽名視覺

**Don't**：
- ❌ 禁用純白背景 `#ffffff`
- ❌ 禁用冷灰色調（cool grays、藍調 neutral）
- ❌ 禁用硬邊陰影（blur < 4px 的 drop shadow）
- ❌ 禁在 tag/badge 背景使用 rgba（WeasyPrint bug）
- ❌ 不使用 bold（700）做 heading——weight 鎖定 500
- ❌ 不使用 italics（模板與 demo 均禁用）
- ❌ 不使用純無襯線字族做全頁排版
- ❌ 不使用高飽和度撞色搭配
- ❌ 不在介面中使用裝飾性循環動畫

---

## 9. AI Prompt Guide

以下提示詞可在全新 AI 對話中重現本設計系統的視覺語言：

> Design a UI using the Kami paper design system. Background: warm parchment `#f5f4ed`; card surfaces: `#faf9f5`; interactive surfaces: `#e8e6dc`. Primary accent: ink-blue `#1B365D` (≤5% surface area). Text hierarchy: near-black `#141413` → warm dark `#3d3d3a` → olive `#504e49` → stone `#6b6a64`. Borders: `--border: #e8e6dc` (primary), `--border-soft: #e5e3d8` (secondary). Typography: Charter/Georgia for English, TsangerJinKai02/Noto Serif SC for Chinese — all weights locked at 500 for headings (no bold), 400 for body. `--sans` aliases `--serif`. Line-height: headlines 1.1–1.3, body 1.5–1.55. Shadows: ring only (`0 0 0 1px var(--border)`) for static; whisper (`0 4px 24px rgba(0,0,0,0.05)`) for hover. No hard drop shadows. Tags use solid hex `#EEF2F7` (never rgba). Section titles use a 2.5pt brand left bar. No italics anywhere. The aesthetic is warm printed paper — ink on parchment, craft over chrome.

### (a) 焦點節點上限

每一頁、每一張投影片，焦點節點上限為 **1–2 個**：
- 主焦點（1 個必有）：以 `--accent: #1B365D` 染色——通常為 H1 標題、品牌左 bar、或唯一 CTA。
- 次焦點（0–1 個，可選）：以「結構強度」而非「顏色」承擔——例如加粗的 metric 數字、或一條明顯的 left-bar 分節線。次焦點 **不得** 再用 accent；違反即視為色彩過載。

### (b) accent hex 設計理據

主 accent `#1B365D`（ink-blue）拆解：

| Space | Coordinates | 設計意圖 |
|-------|-------------|----------|
| HEX | `#1B365D` | 主規格；WeasyPrint print pipeline 以此為準 |
| HSL | `H 211°, S 55%, L 24%` | 冷色相位 211° 接近 royal blue 但偏深；S 55% 避免過飽和顯霓虹；L 24% 屬「深色印刷藍」——在 warm parchment 上形成高對比但不刺眼 |
| oklch（advisory） | `oklch(0.32 0.08 256)` | screen / 設計工具參考用；色相 256° 為 perceptual 等價；C 0.08 對應印刷藍的低彩度 |

選色理由：對齊鋼筆墨水（fountain pen ink）在 cream paper 上的視覺記憶；避開飽和 royal blue（過於數位）與 navy（過於企業）兩端。

### (c) 我不是什麼（anti-patterns / allowed contradictions）

- no second accent — 全頁只有一個彩色；任何「次強調色」皆以中性灰階重量替代
- no italics — 模板與 demo 均禁用，襯線斜體在 print pipeline 容易掉字
- no cool accent shift — accent 不得偏向 cyan / teal 等冷色；warm parchment 需要 warm-shifted blue
- no oklch in attribute — `tokens.css` / `design-cores/` HTML 內聯 style 不可出現 `oklch(`；oklch 僅為文件 advisory
- no gradient bg — 背景永遠是平塗紙色；禁 linear-gradient / radial-gradient 背景
- no hard drop shadow — 深度只用 ring + whisper；禁 `0 8px 16px rgba(0,0,0,0.3)` 類硬邊陰影
- no all-caps headings — 中英混排不使用 letter-spacing + uppercase 的設計派頭
