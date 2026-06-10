---
name: flowchart
status: complete
example: inline
---

# Flowchart

**Best for**: 決策邏輯（decision logic）、演算法步驟（algorithms）、面向使用者的分支流程（"Should I…?"）、onboarding routing、support-triage 分流樹。

## Layout conventions

- Shape 帶 type，**顏色不帶 type**：oval（`rx=20`）= start / end；rect（`rx=6`）= step / action；diamond = decision（≤3 個出口）；small filled `--ink` dot（`r=4`）= merge point（分支匯流點）。
- 主流方向 top→down 固定；從 diamond 出去時 Yes 走右、No 走下為慣例，但**每一條 outgoing arrow 都要 label**，不可省略。
- `--brand` 只用在 happy path **或**單一最關鍵 decision 二擇一，不可同時用在多個 decision；其餘節點走 `--ink` / `--color-muted` 描邊與 `--parchment` 底。
- 若兩條 arrow 必須交叉，在其中一條畫一個 small arc jump 標示穿越，避免讀者誤判為連線。

## Anti-patterns

- 用 fill color 區分 node type（例如所有 action 紅、所有 decision 藍）。
  - *Why fails*：Kami 只給三個語意色（`--brand` / `--brand-tint` / `--color-muted`），fill 拿來標 type 會跟 focal 語意衝突，且色盲讀者無法分辨；type 區分本就是 shape 的工作，shape 已做完的事不需顏色再做一次。
- Decision diamond 開出 4 個以上 exit。
  - *Why fails*：人眼在 diamond 上能快速處理的分支上限是 3；4 個以上會逼讀者把 diamond 當 dispatch table 讀，違背 flowchart 「視覺化判斷」的目的，應重構為 nested diamonds。
- 未 label 的 decision 分支。
  - *Why fails*：flowchart 的本質是「在這一步決定了什麼條件」，少了 label 就只剩拓樸結構，讀者必須回去看 prose 才能理解，圖等同失效。

## Examples

Inline example below — 2 decision diamond + 5 process / terminal node 的標準流程圖（Start → Validate → Decision₁ → Decision₂ → {Persist | Reject} → End）。Diamond 以 `<rect>` 旋轉 45° 表達（rect 寬高皆走 {128} 白名單，旋轉後視覺即菱形）。1 個 `data-role="focal"` 落在 Decision₁（主要分支判斷），所有 `x/y/width/height` 為 4 的倍數。

