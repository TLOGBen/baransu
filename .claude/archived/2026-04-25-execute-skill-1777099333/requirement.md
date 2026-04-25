# Requirements

## REQ-001: Spec 讀取、驗證與 confirm.md 建立

**描述**：Execute 必須在啟動時驗證 Analyze spec 目錄的完整性，並建立 confirm.md 記錄讀取清單，確保 Analyze 文件全程唯讀。

### Scenarios

**Scenario 1: 正常啟動**
- **Given** execute 以 `.claude/analyze/2026-04-25-my-feature/` 路徑啟動，目錄中有完整的 goal.md/requirement.md/design.md/test.md/task-*.md
- **When** execute 讀取所有 spec 文件
- **Then** confirm.md 寫入 `.claude/execute/{date}-{slug}/execute/confirm.md`，列出所有已讀取檔案的路徑與時間戳
- **And** execute 繼續進行 DAG 分析

**Scenario 2: 找不到 Analyze 目錄**
- **Given** execute 以不存在的路徑啟動
- **When** execute 嘗試讀取 spec 目錄
- **Then** execute 拒絕執行，輸出「找不到 Analyze spec 目錄，請先執行 /baransu:analyze」

**Scenario 3: 目錄存在但 requirement.md 缺失**
- **Given** spec 目錄存在，但 requirement.md 或 task-*.md 其中之一缺失
- **When** execute 掃描目錄
- **Then** execute 識別缺失文件，記錄到 confirm.md，升級給用戶說明缺失的文件名稱

**Scenario 4: 任何 subagent 或主 skill 嘗試寫入 Analyze 文件**
- **Given** 某個執行路徑意外嘗試對 `.claude/analyze/` 目錄下的檔案執行 Edit/Write
- **When** SKILL.md 指令層偵測到此行為
- **Then** 立即停止，升級為結構性障礙，不修改 spec 文件

---

## REQ-002: DAG 並行度計算與執行工作文件建立

**描述**：Execute 必須從所有 task-{group}.md 的 `前置群組` 欄位建立依賴 DAG，計算最大並行寬度以分類 XL/L/M，用 Task Tool 建立所有任務追蹤項，並產出 task-map.md 與 impl-checklist-{group}.md。

### Scenarios

**Scenario 1: XL 任務（DAG 最大寬度 ≥4）**
- **Given** spec 目錄有 shared/data/service/api/integration 共 5 個群組，其中 shared 無前置、data/service 前置 shared、api 前置 service、integration 前置 api；第二批 data/service 並行寬度 2，但加上無前置的 shared 估算最大並行為 4（依具體 DAG）
- **When** execute 計算 DAG 最大並行前沿
- **Then** 分類為 XL，啟動 4 個並行 Impl Workflow，每個在獨立 gitworktree 中
- **And** Task Tool 建立所有群組 × task 的追蹤項，task-map.md 寫入群組→Task ID 對應

**Scenario 2: M 任務（DAG 寬度 1，純序列）**
- **Given** spec 目錄的所有群組形成一條線性鏈（每個群組只有一個前置），無任何並行機會
- **When** execute 計算最大並行前沿寬度
- **Then** 分類為 M，啟動 1 個 Impl Workflow 串行執行
- **And** 不建立額外 gitworktree（在主分支直接執行）

**Scenario 3: impl-checklist 建立**
- **Given** execute 完成 DAG 分析並建立 Task Tool 項目
- **When** execute 建立工作文件
- **Then** 每個群組產出一份 `impl-checklist-{group}.md`，內含從 task-{group}.md 驗收標準轉換的空白清單
- **And** task-map.md 記錄「哪個 impl-checklist 對應哪些 Task Tool ID」

**Scenario 4: 並行群組有檔案重疊**
- **Given** 兩個標記為可並行的群組，其 `步驟` 中涉及同一個共用檔案
- **When** execute 執行 pre-scan 偵測
- **Then** 將這兩個群組序列化（不並行），記錄到 task-map.md 的備註欄

---

## REQ-003: TDAID Impl Loop 的主 skill 控制

**描述**：Execute 的主 while loop 必須為每個 task 依序執行「摘要 subagent → Impl subagent → Review subagent」，Review 結果由主 skill 讀取後決定下一輪行動，不依賴 subagent 雙向通訊。

