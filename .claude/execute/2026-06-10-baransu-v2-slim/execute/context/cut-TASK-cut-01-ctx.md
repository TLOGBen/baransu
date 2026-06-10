# Context: TASK-cut-01（移除四技能目錄與代理）

```yaml
Goal: |
  baransu 從 16 技能瘦身為 12 技能：裁除從未實際運轉的自癒 harness（grade/triage/bridge）
  與最少使用的 dev 及其全部附屬資產。
  對應驗收標準 C1：`plugins/baransu/skills/` 僅含 12 個技能目錄＋ `_shared/`；
  grade/triage/bridge/dev 目錄、investigator-agent.md 全部不存在。
  （C1 其餘項目 — hooks .py、harness scripts、_shared 遙測 schema — 由 TASK-cut-02/03 負責。）

Requirements: |
  REQ-001: 裁併與發行面清理
  描述：grade/triage/bridge/dev 四技能及其全部附屬資產自 repo 移除，
  且整個發行面（plugins/、tests/、CLAUDE.md、README、雙 manifest、codex/）無功能性殘留引用。
  （本 task 僅負責其中「四技能目錄＋investigator-agent.md」的刪除；
  hooks/scripts/schema/測試刪除與殘留掃描由 cut-02/03 及後續群組承接。）

Scenarios: |
  REQ-001 Scenario 1: 附屬資產清除（與本 task 直接相關的部分）
  - Given: repo 處於 16 技能狀態
  - When: 裁併完成
  - Then: `plugins/baransu/skills/` 下不存在 grade/triage/bridge/dev 目錄；
    `agents/investigator-agent.md` 不存在
  - And: wiki-sync hook 行為不受影響（hooks.json 仍僅註冊 SessionEnd wiki-sync）

Task: |
  TASK-cut-01: 移除四技能目錄與代理（task-cut.md；前置群組：無）

  需求追溯：REQ-001
  目標：grade/triage/bridge/dev 技能目錄與 investigator-agent 自 plugins/ 消失。

  驗收標準：
  - [ ] `plugins/baransu/skills/{grade,triage,bridge,dev}/` 不存在
  - [ ] `plugins/baransu/agents/investigator-agent.md` 不存在
  - [ ] `ls plugins/baransu/skills/` = 12 技能目錄 + `_shared`

  步驟：
  刪除
  - [ ] `git rm -r` 四個技能目錄
  - [ ] `git rm plugins/baransu/agents/investigator-agent.md`

Design: |
  發行面區塊角色（與本 task 相關列）：
  - 技能層 `plugins/baransu/skills/`：16 個技能目錄 + `_shared/` → 本次刪 4
    （改 12、_shared 變更屬其他 task）
  - 代理層 `plugins/baransu/agents/`：13 個 agent 檔 → 刪 investigator-agent.md；
    review-agent.md 錨點改寫屬 reroute 群；其餘 11 個不動

  執行序：本 task 屬 Wave 1（cut 刪除面），為全管線最先行。
  刪除先行的理由：所有後續編輯的殘留掃描以「刪除後」狀態為基準；
  契約/自動化/治理三組在刪除完成後才可平行展開。

Test: |
  與本 task 相關的驗證點：
  - E2E「殘留掃描」以 Wave 1 刪除後狀態為基準（word-boundary grep 發行面，
    掃描本身由後續 verify 群執行）— 對應 C2
  - 整合驗證「manifest ↔ 技能目錄一致」要求技能目錄數 = 12 — 刪除四目錄是其前提
  - 整合驗證「wiki-sync 不受波及」：hooks.json 內容不變、wiki-sync.sh 零 diff —
    本 task 的刪除動作不得波及 hooks/
  - E2E「pytest import 健康檢查」於 Wave 1 刪除後即跑：
    `python3 -m pytest tests/scripts/ --collect-only` 無 import error
    （耦合測試刪除屬 cut-03，但本 task 刪除後不應自行引入新的 import 破壞）

Constraints: |
  - hooks.json 與 wiki-sync.sh 必須零 diff：本 task 只刪技能目錄與 agent 檔，
    不得觸碰 plugins/baransu/hooks/ 下任何檔案。
  - spec 目錄唯讀：不得修改 .claude/analyze/2026-06-10-baransu-v2-slim/ 下任何文件。
  - goal.md / requirement.md 語義不可改。
  - 僅刪除、不改寫：殘留引用的改寫（tdd.md、review-agent.md、CLAUDE.md、README、
    manifest 等）屬 reroute / distribution / verify 群組，本 task 不處理。
  - 代理層其餘 11 個 agent 檔不動。
  - 刪除使用 `git rm`（保留 git 歷史作為回收站；不提供 deprecation stub / 別名）。

Files: |
  刪除（無新增/修改）：
  - plugins/baransu/skills/grade/        （整個目錄，git rm -r）
  - plugins/baransu/skills/triage/       （整個目錄，git rm -r）
  - plugins/baransu/skills/bridge/       （整個目錄，git rm -r）
  - plugins/baransu/skills/dev/          （整個目錄，git rm -r）
  - plugins/baransu/agents/investigator-agent.md （git rm）
```
