# baransu /design + /book Roadmap to Production Parity — WIP

**Status**: planning，未排程
**Created**: 2026-05-12
**Updated**: 2026-05-12（v2：重新框架為 production capability + 修矛盾 + 整合）
**Fact-checked**: 2026-05-12（v3：兩輪 fact-check 對三 baseline raw material + Kami `references/diagrams.md` + huashu repo 結構 + guizang `checklist.md` 行數，修 2 處錯誤 / 5 處 unverified → confirmed）
**Addenda v3.1**：(1) SKILL.md 內步驟編號應整數化（移除 0.5 / 0.6 fractional） (2) 環境含 Codex（理論支援 GPT image 生成）→ K3/J/§不可達 重估

---

## 目標（核心定錨）

**用 baransu /design + /book 能產出對應這三個 baseline 專案的等價輸出**：

| Baseline | 期待產出能力 |
|----------|------------|
| `op7418/guizang-ppt-skill` | Swiss 國際主義風 PPT slide HTML（22 layout + 圖片協議 + 七問澄清前置）|
| `alchaincyf/huashu-design` | Editorial 印刷學 + 多場景（簡報 / 動畫 / 影音 / 工作流 / 評審 5 類）|
| `tw93/Kami` | 印刷品設計系統：8 文件類型（One-Pager / Long Doc / Letter / Portfolio / Resume / Slides / Equity Report / Changelog）+ 14 inline SVG 圖表 + 紙質感工藝 |

**% 定義**：不是抽象 feature parity，是「**對於 baseline 能產出的 user prompt，baransu 能產出多少比例同等品質的 artifact**」。

---

## 現況基線（修正前版本的數字矛盾）

| 維度 | 對 guizang/huashu | 對 Kami | 加權平均 |
|------|------------------|---------|---------|
| 機械骨架（pipeline / validator / layout 數 / interview） | 48% | 55% | **~52%** |
| 視覺工藝（typography / color craft / 紙質感 / 印刷學詞彙） | 45% | 50% | **~47%** |
| **綜合**（產出能力加權） | — | — | **~50%** |

> 修正：v1 WIP「機械層 85%」是 style-reviewer 相對描述被誤讀為絕對值；實際 ~52%。
> 修正：v1 WIP 工藝層 milestone 「97%」是灌水；V 項全做完理論上限只能到 ~70%（剩 30% 是 baransu plugin scope 外的能力，如 image-gen MCP 整合）。

---

## 整合 Gap Inventory（從 25 項合併為 13 項 + 2 internal debt）

每項 gap 兩切面：**機械骨架**（impl 動作） + **工藝要求**（quality requirement）。**% 跳幅是「對 baseline 產出能力的提升」**，不是抽象功能完成度。

> 整合邏輯：v1 WIP 把 M/G/K（機械軌）vs V（工藝軌）做正交切分，但實作上多數 V 項是 G/K 項的工藝面（同 commit 兩面），故整併。

### A. SVG Visual Primitives 對齊（含 chevron + 節點寬白名單 + diagram-types 12 完整）

合併自：K4 + V1 + K1 + V2

**Kami baseline 完整 specs（已 fact-check `references/diagrams.md`）**：
- Chevron 取代 filled triangle：`<path d="M2 1 L8 5 L2 9" fill="none" stroke=... stroke-width="1.5" stroke-linecap="round"/>`；WeasyPrint 不支援 `<marker orient="auto">`，必須改手繪 chevron（L86）
- Node width 三檔 `{128, 144, 160}`；小圖（viewBox < 360）可壓 2 tier 但仍保持 2，不個別客製（L79）
- Focal rule 1-2 個 per diagram：`#1B365D` stroke + `#EEF2F7` fill（L49）
- All coords / widths / gaps divisible by 4 — "anti-AI-slop floor"（L78）

