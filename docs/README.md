# baransu 文件

[← 回首頁](../README.md)

baransu 是一個簡單的練習：把「該輕的任務走輕量路徑、該重的決策不省思考」這套平衡哲學，包成一個 Claude Code plugin（另有手動維護的 Codex 版）。共 14 個 skill，每個都有清楚的觸發界線——什麼能省、什麼一定要做。

首頁只講概念；這裡放完整參考。

## 從哪裡開始

| 想知道 | 讀這頁 |
|---|---|
| 為什麼是這樣設計、五條理念的完整版 | [理念：バランス](philosophy.md) |
| 一件事該走輕量路還是完整流程 | [三頻段路由](routing.md) |
| 怎麼安裝、安裝後有什麼 | [安裝](install.md) |
| 怎麼修改 baransu 本身、怎麼跑檢查 | [開發指南](development.md) |
| 每一版改了什麼 | [CHANGELOG](../CHANGELOG.md) |

## Skill 參考

14 個 skill 分成五個家族。每頁列出每個 skill 的用途、觸發語、參數、產出位置與不適用的情況。

| 家族 | Skill | 一句話 |
|---|---|---|
| [構想](skills/plan.md) | [`/think`](skills/plan.md#think) | 動手前審議，留下一份計畫，不寫程式 |
| | [`/contract`](skills/plan.md#contract) | 中型任務開工前，一頁釘死驗收條文 |
| [驗證](skills/verify.md) | [`/seal`](skills/verify.md#seal) | 對著合約做五點封緘驗收 |
| | [`/review`](skills/verify.md#review) | 乾淨 context 獨立重驗任何產出 |
| | [`/hunt`](skills/verify.md#hunt) | 從症狀追到根因，確認後才修 |
| [創作](skills/make.md) | [`/draw`](skills/make.md#draw) | 靜態圖、互動圖、影片、說明頁 |
| | [`/ui`](skills/make.md#ui) | 為你 repo 裡的介面定調並直接改檔 |
| | [`/write`](skills/make.md#write) | 雙語潤稿、生成、校對 |
| [學習](skills/learn.md) | [`/read`](skills/learn.md#read) | 任何來源轉成 Markdown 讀進對話 |
| | [`/learn`](skills/learn.md#learn) | 評分篩選來源，整理成學習筆記 |
| [維運](skills/ops.md) | [`/ship`](skills/ops.md#ship) | 歸檔、commit、push、清 worktree |
| | [`/health`](skills/ops.md#health) | 體檢專案的 agent 配置與 AI 可維護性 |
| | [`/evolve`](skills/ops.md#evolve) | 用棘輪一輪輪磨好一份 SKILL.md |
| | [`/codex-skill-transfer`](skills/ops.md#codex-skill-transfer) | Claude／Codex 雙版本的對照與對齊檢查 |

呼叫方式：Claude Code 用 `/baransu:<name>`，Codex 用 `$baransu:<name>`。每個 skill 的設計約束寫在它自己的 `plugins/baransu/skills/<name>/SKILL.md`。

## 授權與第三方來源

repo 根目錄目前沒有授權檔。以下子模組 vendored 自第三方專案，授權與出處隨檔附上：

- `/draw`：`plugins/baransu/skills/draw/NOTICE.md`（diagram、map、手繪動畫等來源與授權清單），各子目錄另附 `LICENSE`。
- `/ui`：`plugins/baransu/skills/ui/NOTICE.txt`。
- `/codex-skill-transfer`：SKILL.md frontmatter 標示 `license: Apache-2.0`。

## 圖片

首頁與家族頁的概念圖放在 [`images/`](images/)：`hero.jpg`（Krea 2 產生）、`family-plan.png`、`family-verify.png`、`family-make.png`、`family-learn.png`、`family-ops.png`。
