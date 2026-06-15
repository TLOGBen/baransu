# baransu

> バランス。

---

## 起源

市面上有很多 skill，但用起來哪裡都不對。

要麼什麼都不管，模型照自己理解直接開工；要麼儀式太重，一個小改動也要先填五張表才動得了手。

第一次嘗試是自己做了一套 `everything-cli`。做完才發現，它走到了另一個極端：token 燒得飛快，每個小任務都要過七道關才能動手。好用，但太重了。

baransu 是第二次。

---

## 核心理念

**平衡不等於折衷——重點是知道什麼時候該輕、什麼時候不能輕。**

小任務不需要三輪對焦；重要決策不能省略思考。工具該配合任務的形狀；任務小就走輕量路徑、大就走完整 spec，不該倒過來逼任務遷就工具的流程。

每個 skill 都有清楚的觸發界線——什麼能省、什麼一定要做。

v2.1.0 起，這條路線成文為五條可驗收的理念。每條綁定一個倉內機制——**無錨點的條款不入冊**，錨點是否存在，由結構驗證器把關：

| 理念 | 一句話 | 機制錨點 |
|---|---|---|
| 規則是天花板 | 只寫防真實翻車的規則；新條目先折入既有原則，容器只能變深、不能變長 | `plugins/baransu/rules/anti-patterns.md` |
| 結構是地板 | 確定性檢查全走腳本閘門，不靠模型自律；13 個技能是上限，要加先裁 | `scripts/verify-skills.py` |
| 人在授權點 | Input PAUSE 在自動化驅動下可走預設值；Authorization PAUSE 任何情況不可覆寫 | `plugins/baransu/skills/_shared/loop-contract.md` |
| 證據優先 | 非顯然主張依賴前先引查證來源；發現過四問門檻，乾淨的 review 也是有效的 review | `plugins/baransu/skills/review/SKILL.md` |
| 狀態落盤 | 長流程的結論落檔交付、不賭終端顯示；工作日誌隨實作持續追記 | `plugins/baransu/skills/_shared/output-journal.md` |

技能串聯維持五平面自動交接：管線負責把事串起來，人守在授權點上。這是刻意的取捨。

---

## 安裝

### Claude Code

```
/plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
```

### Codex CLI（衍生變體）

Codex 變體放在 `codex/` 子樹，repo 根目錄有一份 `.agents/plugins/marketplace.json` 指向它，所以安裝直接用 git URL 即可：

```bash
# HTTPS
codex plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git

# SSH
codex plugin marketplace add git@git.hy-tech.com.tw:ben.tsai/baransu.git

# 釘特定版本（推薦，main 可能隨時動；tag 與 plugin.json 版本同步）
codex plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git --ref v2.1.0

# 本地 clone 也行
codex plugin marketplace add /path/to/baransu
```

`marketplace add` 等同 install — Codex 沒有獨立的 `plugin install` 指令。

注意：

- Codex 版是 Claude 的單向衍生產物。Claude 端先動，再透過 `/codex-skill-transfer` 重生 codex/。不要直接編輯 codex/ 內檔案，會在下次轉換時被覆蓋。
- Agent stubs 放在 `codex/plugins/baransu/.codex-agents-templates/`，install 不會自動寫進 `~/.codex/agents/`，你要用的 agent 自行複製過去。

---

## Skills

### 思考型

動手前先把方向、邏輯、視角釘住的工具。

