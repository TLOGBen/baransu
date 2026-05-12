# Requirements

> 12 條 Criteria 拆成 12 條 REQ-XXX。每條 REQ 對應 WIP 內某個 gap（A-M）或 internal debt（M1-M3）；scenarios 為 Given-When-Then，可由 agent 機械驗證。

---

## REQ-001: SVG 14 圖表類型 status=complete + Kami 視覺簽名落地

**對應 WIP Gap**：A（含 A 剩餘 dogfood 軌）
**對應 Criteria**：C1
**描述**：14 種 SVG 圖表類型（含 fallback）在 `book/references/diagram-types/` 全數含 example HTML 並通過 Kami spec（chevron / 節點寬白名單 / focal 視覺 / 4 倍數座標）。

### Scenarios

**Scenario 1：所有 13 個既有 ref-only diagram-type 升級到 complete**
- **Given** `book/references/diagram-types/type-{architecture,flowchart,sequence,state,er,timeline,swimlane,quadrant,nested,tree,layers,venn,pyramid}.md` 13 個檔
- **When** `/baransu:execute` 跑 svg 群組 task
- **Then** 每檔 frontmatter `status: complete`
- **And** 每檔含至少 1 個 viable example SVG block（含完整 `<defs>` chevron marker + 兩層 paper-mask + 至少 1 個焦點節點）
- **And** 跑 `book/scripts/validate-output.ts` 對 example 全 GATE PASS

**Scenario 2：新 SVG 一律走 chevron stroked path**
- **Given** 用戶在 long-form HTML 內含 `<figure class="diagram">`
- **When** /book Stage 3 §4 渲染 diagram
- **Then** 產出 SVG 的所有 `<marker>` 內含 `<path d="M2 1 L8 5 L2 9" fill="none" stroke=... stroke-width="1.5" stroke-linecap="round">`，**不**含 `<polygon points="0 0, 8 3, 0 6" fill=...>`

**Scenario 3：節點寬白名單合規**
- **Given** 任一張產出的 SVG diagram
- **When** 用 regex 掃 `<rect ... width="(\d+)"` 抓所有節點寬
- **Then** 全數 ∈ `{128, 144, 160}`；**或** viewBox 寬 < 360 且使用 2 檔（任 2 個白名單值）
- **And** 焦點節點（`data-role="focal"`）`fill="#EEF2F7"` 且 `stroke="#1B365D"`（或 preset 對應 accent hex）

**Scenario 4：4 倍數座標 anti-slop**
- **Given** 任一張 SVG diagram
- **When** 抽出所有 `x` / `y` / `width` / `height` / `cx` / `cy` 數值
- **Then** 全數 mod 4 = 0；不滿足即視為 anti-slop fail（單張 diagram >1 違規即 SVG GATE fail）

---

## REQ-002: 紙 preset 含 8 種文件 schema + zh/en 雙語

**對應 WIP Gap**：H（含 G 前置三件套）+ L（EN/CN 模板分離）
**對應 Criteria**：C2
**描述**：紙 preset 新增 6 種文件 schema（Resume / Portfolio / One-Pager / Letter / Equity Report / Changelog），加既有 Long Doc + Slides = 8 種；每種 zh / en 雙語 template。

### Scenarios

**Scenario 1：6 新 schema 全有獨立 DESIGN.md schema 段 + long-form variant**
- **Given** 從零起的乾淨 baransu plugin
- **When** `/baransu:design preset 紙` apply 完
- **Then** `紙-preset/` 下含 6 個新 `schemas/{resume,portfolio,one-pager,letter,equity-report,changelog}.md`，每檔含「適用場景 / 版面骨架 / 必填區塊 / SVG 圖表角色」四段
- **And** `紙-preset/design-cores/` 含對應 6 個新 `*.html` template，class prefix 一律 `kami-*`

**Scenario 2：每 schema 含 zh + en 雙模板**
- **Given** 任一新 schema（例如 resume）
- **When** 檢查 `紙-preset/design-cores/`
- **Then** 同時存在 `resume.html`（zh 預設）和 `resume-en.html`（Charter typography stack）
- **And** en 版 font-family 不含 `TsangerJinKai02` / `Noto Serif TC` / `Source Han Serif TC`，且含 `Charter, Georgia, 'Palatino Linotype'` 三 fallback

