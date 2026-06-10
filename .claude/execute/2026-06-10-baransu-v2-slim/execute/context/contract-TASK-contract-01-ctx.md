task_id: TASK-contract-01
group: contract
spec_dir: .claude/analyze/2026-06-10-baransu-v2-slim

Goal: |
  baransu 16→12 技能瘦身的治理資產之一：建立 Outcome Contract 四行頭。
  對應驗收標準 C3：12 個存活 SKILL.md 開頭均有 Outcome Contract 四行
  （Outcome / Done when / Evidence / Output）；Done when 為可驗證條件。
  本 task 負責其中八個「可驗證型」技能（事件型四技能由 TASK-contract-02 處理）。
  Scope 註記：execute 只加標注與薄 adapter 章節，不動 subagent 迴圈邏輯
  （TDAID 與五平面語義重寫為 out of scope）。

Requirements: |
  REQ-003: Outcome Contract 移植
  描述：12 個存活 SKILL.md 開頭帶 Outcome Contract 四行
  （Outcome / Done when / Evidence / Output），Done when 為可被外部驗證者判定的條件。

Scenarios: |
  REQ-003 Scenario 1: 可驗證型技能（本 task 主場景）
  - Given: analyze/execute/ship/read/learn/hunt/design/codex-skill-transfer
    等產出可觀察 artifact 的技能
  - When: 契約頭加入
  - Then: Done when 為命令、檔案存在或可數狀態
    （例：「.claude/analyze/{dir}/ 五層 spec 齊備且 Stage 6 審查通過」）

  REQ-003 Scenario 3: frontmatter 相容（影響插入位置）
  - Given: 倉內現有兩種 frontmatter 風格（think 極簡式 vs read/learn 的
    Use When/Do/Trigger On 式）
  - When: verify-skills.py 檢查契約
  - Then: 兩種風格均通過；契約四行位於 SKILL.md 正文開頭區，不強改 frontmatter 結構

Task: |
  TASK-contract-01: 可驗證型八技能契約頭（task-contract.md；前置群組：cut）

  需求追溯：REQ-003
  目標：analyze/execute/ship/read/learn/hunt/design/codex-skill-transfer
  八個 SKILL.md 開頭帶四行契約，Done when 為可驗證條件。

  驗收標準：
  - [ ] 各檔 frontmatter 後、第一個 H2 前出現 Outcome Contract 四行
        （Outcome / Done when / Evidence / Output）
  - [ ] Done when 均為命令、檔案存在或可數狀態
        （例：execute =「final-report.md 存在且 Final-Review 100% REQ 覆蓋」）
  - [ ] 既有正文零刪改（契約是前置補充，不重寫技能）

  步驟（撰寫）：
  - [ ] 逐檔 Read 既有開頭 → 從正文現有的完成定義提煉四行（不發明新語義）→ Edit 插入
  - [ ] 對照 requirement.md REQ-003 Scenario 1 自查 Done when 可驗證性

Design: |
  資料模型 — Outcome Contract schema（design.md「資料模型」表）：
  - 位置：每個 SKILL.md 頭部
  - 結構：四行定式 — Outcome（一句）/ Done when（可驗證或事件型）/
    Evidence（判定依據）/ Output（產物形態）
  - 下游消費者：verify-skills.py 將逐檔斷言「契約四行齊備且 Done-when 非空」；
    契約區塊第五行另由 automation 群組加「Automation:」雙軸標注
    （不放 frontmatter — 本 task 只負責四行，知悉第五行會接續其後即可）

  官方 best practices 對齊（design.md，2026-06-10 官方文件查核）：
  - 自訂 frontmatter 欄位：官方建議僅用標準欄位（非標準欄位被忽略）→
    契約/標注放 SKILL.md 契約區塊（正文開頭區），不放 frontmatter。
  - 500 行上限：官方明訂 SKILL.md 本文 <500 行 → 新增內容一律走 references/
    一層深；verify-skills.py 對超限檔出 advisory 清單（execute 為既有超限戶）。
  - frontmatter 機器檢查：name ≤64 小寫連字符、description 非空 ≤1024、
    第三人稱 — 由 verify-skills.py 負責，本 task 不改 frontmatter。

  執行序：contract 群組屬 Wave 2，與 reroute/automation/governance 平行，
  依賴 Wave 1（cut 刪除面）完成；產出供 Wave 3 verify-skills.py 驗證。

Test: |
  E2E（test.md）：
  - 「結構完整性一條命令」：python3 scripts/verify-skills.py → exit 0，
    輸出 12 技能逐項通過（含契約四行）— 對應 C3。
  - 整合測試「Outcome Contract 齊備」：verify-skills.py 逐檔斷言四行非空＋
    Done-when 非空；負向 fixture 缺行 → exit 1。

  關鍵邊界條件：
  - 契約頭對兩種 frontmatter 風格（think 極簡式 / read-learn 完整式）都要通過
    verify-skills.py 解析 — REQ-003, REQ-005
  - 驗證器只查四行齊備與非空，語義品質由 spec review 把關 — REQ-003
  - SKILL.md >500 行為 advisory（execute 既有超限戶），不影響 exit code — REQ-005
  - 整合測試「review-agent 錨點改掛後 execute 管線語義」要求 execute/SKILL.md 的
    Goal-Alignment Filter 與 failure_count 章節零變更（diff 為證）—
    本 task 對 execute 僅前置插入四行，不得觸及這些章節。

Constraints:
  - 四行契約（Outcome / Done when / Evidence / Output）置於 frontmatter 後、第一個 H2 前。
  - Done when 必須為命令、檔案存在或可數狀態（例：execute =「final-report.md 存在且 Final-Review 100% REQ 覆蓋」）。
  - 從各技能正文現有的完成定義提煉四行，不發明新語義。
  - 既有正文零刪改 — 契約是前置補充，不重寫技能。
  - 官方 SKILL.md 500 行上限考量：execute 已超限，契約四行是允許的小幅新增，但不得趁機重寫或實質增長 execute 正文。
  - 倉內兩種 frontmatter 風格（think 極簡式 vs read/learn 的 Use When/Do/Trigger On 式）都不改動；契約只放正文開頭區，不強改 frontmatter 結構。
  - 不得出現「輸出存在」式空殼 Done when。
  - 不修改 Analyze spec 目錄（.claude/analyze/）下的任何文件。

Files:
  - plugins/baransu/skills/analyze/SKILL.md（修改：插入契約四行）
  - plugins/baransu/skills/execute/SKILL.md（修改：插入契約四行；其餘章節零變更）
  - plugins/baransu/skills/ship/SKILL.md（修改：插入契約四行）
  - plugins/baransu/skills/read/SKILL.md（修改：插入契約四行）
  - plugins/baransu/skills/learn/SKILL.md（修改：插入契約四行）
  - plugins/baransu/skills/hunt/SKILL.md（修改：插入契約四行）
  - plugins/baransu/skills/design/SKILL.md（修改：插入契約四行）
  - plugins/baransu/skills/codex-skill-transfer/SKILL.md（修改：插入契約四行）
