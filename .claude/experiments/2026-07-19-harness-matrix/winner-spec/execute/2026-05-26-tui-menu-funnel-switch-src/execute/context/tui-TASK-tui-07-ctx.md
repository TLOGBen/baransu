Goal: |
  在 CLAUDE.md 既有 "Presentation — handlers compose facades" 一節後補一段 doc-debt，
  明寫 TUI screen 屬於 handler 等價層、可跨 context；並記下 `Cli.cmd: Option<Cmd>`、None → menu 的入口分流。
  屬於 goal.md 中明列的 In-scope 文件變更：「CLAUDE.md：補一節「TUI screen = handler 等價」doc-debt（一段話即可、不展開）」。

Requirements: |
  非 REQ 編號追溯——goal.md Out-of-scope 註腳的 doc-debt（non-blocking 但建議順手）。
  關聯背景（不需重述於 CLAUDE.md）：
  - REQ-001（入口分流）：`Cli.cmd: Option<Cmd>`、None → handlers::menu::handle 進主菜單；既有子命令維持
  - C9 Layer invariant：catalog/ 與 library/ 內部不互呼 facade（grep 零命中）

Scenarios: |
  N/A — 本 task 為 doc-only，無 Given-When-Then scenario；驗收靠 `git diff CLAUDE.md`。

Task: |
  TASK-tui-07: CLAUDE.md doc-debt 補一節「TUI screen = handler 等價」

  目標：在 CLAUDE.md 既有 "Presentation — handlers compose facades" 一節後補一段，
  明寫 TUI screen 屬於 handler 等價層、可跨 context；以及記下「`Cli.cmd: Option<Cmd>`、None → menu」入口分流。

  驗收標準：
  - [ ] CLAUDE.md 補完
  - [ ] 一段話、不超過 10 行；不畫圖
  - [ ] `git diff CLAUDE.md` 顯示新增段落、無誤排版

  步驟：
  - [ ] Read CLAUDE.md，定位 "Presentation — handlers compose facades" 一節結尾（在 "### TUI (`src/presentation/reader.rs`)" 之前）
  - [ ] 於該節後插入新段落，內容含以下要點（不超過 10 行、不畫圖）：
    1. TUI screen 屬 handler 等價層（不是新一層）
    2. 每個 screen 等同一個 cross-context use case 組合點：可同時 import catalog::facade + library::facade（與 CLI handler 同層、同權限）
    3. layer invariant 不變：catalog/ 與 library/ 內部不互呼 facade（grep 仍零命中）
    4. 補一句「Cli.cmd: Option<Cmd>；無參數時走 handlers::menu::handle 進 TUI 主菜單；既有子命令維持」
  - [ ] 確認排版（標題層級、項目符號、行距）與 CLAUDE.md 既有風格一致
  - [ ] `git diff CLAUDE.md` 自查

Design: |
  N/A — 本 task 不動程式碼；design.md 中關於 screen / handler / facade 分層的論述為這段 doc 的依據，但無需引入新設計。
  關鍵分層事實（已在 CLAUDE.md 主表中、本段只需呼應、不重複展開）：
  - 五層：mod.rs(PL) / facade / service / dao / handlers (presentation)
  - handlers 是跨 context use case 唯一組合點
  - backup 是 4 層（無 dao），透過 library::facade 取資料
  本 task 補的就是「TUI screen 也屬 handlers 層」這條既有事實的明文化。

Test: |
  無自動化測試；驗收為人工檢視：
  - `git diff CLAUDE.md` 顯示新增段落
  - 段落不超過 10 行、無圖
  - 涵蓋四個要點（handler 等價層、cross-context 組合點、layer invariant 不變、Cli.cmd 入口分流）
  - Markdown 排版乾淨（無破標題層級、無孤立 code fence）

Constraints:
  - 唯讀範圍：`.claude/analyze/` 下任何檔案皆不得修改
  - 修改範圍：只動 `CLAUDE.md`，不動程式碼、不動其他 .md
  - 段落長度上限：10 行
  - 禁止畫圖（不得新增 ASCII / mermaid / 表格圖）
  - layer invariant 必須在文字中明點：catalog/ 與 library/ 內部不互呼 facade（grep 零命中）
  - 入口分流文字必須明點：`Cli.cmd: Option<Cmd>`；None → handlers::menu::handle 進 TUI 主菜單；既有子命令維持
  - TUI screen 定位必須明點：handler 等價層（不是新一層）、與 CLI handler 同層同權限、可同時 import catalog::facade + library::facade
  - 插入位置：CLAUDE.md 既有 "Presentation — handlers compose facades" 一節之後（"### TUI (`src/presentation/reader.rs`)" 之前）
  - 不得重寫既有段落；採新增方式

Files:
  - /home/vakarve/project/others/NovelReader/CLAUDE.md  (modify — 在 "Presentation — handlers compose facades" 一節後新增 ≤10 行段落)
