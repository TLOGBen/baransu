---
name: er
status: complete
example: inline
---

# ER / Data Model

**Best for**: database schema、API resource 關係、domain model、aggregate boundary、跨服務資料 ownership map。

## Layout conventions

- Layer 3 derived token：`entity-key` = `--brand-tint`（v1 ground truth `#EEF2F7`），`entity-attr` = `--parchment`（v1 ground truth `#faf9f5`）；皆預計算為 solid hex，不得出現 alpha-channel CSS 函式形式，參見 `references/design-token-resolver.md`。
- 每個 entity 為兩段式 box：**header** = type tag（`ENTITY`）+ entity 名（`--font-sans`），底色走 `entity-key`；**body** = field list（`--font-mono`，每行一個），底色走 `entity-attr`；PK 前綴 `#`，FK 前綴 `→`。
- Relationship 為 entity 之間的線，**兩端各標 cardinality**（`1` / `N` / `0..1` / `1..*`），`--font-mono` 8px，距 entity 邊 10–12px；可選的關係 label（"has"、"belongs to"）置於線中央。
- 相關 entity 群聚靠近，rearrange 直到大多數 relationship 為直線（不糾結）；`--brand` 只用在 aggregate root 或模型的中心 entity，一張圖一個。

## Anti-patterns

- 在數十個 FK 的模型上每條 FK 都畫 arrow。
  - *Why fails*：線數量會以 O(entities²) 暴增，視覺變 hairball；ER 圖的價值是讓人在 5 秒內看出 cluster 邊界，FK 太多時應改以 cluster 分組或拆 sub-diagram。
- 同一條 relationship 的兩端 cardinality 標注不一致（如一端 `1`、另一端忘記標）。
  - *Why fails*：cardinality 是 relationship 唯一回答的問題，缺一端等於宣告未定義；讀者會在「是 1:N 還是 N:M」之間反覆推敲，圖的決策力為零。
- 為了視覺整齊把 field 強制 padding 成等高 box。
  - *Why fails*：natural height 本就應 by content；padding 補白會讓 entity 大小錯位 imply 「這個 entity 比較重要」，但實際只是 field 數差異，誤導讀者建立錯誤心智模型。

## Examples

Inline example below — 3-entity ER（`User → Order[focal] → Item`，含 1-to-many cardinality）。完整 `<defs>` 三 chevron marker、兩層 paper-mask、1 個 `data-role="focal"` 節點、節點寬 2 檔白名單 `{128, 160}`、legend strip、所有 `x/y/width/height` 為 4 的倍數。Entity body 內的細條（field row）寬度走 sub-primitive，不計入 node-width 白名單。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="User-Order-Item entity relationship">
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

    <!-- ===== EDGES（先畫線；relationship 帶 cardinality） ===== -->
    <!-- User (1) → Order[focal] (N): external entry (link 色) -->
    <line x1="208" y1="232" x2="416" y2="232"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="220" y="224" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace">1</text>
    <text x="396" y="224" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace">N</text>
    <text x="312" y="220" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">places</text>

    <!-- Order[focal] (1) → Item (N): accent focal flow -->
    <line x1="576" y1="232" x2="784" y2="232"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="588" y="224" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace">1</text>
    <text x="764" y="224" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace">N</text>
    <text x="680" y="220" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">contains</text>

    <!-- Item → User (N..1): FK back-reference (muted internal) -->
    <path d="M 864 304 C 864 408, 144 408, 144 304"
          fill="none" stroke="#504e49" stroke-width="1.2"
          stroke-dasharray="4 3" marker-end="url(#arrow)"/>
    <text x="504" y="404" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">FK back-reference (owner_id)</text>

    <!-- ===== ENTITIES — 寬白名單 2 檔 {128, 160}；focal 用 160 ===== -->
    <!-- User entity (128) -->
    <rect x="80" y="160" width="128" height="144" rx="6" fill="#f5f4ed"/>
    <rect x="80" y="160" width="128" height="144" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <!-- header band -->
    <rect x="80" y="160" width="128" height="32" rx="6"
          fill="#EEF2F7" stroke="#504e49" stroke-width="1"/>
    <rect x="88" y="168" width="40" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="108" y="177" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ENTITY</text>
    <text x="144" y="184" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">User</text>
    <!-- field rows (sub-primitive) -->
    <text x="96" y="216" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"># id</text>
    <text x="96" y="236" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace">  email</text>
    <text x="96" y="256" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace">  name</text>
    <text x="96" y="284" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">aggregate</text>

    <!-- Order entity — FOCAL (160) -->
    <rect x="416" y="160" width="160" height="144" rx="6" fill="#f5f4ed"/>
    <rect data-role="focal"
          x="416" y="160" width="160" height="144" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <!-- header band -->
    <rect x="416" y="160" width="160" height="32" rx="6"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    <rect x="424" y="168" width="40" height="12" rx="2"
          fill="transparent" stroke="#1B365D" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="444" y="177" fill="#1B365D" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ROOT</text>
    <text x="496" y="184" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Order</text>
    <!-- field rows -->
    <text x="432" y="216" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"># id</text>
    <text x="432" y="236" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace">→ user_id</text>
    <text x="432" y="256" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace">  total</text>
    <text x="432" y="284" fill="#1B365D" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">aggregate root</text>

    <!-- Item entity (160) -->
    <rect x="784" y="160" width="160" height="144" rx="6" fill="#f5f4ed"/>
    <rect x="784" y="160" width="160" height="144" rx="6"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <!-- header band -->
    <rect x="784" y="160" width="160" height="32" rx="6"
          fill="#EEF2F7" stroke="#504e49" stroke-width="1"/>
    <rect x="792" y="168" width="40" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="812" y="177" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">ENTITY</text>
    <text x="864" y="184" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Item</text>
    <!-- field rows -->
    <text x="800" y="216" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace"># id</text>
    <text x="800" y="236" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace">→ order_id</text>
    <text x="800" y="256" fill="#141413" font-size="10"
          font-family="'Geist Mono', ui-monospace, monospace">  sku</text>
    <text x="800" y="284" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace">line item</text>

    <!-- ===== LEGEND STRIP ===== -->
    <line x1="60" y1="540" x2="940" y2="540"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="560" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>

    <rect x="140" y="552" width="16" height="12" rx="2"
          fill="#faf9f5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Entity</text>

    <rect x="240" y="552" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="260" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Aggregate root</text>

    <line x1="380" y1="556" x2="400" y2="556"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="408" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal 1-to-many</text>

    <line x1="540" y1="556" x2="560" y2="556"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="568" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">External entry</text>

    <line x1="700" y1="556" x2="720" y2="556"
          stroke="#504e49" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
    <text x="728" y="561" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">FK ref</text>

    <text x="820" y="561" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"># PK · → FK</text>
  </svg>
  <figcaption>圖：3-entity ER 模型（User 1—N Order[focal] 1—N Item），Order 為 aggregate root。</figcaption>
</figure>
```