| Skill | 核心介紹 |
|---|---|
| `/think` | 動手前的對焦工具。先用三輪提問把方向收斂，再用五節計畫釘死細節，最後拿到一句明確批准才往實作走。防的是這件事：模型抓到一個假需求，還把它做得很完整。 |
| `/review` | 帶著明確問題，在乾淨 context 裡重新讀一次已經做完的工作。重點不是抓語法錯誤，是抓慣性讓人看不見的事——邊界沒守住、邏輯有跳格、宣稱和實作對不起來。 |
| `/hunt` | 抓 bug 的工作流。先選對觀測層放工具（看事件時序、重現資料、髒資料特徵），再用 log 二分法一輪不超過三個探點往內收斂，直到能一句話講清根因——指到 file:line，不接受「可能是狀態問題」這種答案。動手修以前先把呼叫鏈與會被影響的測試列出來，修完依規模走直接實作（`_shared/tdd.md` §7 紅綠紀律）或 `/analyze` 收尾。 |
| `/health` | 體檢你專案的 agent 配置與 AI 可維護性——指令漂移、hooks/MCP、驗證面、code-rot 訊號。五層審計（agent config → instruction surfaces → tools/runtime → verifiers → maintainability），預算姿態先行：預設只跑 summary，深審需明確觸發並先告知成本。baransu 自身的結構驗證歸 `scripts/verify-skills.py`，審單次模型輸出歸 `/review`。 |

### 設計型

方向確定後，把它敲成可執行規格／藍圖的工具。

| Skill | 核心介紹 |
|---|---|
| `/analyze` | 方向已經確定，但任務大到一個 session 收不掉。從一句需求出發，展開成五層文件：目標、需求、設計、測試、任務。再派三個 subagent 跨層核對，沒衝突才把整包交給實作端。 |
| `/design` | 寫 UI/UX 設計規格的工具。三種模式：`gen` 用問題引導你生出九段 `DESIGN.md` 與自展示 `DESIGN.html`、`lint` 對照 Stitch 九段結構與 Kami 十條不變量挑出具名違規、`preset [名稱]` 整包套用內建模板（目前內建「紙」這套羊皮紙暖色系，含 `tokens.css` + 6 個 `design-cores/` 通用骨架）。Stage 0 會在 `CLAUDE.md` / `AGENT.md` / `INSTRUCTION.md` 頭部注入三條 bullet（DESIGN.md / tokens.css / design-cores/，後兩者 if-present），讓後續 session 帶著設計脈絡走。 |

### 實作型

把規格／方向鎚成最終產物的工具。

一個 session 收得掉的小任務不再有專屬 skill：由主 session 依 `plugins/baransu/skills/_shared/tdd.md` §7 的紅綠文件紀律直接實作（先列 task list、測試先紅後綠），寫完送 `/review` 收尾。

| Skill | 核心介紹 |
|---|---|
| `/execute` | 中大型任務的自動執行入口。吃 `/analyze` 產出的 spec 目錄（`.claude/analyze/{date}-{slug}/`），依任務之間的相依關係算出可以並行的子組（規模分 XL/L/M），開多個 git worktree 同時跑；每個任務都走 Summarize → Impl → Review 的 TDAID 迴圈，由 8 個專責 agent 接力，跑到 spec 上所有 requirement 全綠、E2E 與 final review 都簽掉為止，最後產出 `final-report.md`。需先完成 `/analyze`。範例：`/baransu:execute .claude/analyze/2026-04-25-my-feature/` |
| `/write` | 雙語寫作 / 潤色助手。給它已有文字，它會逐條套上排版規則與寫作風格（zh 參考余光中，en 參考 Orwell），輸出 Before/After 與每處改動的理由；給它需求而沒給文字，它直接生一份格式、語氣、用字都校準過的成品。 |

### 研究型

把外部資料轉成可讀、可吸收材料的工具。

| Skill | 核心介紹 |
|---|---|
| `/read` | 萬用內容擷取工具。URL、本地路徑、glob、Chrome 分頁、剪貼簿一律轉成離線 Markdown，儲存至指定目錄。四個搜尋擴充：`--topic` 學術論文、`--web` 一般網頁、`--gh` GitHub repo/code/issue、`--x` X (Twitter)；先列結果，互動式挑選後才下載。 |
| `/learn` | 把素材整理成讀書筆記。輸入 URL、`--topic` 學術關鍵字、或 `/read` 抓回的素材代號（`.claude/read/material/` 下的資料夾名，例如 `effective-context-engineering`）；每份素材會出一張五欄重點摘要，加 `--outline` 會再續寫成完整大綱與填好內容的筆記。產物放在 `.claude/learn/`。 |
| `/book` | 把任何來源（URL、`/read` slug、`/learn` digest、本地檔案、`--text` 純文字）轉成 Kami 主題的瀏覽器 HTML，含 SVG 圖解、側欄目錄、紙質排版，輸出至 `.claude/book/{slug}.html`。三階段流程：Acquire（取得內容，proxy cascade 自動試三層）→ Synthesize（分辨 technical / narrative / research，拆 4–8 節結構）→ Render（依黃金模板輸出，品質閘 + browser-use 自動驗跑版）。 |

