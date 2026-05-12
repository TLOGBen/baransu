# Goal

## 目標（Goal）

把 baransu `/design` + `/book` 兩 skill 從目前 ~50% baseline-parity（對 `op7418/guizang-ppt-skill` / `alchaincyf/huashu-design` / `tw93/Kami` 三 baseline）提升到理論上限 ~95%，方式是分四個 milestone 落實 WIP roadmap 內 A–M 13 個 gap + M1/M2/M3 三項 internal debt，使任何用戶以 baransu plugin 為唯一設計工具，都能產出與三 baseline 等價的 artifact（PPT slide / editorial 印刷品 / Kami 風文件系統 / 圖表）。

## 驗收標準（Criteria）

可觀察、可由 agent 機械判定：

- [ ] **C1 — Kami 視覺簽名落地**：14 種 SVG 圖表（architecture / flowchart / sequence / state / er / timeline / swimlane / quadrant / nested / tree / layers / venn / pyramid + 1 fallback）全數 `status: complete`（含 example HTML），且每張 SVG 通過 Kami `references/diagrams.md` 規格——chevron stroked marker + 節點寬白名單 `{128,144,160}`（含 `viewBox<360` 2-tier 例外）+ focal `#1B365D` stroke / `#EEF2F7` fill + 4 倍數座標。
- [ ] **C2 — 多文件 schema 覆蓋**：`紙-preset/` 含 8 個獨立 schema（Long Doc + Slides 已有；新增 Resume / Portfolio / One-Pager / Letter / Equity Report / Changelog 6 種），每種有對應 long-form variant `.html` 模板 + zh / en 雙語版本。
- [ ] **C3 — Slide 多樣性對齊 guizang 22 layout**：三 preset（紙 / swiss / google-design）`slide-cores/` 各含 22 個 Swiss-locked layout（S01–S22，含 timeline / process / testimonial / agenda / stat-hero / icon-grid / table-heavy / before-after 等），通過 `validate-swiss-deck.mjs` 等價檢查。
- [ ] **C4 — 印刷學三件套生效**：`tokens.css` + 三 preset `design-cores/` 全面採用 `text-wrap: pretty` + `.dropcap` 3-line drop + curly quotes（`U+201C` / `U+201D`），且通過新增的 `editorial-sanity.sh` 三項檢查（dropcap line-count / quote-curly / widow-orphan）。
- [ ] **C5 — Slide checklist 對齊 guizang 523 行**：`slide-checklist.md` 從 5 條擴張到 15-20 條，分 P0/P1/P2/P3 四層（P0 含 `0-S` / `0-A` / `0-B` 子前綴），每條三欄（現象 → 根因 → 做法）。
- [ ] **C6 — 圖片 governance 整套**：`/book` Stage 2A 對「具體產品 / 版本 / 人名」段強制 `WebSearch` 驗證；新增 Core Asset Protocol 4 步（ask → generate-via-Codex OR search → verify → freeze）+ 每 preset 各自的 `image-prompts.md` 含負面尾巴 `no title, no footer, no page chrome, no logo, no border`。
- [ ] **C7 — Export-brief 子模式可用**：`/baransu:design export-brief` 子指令打包 DESIGN.md + tokens.css + design-cores 結構為單一 prompt-ready text，可直接餵 Codex CLI / ChatGPT Images 2.0 端做 cross-tool image generation；prompt brief 自動引用 §9 hex 理據 / §J 負面尾巴 / §G editorial 規格。
- [ ] **C8 — AI Prompt Guide §9 reproducibility**：三 preset 各自 `DESIGN.md §9` 完整含（a）焦點節點上限 1-2 個（b）`#1B365D` / preset accent hex 設計理據（c）allowed contradictions（「我不是什麼」段，至少 5 條 "no X"）。
- [ ] **C9 — `oklch()` advisory 落地**：三 preset `DESIGN.md §2` 加 `oklch()` footnote，每個 accent token 旁標 `oklch(...)` 等價值；不改現有 hex 為主規格。
- [ ] **C10 — v1.3 internal debt 收尾**：M1（swiss-smoke-test fixture regen + 三 preset E2E full pass）/ M2（design-token-resolver.md + golden-template.html v1.3-aware 升級）/ M3（SKILL.md 步驟編號整數化）全部完成；CI / smoke test 全綠。
- [ ] **C11 — plugin 升版**：`plugins/baransu/.claude-plugin/plugin.json` 從 `1.3.1` 升至 `1.4.0`（minor bump 表示 baseline-parity milestone）。
- [ ] **C12 — Production-parity 自評腳本**：新增 `scripts/baseline-parity-score.py` 對三 baseline 各算 mechanical / craft 分軸分數，能輸出單一加權 % 數字，run 一次即跑完 11 項 sanity check 並印 ~95% target hit/miss。

## 範圍（Scope）

### 包含（In scope）

- WIP 內 A-M 全 13 gap 的 spec 落地（含 mechanical 骨架 + craft 工藝兩面）
- M1 / M2 / M3 三項 internal debt 收尾
- 三 preset（紙 / swiss / google-design）跨 preset 一致性對齊
- 三 baseline 對標的視覺簽名、印刷學詞彙、layout 多樣性、checklist 防 regression
- Codex CLI bridge（用於 J 的 image-gen + K 的 export-brief 兩處）以 prompt template 形式預留 hook，**不**實作 MCP server
- 新增 schema：Resume / Portfolio / One-Pager / Letter / Equity Report / Changelog（6 種）
- zh / en 雙語 template 分離
- Smoke test + sanity script 擴充（紙-sanity.sh / editorial-sanity.sh / baseline-parity-score.py）
- plugin.json v1.3.1 → v1.4.0 bump
- 「立即可動」B + A(部分) + C 已 landed（v1.3.1，commit 44f1c6a）視為前置完成，不重做但會被自評腳本一起 score

### 不包含（Out of scope）

- 任何 image-gen MCP server 實作 / 第三方 OAuth 整合 / API key 管理（純文字 prompt brief，由用戶手動帶到 Codex 端）—— 這超出 plugin 作為 skill 集合的職責
- 改 baransu plugin 以外的檔案（例如 user CLAUDE.md、其他 plugin、Claude Code core）
- 從零實作另一個 `/render` 或 `/figma-bridge` skill —— K3 是 `/design` 子模式而非新 skill
- 「對標 100%」—— 對 baransu 作為 Claude Code skill plugin，90-95% 是合理理論上限（剩 5-10% 涉及視覺深度 vs 三 preset 並行的根本互斥拉扯）
- /grade / /triage / /bridge 三 cron skill 的調整 —— 它們不屬於 design/book 軸
- DESIGN.md 根目錄檔（Swiss IKB）視覺改動 —— 它是 baransu plugin 自身的 UI 設計規格，與 design/book skill 產出能力是不同層次
- C1 dogfood 軌的 12 個 SVG example 全部由用戶手動產出 —— 本 spec 提供樣板 + 規格，但 12 example HTML 完整實作走 dogfood 累積（task 標記為 `dogfood-driven`，不卡 milestone gate）
