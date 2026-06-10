# Context: TASK-contract-02（事件型四技能契約頭）

```yaml
Goal: |
  baransu 16 技能瘦身為 12 技能並建立四個治理資產（含 Outcome Contract 四行頭），以 2.0.0 出貨。
  與本 task 直接相關的驗收標準：
  - C3：12 個存活 SKILL.md 開頭均有 Outcome Contract 四行（Outcome / Done when / Evidence / Output）；
    Done when 為可驗證條件，think/write/book 等允許事件型 done。
  Scope（改寫面，相關部分）：12 個 SKILL.md 契約頭與標注。

Requirements: |
  ## REQ-003: Outcome Contract 移植
  **描述**：12 個存活 SKILL.md 開頭帶 Outcome Contract 四行（Outcome / Done when / Evidence / Output），
  Done when 為可被外部驗證者判定的條件。

Scenarios: |
  REQ-003 Scenario 1: 可驗證型技能
  - Given analyze/execute/ship/read/learn/hunt/design/codex-skill-transfer 等產出可觀察 artifact 的技能
  - When 契約頭加入
  - Then Done when 為命令、檔案存在或可數狀態（例：「.claude/analyze/{dir}/ 五層 spec 齊備且 Stage 6 審查通過」）
  （註：review 的 Done when 走「報告含八欄 sign-off receipt 且 hard-stops sweep 完成」之產物＋檢核混合型，見 Task 驗收標準。）

  REQ-003 Scenario 2: 事件型技能（全文）
  - Given think/write/book 等以人為核准或審美輸出為終點的技能
  - When 契約頭加入
  - Then Done when 允許事件型表述（例：think =「使用者於 Stage G 批准」）或人工檢核點列舉，
    不得出現「輸出存在」之類空殼條件

  REQ-003 Scenario 3: frontmatter 相容
  - Given 倉內現有兩種 frontmatter 風格（think 極簡式 vs read/learn 的 Use When/Do/Trigger On 式）
  - When verify-skills.py 檢查契約
  - Then 兩種風格均通過；契約四行位於 SKILL.md 正文開頭區，不強改 frontmatter 結構

Task: |
  ## TASK-contract-02: 事件型四技能契約頭
  **群組**：contract（Outcome Contract 移植）；前置群組：cut
  **需求追溯**：REQ-003
  **目標**：think/write/book/review 四個 SKILL.md 帶事件型或混合型契約。
  **驗收標準**：
  - [ ] think Done when =「使用者於 Stage G 批准（四選項閘事件）」類事件型表述
  - [ ] write/book 以人工檢核點列舉或產物＋檢核混合型表述；review =「報告含八欄 sign-off receipt 且 hard-stops sweep 完成」
  - [ ] 無「輸出存在」式空殼條件

  ### 步驟
  #### 撰寫
  - [ ] 逐檔 Read → 提煉 → Edit；book 的 Done when 可錨定 validate-output.ts 閘

Design: |
  - 技能層動作：16 技能目錄刪 4、改 12（契約頭＋標注）；本 task 負責其中 think/write/book/review 四檔的契約頭。
  - 執行序：contract 群在 Wave 2，於 Wave 1（cut 刪除面）之後；契約/自動化/治理三組互不依賴可平行。
  - 資料模型 — Outcome Contract schema（每個 SKILL.md 頭部）：
    四行定式：Outcome（一句）/ Done when（可驗證或事件型）/ Evidence（判定依據）/ Output（產物形態）。
  - 官方 best practices 對齊（相關項）：
    * 自訂 frontmatter 欄位：官方建議僅用標準欄位 → 契約相關內容放 SKILL.md 契約區塊，不放 frontmatter。
    * 500 行上限：官方明訂 SKILL.md 本文 <500 行；verify-skills.py 對超限檔出 advisory（execute 為既有超限戶）—
      契約頭應保持精簡，避免推升行數。
  - verify-skills.py 後續會檢查：契約四行齊備且 Done-when 非空（本 task 產出須能通過該檢查）。

Test: |
  - E2E：`python3 scripts/verify-skills.py` exit 0，輸出 12 技能逐項通過（含契約四行）— 對應 C3。
  - 整合：「Outcome Contract 齊備」— verify-skills.py 逐檔斷言四行非空＋Done-when 非空。
  - 邊界條件（REQ-003）：
    * 事件型 Done when（think/write/book）不得寫成空殼條件（「輸出存在」不合格）；
      驗證器只查四行齊備與非空，語義品質由 spec review 把關。
    * 契約頭對兩種 frontmatter 風格（think 極簡式 / read-learn 完整式）都要通過 verify-skills.py 解析。

Constraints: |
  - think 的 Done when 必須為事件型：「使用者於 Stage G 批准（四選項閘事件）」類表述。
  - review 的 Done when 必須為「報告含八欄 sign-off receipt 且 hard-stops sweep 完成」。
  - write/book 採人工檢核點列舉或產物＋檢核混合型；book 的 Done when 可錨定 validate-output.ts 閘。
  - 禁止空殼條件：「輸出存在」之類表述不合格（test.md 明文：事件型 Done when 不得寫成空殼條件）。
  - REQ-003 Scenario 2 全文（自查依據）：
    Given think/write/book 等以人為核准或審美輸出為終點的技能；
    When 契約頭加入；
    Then Done when 允許事件型表述（例：think =「使用者於 Stage G 批准」）或人工檢核點列舉，
    不得出現「輸出存在」之類空殼條件。
  - 其餘同 contract-01 的格式與零刪改約束：
    * 契約四行（Outcome / Done when / Evidence / Output）插入於各檔 frontmatter 後、第一個 H2 前。
    * 既有正文零刪改 — 契約是前置補充，不重寫技能。
    * 從正文現有的完成定義提煉四行，不發明新語義；逐檔先 Read 再 Edit。
    * 不強改 frontmatter 結構；兩種 frontmatter 風格均須維持可被 verify-skills.py 解析。

Files:
  - plugins/baransu/skills/think/SKILL.md   # 修改：插入事件型契約四行
  - plugins/baransu/skills/write/SKILL.md   # 修改：插入人工檢核點/混合型契約四行
  - plugins/baransu/skills/book/SKILL.md    # 修改：插入混合型契約四行（可錨定 validate-output.ts 閘）
  - plugins/baransu/skills/review/SKILL.md  # 修改：插入產物＋檢核混合型契約四行
```