| 切面 | 內容 |
|------|------|
| 機械 | marker polygon → chevron `<path d="M2 1 L8 5 L2 9">` 全面遷移；`book/references/diagram-types/` 12 種 `ref-only` → `complete`（補 example SVG） |
| 工藝 | 四項 Kami 視覺簽名嚴格落地：chevron / 節點寬 128-144-160 三檔（含 < 360 viewBox 2-tier 例外）/ focal ≤ 2 含 `#EEF2F7` fill / 4-multiple 座標 |
| Enables | **Kami 14 圖表類型對應產出** + 長文 HTML diagram 視覺簽名復原 |
| 工程量 | 中大（12 SVG example + svg-rendering-rules.md §4.3 / §4.5 重寫 + golden-template.html SVG 範例改三檔） |
| 跳幅 | **+12 pp** |
| Status | 🔴 anchor 違規修復（最戲劇性 spec/impl drift）|

### B. /book Pre-interview Gate（七問澄清前置閘門）

維持單獨：G1

| 切面 | 內容 |
|------|------|
| 機械 | 在 /book Stage 0.5-1 之間插入 batch interview：受眾 / 時長 / 風格傾向 / 已有素材 / 硬約束（4-5 題）。搬 /design Gen Mode 訪談 pattern |
| 工藝 | N/A（純結構） |
| Enables | **對應 guizang 七問澄清 / huashu 五類必問** —— 動手前壓住 50% 不確定性 |
| 工程量 | 小（~30 行 SKILL.md edit） |
| 跳幅 | **+10 pp**（單一最高 CP） |
| Status | 🔴 最高 ROI |

### C. 紙質感 Spec/Impl 對齊

合併自：V3 + V4

| 切面 | 內容 |
|------|------|
| 機械 | `golden-template.html` / `long-form.html` border 1px → 0.5px；`.paper` 第三 shadow 規格化（新增 `--shadow-paper-stack` token 或改 whisper-only） |
| 工藝 | 0.5pt hairline 紙張纖維邊錯覺；`.paper` 雙層 shadow 「紙張堆疊感」明確收編成第三類陰影規格 |
| Enables | **Kami-grade 紙質感工藝在 baransu impl 真實落地**（目前 spec 寫了但 impl 全部用 1px / shadow 違規）|
| 工程量 | 小 | 跳幅 | **+4 pp** |
| Status | 🟡 spec/impl drift 修復 |

### D. Slide-Cores 擴張 + Modular Scale 對齊

合併自：G2 + V8

> **Fact-check 修正**：原 WIP 寫「對齊 guizang 47 layout」是錯的；實際 guizang 為 **22 個 Swiss-locked layout（S01-S22）**。baransu slide-cores 從 12 → **20-22** 即接近上限，**跳幅可能下修為 +7 pp**。

| 切面 | 內容 |
|------|------|
| 機械 | slide-cores 每 preset 12 → 20+ layout（timeline / process / testimonial / agenda / stat-hero / icon-grid / table-heavy / before-after）×3 preset = 24 新檔 |
| 工藝 | 同時校正 modular scale 為 perfect fourth 1.333（H1:Body 從 2.2× 改 2.37×；H2:H3 從 1.24× 改 1.333×）。新 layout 必須遵循新 scale |
| Enables | **對應 guizang 22 Swiss layout S01-S22** PPT 多樣性（不再 47 個假目標）|
| 工程量 | 中 | 跳幅 | **+7-10 pp**（依最終 lock 多少個新 layout） |
| Status | 🟡 視覺多樣性核心 |

### E. Checklist 完整擴張（含具體 CSS 陷阱）

合併自：G3 + V10

> **Fact-check 修正**：guizang `checklist.md` 實際 **523 行**（不是 524；off-by-1）+ **P0/P1/P2/P3 四層**（不是三層）。P0 條目以 `0-S` / `0-A` / `0-B` 子前綴細分（Swiss 模式專屬）。

