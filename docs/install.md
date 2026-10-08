# 安裝

[← 回文件索引](README.md)

## Claude Code

```
/plugin marketplace add https://github.com/TLOGBen/baransu.git
/plugin install baransu@baransu
```

安裝後以 `/baransu:<name>` 呼叫，例如 `/baransu:think`。多數 skill 也會依對話內容自動觸發（觸發語見各家族頁）。

## Codex CLI（衍生變體）

```
codex plugin marketplace add https://github.com/TLOGBen/baransu.git
codex plugin add baransu@baransu
```

Codex 版放在 `codex/` 子樹，與 Claude 版並列手動維護。Codex 以 `$baransu:<name>` 提及 skill，例如 `$baransu:think`。

兩邊的 marketplace 檔：

| 平台 | marketplace | plugin 來源 |
|---|---|---|
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/baransu/` |
| Codex | `.agents/plugins/marketplace.json` | `codex/plugins/baransu/` |

## 安裝後會生效的東西

- **14 個 skill**：見 [文件索引](README.md#skill-參考)。
- **seal-guard hook**（Claude Code，預設阻擋）：session 結束時若有未 `/seal` 的 user-facing 變更會擋下。降級用環境變數 `SEAL_GUARD=log`（只記錄）或 `SEAL_GUARD=off`。詳見 [三頻段路由](routing.md#seal-guard-hook)。
- **bundled agents**：review 的視角 reviewer、seal-agent、verifier、health inspector、evolve 的 diagnostician 與 judge，由對應 skill 派遣，不需要手動呼叫。

## 更新

plugin 有快取：只有版本號變了，使用者才會拿到新內容。每次發佈都會升版，對照 [CHANGELOG](../CHANGELOG.md)。

## 本機開發安裝

從本機 clone 安裝（路徑換成你的 clone 位置）：

```
/plugin marketplace add /path/to/baransu
/plugin install baransu@baransu
/plugin validate
```

開發流程見 [開發指南](development.md)。
