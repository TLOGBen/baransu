# Design System: Google (Material 3 / Material You)

## 1. Visual Theme & Atmosphere

**哲學**：Material You — 表達性、無障礙、動態色彩。介面是一塊有層次、有材質的數位平面，色彩、形狀、動效都為了傳達清晰的階層與狀態。

**Material 3 五大基調**：
1. **Personal**：色彩可由使用者壁紙、品牌或內容動態派生（dynamic color），baseline 配色僅為起點。
2. **Adaptive**：跨 compact / medium / expanded 三種視窗尺寸的響應式布局，不只縮放、是重排。
3. **Expressive**：30 種 type style（15 baseline + 15 emphasized）、彈性形狀 scale，鼓勵層次化的視覺表達。
4. **Accessible**：色彩 role 系統強制配對 on-* 對比文字色，確保 WCAG AA 對比度 ≥ 4.5:1。
5. **Material**：表面有「材質感」——elevation 透過 surface tint（與 primary 同色的半透明疊加）+ 柔和陰影一起傳達深度。

**密度**：可調。Material 提供 standard / dense 兩種密度節奏，後台類介面用 dense，消費型用 standard。

**氛圍**：清新、明確、有呼吸感。色塊飽滿但不刺眼；動效有「彈性」但不浮誇；圓角不會極端到失重，也不會直角到冷硬。

---

## 2. Color Palette & Roles

Material 3 的色彩系統是 **role-based**——你不直接指定顏色，而是指定角色（primary / surface / outline...），系統依 baseline scheme 或 dynamic color 解析成實際 hex。

### 2.1 Baseline 配色（Light scheme，M3 預設）

| Token Name | Hex | Role |
|------------|-----|------|
| `--md-primary` | `#6750A4 → oklch(0.49 0.16 304)` | 主色，FAB / 主要按鈕 / 強調圖示 |
| `--md-on-primary` | `#FFFFFF` | 主色之上的文字 / 圖示 |
| `--md-primary-container` | `#EADDFF` | 次強調容器（chip 選中、淡色按鈕） |
| `--md-on-primary-container` | `#21005D` | primary-container 之上的文字 |
| `--md-secondary` | `#625B71` | 次色，較中性，多用於互補強調 |
| `--md-on-secondary` | `#FFFFFF` | 次色之上的文字 |
| `--md-secondary-container` | `#E8DEF8` | 次容器 |
| `--md-on-secondary-container` | `#1D192B` | 次容器之上的文字 |
| `--md-tertiary` | `#7D5260` | 第三色（補色 / accent for accent） |
| `--md-on-tertiary` | `#FFFFFF` | 第三色之上的文字 |
| `--md-tertiary-container` | `#FFD8E4` | 第三容器 |
| `--md-on-tertiary-container` | `#31111D` | 第三容器之上的文字 |
| `--md-error` | `#B3261E` | 錯誤狀態 |
| `--md-on-error` | `#FFFFFF` | 錯誤色之上的文字 |
| `--md-error-container` | `#F9DEDC` | 錯誤容器（淺紅警示底） |
| `--md-on-error-container` | `#410E0B` | 錯誤容器之上的文字 |
| `--md-background` | `#FEF7FF` | 頁面背景（暖白，極淡的 primary tint） |
| `--md-on-background` | `#1D1B20` | 背景上的主要文字 |
| `--md-surface` | `#FEF7FF` | 卡片 / 對話框預設表面 |
| `--md-on-surface` | `#1D1B20` | 表面上的主要文字 |
| `--md-surface-variant` | `#E7E0EC` | 次表面（chip 背景、表單欄填色） |
| `--md-on-surface-variant` | `#49454F` | 次表面之上的文字 |
| `--md-outline` | `#79747E` | 邊框（文字框、分隔線） |
| `--md-outline-variant` | `#CAC4D0` | 弱邊框（次要分隔） |
| `--md-shadow` | `#000000` | 陰影基底色 |
| `--md-scrim` | `#000000` | Modal 背後遮罩 |
| `--md-surface-tint` | `#6750A4 → oklch(0.49 0.16 304)` | Elevation 表面色調疊加（= primary） |
| `--md-inverse-surface` | `#322F35` | 反相表面（snackbar 等） |
| `--md-inverse-on-surface` | `#F5EFF7` | 反相表面之上的文字 |
| `--md-inverse-primary` | `#D0BCFF` | 反相表面之上的 primary（連結色） |

