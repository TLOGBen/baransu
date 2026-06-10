task_id: TASK-distribution-01
group: distribution
spec_dir: .claude/analyze/2026-06-10-baransu-v2-slim

Goal: |
  baransu 從 16 技能瘦身為 12 技能（裁除 grade/triage/bridge/dev 及全部附屬資產與發行面殘留），
  以 2.0.0 破壞性改版出貨。本 task 對應的驗收標準：
  - C8：雙 manifest description 為 12 技能、keywords/tags 無 dev/harness 殘留；CLAUDE.md 技能表
    12 列；README 工作流鏈改道；plugin.json version = 2.0.0。
  - C2（發行面部分）：以 word-boundary 模式掃描發行面（CLAUDE.md、README.md、雙 manifest），
    無任何指向被裁資產的功能性引用或行文殘留（upgrade/downgrade 等同形字樣不算）。
  - C7（關聯）：`/plugin validate` 通過。
  - Scope 包含面：CLAUDE.md、README、雙 manifest 改寫；升級註記與閘門語義降級寫入 release
    notes 草稿。Out of scope：對外發佈動作（git push、tag、marketplace 發佈）由使用者透過
    /ship 決定；deprecation stub / 別名不做。

Requirements: |
  REQ-001: 裁併與發行面清理
    描述：grade/triage/bridge/dev 四技能及其全部附屬資產自 repo 移除，且整個發行面
    （plugins/、tests/、CLAUDE.md、README、雙 manifest、codex/）無功能性殘留引用。

  REQ-005: 治理資產與出貨鏈
    描述：anti-patterns 容器與 verify-skills 驗證器就位，測試套件修剪後全綠，發行 metadata
    同步至 12 技能與 2.0.0。

Scenarios: |
  REQ-001 Scenario 2: 殘留掃描
    - Given 裁併與改寫完成
    - When 以 word-boundary 模式掃描發行面（`\bgrade\b|\btriage\b|\bbridge\b|baransu:dev|\bdev\b`
      經人工分類）
    - Then 無任何指向被裁資產的功能性引用；upgrade/downgrade/gradient 等同形字樣與 git 歷史不計

  REQ-001 Scenario 3: 曾安裝者升級路徑
    - Given 某環境曾依 harness 安裝流程在使用者層 settings.json 註冊三個 telemetry hooks
    - When 該環境升級至 2.0.0
    - Then release notes 含明確指示：自 settings.json 移除三個 hook 條目，否則每個 session
      會呼叫不存在的腳本

  REQ-005 Scenario 4: 發行 metadata
    - Given plugin.json description「sixteen governance skills」、marketplace.json 同樣字樣與 tags
    - When 同步完成
    - Then 兩 manifest 描述 12 技能、keywords/tags 無 dev/tdd/harness 殘留、plugin.json
      version = 2.0.0；CLAUDE.md 技能表 12 列；README 工作流鏈改道；`/plugin validate` 通過

  REQ-005 Scenario 3（與本 task 的時序關聯部分）: 測試修剪
    - test-claude-md-skills-table.sh 的 baseline 重生為 12 技能列 — 但 baseline 重生屬 verify 群
      （verify-02），本 task 只負責改完 CLAUDE.md 表後通知可重生

Task: |
  TASK-distribution-01: manifests／CLAUDE.md／README 同步
  需求追溯：REQ-001, REQ-005
  目標：發行 metadata 全面反映 12 技能與新治理資產。
  驗收標準：
  - [ ] plugin.json：description 「sixteen governance skills」→ twelve（敘述同步改寫，去 harness
        描述）；keywords 去 dev/tdd/harness 殘留；version = 2.0.0
  - [ ] marketplace.json：description/tags 同步；版本欄位與 plugin.json 一致
  - [ ] CLAUDE.md：技能表 12 列（去 grade/triage/bridge/dev 四列）；Layout 區塊 skills/agents
        清單更新；Non-obvious Invariants 中 harness/dev 專屬條目移除或改寫；
        「self-healing harness」相關敘述全面修訂
  - [ ] README：技能清單與兩條工作流鏈（/think→/dev→/ship、/hunt→/dev）改道為
        直接實作＋tdd.md
  - [ ] release notes 草稿（.claude/execute/ 工件）：含 16→12 清單、閘門語義降級聲明、
        settings.json 升級註記
  步驟（同步）：
  - [ ] 逐檔 Read → Edit；CLAUDE.md 表改完即通知 verify 群可重生 baseline
  - [ ] `claude plugin validate`（或 /plugin validate）通過
  前置群組：cut, reroute, contract, automation（本 task 執行時這些群組的最終態已就位）

