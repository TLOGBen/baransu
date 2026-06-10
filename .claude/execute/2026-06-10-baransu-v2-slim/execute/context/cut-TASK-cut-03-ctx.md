# Context: TASK-cut-03（group: cut）

```yaml
task_id: TASK-cut-03
group: cut
source_spec: .claude/analyze/2026-06-10-baransu-v2-slim

Goal: |
  baransu 從 16 技能瘦身為 12 技能，裁除自癒 harness（grade/triage/bridge）與 dev
  及其全部附屬資產。本 task 對應刪除面中的「_shared 三份遙測 schema＋約 28 個耦合測試檔」。
  相關驗收標準（goal.md）：
  - C1：_shared 三份遙測 schema 全部不存在（_shared/ 部分）。
  - C7（部分）：修剪後測試套件全綠的前置 — 刪除清單內測試檔不存在、pytest 收集無 import error。

Requirements:
  - id: REQ-001
    title: 裁併與發行面清理
    description: |
      grade/triage/bridge/dev 四技能及其全部附屬資產自 repo 移除，且整個發行面
      （plugins/、tests/、CLAUDE.md、README、雙 manifest、codex/）無功能性殘留引用。
  - id: REQ-005
    title: 治理資產與出貨鏈
    description: |
      anti-patterns 容器與 verify-skills 驗證器就位，測試套件修剪後全綠，
      發行 metadata 同步至 12 技能與 2.0.0。
      （本 task 僅承擔其中「測試修剪」的刪除部分；baseline 重生與 tdd_trigger
      修剪屬 verify 群，不在本 task。）

Scenarios:
  - req: REQ-001
    name: "Scenario 1: 附屬資產清除（與本 task 相關片段）"
    gwt: |
      Given repo 處於 16 技能狀態
      When 裁併完成
      Then `_shared/` 僅剩 tdd.md 與新增的 loop-contract.md
      （注：loop-contract.md 由 automation 群新增；本 task 完成時 _shared/ 僅含 tdd.md）
  - req: REQ-005
    name: "Scenario 3: 測試修剪"
    gwt: |
      Given 現有 37 個測試檔中約 28 個耦合被裁面（含今天就紅的 test-settings-registration.sh）
      When 修剪完成
      Then 刪除清單內的測試檔不存在；test-claude-md-skills-table.sh 的 baseline 重生為
      12 技能列；test_tdd_trigger.sh 與其 fixtures 修剪 dev 觸發點、保留
      impl-agent/review-agent 斷言
      And 修剪後套件（約 6-8 檔）一次跑全綠
      （注：baseline 重生與 tdd_trigger 修剪由 verify 群承接，本 task 只負責刪除清單）

Task:
  id: TASK-cut-03
  title: 移除遙測 schema 與耦合測試
  traceability: [REQ-001, REQ-005]
  objective: "_shared 只剩 tdd.md；測試層只剩存活清單與待修剪檔。"
  acceptance:
    - "`_shared/` 僅含 tdd.md（loop-contract.md 由 automation 群新增）"
    - "刪除清單 28 檔不存在；存活：test-claude-md-skills-table.sh＋baseline、
       test_tdd_trigger.sh＋fixtures（待 verify 群修剪）、test-install-deps-format.sh、
       test_check_design.py、test-book-skill-stage0.sh、test-write-skill.sh"
    - "`python3 -m pytest tests/scripts/ --collect-only` 無 import error"
  steps: |
    刪除 _shared schema：
    - git rm plugins/baransu/skills/_shared/{telemetry-schema.md,grade-triage-schema.md,state-json-schema.md}
    刪除測試（任務標題為 28 檔；步驟節逐檔列舉合計 27 檔，見 Files 欄注記）：
    - tests/agents/test-investigator-agent.sh
    - tests/hooks/ 全部 4 檔（post-tool-use、settings-registration、stop、user-prompt-submit）
    - tests/integration/test-check-invariants.sh、test-cron-runbook.sh
    - tests/scripts/：test-bridge-replay.sh、test-harness-reaper.sh、test-health-check.sh、
      test-push-gate.sh、test_grade_collector.py、test_state_partition.py、
      test_triage_cluster.py、test_render_auto_fix_prompt.py
    - tests/shared/ 全部 4 檔
    - tests/skills/：test-bridge-inconclusive.sh、test-bridge-skill.sh、test-grade-skill.sh、
      test-grade-tune-trigger.sh、test-triage-auto-fix-template.sh、test-triage-push-gates.sh、
      test-triage-skill.sh、test-triage-worktree-isolation.sh
    收尾：
    - 刪後空目錄（tests/hooks、tests/shared、tests/agents）移除
    - pytest collect-only 驗證無殘缺 import

Design: |
  - 系統架構（design.md 區塊表，與本 task 相關列）：
    * 技能層 _shared/：刪 3 schema、改 tdd.md（改寫屬 reroute 群）、增 loop-contract.md（屬 automation 群）。
    * 測試層 tests/：37 檔 → 刪 ~28、改 2（baseline 重生、tdd_trigger 修剪，屬 verify 群）、
      增 1（verify-skills 負向 fixture 測試，屬 verify 群）、留 ~6。
  - 執行序：本 task 屬 Wave 1（cut 刪除面），前置群組無；刪除先行的理由是
    後續所有編輯的殘留掃描以「刪除後」狀態為基準。
  - 錯誤處理（design.md）：測試修剪後若存活測試出現非預期紅燈，先判定是裁併破壞
    還是既有紅燈（test-settings-registration 是已知既有紅燈，刪除即可），
    不得為過閘而改測試斷言語義。

Test: |
  - 核心錨點（test.md E2E 表）：`python3 -m pytest tests/scripts/ --collect-only`
    （Wave 1 刪除後即跑）→ 無 import error；conftest/fixture 無殘缺（對應 C7）。
  - 邊界條件（test.md）：
    * 刪除 28 個測試檔後，pytest 對 tests/scripts/ 的收集不得因 conftest 或
      fixture 殘缺而報 import error — REQ-005。
    * test-settings-registration.sh 是既有紅燈（斷言對象即被裁 hooks），
      刪除它不得記為「修復」— REQ-005。
    * 存活測試出現非預期紅燈須先判定根因（既有 vs 裁併破壞），
      不得為過閘改斷言語義 — REQ-005。
  - 後續驗收（非本 task 執行，但本 task 是其前置）：修剪後套件逐一執行全綠、
    存活清單落盤（C7）。

Constraints:
  - 存活測試清單（不可誤刪）：
    * tests/integration/test-claude-md-skills-table.sh ＋ tests/integration/claude-md-skills-baseline.txt
    * tests/scripts/test_tdd_trigger.sh ＋其 fixtures（待 verify 群修剪，本 task 不動）
    * tests/scripts/test-install-deps-format.sh
    * tests/scripts/test_check_design.py
    * tests/skills/test-book-skill-stage0.sh
    * tests/skills/test-write-skill.sh
  - _shared/tdd.md 必須保留；本 task 不新增 loop-contract.md（automation 群負責）。
  - 不動 hooks/、scripts/（屬 TASK-cut-02 範圍）；不動 tdd.md 內容（屬 reroute 群）。
  - tests/shared/ 全部 4 檔均刪（含 test-harness-gitignore.sh）。
  - 空目錄收尾僅限 tests/hooks、tests/shared、tests/agents。
  - 不得為通過收集/閘門而修改任何存活測試的斷言語義。
  - 刪除 test-settings-registration.sh 不得記為「修復」既有紅燈。

Files:
  delete:
    # _shared 三 schema
    - plugins/baransu/skills/_shared/telemetry-schema.md
    - plugins/baransu/skills/_shared/grade-triage-schema.md
    - plugins/baransu/skills/_shared/state-json-schema.md
    # tests/agents（1）
    - tests/agents/test-investigator-agent.sh
    # tests/hooks（4）
    - tests/hooks/test-post-tool-use.sh
    - tests/hooks/test-settings-registration.sh
    - tests/hooks/test-stop.sh
    - tests/hooks/test-user-prompt-submit.sh
    # tests/integration（2）
    - tests/integration/test-check-invariants.sh
    - tests/integration/test-cron-runbook.sh
    # tests/scripts（8）
    - tests/scripts/test-bridge-replay.sh
    - tests/scripts/test-harness-reaper.sh
    - tests/scripts/test-health-check.sh
    - tests/scripts/test-push-gate.sh
    - tests/scripts/test_grade_collector.py
    - tests/scripts/test_state_partition.py
    - tests/scripts/test_triage_cluster.py
    - tests/scripts/test_render_auto_fix_prompt.py
    # tests/shared（4）
    - tests/shared/test-grade-triage-schema.sh
    - tests/shared/test-harness-gitignore.sh
    - tests/shared/test-state-json-schema.sh
    - tests/shared/test-telemetry-schema.sh
    # tests/skills（8）
    - tests/skills/test-bridge-inconclusive.sh
    - tests/skills/test-bridge-skill.sh
    - tests/skills/test-grade-skill.sh
    - tests/skills/test-grade-tune-trigger.sh
    - tests/skills/test-triage-auto-fix-template.sh
    - tests/skills/test-triage-push-gates.sh
    - tests/skills/test-triage-skill.sh
    - tests/skills/test-triage-worktree-isolation.sh
  remove_empty_dirs:
    - tests/agents/
    - tests/hooks/
    - tests/shared/
  note: |
    task-cut.md 標題稱「28 檔」，但步驟節逐檔列舉合計 27 個測試檔
    （1+4+2+8+4+8）；上列清單忠實轉錄步驟節，並以實際檔名
    （Glob 確認 tests/hooks、tests/shared 等目錄現況）補全簡稱。
    goal.md 亦寫「約 28 個耦合測試檔」。執行時以逐檔清單為準。
```