### 2.2 Dark scheme（Material You 暗色配色）

| Token Name | Hex |
|------------|-----|
| `--md-primary` | `#D0BCFF` |
| `--md-on-primary` | `#381E72` |
| `--md-primary-container` | `#4F378B` |
| `--md-on-primary-container` | `#EADDFF` |
| `--md-secondary` | `#CCC2DC` |
| `--md-on-secondary` | `#332D41` |
| `--md-secondary-container` | `#4A4458` |
| `--md-on-secondary-container` | `#E8DEF8` |
| `--md-tertiary` | `#EFB8C8` |
| `--md-on-tertiary` | `#492532` |
| `--md-tertiary-container` | `#633B48` |
| `--md-on-tertiary-container` | `#FFD8E4` |
| `--md-error` | `#F2B8B5` |
| `--md-error-container` | `#8C1D18` |
| `--md-background` | `#141218` |
| `--md-on-background` | `#E6E0E9` |
| `--md-surface` | `#141218` |
| `--md-on-surface` | `#E6E0E9` |
| `--md-surface-variant` | `#49454F` |
| `--md-on-surface-variant` | `#CAC4D0` |
| `--md-outline` | `#938F99` |

### 2.3 用色原則

- **永遠用 role，不用 hex**：寫 `color: var(--md-on-surface)` 而不是 `color: #1D1B20`。Dark mode / dynamic color 切換時 token 會自動翻轉。
- **on-* 配對**：任何 surface 之上的文字必須用對應的 on-* token，這是無障礙合規的保證。
- **Primary 比例**：primary 是視覺重心，但不應 dominate。FAB / 主 CTA / 主要 icon 用 primary，大面積色塊優先用 surface-variant 或 primary-container（淡色容器版本）。
- **Surface tint**：M3 廢除 Material 2 的「白色 elevation overlay」，改用 surface-tint（與 primary 同色的低透明度疊加）。Level 1 → tint 5%，Level 5 → tint 14%。
- **不要用純黑**：陰影基底是 `#000000` 但實際渲染靠 rgba，UI 元素永遠走 surface 系列。

> **Footnote — oklch advisory**：表中 `→ oklch(...)` 為 advisory 等價值，僅供色彩感知比對與未來 Chromium-print migration 參考；現行 WeasyPrint print pipeline 仍以 hex 為唯一渲染來源，tokens.css 與 design-cores HTML 不得出現 `oklch()` 函數。

---

## 3. Typography Rules

**字型堆疊**：

```css
/* Roboto Flex 是 M3 預設字體（variable font，支援 wght/wdth/opsz 三軸） */
--md-font-brand:  "Google Sans", "Product Sans", "Roboto Flex", Roboto, system-ui, sans-serif;
--md-font-plain:  "Roboto Flex", Roboto, "Helvetica Neue", Arial, sans-serif;
--md-font-mono:   "Roboto Mono", "JetBrains Mono", "SF Mono", Consolas, monospace;
```

**中文堆疊**（Material 官方對 CJK 採 Noto Sans CJK）：

```css
--md-font-plain:  "Roboto Flex", Roboto, "Noto Sans TC", "Noto Sans CJK TC",
                  "PingFang TC", "Microsoft JhengHei", sans-serif;
```

**Type Scale**（M3 baseline 15 種，screen px / line-height px / weight / letter-spacing）：

| Role | Size | Line Height | Weight | Tracking |
|------|------|-------------|--------|----------|
| Display Large | 57px | 64px | 400 | -0.25px |
| Display Medium | 45px | 52px | 400 | 0 |
| Display Small | 36px | 44px | 400 | 0 |
| Headline Large | 32px | 40px | 400 | 0 |
| Headline Medium | 28px | 36px | 400 | 0 |
| Headline Small | 24px | 32px | 400 | 0 |
| Title Large | 22px | 28px | 400 | 0 |
| Title Medium | 16px | 24px | 500 | 0.15px |
| Title Small | 14px | 20px | 500 | 0.1px |
| Body Large | 16px | 24px | 400 | 0.5px |
| Body Medium | 14px | 20px | 400 | 0.25px |
| Body Small | 12px | 16px | 400 | 0.4px |
| Label Large | 14px | 20px | 500 | 0.1px |
| Label Medium | 12px | 16px | 500 | 0.5px |
| Label Small | 11px | 16px | 500 | 0.5px |

