# Impl Checklist: cut

前置群組：無

## TASK-cut-01: 移除四技能目錄與代理

需求追溯：REQ-001
- [x] `plugins/baransu/skills/{grade,triage,bridge,dev}/` 不存在
- [x] `plugins/baransu/agents/investigator-agent.md` 不存在
- [x] `ls plugins/baransu/skills/` = 12 技能目錄 + `_shared`

Review 結果：advisory
備註：三條驗收標準於 worktree 重跑 bash 斷言全數通過（exit 0）；hooks/ 零 diff、spec 目錄未動、其餘 12 agent 檔保留、staged diff 僅 6 個 D 條目無越界。pytest collect-only 47 tests 無 import error。Advisory：tests/scripts/ 內 grade/triage 耦合測試目前仍綠係因 plugins/baransu/scripts/ 尚存，cut-02（刪 scripts/）與 cut-03（刪耦合測試）需注意波次間的 import 健康。

---

## TASK-cut-02: 移除 hooks 與 scripts

需求追溯：REQ-001
- [x] `plugins/baransu/hooks/` 僅剩 hooks.json、wiki-sync.sh，兩檔零 diff
- [x] `plugins/baransu/scripts/` 目錄不存在（9 檔全刪後移除空目錄）

Review 結果：advisory
備註：worktree 重跑 6 條斷言全綠（exit 0）：hooks/ 僅剩兩檔、兩檔對 HEAD 零 diff（`git diff HEAD` 空）、scripts/ 目錄不存在、staged 刪除恰為本 task 12 檔、hooks.json 仍僅註冊 SessionEnd wiki-sync、無越界 untracked 新增。`pytest tests/scripts/ --collect-only` 47 tests 收集無 import error（exit 0）。Advisory：tests/scripts/ 耦合測試（test_grade_collector / test_triage_cluster 等）collect 仍綠但 run 時必紅（測試對象腳本已刪），cut-03 須如期刪除以免 Wave 1 後段紅燈誤判；test-settings-registration.sh 既有紅燈依 ctx 邊界不記為修復。

---

## TASK-cut-03: 移除遙測 schema 與耦合測試

需求追溯：REQ-001, REQ-005
- [x] `_shared/` 僅含 tdd.md（loop-contract.md 由 automation 群新增）
- [x] 刪除清單 28 檔不存在；存活：test-claude-md-skills-table.sh＋baseline、test_tdd_trigger.sh＋fixtures（待 verify 群修剪）、test-install-deps-format.sh、test_check_design.py、test-book-skill-stage0.sh、test-write-skill.sh
- [x] `python3 -m pytest tests/scripts/ --collect-only` 無 import error

Review 結果：advisory
備註：worktree 重跑斷言全綠（exit 0）：`ls _shared/` = tdd.md 單檔；ctx 逐檔清單 30 路徑（3 schema＋27 測試檔，checklist「28 檔」依 ctx note 以 27 檔逐檔清單語意覆蓋判定）全數不存在；存活六項（含 baseline 與 tdd-trigger fixtures 3 檔）俱在；空目錄僅 tests/agents、tests/hooks、tests/shared 移除，未越界。`pytest tests/scripts/ --collect-only` 收集 14 tests、exit 0、無 import error。staged 共 48 D（18 既有＋本任務 30），無 M/A 越界條目；test-settings-registration 僅刪除、未記為修復，符合 ctx 邊界。Advisory：tests/scripts/__pycache__/ 殘留 5 個已刪模組的舊 .pyc（untracked、不影響收集），可由 verify 群或 /ship 收尾時清除。
