# Goal

## 目標（Goal）
在 baransu plugin 中新增 `/baransu:execute` skill：讀取 `/baransu:analyze` 產出的 spec 目錄，以 agent-only skill 架構驅動完整 TDAID 開發流程（並行 worktree + E2E + Final-Review），直到 Requirements 100% 通過為止。

## 驗收標準（Criteria）

- [ ] `skills/execute/SKILL.md` 存在，可被 baransu plugin 識別和啟動
- [ ] execute 啟動時讀取 `.claude/analyze/{date}-{slug}/` 目錄，缺少必要 spec 文件時拒絕執行
- [ ] `confirm.md` 在啟動時寫入，記錄所有已讀取 Analyze spec 檔案的路徑 + 時間戳
- [ ] execute 從 `前置群組` DAG 算出最大並行寬度，正確分類 XL（≥4）/L（2–3）/M（1）
- [ ] 每個並行 Impl Workflow 在獨立 gitworktree 中執行
- [ ] TDAID loop（摘要 subagent → Impl subagent → Review subagent）的往返由主 skill while loop 控制，不依賴 subagent 雙向通訊
- [ ] 失敗 2 次後自動派 smart-friend subagent；第 3 次仍失敗後標記 blocked 並升級用戶
- [ ] E2E 測試和 Final-Review 在所有 worktree merge 回 main 後執行
- [ ] `final-report.md` 包含所有 task 的 ✅/❌ 狀態、E2E 結果、blocked 項目與建議
- [ ] 8 個 agent-only skill 文件均存在於 `agents/`，固定 prompt 在文件開頭以命中 prompt cache
- [ ] Review 阻斷使用 /review 四層語義（packaged confirm 以上觸發阻斷）
- [ ] `plugin.json` 版本號升級，`README.md` 新增 /execute skill 說明

## 範圍（Scope）

### 包含（In scope）
- `plugins/baransu/skills/execute/SKILL.md`
- `plugins/baransu/agents/summarize-agent.md`（摘要 subagent — 提取 8 欄位 task context）
- `plugins/baransu/agents/impl-agent.md`（Impl subagent — Red/Green TDD）
- `plugins/baransu/agents/review-agent.md`（Review subagent — 呼叫 /baransu:review）
- `plugins/baransu/agents/smart-friend-agent.md`（失敗方向對焦 subagent）
- `plugins/baransu/agents/e2e-fix-agent.md`（E2E Fix subagent）
- `plugins/baransu/agents/final-review-agent.md`（Final-Review subagent）
- `plugins/baransu/agents/final-fixer-agent.md`（Final-Fixer subagent）
- `plugins/baransu/agents/merge-agent.md`（Merge subagent — worktree merge + Green 確認）
- `plugins/baransu/.claude-plugin/plugin.json` 版本升級
- `README.md` 新增 /execute 說明

### 不包含（Out of scope）
- 不修改 `/baransu:analyze` skill 或其輸出格式
- 不修改 `/baransu:dev` skill
- 不修改既有三個 reviewer agents（architecture/quality/security）
- 不設計跨 DAG 批次協調（wave 2 及後續）
- 不自動 git push 或開 PR
- 不實作 spec 過時偵測（execute 信任 spec 是有效的）
- 不加入 `--dry-run`、`--verbose` 等 CLI flag（dogfood 後視需要補充）
