# Tasks: automation（loop-contract＋雙模單一介面＋標注）
**前置群組**：cut

## TASK-automation-01: _shared/loop-contract.md

**需求追溯**：REQ-004
**目標**：loop/cron/Workflow 驅動下的技能行為契約成文。
**驗收標準**：
- [ ] 規則段：Input PAUSE 取推薦預設＋報告標注；Authorization PAUSE 無條件硬停；「驅動上下文覆寫平台預設，Authorization 不可覆寫」優先序明文（引用全域 platform-awareness，不複述第三份）
- [ ] 三硬停責任分界：迭代上限/無進展/預算歸驅動方；技能側義務=可重入＋狀態落盤（.claude/<skill>/）＋無進展明確回報
- [ ] PAUSE 分類表：review/execute/learn 逐互動點標注 Input/Authorization 與預設值；think 列為「不可 loop 驅動」

### 步驟

#### 撰寫
- [ ] Read review/execute/learn 三份 SKILL.md，枚舉全部 AskUserQuestion/確認點
- [ ] 逐點分類（例：review 需判斷裁決=Authorization；learn 評分確認=Input、預設=全部保留；execute 的 E2E 失敗處置=Authorization）
- [ ] 撰寫 loop-contract.md；Read 全域 platform-awareness 規則確認引用而非複述

## TASK-automation-02: 三技能雙模「單一介面＋薄 adapter」references 檔

**需求追溯**：REQ-004
**目標**：review/execute/learn 各增 `references/orchestration-interface.md`（一層深），SKILL.md 留 ≤10 行指針段；現行路徑語義零變更。
**驗收標準**：
- [ ] 各技能 references/orchestration-interface.md 含介面契約：回傳同形（review=findings schema；execute=review-agent 回傳形狀，Goal-Alignment Filter/failure_count 章節零 diff；learn=候選池 {path,lane} 形狀）
- [ ] Stage 0 模式釘死：偵測 ultracode（system-reminder）→ 落盤 → 整輪不切換；偵測不可靠退化為顯式聲明
- [ ] depth 不變量在現行 adapter 與 Workflow adapter 兩段各重述一次（grep 每個 reference 檔 ≥2 處）
- [ ] Workflow 段只描述派發與收集，不複製業務規則（lane-keeping/balance/記帳只在主流程一份）
- [ ] SKILL.md 本文僅增 ≤10 行指針段（官方 500 行上限考量；execute 已超限，不得再實質增長）

### 步驟

#### 撰寫
- [ ] 逐檔 Read → 撰寫 references/orchestration-interface.md → SKILL.md 插入指針段
- [ ] diff 自查：execute 的 filter/failure_count 章節、review 的 Stage 5-7、learn 的 Stage 2-5 主流程零變更

## TASK-automation-03: 12 技能雙軸相容標注（契約區塊內）

**需求追溯**：REQ-004
**目標**：每個存活 SKILL.md 的 Outcome Contract 區塊內帶一行自動化標注（ultracode: overlap/assist/neutral × loop: drivable/assisted/not-drivable）。
**驗收標準**：
- [ ] 12 檔均有標注，分級與計畫表一致（review/execute/learn=overlap+drivable；hunt/analyze/codex-skill-transfer=assist；think=neutral+not-drivable；write/ship/read/book/design=neutral）
- [ ] 標注位於 SKILL.md 本文契約區塊（第五行「Automation: …」），不使用非標準 frontmatter 欄位（官方跨平台相容建議；亦確保 codex transfer 不丟失）
- [ ] hunt/analyze 增一句「ultracode 時可派 Workflow 平行探查/調研」提示與 loop-mode 預設值句

### 步驟

#### 標注
- [ ] 逐檔 Edit 契約區塊；hunt/analyze 加提示句（與 TASK-contract 協調：contract 群先落四行，本 task 補第五行）
