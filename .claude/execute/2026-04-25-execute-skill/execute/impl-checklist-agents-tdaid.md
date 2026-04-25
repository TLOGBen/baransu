# Impl Checklist: agents-tdaid

前置群組：無

---

## TASK-agents-tdaid-01: 建立 summarize-agent.md
需求追溯：REQ-006, REQ-003
- [ ] 文件存在於 `plugins/baransu/agents/summarize-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則明確列出 8 欄位（Goal/Requirements/Scenarios/Task/Design/Test/Constraints/Files）的提取規則
- [ ] 禁忌包含「不傳入整份文件；只提取與當前 task ID 直接相關的段落」
- [ ] 禁忌包含「不修改 Analyze spec 目錄下的任何文件」
- [ ] 無角色扮演描述（無 "you are a senior X" 語句）
- [ ] 固定 prompt（role + constraints）位於文件開頭，動態部分（task ID + spec paths）在後注入
Review 結果：
備註：

---

## TASK-agents-tdaid-02: 建立 impl-agent.md
需求追溯：REQ-003, REQ-006
- [ ] 文件存在於 `plugins/baransu/agents/impl-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則明確說明 Red gate（測試必須先失敗）和 Green gate（實作後測試必須通過）
- [ ] 通用原則說明 compile error 不計入 Green 失敗計數
- [ ] 通用原則說明 L/XL 任務的 Refactor 條件（Review 判定需要時，最多一次）
- [ ] 禁忌包含「不修改 Analyze spec 目錄下的任何文件」
- [ ] 禁忌包含「不在沒有失敗測試的情況下直接寫實作」
- [ ] 固定 prompt 在前，動態參數（ctx.md 內容 + worktree path）在後
Review 結果：
備註：

---

## TASK-agents-tdaid-03: 建立 review-agent.md
需求追溯：REQ-003, REQ-005, REQ-006
- [ ] 文件存在於 `plugins/baransu/agents/review-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則明確說明四層語義定義（advisory/packaged confirm/needs judgment/direct fix）及判斷準則
- [ ] 通用原則說明回傳格式：結構化的四層結果（tier + findings 清單），主 skill 可直接讀取判斷下一步
- [ ] 通用原則說明 Spec 矛盾（REQ-XXX 無法共存）的上報流程
- [ ] 通用原則說明填寫 `impl-checklist-{group}.md` 的規則
- [ ] 禁忌包含「不呼叫 /baransu:review skill（subagent 深度限制）」
- [ ] 禁忌包含「不自行修改 Analyze spec 文件」
- [ ] 禁忌包含「不合併多個 task 的 Review 結果為一次回報」
Review 結果：
備註：

---

## TASK-agents-tdaid-04: 建立 smart-friend-agent.md
需求追溯：REQ-004, REQ-006
- [ ] 文件存在於 `plugins/baransu/agents/smart-friend-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（task goal + spec 段落 + 兩次失敗摘要）
- [ ] 通用原則說明輸出格式（修正策略，供主 skill 傳給第 3 輪 Impl）
- [ ] 通用原則明確：若認為 spec 本身有問題，輸出「需升級用戶：spec 可能有矛盾」，不自行修改
- [ ] 禁忌包含「不自行實作任何程式碼」
- [ ] 禁忌包含「不修改 Analyze spec 文件」
Review 結果：
備註：
