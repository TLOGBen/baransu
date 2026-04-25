# baransu

> バランス。

---

## 起源

市面上有很多 skill，但用起來哪裡都不對。

要麼什麼都不管，模型照著自己的理解直接開工；要麼儀式感過厚，一個小改動也要填五張表才能動手。

第一次嘗試是自己做了一套 `everything-cli`。做完才發現，它走到了另一個極端——token 燒得飛快，每個小任務都要過七道關才能動手。不是不好用，是太重了。

baransu 是第二次。

---

## 核心理念

**平衡不是折衷，是知道什麼時候該輕、什麼時候不能輕。**

小任務不需要三輪對焦；重要決策不能省略思考。工具應該配合任務的形狀，而不是讓任務遷就工具的流程。

每個 skill 都有明確的切換條件——什麼可以省，什麼不能省。

---

## Skills

| Skill | 核心介紹 |
|---|---|
| `/think` | 動手前的對焦儀式。三輪提問收斂方向，五節計畫釘死細節，一個明確批准才能進入實作。防止的是：模型理解了一個假需求，然後把它做得很完整。 |
| `/review` | 帶著明確問題，在隔離的 context 裡重新閱讀已完成的工作。找的不是語法錯誤，是慣性讓人看不見的問題——邊界定義、邏輯跳躍、宣稱和實作之間的落差。 |
| `/analyze` | 方向確定了，但任務夠大。從一句話出發，展開成五層文件：目標、需求、設計、測試、任務。三個 subagent 做跨層驗收，對齊後才交接實作。 |
| `/dev` | 小任務的執行層。先把清單建好，再走 Red/Green gate：測試要真的失敗，實作要真的通過。純格式變更直接略過。完成後自動呼叫 `/review`。 |
| `/write` | 雙語 copywriting 助理。貼入現有文字，套用排版規則與寫作風格原則（zh 參考余光中，en 參考 Orwell），輸出逐條說明的 Before/After；給出請求，生成格式、語氣、用字都對準的成品。 |
| `/execute` | 中大型任務的自動執行引擎。讀取 `/analyze` 產出的 spec 目錄（`.claude/analyze/{date}-{slug}/`），以前置群組 DAG 計算並行度（XL/L/M），透過 8 個 agent-only skill 驅動完整 TDAID 流程（並行 worktree + E2E + Final-Review），直到 Requirements 100% 通過為止，產出 `final-report.md`。需先完成 `/analyze`。範例：`/baransu:execute .claude/analyze/2026-04-25-my-feature/` |
| `/ship` | session 結束後的清理工具。將 `.claude/tmp/`、`.claude/analyze/`、`.claude/execute/` 歸檔至 `.claude/archived/`，執行 `git add -A` + commit + push，並在 git worktree 環境下自動清理 worktree 與分支。完全自動，無需人工確認。 |

---

## 安裝

```
/plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
```

---

[MIT](./LICENSE) © 2026 ben.tsai