**Scenario 3：人像 schema 必設 object-position**
- **Given** Portfolio 或 Resume schema 含 `<img>` 人像區塊
- **When** template render
- **Then** 該 `<img>` 含 `object-position: center 35%`（rule of thirds 對齊 guizang README L544/852/2012）
- **And** `紙-sanity.sh` 含對應 lint 規則，無此屬性即 fail

---

## REQ-003: 三 preset slide-cores 各 22 個 Swiss-locked layout

**對應 WIP Gap**：D（含 modular scale 校正）
**對應 Criteria**：C3
**描述**：三 preset 的 `slide-cores/` 各擴張到 22 個 layout（對齊 guizang S01-S22），且全 preset 採用 perfect fourth 1.333× modular scale。

### Scenarios

**Scenario 1：layout 數量達 22**
- **Given** 任一 preset（紙 / swiss / google-design）
- **When** `ls slide-cores/*.html` 數檔案
- **Then** 數量 = 22；檔名包含 `timeline / process / testimonial / agenda / stat-hero / icon-grid / table-heavy / before-after / content-bullets / kpi-grid / quote / section / data` 等核心 layout

**Scenario 2：通過 swiss layout-lock 驗證**
- **Given** 任一 slide-core HTML
- **When** 跑 `book/scripts/validate-swiss-deck.mjs`（新增）
- **Then** 每檔對應 22 lock entry 之一，無冗餘 / 無遺漏

**Scenario 3：modular scale 校正到 1.333**
- **Given** 三 preset 的 `tokens.css`
- **When** 解析 `--font-h1 / --font-h2 / --font-h3 / --font-body` 比例
- **Then** `h1:body ≈ 2.37` ± 0.05；`h2:h3 ≈ 1.333` ± 0.02
- **And** v1.2 的 2.2× / 1.24× 舊比例不可出現

---

## REQ-004: 印刷學三件套全面採用

**對應 WIP Gap**：G（H 的前置）
**對應 Criteria**：C4
**描述**：所有 body / paragraph 採 `text-wrap: pretty`；新增 `.dropcap` 3-line class；template HTML 用 curly quotes（`U+201C` / `U+201D`），不留 straight `"`。

### Scenarios

**Scenario 1：text-wrap: pretty 全面採用**
- **Given** 三 preset 的 `design-cores/long-form.html` + golden-template.html
- **When** grep `body\|\.paper p\|p[^a-zA-Z]` 對應 CSS rule
- **Then** 全含 `text-wrap: pretty`

**Scenario 2：dropcap 3-line drop**
- **Given** `.dropcap` class 定義
- **When** apply 到任一段 `<p>` 第一字
- **Then** 該字 `float: left` + `font-size` 計算後高度 = 3× line-height（不是 2 也不是 4）
- **And** 對應 `editorial-sanity.sh` 新增 dropcap line-count check（解析計算後 height / line-height）

**Scenario 3：Curly quotes 全面取代**
- **Given** 三 preset `design-cores/*.html` + golden-template.html
- **When** grep `"` 不在 HTML attribute 內的位置
- **Then** 計數 = 0（attribute 值內的 `"` 允許）
- **And** 同等位置 `U+201C` / `U+201D` 出現 ≥ 1

---

## REQ-005: Slide checklist 對齊 guizang 523 行 P0-P3 四層

**對應 WIP Gap**：E
**對應 Criteria**：C5
**描述**：`slide-checklist.md` 從 5 條擴張到 15-20 條，分 P0/P1/P2/P3 四層，P0 含 `0-S` / `0-A` / `0-B` 子前綴；每條三欄（現象 / 根因 / 做法）。

### Scenarios

**Scenario 1：分層完整**
- **Given** `design/references/slide-checklist.md`
- **When** 解析 ID 欄
- **Then** 含 ≥ 4 個 P0 條（其中 ≥ 1 條使用 `0-S` 或 `0-A` 或 `0-B` 子前綴）+ ≥ 4 個 P1 + ≥ 4 個 P2 + ≥ 2 個 P3
- **And** 總條目 ∈ [15, 20]

**Scenario 2：每條三欄完整**
- **Given** 任一 checklist 條目
- **When** 讀該條 markdown
- **Then** 含「現象 / 根因 / 做法」三 sub-section 各非空（≥ 10 字）

**Scenario 3：條目來源可追溯**
- **Given** 任一 checklist 條目
- **When** 讀條目 metadata
- **Then** 含 `source: dogfood-{deck-name}` 或 `source: huashu-incident-{date}`（不可憑空虛構）

