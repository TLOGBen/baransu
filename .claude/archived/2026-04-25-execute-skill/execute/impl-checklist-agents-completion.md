# Impl Checklist: agents-completion

前置群組：無

---

## TASK-agents-completion-01: 建立 e2e-fix-agent.md
需求追溯：REQ-005, REQ-006
- [ ] 文件存在於 `plugins/baransu/agents/e2e-fix-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（E2E 失敗報告 + test.md 的 E2E 策略）
- [ ] 通用原則說明修復範圍：只修復 E2E 失敗的程式邏輯，不修改 test.md 的測試策略
- [ ] 通用原則說明輸出格式（修復描述 + 修復結果 ✅/❌）
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不更改 test.md 的 E2E 測試策略以讓測試通過」
Review 結果：
備註：

---

## TASK-agents-completion-02: 建立 final-review-agent.md
需求追溯：REQ-005, REQ-006
- [ ] 文件存在於 `plugins/baransu/agents/final-review-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明驗收方式：逐條 REQ-XXX 確認是否有對應的綠燈測試
- [ ] 通用原則說明輸出格式（Coverage Report：REQ-XXX → 測試檔案:行號 或 ❌ 未覆蓋）
- [ ] 通用原則說明何時回傳「需要 Final-Fixer」（有任何 REQ-XXX 未覆蓋）
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不修改現有測試以讓 coverage 看起來通過」
Review 結果：
備註：

---

## TASK-agents-completion-03: 建立 final-fixer-agent.md
需求追溯：REQ-005, REQ-006
- [ ] 文件存在於 `plugins/baransu/agents/final-fixer-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（Coverage Report + requirement.md + design.md）
- [ ] 通用原則說明修復範圍：只針對 Coverage Report 中 ❌ 的 REQ-XXX 補充測試和最小必要實作
- [ ] 通用原則說明完成後主動回報「已補充 REQ-XXX 的測試，請重跑 Final-Review」
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不修改已通過的 REQ-XXX 的測試」
Review 結果：
備註：

---

## TASK-agents-completion-04: 建立 merge-agent.md
需求追溯：REQ-003, REQ-006
- [ ] 文件存在於 `plugins/baransu/agents/merge-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（worktree 路徑清單 + 目標分支）
- [ ] 通用原則說明三種回報結果：✅ merge 成功且 Green 通過 / ⚠️ merge 成功但 Green 破壞（附失敗測試清單）/ ❌ 語意衝突（附衝突檔案和雙方修改意圖）
- [ ] 通用原則說明 Green 確認方式（執行測試指令，從 test.md 讀取）
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不自行解決語意衝突——回報即止，不擅自選擇任一方的實作」
Review 結果：
備註：
