# slide-checklist.md

> Lint rules for `/design` slide + long-form output. Each entry uses a three-column structure: **現象 → 根因 → 做法**, with a `source:` metadata line. Audience: `check.py` lint source, slide-core authors, and preset reviewers.

## P0 sub-prefix legend

P0 entries 依「強制範圍」分三類前綴。`check.py` / sanity 腳本依前綴對應觸發條件：

- **P0-S-\*** — Swiss-locked invariants：僅在 `swiss` preset 下強制（kami / google 模式略過）。例：禁斜體、oklch 不可在 attribute。
- **P0-A-\*** — All-preset universal：kami / swiss / google-design 三 preset 皆強制。例：focal cap 2 / chevron marker / 4 倍數座標。
- **P0-B-\*** — Baransu plugin self-discipline：針對 baransu 本身發版紀律（plugin.json / SKILL.md / CLAUDE.md invariants），不對外用戶 slide 產出強制，但 baransu repo 內 PR 時強制。

P1 / P2 / P3 不分子前綴，僅以嚴重度區隔（P1 fail；P2 soft-warning；P3 advisory）。

---

## P0-S-01：swiss prose 不可使用斜體

### 現象
swiss preset 下的 long-form / slide HTML body 出現 `<em>` / `<i>` / `font-style: italic`，導致字級被瀏覽器以「假斜體」算繪、Swiss baseline grid 對齊破碎、與 Inter / Söhne 等 grotesque 字體的設計意圖相違。

### 根因
作者沿用一般網頁強調直覺，把語意強調等同於視覺斜體；Swiss invariant 第 10 條明文：強調走 weight / spacing / accent color，不走 italic。Inter 等字體的 italic glyph set 在 numeric tabular 場景反而會破壞 KPI 對齊。

### 做法
slide-core / long-form 模板移除所有 `<em>` / `<i>` / `font-style: italic` 宣告；改用 `<strong>` + `--swiss-weight-emphasis` token，或 `letter-spacing` 微調。`check.py` 在 `preset == swiss` 上下文加入 `<em>|<i\b|font-style:\s*italic` regex 偵測，命中即 fail。

source: kami-spec-L86

---

## P0-S-02：swiss CSS attribute 不可寫死 `oklch()`

### 現象
swiss preset slide-core / long-form HTML 內聯 `style="color: oklch(...)"` 或 SVG attribute `fill="oklch(...)"`，導致 Safari < 15.4 / 部分 print pipeline 算繪為黑色或透明，preset accent 完全失效。

### 根因
作者直接從 `tokens.css` 複製 oklch 數值塞 attribute；忽略 CSS attribute 字面值與 CSS property 在解析器上的分流——attribute 走的是 SVG presentation parser，oklch 支援度遠不及 CSS。TASK-shared-02 已劃線：oklch 僅准存在於 CSS variable 或 stylesheet，**不可**進 attribute。

### 做法
所有顏色 attribute 一律改走 CSS class 或 `var(--token-name)`（且該 token 內部可用 oklch）；SVG `fill` / `stroke` attribute 改用 `currentColor` 或具名 class。`check.py` 加入 `(style|fill|stroke)=["'][^"']*oklch\(` regex；命中即 P0-S-02 fail。

source: dogfood-v1.3-handoff

---

## P0-A-01：chevron marker 必須用 `<polygon>`，不可用 `<path>` 模擬