---

## REQ-006: Fact-Verification + 圖片 Governance + Codex bridge

**對應 WIP Gap**：I + J（含 v3.1 Codex 整合）
**對應 Criteria**：C6
**描述**：/book Stage 2A 加 WebSearch 驗證閘；新增 Core Asset Protocol；三 preset 各自 `image-prompts.md` 含負面尾巴。

### Scenarios

**Scenario 1：產品 / 版本字串強制 WebSearch**
- **Given** /book Stage 2A 對長文偵測到 `(產品名)\s+v?\d+(\.\d+)*` 或人名 + 職位 pattern
- **When** Stage 2A 走 §1 分類前
- **Then** 強制觸發 WebSearch 驗證該字串；未驗證即報「Fact-verify pending」並 ask user 確認
- **And** SKILL.md 內 §0 加「Fact-Verification Principle #0」明文段

**Scenario 2：Core Asset Protocol 4 步**
- **Given** /book 任一階段需 fetch 圖
- **When** 走 image acquisition flow
- **Then** 嚴格依序 ask（user 確認需求）→ generate（Codex CLI image-gen）OR search（Web）→ verify（檢視）→ freeze（commit 到 `.claude/book/{slug}/assets/`）
- **And** 跳步即 fail（例：未 verify 就 freeze）

**Scenario 3：image-prompts.md 負面尾巴標準化**
- **Given** 三 preset 各自的 `image-prompts.md`
- **When** grep prompt template
- **Then** 每個 prompt 結尾固定含「`no title, no footer, no page chrome, no logo, no border`」一字不差
- **And** 產品圖 / logo / UI 三段 fallback 區分清楚

---

## REQ-007: /baransu:design export-brief 子模式

**對應 WIP Gap**：K（v3.1 升級為高優先）
**對應 Criteria**：C7
**描述**：`/baransu:design export-brief` 子指令打包當前 preset 的 DESIGN.md + tokens.css + design-cores 結構為單一 prompt-ready 純文字，可餵 Codex CLI / ChatGPT Images 2.0 端做 cross-tool image-gen。

### Scenarios

**Scenario 1：export-brief 子模式可呼叫**
- **Given** `/baransu:design` SKILL.md
- **When** 跑 `/baransu:design export-brief`
- **Then** 進入 Export-brief mode（gen / preset / lint 之外的第 4 模式）
- **And** SKILL.md 內含「## Export-brief Mode」獨立段

**Scenario 2：產出 prompt brief 含全部資訊**
- **Given** project root 含 tokens.css + DESIGN.md + design-cores/
- **When** 跑 `/baransu:design export-brief`
- **Then** 輸出單一 markdown 區塊（壓在 stdout 或寫到 `.claude/design/brief-{preset}-{date}.md`）
- **And** brief 含 §9 hex 理據（每個 accent token + oklch 等價值）+ §J 負面尾巴 + §G editorial 規格 + 12 行內 design-cores 結構摘要

**Scenario 3：Codex bridge prompt template 預留**
- **Given** brief 輸出末段
- **When** 讀 brief
- **Then** 含「Codex CLI bridge」段，指示用戶如何將 brief 餵 `codex` CLI 端做 image-gen（純文字指引，不實作 MCP）

---

## REQ-008: AI Prompt Guide §9 reproducibility 完整

**對應 WIP Gap**：F
**對應 Criteria**：C8
**描述**：三 preset 的 `DESIGN.md §9` 各自完整含三要素（焦點上限 / hex 設計理據 / 我不是什麼）。

### Scenarios

**Scenario 1：每 preset §9 含三要素**
- **Given** 三 preset 的 `DESIGN.md`
- **When** 讀 §9 段
- **Then** 該段含「(a) 焦點節點 1-2 個」+「(b) accent hex 設計理據（HSL 拆解或 oklch 等價）」+「(c) 我不是什麼（至少 5 條 `no X`）」三標題

**Scenario 2：「我不是什麼」對齊 baseline 反例**
- **Given** Swiss preset §9
- **When** 讀「我不是什麼」清單
- **Then** 至少 5 條，含「no cool accent」+「no oklch in attribute」+「no italics」+「no gradient bg」+「no second accent」（或語義等價）

---

## REQ-009: oklch advisory footnote

