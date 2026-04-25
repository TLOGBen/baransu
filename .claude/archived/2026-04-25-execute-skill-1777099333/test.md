# Test Strategy

## E2E 測試策略

執行 `/baransu:execute` 的完整流程需要一個真實的 Analyze spec 目錄和一個可執行的專案。E2E 測試以「觀察 final-report.md 的內容」作為驗收依據。

**E2E 啟動條件**：準備一個已完成 `/baransu:analyze` 的專案，確認 `.claude/analyze/{date}-{slug}/` 目錄存在且完整。

| 場景 | 起點 | 終點 | 對應 Criteria |
|------|------|------|--------------|
| 正常全流程（M 任務） | 提供有效 spec 目錄，DAG 寬度 1 | final-report.md 顯示 100% REQ 完成、E2E 通過 | Criteria 1–12 |
| XL 任務並行執行 | spec 有 4 個可並行群組 | 4 個 worktree 建立、merge 成功、final-report 無 blocked | Criteria 3–5 |
| 含 Blocked task | spec 包含一個蓄意設計為難以實作的 task | final-report.md 列出 blocked 項目，其他 task 仍完成 | Criteria 9 |
| spec 目錄不存在 | 以不存在路徑啟動 execute | 立即拒絕，輸出清楚錯誤訊息 | Criteria 2 |
| E2E 無啟動命令 | test.md 未標注 E2E 命令 | final-report.md 記錄「E2E 跳過」而非錯誤 | Criteria 9 |

---

## 整合測試策略

對各個 stage 和 subagent 互動進行驗證，不需要跑完整個 execute 流程。

| 測試目標 | 涉及層 | 關鍵驗證點 |
|---------|--------|-----------|
| confirm.md 建立 | Stage 0 + 工作文件 | 確認 confirm.md 含所有讀取的 spec 文件路徑 + 時間戳 |
| DAG 並行寬度計算 | Stage 1 + task-*.md | 給定已知 DAG，驗證 XL/L/M 分類正確 |
| Task Tool 建立 | Stage 2 + Task Tool | 確認所有 group × task 的 Task Tool 項目均已建立 |
| task-map.md 格式 | Stage 3 + 工作文件 | 每個 Task Tool ID 對應正確的 group/task/checklist |
| 摘要 subagent 輸出 | summarize-agent + context/{id}-ctx.md | 8 欄位均存在且只含與 task 相關的段落 |
| Impl subagent Red gate | impl-agent + 測試執行環境 | Red 測試必須先失敗才能繼續 Green |
| Review subagent 四層輸出 | review-agent（直接實作四層語義） | Review 結果正確映射到 advisory/packaged confirm/needs judgment/direct fix，不需呼叫外部 skill |
| smart-friend 觸發時機 | TDAID loop 失敗計數 | 確認第 2 次（非第 1 次）失敗後派 smart-friend |
| Merge Subagent 觸發 | Merge point + gitworktree | 並行 worktree 收斂後正確執行 merge |
| E2E Fix 並行派遣 | E2E stage | E2E 失敗時可派多個並行 E2E Fix subagent |
| final-report.md 完整性 | Stage 7 + 工作文件 | 報告包含 task 狀態、E2E 結果、blocked 項目、Final-Review 結論 |
| Agent-only skill 文件結構 | agents/*.md | 每個 agent 文件含 視角/目標/通用原則/禁忌，無角色扮演描述 |
| Agent 固定前綴順序 | agents/*.md + prompt cache | 每個 agent 文件的固定 prompt（視角/目標/通用原則/禁忌）位於動態參數注入點之前，不倒置 |
| impl-checklist 寫入操作 | review-agent + impl-checklist-{group}.md | Review 完成後 checklist 文件存在、task ID 對應正確、多次呼叫不污染先前條目 |
| smart-friend 成功後失敗計數重置 | TDAID loop 失敗計數 | smart-friend 介入後 Impl 通過時，failure 計數重置為 0（後續失敗從頭計）|
| plugin.json + README 結構驗證 | task-plugin-meta + plugin.json | skills 陣列包含 execute 條目（name/description/path）；README 包含 /baransu:execute 段落 |

---

## 關鍵邊界條件

以下邊界條件必須有測試覆蓋，各自對應需求：

- **spec 目錄存在但 requirement.md 缺失** — REQ-001：execute 應列出缺失文件並升級，不嘗試跳過繼續
- **DAG 所有群組無前置（全部可並行，寬度 = 群組總數）** — REQ-002：XL 分類時上限為 4 worktrees，超過 4 的群組序列化等待
- **DAG 最大寬度正好 = 4**（邊界值）— REQ-002：應正確分類為 XL，不誤判為 L
- **並行群組 A 和 B 的步驟均涉及同一個共用 utils 檔案** — REQ-002：pre-scan 偵測到重疊，序列化這兩個群組
- **Review 在第 1 次就回傳 needs judgment（最嚴重）** — REQ-003：第 1 次算作 failure #1，計數從此開始
- **Impl 失敗恰好 2 次（邊界值）** — REQ-004：第 2 次失敗後必須派 smart-friend，不能在第 3 次才派
- **smart-friend 介入後 Impl 通過** — REQ-004：成功路徑，failure 計數重置
- **smart-friend 介入後 Impl 仍失敗（第 3 次）** — REQ-004：立即 blocked，不再重試
- **merge 後測試不通過（Green 破壞）** — REQ-003：回派 Merge subagent 修到好，不直接進入 E2E
- **task A blocked，但 task B 無前置依賴於 A** — REQ-004：task B 繼續執行，不因 A blocked 而停頓
- **E2E Fix 失敗後重跑 E2E 仍失敗** — REQ-005：記錄到 final-report.md blocked，不無限重試
- **Final-Review 通過但有 advisory 等級發現** — REQ-005：advisory 記錄到報告，不觸發 Final-Fixer
- **所有 task 均 blocked（無法完成任何 task）** — REQ-005：final-report.md 完整記錄所有 blocked，不視為「崩潰」
- **摘要 subagent 提取時 design.md 有多個與 task 相關的 section** — REQ-006：只提取直接相關的段落，避免 context 過大
- **同一個 agent 在一次 execute 中被呼叫 20+ 次** — REQ-006：prompt cache 應在第 2 次呼叫後命中，不因多次呼叫累積 context
- **spec 目錄存在但 requirement.md 缺失，confirm.md 狀態** — REQ-001：confirm.md 應存在並記錄已讀取的檔案（goal.md 等），並在其中標注缺失的 requirement.md；不應是空文件或不存在
- **Merge 修復重試恰好 2 次（上限邊界值）** — REQ-003：第 2 次 Merge Subagent 後若 Green 仍不通過，升級用戶並標記 blocked；不應再重試第 3 次
- **task A blocked，task B 唯一前置群組為 A** — REQ-004：task B 應自動標記 cascade-blocked，不繼續等待 A，final-report.md 中 cascade-blocked 與直接 blocked 分別列出
