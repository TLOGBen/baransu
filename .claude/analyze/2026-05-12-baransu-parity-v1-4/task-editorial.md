# Tasks: editorial

**前置群組**：shared

## TASK-editorial-01: 三 preset design-cores + tokens.css 全面採用 `text-wrap: pretty`

**需求追溯**：REQ-004 Scenario 1
**目標**：所有 body / paragraph CSS rule 加 `text-wrap: pretty`，覆蓋三 preset。
**驗收標準**：
- [ ] 三 preset 的 `design-cores/long-form.html` body / `.kami-body` / `.swiss-body` / `.gd-body` 對應 CSS rule 含 `text-wrap: pretty`
- [ ] golden-template.html body / p / .paper p 同含
- [ ] grep 三 preset design-cores 內所有 `<p>` / body 相關 selector，含 `text-wrap: pretty` 命中 ≥ 3

### 步驟

#### 模板層
- [ ] 紙 preset：對 `long-form.html` 的 body / `.kami-body` 加 `text-wrap: pretty`
- [ ] swiss preset 同等
- [ ] google-design preset 同等
- [ ] golden-template.html body + p block 加

#### 驗證
- [ ] `grep -r "text-wrap: pretty" plugins/baransu/skills/design/references/*-preset/design-cores/long-form.html` 命中 = 3
- [ ] `grep -c "text-wrap: pretty" plugins/baransu/skills/book/references/golden-template.html` ≥ 1

---

## TASK-editorial-02: 三 preset 新增 `.dropcap` class 3-line drop

**需求追溯**：REQ-004 Scenario 2
**目標**：印刷學 dropcap 視覺工藝，3-line 是甜蜜點（不是 2 也不是 4）。
**驗收標準**：
- [ ] 三 preset `tokens.css` 或 `design-cores/long-form.html` `<style>` 含 `.dropcap` / `.kami-dropcap` class（前綴對齊各 preset）
- [ ] computed height ≈ 3 × line-height（用 `font-size: calc(var(--leading-body) * 3)` 或對應實值）
- [ ] `float: left` + `padding-right` ≥ 4px 防擠壓
- [ ] long-form template HTML 含 ≥ 1 個示範段使用 dropcap

### 步驟

#### 規格層
- [ ] 在 `紙-preset/DESIGN.md §3 Typography Rules` 段加 `.dropcap` 段（含 3-line 規格說明）
- [ ] swiss / google-design DESIGN.md 同等

#### 模板層
- [ ] 紙 preset 的 `design-cores/long-form.html` `<style>` 加 `.kami-dropcap` rule
- [ ] 同檔 demo section 加一段使用 `<p class="kami-body"><span class="kami-dropcap">L</span>orem...</p>`
- [ ] swiss / google-design preset 同等

#### 驗證
- [ ] grep `kami-dropcap\|swiss-dropcap\|gd-dropcap` 三 preset design-cores 命中 ≥ 6（class 定義 + demo 使用各 1）

---

## TASK-editorial-03: 三 preset design-cores curly quotes 全面替換

**需求追溯**：REQ-004 Scenario 3
**目標**：HTML template 內所有 prose 區域的 straight `"` 替換為 curly `U+201C` / `U+201D`，相應的單引號替換為 `U+2018` / `U+2019`。
**驗收標準**：
- [ ] 三 preset design-cores HTML 內 prose 文本（非 HTML attribute、非 code block）不含 `"` straight
- [ ] curly `“` `”` 出現 ≥ 1 per file（demo content 內）

### 步驟

#### 模板層
- [ ] 對每 preset 的 `design-cores/long-form.html`，掃出 demo content（`<p>` / `<blockquote>` / `<figcaption>` 內文）
- [ ] 用 sed 或手動替換 straight 為 curly（注意保留 attribute 內的 `"`）
- [ ] golden-template.html 同等

#### 驗證
- [ ] 寫 awk 一行：解析 HTML，只取 element text content（不含 attribute / code / pre），grep `"` 命中 = 0
- [ ] 同樣解析後 grep `[“”]` 命中 ≥ 1

---

## TASK-editorial-04: editorial-sanity.sh 新增 + 三 preset sanity.sh 整合

**需求追溯**：REQ-004 整體 + B11/B12 邊界條件機械化
**目標**：新增 editorial 三檢查為 reusable shell script，由三 preset sanity.sh 共用呼叫。
**驗收標準**：
- [ ] 新檔 `plugins/baransu/skills/design/references/editorial-sanity.sh`，含三 check：dropcap line-count / curly-quote-presence / widow-orphan-stub
- [ ] 紙-sanity.sh / swiss-sanity.sh / gd-sanity.sh 三檔結尾 source 或呼叫 `editorial-sanity.sh`
- [ ] 對故意違規 fixture，editorial-sanity.sh exit 1
- [ ] 對 task-editorial-01/02/03 改完的 design-cores，exit 0

### 步驟

#### 驗證層
- [ ] 寫 `editorial-sanity.sh` shell（接受 design-core file path 為 arg；對單檔 / 整目錄都能跑）
  - Check 1: `text-wrap: pretty` 存在於 body 或 `.kami-body` / `.swiss-body` / `.gd-body` rule
  - Check 2: `.dropcap` class 定義 + 用 awk 解析 `font-size` 對應 `line-height` 倍數 ≈ 3
  - Check 3: prose text content 中 straight `"` 數量 = 0（用 awk 解析）
- [ ] 三 preset sanity.sh 加入呼叫：`bash ../editorial-sanity.sh design-cores/long-form.html`

#### 驗證
- [ ] 跑各 preset sanity.sh，editorial 段全 PASS
- [ ] 製造一個故意 strip 掉 `text-wrap: pretty` 的 fixture，sanity exit 1
