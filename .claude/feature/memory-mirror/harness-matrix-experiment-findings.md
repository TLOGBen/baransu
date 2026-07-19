---
name: harness-matrix-experiment-findings
description: 2026-07-19 十格 harness×model 矩陣實驗結論 — 條文可測性是最大品質槓桿，review 應窄化為掃無測試表面
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f046418-ed4e-4c99-9d8c-f8a339d5e0ef
  modified: 2026-07-19T13:10:10.355Z
---

2026-07-19 在 NovelReader 上跑的 10-arm 實驗（P1 原生/P2 analyze/P3 analyze+execute ×
F/OS/FOS，同一簡報三工作項，盲評）。完整記錄正本已歸檔至 baransu repo
`.claude/experiments/2026-07-19-harness-matrix/`（main 已推送；NovelReader
`origin/legado-parity-p3f` 分支留歷史快照）。

核心結論（供 baransu 輕量化路線引用）：
1. 優勝 p3-f（Fable 全套 execute）20/21 釘死、0 bug；但 p1-o（Opus 單體）$4.92 拿第 4 名。
2. **最大品質槓桿是 goal.md 驗收條文的可測性**，不是流程重量：p3-fos 與 p3-os 同儀式
   （sonnet 實作+opus 審查），條文釘得死的打槍修掉 idx+1 缺陷、條文只要求子字串的
   advisory 放行 → 盲評 HIGH。
3. 強模型的 bug 幾乎全落在「無測試釘住的 user-facing 表面」（訊息接線/UI 文案）；
   6 個引入 bug 中 5 個是 idx+1 章數陷阱，連 Fable 單體也踩（自盲）。
4. 架構遵循度全體 9+/10 天花板：CLAUDE.md 不變量寫清楚時任何組合都守得住。
5. 測試有效率由「規格有 test.md」驅動（P2/P3≈9 vs P1 7-8.5），非 Red gate 儀式本身。

**How to apply:** baransu 演化方向 — (a) analyze 加「條文可斷言性」結構檢查；
(b) review/execute 的審查窄化為「未被測試覆蓋的 user-facing 行為掃描」；
(c) 小任務預設單體 + 窄域 review，大任務才上全套 execute。
相關：[[baransu-optimization-roadmap]]、[[one-workflow-at-a-time]]。

**活文件（持續維護，每階段轉換回寫）**：baransu repo `.claude/feature/harness-reform.md` —
起因/兩輪實驗判決/當前階段/後續 Phase/目標判準/檔案索引全在那裡；喚醒後先讀它。
驗證輪補記（2026-07-19）：R1–R9 改革讓 p3-os′ 翻身 20/20/0bug/6-6 突變（$19.29＝冠軍 59%）；
p-min 一頁合約+seal 行為面 20/20/$7.27。Phase 1 版圖重組（contract/seal 獨立＋雙塔合一＋15 上限）
計畫在 /review 中。

**Phase 1 已落地（2026-07-19）**：baransu 3.0.0 於 branch feat/phase1-restructure 三段手術完成——
/contract＋/seal 新增、execute 併入 analyze（execution-pipeline.md，R8 裁剪＋四機件保留）、
修憲 15（falsifiable）、三頻段路由、seal-guard hook 出貨即生效**預設阻擋**（SEAL_GUARD=log|off 降級、
stop_hook_active 防迴圈）、遙測慣例 _shared/selection-telemetry.md。使用者重裝 plugin 後生效。
