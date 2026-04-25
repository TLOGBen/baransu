# Tasks: skill-execute
**前置群組**：agents-tdaid, agents-completion

主 skill 的 SKILL.md 在所有 agent-only skill 文件設計完成後才能撰寫，因為 SKILL.md 需要引用各 agent 的名稱、輸入格式和輸出格式。

---

## TASK-skill-execute-01: SKILL.md Stage 0–3（設定、DAG 分析、任務建立）

**需求追溯**：REQ-001, REQ-002
**目標**：撰寫 SKILL.md 的前三個 stage：spec 讀取與驗證、DAG 並行度計算 + XL/L/M 分類、Task Tool 建立 + 工作文件初始化。
**驗收標準**：
- [ ] `plugins/baransu/skills/execute/SKILL.md` 存在，前三個 stage 內容完整
- [ ] Stage 0 明確說明：讀取 spec 文件的順序、confirm.md 的寫入規則、缺少文件時的拒絕流程
- [ ] Stage 1 明確說明：從 task-*.md 的 `前置群組` 欄位建 DAG、計算最大並行前沿寬度、XL/L/M 分類表（≥4/2–3/1）、pre-scan 檔案重疊偵測
- [ ] Stage 2 明確說明：Task Tool Create 的呼叫時機（全部任務先建立再執行）、task 命名規範
- [ ] Stage 3 明確說明：task-map.md 的格式與寫入時機、impl-checklist-{group}.md 的初始化規則
- [ ] 所有 Stage 的指令說明對象是「執行此 skill 的 agent」（英文 body，繁中 output）

### 步驟

#### 起草 Stage 0（Spec 讀取與驗證）
- [ ] 寫入：讀取清單（五類文件）、缺失處理、confirm.md 格式
- [ ] 明確寫入：Analyze 文件為唯讀，禁止任何 Edit/Write

#### 起草 Stage 1（DAG 分析）
- [ ] 寫入：DAG 建立演算法（從 `前置群組` 欄位）
- [ ] 寫入：最大並行前沿計算方式（BFS 或拓撲排序）
- [ ] 寫入：XL/L/M 分類表 + 各分類的並行 Workflow 數量
- [ ] 寫入：pre-scan 偵測步驟（掃描所有並行群組的步驟涉及的檔案，檢查交集）

#### 起草 Stage 2（Task Tool 建立）
- [ ] 寫入：Task Tool Create 呼叫規則（全部建立 → 再開始執行）
- [ ] 寫入：task naming 規範（{group}-{task-id}）

#### 起草 Stage 3（工作文件初始化）
- [ ] 寫入：task-map.md 格式（Task Tool ID ↔ group/task-id ↔ checklist 路徑）
- [ ] 寫入：impl-checklist-{group}.md 初始化規則（從 task-{group}.md 驗收標準複製）

---

## TASK-skill-execute-02: SKILL.md Stage 4（TDAID Loop 編排）

**需求追溯**：REQ-003, REQ-004
**目標**：撰寫 SKILL.md 的核心 Stage 4：TDAID loop 的 while loop 控制邏輯，包含 subagent 呼叫序列、失敗計數、smart-friend 觸發、Merge point 處理。
**驗收標準**：
- [ ] Stage 4 內容完整描述單一 task 的執行序列（摘要→Impl→Review 的 while loop）
- [ ] 明確說明失敗計數規則：compile error 不計數；Review packaged confirm 以上計一次
- [ ] 明確說明 smart-friend 觸發條件：第 2 次失敗後（非第 1 次，非第 3 次）
- [ ] 明確說明 blocked 觸發條件：第 3 次失敗後立即標記，不再重試
- [ ] 明確說明 Merge point 流程：並行群組結束後 Merge Subagent → Green 確認 → 下一批
- [ ] 明確說明 Refactor stage：M 跳過，L/XL Review 判定需要時最多一次
- [ ] 明確說明 Spec 矛盾的升級流程
- [ ] Stage 4 的 subagent 呼叫格式一致（每次派遣說明傳入什麼參數、期望什麼回傳）

### 步驟

#### 起草主 while loop 結構
- [ ] 寫入：單一 task 的主 loop 結構（摘要 → Impl → Review → 判斷 → 繼續或重試）
- [ ] 寫入：失敗計數器的初始化和更新規則

#### 起草 smart-friend 分支
- [ ] 寫入：smart-friend 呼叫的觸發條件（failure_count == 2）
- [ ] 寫入：傳入 smart-friend 的參數格式（task goal + spec 段落 + 兩次失敗摘要）
- [ ] 寫入：smart-friend 輸出如何傳給第 3 輪 Impl

#### 起草 blocked 標記與繼續機制
- [ ] 寫入：blocked 的標記方式（Task Tool 狀態更新）
- [ ] 寫入：blocked 後繼續執行其他無前置依賴 task 的邏輯

#### 起草 Merge point 流程
- [ ] 寫入：偵測所有並行 Workflow 完成的時機
- [ ] 寫入：Merge Subagent 的呼叫規則和輸入格式
- [ ] 寫入：merge 後 Green 確認失敗時的回派邏輯

---

## TASK-skill-execute-03: SKILL.md Stage 5–7（E2E、Final-Review、結束）

**需求追溯**：REQ-005
**目標**：撰寫 SKILL.md 的後三個 stage：E2E 測試 + Fix 流程、Final-Review + Fixer 流程、final-report.md 產出與 session 結束。
**驗收標準**：
- [ ] Stage 5 描述 E2E 執行條件（所有 worktree 已 merge 回 main）
- [ ] Stage 5 描述：從 test.md 讀取 E2E 啟動命令 → Monitor tool 執行 → E2E Fix subagent 處理失敗
- [ ] Stage 5 描述：test.md 無啟動命令時跳過並記錄的規則
- [ ] Stage 6 描述 Final-Review subagent 呼叫規則與 Coverage Report 讀取
- [ ] Stage 6 描述 Final-Fixer 觸發條件（有 ❌ REQ-XXX）和重跑 Final-Review 的循環（最多一次）
- [ ] Stage 7 描述 final-report.md 的完整格式（task 狀態、E2E 結果、blocked 清單、Final-Review 結論）
- [ ] Stage 7 描述 session 結束時清理 worktree 分支的規則

### 步驟

#### 起草 Stage 5（E2E）
- [ ] 寫入：E2E 啟動命令讀取規則
- [ ] 寫入：E2E subagent 呼叫格式 + Monitor tool 使用方式
- [ ] 寫入：E2E Fix 觸發條件 + 並行派遣規則
- [ ] 寫入：E2E 跳過條件與 final-report 記錄方式

#### 起草 Stage 6（Final-Review + Fixer）
- [ ] 寫入：Final-Review subagent 呼叫格式
- [ ] 寫入：Coverage Report 讀取和 Final-Fixer 觸發條件
- [ ] 寫入：Final-Fixer 後重跑 Final-Review 的一次限制

#### 起草 Stage 7（產出與結束）
- [ ] 寫入：final-report.md 的完整格式模板
- [ ] 寫入：worktree 清理規則（通過 Final-Review 後清理分支）
- [ ] 寫入：session 結束的告知方式（繁中輸出給用戶）
