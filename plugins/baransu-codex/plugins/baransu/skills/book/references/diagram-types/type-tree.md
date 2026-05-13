---
name: tree
status: complete
example: inline
---

# Tree / Hierarchy

**Best for**: org chart、dependency tree、taxonomy、file tree、decision breakdown、skill tree。

## Layout conventions

- Root 置頂、children 向下扇開（或 root 在左、children 向右）；root 不能有兩個。
- Node 為 small labeled rectangle（`rx=6`），name 用 `--font-sans` 12px 600，可選 sublabel 用 `--font-mono` 9px；node 寬度 120–180px，高度 40–52px，整張圖只用 2 種寬度。
- **Connector 一律 orthogonal（elbow）不畫對角線**：parent 下一條 short vertical → horizontal bus 連接 sibling → 每個 child 上方 short vertical 入頂邊；stroke 走 `--color-muted` 1px；connector 必須先畫，node 後畫（z-order）。
- 最大深度 4（root + 3 tier）、每層最大寬度 5；`--brand` 只能上在**單一 node**（root 或關鍵 leaf，二擇一，不可兩者皆有）。

## Anti-patterns

- 在單張圖畫 5 層以上深度。
  - *Why fails*：tree 越深 leaf 字越小、垂直空間越擠，5 層後讀者無法掃讀整體結構；應水平拆分為 sub-tree 或改用 nested containment 重新表達。
- Node 寬度自由發揮、每個都不一樣。
  - *Why fails*：tree 結構本應靠拓撲傳遞 hierarchy，寬度變化會被讀者誤讀為「這個 node 比較重要」；統一 2 種寬度可讓視覺節律穩定，讓讀者聚焦在連線結構而非 box 尺寸。
- 跳級連線（parent 直接連到 grandchild，中間 node 不畫）。
  - *Why fails*：tree 的語意是「parent → child」單階關係，跳級線等於宣告中介層級不存在，但實際 tree 結構仍有；視覺上讀者會誤判 depth，導致對整體 hierarchy 的錯估。

## Examples

Inline example below — 3-level hierarchy（1 root[focal] → 3 child → 6 leaf，2 leaf per child）。完整 `<defs>` 三 chevron marker、兩層 paper-mask、1 個 `data-role="focal"` 節點（root）、節點寬 2 檔白名單 `{128, 144}`、orthogonal elbow connector、legend strip、所有 `x/y/width/height` 為 4 的倍數。複製此 `<figure class="diagram">` block 後改節點即可重用。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="3-level taxonomy tree">
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

    <!-- ===== CONNECTORS (orthogonal elbow, drawn before nodes) ===== -->
    <!-- Root focal stem (down to bus) -->
    <line x1="500" y1="160" x2="500" y2="220"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- Horizontal bus across 3 children -->
    <line x1="232" y1="220" x2="768" y2="220"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.50"/>
    <!-- Child 1 stem down -->
    <line x1="232" y1="220" x2="232" y2="260"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- Child 2 stem down -->
    <line x1="500" y1="220" x2="500" y2="260"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- Child 3 stem down -->
    <line x1="768" y1="220" x2="768" y2="260"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- Child 1 leaf bus + 2 leaf stems -->
    <line x1="168" y1="368" x2="296" y2="368"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.50"/>
    <line x1="500" y1="324" x2="500" y2="324"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.50"/>
    <line x1="168" y1="368" x2="168" y2="408"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <line x1="296" y1="368" x2="296" y2="408"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- Child 2 leaf bus + 2 leaf stems -->
    <line x1="436" y1="368" x2="564" y2="368"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.50"/>
    <line x1="500" y1="324" x2="500" y2="368"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.50"/>
    <line x1="436" y1="368" x2="436" y2="408"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <line x1="564" y1="368" x2="564" y2="408"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- Child 3 leaf bus + 2 leaf stems -->
    <line x1="704" y1="368" x2="832" y2="368"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.50"/>
    <line x1="768" y1="324" x2="768" y2="368"
          stroke="#504e49" stroke-width="1" stroke-opacity="0.50"/>
    <line x1="704" y1="368" x2="704" y2="408"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <line x1="832" y1="368" x2="832" y2="408"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== NODES — 寬白名單 2 檔 {128, 144}；focal 用 144 ===== -->
    <!-- Tier 1：Root — FOCAL（144） -->
    <rect x="428" y="96" width="144" height="64" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="428" y="96" width="144" height="64" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="436" y="104" width="28" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="450" y="113" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ROOT</text>
    <text x="500" y="136" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Products</text>
    <text x="500" y="152" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">catalog root</text>

    <!-- Tier 2：Child 1（128） -->
    <rect x="168" y="260" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="168" y="260" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="176" y="268" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="190" y="277" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CAT</text>
    <text x="232" y="300" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Hardware</text>
    <text x="232" y="316" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">tangible</text>

    <!-- Tier 2：Child 2（128） -->
    <rect x="436" y="260" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="436" y="260" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="444" y="268" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="458" y="277" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CAT</text>
    <text x="500" y="300" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Software</text>
    <text x="500" y="316" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">licensed</text>

    <!-- Tier 2：Child 3（128） -->
    <rect x="704" y="260" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="704" y="260" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="712" y="268" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="726" y="277" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">CAT</text>
    <text x="768" y="300" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Services</text>
    <text x="768" y="316" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">recurring</text>

    <!-- Tier 3：6 leaves（128 each） -->
    <!-- Leaf 1.1 -->
    <rect x="104" y="408" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="104" y="408" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="112" y="416" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="126" y="425" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SKU</text>
    <text x="168" y="448" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Laptops</text>
    <text x="168" y="464" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">42 SKUs</text>

    <!-- Leaf 1.2 -->
    <rect x="232" y="408" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="232" y="408" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="240" y="416" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="254" y="425" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SKU</text>
    <text x="296" y="448" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Monitors</text>
    <text x="296" y="464" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">18 SKUs</text>

    <!-- Leaf 2.1 -->
    <rect x="372" y="408" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="372" y="408" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="380" y="416" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="394" y="425" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SKU</text>
    <text x="436" y="448" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">CRM</text>
    <text x="436" y="464" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">8 seats</text>

    <!-- Leaf 2.2 -->
    <rect x="500" y="408" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="500" y="408" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="508" y="416" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="522" y="425" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SKU</text>
    <text x="564" y="448" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">ERP</text>
    <text x="564" y="464" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">enterprise</text>

    <!-- Leaf 3.1 -->
    <rect x="640" y="408" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="640" y="408" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="648" y="416" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="662" y="425" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SVC</text>
    <text x="704" y="448" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Support</text>
    <text x="704" y="464" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">24×7</text>

    <!-- Leaf 3.2 -->
    <rect x="768" y="408" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="768" y="408" width="128" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="776" y="416" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="790" y="425" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">SVC</text>
    <text x="832" y="448" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Training</text>
    <text x="832" y="464" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">workshops</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Tree node</text>

    <rect x="280" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="300" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Root (focal)</text>

    <line x1="420" y1="556" x2="440" y2="556"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="448" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Parent→child</text>

    <line x1="560" y1="556" x2="580" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal stem</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Cross-tree link</text>
  </svg>
  <figcaption>圖：3-level taxonomy tree（Products[focal] → Hardware / Software / Services → 6 leaf SKU 群）。</figcaption>
</figure>
```
