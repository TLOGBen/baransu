# Design System: 紙 (Kami)

## 1. Visual Theme & Atmosphere

**哲學**：溫潤羊皮紙感。介面如一張好紙——有重量、有肌理、讓文字安靜地躺在上面。

核心信念（Kami 十不變量）：
- 背景不用純白，用暖調羊皮紙色，讓眼睛休息
- 主色是墨藍（ink-blue），如硯台的沉靜
- 字型層次靠襯線建立：serif 承擔閱讀主力，hierarchy 靠字重與大小而非色彩
- 陰影要柔，如紙張微翹的自然光影；禁用硬邊陰影
- 不用 rgba 標記顏色，用具名 token 以確保一致性
- 暖調限定：色票不進入冷灰區域
- warm parchment canvas, ink-blue accent, serif carries hierarchy, avoid cool grays and hard shadows

**密度**：適中。留白是設計元素，不是空間浪費。段落間距寬鬆，讓閱讀有呼吸感。

**氛圍**：書房、工藝、手感印刷品。不是高科技冷峻，是紙墨溫度。

---

## 2. Color Palette & Roles

| Token Name | Hex | Role |
|------------|-----|------|
| `--parchment` | `#f5f4ed` | 主背景（Primary background） |
| `--ivory` | `#faf9f5` | 卡片、面板背景（Card / panel surface） |
| `--brand` | `#1B365D` | 主色 / Accent（Ink-blue，品牌色） |
| `--near-black` | `#141413` | 主要文字（Primary text） |
| `--dark-warm` | `#3d3d3a` | 次要文字（Secondary text） |
| `--olive` | `#504e49` | 輔助文字、icon（Tertiary / muted） |
| `--stone` | `#6b6a64` | 佔位符、停用狀態（Placeholder / disabled） |
| `--line` | `#d8d6cf` | 分隔線、邊框（Divider / border） |
| `--hover` | `#e8e6de` | Hover 背景（Interactive hover state） |
| `--brand-light` | `#2a4f8a` | 主色亮版（Link / active state） |

**用色原則**：
- 背景層次：`--parchment` → `--ivory`（由深至淺，卡片浮在底色上）
- 文字層次：`--near-black` → `--dark-warm` → `--olive` → `--stone`
- 互動狀態唯一主色：`--brand`；hover 加亮至 `--brand-light`
- 禁用純白 `#ffffff`；禁用純黑 `#000000`

---

## 3. Typography Rules

**英文字型堆疊**（按優先順序）：
```
Charter, Georgia, 'Palatino Linotype', Palatino, serif
```

**中文字型堆疊**（按優先順序）：
```
'TsangerJinKai02', 'Noto Serif TC', 'Source Han Serif TC', 'AR PL UMing TW', serif
```

**完整堆疊組合**：
```css
font-family: 'TsangerJinKai02', 'Noto Serif TC', Charter, Georgia, 'Palatino Linotype', serif;
```

**層次規則**：

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| H1 | 2rem | 700 | 1.2 |
| H2 | 1.5rem | 600 | 1.3 |
| H3 | 1.25rem | 600 | 1.35 |
| Body | 1rem | 400 | 1.75 |
| Caption / Label | 0.875rem | 400 | 1.5 |
| Code | 0.9rem (monospace) | 400 | 1.6 |

**字型規則**：
- 標題不用 all-caps，保留中文字的自然重量感
- 行高偏寬（body 1.75），給文字足夠呼吸
- 中英文混排時，中文字型優先，英文 fallback 到 Charter/Georgia

---

## 4. Component Stylings

**Button（按鈕）**：
- Primary：`--brand` 填色，`--ivory` 文字，border-radius `6px`，padding `10px 20px`
- Secondary：無填色，`--brand` 邊框 1px，`--brand` 文字
- Hover：Primary 亮化至 `--brand-light`；Secondary 背景填 `--hover`
- Disabled：整體透明度降至 40%，cursor not-allowed
- 無硬陰影；只使用柔化陰影：`box-shadow: 0 1px 3px rgba(27,54,93,0.15)`

