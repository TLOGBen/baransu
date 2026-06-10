# Anti-Patterns — 跨技能行為護欄

Cross-skill behavioral guardrails for all baransu skills and agents.

## 自治條款（Autonomy Clauses）

1. **收斂不堆積**：新條目進入前，必須先嘗試折入既有原則；禁止以近義詞另立新條。容器只能變深，不能變長。
2. **strip-provenance**：每條規則靠「防止什麼」掙得位置；不帶事故敘事、不附來源規模數字。規則若需要故事才站得住，就還不夠格收錄。

## 分層原則（Layering）

- **跨技能成立者**收錄於本容器：任何 skill / agent 都可能踩到的慣性。
- **技能專屬不變量**留在原處（CLAUDE.md Non-obvious Invariants 或各 SKILL.md），本容器不收錄、不複製 — 例如 `/ship` 的 `-D` 旗標、`DESIGN.md` vs `design.md` 大小寫語義、`plugin.json` 的 no-skills-array、execute 的 `failure_count` 計數規則。

## 首批條目

| 慣性 | 錯誤示範 | 正確做法 |
|------|----------|----------|
| 巢狀 skill 呼叫 | subagent 內呼叫 `/baransu:<skill>`，觸發 AskUserQuestion 或平行 Task | subagent depth = 1：所需語義直接內嵌於 agent 定義，不向外呼叫 skill |
| 憑記憶改檔 | 依先前輪次的 Read 結果直接 Edit/Write | Read-before-write：同一輪先 Read 再改；中間有其他操作即重讀 |
| 改測試遷就實作 | 修改既有通過的測試，讓新實作轉綠 | 修實作不修測試；唯有測試本身錯誤時才改測試 |
| 跳過紅燈直寫實作 | 未確認測試失敗（exit code ≠ 0）即開始實作 | 先寫失敗測試、確認確實失敗，再寫最小實作 |
| 語言慣例漂移 | skill 本文寫中文，或使用者輸出寫英文 | English body、繁體中文 user output；所有 skill 一體適用 |
| 改完不 bump 版本 | 發行內容已變更，`plugin.json` 版本原地不動 | 任何 distributed change 必同步 bump `plugin.json` 版本 |
