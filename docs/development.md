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
  skills/                        # 23 個 skill ＋ _shared/（跨 skill 參考、evals、scripts）
  agents/                        # 派遣用 agent：review 的 reviewer 與 verifier、health inspector、evolve
  rules/anti-patterns.md         # 跨 skill 行為護欄
codex/plugins/baransu/           # Codex 版（手動維護，Codex 的正本）
  plugin.json
  skills/                        # 與 Claude 版逐檔對應；可多出 agents/openai.yaml
  .codex-agents/                 # agent 的 TOML 版
scripts/
  verify-skills.py               # 結構驗證器（含 README 理念錨點檢查）
  verify-codex-parity.py         # Claude／Codex 逐檔配對＋版本一致
docs/                            # 本文件
```

兩個 manifest 不能合併：根目錄的 `marketplace.json` 是目錄，`plugins/baransu/.claude-plugin/plugin.json` 是 manifest。`skills/`、`agents/` 放在 plugin 根目錄，不放進 `.claude-plugin/`；`plugin.json` 不放 `skills` 陣列（Claude Code 從檔案系統探索）。

## Claude 版與 Codex 版

- 兩邊並列手動維護，各自是自己平台的正本。
- Claude 版有改動時，**同一次變更**一併同步到 `codex/plugins/baransu/`。平台規則（Codex 讀哪些欄位、工具怎麼對應、agent 怎麼派）不寫在這裡，也不寫進 skill，一律用 `/baransu:codex-skill-transfer` 即時查兩邊的官方文件和 Codex 原始碼；它只留下方法，以及官方沒寫的事實清單（`references/unverified-facts.md`）。
- 內容是否正確移植由這個 skill 的稽核負責；`make parity-check` 只檢查結構：檔案逐一對應、兩份 manifest 版本一致。

### 本 repo 的鏡像慣例

這些是 baransu 自己的規定，不是平台規則。

- **檔案逐一對應**：`plugins/baransu/skills/**` 和 `codex/plugins/baransu/skills/**` 同路徑一對一。只有 `agents/openai.yaml` 和 `assets/icon-*.png` 可以只存在於 Codex 版。共用檔留在 `skills/_shared/`，不要複製進個別 skill；也不要為了 Codex 把 skill 改成自給自足的結構。
- **agent**：`plugins/baransu/agents/<name>.md` 對應 `codex/plugins/baransu/.codex-agents/<name>.toml`（`name`、`description`、`developer_instructions`）。Codex plugin 不會自動註冊 agent，所以會派 agent 的 skill，在 Codex 版加一段「Codex Port Adapter - Bundled Agent Resolution」：把 TOML 的路徑交給一般 subagent，並且不帶 parent 的對話紀錄（`fork_turns="none"`；`spawn_agent` 預設會繼承整段對話）。
- **呼叫語法**：`/baransu:x`，以及指 baransu skill 的 `/x`，改成 `$baransu:x`；references 和 scripts 裡的字串也要改。
- **skill 自己的工作目錄**：`.claude/<skill>/` 改成 `.codex/<skill>/`。但路徑如果是 skill 處理的**對象**，就照原樣不改，例如 `/health` 要稽核的 `~/.claude/projects/<slug>/memory/`、`.claude/settings.local.json`。`CLAUDE.md` 也一樣：指「agent 讀的指令檔」時改成 `AGENTS.md`，指 Claude Code 的設定檔時不改。
- **frontmatter**：Codex 只讀 `name`、`description`、`metadata.short-description`。`when_to_use` 要併進 `description`，觸發詞一個都不能少，因為 Codex 只靠 `description` 判斷要不要叫出 skill。`compatibility: Designed for Claude Code; ported to Codex.` 和 `metadata.version: 0.1.0-codex` 是舊慣例，Codex 不會讀，目前有些 skill 有、有些沒有；要保留還是統一拿掉，還沒決定。
- **防慣性停點**：Claude 版有 AskUserQuestion 輸入停點的 skill，Codex 版要加「Codex Port Adapter - Request User Input Gate」段（寫法照 `think` 的 Codex 版）：有 `request_user_input` 就用，沒有就用文字提問，然後停下來等回答。授權停點一律是硬停。
- **manifest**：`codex/plugins/baransu/plugin.json` 是 root 形式，介面設定放在 `extensions."com.openai".interface`；`version` 要和 Claude 版一致。

## 驗證

此 plugin 不寫單元測試，但測試照做。skill 好不好用跟單元測試無關，skill 壞掉也跟它們無關；skill 改版時壞的是測試、不是 skill。8.0.0 起刻意一支單元測試都不留；留下的是真的追得到 skill 好壞的測試：結構驗證器（`make test`，理念表綁定的機制錨點）、Codex parity（`make parity-check`）、各 skill `evals/` 用 `claude plugin eval` 跑、改過的 skill 真跑一次看輸出。盲評材料不進 repo。

```bash
make test         # 只跑 scripts/verify-skills.py（結構驗證器）
make parity-check # scripts/verify-codex-parity.py
make ship-check   # test ＋ parity-check，發佈前跑這個
```

- `make test` 是單一穩定入口。
- `parity-check` 刻意不放進 `make test`：開發途中兩邊可能暫時不同步。repo 沒有 CI 也沒有排程，`make ship-check` 是唯一會跑它的入口。
- 兩支腳本只用標準函式庫，Windows 上透過 WSL 直接 `make ship-check` 即可。

### 與文件相關的檢查

- `scripts/verify-skills.py` 會讀 README.md 的 `## 核心理念` 段：理念表每一列都要有一個存在於倉內的反引號路徑錨點。改首頁時保留這個標題與表格。
- 同一支腳本會掃 `plugins/`、CLAUDE.md、README.md 與兩份 manifest（`tests/` 自 8.0.0 起不存在，掃描面仍保留它以防回流），不得出現已退役 skill 的名稱或指令（含 `/contract`、`/seal`、`/book`、`/design` 的 slash 形式、`style-reviewer` 與 sealed 標記字面；`.claude/design/` 目錄名不算）。
- 它也檢查每個 skill 目錄都有 `SKILL.md`，且和 CLAUDE.md 的 skill 表一一對應；skill 表本身就是清單，沒有另外的 baseline 檔。

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
- `/learn` 完整筆記以批判層四段結尾，沒有矛盾也要明寫。
- `/read` 的 `raw/` 不可變。
- `verify-skills.py` Gate 10 是 loop-pauses 註冊表的契約；Gate 11 已退役，編號不再使用。
- 沒有 git 的專案，`/ship` 在任何歸檔搬移之前就失敗。
- 跨 skill 的行為護欄放在 `plugins/baransu/rules/anti-patterns.md`。

## 新增或退役 skill

- 新增或退役 skill 時，目錄與 CLAUDE.md 的 skill 表要在同一次變更裡一起改。
- 新 skill 先用 `/baransu:think` 自己吃自己的狗糧。
- 調整 skill 的 Automation 行時要通過 `verify-skills.py` Gate 10：`loop=drivable`／`assisted` 的 skill 要附 `references/loop-pauses.md`，並在 `_shared/loop-contract.md` §4 有一列正式註冊。

## Commit 風格

Conventional commits（`feat`、`fix`、`refactor`、`docs`、`chore`）。
