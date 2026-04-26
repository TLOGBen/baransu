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

### 思考型

動手前先把方向、邏輯、視角釘住的工具。

| Skill | 核心介紹 |
|---|---|
| `/think` | 動手前的對焦儀式。三輪提問收斂方向，五節計畫釘死細節，一個明確批准才能進入實作。防止的是：模型理解了一個假需求，然後把它做得很完整。 |
| `/review` | 帶著明確問題，在隔離的 context 裡重新閱讀已完成的工作。找的不是語法錯誤，是慣性讓人看不見的問題——邊界定義、邏輯跳躍、宣稱和實作之間的落差。 |
| `/analyze` | 方向確定了，但任務夠大。從一句話出發，展開成五層文件：目標、需求、設計、測試、任務。三個 subagent 做跨層驗收，對齊後才交接實作。 |
| `/hunt` | 狩獵 bug 的執行協議。工具掃描選對觀測層，定位症狀（事件時序、重現資料、髒資料特徵），log 二分法每輪最多三個觀測點往內收斂，直到能用一句話說出根因——指名 file:line，不接受「可能是狀態問題」。修前強制呼叫鏈分析和測試矩陣，修後路由至 `/dev` 或 `/analyze` 收尾。 |

### 實作型

把方向變成具體產物的工具。

| Skill | 核心介紹 |
|---|---|
| `/dev` | 小任務的執行層。先把清單建好，再走 Red/Green gate：測試要真的失敗，實作要真的通過。純格式變更直接略過。完成後自動呼叫 `/review`。 |
| `/execute` | 中大型任務的自動執行引擎。讀取 `/analyze` 產出的 spec 目錄（`.claude/analyze/{date}-{slug}/`），以前置群組 DAG 計算並行度（XL/L/M），透過 8 個 agent-only skill 驅動完整 TDAID 流程（並行 worktree + E2E + Final-Review），直到 Requirements 100% 通過為止，產出 `final-report.md`。需先完成 `/analyze`。範例：`/baransu:execute .claude/analyze/2026-04-25-my-feature/` |
| `/write` | 雙語 copywriting 助理。貼入現有文字，套用排版規則與寫作風格原則（zh 參考余光中，en 參考 Orwell），輸出逐條說明的 Before/After；給出請求，生成格式、語氣、用字都對準的成品。 |
| `/design` | UI/UX 設計規格生成器。三種模式：`gen`（問題引導式，生成九段 DESIGN.md）、`lint`（對照 Stitch 九段結構＋Kami 十不變量，輸出具名違規報告）、`preset [名稱]`（整包套用 preset，內建「紙」暖調羊皮紙色系）。輸出至專案根目錄 `DESIGN.md`，可選寫入 `CLAUDE.md` 傳遞設計語境。 |

### 研究型

把外部資料轉成可讀、可吸收材料的工具。

| Skill | 核心介紹 |
|---|---|
| `/read` | 萬用內容擷取工具。URL、本地路徑、glob、Chrome 分頁、剪貼簿，一律轉成離線 Markdown，儲存至指定目錄。學術論文模式（`--topic`）自動查詢並下載相關文獻。 |
| `/learn` | 內容研讀整理工具。輸入 URL、`--topic` 學術關鍵字、或 `/read` 已捕獲的 slug，每筆產出五欄式 digest brief 抓核心；加 `--outline` 續寫完整大綱與填注筆記。輸出至 `.claude/learn/`。 |

### 收尾型

session 結束的清理與交付。

| Skill | 核心介紹 |
|---|---|
| `/ship` | session 結束後的清理工具。將 `.claude/tmp/`、`.claude/analyze/`、`.claude/execute/`、`.claude/think/`、`.claude/dev/` 歸檔至 `.claude/archived/`，執行 `git add -A` + commit + push，並在 git worktree 環境下自動清理 worktree 與分支。`.claude/think/` 與 `.claude/dev/` 由 `.gitignore` 排除，僅本地累積。完全自動，無需人工確認。 |

---

## 推薦工作流

依任務規模選流程。收尾統一走 `/ship`。

**大型新功能（方向未定）**
```
/think → /analyze → /execute {spec目錄} → /ship
```
`/think` 三輪對焦確認方向，`/analyze` 展開五層 spec，`/execute` 驅動完整 TDAID 流程。

**大型任務（方向已定）**
```
/analyze → /execute {spec目錄} → /ship
```
方向清楚，直接從 spec 建構開始，跳過 `/think`。

**小型任務（單一模組、一個 session 可完成）**
```
/think → /dev → /ship
```
`/dev` 走 Red/Green gate，完成後自動呼叫 `/review`。

**已有 spec**
```
/execute .claude/analyze/{date}-{slug}/ → /ship
```

**排查 bug（症狀已知，根因未定）**
```
/hunt → /dev（或 /analyze）→ /ship
```
工具掃描選觀測層，定位症狀後 log 二分法縮小範圍。根因確定，路由修復，送 review 收尾。

**內容研讀（擷取 → 整理 → 心得）**
```
/read {來源} → /learn {slug} → /write zh [請求]
```
`/read` 轉離線 Markdown，`/learn` 抓五欄重點或續寫大綱，`/write` 套規則產出成稿。產物留在 `.claude/read/material/` 與 `.claude/learn/`，不走 `/ship` 歸檔。

**文字 copywriting**
```
/write zh [貼入文字或寫請求]
/write en [paste text or write a request]
```
不產生工作檔案，無需 `/ship`。

---

## 安裝

```
/plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
```

---

[MIT](./LICENSE) © 2026 ben.tsai