**對應 WIP Gap**：M
**對應 Criteria**：C9
**描述**：三 preset 的 `DESIGN.md §2` 加 `oklch()` advisory footnote，accent token 旁標等價值；不改現有 hex 為主規格。

### Scenarios

**Scenario 1：§2 含 footnote 標記**
- **Given** 三 preset `DESIGN.md`
- **When** 讀 §2 表
- **Then** `--accent` row 包含 oklch 等價（例：`#1B365D → oklch(0.32 0.08 256)`）
- **And** §2 結尾含 footnote「oklch 為 advisory；WeasyPrint print pipeline 仍以 hex 為準」

**Scenario 2：實際 CSS 不含 oklch()**
- **Given** tokens.css + 任一 design-core HTML
- **When** grep `oklch\(`
- **Then** 命中 = 0（advisory 只在 DESIGN.md 文件，不入 CSS）

---

## REQ-010: v1.3 internal debt 收尾

**對應 WIP Internal Debt**：M1 + M2 + M3
**對應 Criteria**：C10
**描述**：v1.3 handoff 三項 internal debt 全收。

### Scenarios

**Scenario 1：M1 swiss-smoke-test fixture regen**
- **Given** `book/scripts/swiss-smoke-test.sh`
- **When** 跑該腳本對三 preset E2E
- **Then** 全 GATE PASS（含新增的 GATE-H editorial-sanity / GATE-I export-brief-presence）
- **And** validate-fixtures 對應更新 22 layout coverage

**Scenario 2：M2 design-token-resolver + golden-template v1.3-aware**
- **Given** `book/references/design-token-resolver.md` 與 `book/references/golden-template.html`
- **When** 讀檔
- **Then** wording 含「v1.3」/「v1.4」字串，不含 Kami-only / v1.2 殘留 wording
- **And** golden-template 同時涵蓋三 preset（紙 / swiss / google-design）的解析路徑示例，不再只展示 Kami

**Scenario 3：M3 SKILL.md 步驟整數化**
- **Given** `/baransu:book` SKILL.md + `/baransu:design` SKILL.md
- **When** grep `^### \d+\.\d+` 抓 fractional 步驟編號
- **Then** 命中 = 0（v1.3 過程中產生的 0.5 / 0.6 / 2.5 fractional 編號全 renumber 成純整數，可使用「Step 0.5 已併入 Step 0」過渡記號但章節 heading 不再有 .5）

---

## REQ-011: plugin 升版 v1.3.1 → v1.4.0

**對應 Criteria**：C11
**描述**：minor bump 表示 baseline-parity milestone。

### Scenarios

**Scenario 1：plugin.json 升版**
- **Given** `plugins/baransu/.claude-plugin/plugin.json`
- **When** 最後一筆 task commit 後讀檔
- **Then** `version: "1.4.0"`

**Scenario 2：CHANGELOG 追加 v1.4.0 entry（若 CHANGELOG 存在）**
- **Given** repo root 含 `CHANGELOG.md`（若無則跳過）
- **When** 讀 changelog
- **Then** 含「## [1.4.0] - 2026-MM-DD」段，列出 12 條 Criteria 對應的 feat / fix entries

---

## REQ-012: Production-parity 自評腳本

**對應 Criteria**：C12
**描述**：新增 `scripts/baseline-parity-score.py` 對三 baseline 計算單一加權 % 分數；可單命令跑完所有 sanity check。

### Scenarios

**Scenario 1：腳本可跑、輸出結構化結果**
- **Given** repo root，clean checkout
- **When** 跑 `python3 scripts/baseline-parity-score.py`
- **Then** stdout 含 11 行（C1-C11 每行一個 pass / fail + 各別百分比）
- **And** 末行印「Overall baseline-parity score: NN.N%」單一加權數字

**Scenario 2：~95% target 偵測**
- **Given** v1.4.0 final state（所有 REQ-001 - REQ-011 完成）
- **When** 跑 score 腳本
- **Then** Overall ≥ 90.0%（理論上限 95%，給 5% 容差）
- **And** exit code = 0（< 90% 則 exit 1，作為 CI gate 備用）

**Scenario 3：腳本自評不含 REQ-012 自身**
- **Given** 腳本實作
- **When** 讀腳本邏輯
- **Then** 12 條 Criteria 中只算 C1-C11 11 條的加權 %（C12 = 腳本自身，避免循環自評）
