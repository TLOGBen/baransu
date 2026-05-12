# Test Strategy

> 本 spec 動的是純文檔 + 規格 + sanity script，不存在傳統 E2E（browser flow）。E2E 改為「**從 user prompt 到 baransu 產出 baseline-equivalent artifact 的端到端跑通**」；整合測試改為「**跨 skill / 跨 preset / 跨 sanity 腳本**」的協同驗證；單元測試改為「**每條 sanity rule / 每個 schema 規格 / 每個 SVG GATE**」的 isolated check。

---

## E2E 測試策略

每條對應一個 baseline-equivalent artifact，從用戶 prompt 走到產出 + sanity-pass。

| 場景 | 起點（user prompt） | 終點 | 對應 Criteria |
|------|-------------------|------|--------------|
| **E1：Kami 風 long-form 文件**（含 14 圖表類型至少 3 種、紙-stack shadow、dropcap、curly quotes） | `/baransu:book https://example.com/long-essay --format html` | `.claude/book/{slug}.html` + 所有 GATE-A 到 GATE-I 全 PASS + `editorial-sanity.sh` PASS | C1 / C4 |
| **E2：guizang-equivalent Swiss PPT 22 layout 覆蓋** | `/baransu:book {topic} --format ppt --style swiss`，要求 deck ≥ 10 slide，涵蓋 timeline / process / testimonial / stat-hero 至少 1 layout 一次 | `.claude/book/{slug}.html` + `validate-swiss-deck.mjs` PASS | C3 / C5 |
| **E3：紙 preset Resume 雙語產出** | `/baransu:design preset 紙` apply 後，手動 copy `schemas/resume.html` + `resume-en.html` 並填內容 | 兩檔通過 `紙-sanity.sh` + `editorial-sanity.sh` + 含 `object-position: center 35%` | C2 / C4 |
| **E4：Export-brief 餵 Codex 端跑通**（人工） | `/baransu:design export-brief` 對紙 preset | brief 寫入 `.claude/design/brief-kami-{date}.md`，純文字格式可貼到 Codex CLI 端做 image-gen prompt，內含三段（§9 hex + §J 負面尾巴 + §G editorial） | C7 |
| **E5：huashu-equivalent Fact-verify 阻擋 hallucinated 規格** | `/baransu:book` 對含「Linear MCP v3.4.7 release 2025-09-15」之類**虛構**字串的長文 | Stage 2A 觸發 WebSearch verify → 找不到 → AskUserQuestion 阻擋 | C6 |
| **E2.5：三 golden-template 變體 cross-preset 跑通** | 對 `golden-template.html` / `golden-template-swiss.html` / `golden-template-gd.html` 三檔分別跑 `swiss-smoke-test.sh` 對應 fixture | 三檔皆 GATE A-K 全 PASS | C3 + REQ-010 M2 |
| **E6：100% Criteria pass run baseline-parity-score** | repo clean，跑 `python3 scripts/baseline-parity-score.py` | stdout 印 11 行 C1-C11 結果 + 末行「Overall: ≥ 90.0%」+ exit 0 | C12 + 全部 C1-C11 acceptance gate |

---

## 整合測試策略

跨 skill / 跨 preset / 跨 script 邊界的驗證。

