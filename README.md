# baransu

> バランス ── 一個 Claude Code 插件市集（Plugin Marketplace）。
> 專注在 governance 類 skill：在動手寫 code 之前，先對焦、調研、取得明確批准。

## 目前狀態

**v0.1.0** — 首個 skill 已上線。

| Skill | 類型 | 觸發 | 產出 |
|-------|------|------|------|
| `/baransu:think` | Governance（Type 10） | 使用者說要做新功能／設計／架構決策時自動觸發；也可手動呼叫 | 經過三輪對焦 + 官方解檢查 + 自我反駁 + 複雜度分級 + 明確批准的五段式計畫 |

`/think` 的核心鐵律：**未經使用者透過 `AskUserQuestion` 明確批准前，絕對不輸出程式碼、腳手架、偽碼、檔案樹**。

## 專案結構

```
.claude-plugin/
  marketplace.json             # 市集目錄（catalog）
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # 插件 manifest (v0.1.0)
    skills/
      think/
        SKILL.md               # think skill 本體（英文主體、中文輸出）
```

> `.claude-plugin/marketplace.json` 是「市集目錄」，`plugins/baransu/.claude-plugin/plugin.json` 才是「插件 manifest」，兩者用途不同，請勿混用。

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

```
/baransu:think 我想加一個 X 功能
```

或是讓模型自動觸發：只要在對話中提到「我想做／加／實作／設計…」類的請求，`/think` 就會介入，把粗糙想法變成一份可被批准的詳細計畫。

## 路線

下一個 skill 預計是 /think 的下游消費者（暫定 `/execute`，方向是「信任 /think 的批准、剝除重複 ceremony、讓簡單任務能在分鐘級完成」）。詳細設計將透過 /think 本身產出。

## 開發慣例

- 本目錄本身即是插件市集 root，所有編輯都以此為基準。
- 遵循全域 `CLAUDE.md`：Conventional Commits、read-before-write、`.agent-workspace/` 為暫存區不入版控。
- **發佈任何對外變更前，務必** 在 `plugins/baransu/.claude-plugin/plugin.json` 中提升 `version`，否則因為插件快取，使用者不會收到更新。
- 目前尚無 build／test／lint 工具鏈。

## 授權

尚未決定。
