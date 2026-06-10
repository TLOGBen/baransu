# baransu 2.0.0 — Release Notes（草稿）

> 破壞性改版：16 技能瘦身為 12 技能。本檔為草稿工件，對外發佈措辭由使用者在 /ship 前定稿。

## 一、16 → 12 技能清單與升級指示

### 技能異動

| 狀態 | 技能 |
|---|---|
| 保留（12） | `/think` `/review` `/analyze` `/execute` `/write` `/ship` `/hunt` `/read` `/design` `/learn` `/book` `/codex-skill-transfer` |
| 移除（4） | `/dev`、`/grade`、`/triage`、`/bridge` |

- `/dev`：小任務改由主 session 依 `plugins/baransu/skills/_shared/tdd.md` §7 的紅綠文件紀律直接實作（見第二節）。
- `/grade`、`/triage`、`/bridge`：自我治癒 harness 三技能整組裁除，含全部附屬資產（`plugins/baransu/hooks/` 三支 telemetry hook 腳本、`scripts/harness-reaper.py`、telemetry schema、coupled tests、`investigator-agent`）。

### 曾安裝者升級指示（必讀）

若你曾依 harness 安裝流程在 **使用者層 `~/.claude/settings.json`** 註冊過三個 telemetry hooks，升級至 2.0.0 後必須手動移除下列三個 hook 條目，否則每個 session 都會呼叫已不存在的腳本：

1. `UserPromptSubmit` → `plugins/baransu/hooks/user-prompt-submit.py`
2. `PostToolUse` → `plugins/baransu/hooks/post-tool-use.py`
3. `Stop` → `plugins/baransu/hooks/stop.py`

操作：編輯 `~/.claude/settings.json`，刪除 `hooks` 區塊中指向上述三支 `plugins/baransu/hooks/*.py` 絕對路徑的條目（僅刪 baransu 相關條目，保留其他 hooks）。本次升級不會主動修改你的 settings.json。

另外：`.claude/harness/` 下的本地 telemetry 累積檔（`telemetry.jsonl`、`grade.jsonl`、`state.json`）已無消費者，可自行刪除。

## 二、閘門語義降級記錄

| | 舊（1.x，`/dev`） | 新（2.0.0） |
|---|---|---|
| 小任務 TDD 閘 | workflow-enforced：由 `/dev` skill 的硬性紅綠閘把關 | discipline-suggested：文件紀律，無 orchestrator 把關 |

遷移指引：小任務依 `plugins/baransu/skills/_shared/tdd.md` §7 自建紅綠 task list —— 先分類（TDD 或 cosmetic）、四工項（撰寫紅燈測試 → 確認紅燈 → 撰寫綠燈實作 → 確認綠燈）、順序不可換。`/think` 與 `/hunt` 的小任務改道句均已指向該節。

中大型任務不受影響：`/analyze` → `/execute` 的 TDAID 閘門仍為 workflow-enforced。

## 三、新治理資產一覽

| 資產 | 位置 | 作用 |
|---|---|---|
| Outcome Contract 四行頭 | 各 skill `SKILL.md` 頭部 | 每個技能宣告可驗收的成果契約 |
| Loop contract | `plugins/baransu/skills/_shared/loop-contract.md` | 跨技能迴圈／重試契約的單一知識來源 |
| Anti-patterns 容器 | `plugins/baransu/rules/anti-patterns.md` | 跨技能行為反模式守則（CLAUDE.md 僅留指針） |
| TDD 紀律 | `plugins/baransu/skills/_shared/tdd.md` | 紅綠閘單一知識來源（含 §7 直接實作紀律） |
| Skill 驗證器 | `scripts/verify-skills.py` | 結構驗證 12 技能與發行面一致性 |