| 切面 | 內容 |
|------|------|
| 機械 | `slide-checklist.md` 5 → 15-20 條 **P0/P1/P2/P3 四層**（含 P0 子前綴細分如 `0-S`、`0-A`） |
| 工藝 | 從真實 bug 沉澱「現象 → 根因 → 做法」三欄；具體 CSS 陷阱（如 `.paper` 雙層 padding trap、`.kami-quote` left-edge 對齊、code-prose 接縫 padding）|
| Enables | **對應 guizang 523 行 checklist 四層防 regression 能力** |
| 工程量 | 累積（dogfood-driven） | 跳幅 | **+6 pp** |
| Status | 🟢 dogfood-driven，每次跑完 deck 補 3-5 條 |

### F. AI Prompt Guide §9 Reproducibility 強化

合併自：V5 + V6 + V13

| 切面 | 內容 |
|------|------|
| 機械 | DESIGN.md §9 段落擴充 |
| 工藝 | (a) 焦點節點上限 1-2 個 (b) `#1B365D` hex 設計理據（S=55 L=24 避開 navy/indigo）(c) allowed contradictions / 我不是什麼（無 cool accent / oklch / italics） |
| Enables | **餵 §9 prompt 給外部 AI 能生 Kami 風**（reproducibility 工藝） |
| 工程量 | 小 | 跳幅 | **+2.5 pp** |
| Status | 🟢 |

### G. Editorial 三件套

維持單獨：V7

| 切面 | 內容 |
|------|------|
| 機械 | `text-wrap: pretty` 加 body + `.paper p`；新增 `.dropcap` class 3-line drop；HTML 內 `\201C` / `\201D` curly quotes |
| 工藝 | dropcap 高度 3 行（不是 2 也不是 4——印刷學甜蜜點）；curly quotes 取代 straight quotes；widow/orphan 防護 |
| Enables | **印刷學辨識度** + Letter / Resume 等 K2 schema **前置工藝**（無此三件套，K2 落地仍是 AI 風） |
| 工程量 | 中（spec + template + tokens 三處改） | 跳幅 | **+4 pp** |
| Status | 🟡 H 的前置 |

### H. 新文件 Schema（含 G 工藝必填）

合併自：K2 + V11

| 切面 | 內容 |
|------|------|
| 機械 | 4 新 schema：Resume / Portfolio / One-Pager / Letter（每種獨立 DESIGN.md schema + long-form variant） |
| 工藝 | 必引用 G 的 editorial 三件套；Portfolio / Resume 含人像時必設 `object-position: center 35%`（rule of thirds） |
| Enables | **Kami 8 文件類型橫向覆蓋的 4/8 = 50%**（已有 long-form 等於 Long Doc + Slides 兩種，加 4 種 = 6/8） |
| 工程量 | 大 | 跳幅 | **+7 pp** |
| Status | 🟢 需 G 先行 |

### I. Fact-Verification Principle #0

維持單獨：G4

| 切面 | 內容 |
|------|------|
| 機械 | /book Stage 2A 對具體產品/版本 → 強制 `WebSearch` 驗證 |
| 工藝 | N/A | Enables | **對應 huashu 2026-04-20 事故沉澱**（防生 hallucinated 規格） |
| 工程量 | 小 | 跳幅 | **+3 pp** |
| Status | 🟢 |

### J. 圖片 Governance 整套

合併自：G5 + V12（V11 已歸 H）

> **v3.1 升級**：用戶環境含 Codex → image acquisition step 從「需接外部 MCP / search」可以走 **Codex CLI image-gen 端**直接生成而非 download。Core Asset Protocol 5 步可重定義為：ask → **generate (via Codex GPT image)** → verify → freeze。工程量從「大」降為「中」。

| 切面 | 內容 |
|------|------|
| 機械 | Core Asset Protocol（v3.1 修訂）：ask → search **OR Codex image-gen** → verify → freeze；新增 `紙-preset/image-prompts.md` |
| 工藝 | 配圖 prompt 固定負面尾巴 `no title, no footer, no page chrome, no logo, no border`；產品圖 / logo / UI 三段 fallback（v3.1: Codex-generated 也走同 prompt brief） |
| Enables | **對應 huashu Core Asset Protocol** + **Codex GPT image inline 生成 baransu-styled artwork** —— 不再「畫框中畫框」AI slop |
| 工程量 | 中（v3.1: 從「大需 MCP」降為「中含 Codex bridge」）| 跳幅 | **+4 pp** |
| Status | 🟢 邊際大幅縮減（Codex 已就位）|