```html
<figure class="diagram">
  <svg viewBox="0 0 1000 880" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Onboarding routing flowchart">
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

    <!-- Paper-mask Layer 1（強制） -->
    <rect width="100%" height="100%" fill="#f5f4ed"/>
    <!-- Paper-mask Layer 2（dotted overlay，可選） -->
    <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

    <!-- ===== EDGES（先畫線） ===== -->
    <!-- Start → Validate -->
    <line x1="500" y1="128" x2="500" y2="160"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- Validate → D1（focal 主流） -->
    <line x1="500" y1="224" x2="500" y2="288"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <!-- D1 Yes（右）→ Format -->
    <line x1="592" y1="384" x2="688" y2="384"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="640" y="376" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.06em">YES</text>
    <!-- D1 No（下）→ D2 -->
    <line x1="500" y1="476" x2="500" y2="536"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="512" y="508" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.06em">NO</text>
    <!-- D2 Yes（右）→ Persist -->
    <line x1="592" y1="624" x2="688" y2="624"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="640" y="616" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.06em">YES</text>
    <!-- D2 No（左）→ Reject -->
    <line x1="408" y1="624" x2="372" y2="624"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="392" y="616" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.06em">NO</text>
    <!-- Format → End（從右側繞下並回中） -->
    <line x1="768" y1="416" x2="768" y2="752"
          stroke="#504e49" stroke-width="1.2"/>
    <line x1="768" y1="752" x2="580" y2="752"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <!-- Persist → End -->
    <line x1="768" y1="656" x2="768" y2="752"
          stroke="#504e49" stroke-width="1.2"/>
    <!-- Reject → End（從左側繞下） -->
    <line x1="304" y1="656" x2="304" y2="752"
          stroke="#504e49" stroke-width="1.2"/>
    <line x1="304" y1="752" x2="420" y2="752"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>

    <!-- ===== NODES — 寬白名單 2 檔 {128, 160} ===== -->
    <!-- Start（oval rx=20，w=160） -->
    <rect x="420" y="64" width="160" height="64" rx="20" fill="#f5f4ed"/>
    <rect x="420" y="64" width="160" height="64" rx="20"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="72" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="81" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">START</text>
    <text x="500" y="104" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">User signs up</text>

    <!-- Validate（process rect，w=160） -->
    <rect x="420" y="160" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="420" y="160" width="160" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="168" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="177" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STEP</text>
    <text x="500" y="200" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Validate input</text>
    <text x="500" y="216" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">schema check</text>

    <!-- D1 — FOCAL（rotated rect 128×128 表 diamond） -->
    <g transform="rotate(45 500 384)">
      <rect x="436" y="320" width="128" height="128" rx="6" fill="#f5f4ed"/>
      <rect data-role="focal"
            x="436" y="320" width="128" height="128" rx="6"
            fill="#EEF2F7" stroke="#1B365D" stroke-width="1.4"/>
    </g>
    <text x="500" y="380" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Email valid?</text>
    <text x="500" y="396" fill="#1B365D" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">DECISION</text>

    <!-- Format（process rect，w=160） -->
    <rect x="688" y="352" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="688" y="352" width="160" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="696" y="360" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="710" y="369" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STEP</text>
    <text x="768" y="392" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Format normalize</text>

    <!-- D2（rotated rect 128×128 表 diamond，非 focal） -->
    <g transform="rotate(45 500 624)">
      <rect x="436" y="560" width="128" height="128" rx="6" fill="#f5f4ed"/>
      <rect x="436" y="560" width="128" height="128" rx="6"
            fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    </g>
    <text x="500" y="620" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">User exists?</text>
    <text x="500" y="636" fill="#504e49" font-size="9"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle">DECISION</text>

    <!-- Reject（process rect，w=128） -->
    <rect x="244" y="592" width="128" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="244" y="592" width="128" height="64" rx="6"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="252" y="600" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="266" y="609" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STEP</text>
    <text x="308" y="632" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Show conflict</text>

    <!-- Persist（process rect，w=160） -->
    <rect x="688" y="592" width="160" height="64" rx="6" fill="#f5f4ed"/>
    <rect x="688" y="592" width="160" height="64" rx="6"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <rect x="696" y="600" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="710" y="609" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">STEP</text>
    <text x="768" y="632" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Persist user</text>

    <!-- End（oval rx=20，w=160） -->
    <rect x="420" y="720" width="160" height="64" rx="20" fill="#f5f4ed"/>
    <rect x="420" y="720" width="160" height="64" rx="20"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <rect x="428" y="728" width="28" height="12" rx="2"
          fill="transparent" stroke="#141413" stroke-opacity="0.40" stroke-width="0.8"/>
    <text x="442" y="737" fill="#141413" font-size="7"
          font-family="'Geist Mono', ui-monospace, monospace"
          text-anchor="middle" letter-spacing="0.08em">END</text>
    <text x="500" y="760" fill="#141413" font-size="12" font-weight="600"
          font-family="'Geist', system-ui, sans-serif" text-anchor="middle">Send welcome email</text>

    <!-- ===== LEGEND STRIP（viewBox 高度 ≥ 400，必選） ===== -->
    <line x1="60" y1="820" x2="940" y2="820"
          stroke="#141413" stroke-opacity="0.10" stroke-width="0.8"/>
    <text x="60" y="840" fill="#504e49" font-size="8"
          font-family="'Geist Mono', ui-monospace, monospace"
          letter-spacing="0.14em">LEGEND</text>
    <rect x="140" y="832" width="16" height="12" rx="20"
          fill="#ebeae5" stroke="#504e49" stroke-width="1"/>
    <text x="160" y="841" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Terminal (oval)</text>
    <rect x="280" y="832" width="16" height="12" rx="2"
          fill="#f1f0eb" stroke="#504e49" stroke-width="1"/>
    <text x="300" y="841" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Process (rect)</text>
    <rect x="420" y="832" width="16" height="12" rx="2"
          fill="#EEF2F7" stroke="#1B365D" stroke-width="1.2"/>
    <text x="440" y="841" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal decision</text>
    <line x1="568" y1="836" x2="588" y2="836"
          stroke="#504e49" stroke-width="1.2" marker-end="url(#arrow)"/>
    <text x="596" y="841" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Generic</text>
    <line x1="688" y1="836" x2="708" y2="836"
          stroke="#1B365D" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
    <text x="716" y="841" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">Focal flow</text>
    <line x1="820" y1="836" x2="840" y2="836"
          stroke="#2D5A8A" stroke-width="1.2" marker-end="url(#arrow-link)"/>
    <text x="848" y="841" fill="#504e49" font-size="9"
          font-family="'Geist', system-ui, sans-serif">External</text>
  </svg>
  <figcaption>圖：Onboarding routing flowchart（2 decision diamond + 5 process/terminal node；Decision₁ 為 focal）。</figcaption>
</figure>
```
