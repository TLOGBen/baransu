# Requirements

## REQ-001: 裁併與發行面清理

**描述**：grade/triage/bridge/dev 四技能及其全部附屬資產自 repo 移除，且整個發行面（plugins/、tests/、CLAUDE.md、README、雙 manifest、codex/）無功能性殘留引用。

### Scenarios

**Scenario 1: 附屬資產清除**
- **Given** repo 處於 16 技能狀態
- **When** 裁併完成
- **Then** `plugins/baransu/skills/` 下不存在 grade/triage/bridge/dev 目錄；`hooks/` 僅剩 hooks.json 與 wiki-sync.sh；`scripts/` 下 9 個 harness 腳本不存在；`agents/investigator-agent.md` 不存在；`_shared/` 僅剩 tdd.md 與新增的 loop-contract.md
- **And** wiki-sync hook 行為不受影響（hooks.json 仍僅註冊 SessionEnd wiki-sync）

**Scenario 2: 殘留掃描**
- **Given** 裁併與改寫完成
- **When** 以 word-boundary 模式掃描發行面（`\bgrade\b|\btriage\b|\bbridge\b|baransu:dev|\bdev\b` 經人工分類）
- **Then** 無任何指向被裁資產的功能性引用；upgrade/downgrade/gradient 等同形字樣與 git 歷史不計
- **And** book/SKILL.md:204 展望性 telemetry 字樣、codex-skill-transfer 的 transfer.py:819 註解與 SKILL.md:116 舉例已改寫或移除

**Scenario 3: 曾安裝者升級路徑**
- **Given** 某環境曾依 harness 安裝流程在使用者層 settings.json 註冊三個 telemetry hooks
- **When** 該環境升級至 2.0.0
- **Then** release notes 含明確指示：自 settings.json 移除三個 hook 條目，否則每個 session 會呼叫不存在的腳本

---

## REQ-002: TDD 知識源整併與交接改道

**描述**：dev 移除後，TDD 紀律維持單一知識源（_shared/tdd.md），所有原指向 dev 的交接與語義錨點改道，且閘門語義降級被明文記錄。

### Scenarios

**Scenario 1: 單一知識源**
- **Given** _shared/tdd.md 是自宣告的 TDD 單一知識來源
- **When** 整併完成
- **Then** dev 的 Red→Green 硬閘行為描述併入 tdd.md；不存在 tdd-gate.md 等第二份 TDD 檔
- **And** 「compile error 不計入 failure_count」的權威表述僅存在於 execute/SKILL.md（tdd.md 只引用不複製）

**Scenario 2: 交接改道**
- **Given** think/SKILL.md:381（Stage G 小任務交接）與 hunt/SKILL.md:230（單點修改交接）原指向 /baransu:dev
- **When** 使用者走到該交接點
- **Then** 指引為「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」
- **And** think/SKILL.md:175 的 stage 總覽、review/SKILL.md:210 的字樣、ship 的 .claude/dev/ 歸檔通道同步更新

**Scenario 3: review-agent 錨點**
- **Given** agents/review-agent.md:71 的 cosmetic path 四分類語義錨定在 dev/SKILL.md Stage 0
- **When** dev 移除
- **Then** 該錨點改掛 _shared/tdd.md 內的對應段落，review-agent 語義不變（/execute 管線不受影響）

**Scenario 4: 降級記錄**
- **Given** 小任務 TDD 閘原為 workflow-enforced（dev 的 TaskCreate 四工項＋紅燈確認）
- **When** 2.0.0 release notes 撰寫
- **Then** 明文記載「小任務 TDD 閘降級為 discipline-suggested（文件紀律）」

---

## REQ-003: Outcome Contract 移植

**描述**：12 個存活 SKILL.md 開頭帶 Outcome Contract 四行（Outcome / Done when / Evidence / Output），Done when 為可被外部驗證者判定的條件。

### Scenarios

**Scenario 1: 可驗證型技能**
- **Given** analyze/execute/ship/read/learn/hunt/design/codex-skill-transfer 等產出可觀察 artifact 的技能
- **When** 契約頭加入
- **Then** Done when 為命令、檔案存在或可數狀態（例：「.claude/analyze/{dir}/ 五層 spec 齊備且 Stage 6 審查通過」）

**Scenario 2: 事件型技能**
- **Given** think/write/book 等以人為核准或審美輸出為終點的技能
- **When** 契約頭加入
- **Then** Done when 允許事件型表述（例：think =「使用者於 Stage G 批准」）或人工檢核點列舉，不得出現「輸出存在」之類空殼條件

