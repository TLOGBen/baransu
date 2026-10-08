# 開發指南

[← 回文件索引](README.md)

給要修改 baransu 本身的人。規範的正本是根目錄的 [CLAUDE.md](../CLAUDE.md)（Claude 用）與 [AGENTS.md](../AGENTS.md)（非 Claude agent 用）；本頁整理成好讀的版本，兩者衝突時以 CLAUDE.md 為準。

## Repo 結構

```
.claude-plugin/
  marketplace.json               # Claude Code marketplace 目錄
.agents/plugins/marketplace.json # Codex marketplace 目錄（指向 codex/plugins/baransu）
plugins/baransu/                 # Claude 版（Claude Code 的正本）
  .claude-plugin/plugin.json     # plugin manifest，權威版本號
  skills/                        # 14 個 skill ＋ _shared/（跨 skill 參考、evals、scripts）
  agents/                        # 派遣用 agent：視角 reviewer、seal-agent、verifier、health inspector、evolve
  hooks/                         # seal-guard（.sh ＋ .ps1）
  rules/anti-patterns.md         # 跨 skill 行為護欄
codex/plugins/baransu/           # Codex 版（手動維護，Codex 的正本）
  plugin.json
  skills/                        # 與 Claude 版逐檔對應；可多出 agents/openai.yaml
  .codex-agents/                 # agent 的 TOML 版
scripts/
  verify-skills.py               # 結構驗證器（含 README 理念錨點檢查）
  verify-codex-parity.py         # Claude／Codex 逐檔配對＋版本一致
tests/                           # integration／scripts（pytest）／skills（shell）
docs/                            # 本文件
```

兩個 manifest 不能合併：根目錄的 `marketplace.json` 是目錄，`plugins/baransu/.claude-plugin/plugin.json` 是 manifest。`skills/`、`agents/` 放在 plugin 根目錄，不放進 `.claude-plugin/`；`plugin.json` 不放 `skills` 陣列（Claude Code 從檔案系統探索）。

## Claude 版與 Codex 版

- 兩邊並列手動維護，各自是自己平台的正本。
- Claude 版有改動時，**同一次變更**一併同步到 `codex/plugins/baransu/`，以 `/baransu:codex-skill-transfer` 當對照表與檢查清單。
- `transfer.py` 是選用的草稿工具，只輸出到暫存目錄，不覆蓋 `codex/`。
- 內容是否正確移植由檢查清單負責；`make parity-check` 只檢查結構：檔案逐一對應、兩份 manifest 版本一致。

## 驗證

```bash
make test         # verify-skills.py ＋ pytest tests/scripts/ ＋ tests/ 下每個 shell 測試
make parity-check # scripts/verify-codex-parity.py
make ship-check   # test ＋ parity-check，發佈前跑這個
```

- `make test` 是單一穩定入口，各測試組也能單獨執行。
- `parity-check` 刻意不放進 `make test`：開發途中兩邊可能暫時不同步。repo 沒有 CI 也沒有排程，`make ship-check` 是唯一會跑它的入口。
- 在 Windows 上透過 WSL 執行時，需要 pytest 與 PyYAML，例如：

```bash
uv run --no-project --with pytest --with pyyaml make ship-check
```

### 與文件相關的檢查

- `scripts/verify-skills.py` 會讀 README.md 的 `## 核心理念` 段：理念表每一列都要有一個存在於倉內的反引號路徑錨點。改首頁時保留這個標題與表格。
- 同一支腳本與 `tests/integration/test-distribution-metadata.sh`（D9）會掃 README.md，不得出現已退役 skill 的名稱。
- `tests/integration/test-claude-md-skills-table.sh` 把 CLAUDE.md 的 skill 表釘在 `tests/integration/claude-md-skills-baseline.txt`：14 列、描述逐字比對。改 CLAUDE.md 技能表時要同步 baseline。

## 版本

- `plugins/baransu/.claude-plugin/plugin.json` 是權威版本號；`marketplace.json` 與 Codex 版 `plugin.json` 要跟它一致。
- **每次發佈都升版**：plugin 有快取，不升版使用者看不到更新。
- 變更記錄寫在 [CHANGELOG.md](../CHANGELOG.md)（Keep a Changelog ＋ Semantic Versioning）。

## 撰寫慣例

- **英文本文**：所有給 agent 讀的文字——每個 `SKILL.md` 本文、`references/`、`skills/_shared/`、`rules/`、`agents/` 的系統提示——一律英文。
- 允許的繁體中文只有：使用者看到的輸出（完成、錯誤、狀態訊息與輸出範本）、frontmatter `description` 與易混淆表中的觸發語、示範中文內容的範例產物、`/write` 的雙語寫作內容。
- 使用者看到的輸出一律繁體中文。
- 給使用者讀的文件（README、`docs/`）用繁體中文。

## 不要「優化」掉的不變量

這些都曾造成迴歸，完整說明見 [CLAUDE.md · Non-obvious Invariants](../CLAUDE.md#non-obvious-invariants)：

- `plugin.json` 不放 `skills` 陣列。
- `/ship` 刪分支用 `-D` 不用 `-d`。
- sealed 標記只讀檔案前 3 行偵測；`/contract` 歸檔一律加時間戳，`/ship` 只在名稱衝突時加。
- `/learn` 完整筆記以批判層四段結尾，沒有矛盾也要明寫。
- `/read` 的 `raw/` 不可變。
- `verify-skills.py` Gate 10 是 loop-pauses 註冊表的契約；Gate 11 已退役，編號不再使用。
- 沒有 git 的專案，`/ship` 在任何歸檔搬移之前就失敗。
- `seal-guard.ps1` 必須保留 UTF-8 BOM；`.sh`／`.ps1` 行為要一致。
- 跨 skill 的行為護欄放在 `plugins/baransu/rules/anti-patterns.md`。

## 新增或退役 skill

- 上限 14：要加一個，先退役一個（以裁換建）。見 [理念](philosophy.md#14-個-skill-的上限)。
- 新 skill 先用 `/baransu:think` 自己吃自己的狗糧。
- 調整 skill 的 Automation 行時要通過 `verify-skills.py` Gate 10：`loop=drivable`／`assisted` 的 skill 要附 `references/loop-pauses.md`，並在 `_shared/loop-contract.md` §4 有一列正式註冊。

## Commit 風格

Conventional commits（`feat`、`fix`、`refactor`、`docs`、`chore`）。