**用法**：
- **Display**：超大標題，hero / marketing 頁。
- **Headline**：頁面 / 區段標題。
- **Title**：卡片標題、對話框標題、列表標題。
- **Body**：正文段落、描述文字。
- **Label**：按鈕、tab、chip、表單 label。

**規則**：
- Sans-serif first：M3 沒有預設 serif 字族。需要 serif 時是專案決定，不在 baseline。
- Title / Label 用 weight 500 提示可互動或結構性區隔；Display / Headline / Body 用 weight 400。
- Letter-spacing 在小字級放大（Body Small +0.4px、Label Medium +0.5px）以提升閱讀性。
- 中英混排：CJK 字體放在 sans 堆疊尾段，英文字優先用 Roboto Flex。
- M3 Expressive update（2024+）新增 emphasized variants — 同一 role 的更粗版本（如 Title Large Emphasized = weight 500 而非 400），用於強調但 size 不變。

### Dropcap

長文段首字母採 dropcap 工藝；3-line drop 是印刷學甜蜜點（不是 2，也不是 4）。
class 前綴對齊 preset：`.google-dropcap`（採 `google-` 前綴，非 `gd-`）。

```css
.google-dropcap {
  float: left;
  font-size: 4.65em;      /* 4.65em = 3 × body line-height (1em × 1.55 × 3); renders as 3-line drop with body line-height 1.55 */
  line-height: 1;         /* 避免繼承 body line-height 導致高度爆炸 */
  font-weight: 500;       /* 對齊 M3 Title / Label emphasis weight */
  color: var(--accent);   /* M3 primary tonal accent */
  padding-right: 8px;     /* ≥ 4px 防字身擠壓 */
  padding-top: 2px;       /* 視覺對齊微調 */
}
```

**使用**：`<p class="google-body"><span class="google-dropcap">L</span>orem ipsum...</p>`

**Kami 可移植 invariant**：dropcap 字身禁用 `<small>` 或 italic style；用 `<span>` 而非 `<em>` / `<i>`。

---

## 4. Component Stylings

### 4.1 Elevation 系統

M3 elevation 透過 **surface-tint 疊加 + 柔和陰影** 雙軌傳達深度。

| Level | dp | Surface Tint Opacity | Shadow |
|-------|----|--------------------|---------|
| 0 | 0dp | 0% | none |
| 1 | 1dp | 5% | `0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15)` |
| 2 | 3dp | 8% | `0 1px 2px rgba(0,0,0,0.3), 0 2px 6px 2px rgba(0,0,0,0.15)` |
| 3 | 6dp | 11% | `0 4px 8px 3px rgba(0,0,0,0.15), 0 1px 3px rgba(0,0,0,0.3)` |
| 4 | 8dp | 12% | `0 6px 10px 4px rgba(0,0,0,0.15), 0 2px 3px rgba(0,0,0,0.3)` |
| 5 | 12dp | 14% | `0 8px 12px 6px rgba(0,0,0,0.15), 0 4px 4px rgba(0,0,0,0.3)` |

### 4.2 Shape Scale（圓角）

| Token | Radius |
|-------|--------|
| `--md-shape-none` | 0dp |
| `--md-shape-extra-small` | 4dp |
| `--md-shape-small` | 8dp |
| `--md-shape-medium` | 12dp |
| `--md-shape-large` | 16dp |
| `--md-shape-extra-large` | 28dp |
| `--md-shape-full` | 9999dp（藥丸 / 圓形） |

### 4.3 Button（五種正式變體）

- **Filled**：`background: var(--md-primary); color: var(--md-on-primary);` border-radius `var(--md-shape-full)`，padding `10px 24px`，label `var(--md-label-large)`。主 CTA 用這個。
- **Tonal (Filled Tonal)**：`background: var(--md-secondary-container); color: var(--md-on-secondary-container);` 同 radius / padding，比 filled 弱一階的強調。
- **Outlined**：`background: transparent; color: var(--md-primary); border: 1px solid var(--md-outline);` radius `full`。次要動作。
- **Text**：`background: transparent; color: var(--md-primary);` 無邊框，padding `10px 12px`。對話框取消鈕等。
- **Elevated**：`background: var(--md-surface); color: var(--md-primary);` shadow level 1，需要在繁忙背景上浮起時用。

