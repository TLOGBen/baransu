# Tasks: cut（刪除面）
**前置群組**：無

## TASK-cut-01: 移除四技能目錄與代理

**需求追溯**：REQ-001
**目標**：grade/triage/bridge/dev 技能目錄與 investigator-agent 自 plugins/ 消失。
**驗收標準**：
- [ ] `plugins/baransu/skills/{grade,triage,bridge,dev}/` 不存在
- [ ] `plugins/baransu/agents/investigator-agent.md` 不存在
- [ ] `ls plugins/baransu/skills/` = 12 技能目錄 + `_shared`

### 步驟

#### 刪除
- [ ] `git rm -r` 四個技能目錄
- [ ] `git rm plugins/baransu/agents/investigator-agent.md`

## TASK-cut-02: 移除 hooks 與 scripts

**需求追溯**：REQ-001
**目標**：harness 執行層清空；wiki-sync 完整保留。
**驗收標準**：
- [ ] `plugins/baransu/hooks/` 僅剩 hooks.json、wiki-sync.sh，兩檔零 diff
- [ ] `plugins/baransu/scripts/` 目錄不存在（9 檔全刪後移除空目錄）

### 步驟

#### 刪除
- [ ] `git rm plugins/baransu/hooks/{user-prompt-submit.py,post-tool-use.py,stop.py}`
- [ ] `git rm` scripts 9 檔：baseline-parity-score.py、bridge-replay.sh、check-invariants.sh、grade-collector.py、harness-reaper.py、health_check.py、push-gate.sh、render-auto-fix-prompt.py、triage-cluster.py

#### 確認
- [ ] `git diff --stat` 確認 hooks.json 與 wiki-sync.sh 未被觸碰

## TASK-cut-03: 移除遙測 schema 與耦合測試

**需求追溯**：REQ-001, REQ-005
**目標**：_shared 只剩 tdd.md；測試層只剩存活清單與待修剪檔。
**驗收標準**：
- [ ] `_shared/` 僅含 tdd.md（loop-contract.md 由 automation 群新增）
- [ ] 刪除清單 28 檔不存在；存活：test-claude-md-skills-table.sh＋baseline、test_tdd_trigger.sh＋fixtures（待 verify 群修剪）、test-install-deps-format.sh、test_check_design.py、test-book-skill-stage0.sh、test-write-skill.sh
- [ ] `python3 -m pytest tests/scripts/ --collect-only` 無 import error

### 步驟

#### 刪除 _shared schema
- [ ] `git rm plugins/baransu/skills/_shared/{telemetry-schema.md,grade-triage-schema.md,state-json-schema.md}`

#### 刪除測試（28 檔）
- [ ] tests/agents/test-investigator-agent.sh
- [ ] tests/hooks/ 全部 4 檔（post-tool-use、settings-registration、stop、user-prompt-submit）
- [ ] tests/integration/test-check-invariants.sh、test-cron-runbook.sh
- [ ] tests/scripts/：test-bridge-replay.sh、test-harness-reaper.sh、test-health-check.sh、test-push-gate.sh、test_grade_collector.py、test_state_partition.py、test_triage_cluster.py、test_render_auto_fix_prompt.py
- [ ] tests/shared/ 全部 4 檔
- [ ] tests/skills/：test-bridge-inconclusive.sh、test-bridge-skill.sh、test-grade-skill.sh、test-grade-tune-trigger.sh、test-triage-auto-fix-template.sh、test-triage-push-gates.sh、test-triage-skill.sh、test-triage-worktree-isolation.sh

#### 收尾
- [ ] 刪後空目錄（tests/hooks、tests/shared、tests/agents）移除
- [ ] pytest collect-only 驗證無殘缺 import
