---
name: quadrant
status: complete
example: inline
---

# Quadrant

**Best for**: 優先級排序（Impact × Effort）、定位圖（Reach × Frequency）、portfolio map、2×2 decision frame、scenario planning。

## Layout conventions

- 2×2 grid，axis line 為 1px `--ink` cross 穿過中心；axis arrow tip 收在 viewBox 邊內側 ~60–80px，留呼吸空間給 label。
- **Axis label Jobs-minimal**：每個 arrow tip 一個 **單字**，不帶 `↑` / `→` 等 glyph、不帶 `(HIGH/LOW)` 括號修飾；`--font-mono` 9px regular weight、tracked `0.18em`、uppercase；側 flanking arrow tip，不可坐在 axis line 上。
- Item 為 small labeled dot（`r=4`），分布在四象限內；label 距 dot 8–10px，**不可跨 axis line**；item 數量上限 ~12，超過則 cluster 或拆圖。
- `--brand` 只用在「do first」的單一 item（通常落在右上象限），不可上在多個 item，也不可填色整個象限格。

## Anti-patterns

- 四個象限分別填四種不同色塊。
  - *Why fails*：quadrant 的資訊承載靠「位置 + label」，色塊只是噪音；多色填底會與單一 `--brand` focal 競爭，且色盲讀者無法分辨象限差異，違反 Kami 三語意色限制。
- Item 落在 axis line 上（象限歸屬模糊）。
  - *Why fails*：axis 把平面切成四區的前提是 item 確切在某一區內；落在線上等於宣告「兩個象限都成立」，破壞 2×2 frame 的決策力，讀者無法回答「這個 item 屬於哪一類」。
- 缺 axis name 或 label 上標 `↑ HIGH IMPACT` 之類的多餘修飾。
  - *Why fails*：缺 name 時讀者不知 x/y 各代表什麼維度，圖等同沒有座標系；額外的 `↑` glyph 與 `HIGH / LOW` 括號則重複了 arrow 本身已表達的方向資訊，視覺上累贅且違反 Jobs-minimal 原則。

## Examples

Inline example below — 2×2 Impact × Effort 優先級矩陣，含 4 個象限 label、6 個 data dot、focal = top-left 「Quick Wins」象限。完整 `<defs>` 三 chevron marker、兩層 paper-mask、單一焦點 callout rect 寬白名單 `{128}`（單一檔，符合 ≤ 2 檔規則）、legend strip 與所有 `x/y/width/height/cx/cy` 為 4 的倍數。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Impact by Effort prioritization quadrant">
    <defs>
      <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="0.9" fill="#E3E2DC"/>
      </pattern>
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

    <!-- Paper-mask layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask layer 2（可選 dotted overlay） -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== AXIS CROSS（1px hairline） ===== -->
    <!-- Y axis (vertical) — with up-tip arrow（accent，落焦點維度；marker-end 落在 y=80 對齊 IMPACT 標籤） -->
    <line x1="500" y1="480" x2="500" y2="80"
          stroke="#141413" stroke-width="1"
          marker-end="url(#arrow-accent)"/>
    <!-- X axis (horizontal) — with right-tip arrow（accent） -->
    <line x1="80" y1="280" x2="920" y2="280"
          stroke="#141413" stroke-width="1"
          marker-end="url(#arrow-accent)"/>

    <!-- ===== AXIS LABELS（Jobs-minimal：單字、無 glyph、無括號） ===== -->
    <!-- Y top tip：IMPACT（flanking arrow tip，不坐軸線上） -->
    <text x="476" y="72" fill="#141413" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="end" letter-spacing="0.18em">IMPACT</text>
    <!-- X right tip：EFFORT -->
    <text x="928" y="276" fill="#141413" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.18em">EFFORT</text>

    <!-- ===== QUADRANT LABELS ===== -->
    <!-- Top-right: BIG BETS（高 impact、高 effort） -->
    <text x="720" y="120" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">BIG BETS</text>
    <!-- Bottom-left: FILL-INS（低 impact、低 effort） -->
    <text x="180" y="448" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">FILL-INS</text>
    <!-- Bottom-right: MONEY PIT（低 impact、高 effort） -->
    <text x="708" y="448" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">MONEY PIT</text>

    <!-- Top-left: QUICK WINS — FOCAL callout box (128 wide) -->
    <rect x="120" y="104" width="128" height="32" rx="4" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="120" y="104" width="128" height="32" rx="4"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <text x="184" y="124" fill="#1B365D" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.14em">QUICK WINS</text>

    <!-- ===== DATA POINTS（6 dots，r=4） ===== -->
    <!-- A: Caching — Quick Wins quadrant -->
    <circle cx="232" cy="200" r="4" fill="#1B365D"/>
    <text x="244" y="204" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Caching</text>

    <!-- B: Auth fix — Quick Wins quadrant -->
    <circle cx="320" cy="240" r="4" fill="#1B365D"/>
    <text x="332" y="244" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Auth fix</text>

    <!-- C: Redesign — Big Bets quadrant -->
    <circle cx="720" cy="160" r="4" fill="#141413"/>
    <text x="732" y="164" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Redesign</text>

    <!-- D: ML pipeline — Big Bets quadrant -->
    <circle cx="800" cy="200" r="4" fill="#141413"/>
    <text x="812" y="204" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">ML pipeline</text>

    <!-- E: Linting — Fill-ins quadrant -->
    <circle cx="240" cy="400" r="4" fill="#141413"/>
    <text x="252" y="404" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Linting</text>

    <!-- F: Legacy migration — Money Pit quadrant -->
    <circle cx="760" cy="400" r="4" fill="#141413"/>
    <text x="772" y="404" fill="#141413" font-size="10"
          font-family="'Geist', system-ui, sans-serif">Legacy migration</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <circle cx="148" cy="556" r="4" fill="#141413"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Item</text>

    <circle cx="220" cy="556" r="4" fill="#1B365D"/>
    <text x="232" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal item</text>

    <rect x="320" y="548" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="340" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal quadrant</text>

    <line x1="460" y1="556" x2="480" y2="556"
          stroke="#141413" stroke-width="1" marker-end="url(#arrow-accent)"/>
    <text x="488" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Axis direction</text>

    <line x1="612" y1="556" x2="632" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="640" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Internal flow</text>

    <line x1="752" y1="556" x2="772" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="780" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">External link</text>
  </svg>
  <figcaption>圖：2×2 Impact × Effort 矩陣，6 個 data point；Quick Wins 為 focal 象限。</figcaption>
</figure>
```