### Scenarios

**Scenario 1: 成功路徑**
- **Given** 主 skill 開始執行 TASK-shared-01
- **When** 摘要 subagent 提取 8 欄位 context（Goal/Requirements/Scenarios/Task/Design/Test/Constraints/Files）→ Impl subagent 寫失敗測試（Red）→ 實作直到綠燈（Green）→ Review subagent 審查
- **Then** Review 回傳 advisory 等級以下 → impl-checklist 標記 ✅ → 主 skill 推進至下一 task

**Scenario 2: Review 回傳 packaged confirm 以上 → 重派 Impl**
- **Given** Impl subagent 完成但 Review 回傳 packaged confirm 等級問題
- **When** 主 skill 讀取 Review 結果
- **Then** 計入一次失敗記錄，派新一輪 Impl subagent（攜帶 Review 問題摘要作為輸入）
- **And** 主 skip 繼續 while loop，等待新一輪結果

**Scenario 3: L/XL 任務的 Refactor stage**
- **Given** L 或 XL 任務，Review subagent 判定需要 Refactor（packaged confirm 等級的品質問題）
- **When** 主 skill 接收 Refactor 訊號
- **Then** 執行最多一次 Refactor，M 任務跳過此 stage

**Scenario 4: Merge point（並行 worktrees 收斂）**
- **Given** 並行的多個 Impl Workflow 已各自完成其群組的所有 task
- **When** 所有 worktree 到達 merge point
- **Then** 派 Merge Subagent 執行 merge，merge 完成後確認 Green
- **And** 若 merge 後測試不通過，回派 Merge subagent 修到好

---

## REQ-004: 結構性障礙偵測、smart-friend 介入與升級

**描述**：失敗 2 次後自動派 smart-friend subagent 做方向對焦；三種結構性障礙觸發時標記 blocked 並升級用戶，其他 task 繼續。

### Scenarios

**Scenario 1: 連續失敗 2 次 → smart-friend 介入**
- **Given** 同一 task 的 Impl subagent 連續失敗 2 次（Review 均為 needs judgment 等級）
- **When** 主 skill 累計失敗次數達 2
- **Then** 派 smart-friend subagent，傳入 task goal + 兩次失敗摘要 + 相關 spec 段落
- **And** smart-friend 使用 extended thinking 輸出修正策略，主 skill 以此策略派第 3 輪 Impl

**Scenario 2: 第 3 次仍失敗 → blocked**
- **Given** smart-friend 介入後的第 3 輪 Impl 仍被 Review 判定不通過（packaged confirm 以上）
- **When** 主 skill 計算累計失敗次數 = 3
- **Then** 標記此 task 為 blocked，升級給用戶（輸出明確的失敗原因與 smart-friend 的分析結論）
- **And** 在 final-report.md 的 blocked 清單記錄詳情，繼續執行其他無前置依賴的 task

**Scenario 3: Merge 衝突（人工語意判斷）→ blocked**
- **Given** 並行 worktrees merge 時 Merge Subagent 判定衝突無法自動解決（需要人工語意判斷）
- **When** Merge Subagent 回報無法解決
- **Then** 升級給用戶，在 final-report.md 記錄衝突詳情（哪個檔案、哪兩個 worktree、各自的修改意圖）

**Scenario 4: Spec 矛盾 → blocked**
- **Given** Review subagent 在執行中發現兩個 REQ-XXX 在現有設計下無法同時滿足
- **When** 主 skill 讀取此特殊 Review 結果
- **Then** 標記相關 task 為 blocked（原因：spec 矛盾），升級給用戶
- **And** 不嘗試自行修改 spec，明確說明哪兩個 REQ 衝突

---

## REQ-005: E2E 測試、Final-Review 與 final-report.md 產出

**描述**：所有 worktree merge 回 main 後執行 E2E 測試（含 Fix 路徑）；完成後執行 Final-Review（含 Fixer 路徑）；最終產出完整的 final-report.md。

### Scenarios

**Scenario 1: E2E 成功**
- **Given** 所有 worktree 已 merge 回 main，test.md 有 E2E 啟動命令
- **When** E2E subagent 執行 E2E 測試，Monitor tool 監控結果
- **Then** 全部通過，final-report.md 記錄 ✅ E2E 狀態