**State Layer**（所有可互動元件）：
- Hovered：在元件之上疊一層 8% opacity 的 `currentColor`（或 primary）
- Focused：12% opacity
- Pressed：12% opacity + ripple 動效
- Dragged：16% opacity

### 4.4 Card

```css
background: var(--md-surface);
color: var(--md-on-surface);
border-radius: var(--md-shape-medium);   /* 12px */
padding: 16px;
box-shadow: var(--md-elevation-1);        /* elevated card */
/* OR for filled card */
background: var(--md-surface-variant);
box-shadow: none;
/* OR for outlined card */
background: var(--md-surface);
border: 1px solid var(--md-outline-variant);
box-shadow: none;
```

### 4.5 Text Field

- **Filled**（M3 預設）：`background: var(--md-surface-variant);` bottom border `1px solid var(--md-on-surface-variant)`；focus 時 bottom border 變 2px primary，label float 到上方。
- **Outlined**：`border: 1px solid var(--md-outline);` border-radius `extra-small (4px)`；focus 時 border 變 2px primary，label 切入 outline。

### 4.6 FAB（Floating Action Button）

```css
background: var(--md-primary-container);
color: var(--md-on-primary-container);
border-radius: var(--md-shape-large);    /* 16px for standard FAB */
width: 56px; height: 56px;
box-shadow: var(--md-elevation-3);
```

Hover → elevation level 4。Sizes：Small (40dp) / Standard (56dp) / Large (96dp) / Extended (横向)。

### 4.7 Chip

```css
background: transparent;
border: 1px solid var(--md-outline);
color: var(--md-on-surface-variant);
border-radius: var(--md-shape-small);    /* 8px */
padding: 6px 12px;
font: var(--md-label-large);
```

Selected → `background: var(--md-secondary-container); color: var(--md-on-secondary-container); border: none;`

### 4.8 Navigation

- **Top App Bar**：`background: var(--md-surface);` height 64dp，title 用 Title Large；scroll 時切到 surface tint level 2。
- **Navigation Bar (bottom)**：mobile 主導航，3-5 個 destination。
- **Navigation Rail**：tablet / desktop 側導航，垂直版本。
- **Navigation Drawer**：modal 或 standard，desktop 大型導航。

---

## 5. Layout & Spacing

**間距單位**：4dp 基底（4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 dp）。

**Window Size Classes**（M3 響應式核心）：

| Class | Width | 對應裝置 | 導航模式 |
|-------|-------|---------|---------|
| Compact | < 600dp | 手機直立 | Navigation Bar |
| Medium | 600–839dp | 手機橫向 / 小平板 | Navigation Rail |
| Expanded | 840–1199dp | 平板 / 小筆電 | Navigation Rail + Detail |
| Large | 1200–1599dp | 桌機 | Navigation Drawer |
| Extra-Large | ≥ 1600dp | 大螢幕 | Drawer + Multi-pane |

**Margin**（內容區與視窗邊緣）：
- Compact：16dp
- Medium：24dp
- Expanded+：32dp

**Gutter**（欄與欄之間）：
- Compact：8dp
- Medium / Expanded：16dp
- Large+：24dp

**最大內容寬度**：閱讀內容 840dp，整版面 1440dp。

---

## 6. Iconography & Imagery

**Material Symbols**（M3 官方圖示）：
- 三種風格：**Outlined**（預設）/ **Rounded**（friendly）/ **Sharp**（geometric）
- Variable font，四軸：fill (0-1)、weight (100-700)、grade (-50 to +200)、optical size (20-48)
- 標準尺寸：20dp / 24dp（預設）/ 40dp / 48dp
- 顏色繼承 currentColor，特殊強調才指定 `var(--md-primary)`

**圖示用法**：
- Icon button 中：24dp icon + 8dp padding = 40dp tap target
- 在 navigation rail：`fill=0` 預設、`fill=1` 選中
- 不要混用三種風格，全站擇一

**圖片**：
- Photography 偏向自然光、真實場景，避免過度後製
- Hero 區可疊加 `primary-container` 漸層提升品牌感
- 圖片角落用 `--md-shape-medium`（12dp）統一

**Data Chart 色序**（M3 baseline）：
`--md-primary` → `--md-secondary` → `--md-tertiary` → `--md-primary-container` → `--md-secondary-container` → `--md-tertiary-container`