**Card（卡片）**：
- 背景：`--ivory`
- 邊框：1px solid `--line`
- border-radius：`8px`
- 陰影：`box-shadow: 0 2px 8px rgba(20,20,19,0.06)`（柔化，無硬邊）
- Hover：陰影加深至 `rgba(20,20,19,0.12)`，輕微上浮 `translateY(-1px)`

**Input（輸入框）**：
- 邊框：1px solid `--line`，focus 時換成 `--brand`，border-radius `6px`
- 背景：`--ivory`
- 佔位符：`--stone` 色
- 無填色背景切換；只靠邊框色傳達狀態

**Tag / Badge**：
- 背景：`--hover`，`--olive` 文字，border-radius `4px`，padding `2px 8px`
- Active tag：`--brand` 背景，`--ivory` 文字

---

## 5. Layout & Spacing

**間距單位**：4px 基底（spacing scale: 4, 8, 12, 16, 24, 32, 48, 64）

**網格**：12 欄，column gutter 24px，page margin 48px（桌機）/ 16px（手機）

**留白哲學**：
- 內容區塊間距至少 32px，不要讓頁面顯得緊繃
- 標題與下方內容間距：16px；與上方區塊間距：48px
- 卡片內 padding：24px

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

---

## 7. Motion & Animation

**過渡時間**：
- Micro-interaction（hover、focus）：150ms
- 狀態切換（顯示/隱藏、展開/收折）：250ms
- 頁面層級過渡：350ms

**Easing 曲線**：
- 標準：`ease-out`（cubic-bezier(0.0, 0.0, 0.2, 1.0)）
- 出現：`ease-out`；消失：`ease-in`
- Spring 感（彈性展開）：`cubic-bezier(0.34, 1.56, 0.64, 1)`

**動畫限制**：
- 不使用純粹裝飾性的循環動畫（如旋轉 logo）
- 尊重 `prefers-reduced-motion`：所有動畫在此媒體查詢下降至 0ms
- 避免大範圍平移；優先使用 opacity + scale 的組合

---

## 8. Do / Don't

**Do**：
- ✅ 使用暖調羊皮紙色（`#f5f4ed`）作為主背景
- ✅ 墨藍（`#1B365D`）作為唯一強調色與主色
- ✅ 採用 Charter / TsangerJinKai02 的襯線字型堆疊
- ✅ 柔化陰影（`box-shadow: 0 2px 8px rgba(...)`）
- ✅ 保持充足的行高（body ≥ 1.75）和段落間距
- ✅ 用具名色彩 token，不直接寫 hex 在元件樣式
- ✅ 卡片用 `--ivory` 與 1px `--line` 邊框，輕量浮起

**Don't**：
- ❌ 禁用純白背景 `#ffffff`
- ❌ 禁用冷灰色調（cool grays、藍調 neutral）
- ❌ 禁用硬邊陰影（box-shadow 無 blur radius）
- ❌ 禁在色票中直接使用 rgba(...)，應轉為具名 token
- ❌ 不使用純無襯線字型做全頁排版——serif 必須承擔至少一個層級
- ❌ 不使用高飽和度撞色搭配（紅+綠、橙+藍等）
- ❌ 不在介面中使用裝飾性循環動畫

---

## 9. AI Prompt Guide

以下提示詞可在全新 AI 對話中重現本設計系統的視覺語言：

> Design a UI using the Kami paper design system. Background: warm parchment `#f5f4ed`; card surfaces: `#faf9f5`. Primary accent: ink-blue `#1B365D`. Text hierarchy: near-black `#141413` → warm dark `#3d3d3a` → olive `#504e49`. Typography: Charter/Georgia for English, TsangerJinKai02/Noto Serif TC for Chinese — serif throughout. Components use soft shadows only (`box-shadow: 0 2px 8px rgba(20,20,19,0.08)`), 6–8px border-radius, `#d8d6cf` borders. No pure white, no cool grays, no hard shadows, no rgba color definitions. Motion: 150–250ms ease-out, respect prefers-reduced-motion. The aesthetic is warm printed paper — ink on parchment, craft over chrome.