Design: |
  發行面區塊角色（本次動作）：
  - 發行 metadata 區塊 = 雙 manifest、CLAUDE.md、README、codex/ → 全部同步至 12 技能
    （codex/ 重產屬 TASK-distribution-02，不在本 task）。
  - 執行序：Wave 4 distribution（manifests/CLAUDE/README/codex/bump）在 Wave 3 verify 之後，
    其後接「驗收: verify-skills + plugin validate + 套件全綠」。
  錯誤處理策略（與本 task 相關）：
  - settings.json 升級註記：寫入 release notes 草稿，不主動改使用者 settings。
  - release notes 草稿工件：由 distribution 群產出；必含三段 —
    (a) 16→12 清單與升級指示（曾安裝者自 settings.json 移除三個 telemetry hook 條目）
    (b) 閘門語義降級記錄（舊：小任務 TDD 閘 workflow-enforced；新：discipline-suggested；
        遷移指引：依 _shared/tdd.md 自建紅綠 task list）
    (c) 新治理資產一覽（Outcome Contract 四行頭、_shared/loop-contract.md、
        rules/anti-patterns.md、scripts/verify-skills.py）

Test: |
  E2E：
  - 插件可安裝：`claude plugin validate`（或 /plugin validate）→ 通過，無 schema 錯誤（C8）
  - 殘留掃描：word-boundary grep 發行面 → 僅同形字樣（人工分類清單為證）（C2）
  整合：
  - manifest ↔ 技能目錄一致：兩 manifest 描述 12 技能、keywords 乾淨、version 2.0.0 同步
  - CLAUDE.md 表 ↔ baseline：test-claude-md-skills-table.sh 以重生後 baseline 通過；表 12 列
  - baseline 重生序列：distribution-01 完成 CLAUDE.md 表同步 → verify-02 重生 baseline →
    重跑該測試（時序依賴明文，不可倒置）
  邊界條件：
  - word-boundary 掃描必須排除同形誤報（upgrade/downgrade/gradient/bridging 行文）；
    分類結果落盤為清單，不得以「grep 無輸出」單獨作為 C2 證據

Constraints: |
  - `claude plugin validate`（或 /plugin validate）必須通過，為本 task 步驟內的硬性驗收。
  - CLAUDE.md 修訂 Non-obvious Invariants 時：governance 群已新增一行指向
    rules/anti-patterns.md — 該行勿動、勿覆寫。
  - 改完 CLAUDE.md 技能表後即通知 verify 群可重生 test-claude-md-skills-table.sh baseline；
    baseline 重生與該測試重跑屬 verify-02，不在本 task 內做；時序不可倒置。
  - test-claude-md-skills-table.sh 現行斷言 14 列 — 此測試的修剪/重生屬 verify 群，
    本 task 不修改測試檔。
  - codex/ 鏡像重產屬 TASK-distribution-02，本 task 不碰 codex/。
  - release notes 草稿只寫升級指示，不主動修改使用者 settings.json。
  - 逐檔 Read → Edit（read-before-write）；surgical changes，每行修改可追溯到本 task 驗收標準。
  - 殘留判定採 word-boundary＋人工分類；upgrade/downgrade/gradient 等同形字樣與 git 歷史不計。
  - 不修改 .claude/analyze/ 下任何 spec 文件。

Files: |
  修改：
  - plugins/baransu/.claude-plugin/plugin.json
      description「sixteen governance skills」→ twelve（去 harness 敘述）；
      keywords 去 dev/tdd/harness 相關；version = 2.0.0
  - .claude-plugin/marketplace.json（repo 根）
      description/tags 同步；版本欄位與 plugin.json 一致
  - CLAUDE.md（repo 根）
      技能表去 grade/triage/bridge/dev 四列（12 列）；Layout 區塊 skills/agents 清單更新；
      Non-obvious Invariants 修訂（harness/dev 專屬條目移除或改寫；保留 governance 群新增的
      anti-patterns.md 指針行）；「sixteen governance skills (thirteen user-facing + three
      cron-driven self-healing harness skills)」開頭段等 harness 敘述全面修訂
  - README.md（repo 根）
      技能清單同步 12 技能；/think→/dev→/ship 與 /hunt→/dev 兩條工作流鏈改道為
      「直接實作＋_shared/tdd.md」
  新增：
  - .claude/execute/2026-06-10-baransu-v2-slim/execute/release-notes-draft.md
      （design.md 規定三段：16→12 清單＋settings.json 升級指示、閘門語義降級記錄、
        新治理資產一覽）