---

## 7. Motion & Animation

**Easing**（M3 命名）：

| Token | cubic-bezier | 用途 |
|-------|--------------|------|
| `--md-easing-emphasized` | `cubic-bezier(0.2, 0.0, 0, 1.0)` | 預設、多數場景 |
| `--md-easing-emphasized-decelerate` | `cubic-bezier(0.05, 0.7, 0.1, 1.0)` | 元素進場（如 dialog 開啟） |
| `--md-easing-emphasized-accelerate` | `cubic-bezier(0.3, 0.0, 0.8, 0.15)` | 元素離場（如 dialog 關閉） |
| `--md-easing-standard` | `cubic-bezier(0.2, 0.0, 0, 1.0)` | 同 emphasized，較舊 token |
| `--md-easing-linear` | `linear` | progress / 載入指示器 |

**Duration tokens**：

| Token | ms | 用途 |
|-------|-----|------|
| `--md-duration-short-1` | 50ms | 極小狀態變化（hover ripple 起點） |
| `--md-duration-short-2` | 100ms | Selection 切換 |
| `--md-duration-short-3` | 150ms | Icon toggle |
| `--md-duration-short-4` | 200ms | 小元件移動 |
| `--md-duration-medium-1` | 250ms | Chip / Button state |
| `--md-duration-medium-2` | 300ms | Card 展開 |
| `--md-duration-medium-3` | 350ms | Bottom sheet / Drawer |
| `--md-duration-medium-4` | 400ms | Top app bar transition |
| `--md-duration-long-1` | 450ms | Full screen transitions |
| `--md-duration-long-2` | 500ms | Same |
| `--md-duration-extra-long-1` | 700ms | Hero transition |

**動效規則**：
- Container Transform：元件間轉場優先用「容器變形」（Material 簽名動效），如 FAB → Dialog。
- 尊重 `prefers-reduced-motion`：動畫長度降至 0ms 或極短。
- 不用純粹裝飾性的循環動畫，progress 例外。

---

## 8. Do / Don't

**Do**：
- ✅ 使用 role token（`var(--md-primary)`）而非 hex
- ✅ 任何 surface 之上的文字配對 on-* token
- ✅ Elevation 用 surface-tint 疊加 + 柔和陰影雙軌
- ✅ Button 用 `--md-shape-full`（藥丸），text field outlined 用 `--md-shape-extra-small`
- ✅ 主導航依視窗尺寸切換（Bar / Rail / Drawer）
- ✅ State layer：hover 8% / focus 12% / pressed 12% / dragged 16%
- ✅ Material Symbols 全站擇一風格（outlined / rounded / sharp）
- ✅ Type scale 按語意挑（Display 用於 hero、Label 用於按鈕）
- ✅ 動效用 emphasized easing + 對應 duration token
- ✅ 響應式以 Window Size Class 設計，不只 media query 縮放

**Don't**：
- ❌ 不要直接寫 hex 值，永遠用 role token
- ❌ 不要在 light surface 上用 dark mode 配色（on-* 對應錯誤會 fail 對比度）
- ❌ 不要在 elevation 上只用陰影、忽略 surface-tint
- ❌ 不要混用三種 Material Symbols 風格
- ❌ Body 用 weight 500 / Label 用 weight 400（顛倒 = 視覺階層混亂）
- ❌ Tracking 不能憑感覺改，table 內每個 type role 都有預設值
- ❌ 不要把 primary 大面積鋪滿（CTA / FAB 用就好，大面積用 primary-container）
- ❌ 不要忽略 `prefers-reduced-motion`
- ❌ 不要用純黑陰影 `#000` 高 opacity，用 0.15 / 0.30 雙層

---

## 9. AI Prompt Guide

以下提示詞可在全新 AI 對話中重現本設計系統：

