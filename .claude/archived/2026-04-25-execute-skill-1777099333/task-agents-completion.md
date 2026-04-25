# Tasks: agents-completion
**前置群組**：無

這個群組包含 E2E、Final 階段及 Merge Point 的四個 agent-only skill 文件，與 agents-tdaid 群組完全獨立，可並行完成。

---

## TASK-agents-completion-01: 建立 e2e-fix-agent.md

**需求追溯**：REQ-005, REQ-006
**目標**：建立 E2E Fix subagent 的 agent-only skill 文件，使其在 E2E 失敗後接收失敗報告並嘗試修復，可被主 skill 多個並行派遣。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/e2e-fix-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（E2E 失敗報告 + test.md 的 E2E 策略）
- [ ] 通用原則說明修復範圍：只修復 E2E 失敗的程式邏輯，不修改 test.md 的測試策略
- [ ] 通用原則說明輸出格式（修復描述 + 修復結果 ✅/❌）
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不更改 test.md 的 E2E 測試策略以讓測試通過」

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以 E2E 修復工程師的角度，根據 E2E 失敗報告定位並修復整合問題」
- [ ] 撰寫 目標：「修復導致 E2E 失敗的程式碼問題，不修改測試本身」
- [ ] 列出通用原則：輸入格式、修復範圍限制、輸出格式、Monitor tool 使用說明
- [ ] 列出禁忌：不改 spec、不改測試、不改 test.md 策略

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `e2e-fix-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範

---

## TASK-agents-completion-02: 建立 final-review-agent.md

**需求追溯**：REQ-005, REQ-006
**目標**：建立 Final-Review subagent 的 agent-only skill 文件，使其驗證 requirement.md 的 100% 覆蓋率（每條 REQ-XXX 均有對應綠燈測試），並產出 Coverage Report。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/final-review-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明驗收方式：逐條 REQ-XXX 確認是否有對應的綠燈測試
- [ ] 通用原則說明輸出格式（Coverage Report：REQ-XXX → 測試檔案:行號 或 ❌ 未覆蓋）
- [ ] 通用原則說明何時回傳「需要 Final-Fixer」（有任何 REQ-XXX 未覆蓋）
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不修改現有測試以讓 coverage 看起來通過」

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以 Requirements Traceability 審查者的角度，驗證每條需求均有可追溯的測試依據」
- [ ] 撰寫 目標：「產出 Coverage Report，識別未被測試覆蓋的 REQ-XXX」
- [ ] 列出通用原則：逐條 REQ 驗證、Coverage Report 格式、不通過條件
- [ ] 列出禁忌：不改 spec、不改測試

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `final-review-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範

---

## TASK-agents-completion-03: 建立 final-fixer-agent.md

**需求追溯**：REQ-005, REQ-006
**目標**：建立 Final-Fixer subagent 的 agent-only skill 文件，使其根據 Final-Review 的 Coverage Report 補充缺失的測試與對應實作。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/final-fixer-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（Coverage Report + requirement.md + design.md）
- [ ] 通用原則說明修復範圍：只針對 Coverage Report 中 ❌ 的 REQ-XXX 補充測試和最小必要實作
- [ ] 通用原則說明完成後主動回報「已補充 REQ-XXX 的測試，請重跑 Final-Review」
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不修改已通過的 REQ-XXX 的測試」

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以 Coverage 修復工程師的角度，為缺失覆蓋的 REQ-XXX 補充最小必要的測試和實作」
- [ ] 撰寫 目標：「根據 Coverage Report 補充缺失測試，修復後回報供重跑 Final-Review」
- [ ] 列出通用原則：輸入格式、修復範圍限制、完成後回報格式
- [ ] 列出禁忌：不改 spec、不改已通過的測試

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `final-fixer-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範

---

## TASK-agents-completion-04: 建立 merge-agent.md

**需求追溯**：REQ-003, REQ-006
**目標**：建立 Merge subagent 的 agent-only skill 文件，使其在 Merge Point 執行 git merge、確認 Green、回報結果（成功/Green 破壞/語意衝突）。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/merge-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（worktree 路徑清單 + 目標分支）
- [ ] 通用原則說明三種回報結果：✅ merge 成功且 Green 通過 / ⚠️ merge 成功但 Green 破壞（附失敗測試清單）/ ❌ 語意衝突（附衝突檔案和雙方修改意圖）
- [ ] 通用原則說明 Green 確認方式（執行測試指令，從 test.md 讀取）
- [ ] 禁忌包含「不修改 Analyze spec 文件」
- [ ] 禁忌包含「不自行解決語意衝突——回報即止，不擅自選擇任一方的實作」

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以整合工程師的角度，執行 worktree merge 並驗證整合後的 Green 狀態」
- [ ] 撰寫 目標：「完成 git merge，確認 Green，回傳主 skill 可依據的結構化結果」
- [ ] 列出通用原則：輸入格式、三種結果格式、Green 確認步驟
- [ ] 列出禁忌：不改 spec、不擅自解決語意衝突

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `merge-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範
