# Context: TASK-automation-02

```yaml
Goal: |
  baransu 16→12 技能瘦身的 C4 子項：review/execute/learn 三技能須含「單一內部介面＋Workflow 薄 adapter」契約，
  依官方 progressive-disclosure 慣例置於各技能 `references/orchestration-interface.md`，SKILL.md 留 ≤10 行指針段；
  同形 finding schema、depth 不變量逐模重述、Stage 0 模式釘死。
  （goal.md C4；範圍排除項明訂：execute 只加標注與薄 adapter 章節，不動 TDAID subagent 迴圈邏輯。）

Requirements: |
  REQ-004: 自動化相容（loop-contract＋雙模單一介面）
  描述：技能可被 /loop、cron、Workflow 安全驅動；review/execute/learn 在 ultracode 下可走 Workflow 編排
  且不破壞既有內部契約。
  （本 task 聚焦 Scenario 3 / 4；Scenario 1 / 2 屬 TASK-automation-01 的 loop-contract.md。）

Scenarios: |
  REQ-004 Scenario 3: 雙模單一介面
  - Given review/execute/learn 各有手刻平行編排（perspective Tasks / TDAID 艦隊 / 四 lane fan-out）
  - When ultracode session 中觸發（Stage 0 偵測並釘死模式，整輪不切換）
  - Then 可改走 Workflow 原語編排，但必須產出與現行路徑同形的內部資料
    （review：同 schema 的 findings；execute：review-agent 回傳形狀不變，
    Goal-Alignment Filter 與 failure_count 記帳不受影響）
  - And depth 不變量（review-agent 不得呼叫 /review 等）在兩模章節各自重述

  REQ-004 Scenario 4: 非 ultracode 回退
  - Given 一般 session（無 ultracode）
  - When 三技能執行
  - Then 走現行已驗證路徑，行為與 1.5.0 一致

Task: |
  TASK-automation-02: 三技能雙模「單一介面＋薄 adapter」references 檔
  需求追溯：REQ-004
  前置群組：cut
  目標：review/execute/learn 各增 `references/orchestration-interface.md`（一層深），
  SKILL.md 留 ≤10 行指針段；現行路徑語義零變更。

  驗收標準：
  - [ ] 各技能 references/orchestration-interface.md 含介面契約：回傳同形
        （review=findings schema；execute=review-agent 回傳形狀，Goal-Alignment Filter/failure_count 章節零 diff；
        learn=候選池 {path,lane} 形狀）
  - [ ] Stage 0 模式釘死：偵測 ultracode（system-reminder）→ 落盤 → 整輪不切換；偵測不可靠退化為顯式聲明
  - [ ] depth 不變量在現行 adapter 與 Workflow adapter 兩段各重述一次（grep 每個 reference 檔 ≥2 處）
  - [ ] Workflow 段只描述派發與收集，不複製業務規則（lane-keeping/balance/記帳只在主流程一份）
  - [ ] SKILL.md 本文僅增 ≤10 行指針段（官方 500 行上限考量；execute 已超限，不得再實質增長）

  步驟（撰寫）：
  - [ ] 逐檔 Read → 撰寫 references/orchestration-interface.md → SKILL.md 插入指針段
  - [ ] diff 自查：execute 的 filter/failure_count 章節、review 的 Stage 5-7、learn 的 Stage 2-5 主流程零變更

Design: |
  ## 雙模單一介面設計（REQ-004 核心）— design.md 全文

  三技能各定義一個「編排介面」，兩個 adapter 都實作它；介面是 SKILL.md 內的契約段落，不是程式碼：

  ```mermaid
  flowchart LR
    subgraph 單一內部介面
      I["dispatch(視角/任務清單) → findings[同形 schema]"]
    end
    M1[現行 adapter: 平行 Task / subagent 迴圈] --> I
    M2[薄 adapter: ultracode 時 Workflow pipeline] --> I
    I --> C1[review: Stage 6 整併/balance]
    I --> C2[execute: Goal-Alignment Filter + failure_count 記帳]
    I --> C3[learn: Stage 2 評分池]
  ```

  介面契約要點（寫入各技能 `references/orchestration-interface.md`，SKILL.md 僅留 ≤10 行指針段 —
  官方 progressive-disclosure 慣例，且 execute/SKILL.md 已超官方 500 行上限不得再實質增長）：
  1. **回傳同形**：findings/結果的欄位、tier 語彙、引用格式與現行路徑完全一致 —
     下游消費者（review 的 Stage 6、execute 的 filter 與記帳、learn 的評分表）不感知模式。
  2. **Stage 0 模式釘死**：session 開始時偵測 ultracode（system-reminder 確認）並落盤記錄；
     整輪不切換；偵測不可靠時退化為「使用者顯式聲明才走 Workflow」。
  3. **depth 不變量逐模重述**：「review-agent / perspective agent 不得再呼叫 skill、不得互審」
     在現行 adapter 與 Workflow adapter 兩個章節各寫一次。
  4. **薄 adapter 的「薄」**：Workflow 章節只描述「用 pipeline/parallel 派發、收同形結果」，
     不複製業務規則；業務規則（lane-keeping、balance check、failure_count）只在主流程寫一次。

  相關官方 best practices 對齊（design.md）：
  - 500 行上限：新增內容（介面契約、薄 adapter）一律走 references/ 一層深；execute 為既有超限戶。
  - references 一層深：所有新 reference 檔直接從 SKILL.md 連結，禁巢狀（官方警告巢狀導致 partial read）。

Test: |
  關鍵邊界條件（test.md，與本 task 直接相關）：
  - 雙模 depth 不變量：review/execute/learn 各自的 references/orchestration-interface.md 內，
    depth 限制語句於兩個 adapter 段各出現一次（grep 計數每檔 ≥2）— REQ-004
  - depth 違反的「行為層」偵測（agent 實際呼叫 skill）不納入 verify-skills.py 自動驗證 —
    文字層計數可自動，行為層留給 spec review 與 execute 既有測試 — REQ-004
  - verify-skills.py 會檢查 SKILL.md 引用的 references/ 檔案存在且一層深（後續 verify 群消費本 task 產物）
  - SKILL.md >500 行為 advisory 清單（execute 既有超限戶），不影響 exit code — REQ-005
  - 整合測試「review-agent 錨點改掛後 execute 管線語義」要求：execute/SKILL.md 的
    Goal-Alignment Filter 與 failure_count 章節零變更（diff 為證）

Constraints:
  - 每技能 references/orchestration-interface.md 必須一層深：直接從 SKILL.md 連結，禁巢狀引用
  - SKILL.md 本文僅增 ≤10 行指針段；execute/SKILL.md 已超官方 500 行上限，不得再實質增長
  - execute 的 Goal-Alignment Filter 與 failure_count 章節零 diff；review 的 Stage 5-7、
    learn 的 Stage 2-5 主流程零變更（現行路徑語義零變更，非 ultracode 行為與 1.5.0 一致）
  - depth 不變量語句（review-agent / perspective agent 不得再呼叫 skill、不得互審）
    每個 reference 檔 grep 計數 ≥2（現行 adapter 段與 Workflow adapter 段各一次）
  - Stage 0 偵測退化方案：ultracode 偵測（system-reminder）不可靠時，退化為「使用者顯式聲明才走 Workflow」；
    模式落盤後整輪不切換
  - Workflow 段只描述派發與收集（pipeline/parallel 派發、收同形結果），不複製業務規則 —
    lane-keeping/balance check/failure_count 記帳只在主流程寫一份
  - 不動 TDAID 與五平面語義（goal.md out-of-scope：execute 只加標注與薄 adapter 章節，不動 subagent 迴圈邏輯）
  - 倉內慣例：skill 英文本文、繁體中文使用者輸出，不得更動

Files:
  - plugins/baransu/skills/review/references/orchestration-interface.md   # 新增
  - plugins/baransu/skills/execute/references/orchestration-interface.md  # 新增
  - plugins/baransu/skills/learn/references/orchestration-interface.md    # 新增
  - plugins/baransu/skills/review/SKILL.md    # 修改：插入 ≤10 行指針段
  - plugins/baransu/skills/execute/SKILL.md   # 修改：插入 ≤10 行指針段（已超 500 行，不得實質增長）
  - plugins/baransu/skills/learn/SKILL.md     # 修改：插入 ≤10 行指針段
```
