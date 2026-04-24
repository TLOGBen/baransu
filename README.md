# baransu

> バランス ── 一個 Claude Code 插件市集（Plugin Marketplace）。

## 核心理念：平衡

baransu 的設計主軸是**平衡**：

- **效率與結果的平衡** — 不為了快而草率，也不為了嚴謹而拖慢；每個 skill 都要同時交代「這樣做能多快」與「這樣做能多穩」。
- **輕與重的平衡** — 不是所有任務都值得完整儀式，也不是所有任務都該省略 gate。每個 skill 都有輕量模式與完整模式的明確切換條件，讓工具配合任務而非任務遷就工具。
- **優美且精準** — 輸出是可讀的、格式是穩定的、決策是可追溯的。不追求華麗，追求讓下一個人（或下一個 skill）能無痛接手。

目標不是建立又一個 governance 框架，而是在「想清楚再做」與「別卡住」之間找一個恰好的落點。

## 目前狀態

**v0.1.9** — 五個 skill 上線。

| Skill | 角色 | 觸發 | 產出 |
|-------|------|------|------|
| `/baransu:think` | 做之前：對焦與批准 | 使用者說要做新功能／設計／架構決策時自動觸發；也可手動呼叫 | 經過三輪對焦 + 官方解檢查 + 自我反駁 + 複雜度分級 + 明確批准的五段式計畫；Stage G 四選一（/review 再決定為推薦）；批准後小任務交 /dev、中大型交 /analyze |
| `/baransu:review` | 做之後：獨立多視角複審 | 手動呼叫，通常在某個長流程宣稱完成後 | 派遣隔離視角（架構／品質／安全）在乾淨 context 中審視目標，加一輪對抗測試（> 500 行或跨層級時），findings 分四級（直修／打包確認／需判斷／僅供參考），每條過天平四問，code target 必須 e2e 跑過才能說完成 |
| `/baransu:analyze` | 做之前：中大型任務規格展開 | 手動呼叫，任務跨 ≥ 2 個相依模組且有 context rot 風險時 | 五層 spec（goal → requirement → design → test → task）落在 `.claude/analyze/{date}-{slug}/`，3 個跨層 subagent 驗收對齊，自動修正一輪後交接 execute |
| `/baransu:dev` | 做：gate 強制 TDD 執行者 | `/think` 批准後自動交接（小任務）；也可直接呼叫 | 先建 TaskCreate 清單（紅燈測試→確認紅燈→綠燈實作→確認綠燈），每個 gate 硬卡，Green 失敗兩次自動轉 /think，完成後自動呼叫 /review；純 cosmetic 直接跳 review |
| `/baransu:write` | 寫：雙語 copywriting 助理 | 手動呼叫，前綴 `zh` 或 `en` 指定語言（可省略自動偵測） | 自動判斷潤色（Refine）或生成（Generate）模式，套用對應規則集（zh: sparanoid 精簡版；en: Oxford comma / 主動語態 / 句長 / 平行結構），輸出 Before/After 對比或成品加格式/語氣說明 |

五個 skill 的共通約束：
- **英文 body，繁中輸出** — SKILL.md 主體給 agent 讀，繁中留給最終使用者。
- **絕不越權改行為** — `/think` 未批准前一行程式碼都不出；`/review` 的自動修復只碰格式／import／typo／dead import。
- **複雜度需要證明自己的價值** — skill 本身的任何新段落、新規則都要過天平四問才能留下。

## 專案結構

```
.claude-plugin/
  marketplace.json             # 市集目錄（catalog）
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # 插件 manifest (v0.1.9)
    skills/
      think/
        SKILL.md               # 做之前的對焦與批准
      review/
        SKILL.md               # 做之後的獨立多視角複審
      analyze/
        SKILL.md               # 做之前：中大型任務規格展開（五層 spec）
      dev/
        SKILL.md               # 做：gate 強制 TDD 執行者（小任務）
      write/
        SKILL.md               # 寫：雙語 copywriting 助理（zh/en Refine + Generate）
    agents/
      architecture-reviewer.md # 視角：結構、邊界、過度抽象
      quality-reviewer.md      # 視角：宣稱對不對實作、邏輯、邊界
      security-reviewer.md     # 視角：攻擊面、輸入信任、秘密、跨信任邊界
```

