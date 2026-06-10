# Context: TASK-reroute-01（tdd.md 整併為唯一知識源）

```yaml
Goal: |
  baransu 16 技能瘦身為 12 技能（裁 grade/triage/bridge/dev），以 2.0.0 破壞性改版出貨。
  本 task 屬改寫面：_shared/tdd.md（閘門文字併入、§8 去 dev、scope 行去 /dev），
  使 dev 移除後 TDD 紀律維持單一知識源。
  相關驗收標準：
  - C2：word-boundary 掃描發行面無任何指向被裁資產的功能性引用或行文殘留。

Requirements: |
  REQ-002: TDD 知識源整併與交接改道
  描述：dev 移除後，TDD 紀律維持單一知識源（_shared/tdd.md），所有原指向 dev 的
  交接與語義錨點改道，且閘門語義降級被明文記錄。

Scenarios: |
  REQ-002 Scenario 1: 單一知識源
  - Given: _shared/tdd.md 是自宣告的 TDD 單一知識來源
  - When: 整併完成
  - Then: dev 的 Red→Green 硬閘行為描述併入 tdd.md；不存在 tdd-gate.md 等第二份 TDD 檔
  - And: 「compile error 不計入 failure_count」的權威表述僅存在於 execute/SKILL.md
    （tdd.md 只引用不複製）

  REQ-002 Scenario 3: review-agent 錨點（下游依賴本 task 產出的段落）
  - Given: agents/review-agent.md:71 的 cosmetic path 四分類語義錨定在 dev/SKILL.md Stage 0
  - When: dev 移除
  - Then: 該錨點改掛 _shared/tdd.md 內的對應段落，review-agent 語義不變（/execute 管線不受影響）
  （錨點改掛動作屬 TASK-reroute-02，但 tdd.md 須在本 task 提供可被錨定的對應段落）

  REQ-002 Scenario 4: 降級記錄
  - Given: 小任務 TDD 閘原為 workflow-enforced（dev 的 TaskCreate 四工項＋紅燈確認）
  - When: 2.0.0 release notes 撰寫
  - Then: 明文記載「小任務 TDD 閘降級為 discipline-suggested（文件紀律）」
  （release notes 草稿由 distribution 群產出，非本 task 交付；本 task 的整併文字
  須與此降級語義一致 — 紅綠閘在 tdd.md 中是 discipline，不是 workflow gate）

Task: |
  TASK-reroute-01: tdd.md 整併為唯一知識源（群組 reroute，前置群組：cut）
  需求追溯：REQ-002
  目標：dev 的閘門紀律併入 _shared/tdd.md，無第二份 TDD 檔，failure_count 權威不複製。

  驗收標準：
  - [ ] tdd.md 含「直接實作時的紅綠閘」段落（自建紅綠 task list、先紅後綠、紅燈確認再實作）
  - [ ] tdd.md scope 行與 §8 觸發點表僅列存活消費者（impl-agent、review-agent、think/hunt 改道句）
  - [ ] 「compile error 不計入 failure_count」在 tdd.md 中僅以「見 execute/SKILL.md」形式出現，
        全倉權威表述恰一處
  - [ ] 不存在 tdd-gate.md

  步驟（整併）：
  - [ ] Read tdd.md 全文與 dev/SKILL.md 閘門段（自 git 歷史或裁前快照取 dev 文字）
  - [ ] 撰寫「直接實作時的紅綠閘」段，融入既有結構（不重複既有原則）
  - [ ] scope 行去 /dev、§8 表去 dev 列、加 think/hunt 改道列

Design: |
  執行序：本 task 屬 Wave 2（reroute），在 Wave 1（cut 刪除面）之後執行 —
  dev/SKILL.md 已被刪除，dev 原文須自 git 歷史取。
  Wave 2 的 reroute 完成後才進 Wave 3（verify：驗證器＋測試修剪，含 test_tdd_trigger 修剪）。

  技能層動作（與本 task 相關部分）：`_shared` 刪 3 schema、改 tdd.md、增 loop-contract.md。
  整併完成後 `_shared/` 僅剩 tdd.md 與新增的 loop-contract.md（REQ-001 Scenario 1）。

  release notes 降級記錄（design.md 錯誤處理策略）：release notes 草稿工件由
  distribution 群產出，存放 `.claude/execute/release-notes-draft.md`；必含三段 —
  (a) 16→12 清單與升級指示（曾安裝者自 settings.json 移除三個 telemetry hook 條目）、
  (b) 閘門語義降級記錄（舊：小任務 TDD 閘 workflow-enforced；新：discipline-suggested；
      遷移指引：依 _shared/tdd.md 自建紅綠 task list）、
  (c) 新治理資產一覽。
  本 task 的「直接實作時的紅綠閘」段落即 (b) 遷移指引的落地對象。

Test: |
  整合測試（test.md「tdd.md 整併後消費者」列）：
  - impl-agent/review-agent 對 tdd.md 的既有引用行不變
  - tdd.md §8 觸發表僅剩存活消費者
  - test_tdd_trigger.sh 修剪後通過（修剪動作屬 verify 群：修剪 dev 觸發點、
    保留 impl-agent/review-agent 斷言）

  整合測試（test.md「review-agent 錨點改掛後 execute 管線語義」列）：
  - review-agent.md 的 cosmetic 四分類引用 _shared/tdd.md 對應段落
  - execute/SKILL.md 的 Goal-Alignment Filter 與 failure_count 章節零變更（diff 為證）

  邊界條件：
  - failure_count compile-error 規則在全倉的權威表述恰好一處（execute/SKILL.md），
    tdd.md 僅引用 — REQ-002
  - 改寫後 grep 零 `baransu:dev` 與 `\.claude/dev` 功能性引用（word-boundary）— REQ-002

Constraints:
  - 「compile error 不計入 failure_count」權威表述全倉恰一處：execute/SKILL.md（:161、:537）。
    tdd.md 僅以「見 execute/SKILL.md」形式引用，不得複製規則內文。
  - 不得建立 tdd-gate.md 或任何第二份 TDD 檔。
  - dev/SKILL.md 已在 cut 波次刪除；dev 閘門段原文須自 git 歷史取 —
    `git show b09b093:plugins/baransu/skills/dev/SKILL.md`。
  - execute/SKILL.md 本 task 零 diff（僅被引用，不修改）。
  - 新段落須融入 tdd.md 既有結構，不重複既有原則。
  - 紅綠閘語義為 discipline-suggested（文件紀律），不得寫成 workflow-enforced 閘門
    （與 REQ-002 Scenario 4 降級記錄一致）。
  - tdd.md scope 行與 §8 表僅列存活消費者：impl-agent、review-agent、think/hunt 改道句；
    去除 /dev 與 dev 列。
  - 新段落須可供 reroute-02 的 review-agent.md:71 cosmetic 四分類錨點改掛
    （提供對應 dev Stage 0 語義的段落）。
  - CLAUDE.md 不變量：failure_count excludes compile errors —
    compile error 不計入 3-strike TDAID block limit，兩計數器不得合併。

Files:
  modify:
    - plugins/baransu/skills/_shared/tdd.md
  read_only_sources:
    - "git show b09b093:plugins/baransu/skills/dev/SKILL.md"  # dev 閘門段原文（已刪檔）
    - plugins/baransu/skills/execute/SKILL.md  # failure_count 權威表述（:161、:537），零 diff
  must_not_create:
    - plugins/baransu/skills/_shared/tdd-gate.md
```
