# ctx: TASK-automation-01（_shared/loop-contract.md）

```yaml
Goal: |
  baransu 16→12 技能瘦身中，建立四個治理資產之一：_shared/loop-contract.md，
  使每個技能可被 /goal 式外部驗證者與 loop 驅動。
  對應驗收 C4（前半）：「_shared/loop-contract.md 存在且含 review/execute/learn
  的逐互動點 PAUSE 分類表」。
  Scope（新增面）明列：_shared/loop-contract.md。
  Out of scope：事後遙測替代品 — 要 loop 用官方 /loop、/goal、cron、Workflow；
  12 技能的 automation 深度整合（夜巡配方等）等真實 loop 需求出現再做。

Requirements: |
  REQ-004: 自動化相容（loop-contract＋雙模單一介面）
  描述：技能可被 /loop、cron、Workflow 安全驅動；review/execute/learn 在
  ultracode 下可走 Workflow 編排且不破壞既有內部契約。
  （本 task 只負責 loop-contract.md；雙模介面與標注分屬 TASK-automation-02/03。）

Scenarios: |
  REQ-004 Scenario 1: loop 驅動下的 PAUSE 行為
  - Given 任一存活技能被 /loop、cron 或 Workflow 驅動（非互動）
  - When 流程遇到 Input PAUSE（資訊性確認）
  - Then 取推薦預設值續行，並在最終報告標注「此處採預設：{假設}」
  - And 遇到 Authorization PAUSE（破壞性/不可逆授權）時無條件硬停，
    loop-contract 明文：驅動上下文覆寫平台預設，但 Authorization PAUSE
    任何情況不可覆寫

  REQ-004 Scenario 2: PAUSE 分類表
  - Given review/execute/learn 三技能的全部 AskUserQuestion 互動點
  - When loop-contract.md 撰寫
  - Then 每個互動點被標注為 Input 或 Authorization
    （例：/review 的需判斷裁決 = Authorization；/learn 的評分確認 = Input）
  - And think 標注「不可 loop 驅動」（對焦無法用預設值替代）

  （Scenario 3 雙模單一介面、Scenario 4 非 ultracode 回退屬 TASK-automation-02，
  不在本 task 範圍。）

Task: |
  TASK-automation-01: _shared/loop-contract.md
  前置群組：cut
  需求追溯：REQ-004
  目標：loop/cron/Workflow 驅動下的技能行為契約成文。

  驗收標準：
  - [ ] 規則段：Input PAUSE 取推薦預設＋報告標注；Authorization PAUSE 無條件硬停；
        「驅動上下文覆寫平台預設，Authorization 不可覆寫」優先序明文
        （引用全域 platform-awareness，不複述第三份）
  - [ ] 三硬停責任分界：迭代上限/無進展/預算歸驅動方；技能側義務=可重入＋
        狀態落盤（.claude/<skill>/）＋無進展明確回報
  - [ ] PAUSE 分類表：review/execute/learn 逐互動點標注 Input/Authorization
        與預設值；think 列為「不可 loop 驅動」

  步驟（撰寫）：
  - [ ] Read review/execute/learn 三份 SKILL.md，枚舉全部 AskUserQuestion/確認點
  - [ ] 逐點分類（例：review 需判斷裁決=Authorization；learn 評分確認=Input、
        預設=全部保留；execute 的 E2E 失敗處置=Authorization）
  - [ ] 撰寫 loop-contract.md；Read 全域 platform-awareness 規則確認引用而非複述

Design: |
  系統架構定位：技能層 _shared/ 本次「刪 3 schema、改 tdd.md、增 loop-contract.md」；
  automation 群為 Wave 2，前置 Wave 1（cut），與 reroute/contract/governance 平行。

  loop-contract 資料流（design.md）：
  ```mermaid
  flowchart TD
    D[驅動上下文: /loop, cron, Workflow, automation] --> S[技能 Stage 0: 識別非互動驅動]
    S --> P{PAUSE 類型?}
    P -->|Input| DEF[取推薦預設 + 報告標注假設]
    P -->|Authorization| HALT[無條件硬停, 回報 needs input]
    DEF --> R[執行 → 狀態落盤 .claude/skill 工件]
    R --> O[最終報告: 假設清單 + 三硬停狀態]
  ```

  三硬停的承接：迭代上限與無進展偵測由驅動方（/loop、Workflow script）持有；
  技能側義務是「可重入＋狀態落盤＋無進展時明確回報而非重試」。預算上限由
  harness 的 budget 機制持有。loop-contract.md 記錄這個責任分界。

  資料模型（loop-contract.md 的結構）：
  規則段（PAUSE 語義、覆寫優先序、三硬停責任分界）＋
  PAUSE 分類表（技能 × 互動點 × Input/Authorization × 預設值）。

  官方 best practices 對齊（2026-06-10 查核，與本 task 直接相關的最後一條）：
  headless/cron 場景官方文件未覆蓋 → loop-contract.md 是插件層慣例，
  需自我聲明非官方標準。

Test: |
  整合測試「loop-contract ↔ 全域規則分層」（_shared × 使用者全域 rules）：
  - 明文「驅動上下文覆寫平台預設；Authorization 不可覆寫」
    （引用 platform-awareness 而非第三份編碼）
  - 三硬停責任分界 ≥3 項明文
  - PAUSE 分類表覆蓋 review/execute/learn 全部互動點
  - 含「本慣例非官方標準」自宣告
  下游：verify 群的 verify-skills.py 會檢查 SKILL.md 引用的 references/ 檔案存在；
  loop-contract.md 本身為 _shared/ 文件，REQ-001 Scenario 1 預期裁併後
  _shared/ 僅剩 tdd.md 與新增的 loop-contract.md。

Constraints: |
  - 覆寫優先序必須明文：「驅動上下文覆寫平台預設；Authorization PAUSE
    任何情況不可覆寫」。
  - 引用使用者全域 platform-awareness 規則
    （~/.claude/rules/common/platform-awareness.md 的 Input/Authorization PAUSE
    分類），不得複述成第三份編碼。
  - 三硬停責任分界（≥3 項明文）：迭代上限、無進展偵測、預算上限由驅動方
    （/loop、Workflow script、harness budget）持有；技能側義務 = 可重入＋
    狀態落盤（.claude/<skill>/）＋無進展時明確回報而非重試。
  - PAUSE 分類表須逐互動點列出 review/execute/learn 三技能；實際互動點必須
    Read 三份 SKILL.md 現況枚舉全部 AskUserQuestion/確認點，不得憑記憶或
    舉例充數（spec 例：review 需判斷裁決=Authorization；learn 評分確認=Input、
    預設=全部保留；execute E2E 失敗處置=Authorization）。
  - think 列為「不可 loop 驅動」（對焦無法用預設值替代）。
  - 含「本慣例非官方標準」自宣告（官方文件未覆蓋 headless/cron 場景）。
  - 前置群組 cut 須已完成；完成後 _shared/ 僅剩 tdd.md 與本檔。
  - 不修改 .claude/analyze/ spec 目錄下任何文件。

Files: |
  新增：
  - plugins/baransu/skills/_shared/loop-contract.md
  需 Read（不修改）：
  - plugins/baransu/skills/review/SKILL.md
  - plugins/baransu/skills/execute/SKILL.md
  - plugins/baransu/skills/learn/SKILL.md
  - ~/.claude/rules/common/platform-awareness.md（確認引用而非複述）
```
