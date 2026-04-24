# baransu

> バランス ── 一個 Claude Code 插件市集（Plugin Marketplace）。

## 核心理念：平衡

baransu 的設計主軸是**平衡**：

- **效率與結果的平衡** — 不為了快而草率，也不為了嚴謹而拖慢；每個 skill 都要同時交代「這樣做能多快」與「這樣做能多穩」。
- **輕與重的平衡** — 不是所有任務都值得完整儀式，也不是所有任務都該省略 gate。每個 skill 都有輕量模式與完整模式的明確切換條件，讓工具配合任務而非任務遷就工具。
- **優美且精準** — 輸出是可讀的、格式是穩定的、決策是可追溯的。不追求華麗，追求讓下一個人（或下一個 skill）能無痛接手。

目標不是建立又一個 governance 框架，而是在「想清楚再做」與「別卡住」之間找一個恰好的落點。

## 目前狀態

**v0.1.5** — 兩個 skill 上線。

| Skill | 角色 | 觸發 | 產出 |
|-------|------|------|------|
| `/baransu:think` | 做之前：對焦與批准 | 使用者說要做新功能／設計／架構決策時自動觸發；也可手動呼叫 | 經過三輪對焦 + 官方解檢查 + 自我反駁 + 複雜度分級 + 明確批准的五段式計畫 |
| `/baransu:review` | 做之後：獨立多視角複審 | 手動呼叫，通常在某個長流程宣稱完成後 | 派遣隔離視角（架構／品質／安全）在乾淨 context 中審視目標，加一輪對抗測試（> 500 行或跨層級時），findings 分四級（直修／打包確認／需判斷／僅供參考），每條過天平四問，code target 必須 e2e 跑過才能說完成 |

兩個 skill 的共通約束：
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
      plugin.json              # 插件 manifest (v0.1.5)
    skills/
      think/
        SKILL.md               # 做之前的對焦與批准
      review/
        SKILL.md               # 做之後的獨立多視角複審
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

## 路線

下一個 skill 預計是 `/think` 的下游**實作者**（暫定 `/execute`，方向是「信任 `/think` 的批准、剝除重複 ceremony、讓簡單任務能在分鐘級完成」）。`/review` 是審核側的對位，不是實作者本身。詳細設計將透過 `/baransu:think` 本身產出 —— dogfood。

## 開發慣例

- 本目錄本身即是插件市集 root，所有編輯都以此為基準。
- 遵循全域 `CLAUDE.md`：Conventional Commits、read-before-write、`.agent-workspace/` 為暫存區不入版控。
- **發佈任何對外變更前，務必** 在 `plugins/baransu/.claude-plugin/plugin.json` 中提升 `version`，否則因為插件快取，使用者不會收到更新。
- 設計新 skill 時 dogfood `/baransu:think` 本身；完成後可再用 `/baransu:review` 對自己做複審。
- 目前尚無 build／test／lint 工具鏈。

## 授權

[MIT](./LICENSE) © 2026 ben.tsai
