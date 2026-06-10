# Tasks: contract（Outcome Contract 移植）
**前置群組**：cut

## TASK-contract-01: 可驗證型八技能契約頭

**需求追溯**：REQ-003
**目標**：analyze/execute/ship/read/learn/hunt/design/codex-skill-transfer 八個 SKILL.md 開頭帶四行契約，Done when 為可驗證條件。
**驗收標準**：
- [ ] 各檔 frontmatter 後、第一個 H2 前出現 Outcome Contract 四行（Outcome / Done when / Evidence / Output）
- [ ] Done when 均為命令、檔案存在或可數狀態（例：execute =「final-report.md 存在且 Final-Review 100% REQ 覆蓋」）
- [ ] 既有正文零刪改（契約是前置補充，不重寫技能）

### 步驟

#### 撰寫
- [ ] 逐檔 Read 既有開頭 → 從正文現有的完成定義提煉四行（不發明新語義）→ Edit 插入
- [ ] 對照 requirement.md REQ-003 Scenario 1 自查 Done when 可驗證性

## TASK-contract-02: 事件型四技能契約頭

**需求追溯**：REQ-003
**目標**：think/write/book/review 四個 SKILL.md 帶事件型或混合型契約。
**驗收標準**：
- [ ] think Done when =「使用者於 Stage G 批准（四選項閘事件）」類事件型表述
- [ ] write/book 以人工檢核點列舉或產物＋檢核混合型表述；review =「報告含八欄 sign-off receipt 且 hard-stops sweep 完成」
- [ ] 無「輸出存在」式空殼條件

### 步驟

#### 撰寫
- [ ] 逐檔 Read → 提煉 → Edit；book 的 Done when 可錨定 validate-output.ts 閘
