# C2 殘留掃描分類清單 — 發行面（TASK-distribution-01）

掃描日期：2026-06-10
掃描面：`CLAUDE.md`、`README.md`、`plugins/baransu/.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`
掃描指令（case-insensitive 變體亦跑過，結果相同）：

```bash
grep -nE '\bgrade\b|\btriage\b|\bbridge\b|baransu:dev|\bdev\b|\btdd\b|\bharness\b' \
  CLAUDE.md README.md plugins/baransu/.claude-plugin/plugin.json .claude-plugin/marketplace.json
```

## 命中與人工分類

| # | 位置 | 命中字樣 | 分類 | 理由 |
|---|---|---|---|---|
| 1 | CLAUDE.md:83 | `tdd.md` | 合法 | Layout 註解指向保留資產 `_shared/tdd.md` |
| 2 | CLAUDE.md:122 | `tdd.md` | 合法 | 小任務改道句，依 spec 要求指向 `_shared/tdd.md` §7 |
| 3 | README.md:75 | `tdd.md` | 合法 | `/hunt` 修復改道句，指向保留資產 |
| 4 | README.md:90 | `tdd.md` | 合法 | 實作型段落改道說明，指向保留資產 |
| 5 | README.md:143 | `tdd.md` | 合法 | 小型任務工作流鏈改道（spec 明文要求） |
| 6 | README.md:145 | `tdd.md` | 合法 | 同上，鏈說明句 |
| 7 | README.md:154 | `tdd.md` | 合法 | 排查 bug 工作流鏈改道（spec 明文要求） |

## 結論

- `\bgrade\b`、`\btriage\b`、`\bbridge\b`、`baransu:dev`、`\bdev\b`、`\bharness\b`：**零命中**。
- `\btdd\b` 僅以 `tdd.md` 檔名形式出現（7 處），全部為指向保留資產
  `plugins/baransu/skills/_shared/tdd.md` 的功能性引用 —— 此為 spec 要求的改道目標，非被裁資產殘留。
- 同形字樣（upgrade／downgrade／gradient／bridging）零命中，無需排除。

判定：發行面無任何指向被裁資產（`/dev`、`/grade`、`/triage`、`/bridge` 及 harness 附屬）的功能性引用。C2（發行面部分）通過。