| 測試目標 | 涉及層 | 關鍵驗證點 |
|---------|--------|-----------|
| **三 preset 一致性對齊** | 紙-sanity.sh / swiss-sanity.sh / google-design-sanity.sh | 三 sanity 對同等 lint rule（editorial 三件套 / SVG node-width 白名單 / class-prefix）都生效；任一 preset 缺對應 rule = 整合 fail |
| **DESIGN.md ↔ tokens.css ↔ design-cores 三層 hex 同步** | 規格 / 模板 / sanity | DESIGN.md §2 列的 hex 必須與 tokens.css 對應 CSS variable 值一致；design-cores HTML 中所有 hard-coded hex 必須 ∈ DESIGN.md §2 範圍 |
| **export-brief ↔ tokens.css 動態解析** | /design SKILL.md / tokens.css | brief 輸出的 hex 從當下 preset 的 tokens.css 解析（不 hard-code）；切 preset 後再跑 brief，輸出的 hex 對應跟著切 |
| **/book Stage 3 ↔ 三 preset design-cores 切換** | /book SKILL.md / design-cores | `--style` 旗標可在三 preset 間切換；切換後產出的 long-form HTML class prefix 對應切換（kami-* / swiss-* / gd-*） |
| **validate-output.ts GATE-D marker integrity ↔ chevron 規格** | validator / golden-template | 新增的 chevron marker（v1.3.1 已 land）defs 與 marker-end refs 雙射；無 dangling、無 unused |
| **baseline-parity-score 加權計算正確** | score 腳本 / 全 sanity 鏈 | C1-C11 加權總和 = 1.0；任一條 fail 時對應百分比扣除正確；機械跑 100% pass 的 fixture set 應 score = 100% |
| **Stage 整數化 ↔ SKILL.md 內部 cross-reference** | book / design SKILL.md | renumber 後內部「見 Stage 2.5」之類 cross-ref 全部跟著改；無 broken ref（grep 不到斷裂 anchor） |
| **Checklist sanity 結構驗證** | slide-checklist.md / sanity scripts | P0-P3 各層計數合規（≥ 4/4/4/2）+ 每條三 sub-heading（現象 / 根因 / 做法）grep 命中 + `source:` metadata 非空非 TBD（補 TASK-cg-01） |
| **design-token-resolver 三 preset hex 範例存在** | book/references/design-token-resolver.md | grep 三 preset hex 對照表存在（補 TASK-ct-03 驗證錨） |
| **三 golden-template 變體 swiss-smoke-test 全綠** | golden-template{,-swiss,-gd}.html | 三檔皆能跑 validate-output.ts 全 GATE PASS（補 TASK-ct-04 驗證錨；測試名稱 E2.5） |
| **GATE-D marker integrity ↔ chevron 規格**（已 v1.3.1 land；列入整合僅作 regression watch，無新 task） | validator / golden-template | 沿用 v1.3.1 既有實作；本 spec 不新增 task，但 score 腳本仍會驗證 |

---

## 關鍵邊界條件