### 互通型

把 baransu 的 skill / plugin 投放到其他生態系。Claude 永遠是源頭，Codex 是衍生目標。

| Skill | 核心介紹 |
|---|---|
| `/codex-skill-transfer` | 一份 Claude Code 的 SKILL.md（或整個 plugin）轉成 Codex 對應格式（`.codex-plugin/plugin.json` + 翻譯後的 SKILL.md + agent stub TOML）。三種輸入自動偵測：單一 skill / 多 skill 批次 / 整個 plugin。動態注入（`` !`cmd` ``、`$ARGUMENTS`）改寫成 Codex 不會誤解的自然語言；`disable-model-invocation` 翻成 `agents/openai.yaml` policy；含 `context: fork` 的 skill 拒絕自動轉並列出三條 Codex 路徑（native Subagents / skill chain / Codex MCP）給人挑。高風險 Claude 能力會經 capability 降級表評估「對抗哪種模型慣性」，必要時搬到 artifact gate / phase split / machine gate，而非只降成 prompt。Plugin mode 會產生 Codex Layout B marketplace；git URL 發布仍需 repo-root Layout A catalog 手動維護。 |

### 收尾型

session 結束的清理與交付。

| Skill | 核心介紹 |
|---|---|
| `/ship` | session 結束後的清理工具。將 `.claude/tmp/`、`.claude/analyze/`、`.claude/execute/`、`.claude/think/` 歸檔至 `.claude/archived/`，執行 `git add -A` + commit + push，並在 git worktree 環境下自動清理 worktree 與分支。`.claude/think/` 由 `.gitignore` 排除，僅本地累積。完全自動，無需人工確認。 |

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
方向清楚就跳過 `/think`，直接從寫 spec 開始。

**小型任務（單一模組、一個 session 可完成）**
```
/think → 直接實作（_shared/tdd.md §7）→ /ship
```
方案核可後由主 session 依 `plugins/baransu/skills/_shared/tdd.md` §7 的紅綠文件紀律直接實作，寫完送 `/review`。

**已有 spec**
```
/execute .claude/analyze/{date}-{slug}/ → /ship
```

**排查 bug（症狀已知，根因未定）**
```
/hunt → 直接實作（_shared/tdd.md §7）或 /analyze → /ship
```
`/hunt` 選對觀測層放工具，定位症狀後用 log 二分法往內收。根因確定後依規模走直接實作（紅綠文件紀律）或 `/analyze` 修復，再送 `/review` 收尾。

**內容研讀（擷取 → 整理 → 心得）**
```
/read {來源} → /learn {slug} → /write zh [請求]
```
`/read` 轉離線 Markdown，`/learn` 抓五欄重點或續寫大綱，`/write` 套規則產出成稿。產物留在 `.claude/read/material/` 與 `.claude/learn/`，不走 `/ship` 歸檔。

**內容視覺化（研究素材 → HTML 閱讀頁）**
```
/read {來源} → /book {slug}
/learn {來源} → /book {digest-slug}
```
`/book` 讀取 `/read` 或 `/learn` 已存好的素材，渲染成 Kami 主題 HTML + SVG，存至 `.claude/book/`。也可直接 `/book {URL}` 或 `/book --text "…"` 一步到位。

**文字 copywriting**
```
/write zh [貼入文字或寫請求]
/write en [paste text or write a request]
```
不產生工作檔案，無需 `/ship`。

---

[MIT](./LICENSE) © 2026 ben.tsai