### K. Export-brief 模式（設計系統作外部 AI prompt brief）

維持單獨：K3

> **v3.1 升級**：用戶環境含 Codex（OpenAI Codex CLI），理論已支援 GPT image 生成。K3 從「準備好給用戶手動餵 ChatGPT 端」升級為「**可作為 Codex 端 image-gen 流程的直接 prompt brief**」——paradigm 不再是「跨工具邊界手動」，而是「同環境內 inline 調用」。**Status 升級為 🔴 priority**，可能提前到 M3 或 M4。

| 切面 | 內容 |
|------|------|
| 機械 | `/baransu:design export-brief` 子模式：打包 DESIGN.md + tokens.css + design-cores 結構為單一 prompt-ready text + (v3.1) 預留 Codex CLI / MCP bridge hook |
| 工藝 | 自動引用 F 的 hex 理據 / J 的負面尾巴 / G 的 editorial 規格作 brief payload |
| Enables | **對應 Kami「references/ 整資料夾餵 ChatGPT Images 2.0」工作流** + **Codex GPT image 端 baransu-style 生圖** —— 設計系統 cross-tool 可復用 |
| 工程量 | 中（v3.1: 加 Codex bridge prompt template 為 +1 ref doc）| 跳幅 | **+4 pp**（可能 +1 pp from Codex integration） |
| Status | 🔴 paradigm 革新（v3.1 升級為高優先；F + J 前置 → 但 G5/J 也因 Codex 變可達） |

### L. EN/CN 模板分離

維持單獨：K5

| 切面 | 內容 |
|------|------|
| 機械 | `long-form-en.html` variant；slide-cores EN variants |
| 工藝 | Charter typography stack for EN；中文 TsangerJinKai02 留 zh path |
| Enables | **對應 Kami `*.html` / `*-en.html` 雙模板** —— 跨語言 fidelity |
| 工程量 | 小 | 跳幅 | **+2 pp** |
| Status | 🟢 |

### M. `oklch()` 妥協明示（與 WeasyPrint 對接記錄）

維持單獨：V9

| 切面 | 內容 |
|------|------|
| 機械 | DESIGN.md §2 加 footnote |
| 工藝 | 雙語標記 `--accent` 旁邊 `oklch(0.45 0.09 248)` 對照 |
| Enables | 未來改 Chromium-print pipeline 時可遷移；advisory 性質 |
| 工程量 | 小 | 跳幅 | **+0.5 pp** |
| Status | 🟢 advisory |

---

## Internal Debt 軌（**不算對標分數**，但要做）

| ID | 內容 | 工程量 |
|----|------|--------|
| **M1** | v1.3 handoff 收尾：swiss-smoke-test fixture regen + 三 preset E2E full pass | 中（需實跑） |
| **M2** | `design-token-resolver.md` + `golden-template.html` v1.3-aware 升級（兩檔仍 v1.2 wording / Kami-only） | 小 |
| **M3** | SKILL.md 步驟整數編號統一化（移除 `### 0.5` / `### 0.6` fractional；改為純整數 0, 1, 2, ...）。本次 v1.3 重構過程中產生的數字 cosmetic drift；不影響功能但讓 reader 找段落困難 | 小（兩 skill SKILL.md 各 ~10 處 renumber） |

**為什麼不算對標**：M1/M2 是 plugin internal consistency，**不直接影響「能否產出對標 baseline 的 artifact」**。但 v1.3 不收尾後續 work 容易 cascade 失敗，仍須做。

---

## Roadmap Milestones（修正後的數字）

### → 65%（從 ~50% + ~15 pp）「初稿即可用」

