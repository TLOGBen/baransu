# Context: TASK-cut-02（移除 hooks 與 scripts）

```yaml
Goal: |
  baransu 從 16 技能瘦身為 12 技能：裁除從未實際運轉的自癒 harness（grade/triage/bridge）
  與最少使用的 dev 及其全部附屬資產與發行面殘留。
  本 task 對應刪除面範圍：「hooks 3 檔（903 行）、scripts 9 檔（2,889 行）」。
  對應驗收標準 C1（節錄）：「3 個 telemetry hooks（.py）、9 個 harness scripts …全部不存在」。

Requirements:
  - id: REQ-001
    title: 裁併與發行面清理
    description: |
      grade/triage/bridge/dev 四技能及其全部附屬資產自 repo 移除，且整個發行面
      （plugins/、tests/、CLAUDE.md、README、雙 manifest、codex/）無功能性殘留引用。

Scenarios:
  - req: REQ-001
    name: "Scenario 1: 附屬資產清除（與本 task 直接相關部分）"
    given: repo 處於 16 技能狀態
    when: 裁併完成
    then: |
      `hooks/` 僅剩 hooks.json 與 wiki-sync.sh；`scripts/` 下 9 個 harness 腳本不存在。
    and: wiki-sync hook 行為不受影響（hooks.json 仍僅註冊 SessionEnd wiki-sync）
  - req: REQ-001
    name: "Scenario 3: 曾安裝者升級路徑（背景知識，本 task 不負責 release notes）"
    given: 某環境曾依 harness 安裝流程在使用者層 settings.json 註冊三個 telemetry hooks
    when: 該環境升級至 2.0.0
    then: |
      release notes 含明確指示：自 settings.json 移除三個 hook 條目，
      否則每個 session 會呼叫不存在的腳本。（由 distribution 群產出）

Task:
  id: TASK-cut-02
  group: cut
  title: 移除 hooks 與 scripts
  需求追溯: REQ-001
  前置群組: 無
  目標: harness 執行層清空；wiki-sync 完整保留。
  驗收標準:
    - "`plugins/baransu/hooks/` 僅剩 hooks.json、wiki-sync.sh，兩檔零 diff"
    - "`plugins/baransu/scripts/` 目錄不存在（9 檔全刪後移除空目錄）"
  步驟:
    刪除:
      - "`git rm plugins/baransu/hooks/{user-prompt-submit.py,post-tool-use.py,stop.py}`"
      - "`git rm` scripts 9 檔：baseline-parity-score.py、bridge-replay.sh、check-invariants.sh、grade-collector.py、harness-reaper.py、health_check.py、push-gate.sh、render-auto-fix-prompt.py、triage-cluster.py"
    確認:
      - "`git diff --stat` 確認 hooks.json 與 wiki-sync.sh 未被觸碰"

Design: |
  執行層 `plugins/baransu/{hooks,scripts}/`（現況 hooks 5 檔、scripts 9 檔）本次動作：
  hooks 刪 3 留 2（hooks.json＋wiki-sync.sh）；scripts 全刪 9。
  驗證器位置決策（與本 task 的邊界）：新的 verify-skills.py 放 repo 根 `scripts/`
  （dev/CI 工具），不放 `plugins/baransu/scripts/` — 這讓
  「plugins/baransu/scripts/ 整個目錄刪空」成為乾淨的驗收條件。
  verify-skills.py 的新增不屬於本 task（屬 verify 群）。
  執行序：cut 群屬 Wave 1 刪除面，刪除先行 — 所有後續編輯的殘留掃描
  以「刪除後」狀態為基準。

Test: |
  與本 task 相關的驗證點：
  - 整合測試「wiki-sync 不受波及」（hooks 層）：hooks.json 內容不變；wiki-sync.sh 零 diff。
  - 整合測試「repo scripts/ 新建」（執行層）的後半條件：plugins/baransu/scripts/ 不存在。
  - E2E「pytest import 健康檢查」：`python3 -m pytest tests/scripts/ --collect-only`
    於 Wave 1 刪除後即跑，無 import error（耦合測試的刪除在 TASK-cut-03，
    本 task 完成後相關 .py 測試對象已不存在）。
  - E2E「殘留掃描」以 Wave 1 刪除後狀態為基準（掃描本身屬後續 wave）。
  邊界條件：
  - test-settings-registration.sh 是既有紅燈（斷言對象即本 task 所裁 hooks），
    其刪除屬 TASK-cut-03，不得記為「修復」。

Constraints:
  - "hooks.json 與 wiki-sync.sh 必須零 diff — 完全不觸碰，以 `git diff --stat` 為證（task 驗收 + test.md「wiki-sync 不受波及」）"
  - "hooks.json 仍僅註冊 SessionEnd wiki-sync，行為不受影響（REQ-001 Scenario 1）"
  - "`plugins/baransu/scripts/` 9 檔全刪後須移除空目錄，使目錄不存在成為驗收條件"
  - "只刪不增：verify-skills.py（repo 根 scripts/）由 verify 群新增，本 task 不碰"
  - "耦合測試檔（tests/hooks/ 4 檔、tests/scripts/ 等）的刪除屬 TASK-cut-03，本 task 不刪"
  - "release notes 升級指示（settings.json 移除三個 hook 條目）由 distribution 群產出，本 task 不寫"
  - "git 歷史是回收站 — 用 git rm 刪除，不做 deprecation stub / 別名（goal.md Out of scope）"

Files:
  delete:
    # hooks 3 檔
    - plugins/baransu/hooks/user-prompt-submit.py
    - plugins/baransu/hooks/post-tool-use.py
    - plugins/baransu/hooks/stop.py
    # scripts 9 檔（刪畢後移除 plugins/baransu/scripts/ 空目錄）
    - plugins/baransu/scripts/baseline-parity-score.py
    - plugins/baransu/scripts/bridge-replay.sh
    - plugins/baransu/scripts/check-invariants.sh
    - plugins/baransu/scripts/grade-collector.py
    - plugins/baransu/scripts/harness-reaper.py
    - plugins/baransu/scripts/health_check.py
    - plugins/baransu/scripts/push-gate.sh
    - plugins/baransu/scripts/render-auto-fix-prompt.py
    - plugins/baransu/scripts/triage-cluster.py
  keep_untouched:
    - plugins/baransu/hooks/hooks.json
    - plugins/baransu/hooks/wiki-sync.sh
```