**Scenario 3: frontmatter 相容**
- **Given** 倉內現有兩種 frontmatter 風格（think 極簡式 vs read/learn 的 Use When/Do/Trigger On 式）
- **When** verify-skills.py 檢查契約
- **Then** 兩種風格均通過；契約四行位於 SKILL.md 正文開頭區，不強改 frontmatter 結構

---

## REQ-004: 自動化相容（loop-contract＋雙模單一介面）

**描述**：技能可被 /loop、cron、Workflow 安全驅動；review/execute/learn 在 ultracode 下可走 Workflow 編排且不破壞既有內部契約。

### Scenarios

**Scenario 1: loop 驅動下的 PAUSE 行為**
- **Given** 任一存活技能被 /loop、cron 或 Workflow 驅動（非互動）
- **When** 流程遇到 Input PAUSE（資訊性確認）
- **Then** 取推薦預設值續行，並在最終報告標注「此處採預設：{假設}」
- **And** 遇到 Authorization PAUSE（破壞性/不可逆授權）時無條件硬停，loop-contract 明文：驅動上下文覆寫平台預設，但 Authorization PAUSE 任何情況不可覆寫

**Scenario 2: PAUSE 分類表**
- **Given** review/execute/learn 三技能的全部 AskUserQuestion 互動點
- **When** loop-contract.md 撰寫
- **Then** 每個互動點被標注為 Input 或 Authorization（例：/review 的需判斷裁決 = Authorization；/learn 的評分確認 = Input）
- **And** think 標注「不可 loop 驅動」（對焦無法用預設值替代）

**Scenario 3: 雙模單一介面**
- **Given** review/execute/learn 各有手刻平行編排（perspective Tasks / TDAID 艦隊 / 四 lane fan-out）
- **When** ultracode session 中觸發（Stage 0 偵測並釘死模式，整輪不切換）
- **Then** 可改走 Workflow 原語編排，但必須產出與現行路徑同形的內部資料（review：同 schema 的 findings；execute：review-agent 回傳形狀不變，Goal-Alignment Filter 與 failure_count 記帳不受影響）
- **And** depth 不變量（review-agent 不得呼叫 /review 等）在兩模章節各自重述

**Scenario 4: 非 ultracode 回退**
- **Given** 一般 session（無 ultracode）
- **When** 三技能執行
- **Then** 走現行已驗證路徑，行為與 1.5.0 一致

---

## REQ-005: 治理資產與出貨鏈

**描述**：anti-patterns 容器與 verify-skills 驗證器就位，測試套件修剪後全綠，發行 metadata 同步至 12 技能與 2.0.0。

### Scenarios

**Scenario 1: anti-patterns 容器**
- **Given** rules/anti-patterns.md 新建
- **When** 檢視其內容
- **Then** 檔頭含自治條款（收斂不堆積：新條目須折入既有原則；strip-provenance：規則不帶事故敘事）
- **And** 首批條目來自 CLAUDE.md Non-obvious Invariants 中跨技能成立者（逐條評估，技能專屬者留在原處）

**Scenario 2: 驗證器與負向 fixture**
- **Given** scripts/verify-skills.py 新建
- **When** 對倉庫執行
- **Then** 檢查通過：12 技能 frontmatter 解析（容納兩種風格）、SKILL.md 引用的 references/ 檔案存在、被裁名稱零功能殘留（掃描 glob 與排除規則寫死在腳本內）、雙 manifest 版本一致、契約四行齊備且 Done-when 非空 — exit 0
- **And** 對負向 fixture（一份違規 SKILL stub）執行時 exit 1，該行為由 tests/ 內的 fixture 測試證明

**Scenario 3: 測試修剪**
- **Given** 現有 37 個測試檔中約 28 個耦合被裁面（含今天就紅的 test-settings-registration.sh）
- **When** 修剪完成
- **Then** 刪除清單內的測試檔不存在；test-claude-md-skills-table.sh 的 baseline 重生為 12 技能列；test_tdd_trigger.sh 與其 fixtures 修剪 dev 觸發點、保留 impl-agent/review-agent 斷言
- **And** 修剪後套件（約 6-8 檔）一次跑全綠

**Scenario 4: 發行 metadata**
- **Given** plugin.json description「sixteen governance skills」、marketplace.json 同樣字樣與 tags
- **When** 同步完成
- **Then** 兩 manifest 描述 12 技能、keywords/tags 無 dev/tdd/harness 殘留、plugin.json version = 2.0.0；CLAUDE.md 技能表 12 列；README 工作流鏈改道；`/plugin validate` 通過

**Scenario 5: codex/ 鏡像重產**
- **Given** codex/ 為 CLAUDE.md 明訂的 canonical Codex output path，現含 16 技能
- **When** 以 /codex-skill-transfer 重產
- **Then** codex/ 反映 12 技能與更新後的 SKILL.md 內容，無 grade/triage/bridge/dev 目錄