> `.claude-plugin/marketplace.json` 是「市集目錄」，`plugins/baransu/.claude-plugin/plugin.json` 才是「插件 manifest」，兩者用途不同，請勿混用。agent 目錄在 `plugins/baransu/agents/`（plugin root 下），不在 `.claude-plugin/` 內，也不在 repo root。

## 安裝

從本地路徑：
```
/plugin marketplace add /home/vakarve/projects/baransu
/plugin install baransu@baransu
/plugin validate
```

從 Git 遠端：
```
/plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
```

## 使用

**`/think` — 做之前**
```
/baransu:think 我想加一個 X 功能
```
或讓模型在對話中聽到「我想做／加／實作／設計…」時自動觸發，把粗糙想法變成一份可被批准的詳細計畫。

**`/review` — 做之後**
```
/baransu:review                    # 審核目前未 commit 的變更
/baransu:review HEAD~3..HEAD       # 審核特定 commit range
/baransu:review src/auth/          # 審核一個目錄
/baransu:review path/to/plan.md    # 審核 /think 的計畫文件
```
適合用在某個長流程剛宣稱完成、多輪 session 累積了上下文污染、或你想要一份手術刀般精準的第二意見時。

**`/analyze` — 做之前（中大型任務）**
```
/baransu:analyze                   # 開始規格展開
```
任務跨 ≥ 2 個相依模組、有 context rot 風險時使用。skill 帶你從一句話目標出發，依序展開五層文件（goal → requirement → design → test → task），每份文件落在 `.claude/analyze/{date}-{slug}/`，最後由 3 個 subagent 做跨層驗收，修正後交接 execute。

與 `/think` 的分工：`/think` 做方向對焦（任務方向不確定時）；`/analyze` 做規格展開（方向已知、任務夠大時）。

**`/dev` — 做（小任務）**
```
/baransu:dev 實作 X 功能
```
或由 `/think` 批准後自動交接。skill 判斷是否需要 TDD（cosmetic 直接跳 review），用 TaskCreate 建立清單，依序跑 Red→Green gate，完成後自動呼叫 `/baransu:review`。

管線：`/think → /dev`（小任務）；`/think → /analyze`（中大型）。

**`/write` — 寫（雙語 copywriting）**
```
/baransu:write zh 這是一段需要潤色的中文文字 ...
/baransu:write en Here is a draft that needs polishing ...
/baransu:write zh 幫我寫一封請假信，輕鬆口吻
/baransu:write en write a thank-you note, professional tone
/baransu:write [input]   # 省略前綴：自動偵測語言
```
前綴（`zh`/`en`）同時決定規則集與輸出語言。Refine 模式（現有文字）輸出 Before/After 對比加規則標記；Generate 模式（請求提示）輸出成品加格式/語氣說明。主題模糊時 fallback 短文（3–5 句）。

## 路線

- `/analyze` 已在 v0.1.6 上線。
- `/dev` 已在 v0.1.7 上線 — `/think` 的小任務下游實作者。
- `/write` 已在 v0.1.9 上線 — 雙語 copywriting 助理；zh 套 sparanoid 精簡規則，en 套英文 copywriting 規則；前綴控制語言與規則集。
- 下一個 skill 預計是 `/analyze` 的下游**編排者**（暫定 `/execute`，重型編排，讀 task-*.md spec 檔案，將內容注入 subagent）。詳細設計將透過 `/baransu:think` 本身產出 —— dogfood。

## 開發慣例

- 本目錄本身即是插件市集 root，所有編輯都以此為基準。
- 遵循全域 `CLAUDE.md`：Conventional Commits、read-before-write、`.agent-workspace/` 為暫存區不入版控。
- **發佈任何對外變更前，務必** 在 `plugins/baransu/.claude-plugin/plugin.json` 中提升 `version`，否則因為插件快取，使用者不會收到更新。
- 設計新 skill 時 dogfood `/baransu:think` 本身；完成後可再用 `/baransu:review` 對自己做複審。
- 目前尚無 build／test／lint 工具鏈。

## 授權

[MIT](./LICENSE) © 2026 ben.tsai