> Design a UI using Material 3 (Material You). Use role-based color tokens, not hex values: primary `#6750A4`, on-primary `#FFFFFF`, primary-container `#EADDFF`, secondary `#625B71`, tertiary `#7D5260`, surface `#FEF7FF`, on-surface `#1D1B20`, surface-variant `#E7E0EC`, outline `#79747E`. Typography uses Roboto Flex with the M3 baseline type scale (Display 57/45/36px, Headline 32/28/24px, Title 22/16/14px, Body 16/14/12px, Label 14/12/11px) — Title and Label use weight 500, others 400, with per-role letter-spacing (Body Medium +0.25px, Label Medium +0.5px). Elevation is conveyed with both a soft two-layer shadow AND a primary-tinted overlay on the surface (5% at level 1, scaling up to 14% at level 5). Shape scale: extra-small 4dp, small 8dp, medium 12dp (cards), large 16dp (FAB), extra-large 28dp, full 9999dp (buttons). Button styles: Filled (primary bg + on-primary text + full radius), Tonal (secondary-container bg), Outlined (1px outline border), Text (transparent), Elevated (surface + elevation 1). State layers add opacity overlays — hover 8%, focus 12%, pressed 12%, dragged 16%. Use Material Symbols for icons, picking one style (outlined / rounded / sharp) globally, 24dp default. Layout adapts via Window Size Classes (Compact <600dp → Navigation Bar, Medium 600-839 → Rail, Expanded 840-1199 → Rail+Detail, Large 1200+ → Drawer). Motion uses emphasized easing `cubic-bezier(0.2, 0, 0, 1)` with M3 duration tokens (short 50-200ms, medium 250-400ms, long 450-700ms). Light and dark schemes are symmetric — every token swaps. The aesthetic is expressive, accessible, dynamic — Material You principles applied throughout.

### (a) 焦點節點上限

每一頁、每一張投影片，焦點節點上限為 **1–2 個**：
- 主焦點（1 個必有）：以 `--md-primary: #6750A4` 染色——通常為 Display / Headline 標題、Filled button、或 FAB。
- 次焦點（0–1 個，可選）：以 `--md-primary-container: #EADDFF` 或 `--md-secondary: #625B71` 的 Tonal 角色承擔，不再加第三層強調。Material You 的色彩擴張性需要被克制以維持「focal hierarchy」。

### (b) accent hex 設計理據

主 accent `--md-primary: #6750A4`（M3 baseline purple，亦同 `--md-surface-tint`）拆解：

| Space | Coordinates | 設計意圖 |
|-------|-------------|----------|
| HEX | `#6750A4` | M3 baseline 規格；token role 為 `primary` / `surface-tint`，WeasyPrint 以此為準 |
| HSL | `H 256°, S 34%, L 48%` | 紫藍色相位 256°——M3 baseline 從 HCT (Hue-Chroma-Tone) 推導為 H 270°/C 36/T 40，sRGB 投影後得此 HSL；S 34% 低於純彩色避免螢幕灼眼；L 48% 對應 M3 tone 40，即「primary on light scheme」 |
| oklch（advisory） | `oklch(0.49 0.16 304)` | perceptual 等價；色相 304° 接近 M3 HCT 原始 270° + sRGB 投影偏移；C 0.16 反映 baseline palette 的中等彩度 |

選色理由：M3 baseline `#6750A4` 是 Google 提供的「無品牌（pre-branding）」起點色——在沒有 dynamic color 萃取（從 wallpaper / brand image 推導）時的安全預設。每個 surface tint 與 elevation overlay 都從這一個 hue 延伸，破壞 hue 一致性即破壞 Material You 的核心承諾。

### (c) 我不是什麼（anti-patterns / allowed contradictions）

對齊 Material You constraint（避免與品牌規格衝突）：

- no raw hex in components — 元件 layer 一律走 `var(--md-*)` token role，不可硬編碼 `#6750A4`；換 brand 時整個系統需可重綁
- no clashing brand accent — 若品牌色與 baseline `#6750A4` 衝突，必須執行 dynamic color extraction 重新生成整個 tonal palette，不可只覆蓋 `--md-primary`
- no third accent — `primary` + `secondary` + `tertiary` 三 role 已是上限；不得再加第四個彩色 token
- no asymmetric light/dark — 任何 light scheme 的 token 必須在 dark scheme 有對應 swap；單側設色即破壞 Material You 對稱性
- no elevation without tint overlay — Elevation 不可只用 shadow，必須同時疊 `--md-surface-tint` overlay（M3 specification 要求兩者並存）
- no italics for emphasis — M3 type scale 使用 weight 與 letter-spacing 區分階層，斜體不在規範內
- no rgba state layer — State layer 透明度透過 token opacity（hover 8% / focus 12% / pressed 12%）表達，不可硬編碼 rgba