### 現象
diagram-types/*.md 內 SVG chevron / arrow marker 使用 `<path d="M..."/>` 描繪三角，導致 marker units 在不同 SVG renderer（Chromium vs WebKit vs Inkscape print）下大小錯位、stroke-linejoin 殘留圓角。

### 根因
作者把「marker = 任意向量」當前提，未理解 `<polygon points="0,0 10,5 0,10"/>` 是 marker 的標準形態：頂點明確、無 control point、可被 marker-orient 正確旋轉。Kami spec L86 明示：chevron marker = polygon-three-points，path 模擬一律 fail。

### 做法
所有 13 份 `references/diagram-types/*.md` 範例 SVG 將 chevron `<path>` 替換為 `<polygon points="0,0 10,5 0,10" fill="currentColor"/>`，並在 `<marker>` 上設 `markerUnits="strokeWidth"` `orient="auto"`。`validate-output.ts` GATE-J 已涵蓋；`check.py` 加入 `<marker[^>]*>\s*<path` regex 偵測。

source: kami-spec-L86

---

## P0-A-02：top-level node `<rect>` 寬度必須 ∈ {128, 144, 160}

### 現象
diagram SVG 內最外層 node（focal / hub node）`<rect width="..."/>` 取值如 130 / 150 / 175，導致跨 13 份 diagram-types 對齊不一致；多 diagram 並排時 hub node 視覺權重抖動。

### 根因
作者按「目測剛好」設寬度，未對齊 baseline grid 4 倍數白名單；TASK-svg-05 GATE-J 將 top-level node width 鎖在 {128, 144, 160} 三檔（small / medium / large），對應 4 倍數 × 黃金比例近似。任意值會破壞跨 diagram 視覺節奏。

### 做法
所有 diagram-types/*.md 內 top-level node `<rect width>` 一律改為 128 / 144 / 160 三選一；focal node 預設 144。`validate-output.ts` GATE-J 已實作；`check.py` 加入 SVG 解析後對 top-level rect width 比對白名單，不在內即 fail。

source: huashu-incident-2026-04-20

---

## P0-A-03：每個 SVG 至多 2 個 focal node

### 現象
diagram SVG 內以 `--focal-fill` token 或 `class="focal"` 標示的 node 數量 > 2，導致視覺焦點分散、Kami「決定論視覺重心」原則崩壞，reader 無法在 3 秒內定位主軸。

### 根因
作者把所有重要 node 都標 focal，未理解 focal = 視覺重心黏點，應對應「最多兩條敘事主線」；TASK-svg-01..04 共同 invariant：focal cap 2，超過即為「全標 = 沒標」反模式。

### 做法
diagram-types/*.md 範例 SVG 重新審視 focal 標註，每張至多 2 個 focal class / token 使用；其他重要 node 改用 `secondary` class（自動降一級對比）。`check.py` 對 `class="[^"]*focal[^"]*"` 出現次數計數；> 2 即 P0-A-03 fail。

source: kami-spec-L86

---

## P0-B-01：plugin.json `version` 必須在每次發版 bump

### 現象
baransu repo PR 含 `plugins/baransu/skills/**` 或 `plugins/baransu/agents/**` diff，但 `plugins/baransu/.claude-plugin/plugin.json` 的 `version` 欄位未動，導致使用者本機 plugin cache 不會 invalidate、新版 SKILL.md 永遠不會生效。

### 根因
Claude Code plugin 載入機制依 plugin.json version 判斷 cache validity；漏 bump = 等同沒發版。CLAUDE.md non-obvious invariants 明列此項；歷史上 v0.3.x → v0.4.0 多次因此回滾。

### 做法
PR 加入 pre-commit / CI gate：偵測 `plugins/baransu/skills/**` 或 `plugins/baransu/agents/**` 有 diff 但 plugin.json `version` 未變，即 fail。`scripts/check-plugin-version-bump.sh` 對 git diff 解析，未 bump 退碼 1。

source: dogfood-v1.3-handoff

---

## P1-01：dropcap `font-size` 必須 ∈ [4.0em, 5.0em]

### 現象
long-form 首段 dropcap 樣式 `font-size` 設為 3.5em / 6em / 2.8em，導致 dropcap 高度不對齊三行 baseline，視覺上「飄」或「沉」。

### 根因
作者按 print magazine 直覺設大或設小，未對應 line-height × 3 行的 baseline 數學關係；editorial-sanity Check 2 已將 dropcap 鎖在 4.0–5.0em 區間（對應 line-height 1.5 × 3 行 ≈ 4.5em 中位數）。

### 做法
all-preset typography.css dropcap rule 寫死 `font-size: clamp(4.0em, 4.5em, 5.0em)`；editorial-sanity 加入 dropcap font-size 解析 + 區間檢查，超出即 P1-01 fail。

source: dogfood-v1.3-handoff

---

## P1-02：prose 直引號 `"` / `'` 必須 curly 化

### 現象
long-form / slide HTML 文章正文出現直引號 `"abc"` / `'xyz'`（非 HTML attribute 內），導致排印視覺破碎、與 typography 字體的 curly quote glyph 不一致。

### 根因
作者從 markdown 編輯器 / Slack 貼上原文，未經過 smart-quote 轉換；HTML attribute（如 `class="..."`）必須用直引號是 syntax 必然，但 prose 區段必須 typographic curly quote。editorial-sanity Check 3 已明列。

### 做法
build pipeline 加入 prose-only smart-quote 轉換（避開 `<code>` / `<pre>` / HTML attribute）；regex 用 DOM walker 而非純字串替換，避免污染 code block。editorial-sanity 對 `<p>` / `<li>` text content 內 `["']` 計數，> 0 即 P1-02 fail。

source: kami-spec-L86

---

## P1-03：lead paragraph 缺 `text-wrap: pretty`

### 現象
long-form 首段（lead paragraph）末行出現 widow / orphan（單字或極短殘行），閱讀流被打斷；多 preset 並排對照時尤為刺眼。

### 根因
typography 模板未對 lead paragraph 套 `text-wrap: pretty`；該屬性會讓瀏覽器在斷行時優先避免 widow / orphan，但 Safari < 17.4 不支援故許多作者選擇省略。kami spec 立場：能套就套，不支援的瀏覽器 fallback 自然降級無害。

### 做法
all-preset typography.css 對 `.lead`、`article > p:first-of-type` 加 `text-wrap: pretty`；editorial-sanity 解析 stylesheet 對 lead paragraph rule 缺此屬性即報 warning（v1.4 暫列 cosmetic warning，v1.5 視 Safari 17.4 普及率升格 P0）。

source: dogfood-v1.3-handoff

---

## P1-04：人物 `<img>` 缺 `object-position: center 35%`

### 現象
long-form / slide 人像照在 `content-2col` / `compare` / `cover` 版式以預設 `object-position: center center` 算繪，導致頭頂留白過多或下巴被裁。

### 根因
作者未對人像照單獨設 object-position；人臉視覺重心在「上 1/3」處（約 35%），center center 等於把焦點壓到鼻尖以下。schemas sanity Check B 已要求所有 `<img>` 在 `role="portrait"` 或 alt 含 person hint 時走 35%。

### 做法
slide-core / long-form 模板對 `img.portrait` / `[role="portrait"]` rule 寫死 `object-position: center 35%`；schemas sanity 對 portrait class img 缺此宣告即 P1-04 fail。

source: kami-spec-L86

---

## P2-01：top-level node 座標違反 4 倍數

### 現象
diagram SVG 內 top-level node `<rect x="..." y="...">` 取值如 17 / 33 / 51，雖不致破版但與 baseline grid 4 倍數慣例不一致，並排多 diagram 時節奏抖動。

### 根因
作者按手動拖曳 Figma 位置匯出，未做 snap-to-grid 4px；TASK-svg-05 GATE-J 軟性要求 top-level 座標 % 4 == 0，違反僅報 warning（非 P0 fail，因不影響功能）。

### 做法
匯出 SVG 後跑 `scripts/svg-snap-grid.mjs` 自動取整到 4 倍數；`check.py` 對 top-level rect x / y 做 `% 4 != 0` 偵測，命中即 P2-01 soft warning。

source: huashu-incident-2026-04-20

---

## P2-02：chevron marker `<defs>` 在 13 份 diagram-types 重複定義

### 現象
13 份 `references/diagram-types/*.md` 範例 SVG 各自內嵌 `<defs><marker id="chevron">...</marker></defs>`，總計 13 份近乎相同的 marker 定義散落各檔，後續修 marker 樣式要改 13 處。

### 根因
作者按單檔可獨立 render 的便利性把 marker 內聯各檔；忽略 marker 是跨 diagram 共享資產，應 hoist 到 preset 共用 SVG sprite 或單一 `references/diagram-svg-defs.md` 引入。

### 做法
建立 `references/diagram-svg-defs.md` 含 canonical chevron / dot / arrow marker 定義；13 份 diagram-types/*.md 引用同一 `<defs>` block（以 markdown include 或文字 reference）。`check.py` 對 chevron marker `<polygon points="0,0 10,5 0,10"/>` 字面在多檔出現計數，> 1 即 P2-02 hoist 建議 warning。

source: dogfood-v1.3-handoff

---

## P2-03：slide-core layout 名稱不在 22-lock-list

### 現象
slide-core HTML `data-layout="..."` 取值為 `hero-split` / `triple-column` 等自創名稱，不在 swiss preset 22 種鎖定 layout 白名單內，導致 `validate-swiss-deck.mjs` 無法套對應 grid CSS、整張 slide 退到 fallback 樣式。

### 根因
作者按 PPT 思維自由命名 layout，未對齊 swiss preset 的 22 種正規版式（cover / closing / content-2col / kpi-grid / compare / quote / section / data / image-full / image-2col / bullets / timeline / matrix / process / hierarchy / comparison-table / stats / quote-fullscreen / agenda / chapter / divider / appendix）；validate-swiss-deck.mjs 對未知 layout 一律 fail。

### 做法
slide-core 生成階段強制 `data-layout` 取值來自 `references/swiss-22-layouts.md` 名單；未在內即 fail 並提示最近 layout 建議。`validate-swiss-deck.mjs` 已實作；`check.py` 補同步檢查。

source: kami-spec-L86

---

## P2-04：en variant HTML 含 CJK font stack

### 現象
`--locale en` 產出的 long-form / slide HTML `font-family` 含 `"Noto Sans TC"` / `"PingFang TC"` / `"思源黑體"` 等 CJK 字體名，導致英文段落 fallback 至 CJK 字體的 Latin glyph，行距 / 字距與 Inter / Söhne 設計意圖不符。

### 根因
作者複用 zh variant 的 font stack 未做 locale 分流；TASK-schemas-04 明示 en / zh variant 必須各自 font stack：en 走 Inter / Söhne / system-ui，zh 走 Noto Sans TC / PingFang TC。

### 做法
typography.css 拆 `:lang(en)` 與 `:lang(zh)` 兩段 font-family；build 階段對 `--locale en` 產物驗證 stylesheet 中 `font-family` 不含 CJK 字體名（白名單比對）。schemas sanity 加入 locale × font-family 交叉檢查，命中即 P2-04 fail。

source: dogfood-v1.3-handoff

---

## P3-01：SKILL.md 出現分數標題

### 現象
baransu skill SKILL.md 內出現 `### 0.5 Pre-flight` / `### 2.5 Cleanup` 等分數編號 heading，導致 outline / TOC 工具排序錯亂，markdown lint 抱怨 heading sequence。

### 根因
作者為「補插一段不想動既有 1 / 2 / 3 編號」採分數補編號；M3 cosmetic 立場：heading 編號應為連續整數，需插段時要 renumber 後續 heading 或改用 `#### a`。

### 做法
SKILL.md lint 加入 `^### \d+\.\d+` regex 偵測；命中即 P3-01 advisory（不 block merge，但 PR 訊息提示 renumber）。v1.5 視普及度升 P2。

source: dogfood-v1.3-handoff

---

## P3-02：chevron marker `fill` 非 `"none"` 之外的取值

### 現象
SVG `<marker id="chevron">` 內 `<polygon fill="black"/>` 或 `fill="#000"`，導致 print pipeline（特別是 PDF/A 模式）在 marker stroke 與 fill 同色時算繪為實心方塊。

### 根因
作者把 marker 視為實心元件而設 fill；kami spec 慣例：chevron marker `fill="currentColor"` 配合外層 `<path stroke="currentColor" marker-end="url(#chevron)"/>`，由 stroke 顏色決定 marker 顏色。`fill="none"` 適用於空心 marker（不常用）。

### 做法
diagram-types/*.md 範例 SVG marker polygon fill 統一改 `"currentColor"`；空心 chevron 例外用 `"none"`。`check.py` 對 marker polygon fill 取值非 `currentColor` 或 `none` 即 P3-02 advisory。

source: kami-spec-L86

---

## future-trigger 觀察項

每次 `/design preset` dogfood 跑完，將 `check.py` 跳出的 warning top-5 寫進本節「觀察項」；連續 3 個 release 出現的 warning 自動評估升格 P2 或 P1。當前觀察中：

- `<figure>` 缺 `<figcaption>`（image_slot 版式以外）
- `kpi-grid` 內 KPI tile 數量 < 3 或 > 6
- SVG `viewBox` 缺失或比例與 slot 不符
- `<aside>` 註腳字級下限
- long-form bullets 上限是否升 P0
