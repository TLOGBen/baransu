# Tasks: agents-tdaid
**前置群組**：無

這個群組包含 TDAID loop 的四個核心 agent-only skill 文件。它們彼此獨立，可在同一 session 內依序完成。

---

## TASK-agents-tdaid-01: 建立 summarize-agent.md

**需求追溯**：REQ-006, REQ-003
**目標**：建立摘要 subagent 的 agent-only skill 文件，讓主 skill 呼叫它時能從 spec 文件提取單一 task 的 8 欄位 context，輸出寫入 `context/{group}-{id}-ctx.md`。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/summarize-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則明確列出 8 欄位（Goal/Requirements/Scenarios/Task/Design/Test/Constraints/Files）的提取規則
- [ ] 禁忌包含「不傳入整份文件；只提取與當前 task ID 直接相關的段落」
- [ ] 禁忌包含「不修改 Analyze spec 目錄下的任何文件」
- [ ] 無角色扮演描述（無 "you are a senior X" 語句）
- [ ] 固定 prompt（role + constraints）位於文件開頭，動態部分（task ID + spec paths）在後注入

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以文件摘要器的角度，從 Analyze spec 目錄提取與特定 task 相關的最小必要資訊」
- [ ] 撰寫 目標：「產出一份 8 欄位 YAML 摘要（ctx.md），供 impl-agent 作為執行上下文」
- [ ] 列出通用原則：8 欄位定義、只取相關段落、輸出格式（YAML）、輸出路徑規則
- [ ] 列出禁忌：不傳整份文件、不修改 spec、不做任何程式碼判斷

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `summarize-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範

---

## TASK-agents-tdaid-02: 建立 impl-agent.md

**需求追溯**：REQ-003, REQ-006
**目標**：建立 Impl subagent 的 agent-only skill 文件，使其能根據 ctx.md 執行完整的 Red/Green TDD 實作（寫失敗測試 → 實作 → 確認通過）。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/impl-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則明確說明 Red gate（測試必須先失敗）和 Green gate（實作後測試必須通過）
- [ ] 通用原則說明 compile error 不計入 Green 失敗計數
- [ ] 通用原則說明 L/XL 任務的 Refactor 條件（Review 判定需要時，最多一次）
- [ ] 禁忌包含「不修改 Analyze spec 目錄下的任何文件」
- [ ] 禁忌包含「不在沒有失敗測試的情況下直接寫實作」
- [ ] 固定 prompt 在前，動態參數（ctx.md 內容 + worktree path）在後

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以 TDD 實作者的角度，根據 ctx.md 的規格完成 Red/Green 循環」
- [ ] 撰寫 目標：「在指定的 worktree 中完成測試撰寫 + 實作，所有測試通過後回報主 skill」
- [ ] 列出通用原則：Red gate 規則、Green gate 規則、compile error 處理、Refactor 觸發條件
- [ ] 列出禁忌：不改 spec、不跳過 Red gate、不超過 Refactor 次數限制

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `impl-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範

---

## TASK-agents-tdaid-03: 建立 review-agent.md

**需求追溯**：REQ-003, REQ-005, REQ-006
**目標**：建立 Review subagent 的 agent-only skill 文件，使其直接實作四層語義審查（不呼叫 /baransu:review skill）並將結構化結果回傳給主 skill，同時填寫 impl-checklist。不呼叫外部 skill 的原因：subagent 深度上限為 1，/baransu:review 本身會派遣 Tasks + AskUserQuestion，不可在 subagent 內巢狀呼叫。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/review-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則明確說明四層語義定義（advisory/packaged confirm/needs judgment/direct fix）及判斷準則
- [ ] 通用原則說明回傳格式：結構化的四層結果（tier + findings 清單），主 skill 可直接讀取判斷下一步
- [ ] 通用原則說明 Spec 矛盾（REQ-XXX 無法共存）的上報流程
- [ ] 通用原則說明填寫 `impl-checklist-{group}.md` 的規則
- [ ] 禁忌包含「不呼叫 /baransu:review skill（subagent 深度限制）」
- [ ] 禁忌包含「不自行修改 Analyze spec 文件」
- [ ] 禁忌包含「不合併多個 task 的 Review 結果為一次回報」

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以品質審查者的角度，驗證 impl-agent 的實作是否滿足 task 的驗收標準和需求」
- [ ] 撰寫 目標：「直接套用 /baransu:review 的四層語義框架審查實作，產出結構化結果供主 skill 消費，填寫 impl-checklist」
- [ ] 列出通用原則：四層語義定義與判斷準則、回傳格式、Spec 矛盾上報、checklist 填寫格式
- [ ] 列出禁忌：不改 spec、不合併多 task 結果

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `review-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範

---

## TASK-agents-tdaid-04: 建立 smart-friend-agent.md

**需求追溯**：REQ-004, REQ-006
**目標**：建立 smart-friend subagent 的 agent-only skill 文件，使其在 Impl 連續失敗 2 次後收到 task goal + 兩次失敗摘要，用 extended thinking 輸出修正策略。
**驗收標準**：
- [ ] 文件存在於 `plugins/baransu/agents/smart-friend-agent.md`
- [ ] 文件包含 視角 / 目標 / 通用原則 / 禁忌 四個 section
- [ ] 通用原則說明輸入格式（task goal + spec 段落 + 兩次失敗摘要）
- [ ] 通用原則說明輸出格式（修正策略，供主 skill 傳給第 3 輪 Impl）
- [ ] 通用原則明確：若認為 spec 本身有問題，輸出「需升級用戶：spec 可能有矛盾」，不自行修改
- [ ] 禁忌包含「不自行實作任何程式碼」
- [ ] 禁忌包含「不修改 Analyze spec 文件」

### 步驟

#### 設計 agent 文件內容
- [ ] 撰寫 視角：「以診斷顧問的角度，分析 Impl subagent 連續失敗的根本原因」
- [ ] 撰寫 目標：「根據失敗摘要輸出修正策略，或識別並上報 spec 層級的問題」
- [ ] 列出通用原則：輸入格式、診斷步驟（根因 vs 症狀）、輸出格式、spec 矛盾上報路徑
- [ ] 列出禁忌：不寫程式碼、不改 spec、不假設失敗原因

#### 建立文件
- [ ] 在 `plugins/baransu/agents/` 建立 `smart-friend-agent.md`
- [ ] 驗證文件結構符合 agent-only skill 規範
