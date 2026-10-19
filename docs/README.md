# baransu 文件

[← 回首頁](../README.md)

baransu 是一個簡單的練習：把「該輕的任務走輕量路徑、該重的決策不省思考」這套平衡哲學，包成一個 Claude Code plugin（另有手動維護的 Codex 版）。共 18 個 skill，每個都有清楚的觸發界線——什麼能省、什麼一定要做。

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

21 個 skill 分成五個家族。每頁列出每個 skill 的用途、觸發語、參數、產出位置與不適用的情況。

| 家族 | Skill | 一句話 |
|---|---|---|
| [構想](skills/plan.md) | [`/think`](skills/plan.md#think) | 動手前審議，留下一份計畫，不寫程式 |
| | [`/draft`](skills/plan.md#draft) | 動手前先畫骨架：兩版獨立設計，選定後寫成實作的合約 |
| [驗證](skills/verify.md) | [`/review`](skills/verify.md#review) | 乾淨 context 獨立重驗任何產出 |
| | [`/hunt`](skills/verify.md#hunt) | 從症狀追到根因，確認後才修 |
| | [`/prove-it`](skills/verify.md#prove-it) | 實際跑一次，證明說有問題的真的有問題、說完成的真的完成；「所有情況」的宣稱用形式化驗證 |
| [創作](skills/make.md) | [`/draw`](skills/make.md#draw) | 靜態圖、互動圖、影片、互動元件 |
| | [`/ui`](skills/make.md#ui) | 為你 repo 裡的介面定調並直接改檔 |
| | [`/write`](skills/make.md#write) | 雙語潤稿、生成、校對 |
| [學習](skills/learn.md) | [`/read`](skills/learn.md#read) | 任何來源轉成 Markdown 讀進對話 |
| | [`/learn`](skills/learn.md#learn) | 評分篩選來源，整理成學習筆記 |
| | [`/how`](skills/learn.md#how) | 講清楚一塊程式怎麼運作 |
| | [`/why`](skills/learn.md#why) | 查出程式為什麼長這樣，每條主張標信心 |
| | [`/teach-me`](skills/learn.md#teach-me) | 用對話把一塊程式或一份筆記教懂 |
| | [`/show-me`](skills/learn.md#show-me) | 用最小的一張圖把當下的重點畫出來 |
| [維運](skills/ops.md) | [`/ship`](skills/ops.md#ship) | 歸檔、commit、push、清 worktree |
| | [`/health`](skills/ops.md#health) | 體檢專案的 agent 配置與 AI 可維護性 |
| | [`/evolve`](skills/ops.md#evolve) | 用減法棘輪一輪輪磨好一份 SKILL.md |
| | [`/codex-skill-transfer`](skills/ops.md#codex-skill-transfer) | Claude／Codex 雙版本的對照與對齊檢查 |

呼叫方式：Claude Code 用 `/baransu:<name>`，Codex 用 `$baransu:<name>`。每個 skill 的設計約束寫在它自己的 `plugins/baransu/skills/<name>/SKILL.md`。

## 授權與第三方來源

repo 根目錄目前沒有授權檔。以下子模組 vendored 自第三方專案，授權與出處隨檔附上：

- `/draw`：`plugins/baransu/skills/draw/NOTICE.md`（diagram、map、手繪動畫等來源與授權清單），各子目錄另附 `LICENSE`。
- `/ui`：`plugins/baransu/skills/ui/NOTICE.txt`。
- `/domain-modeling`：`plugins/baransu/skills/domain-modeling/NOTICE.txt`（MIT，Matt Pocock），授權全文在同目錄 `LICENSE.txt`。
- `/codex-skill-transfer`：SKILL.md frontmatter 標示 `license: Apache-2.0`。
- `/why`、`/how`、`/teach-me`：改編自 Cursor pstack 的 why、how、teach（MIT，Lauren Tan），各自的 `NOTICE.md` 附出處與授權全文。
- `/show-me`：改編自 HumanLayer skills 的 show-me（MIT，HumanLayer），`plugins/baransu/skills/show-me/NOTICE.md` 附出處與授權全文。
- `/prove-it`：改編自 Cursor pstack 的 create-verification-skill、maintain-verification-skill、create-formal-verification-skill、maintain-formal-verification-skill（MIT，Lauren Tan），`plugins/baransu/skills/prove-it/NOTICE.md` 附出處與授權全文。
- `/draft`：改編自 Cursor pstack 的 architect、arena（MIT，Lauren Tan），mattpocock/skills 的 codebase-design、improve-codebase-architecture（MIT，Matt Pocock），以及 ponytail（MIT，DietrichGebert），`plugins/baransu/skills/draft/NOTICE.md` 附出處與授權全文。
- `/write`：去 AI 腔的部分規則改編自 Cursor pstack 的 unslop（MIT），見 `plugins/baransu/skills/write/NOTICE.md`。

## 圖片

首頁與家族頁的概念圖放在 [`images/`](images/)：`hero.jpg`（Krea 2 產生）、`family-plan.png`、`family-verify.png`、`family-make.png`、`family-learn.png`、`family-ops.png`。