| # | 邊界條件 | 對應 REQ |
|---|---------|---------|
| **B1** | 任一 SVG 圖節點寬有第 4 種非白名單值（e.g. 192）即 fail | REQ-001 Scenario 3 |
| **B2** | 焦點節點 `data-role="focal"` 數量 > 2 即 fail | REQ-001 Scenario 4（4 倍數 + focal cap 同 GATE-A） |
| **B3** | viewBox < 360 時節點寬僅用 1 檔（全 128）= fail（仍須 2 檔保持節奏） | REQ-001 Scenario 3 |
| **B4** | viewBox < 360 時節點寬用 3 檔 = fail（超出例外允許範圍） | REQ-001 Scenario 3 |
| **B5** | 三 preset 任一 preset 缺新 schema = REQ-002 整體 fail（不能只紙 preset 有 6 schema） | REQ-002 Scenario 1 |
| **B6** | en variant 含 zh 字體 stack（`Noto Serif TC` 等）= fail | REQ-002 Scenario 2 |
| **B7** | Portfolio / Resume 含 `<img>` 但無 `object-position` 屬性 = sanity fail | REQ-002 Scenario 3 |
| **B8** | 任一 preset slide-cores 數量 ≠ 22（含多 / 少）= REQ-003 fail | REQ-003 Scenario 1 |
| **B9** | Modular scale 仍含 v1.2 的 2.2× / 1.24× 舊比例 = fail | REQ-003 Scenario 3 |
| **B10** | `text-wrap: pretty` 只在部分 design-core 出現，缺一即 fail | REQ-004 Scenario 1 |
| **B11** | dropcap 計算高度 != 3 × line-height（含 ±0.5 容差） = fail | REQ-004 Scenario 2 |
| **B12** | Template HTML 內含未轉換的 straight `"`（非 HTML attribute 位置） = fail | REQ-004 Scenario 3 |
| **B13** | Checklist 總條目 < 15 或 > 20 = fail | REQ-005 Scenario 1 |
| **B14** | 任一條目缺「現象 / 根因 / 做法」三欄之一（即少於三 sub-section） = fail | REQ-005 Scenario 2 |
| **B15** | Checklist 條目 source = 空 / "TBD" / 純造句 = fail（必須 dogfood / huashu / kami 三來源之一） | REQ-005 Scenario 3 |
| **B16** | Fact-verify 對命中字串走 WebSearch 但找到 0 結果，腳本未 AskUserQuestion 即繼續 = fail | REQ-006 Scenario 1 |
| **B17** | Core Asset Protocol 跳步（如 user 未確認需求就 freeze）= fail | REQ-006 Scenario 2 |
| **B18** | image-prompts.md prompt 結尾缺 `no logo` 字符串（部分否定 = 視同 fail）= fail | REQ-006 Scenario 3 |
| **B19** | export-brief 對三 preset 任一 preset 跑 crash / 輸出空 brief = fail | REQ-007 Scenario 2 |
| **B20** | Brief 內容含寫死 Kami `#1B365D`（即使當下 preset 是 swiss `#002FA7`）= fail | 整合測試 #3 |
| **B21** | §9「我不是什麼」清單 < 5 條 = fail | REQ-008 Scenario 2 |
| **B22** | tokens.css 或 design-core HTML 內出現 `oklch(...)` = fail（advisory 只能在 DESIGN.md） | REQ-009 Scenario 2 |
| **B23** | swiss-smoke-test fixture 對 v1.4 新增 layout 缺對應 fixture = M1 fail | REQ-010 Scenario 1 |
| **B24（advisory）** | SKILL.md 內仍含 `### 0.5` / `### 2.5` 章節 heading = 可讀性 advisory（**非** hard fail）；score 加權 0；release notes 提及但不卡 v1.4.0 release | REQ-010 Scenario 3（語義降級為可讀性提升） |
| **B25** | baseline-parity-score crash（exit 2）或 < 90% = E2E gate fail | REQ-012 Scenario 2 |
| **B26** | C12 自評腳本算自己 = circular self-evaluation fail（必須只算 C1-C11） | REQ-012 Scenario 3 |
| **B27** | `/baransu:design export-brief` 在無 git project root 環境下未走 fallback to cwd 或未印 stderr warning「未找到 git root，使用 cwd」 = fail | design.md 錯誤處理表「跨工具層 export-brief 找不到 project root」對應 |
| **B28** | swiss-smoke-test 加新 layout fixture 時，validate-fixtures/ 目錄缺對應 fixture 但 swiss-smoke-test.sh 列入 iteration list = fail（M1 staleness 邊界） | REQ-010 Scenario 1 對應 |

---

## 測試 fixture 與工具

- **新增 fixture**：`book/scripts/validate-fixtures/` 加 22 layout 對應 fixture（紙 / swiss / gd 各 22 個）+ 6 new schema fixture 各 zh/en 兩份
- **新增腳本**：
  - `editorial-sanity.sh`（dropcap line-count / curly-quote-presence / widow-orphan stub）
  - `validate-swiss-deck.mjs`（對標 guizang validate-swiss-deck）
  - `baseline-parity-score.py`（自評腳本）
- **既有腳本擴展**：
  - `紙-sanity.sh` / `swiss-sanity.sh` / `google-design-sanity.sh` 加 editorial / object-position lint
  - `validate-output.ts` 加 GATE-H editorial-sanity / GATE-I export-brief-presence-check
- **跑 mode**：所有腳本支援 `--all-presets` 旗標 = 三 preset 並聯跑；CI 模式則用 `--ci` 印 machine-readable JSON

---

## 不測試的範圍（明確排除）

- 任何 production browser 行為（無 frontend dev）
- 第三方工具（Codex CLI / ChatGPT Images 2.0）的端到端跑通——E4 只到「brief 文件寫出 + 人類肉眼確認結構合理」即可
- Performance test（不關心 sanity 跑多快；只要 CI < 60s 即可）
- Cross-OS test（baransu plugin 開發目標就是 Linux / macOS shell；Windows 走 WSL，由用戶自行 / 不入 v1.4 gate）