| 動作 | 跳幅 | Why |
|------|------|-----|
| **B** /book pre-interview | +10 | 最大 CP，30 行 edit |
| **A**（部分） chevron 遷移 + 節點寬白名單（不含 12 diagram complete） | +6 | spec/impl drift 修復 |

合計 **+16 pp** → ~66%。**單 session 可完成**（B 是搬訪談 pattern，A 部分是 surgical edit）。

### → 75%（從 65% +9-10 pp）「視覺辨識度復原 + 紙質感對齊」

| 動作 | 跳幅 | Why |
|------|------|-----|
| **C** 紙質感 spec/impl 對齊 | +4 | 修 hairline + shadow drift |
| **I** Fact-Verification | +3 | 30 行 SKILL.md edit |
| **F** Prompt Guide §9 強化 | +2.5 | reproducibility |

合計 **+9.5 pp** → ~75%。

### → 82%（從 75% +7 pp）「Slide layout 多樣性 + 印刷學詞彙」

| 動作 | 跳幅 | Why |
|------|------|-----|
| **D** slide-cores 擴張 + modular scale | +10（取 7） | 需分批做 |
| **G** Editorial 三件套（為 H 前置） | +4（取 4） | dropcap / curly / widow |

合計 **+7-8 pp** → ~82-83%。

### → 90%（從 82% +8 pp）「多文件類型 + 圖片 governance」

| 動作 | 跳幅 |
|------|------|
| **H** 新文件 schema × 4 | +7 |
| **A**（剩餘）12 diagram complete dogfood-driven | +6（取 3） |
| **E** Checklist 5→15 dogfood 累積 | +6（取 2） |

合計 **+12 pp** → ~90-94%。

### → ~95%（理論上限）「Paradigm 整合」

| 動作 | 跳幅 |
|------|------|
| **J** 圖片 Governance | +4 |
| **K** Export-brief 模式 | +4 |
| **L** EN/CN 分離 | +2 |
| **M** oklch footnote | +0.5 |

合計 **+10 pp** → ~95-100%。

> **「100%」不可達**：對標兩 baseline（Kami 橫向 8 文件 + guizang/huashu PPT 縱深）在 K6「單一視覺深度 vs 三 preset 並行」等軸**互斥拉扯**。對 baransu 作為 Claude Code skill plugin 中的設計子模組，**90-95% 是合理理論上限**。

---

## 視覺化時間軸

```
~50% (now)
  │
  ├─ B + A(部分)              ──→ 66%  「初稿即可用」
  │
  ├─ C + I + F                ──→ 75%  「視覺辨識度 + 紙感對齊」
  │
  ├─ D + G                    ──→ 82%  「Slide 多樣 + 印刷學詞彙」
  │
  ├─ H + A(剩) + E            ──→ 92%  「多文件類型 + 圖片 governance」
  │
  └─ J + K + L + M            ──→ ~95% 「Paradigm 整合（理論上限）」
```

---

## Critical Path（按 ROI × 戲劇性 × 工程量排序）

1. **B**：30 行 edit，+10 pp。**單一最高 CP**。
2. **A 部分**（chevron 遷移 + 節點寬白名單）：surgical edit，+6 pp，修最戲劇性 spec/impl drift bug。
3. **C**：surgical edit，+4 pp，紙質感工藝復原。
4. **I**：30 行 SKILL.md edit，+3 pp。
5. **G**：中等工程量，+4 pp，**H 的前置**。
6. **D**：中等工程量，+10 pp，多 layout 視覺擴張。
7. **H**：大工程，+7 pp，跨文件類型。
8. **A 剩餘**（12 diagram complete）：dogfood-driven。
9. **E**：dogfood-driven。
10. **F / J / K / L / M**：paradigm 整合，邊際大。

---

## 立即可動：**B + A(部分) + C**（單 session 三個 surgical edit 組合）

