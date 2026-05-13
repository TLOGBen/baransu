# Tasks: checklist-governance

**前置群組**：schemas, layouts

## TASK-cg-01: slide-checklist.md 5 → 15-20 條 P0/P1/P2/P3 四層

**需求追溯**：REQ-005
**目標**：對齊 guizang 523 行 checklist 結構（不是字數對齊，是結構 + 分層 + 三欄沉澱）。
**驗收標準**：
- [x] `design/references/slide-checklist.md` 總條目 ∈ [15, 20]
- [x] 含 ≥ 4 個 P0（其中 ≥ 1 使用 `0-S` / `0-A` / `0-B` 子前綴）+ ≥ 4 個 P1 + ≥ 4 個 P2 + ≥ 2 個 P3
- [x] 每條含「現象 / 根因 / 做法」三 sub-section
- [x] 每條含 `source: ...` metadata（dogfood / huashu-incident / kami-spec 三來源）

### 步驟

#### 規格層
- [x] 讀既有 slide-checklist.md 5 條
- [x] 把 5 條既有的逐條補三欄 + source（多數應為 `source: kami-spec-Lxx` 或 `source: dogfood-v1.3-handoff`）
- [x] 新增 10-15 條 from dogfood / kami spec / huashu Junior Designer 原則
- [ ] 分層分配：
  - P0-S（Swiss 模式專屬）：no italics / no oklch in attribute / no second accent
  - P0-A（all preset）：focal cap 2 / chevron 強制 / 4 倍數座標
  - P1：dropcap 3-line / curly quotes / object-position 35%
  - P2：node-width 白名單 / paper-stack shadow / hairline 0.5px
  - P3：oklch advisory / Stage 整數化 / SKILL.md cross-ref clean

#### 驗證
- [ ] grep `^## P[0-3]` 計數 ≥ 15
- [ ] 對每條目 grep `### 現象` / `### 根因` / `### 做法` 三 heading 存在
- [ ] **新增 checklist-sanity check**：寫一小段 shell（或加進三 preset sanity.sh）：對 slide-checklist.md 用 awk 解析 P0/P1/P2/P3 計數 + 每條三 heading 存在 + `source:` 非空非 "TBD"；不合規即 exit 1（對應 test.md 整合測試「Checklist sanity 結構驗證」）

---

## TASK-cg-02: /book SKILL.md Stage 0 加 Fact-Verification Principle #0

**需求追溯**：REQ-006 Scenario 1
**目標**：對含具體產品 / 版本 / 人名 + 職位 pattern 的長文，Stage 2A 前強制 WebSearch verify。
**驗收標準**：
- [x] `book/SKILL.md` Stage 0 段（或 Stage 2A 開頭）含「Fact-Verification Principle #0」標題段
- [x] 段內含正則模式 + WebSearch 觸發 flow + AskUserQuestion 阻擋 flow
- [x] 對 fixture「`Linear MCP v3.4.7 released 2025-09-15`」測試（虛構字串），SKILL.md 邏輯走 ask

### 步驟

#### 規格層
- [x] 在 SKILL.md Stage 0 後（或 Stage 2A §0）加新段「Fact-Verification Principle #0」
- [x] 內含：
  - 偵測 regex：`/([A-Z][a-zA-Z]+\s+(MCP|SDK|CLI|API)?\s*v?\d+(\.\d+)*)|([A-Z][a-z]+\s+[A-Z][a-z]+(\s|,)+(CEO|CTO|founder|engineer))/`
  - 命中 → WebSearch verify each hit（提供 query template）
  - 0 結果 → AskUserQuestion「Fact-verify pending: {hit}; 強制繼續 / 改用 --text / 中止」
- [x] 在 SKILL.md Stage 0 開頭加引述：「本 SKILL.md 採 Fact-Verification Principle #0（見下 §...）」

#### 驗證
- [x] grep `Fact-Verification Principle` book/SKILL.md 命中 ≥ 2（引述 + 段標題）

---

## TASK-cg-03: Core Asset Protocol 4 步寫入 SKILL.md + Codex CLI bridge wording

**需求追溯**：REQ-006 Scenario 2
**目標**：圖片取得走 ask → generate-OR-search → verify → freeze 4 步，跳步即 fail。
**驗收標準**：
- [x] `book/SKILL.md` Stage 3 內含「Core Asset Protocol」獨立段
- [x] 段內含 4 步明細，第 2 步明示「Codex CLI image-gen 端 OR Web search 二擇一」
- [x] 含「跳步 = fail」明文

### 步驟

#### 規格層
- [x] 在 SKILL.md Stage 3 §image 對應段加 Core Asset Protocol 段
- [x] 4 步：
  1. **Ask**：與 user 確認圖片用途、構圖、必含元素
  2. **Generate OR Search**：跑 Codex CLI image-gen（傳入 brief from /design export-brief） OR WebSearch 找現成資源（CC license）
  3. **Verify**：renderer 將圖嵌入 long-form HTML preview，user 肉眼確認
  4. **Freeze**：commit 到 `.claude/book/{slug}/assets/` 並寫 `meta.json` 含 source / prompt / license

- [x] 加「跳步 = fail」明文：「Steps must run in order; skipping = fail and abort.」

#### 驗證
- [x] grep `Core Asset Protocol` book/SKILL.md 命中 ≥ 1
- [x] grep `Codex CLI image-gen` book/SKILL.md 命中 ≥ 1

---

## TASK-cg-04: 三 preset image-prompts.md 新增 + 負面尾巴標準化

**需求追溯**：REQ-006 Scenario 3
**目標**：每 preset 各自 `image-prompts.md` 含產品圖 / logo / UI 三段 fallback；prompt 結尾固定負面尾巴。
**驗收標準**：
- [x] 三 preset 各含 `image-prompts.md`（含紙、swiss、google-design 各一）
- [x] 每檔含三段：產品圖 / logo / UI 三 fallback
- [x] 每段 prompt 結尾字面含：`no title, no footer, no page chrome, no logo, no border`

### 步驟

#### 規格層
- [x] 寫 `紙-preset/image-prompts.md`：
  - 段 1「產品圖」prompt：偏 editorial 攝影、紙質感、無 UI chrome
  - 段 2「logo」prompt：minimalist mark、單色（preset accent）
  - 段 3「UI」prompt：long-form 紙感 mockup
- [x] 每段 prompt 結尾加負面尾巴
- [x] swiss-preset / google-design-preset 同等（但風格詞換成 Swiss / Material）

#### 驗證
- [x] `grep -c "no title, no footer, no page chrome, no logo, no border" plugins/baransu/skills/design/references/*-preset/image-prompts.md` 命中 ≥ 9（三檔 × 3 段）
- [x] 三檔 sanity 跑過
