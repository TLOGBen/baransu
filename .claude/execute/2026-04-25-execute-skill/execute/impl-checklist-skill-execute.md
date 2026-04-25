# Impl Checklist: skill-execute

前置群組：agents-tdaid, agents-completion

---

## TASK-skill-execute-01: SKILL.md Stage 0–3（設定、DAG 分析、任務建立）
需求追溯：REQ-001, REQ-002
- [ ] `plugins/baransu/skills/execute/SKILL.md` 存在，前三個 stage 內容完整
- [ ] Stage 0 明確說明：讀取 spec 文件的順序、confirm.md 的寫入規則、缺少文件時的拒絕流程
- [ ] Stage 1 明確說明：從 task-*.md 的 `前置群組` 欄位建 DAG、計算最大並行前沿寬度、XL/L/M 分類表（≥4/2–3/1）、pre-scan 檔案重疊偵測
- [ ] Stage 2 明確說明：Task Tool Create 的呼叫時機（全部任務先建立再執行）、task 命名規範
- [ ] Stage 3 明確說明：task-map.md 的格式與寫入時機、impl-checklist-{group}.md 的初始化規則
- [ ] 所有 Stage 的指令說明對象是「執行此 skill 的 agent」（英文 body，繁中 output）
Review 結果：
備註：

---

## TASK-skill-execute-02: SKILL.md Stage 4（TDAID Loop 編排）
需求追溯：REQ-003, REQ-004
- [ ] Stage 4 內容完整描述單一 task 的執行序列（摘要→Impl→Review 的 while loop）
- [ ] 明確說明失敗計數規則：compile error 不計數；Review packaged confirm 以上計一次
- [ ] 明確說明 smart-friend 觸發條件：第 2 次失敗後（非第 1 次，非第 3 次）
- [ ] 明確說明 blocked 觸發條件：第 3 次失敗後立即標記，不再重試
- [ ] 明確說明 Merge point 流程：並行群組結束後 Merge Subagent → Green 確認 → 下一批
- [ ] 明確說明 Refactor stage：M 跳過，L/XL Review 判定需要時最多一次
- [ ] 明確說明 Spec 矛盾的升級流程
- [ ] Stage 4 的 subagent 呼叫格式一致（每次派遣說明傳入什麼參數、期望什麼回傳）
Review 結果：
備註：

---

## TASK-skill-execute-03: SKILL.md Stage 5–7（E2E、Final-Review、結束）
需求追溯：REQ-005
- [ ] Stage 5 描述 E2E 執行條件（所有 worktree 已 merge 回 main）
- [ ] Stage 5 描述：從 test.md 讀取 E2E 啟動命令 → Monitor tool 執行 → E2E Fix subagent 處理失敗
- [ ] Stage 5 描述：test.md 無啟動命令時跳過並記錄的規則
- [ ] Stage 6 描述 Final-Review subagent 呼叫規則與 Coverage Report 讀取
- [ ] Stage 6 描述 Final-Fixer 觸發條件（有 ❌ REQ-XXX）和重跑 Final-Review 的循環（最多一次）
- [ ] Stage 7 描述 final-report.md 的完整格式（task 狀態、E2E 結果、blocked 清單、Final-Review 結論）
- [ ] Stage 7 描述 session 結束時清理 worktree 分支的規則
Review 結果：
備註：
