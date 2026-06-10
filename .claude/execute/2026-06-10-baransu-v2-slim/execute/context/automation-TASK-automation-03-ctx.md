task_id: TASK-automation-03
group: automation

Goal: |
  baransu 從 16 技能瘦身為 12 技能的 2.0.0 改版中，每個存活技能須「可被 /goal 式外部驗證者
  與 loop 驅動」。本 task 對應驗收標準 C4 的標注部分：
  「12 技能於 SKILL.md 契約區塊內帶雙軸自動化相容標注（不用非標準 frontmatter 欄位）」。

Requirements: |
  REQ-004: 自動化相容（loop-contract＋雙模單一介面）
  描述：技能可被 /loop、cron、Workflow 安全驅動；review/execute/learn 在 ultracode 下
  可走 Workflow 編排且不破壞既有內部契約。

Scenarios: |
  REQ-004 Scenario 1: loop 驅動下的 PAUSE 行為
  - Given 任一存活技能被 /loop、cron 或 Workflow 驅動（非互動）
  - When 流程遇到 Input PAUSE（資訊性確認）
  - Then 取推薦預設值續行，並在最終報告標注「此處採預設：{假設}」
  - And 遇到 Authorization PAUSE（破壞性/不可逆授權）時無條件硬停，loop-contract 明文：
    驅動上下文覆寫平台預設，但 Authorization PAUSE 任何情況不可覆寫

  REQ-004 Scenario 2: PAUSE 分類表
  - Given review/execute/learn 三技能的全部 AskUserQuestion 互動點
  - When loop-contract.md 撰寫
  - Then 每個互動點被標注為 Input 或 Authorization
  - And think 標注「不可 loop 驅動」（對焦無法用預設值替代）

  REQ-004 Scenario 3: 雙模單一介面
  - Given review/execute/learn 各有手刻平行編排（perspective Tasks / TDAID 艦隊 / 四 lane fan-out）
  - When ultracode session 中觸發（Stage 0 偵測並釘死模式，整輪不切換）
  - Then 可改走 Workflow 原語編排，但必須產出與現行路徑同形的內部資料
  - And depth 不變量在兩模章節各自重述

Task: |
  TASK-automation-03: 12 技能雙軸相容標注（契約區塊內）
  需求追溯：REQ-004
  前置群組：cut

  目標：每個存活 SKILL.md 的 Outcome Contract 區塊內帶一行自動化標注
  （ultracode: overlap/assist/neutral × loop: drivable/assisted/not-drivable）。

  驗收標準：
  - [ ] 12 檔均有標注，分級與計畫表一致（review/execute/learn=overlap+drivable；
        hunt/analyze/codex-skill-transfer=assist；think=neutral+not-drivable；
        write/ship/read/book/design=neutral）
  - [ ] 標注位於 SKILL.md 本文契約區塊（第五行「Automation: …」），不使用非標準
        frontmatter 欄位（官方跨平台相容建議；亦確保 codex transfer 不丟失）
  - [ ] hunt/analyze 增一句「ultracode 時可派 Workflow 平行探查/調研」提示與
        loop-mode 預設值句

  步驟（標注）：
  - [ ] 逐檔 Edit 契約區塊；hunt/analyze 加提示句（與 TASK-contract 協調：
        contract 群先落四行，本 task 補第五行）

Design: |
  - 官方 best practices 對齊（design.md 查核結果）：自訂 frontmatter 欄位 — 官方建議僅用
    標準欄位（跨平台相容；非標準欄位被忽略）→ 雙軸 automation 標注放 SKILL.md 契約區塊
    第五行，不放 frontmatter。
  - Outcome Contract 資料模型（每個 SKILL.md 頭部）：四行定式 — Outcome（一句）/
    Done when（可驗證或事件型）/ Evidence（判定依據）/ Output（產物形態）；契約四行位於
    frontmatter 後、第一個 H2 前。本 task 在 Output bullet 之後補第五行 Automation。
  - verify-skills.py 檢查項含「契約四行＋第五行 Automation 標注」；缺漏 → exit 1。
  - 執行序：本 task 屬 Wave 2 automation 群，與 contract/governance 群平行，
    但 12 檔契約區塊（四 bullet）已由 contract 群先落地，本任務只插第五行。

Test: |
  - E2E：python3 scripts/verify-skills.py → exit 0，輸出 12 技能逐項通過
    （含契約四行、第五行 Automation 標注）— 對應 C4。
  - 邊界條件（test.md）：自動化標注覆蓋 — 12 檔契約區塊第五行均含「Automation:」
    且值非空（缺漏 → verify-skills exit 1）— REQ-004。
  - 契約頭對兩種 frontmatter 風格（think 極簡式 / read-learn 完整式）都要通過解析；
    本 task 不得破壞任一風格的 frontmatter 結構。

Constraints: |
  - 標注格式固定為一行 bullet：
    「- **Automation**: ultracode={overlap|assist|neutral}, loop={drivable|assisted|not-drivable}」
    置於契約區塊第五行（Output bullet 之後）。
  - 分級表（全文，12 檔分級必須與此一致）：
    * review / execute / learn = ultracode=overlap, loop=drivable
    * hunt / analyze / codex-skill-transfer = ultracode=assist, loop=assisted
    * think = ultracode=neutral, loop=not-drivable
    * write / ship / read / book / design = ultracode=neutral，loop 軸各自判定 —
      write/read/book/design 可 loop 驅動（單線可預設）標 drivable 或 assisted；
      ship 涉 push 授權標 assisted。
  - 不動 frontmatter：標注只進 SKILL.md 本文契約區塊，不新增任何非標準 frontmatter 欄位。
  - hunt/analyze 各加一句「ultracode 時可派 Workflow 平行探查/調研」提示與
    loop-mode 預設值句（加在正文適當位置，≤2 行）。
  - 12 檔契約區塊已由 contract 群落地（四 bullet 已存在），本任務只插第五行 —
    不得重寫或調整既有四行內容。
  - 與 TASK-contract 協調：contract 群先落四行，本 task 補第五行（時序不可倒置）。
  - SKILL.md 官方 500 行上限考量：execute 已超限，新增僅限第五行一行，不得實質增長。
  - 不修改 Analyze spec 目錄下任何文件。

Files:
  - plugins/baransu/skills/think/SKILL.md        # 標注 neutral + not-drivable
  - plugins/baransu/skills/review/SKILL.md       # 標注 overlap + drivable
  - plugins/baransu/skills/analyze/SKILL.md      # 標注 assist + assisted；加 Workflow 提示句 + loop-mode 預設值句
  - plugins/baransu/skills/write/SKILL.md        # 標注 neutral + drivable/assisted（單線可預設）
  - plugins/baransu/skills/execute/SKILL.md      # 標注 overlap + drivable（僅加一行，已超 500 行）
  - plugins/baransu/skills/ship/SKILL.md         # 標注 neutral + assisted（涉 push 授權）
  - plugins/baransu/skills/hunt/SKILL.md         # 標注 assist + assisted；加 Workflow 提示句 + loop-mode 預設值句
  - plugins/baransu/skills/read/SKILL.md         # 標注 neutral + drivable/assisted（單線可預設）
  - plugins/baransu/skills/learn/SKILL.md        # 標注 overlap + drivable
  - plugins/baransu/skills/book/SKILL.md         # 標注 neutral + drivable/assisted（單線可預設）
  - plugins/baransu/skills/design/SKILL.md       # 標注 neutral + drivable/assisted（單線可預設）
  - plugins/baransu/skills/codex-skill-transfer/SKILL.md  # 標注 assist + assisted