| 動作 | 檔案 | 工程量 |
|------|------|--------|
| **B** /book pre-interview gate | `plugins/baransu/skills/book/SKILL.md` Stage 0.5-1 之間 | ~30 行 edit |
| **A 部分** chevron 遷移 | `plugins/baransu/skills/book/references/svg-rendering-rules.md §4.3` + `references/golden-template.html` SVG `<marker>` | ~15 行 edit |
| **A 部分** 節點寬白名單 | `svg-rendering-rules.md §4.5`（明列 `{128,144,160}`）+ `golden-template.html` SVG `<rect width="?">` 改三檔合規 | ~10 行 edit |
| **C** 0.5pt hairline + shadow 對齊 | `design/references/紙-preset/design-cores/long-form.html` + `book/references/golden-template.html` `.paper` + 紙 `DESIGN.md §4` token | ~10 行 edit |

合計 ~65 行 edit。**做完 ~66% → 70%，且 Kami 視覺簽名（chevron / 三檔節點寬 / 紙感 hairline / 七問澄清前置）全部到位**。

---

## Fact-check 紀錄（v3 round，2026-05-12）

**對 raw material grounding 結果**：

| Item | 結論 |
|------|------|
| Kami 8 文件類型 + 14 SVG 圖表 | ✅ verified（README L363）|
| Kami `#1B365D` / `#f5f4ed` / 無 second accent | ✅ verified（README L367-368）|
| Kami TsangerJinKai02 / Charter / YuMincho | ✅ verified（README L375）|
| Kami「references/ as brief」+ ChatGPT Images 2.0 | ✅ verified（README L379-393）|
| Kami chevron / marker bug 細節 | ✅ verified（`references/diagrams.md` L86，連 path data `M2 1 L8 5 L2 9` 都對）|
| Kami 節點寬 128/144/160 三檔 | ✅ verified（`diagrams.md` L79；bonus: viewBox<360 可壓 2 tier）|
| Kami focal 1-2 個 | ✅ verified（`diagrams.md` L49；bonus: focal fill `#EEF2F7`）|
| Kami 4 倍數座標 | ✅ verified（`diagrams.md` L78）|
| guizang 22 layout (S01-S22) | ✅ verified（README L106/483）|
| guizang validate-swiss-deck.mjs / swiss-layout-lock.md | ✅ verified |
| guizang `object-position: center 35%` | ✅ verified（README L544/852/2012）|
| guizang `checklist.md` 523 行 + P0/P1/P2/P3 四層 | ✅ verified（gh api 抓 raw 行數）|
| huashu 21 references | ✅ verified（gh api: animation-best-practices.md / animations.md / ... = exactly 21）|
| huashu Core Asset Protocol 5 步 | ✅ verified（README）|
| huashu 5-dim critique / Junior Designer / 20 design philosophies | ✅ verified |

**WIP v2 → v3 修正**：
- E1：guizang「47 layout」→ **22 layout (S01-S22)**；Gap D 跳幅下修為 +7-10 pp
- E2：「P0/P1/P2 三層」→ **P0/P1/P2/P3 四層**；Gap E 更新
- E3：「checklist 524 行」→ **523 行**（off-by-1）；Gap E 更新
- U1/U2/U3：原標「unverified」項全部 verified；Gap A 加入完整 Kami spec quote

## 完整 review 報告原檔

四輪 /review 完整 finding 在以下對話歷史段：

- 1️⃣ vs guizang/huashu：「review 花淑x誰的 ppt」回合（architecture-reviewer dispatched，7 Layer 估算）
- 2️⃣ vs tw93/Kami：「review tw93/Kami」回合（main session direct analysis，7 軸對標）
- 3️⃣ 視覺工藝層 audit：「視覺體驗 那些巧思」回合（general-purpose 套 style-reviewer rubric，13 個具體 visual craft gaps）
- 4️⃣ WIP self-audit：「以視覺為主 重新檢視 wip」回合（5 矛盾 + 9 整合建議，本 v2 重寫的依據）

本 WIP v2 為彙整版；具體 finding 引用與 hex / px / line 細節在原 review 報告。
