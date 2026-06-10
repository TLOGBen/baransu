```yaml
task_id: TASK-reroute-02
group: reroute
source_spec: .claude/analyze/2026-06-10-baransu-v2-slim

Goal: |
  baransu 16 技能瘦身為 12 技能（裁除 grade/triage/bridge/dev）。本 task 屬改寫面：
  think:175,381、hunt:230、review:210、ship 的 .claude/dev/ 通道、agents/review-agent.md:71
  錨點、codex-skill-transfer 兩處行文 — 全部脫離 dev 引用，語義不變。
  對應驗收標準 C2：以 word-boundary 模式掃描發行面（plugins/、tests/、CLAUDE.md、README.md、
  雙 manifest；排除 git 歷史），無任何指向被裁資產的功能性引用或行文殘留
  （upgrade/downgrade 等同形字樣不算）。

Requirements: |
  REQ-002: TDD 知識源整併與交接改道
  描述：dev 移除後，TDD 紀律維持單一知識源（_shared/tdd.md），所有原指向 dev 的交接與
  語義錨點改道，且閘門語義降級被明文記錄。

Scenarios: |
  REQ-002 Scenario 2: 交接改道
  - Given: think/SKILL.md:381（Stage G 小任務交接）與 hunt/SKILL.md:230（單點修改交接）
    原指向 /baransu:dev
  - When: 使用者走到該交接點
  - Then: 指引為「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」
  - And: think/SKILL.md:175 的 stage 總覽、review/SKILL.md:210 的字樣、
    ship 的 .claude/dev/ 歸檔通道同步更新

  REQ-002 Scenario 3: review-agent 錨點
  - Given: agents/review-agent.md:71 的 cosmetic path 四分類語義錨定在 dev/SKILL.md Stage 0
  - When: dev 移除
  - Then: 該錨點改掛 _shared/tdd.md 內的對應段落，review-agent 語義不變
    （/execute 管線不受影響）

  關聯 REQ-001 Scenario 2（殘留掃描，本 task 涉及部分）：
  - codex-skill-transfer 的 transfer.py:819 註解與 SKILL.md:116 舉例已改寫或移除

Task: |
  TASK-reroute-02: 四處交接與錨點改道（位於 task-reroute.md；前置群組：cut）
  需求追溯：REQ-002
  目標：think/hunt/review/ship/review-agent 全部脫離 dev 引用，語義不變。

  驗收標準：
  - [ ] think/SKILL.md:381 與 :175：小任務 → 「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」
  - [ ] hunt/SKILL.md:230：同上改道
  - [ ] review/SKILL.md:210：regression-first 歸屬句改為「/baransu:execute 或依 tdd.md 的直接實作」
  - [ ] ship/SKILL.md：.claude/dev/ 自歸檔清單移除，其餘目錄行為不變
  - [ ] agents/review-agent.md:71：cosmetic 四分類錨點改掛 tdd.md 對應段；execute/SKILL.md 零 diff
  - [ ] codex-skill-transfer/SKILL.md:116 舉例與 scripts/transfer.py:819 註解改寫（換存活例子）

  步驟（改道）：
  - [ ] 逐檔 Read → Edit 上列七處
  - [ ] word-boundary grep `baransu:dev` 與 `\.claude/dev` 確認 plugins/ 內零殘留

Design: |
  技能層動作（design.md 系統架構表）：刪 4 技能、改 12；代理層改 review-agent.md 錨點，
  其餘 11 個 agent 不動。
  執行序：本 task 屬 Wave 2（reroute TDD 整併改道），前置 Wave 1（cut 刪除面）已完成 —
  所有殘留掃描以「刪除後」狀態為基準。
  錯誤處理（與本 task 相關）：release notes 草稿由 distribution 群產出，含閘門語義降級記錄
  （舊：小任務 TDD 閘 workflow-enforced；新：discipline-suggested；遷移指引：依 _shared/tdd.md
  自建紅綠 task list）— 本 task 的改道語式須與該遷移指引一致。

Test: |
  整合測試（test.md）：
  - review-agent 錨點改掛後 execute 管線語義：review-agent.md 的 cosmetic 四分類引用
    _shared/tdd.md 對應段落；execute/SKILL.md 的 Goal-Alignment Filter 與 failure_count
    章節零變更（diff 為證）。
  - tdd.md 整併後消費者：impl-agent/review-agent 對 tdd.md 的既有引用行不變。

  關鍵邊界條件（test.md）：
  - 改道內容驗證：reroute-02 的 7 處改寫點（think:381/175、hunt:230、review:210、ship、
    review-agent:71、codex-skill-transfer 兩處）改寫後須引用「_shared/tdd.md」或
    「直接實作」語式；grep 零 `baransu:dev` 與 `\.claude/dev` 功能性引用 — REQ-002
  - word-boundary 掃描必須排除同形誤報（upgrade/downgrade/gradient/bridging 行文）；
    不得以「grep 無輸出」單獨作為 C2 證據 — REQ-001
  - ship 的歸檔通道移除 .claude/dev/ 後，對其餘目錄（tmp/analyze/execute/think）的
    歸檔行為不變 — REQ-002

Constraints:
  - "execute/SKILL.md 零 diff：review-agent 錨點改掛不得波及 execute 的 Goal-Alignment Filter 與 failure_count 章節"
  - "改道語式固定：「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」（與 release notes 遷移指引一致）"
  - "review/SKILL.md:210 語式固定：「/baransu:execute 或依 tdd.md 的直接實作」"
  - "ship 移除 .claude/dev/ 通道後，tmp/analyze/execute/think 等其餘目錄歸檔行為不變"
  - "codex-skill-transfer 兩處改寫須換成存活技能的例子，不得留 dev 同義殘影"
  - "「compile error 不計入 failure_count」全倉權威表述恰一處（execute/SKILL.md）；本 task 不得新增複本"
  - "review-agent 語義不變：cosmetic path 四分類僅換錨點，不改分類邏輯"
  - "word-boundary grep 確認 plugins/ 內零 baransu:dev 與 .claude/dev 功能性引用；同形字樣（upgrade/downgrade 等）不算"
  - "前置依賴：cut 群組（Wave 1 刪除面）與 TASK-reroute-01（tdd.md 整併）— 改道錨點掛載的 tdd.md 對應段落須已存在"

Files:
  - path: plugins/baransu/skills/think/SKILL.md
    action: modify
    note: ":381 Stage G 小任務交接 與 :175 stage 總覽 — 改為「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」（共兩處）"
  - path: plugins/baransu/skills/hunt/SKILL.md
    action: modify
    note: ":230 單點修改交接 — 同 think 改道語式"
  - path: plugins/baransu/skills/review/SKILL.md
    action: modify
    note: ":210 regression-first 歸屬句 — 改為「/baransu:execute 或依 tdd.md 的直接實作」"
  - path: plugins/baransu/skills/ship/SKILL.md
    action: modify
    note: ".claude/dev/ 自歸檔清單移除；其餘目錄（tmp/analyze/execute/think）行為不變"
  - path: plugins/baransu/agents/review-agent.md
    action: modify
    note: ":71 cosmetic 四分類錨點 — 由 dev/SKILL.md Stage 0 改掛 _shared/tdd.md 對應段落"
  - path: plugins/baransu/skills/codex-skill-transfer/SKILL.md
    action: modify
    note: ":116 舉例改寫（換存活技能例子）"
  - path: plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py
    action: modify
    note: ":819 註解改寫（換存活技能例子）"
```
