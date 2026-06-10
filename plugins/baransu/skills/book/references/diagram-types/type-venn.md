---
name: venn
status: complete
example: inline
---

# Venn / Set Overlap

**Best for**: 概念 / 領域交集、跨類別的共同屬性、「A 與 B 交會處」、ikigai-style frame（desirable × feasible × viable）、定位 sweet spot。

## Layout conventions

- **優先用 2 或 3 個圓**，避免 4+（不可讀，改用 matrix）；圓 stroke 1px hairline，每個 set 一個色（`--ink` / `--color-muted` / soft）。
- 圓 fill 走極低 opacity tint（`--ink @ 0.04` 或 `--color-muted @ 0.05`），overlap 區會自然疊出較深底；radii 在 set 大小相當時等大，差異有意義時按比例縮放，**不為美觀偽造等大**。
- **Set label 放在圓外**，絕不跨 stroke；`--font-sans` 12–14px 600 為 set name，可選 `--font-mono` 9px sublabel。
- **Intersection label** 放在 overlap 區內，`--font-sans` 12px 600 置中；overlap 過小時用 leader line 引出到 clear space；`--brand` 只上在**單一 focal 交集**（sweet spot），可選 brand stroke 或 clipPath-bounded brand tint fill；圓心與半徑皆可被 4 整除。

## Anti-patterns

- 區域未 label（讀者無法分辨哪個圓是哪個 set）。
  - *Why fails*：venn 的整個價值是「set 名 + 交集 label」帶來的語意；缺 label 只剩拓樸（兩個圓重疊）讀者必須回 prose 推敲哪個圓代表什麼，圖等同失效。
- 該重疊的圓未重疊（畫成相切或分離）。
  - *Why fails*：venn 的視覺承諾就是「重疊區存在 = 元素同時屬於多個 set」；不重疊等於宣告交集為空，與要表達的 sweet spot 語意直接矛盾。
- Set 大小明顯不同卻畫成等大圓。
  - *Why fails*：圓面積在讀者潛意識中對應 set 規模；等大圓會誤導對相對大小的判斷，例如把 1% 邊角案例與 80% 主流情境放在等大圓上，圖在量級上說謊。

## Examples

Inline example below — 3-circle 經典 Venn（ikigai-style：Desirable × Feasible × Viable），7 區齊備（3 single + 3 double + 1 triple intersection at 中心 [focal]）。`<circle>` 不入 rect 寬白名單；頂端 128-wide title callout `<rect>` 滿足白名單。完整 `<defs>` 三 chevron marker（皆於 legend 引用）、兩層 paper-mask、1 個 `data-role="focal"` 節點（triple-intersection callout）、所有 `cx/cy/r` 與 `x/y/width/height` 為 4 的倍數。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="3-circle Venn — ikigai sweet spot">
    <defs>
      <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
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

    <!-- ===== TITLE CALLOUT（128-wide rect 對齊白名單） ===== -->
    <rect x="436" y="56" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="56" width="128" height="32" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="60" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="69" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">VENN</text>
    <text x="500" y="78" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Ikigai frame</text>

    <!-- ===== 3 CIRCLES（hairline stroke + extremely low-opacity tint） ===== -->
    <!-- Set A：Desirable（top-left） -->
    <circle cx="420" cy="288" r="140"
            fill="#141413" fill-opacity="0.04"
            stroke="#504e49" stroke-width="1"/>
    <!-- Set B：Feasible（top-right） -->
    <circle cx="580" cy="288" r="140"
            fill="#141413" fill-opacity="0.04"
            stroke="#504e49" stroke-width="1"/>
    <!-- Set C：Viable（bottom） -->
    <circle cx="500" cy="400" r="140"
            fill="#141413" fill-opacity="0.04"
            stroke="#504e49" stroke-width="1"/>

    <!-- ===== SET LABELS（位於圓外，絕不跨 stroke） ===== -->
    <text x="280" y="184" fill="#141413" font-size="13" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Desirable</text>
    <text x="280" y="200" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">users want it</text>

    <text x="720" y="184" fill="#141413" font-size="13" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Feasible</text>
    <text x="720" y="200" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">we can build it</text>

    <text x="500" y="568" fill="#141413" font-size="13" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Viable</text>
    <text x="500" y="584" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">business sustains it</text>

    <!-- ===== PAIRWISE INTERSECTION LABELS（3 double regions） ===== -->
    <!-- A ∩ B（top） -->
    <text x="500" y="232" fill="#141413" font-size="11" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Mission</text>
    <text x="500" y="248" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">A ∩ B</text>

    <!-- A ∩ C（left） -->
    <text x="412" y="372" fill="#141413" font-size="11" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Passion</text>
    <text x="412" y="388" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">A ∩ C</text>

    <!-- B ∩ C（right） -->
    <text x="592" y="372" fill="#141413" font-size="11" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Vocation</text>
    <text x="592" y="388" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">B ∩ C</text>

    <!-- ===== TRIPLE INTERSECTION — FOCAL via data-role on backdrop rect ===== -->
    <!-- Focal node 為一個小型 rect callout（width=128 仍於白名單），停在 triple 中心 -->
    <rect x="436" y="332" width="128" height="32" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="436" y="332" width="128" height="32" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="444" y="336" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="345" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">FIT</text>
    <text x="500" y="356" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Ikigai</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#141413" fill-opacity="0.04"
          stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Set circle</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal sweet spot</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Leader line</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal callout</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-frame ref</text>
  </svg>
  <figcaption>圖：3-circle Venn — ikigai frame（Desirable × Feasible × Viable），triple-intersection [focal] 為 Ikigai sweet spot。</figcaption>
</figure>
```
