# Tasks: cross-tool

**前置群組**：shared, schemas, layouts

## TASK-ct-01: /design SKILL.md 新增 Export-brief Mode 段

**需求追溯**：REQ-007 Scenario 1
**目標**：在 /design 既有的 gen / preset / lint 三模式之外新增 export-brief 第 4 模式。
**驗收標準**：
- [x] `design/SKILL.md` 含「## Export-brief Mode」獨立 heading
- [x] 段內描述 invocation pattern（`/baransu:design export-brief [--stdout]`）+ 預期輸出
- [x] SKILL.md 開頭的 mode dispatch 邏輯加 export-brief 分支

### 步驟

#### 規格層
- [x] 在 SKILL.md mode dispatch 開頭區段加 4th branch
- [x] 加新段「## Export-brief Mode (v1.4)」，含：
  - 用途說明（cross-tool brief 給 Codex CLI / ChatGPT Images 2.0）
  - 輸入：當下 preset（從 tokens.css 首行註解解析）
  - 輸出：純 markdown 區塊到 stdout（`--stdout` 旗標）或寫到 `.claude/design/brief-{preset}-{date}.md`（預設）

#### 驗證
- [x] grep `^## Export-brief Mode` design/SKILL.md 命中 = 1
- [x] grep `export-brief` design/SKILL.md 命中 ≥ 3（dispatch、heading、wording）

---

## TASK-ct-02: Export-brief mode 實作（讀 tokens / DESIGN / design-cores 組裝 brief）

**需求追溯**：REQ-007 Scenario 2 / 3
**目標**：mode 邏輯實作（SKILL.md 內列出 step-by-step instruction，不另外開 script）；brief 包含 §9 hex + §J 負面尾巴 + §G editorial + design-cores 結構摘要 + Codex bridge wording。
**驗收標準**：
- [x] SKILL.md Export-brief Mode 段內含「Step 1 — 解析 preset」「Step 2 — 讀 source files」「Step 3 — 組裝 brief」「Step 4 — 輸出」四 sub-step
- [x] 對三 preset 任一執行該 mode（人工 dry-run），brief 含五大段：preset header / §9 hex 理據 / §J 負面尾巴 / §G editorial 規格 / design-cores 結構摘要 / Codex bridge wording
- [x] hex 從 tokens.css 動態解析，不寫死（B20 邊界）

### 步驟

#### 規格層
- [x] 在 SKILL.md Export-brief Mode 段內寫 step-by-step instruction：

  ```
  Step 1 — 解析 preset：讀 {root}/tokens.css 首行，取 /* preset: xxx */ 註解
  Step 2 — 讀 source files：
    - {root}/DESIGN.md 全文
    - {root}/tokens.css 全文
    - {root}/design-cores/*.html 檔名清單 + 每檔開頭 30 行 inline <style>
    - {plugin}/references/{preset}-preset/image-prompts.md
  Step 3 — 組裝 brief（markdown）：
    Section A: Preset header（名稱 / 哲學 1 句）
    Section B: §9 hex 理據（從 DESIGN.md §9 截）
    Section C: §J 負面尾巴（從 image-prompts.md 截）
    Section D: §G editorial 規格（dropcap 3-line / text-wrap pretty / curly quotes）
    Section E: design-cores 結構摘要（每 schema 一行）
    Section F: Codex bridge wording（「將本 brief 餵 codex CLI 端：codex `prompt --stdin < brief.md` ...」）
  Step 4 — 輸出：
    - 預設：寫到 `{root}/.claude/design/brief-{preset}-{date}.md`
    - --stdout：印到 stdout
  ```

- [x] 在 Step 4 後加成功訊息：「Brief 已寫入 {path}（{word_count} 詞）。可餵 Codex CLI 端做 image-gen prompt。」

#### 驗證
- [ ] 人工跑：在三 preset apply 後分別 invoke `/baransu:design export-brief`，檢查產出 brief 含五段
- [x] 切 preset 後重跑，hex 對應切換（不寫死）

---

## TASK-ct-03: M2 design-token-resolver.md v1.3+ 升級

**需求追溯**：REQ-010 Scenario 2a
**目標**：清掉 v1.2 wording / Kami-only 殘留；提到三 preset 適用。
**驗收標準**：
- [x] `book/references/design-token-resolver.md` 含「v1.3」/「v1.4」字串 ≥ 1
- [x] 提到紙 / swiss / google-design 三 preset 各自的 hex 範例（不只 Kami）
- [x] 不含 v1.2-era wording（如「marker 用 polygon」/「節點寬 12 檔」）

### 步驟

#### 規格層
- [x] 讀 `book/references/design-token-resolver.md` 全文
- [x] 改寫 hex 範例段：列三 preset 的 `--paper` / `--accent` 對應 hex 表
- [x] 移除 v1.2-era marker polygon / 12 檔節點寬 wording
- [x] 加 v1.4 ack note

#### 驗證
- [x] grep `v1.3\|v1.4` design-token-resolver.md 命中 ≥ 1
- [x] grep `swiss\|google-design` 命中 ≥ 2
- [x] **整合測試錨點**：grep 三 preset 的 `--paper` / `--accent` hex 對照表存在於 design-token-resolver.md 內（對應 test.md 整合測試「design-token-resolver 三 preset hex 範例存在」）

---

## TASK-ct-04: M2 golden-template.html 三 preset 解析示例擴張

**需求追溯**：REQ-010 Scenario 2b
**目標**：v1.3 golden-template 只展示 Kami 風格；v1.4 加 swiss + google-design preset 對應 reference 區塊或 alt-template 檔。
**驗收標準**：
- [x] 新增 `book/references/golden-template-swiss.html` 與 `book/references/golden-template-gd.html`
- [x] 三檔分別對應 preset 的 typography / color / SVG token
- [x] 三檔 SVG primitives section（chevron / paper-mask / type tag / legend）全綠通過 validate-output.ts

### 步驟

#### 模板層
- [x] copy `golden-template.html` 為 `golden-template-swiss.html`
- [x] 改：body font-family 改 Swiss invariant `'Inter', 'Helvetica Neue', sans-serif`；accent hex 改 `#002FA7`；移除 dropcap demo（Swiss invariant 禁 italics + 禁 dropcap，由 task-editorial-02 決定是否允許 Swiss preset 有 dropcap，否則改示範段省略）
- [x] 改：SVG primitives section 沿用 chevron + 2-tier 節點寬 + focal #002FA7 stroke + #DDE2EF fill（Swiss 對應 brand-tint）
- [x] 同等做 google-design variant

#### 驗證
- [ ] 三檔（`golden-template.html` / `golden-template-swiss.html` / `golden-template-gd.html`）**皆**跑 `book/scripts/validate-output.ts` 對應 fixture，GATE A-K 全 PASS（對應 test.md E2.5「三 golden-template 變體 cross-preset 跑通」）
- [ ] swiss-smoke-test.sh fixture iteration list 加入 swiss / gd variant
- [ ] 視覺檢查：三檔在瀏覽器打開風格明顯不同
