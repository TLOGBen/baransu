# baransu

> バランス ── 一個 Claude Code 插件市集（Plugin Marketplace）。

## 目前狀態

早期骨架。市集目錄結構已建立，但內含的 `baransu` 插件尚未擁有任何 skills／agents／commands／hooks。
在第一個正式版本發佈前，請把本 README 視為占位文件。

## 專案結構

```
.claude-plugin/
  marketplace.json             # 市集目錄（catalog）
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # 插件 manifest
    skills/                    # 尚未建立
    agents/                    # 尚未建立
    commands/                  # 尚未建立
    hooks/                     # 尚未建立
```

> `.claude-plugin/marketplace.json` 是「市集目錄」，`plugins/baransu/.claude-plugin/plugin.json` 才是「插件 manifest」，兩者用途不同，請勿混用。

## 本地安裝測試

```
/plugin marketplace add /home/vakarve/projects/baransu
/plugin install baransu@baransu
/plugin validate
```

若要從 Git 遠端安裝（之後推上去之後）：

```
/plugin marketplace add <git-remote-url>
/plugin install baransu@baransu
```

## 開發慣例

- 本目錄本身即是插件市集 root，所有編輯都以此為基準。
- 遵循全域 `CLAUDE.md` 的規範：Conventional Commits、read-before-write、`.agent-workspace/` 為暫存區不入版控。
- 每次對外發佈的變更，**務必** 在 `plugins/baransu/.claude-plugin/plugin.json` 中提升 `version`，否則因為快取，使用者不會收到更新。
- 目前尚無 build／test／lint 工具鏈；未來若導入會更新此段。

## 授權

尚未決定。