**Scenario 2: E2E 失敗 → E2E Fix subagent**
- **Given** E2E 測試有失敗案例
- **When** E2E Fix subagent（可派多個並行）嘗試修復
- **Then** 修復成功後重跑 E2E 確認；若修復失敗，final-report.md 記錄 ❌ 失敗原因與建議

**Scenario 3: E2E 啟動命令不存在**
- **Given** test.md 未標注 E2E 啟動命令
- **When** E2E stage 開始
- **Then** 跳過 E2E，final-report.md 記錄「E2E 跳過：test.md 未提供啟動命令」

**Scenario 4: Final-Review 發現 Requirements coverage 不足**
- **Given** Final-Review subagent 偵測到某 REQ-XXX 無對應綠燈測試
- **When** 主 skill 讀取 Final-Review 結果
- **Then** 派 Final-Fixer subagent 嘗試補充測試與實作
- **And** 修復後重跑 Final-Review；若仍不通過，在 final-report.md 記錄殘餘問題，不視為整體失敗（blocked item）

**Scenario 5: 成功結束**
- **Given** 所有 REQ-XXX 均有對應綠燈測試，E2E 通過（或已跳過並記錄），Final-Review 通過
- **When** 主 skill 完成最後一步
- **Then** final-report.md 完整呈現：✅ 完成 task 清單、❌ blocked 項目與原因、E2E 狀態、Final-Review 結論
- **And** impl-checklist-{group}.md 全部填寫完成

---

## REQ-006: Agent-only skill 架構與 prompt cache 設計

**描述**：7 個 subagent 均必須設計為 agent-only skill 文件（`agents/*.md`），固定 prompt 置於文件開頭，動態參數在後注入，確保多次呼叫時 prompt cache 命中。

### Scenarios

**Scenario 1: 首次呼叫建立 cache**
- **Given** impl-agent.md 的固定 prompt（role、constraints、TDAID 流程指引）在文件開頭
- **When** 主 skill 第一次派 Impl subagent
- **Then** LLM 載入文件，cache 被溫暖
- **And** 後續對同一 agent 的呼叫 hit cache，降低延遲與成本

**Scenario 2: 動態 task context 注入**
- **Given** impl-agent.md 有固定的 static 前綴（role + constraints + TDAID 規則）
- **When** 主 skill 呼叫 impl-agent 時，注入摘要 subagent 產出的 8 欄位 task context（Goal/Requirements/Scenarios/Task/Design/Test/Constraints/Files）
- **Then** 動態部分在固定 prefix 之後注入，不破壞 cache 命中的前綴穩定性

**Scenario 3: 每個 agent 有明確的 視角/目標/通用原則/禁忌 結構**
- **Given** 新建的 agent-only skill 文件
- **When** 文件內容被驗收
- **Then** 文件包含 視角（agent 的觀察角度）、目標（這個 agent 要達成什麼）、通用原則（執行規則）、禁忌（不做什麼）四個 section
- **And** 不包含 "you are a senior X" 角色扮演描述（避免幻覺）

---

## REQ-007: Plugin 打包與發布

**描述**：Execute skill 必須存在於正確路徑並可被 baransu plugin 識別；plugin.json 版本號必須隨本次新增功能升級；README.md 必須新增 /execute skill 說明。

### Scenarios

**Scenario 1: Plugin 識別**
- **Given** `plugins/baransu/skills/execute/SKILL.md` 文件存在
- **When** baransu plugin 啟動時掃描 skills 目錄
- **Then** `/baransu:execute` 可被識別並啟動

**Scenario 2: Plugin 版本升級**
- **Given** plugin.json 目前版本為 v0.2.X
- **When** execute skill 加入後
- **Then** plugin.json 的 version 欄位升級（minor bump），skills 陣列包含 execute 條目（name/description/path）

**Scenario 3: README 更新**
- **Given** README.md 目前缺少 /baransu:execute 說明
- **When** README.md 更新後
- **Then** 包含 /baransu:execute 的核心目的、前置需求（需先跑 /baransu:analyze）、使用範例、Roadmap 標記已完成
