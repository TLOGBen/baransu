# Changelog

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## v2.5.1 (2026-06-17)

**`/write` 補 `argument-hint` 參數提示(輸入 `/write` 時顯示可打參數)**。plugin version 2.5.0 → 2.5.1。

### Added — 新增

1. **`/write` frontmatter 補 `argument-hint` + `user-invocable: true`**:對齊 book/design/read/learn/execute 慣例(可呼叫 skill 成對宣告兩欄位)。hint 把參數直接對應模式以利記憶:`[zh|en] [voice="…"] <text=潤稿 | prompt=生成 | file/path=校對>`。屬官方 doc 複檢列出的 MINOR 後續之一(discoverability)。

### Notes

- codex 鏡像同步重產:`argument-hint` 隨之進 codex 版 `/write`;版本同步 2.5.1。

## v2.5.0 (2026-06-17)

**`/write` 新增 Proofread（校對）模式,並對擴充後的 `/write` 跑 `/evolve` 棘輪(結構軸 84→94,3 輪皆 3/3 盲評採納)**。plugin version 2.4.5 → 2.5.0。

### Added — 新增

1. **`/write` Proofread 模式(第三模式)**:Stage 1 由 Refine/Generate 二分擴為三分(優先序 Proofread > Refine > Generate)。新增 Stage 4 校對路徑 —— 逐頁取得來源(PDF 多視窗以絕對頁碼累積、掃描頁讀不到標「無法擷取」不靜默丟棄)→ 六類作者關注收斂成三個固定 `錯誤類型`(錯別字／用語不妥／語句不通順,含台灣商業用語透鏡)→ 六欄 findings(頁數／段落上下文／原文內容／錯誤類型／建議修正／修改原因)→ 沿用 `/book` 的 Kami 設計 token 自包含渲染成 `.claude/write/錯字修改.html`。frontmatter description / 觸發詞 / Outcome Contract / Constraints 同步擴充。

### Design notes

- **不走 `/book` pipeline**:校對錯字表屬「分析輸出」,違反 `/book`「禁把 Claude 分析寫進 HTML」紅線,且無 SVG 會被 `validate-output.ts` 品質閘擋。故直接渲染、沿用 tokens.css(缺失時用乾淨現代 fallback 調色盤),不跑 SVG 閘。
- **overwrite 守衛**:`錯字修改.html` 已存在 → 改寫 `-N` 後綴並回報,杜絕覆寫前一份報告。

### `/evolve` dogfood

- 對加完功能的 `/write` 跑棘輪:R1 dim9 Robustness(PDF 多視窗契約 82→88)、R2 dim1 Trigger Clarity(frontmatter not-for 邊界 88→90)、R3 dim3/6 Failure-Mode/High-Risk(overwrite 守衛 90→94),三輪皆 3/3 盲評 strict improvement、0 回滾、結構閘全過。效能軸 dim7–9 因無 benchmark 全程標 advisory／offline,held-out 標 `no-benchmark`(誠實標,非假設)。演化包落於 `.claude/evolve/write/`(report / results.tsv / log / held-out / convergence.svg / card.png)。
- **Claude Code 官方 doc 複檢**:剔除兩條誤判(description 未超 1,536 上限;`/write` 雙語規則內容受 English-body 豁免);列出可採後續(rule sets / proofread taxonomy 外移 references/、proofread-template 統一 token、`argument-hint`、路徑 fork 約束) —— 本次未做,留待後續。

### Notes

- codex 鏡像本次僅同步版本號(2.5.0),內容未重產(Proofread 模式未反映進 codex 版);如需 codex 端對齊請另跑 `/codex-skill-transfer`。

## v2.4.5 (2026-06-16)

**`/evolve` dogfood:用 /evolve 演化 /evolve 自己,2 輪盲評棘輪(結構軸 44→48)**。plugin version 2.4.4 → 2.4.5。

### Fixed — 修正

1. **Stage 3 結構閘對「有 references/ 的 skill」假性失敗(dim 3,headroom 最大)**:原指令 `verify-skills.py <skill_dir>` 會被 verify-skills 當成 skills-root 迭代,把 skill 自己的 `references/`/`scripts/` 子目錄誤掃成 skill → 噴 `references: 缺 SKILL.md` exit 1。這讓 /evolve 對 book/design/evolve **自己** 等含 references/ 的 skill 整輪 produce nothing。改為 whole-repo 無參數模式 + 寫明陷阱。3 位盲評委各自 trace `verify-skills.py` + test fixture 實證確認。

2. **Stage 7 成果卡未持久化(dim 4)**:原「render the result card through /book」沒明說落地路徑,`成果卡`/`card.png`/「透過 /book」三方命名不一致 —— 導致上一輪 evolve 只送出暫存 PNG、沒進演化包。釘死所有工件落地 `.claude/evolve/<slug>/`、成果卡 = `card.png`、補 `convergence.svg` 語意。

### Notes

- 兩輪皆 3/3 盲評 strict improvement、0 revert、dry-run 0%;held-out 獨立層驗證 generalization pass(`硬證據`):dim-3 修正泛化到 book/design,dim-4 工件釘定 target-agnostic。
- 演化包(含本次 dogfood 正確落地的 `card.png`)落於 `.claude/evolve/evolve/`。
- 開放後續(非回歸):`held-out.md` inline 路徑、`safety-gates.md` Gate 4 殘留 `<skill_dir>` 字樣。

## v2.4.4 (2026-06-16)

**`/ship` 能力演化（由真實收尾摩擦驅動，先 `/learn` 業界做法再改）**。plugin version 2.4.3 → 2.4.4。

### Changed — 變更

1. **歸檔範圍擴大（白名單）**：Step 1/2 歸檔來源由 `{tmp,analyze,execute,think}` 擴為涵蓋全部 baransu 工作目錄 `{tmp,analyze,execute,think,design,hunt-report,evolve,review}`；`read/learn/book` 為保留產物不歸檔；Claude Code 基礎設施（worktrees/projects/jobs/settings…）以白名單機制天然不受影響。

2. **可指定 ship 到目標分支**：新增 Step 0 解析 `/ship <branch>`／`/ship 到 <branch>`／`/ship to <branch>`。land-on-target 模式（GitHub Flow 心智）將當前 worktree 分支 `merge --no-ff` 進目標分支再 push 目標；**絕不 `--force`**，遇 non-fast-forward 先 `pull --no-rebase` 再推一次。

3. **worktree 退出順化 + 安全閘**：Step 5 改為 **ancestor 安全閘** —— 拆除前以 `git merge-base --is-ancestor <branch> <safe-ref>`（Mode B 對 `origin/<target>`、Mode A 對 `origin/<branch>`）確認工作已落地才拆；精準，不像 branch-tip 啟發式會誤拒已合併分支，也不會默默丟棄未合併工作。移除採三段 fallback（`remove` → `--force` → `rm -rf` + `prune`），`branch -D` 保留。

4. **`/evolve` 棘輪打磨(dim 5 Constraint Explicitness 6→8)**：跑一輪盲評棘輪,診斷出最弱維為「紅線散在各 step、未具名」,單變數加入具名 `## Invariants` 區塊(INV-1..5),把 allowlist-only、source-emptied-not-deleted、never-force-push、ancestor-gate-before-teardown、`-D`-not-`-d` 提升為綁定 enforcing step 的具名約束。3/3 盲評一致 strict improvement、結構閘過、held-out 獨立驗證 generalization pass(且誠實標出 dim5 7/8 —— 還缺一條 INV-6「目標分支須先存在、不可 force-create」)。

5. **發行**:CLAUDE.md skills 表為通用敘述故 baseline 無需變動;codex 鏡像重產、版本同步 2.4.4。

> 設計依據:`/learn` 研究 brief 落於 `.claude/learn/briefs/ship-release-automation-git-branching-strategies.md`;`/evolve` 演化包落於 `.claude/evolve/ship/`(report / results.tsv / held-out / log)。

## v2.4.3 (2026-06-16)

**English-body 慣例落實**：把「agent-facing 內文一律英文、僅使用者輸出與 `/write` 內容留中文」這條從一句宣告，擴寫成可執行慣例並全面落實。plugin version 2.4.2 → 2.4.3。

### Changed — 變更

1. **Codify 慣例**：`CLAUDE.md` 的 English-body 條款由單句擴寫成完整定義 —— 涵蓋 `SKILL.md` body、`references/`、`skills/_shared/`、`rules/`、`agents/` system prompt；明列四類合法中文豁免（使用者輸出 / 觸發詞與 routing cue / 示範產物 / `/write` 雙語寫作內容）。

2. **全面英文化（ultracode 多 agent 盤點 + 翻譯）**：先以 17-agent 盤點量化違規（約 1,322 行 agent-facing 中文指令散文），再以 30-agent 逐檔翻譯 **51 個檔、約 2,180 行** 指令散文為英文，逐字保留 frontmatter 觸發詞、使用者輸出字串、grep anchor（design E1–E4、check.py 偵測字面、正則/CSS/code）、範例產物與 `/write` 寫作內容。熱點：`_shared/tdd.md`、`design/SKILL.md` 與五個 reference、`book/SKILL.md` 與全 reference 群（含 13 個 diagram-type）、Execute 家族 8 個 agent prompt、`codex-skill-transfer/references/CODEX_PORT_PLAN.md`、`rules/anti-patterns.md`。`evolve / read / ship` 原本 body 軸即乾淨。

3. **Gate 同步**：翻譯後對齊四處被語言耦合的測試錨點 —— `test_tdd_trigger.sh` 的被動引用語句改抓英文、`test-automation-annotation.sh` 的 loop-mode 預設句改抓 `default`（原抓 `預設`）、`tdd.md §8` 引用表改記英文句、`render-design-html.md` 的「編輯級」改譯 `editorial-tier`（避開 verify-skills 被裁名稱 `grade` 殘留掃描）、design SKILL.md 廢除目錄說明句補回 `removed/deprecated` 標記。`make test` 全綠。

4. **Codex 鏡像重產**：49 檔同步為英文鏡像，版本同步 2.4.3。

**`/book` + `/design` 達爾文式 10 輪盲評演化打磨**，plugin version 2.4.1 → 2.4.2：

### Changed — 變更

1. **/book — 10 輪棘輪（69.6→82.6；最終獨立複評 66→89。20/20 輪 keep、每輪 3/3 盲評、0 revert）**：
   - 新增 `## Red Lines（不要做什麼）` 反模式表（🛑 + 理據錨點 + 正確做法 + 權威 reference）。
   - `references/perception-guide.md`：新增 Output Anti-Slop Blacklist（8 條 grep 可驗）+ Quantified Type Scale 量化字級表 + Kami 行高禁區/單一 accent ≤5%/暖灰限定。
   - `references/slide-synthesis.md`：新增投影片字級/限高硬規則（vw/vh 雙約束 Y≥X×1.6）；SKILL.md render-time 🔴 GATE 把反 slop/字級規則由條件式升為 render 前必載；Stage 4 品質閘失敗改三段式「觸發/一線修復/兜底」。
   - `references/svg-rendering-rules.md`：修 13 型選型表 status 事實漂移，改為可 grep 二值驗證。
2. **/design — 10 輪棘輪（59.5→83.7；最終獨立複評 52→82。20/20 輪 keep、每輪 3/3 盲評、0 revert）**：
   - 新增 Decision checkpoint map + 三處行內 🔴 GATE/CHECKPOINT 顯性標記。
   - 新增 Anti-patterns 專章（5 條 ❌X→because Y→✅Z）。
   - `references/render-design-html.md`：落 Kami 編輯級排版硬規則 + E1–E4 grep 自查；`slide-checklist.md` 現象→根因→做法 fallback 正式 wire；`slide-image-prompts.md` 補 guizang P0-A-04 大字雙約束。
   - reference-honesty 修正：把假稱可跑的 script 改標 proposed 並指向真實 validator。
3. **codex 鏡像同步重產**：`/codex-skill-transfer` plugin mode 重產 book/design 鏡像（10 檔），三發行面 version 同步 2.4.2。

### 方法

達爾文式（alchaincyf/darwin-skill）：固定 9 維適應度標準 + 5 設計參考（Kami / diagram-design / guizang-ppt / huashu-design / guizang-social-card）+ 官方 Agent Skills 最佳實踐。每輪全新獨立評委盲評、不吸收前次、棘輪只進不退（嚴格進步 + `verify-skills` exit 0 + 體積 ≤150% 才 keep）。零新增檔、HTML 模板未手改、不變量全守。

### SemVer 註

patch：純改善既有 skill 的指令撰寫與產出品質，未改 skill 對外契約/功能，未新增 skill。

## v2.4.1 (2026-06-15)

**`/baransu:evolve` 自我演化三輪精修 + codex 鏡像補產**，plugin version 2.4.0 → 2.4.1：

### Changed — 變更

1. **evolve SKILL.md 三輪自演化（dogfood，皆盲評 3/3 採納）**：
   - R1 — dim3 失敗模式編碼 6→7：Stage 0.4 補上「無 benchmark / 使用者拒絕」的顯式 if-then 復原分支（只跑結構軸、硬標 dims 7–9 為 `no-benchmark`、跳過 held-out、禁靜默假裝已測效）。
   - R2 — dim4 可執行具體性 7→8：Stage 7 把未定值的 round cap 釘成 `R=6 total rounds`（與 `N=3` 對齊）。
   - R3（使用者直接回饋）— dim8 輸出保真：收尾摘要與成果卡文案強制先過 `/write` 寫成可讀白話，成果卡強制走 `/book` 渲染（禁手工拼 HTML）；`references/output-contract.md` 新增「Human-readable delivery」節。
2. **codex 鏡像全量重產**：`/codex-skill-transfer` plugin mode 重產 `codex/`，`evolve`（SKILL.md + 4 references + `evolve-diagnostician`/`evolve-judge` agent stub）正式進鏡像；三發行面 version 同步 2.4.1。

### SemVer 註

採 patch（2.4.0 → 2.4.1）：evolve skill body 精修 + 鏡像同步，無新 skill、向後相容。

## v2.4.0 (2026-06-15)

**新增第 14 個治理 skill `/baransu:evolve`（skill 演化器）**，純擴增（技能上限 13 → 14），plugin version 2.3.0 → 2.4.0：

### Added — 新增

1. **`/evolve` skill**：像訓練模型一樣優化一份 SKILL.md。固定 9 維 rubric 當選擇環境，跑只能向前轉的棘輪——獨立 diagnostician 挑最弱一維、單變數 mutation、3 個全新盲評委（中性命名、奇偶換位）≥2/3 判嚴格進步才採納、否則還原檔案級快照；連續 N=3 輪無進步收斂。含 `SKILL.md` + 4 references（`rubric-9dim` 選擇環境 / `safety-gates` 四道紅線 / `output-contract` / `provenance` 淨室）。
2. **2 個 perspective agent**：`evolve-diagnostician`（挑最弱維、只診斷不改寫）、`evolve-judge`（盲評嚴格進步，subagent depth=1）。
3. **雙軸評估與安全閘**：結構軸（9 維 rubric 靜態）+ 效果軸（real-exec 經信任+能力雙閘，否則 offline-同源重演）；held-out 加獨立層驗證防 rubric 過擬合；採納寫入釘 Authorization PAUSE（任何驅動不可跳）；回滾用檔案級 snapshot，禁 `git reset --hard` / `stash` / `clean` / `checkout`。
4. **E2E fixture**：`tests/fixtures/weak-skill/`。

### Changed — 變更

1. **技能上限 13 → 14**：同步更新 `scripts/verify-skills.py`（`EXPECTED_SKILL_COUNT` + docstring）、`tests/scripts/test_verify_skills.py`、三支 shell gate（`test-claude-md-skills-table.sh` / `test-distribution-metadata.sh` / `test-automation-annotation.sh`）、`tests/integration/claude-md-skills-baseline.txt`、`CLAUDE.md`（ceiling 句改述為「14 is the skill-count ceiling」）、`AGENTS.md`、`README.md`，以及三發行面 description（`plugin.json` / `marketplace.json` / codex `.codex-plugin/plugin.json`，皆 fourteen / 2.4.0）。

### SemVer 註

採 minor（2.3.0 → 2.4.0）：新增一個功能級 skill，向後相容。

### 建置全程

經 `/think → /review → /analyze → /execute` 全管線（兩次方向轉向：外掛式→catalog、裁撤→純擴增）；review 補抓 AGENTS.md 漏網觸點；E2E diagnostician smoke 並驅動一處 rubric 改進（dim6 vacuous-compliance 計分）。`make test` 全綠。

## v2.3.0 (2026-06-15)

**`/codex-skill-transfer` Codex Port 施工圖落地**：把 Claude→Codex 轉換從「API 對映」升級為「對抗模型慣性的配重保留」，skill metadata version 0.9.0 → 0.10.0：

### Added — 新增

1. **Capability 降級表**：`transfer.py` 新增 capability registry，每個 Claude 能力 token 對應 Codex 執行強度、替代策略、對抗的模型慣性強度、Tier 與加權風險；transfer report 新增 `Capability 降級風險 (weighted by model inertia)` 區塊。
2. **Codex Port 施工圖**：新增 `references/CODEX_PORT_PLAN.md`，明確定義「牙齒搬家，而不是降級」原則：強慣性 × 軟提示不得只靠 prompt，必須搬到 artifact gate、phase split、sandbox/approval gate 或獨立 session artifact。
3. **skill-specific adapter 注入**：Codex mirror 的 `/think`、`/review`、`/health`、`/execute` 會自動注入 adapter note，將高風險降級從報告提示變成 runtime 可見流程。

### Changed — 變更

1. **`/think` AskUserQuestion 搬牙**：不再降成一般文字詢問；Codex 版要求 Phase 1 只產對焦問題並停止，Phase 2 必須有 `alignment.md` 才能產出五段計畫。
2. **`/review` / `/health` 隔離驗證**：Codex 版要求先跑或查 `codex-isolation-probe.md`，若 subagent context 不夠乾淨，改以獨立 invocation/session 產 artifact 後再彙整，避免同 context 連續提問假裝多視角。
3. **`/execute` machine gate 與 durable state**：紅綠判定明確要求真實 test runner exit code；`TaskCreate` / `TaskUpdate` / `TaskGet` / `TaskList` / `TaskOutput` / `TaskStop` 改寫為 `task-map.md` durable source of truth，`update_plan` 僅是顯示層。
4. **AskUser 與 SendUserFile 分級**：`AskUserQuestion` 依 skill 分成 `/think` artifact gate、`/analyze`/`/review` authorization PAUSE、`/hunt` input gate、`/read`/`/book`/`/design` selection/cosmetic；`SendUserFile` 降成「寫檔並列絕對路徑」，列為低風險 delivery convenience。

### Added — 測試

- 擴充 `tests/scripts/test_codex_skill_transfer.py`，覆蓋 capability report 排序、`/think` alignment artifact gate、cosmetic AskUser 降級、`/execute` machine gate/task-map adapter、`SendUserFile` path delivery、reference scan。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 minor（2.2.4 → 2.3.0）：Codex port 的 runtime-facing skill body 與 transfer report 行為新增高風險 gate adapter，屬於功能級增強。

## v2.2.4 (2026-06-15)

**`/codex-skill-transfer` Codex subagent 對齊強化**（對照 2026-06-15 官方 Codex manual：Agent Skills、Build plugins、Subagents、MCP、sandbox/approval），skill metadata version 0.8.0 → 0.9.0：

### Changed — 變更

1. **多階段 subagent wording 改寫補完**：Codex mirror 不再保留 Claude `parallel Tasks` / `clean Task contexts` / `via Task` / `Dispatch **review-agent**` 等高頻語彙；轉為明確 `Spawn ... Codex subagents` wording，符合 Codex「明確要求才 spawn subagent」語意。
2. **Task 狀態面保留為 task-tracking contract**：`TaskCreate` / `TaskUpdate` / `Task Tool ID` 不再被模糊改成一般內部記憶，轉為 task-tracking record / task state wording；保留 `/execute` 的 task-map、blocked/cascade-blocked、failure_count、green-proof gate 等主 orchestrator contract。
3. **agent TOML stub 對齊官方欄位**：custom agent stubs 改為「預設繼承 parent session」語意，模型範例更新為 `gpt-5.5`（重任務）/ `gpt-5.4-mini`（輕量讀取掃描），reasoning effort 列 `minimal | low | medium | high | xhigh`，補 `.codex/agents/` project-scoped 路徑與 `skills.config` 註解。
4. **stub sandbox/approval 提醒**：依 Claude `tools:` 分辨 read-only 與 Write/Edit/Bash 類 agent，分別提示可考慮 read-only sandbox 或需人工確認 workspace-write 與 approval policy；仍不自動寫入使用者 `~/.codex/agents/`。
5. **reference scan 擴充**：references 仍不自動改寫，但現在會 flag `parallel Tasks`、`clean Task contexts`、`via Task`、`TaskCreate`、`TaskUpdate`、`Dispatch **...**`、`Workflow primitives` 等 Claude orchestration token，讓手動檢視面更完整。

### Added — 測試

- 新增 `tests/scripts/test_codex_skill_transfer.py`，直接鎖住 body rewrite、description rewrite、agent stub shape/sandbox hint、reference scan 四組行為。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 patch（2.2.3 → 2.2.4）：強化既有轉換器輸出與報告精度，無指令介面破壞；Codex 端行為更接近官方 subagent 模型。

## v2.2.3 (2026-06-11)

**Automation 語彙正式定義**：

### Fixed — 修正

1. **`ultracode=` / `loop=` 三值語彙落點**：`overlap`（自有多代理派遣、出貨 orchestration-interface.md 雙 adapter）/ `assist`（無 adapter、body 提示句標記可加速段）/ `neutral`（正交），與 `drivable` / `assisted` / `not-drivable` 的定義此前散落於 gate 期望表與各 body 提示句，無單一定義點——現正式寫入 `_shared/loop-contract.md` §1（Automation 行的讀取觸發已指向該檔，語彙隨之可達）。逐 skill 的分級指派仍由 `tests/skills/test-automation-annotation.sh` 釘死，文件不重複列表（避免漂移）。
2. **Scope 段過時引用清理**：「per the rule cited below」殘句（v2.2.1 內聯後已無被引規則）刪除。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 patch（2.2.2 → 2.2.3）：純文件語彙定義，無行為變更。

## v2.2.2 (2026-06-11)

**引用接線全面修復（reference wiring audit）**：稽核發現 aux 檔（`references/`、`../_shared/`）在 skill 調用時不會自動載入——只有 body 內在流程點下令 Read 的句子才會被執行。本版將「可達」引用全面升級為「會讀」的條件式祈使，並修復跨 skill 斷路徑：

### Fixed — 修正

1. **13 條 Automation 行升級為條件式祈使**：`（contract: ../_shared/loop-contract.md）` 後綴改為 `（when driven non-interactively — /loop, cron, Workflow — read ../_shared/loop-contract.md first and apply its PAUSE semantics）`，從可達指標變成讀取觸發；gate `tests/skills/test-automation-annotation.sh` 同步更新。
2. **orchestration-interface 引用由 locative 轉祈使**：execute（Step 0 前讀＋Step 4 入口重套）、learn（Stage 0 讀＋§3.5 fan-out 觸發時重套）、review（Stage 0 釘模式＋Stage 4 派發前讀）三處「contract lives in …」改為明確的 read-and-apply 指令。
3. **learn §3.5 跨 skill 斷路徑修復**：learn 不附帶 scripts/ 與 acquisition refs——install-deps、search-papers.py、gh-search.md、x-search.md、web-dynamic.md 全數補上 `../read/` 前綴（自安裝目錄可解析），gh/x lane 並加「先讀再跑」觸發句。
4. **design 路徑與過時引用修正**：export-brief Step 2 兩處 `{plugin_root}` 改為既定義的 `{skill_dir}`；Check D 過時的「design.md Appendix B」改指 `scripts/check.py` Check D；`紙-sanity.sh` 描述改寫對齊實際行為（自動定位 check.py、legacy per-file mode、內建 Kami 規則——原述的 `紙-sanity-rules.json` 並不存在）。
5. **hunt 接線修正**：repo-root 路徑 `plugins/baransu/skills/_shared/tdd.md`（安裝目錄不可解析）改 `../_shared/tdd.md` 並加讀取觸發；`hunt-search.py` 接到 Locate 階段（instrument 前先查 `.claude/hunt-report/` 既往案例），尾段無觸發提及改為儲存指標。
6. **read 平台疑難排解收進失敗路徑**：安裝失敗時先讀 `references/setup/{$PLATFORM}.md` 嘗試排解，仍失敗才停；刪除原無觸發的尾句提及。
7. **book perception-guide Layer-1 觸發**：Stage 2A Layer 1 加條件句——§1 未讀過 `references/perception-guide.md` 者套用前先讀。
8. **execute output-journal / error-reference 觸發**：Step 7 工作日誌追記改為明確 read-and-append；Error Reference 段改為「inline Fallback 未涵蓋的錯誤條件發生時讀表套用」。

### 決策記錄

- 否決獨立 References 段：會複製 ~50 條已正確的 in-body 觸發、徒增漂移面。採 in-place 條件式祈使為唯一慣例。

### Internal

- codex/ 鏡像同步重產。

### SemVer 註

採 patch（2.2.1 → 2.2.2）：文件接線與路徑修復，無行為變更。

## v2.2.1 (2026-06-11)

**loop-contract.md 供應鏈修復＋調用路徑接線**：

### Fixed — 修正

1. **PAUSE 分類學內聯**：`_shared/loop-contract.md` §1 原引用使用者私人全域 rule（`~/.claude/rules/common/platform-awareness.md`）定義 Input/Authorization PAUSE 二分法——散布的 plugin 不應依賴未隨附的本機檔（安裝者從未有該檔；本機亦已歸檔致引用死亡）。定義改為自含內聯，平台成本軸保留為背景說明。
2. **調用路徑接線**：loop-contract 此前無任何 SKILL.md 指向（僅 `rules/anti-patterns.md` 提及，而 plugin `rules/` 非 Claude Code 自動載入元件）——skill 被調用時 `Automation: ultracode=…, loop=…` 的值無處可查語義。13 個 SKILL.md 的 Automation 行統一加註 `（contract: ../_shared/loop-contract.md）`。

### Internal

- codex/ 鏡像同步重產（_shared 與 13 個 SKILL.md 鏡像更新）。

### SemVer 註

採 patch（2.2.0 → 2.2.1）：純文件修復與引用接線，無行為變更。

## v2.2.0 (2026-06-11)

**`/codex-skill-transfer` 對照 2026-06 官方 Codex 文件全面重驗**（developers.openai.com/codex：plugins/build、hooks、subagents、skills），skill metadata version 0.7.4 → 0.8.0：

### Fixed — 修正

1. **Plugin mode 安裝指引重寫**：移除不存在的 `codex plugin install` 子指令（`marketplace add` 即安裝）與錯誤的「必須帶 `--sparse`」宣稱（--sparse 只過濾 checkout，不會重定 marketplace root）；改印 Layout B 本地路徑安裝 + git URL 需 repo-root Layout A catalog 的正確指引，導向 marketplace-mapping.md §8。
2. **plugin.json 必填欄位對齊官方**：Codex 只必填 `name`（kebab-case）+ `version`（semver），`description` 為選填；name-暫代 fallback 保留但報告措辭改「(建議補上；Codex 選填)」；§3 補 component pointer 路徑 ≤125 字元、必以 `./` 開頭。
3. **marketplace source types 對齊官方**：官方文件列三種 source（local / url / git-subdir），非「local 唯一」；§8 加註 git-subdir 與 2026-05 `--sparse` 實測發現的未解衝突（先重驗再改 Layout A/B 建議）；provenance 改以官方 build docs 為主、plugin-creator system skill 為輔。

### Changed — 變更

1. **hooks 現實對齊**：Codex 確有 experimental lifecycle hooks（`~/.codex/hooks.json` / config.toml `[hooks]`；事件鏡像 Claude Code），預設關閉、信任授權、僅 command 型執行；frontmatter `hooks` drop 報告改「手動遷移至 .codex/hooks.json（experimental，預設關閉）」；plugin 層 hooks/MCP 設定不再無聲流失，改發需人工檢視行（不自動輸出指標）。
2. **`CLAUDE.md` → `AGENTS.md` body 改寫**：skill body 內的 CLAUDE.md 引用改寫為 AGENTS.md（Codex root-down 讀取，合併上限 32 KiB），翻譯處理報告行；references/*.md 不改寫，改掃描 Claude-only token（AskUserQuestion / Task tool / TodoWrite / EnterPlanMode / $ARGUMENTS / !`cmd` / CLAUDE.md）逐檔發需人工檢視行。
3. **裸 `$N` 改寫加防護**：僅當 frontmatter 宣告 `arguments` / `argument-hint` 時改寫，避免破壞 awk/sed/bash 字面 $1/$2；`$ARGUMENTS[n]` 改寫不受影響。
4. **輸出不變量落地**：每個 SKILL.md 寫出後檢查 ≤500 行、name 字元集/長度（agentskills.io ≤64）；`skills-ref validate` 在 PATH 上才跑並回報結果；違規照常輸出但入報告。
5. **commands 升級為可行動指引**：Codex custom prompts 已官方棄用——逐檔轉 Codex skill，勿移植 `~/.codex/prompts/`（0.117.0 regression）。
6. **安裝目的地指引**：single-skill/batch 模式輸出複製到 `<repo>/.agents/skills/`（專案）或 `~/.agents/skills/`（個人）——是 `.agents/` 不是 `.codex/`/`.claude/`；SKILL.md Step 2 + 報告各加一句。
7. **AskUserQuestion 行降信心**：「request_user_input 僅 Plan mode 可用」改為「無已驗證 Codex 等價物（官方文件未載；社群指南稱任一模式皆無）」——衝突浮出、不裁決；一律改寫為純文字提問。
8. **agent-mapping 欄位信心標注**：name/description/developer_instructions（必填）、model/sandbox_mode/mcp_servers（選填）、built-ins、max_threads=6/max_depth=1 已官方確認（codex/subagents）；model_reasoning_effort / skills.config / nickname_candidates 標社群來源待確認；gpt-5.4 為 2026-06 社群 opus 對等、會漂移。
9. **skill-root 孤兒子目錄列報**：非 scripts/references/assets/agents 的子目錄不複製、逐一入已捨棄。
10. **倉庫工程面**：AGENTS.md 改寫為委派檔（單一事實源指向 CLAUDE.md，只補非 Claude agent 所需）；新增 `make test` 統一驗證入口；測試套件 worktree-safe 修正（test-distribution-metadata / test_check_design 路徑重錨）。

### Internal

- transfer.py 雜項：刪除死碼 NAMED_ARG regex、修 batch 分支過時註解、description 縮減段補官方 skills-list context cap（~2% window / 8,000 chars）系統性理由註解並標注兩條 trigger-phrase regex 為 baransu 專屬啟發式；docstring 改正已退役 template 引用（openai.yaml / agent stub 實為 yaml.safe_dump / json.dumps 直建）。
- codex/ 鏡像以新版 transfer.py 全量重產（13 skills、v2.2.0），鏡像 skill body 已套 CLAUDE.md→AGENTS.md 改寫。
- verify-skills.py 對 gitignored 本地目錄全面免疫：殘留掃描排除 `*-workspace/` 與 `node_modules/`，skill discovery 排除 `*-workspace/`（skill-creator eval 工作區與本地 npm 安裝皆非散布內容；先前在留有這類本地檔的 checkout 上會誤報 'dev' 殘留、技能數 16≠13、workspace 缺 SKILL.md，導致 `make test` 紅而乾淨 worktree 綠——同一倉庫兩種結果）。

### SemVer 註

採 minor（2.1.2 → 2.2.0）：plugin mode 報告/輸出面新增需人工檢視管道與安裝指引變更屬使用者可見行為擴增；指令、frontmatter shape 向前相容。

## v2.1.2 (2026-06-11)

**`/design` 紙-preset 重新初始化揭露的三組修正**（`/design preset 紙` 等冪重跑 → lint 52 violations → 0）：

1. **slide-cores prefix-mix（Check C，8 檔）**：`section/quote/compare/data/closing/content-bullets/content-2col/kpi-grid` 內殘留 `swiss-*` 懸空 class（v1.3 共用 slide-cores 收編進 preset 時改名未盡），全數更名 `kami-*`；全倉本無任何 `.swiss-*` 樣式定義，純 class 字面修正，渲染零變動。
2. **long-form.html slot 註解誤判（Check E）**：slot contract 註解含字面 `data-slot="long-form-body"` 觸發唯一性檢查，改寫註解措辭；實際 slot 本來就唯一。
3. **DESIGN.md token 名對齊 canonical（Check D，43 處）**：§2 表與全文由上游 tw93/Kami 原名（parchment/brand/ivory…）改為 tokens.css 實際存在的 canonical 名（paper/accent/surface…），hex 與視覺規格零變動；表下加上游原名對應註記；`accent-light`/`charcoal`/`accent-tint(-strong)` 四個無 canonical 槽位者改文件列記法（去 `--` 前綴、字面 hex）。使用者裁決：放棄與上游文件逐位同步，換取文件與實際 token 一致＋lint 全綠。

root 與 preset source（`references/紙-preset/`）同步修改，維持 byte-identical；紙-sanity 與 verify-skills 全綠。採 patch：視覺輸出零變動。

## v2.1.1 (2026-06-11)

**README 潤稿（/write zh Refine）**：核心理念段去除上游品牌引用（strip-provenance 的自我實踐——規則靠防什麼掙位置，不靠來自哪裡）；理念段收尾的對仗句式與「存在性」名詞化改寫（rules 5/8 地板）；起源段一處破折號改冒號（rule 10 軟規則）；/health 表列去贅句。機制錨點路徑與技術 token 零變動，verify-skills 理念錨點檢查仍綠。採 patch：純文案，調用面零變動。

## v2.1.0 (2026-06-11)

**理念合併版**：baransu（結構化管線）×（tw93/Waza 的）規則即天花板哲學熔成一套，成文為 README「核心理念」五條（條款綁機制，錨點存在性由 verify-skills 機器驗證）。18 項收錄全數落地，每項標明對應理念條。規格軌跡：`.claude/think/baransu-v2.1-philosophy-merge-plan.md`（含 /review 複審紀錄）。

### Added — 新增

1. **`/health` 第 13 技能**〔結構是地板〕：移植 Waza /health — 體檢「使用者專案」的 agent 配置與 AI 可維護性，五層審計、預算姿態先行、Step 0 專案分級；9 支 stdlib-only 腳本＋3 個 inspector 子代理人（`agents/health-inspector-*.md`）。定位句明寫：baransu 自身結構驗證歸 `scripts/verify-skills.py`、審單次模型輸出歸 `/review`。
2. **「13 即上限、以裁換建」條款**〔規則是天花板〕：寫入 CLAUDE.md；機制錨點＝verify-skills 技能數檢查（12→13）。
3. **/review Finding Quality Gate**〔證據優先〕：Stage 6 四問門檻（file:line／觸發輸入／上下游已讀／嚴重度站得住）、HIGH/CRITICAL 三證據、「乾淨的 review 是有效的 review」、禁止為正當化呼叫製造發現。
4. **HTML 工作日誌**〔狀態落盤〕：/think 與 /review 交付物以 book golden-template 渲染至 `.claude/{think,review}/<slug>.html` 並 SendUserFile；實作期間持續追記規範外決策／變更／取捨。共用契約＝`_shared/output-journal.md`（新檔）；execute 與 tdd.md §7 各掛追記鉤子。
5. **claim-cite-first**〔證據優先〕：anti-patterns 新條「無源依賴」＋ `(verified: <how>)` / `(inferred: 未實查)` 標注慣例進 review/think 輸出格式。
6. **重述＋列步驟＋條件式等確認**〔人在授權點〕：anti-patterns 新條「悶頭就做」— 顯示永遠做；等確認分流（互動等、完全授權/ultracode/loop 走 Input-PAUSE 預設值）。
7. **anti-patterns 淨增 4 條**〔規則是天花板〕：Worktree Safety（授權層級＋隔離驗證）、不受信任內容、無源依賴、悶頭就做（6→10 條）；與 tdd.md 雙向 cross-ref。
8. **/write 長文 change-points 分支＋中文 AI 腔指紋**〔證據優先〕：~300 行以上輸出改變更點清單（可 diff 審）；writing-principles 折入指紋 4 條；em-dash 分級 — en 新 rule 8（U+2014 硬禁、U+2013 限數字區間）、zh 新 rule 10 軟規則＋voice-overridable 新語義類別；en 規則範例自違規兩處改寫。
9. **CLAUDE.md Skills 表「Not for（易混淆）」欄**〔規則是天花板〕：13 列歧義消解（RESOLVER 輕量版），單路由面。
10. **verify-skills 擴充**〔結構是地板〕：三發行面版本一致（plugin.json＝marketplace.json＝codex 鏡像，鏡像缺檔即違規）；README 理念段逐條錨點存在性檢查；`EXPECTED_SKILL_COUNT` 13。

### Changed — 變更（含行為變更，升級必讀）

1. **`/read` 預設改 local-first（隱私面破壞性變更）**〔人在授權點〕：舊版非 GitHub/PDF URL 一律先送 defuddle.md 代理；新版預設本地抽取、URL 不離機，代理需 `--use-proxy` 顯式開啟；本地品質不足時不再無聲降級走代理，改為停止並建議 `--use-proxy` 或 `--chrome`。認證／內部 URL 任何情況不得餵代理。
2. **/think、/review 的 Outcome Contract Output 行**：由「不另落檔」改為同步落檔 HTML 工作日誌（顯式契約變更）。
3. **/ship push 在 loop 驅動下升為 Authorization 等級**：loop-contract 補註 — 驅動上下文無常設授權紀錄即不得自動 push。
4. **execute/SKILL.md 瘦身 605→447 行**：四段自足內容逐字下放 `execute/references/`（green-proof-verify／goal-alignment-filter／correction-strategy／error-reference），failure_count 措辭經逐行比對 verbatim 保留；500 行官方上限 advisory 清除。
5. doc-debt 清零其餘三項：README Codex `--ref` 過時 pin → v2.1.0；book-stage0 測試修復（worktree 相對路徑＋重錨 Stage 0 區段）；anti-patterns↔tdd.md cross-ref 補齊。
6. 測試面 12→13 漣漪全清：baseline 重生（13 列）、D1 改 semver 斷言（不再釘死版本字串）、D2/D7、automation 標注表加 health（assist/assisted）。

### 盤點收尾（差異清零）

- **已存在、不重做**：Pattern-Fix Completeness（/hunt Scope Blast）、Autofix 四級路由（/review 四層 tier）。
- **declined（理由見計畫 Not building）**：make regenerate codegen、36 條 anti-patterns 照搬、/check maintainer 鏈、串聯改手動、第 14 技能。

### SemVer 註

採 minor（2.0.1 → 2.1.0）：主軸為新增（第 13 技能＋治理資產）。/read 的 local-first 預設變更具行為破壞性但屬隱私強化方向，已在本節 Changed 首條顯著標記；嚴格解讀者可視為 major 候選，維持 minor 是因調用面（指令、旗標、模式集）全部向前相容。

## v2.0.1 (2026-06-11)

**`hooks/wiki-sync.sh` 修 slug 抽取 bug**：`read/index.md` 以 `# Read Index` 標題行開頭時，表頭列落在 `NR>2` 之後，awk 把字面值 `slug`（表頭字）當成待同步 slug，產生 `sync | slug` 幽靈紀錄。修法：抽取條件追加 `$3=="slug"` 過濾。實測舊版對現行 index.md 首筆吐出 `slug`、新版正確過濾。採 patch：hook 內部行為修正，調用面零變動。

## v2.0.0 (2026-06-10)

**破壞性改版：治理瘦身，16 技能裁併為 12。** 依使用證據裁決（grade/triage/bridge 自癒迴路從未運轉、dev 使用最少），同版交付四項治理資產。規格與驗收軌跡見 `.claude/analyze/2026-06-10-baransu-v2-slim/` 與 `.claude/execute/2026-06-10-baransu-v2-slim/execute/final-report.md`。

### Removed — 移除（Breaking）

1. **四技能**：`/dev`、`/grade`、`/triage`、`/bridge`。
2. **自癒 harness 全套附屬資產**：`plugins/baransu/hooks/` 三支 telemetry 腳本（903 行；保留 hooks.json 與 wiki-sync.sh）、`plugins/baransu/scripts/` 9 檔（2,889 行，含零引用死碼 baseline-parity-score.py）、`agents/investigator-agent.md`、`_shared/` 三份 telemetry schema、耦合測試約 27 檔。
3. **升級註記（必讀）**：曾依 harness 安裝流程在 `~/.claude/settings.json` 註冊 hooks 者，需手動移除三個條目（`UserPromptSubmit` / `PostToolUse` / `Stop` → `plugins/baransu/hooks/*.py`），否則每個 session 都會呼叫已不存在的腳本。`.claude/harness/` 下的本地 telemetry 累積檔已無消費者，可自行刪除。

### Changed — 變更

1. **小任務 TDD 閘語義降級（明文承認）**：workflow-enforced（`/dev` 硬閘）→ discipline-suggested（`_shared/tdd.md` 新 §7「直接實作時的紅綠閘」文件紀律）；`/think` 與 `/hunt` 的小任務交接均改道至該節。中大型任務 `/analyze` → `/execute` 的 TDAID 閘門不受影響。`failure_count` 不變量唯一事實源維持在 execute/SKILL.md，tdd.md 只引用不複製。
2. **發行面全同步**：CLAUDE.md 技能表、README 工作流鏈、`plugin.json` 與 `marketplace.json` 全改 12 技能；`codex/` 鏡像以 transfer.py 全量重產（12 技能、v2.0.0）。

### Added — 新增

1. **Outcome Contract 四行頭 + Automation 第五行**：12 個 SKILL.md 統一 `Outcome / Done when / Evidence / Output` 契約 + `- **Automation**: ultracode=…, loop=…` 雙軸標注（review/execute/learn＝overlap・drivable；hunt/analyze/codex-skill-transfer＝assist・assisted；think＝neutral・not-drivable；其餘中立）。Done when 以可驗證條件為預設，審美／事件型技能允許事件型逃生門。
2. **`_shared/loop-contract.md`**：技能被 /loop、cron、Workflow 驅動時的契約單一知識源 — Input PAUSE 走預設值並在報告標注假設、Authorization PAUSE 任何情況硬停、三硬停承接（迭代上限／無進展偵測／預算上限）、per-skill PAUSE 分類表（review 2 點／execute 4 列／learn 6 點／think 不可驅動）。驅動上下文覆寫平台 supervised 預設，但 Authorization 永不可覆寫。
3. **`rules/anti-patterns.md` 容器**：含「收斂不堆積」與「strip-provenance」自治條款，首批 6 條跨技能護欄（巢狀 skill 呼叫、憑記憶改檔、改測試遷就實作、跳紅燈、語言慣例漂移、不 bump 版本）。
4. **雙模 orchestration interface（選項 A：單一介面＋薄 adapter）**：review/execute/learn 各加 `references/orchestration-interface.md` — 同形 finding schema、depth 不變量逐模重述（每檔 grep ≥2）、Stage 0 模式釘死（system-reminder 偵測，退化為使用者顯式聲明）。
5. **`scripts/verify-skills.py`**（repo root）：單一結構驗證入口，7 檢查面（frontmatter／引用檔存在／被裁名稱零殘留／雙 manifest 版本一致／Outcome Contract 四行齊備／Automation 標注／500 行 advisory），exit 0/1/2；附負向 fixture 測試（`tests/fixtures/verify-skills/bad-skill/`）堵驗證器自證循環。

### 驗收

`verify-skills.py` 綠燈（12/12 技能）、`claude plugin validate` 通過、pytest 20 綠、5/5 REQ 覆蓋（Final-Review needs_fixer: false）、15/15 TDAID 任務完成（1 重試、0 blocked）。

### SemVer 註

採 major（1.5.0 → 2.0.0）：移除四個使用者調用面技能，且升級需手動清理 settings.json hook 條目，破壞性明確。

## v1.5.0 (2026-06-10)

**`/design` 紙-preset 與 `/book` Kami 渲染對齊 tw93/Kami@5cd7c8e**：

- design 紙-preset：tag 三層規格（#E4ECF5 standard / #EEF2F7 lightest）、breaking-badge 例外色（#f0e0d8/#8b4513）、parchment hex 修正、上游 provenance pin；根目錄 DESIGN.md / tokens.css 重新同步至 byte-identical。
- book：修 stale `--paper`（#faf9f5 → #f5f4ed）、focal fill → #EEF2F7、node width 12 層 → 3 層 {128/144/160}、dots pattern 24 → 22（橫跨 13 個 diagram types）、arrow-link → `--brand-light` #2D5A8A；example-architecture 幾何修正後通過全部 validate-output.ts gates（先前違反 GATE-J/K）。
- 另含 `codex-skill-transfer` 修正：Codex port 排除 `*-workspace/` 目錄。

## v1.4.6 (2026-05-14)

**`/codex-skill-transfer`**：修 `emit_agent_stub` 兩條 bug，讓 13 個 agent stub TOML 成為 Codex `spawn_agent` 真正可載入的 schema（先前 Codex subagent runtime 實測四件套 `spawn_agent` / `send_input` / `wait_agent` / `close_agent` / `resume_agent` 全綠後，stub 內容的正確性從「UI 觀感」升格為「runtime 載入」）。

### Fixes — 修正

1. **F2：agent stub `description` 不再被截斷**。先前 200-char 硬切會在 11/13 個 stub 中產生 `Fills impl-checklist and returns s`、`Invoked once by /baransu:execute when Fin`、甚至 cut 在多 byte emoji 中間變 U+FFFD `�` 的情況。改為 first-line verbatim、`json.dumps` 處理 escape；descriptions 現完整保留（193–352 chars 範圍）。
2. **F3：source frontmatter `tools:` 不再被洗成空 `# mcp_servers = []`**。實際運作邏輯 source 已有但舊 cache 版（1.4.1 安裝快取）缺；本輪改跑 source transfer.py 後正常產出 `# mcp_servers = ["Read", "Grep", "Glob", "Bash", "Edit"]  # ported from Claude tools:; rename to Codex MCP server ids before enabling`——使用者複製 stub 到 `~/.codex/agents/` 後一眼看到工具能力線索。
3. **副產品**：跑 source（39k）vs cache（33k）transfer.py 的差異使 13 個 SKILL.md / reference 也套到 v0.7.3 既有但未套用的 Claude→Codex tool-name 重寫（`TaskCreate` → `track the task internally`、`AskUserQuestion` → `ask the user directly` 等）。文法略生硬，但符合 SKILL.md §Boundaries 規約。

### Internal

- 起因：本輪 `/review` 對 codex/ 派 architecture-reviewer，在 Codex subagent runtime 實測之後重新估權，把 F2/F3 升格為 needs-judgment。
- 修正：`plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py` `emit_agent_stub` line 634-642 改為 `desc = str(fm.get("description") or "").splitlines()[0]`（拿掉 200-char cap）。F3 之 mcp_servers 改寫 logic source v0.7.3 早已含。
- skill metadata version: 0.7.3 → 0.7.4。
- codex/ 重新覆蓋：13 agent stub + 13 SKILL.md/reference 被更新。

### SemVer 註

採 patch（1.4.5 → 1.4.6）：runtime schema 修正，使用者調用面（指令名、frontmatter shape）零變動。

## v1.4.5 (2026-05-14)

**`/codex-skill-transfer`**：Step 2 補一句明示 `baransu` plugin 的 `<codex-output>` 是 repo 根目錄的 `codex/`，與 `<repo-root>/.agents/plugins/marketplace.json` (Layout A catalog) 的 `source.path` 對齊。避免下次跑時又另開一個輸出目錄、把 catalog 的 `source.path` 留成 dangling。skill metadata.version 0.7.2 → 0.7.3。

## v1.4.4 (2026-05-14)

**`/review` 強化**：源自 Waza `/check` 的「Hard stops sweep + Sign-off receipt」結構化尾段機制，作為 Stage 6 balance check 之後的彙整型閘門。

### Features — 新增功能

1. **Hard stops sweep（Stage 6 後新增）**：4 條 Required item（Unverified claims / Destructive auto-execution / Unknown identifier in target / Dependency changes）+ 1 條 Optional item（Injection / hardcoded secret，僅在 Stage 4 未派 `security-reviewer` 時列出，避免雙重把關）。任一命中時，相關 finding **強制 pin 到「需判斷」**，禁止透過 balance check 降為 advisory；report 整體 verdict 改為「需判斷」或「未完成」。
2. **Sign-off receipt（report 結構化尾段）**：fenced code block，固定 8 個對齊欄位 — `files`、`scope`、`depth`、`perspectives`、`hard_stops`、`new_tests`、`doc_debt`、`e2e_status`。SKILL.md 內 pin 死每個欄位的 semantics（避免日後漂移）；其中 `perspectives` 採 baransu Stage 4 dispatched set + Stage 5 adversarial 標記（不繼承 Waza pooled-specialists 語意），`new_tests` 為純計數（不繼承 regression-first 語意，該責任歸 /dev 或 /execute）。
3. **Hard-stops-sweep checklist**（與 prose body 並列輸出）：Required 4 條永遠列出；Optional 1 條僅當 `security-reviewer` 未派時列出。每行格式 `□ <item>: not hit` 或 `☒ <item>: hit — <one-line citation>`。

### Internal

- Source：Waza `/check` skill（read material 收於 `.claude/read/material/check-review-before-you-ship/`、digest 於 `.claude/learn/digests/waza-check-skill-code-review.md`）。
- 不繼承 release-artifact missing / generated-artifact drift / version skew 等屬於 `/ship` 的條目（責任分層保留）。
- review SKILL.md +51 行。

### SemVer 註

採 patch（1.4.3 → 1.4.4）：使用者調用面（指令名、`AskUserQuestion` option labels、Stage G handoff routing）未變；尾段結構與 hard-stop 閘門屬於輸出格式擴增與內部行為加嚴，下游消費者只需忽略額外段落即可向前相容。

## v1.4.3 (2026-05-14)

**`/hunt` 強化**：源自 Waza `/hunt` 的四項增補，inline 融入既有 SKILL.md，不引入 references/ 新檔，不更動 description / when_to_use trigger 詞。

### Features — 新增功能

1. **Instrumentation: Side-effect rule**：加 log 後若觀察到行為改變（bug 消失、症狀偏移、事件順序不同），視為 timing / lifecycle / concurrency 問題的直接證據，不准當成「log 副作用」忽略——觀察動作本身已指向根因類別。
2. **Scope Blast Mode（新章節，置於 Confirm or Discard 後、Bisect Mode 前）**：根因確認後、宣稱 fixed 前，grep 全 repo 找同形 bug 的 N-1 個兄弟；每個 match 在 case file 的 `Scope Blast` section 寫下 `<file:line> — fix | leave: <reason> | unsure: <question>`；`unsure` 在使用者回覆後就地更新為 `unsure → fix` 或 `unsure → leave: <reason> after user reply <date>`。宣稱 fixed 雙條件：(a) 每個 match 都有紀錄，AND (b) 成功格式的 `迴歸守護` line 既點到鎖定測試、又以 `HUNT-YYYY-NNN §3` 形式反向引用 case file 該 section。
3. **Repeated Regression Mode（新章節，置於 Bisect Mode 後、Hard Rules 前）**：使用者提供「好的」截圖／版本／fixture 作為 reference oracle 時的 5 步流程——列出每個症狀（保留使用者原話）→ 指認 reference oracle → 編輯前定義 pass/fail check → 比對 current vs reference 命名精確 delta → 同症狀仍在則 cross-reference Hard Rule「Same symptom recurs after fix」並從證據重建假說。末尾分流：純主觀 UI 品味 → `/baransu:design`；render / state / timing / build output / 字型 / 從已知良好版本回歸 → 留在 `/hunt`。
4. **Hard Rules +2 條**：
   - **「Fix plan or current diff touches 6 or more files (without a Scope Blast pattern justification) → Stop before adding the 6th file」**：兩個檢查時點（drafting + after each edit）；若是 class-of-bug 收網則例外（走 Scope Blast Mode）；若是 symptom-patch creep 蔓延則 narrow back 或路由到 `/baransu:analyze`。
   - **「Deflection from a specific area → Treat as a signal」**：明示為語意 trigger 非字面字串比對；附中英文具體例（「那段沒問題」「不是那邊的問題」「我已經檢查過了」/ "that part doesn't matter" / "I already checked there"），特別針對多階段 pipeline（CI segment、data pipeline stage、baransu plane handoff）中某段被排除的盲區。

### Internal

- Source：Waza `/hunt` skill（read material 收於 `.claude/read/material/waza-hunt/` 與 `.claude/read/raw/waza-hunt/`、digest 於 `.claude/learn/digests/waza-hunt-skill-diagnose-before-fix-debugging-methodology.md`）。
- 驗收路徑：`/baransu:review` 雙 perspective（architecture + quality）派發，14 findings 收斂至 5 處 surgical fix（Scope Blast 載體規格化、Repeated Regression 第 5 步改 cross-reference、Hard Rule 閾值與時點明確化、deflection trigger 雙語範例、Scope Blast 例外條款）；dry-run 用 commit `11de678` (GATE-L viewBox containment) 走完所有新段落，全部正確觸發或正確 N/A。
- hunt SKILL.md 227 → 266 行。

### SemVer 註

採 patch（1.4.2 → 1.4.3）：description / when_to_use trigger 詞依使用者明示保留原樣，沒有新增 trigger 句式；新章節是內部紀律補強，使用者調用面零變動。

## v1.4.2 (2026-05-14)

**`/think` 強化**：注入三項源自 Waza `/think`（github.com/tw93/Waza）的機制，未破壞 Stage A-G、iron rule、四選一閘門等既有骨幹。

### Features — 新增功能

1. **Step 0 改為兩層 mode selection**：第一層 Plan vs Evaluation（種類分歧），第二層 Plan 底下 Lightweight vs Full（深度）。Evaluation Mode 作為平行 H2 主體區段（與 Lightweight Mode body 平行），輸出 **Kill / Keep / Pivot** 單行裁決 + 三條基於使用者實際限制的理由。
2. **Evaluation Mode 觸發語清單與 disambiguation**：採 Waza 原文 7 句式（「判断一下」「值不值得」「有没有必要」「我不想做」「商业前景」/ "should we keep this" / "is this worth it"）；含錯誤上下文者（「判断这个报错」「判断这个错误」「这个报错值不值得修」等）一律路由至 `/hunt`，不走 Evaluation。Plan ↔ Evaluation 與 Lightweight ↔ Full 皆互斥獨立，mode 切換需手動重啟 `/think`。
3. **Stage D Premise validation 新增「記憶類型映射」子規則**：三行映射表 + 「現況覆寫記憶」原則。`decision / preference / principle` → 規劃約束（分派至 Stage F）；`pattern / learning` → 設計檢查（分派至 Stage E）；`fact` → 須以當前狀態驗證（Stage D 自身完成）。CLAUDE.md 為記憶映射的潛在全域權威來源，若衝突 global > skill-local；本版確認 CLAUDE.md 尚未編碼此語意，本 skill 暫為事實單一來源。
4. **Gotchas 改混排格式（11 條）**：保留 User-fatigue 一條 prose（多層應對需敘事完整），其餘 6 條既有 + 4 條新增 Waza 反例改 **What happened / Rule** 兩欄表格——pwd 前置、MCP 載入檢查、單一 stack 引入新語言/runtime、「判断一下报错」誤觸 Evaluation。

### Internal

- 體量檢查：SKILL.md 357 → 433 行（+21%，預算 ≤465）。Stage A-G 命名與順序、iron rule、Stage G 四選一閘門、繁中 user-facing 規約全保留。
- 不影響其他 skill：review / dev / analyze / 餘下 12 skill 皆未動。

### Fixes

- Gotchas 表格化過程中順手修正既有 Option 編號誤植：原 prose「treat it as Option 2 (還有地方要對焦)」實際應為 Option 3（Stage G 四選一閘門中 Option 2 是「批准實作（完全授權）」、Option 3 才是「還有地方要對焦」）。新表格列已對齊 Option 3。

### SemVer 註

**就 minimum-impact patch 解讀**——本版採 patch（1.4.1 → 1.4.2）：使用者調用面（指令名、`AskUserQuestion` option labels、Stage G handoff routing）皆未變，僅 SKILL.md 內部行為增補。嚴格 SemVer 解讀因 Step 0 新增使用者可見的 Plan/Evaluation 入口可落 minor；若 policy 後續要求 minor，bump 為 1.5.0。

## v1.4.0 (2026-05-13)

**Baseline-parity milestone**：對標 op7418/guizang-ppt-skill / alchaincyf/huashu-design / tw93/Kami 三 baseline 從 ~50% 推到 ≥ 90%。`baseline-parity-score.py` 自評 **100.0%**（30/33 task complete via /loop autonomous run，剩 3 為 advisory/follow-up dogfood pass）。

依據 `.claude/analyze/2026-05-12-baransu-parity-v1-4/` 規格，全 11 條 C1-C11 Criteria 達標。M3 SKILL.md fractional-heading cleanup 完成（advisory per user 定案）。

### Features — 新增功能

1. **REQ-001 / C1 — SVG 13 diagram-types 全 status=complete**：架構 / 流程 / 序列 / 狀態 / ER / 時間軸 / 泳道 / 象限 / 巢狀 / 樹 / 分層 / Venn / 金字塔，每檔含 Kami-compliant example SVG（chevron stroked markers / 節點寬 `{128,144,160}` 白名單 / focal `#1B365D` stroke + `#EEF2F7` fill / 4-multiple 座標）。
2. **REQ-001 / GATE-J/K**：`validate-output.ts` 新增兩 strict gate — GATE-J（node-width whitelist + 2-tier 例外 viewBox<360）、GATE-K（chevron-strict `<path d="M2 1 L8 5 L2 9">`）；含 negative fixtures 在 swiss-smoke-test。
3. **REQ-002 / C2 — 8 文件 schema × 3 preset × zh/en**：新增 Resume / Portfolio / One-Pager / Letter / Equity-Report / Changelog 共 6 schema md × 3 preset = 18 schema 檔 + 36 HTML 模板（每 schema zh + en variant）；en variant 採 Charter / Georgia / Palatino stack 不含 CJK 字體；人像 `<img>` 強制 `object-position: center 35%`（rule of thirds）。
4. **REQ-003 / C3 — Slide 22 layout lock list × 3 preset**：三 preset slide-cores 各擴張 9 個新 layout（timeline / process / testimonial / agenda / stat-hero / icon-grid / table-heavy / before-after / divider）+ closing 覆寫修補 v1.3 prefix-mix bug。`validate-swiss-deck.mjs` 新增 lock-list 機械驗證 + alias map for v1.3 filenames（cover→title, content-2col→two-column 等）。canonical-tokens.md 加 22-row Slide Layout Registry。
5. **REQ-003 / Modular scale 1.333**：canonical-tokens.md 新增 Modular Scale section（perfect fourth `r=1.333`）；三 preset tokens.css 重新計算 h1=2.375rem, h2=1.75rem, h3=1.3125rem；v1.2 era 2.2× / 1.24× 舊比例移除。
6. **REQ-004 / C4 — Editorial 印刷學三件套全機械化**：三 preset design-cores + golden-template 全面加 `text-wrap: pretty`；新增 `.{preset}-dropcap` class `font-size: 4.65em`（精準 3-line drop 對齊 body line-height 1.55）；prose curly quotes（`U+201C` / `U+201D`）。新增 `editorial-sanity.sh` 三 check（text-wrap pretty / dropcap font-size [4.0, 5.0]em / 0 prose straight quotes）整合進三 preset sanity wrapper。
7. **REQ-005 / C5 — Slide checklist 5 → 16 條 P0-P3**：四層分類（含 P0-S Swiss-specific / P0-A all-preset / P0-B baransu-self 三子前綴）；每條三欄（現象 / 根因 / 做法）+ source metadata（dogfood-v1.3-handoff / kami-spec-L86 / huashu-incident）。
8. **REQ-006 / C6 — Fact-Verification + Core Asset Protocol + 三 preset image-prompts**：`/book SKILL.md` Stage 2A §0 加 Fact-Verification Principle #0（regex 偵測產品/版本 / 人名+職位 → WebSearch verify → AskUserQuestion gate on 0 results）；Stage 3 §5 加 Core Asset Protocol 4-step（Ask → Generate/Search → Verify → Freeze，跳步即 fail）；三 preset image-prompts.md 含產品圖 / logo / UI 三段 + 標準負面尾巴 `no title, no footer, no page chrome, no logo, no border`。
9. **REQ-007 / C7 — `/baransu:design export-brief` 子模式**：第 4 mode（gen / preset / lint 之外）；4-step 組裝邏輯（parse preset → read sources → assemble 6-section brief → output to `.claude/design/brief-{preset}-{date}.md` 或 `--stdout`）；hex 從當前 tokens.css 動態解析（B20 邊界）；Codex CLI bridge example `codex prompt --stdin < brief-{preset}-{date}.md`。
10. **REQ-008 / C8 — DESIGN.md §9 reproducibility 三要素**：三 preset 各自含 (a) 焦點節點上限 1-2 / (b) accent hex 設計理據（HSL + oklch advisory，每 preset ≥1 條）/ (c) 我不是什麼（≥5 條 no-X anti-patterns 對齊各 preset 反例）。
11. **REQ-009 / C9 — oklch advisory**：三 preset DESIGN.md §2 accent token 旁標 `oklch(...)` 等價值 + footnote 說明 advisory；tokens.css / design-cores HTML 不含 `oklch(`（hex-only invariant preserved）。
12. **REQ-012 — `baseline-parity-score.py` 自評腳本**：11 個 check function 對應 C1-C11；加權總和 = 1.0（C1/C2/C3 各 0.15 / C4 0.10 / 其他 0.05-0.08）；`--ci` 旗標印 JSON；`--threshold N` exit 1 if < N；B26 self-exclusion assertion（C12 明文不入 score）。

### Internal Debt 收尾

- **REQ-010 M1**：`swiss-smoke-test.sh` 加 Stage 0 三 preset golden-template presence gate（kami / swiss / gd）。
- **REQ-010 M2a**：`design-token-resolver.md` 從 v1.2-era / Kami-only 升級為 v1.3+ 三 preset aware（polygon marker / 12-檔 node-width 全部標為 v1.2 retired）。
- **REQ-010 M2b**：新增 `golden-template-swiss.html`（Inter / IKB `#002FA7`）與 `golden-template-gd.html`（Roboto Flex / M3 `#6750A4`）；三檔 validate-output.ts GATE A-K 全 PASS。
- **REQ-010 M3**（advisory per user）：`/book SKILL.md` fractional headings (`### 0.0` / `### 0.5` / `### 2.5` / `### 4.5`) 整數化；`## Stage 0.5` → `## Stage 0b`（matching 2A/2B alphabetical convention）。

### Variance（已記錄非阻擋差異）

- 三 preset slide-cores 各落在 **21/22** 而非 22（`closing.html` 已存在 v1.3 軌道，本次為覆寫 prefix-mix 修補非新增）；validator soft-warns 4 missing canonical names（toc / image-full / quote-stack / breakout）— v1.4 follow-up dogfood pass 將補。
- `swiss-sanity.sh` / `google-sanity.sh` 在 TASK-editorial-04 fix attempt 內首次建立（v1.3 軌僅 `紙-sanity.sh`）。
- 完整 v1.4 fixture regen（66 layout × 3 preset + 36 schema fixture）pragmatic-scope 推遲為 follow-up；M1 以 Stage 0 presence gate 涵蓋三 preset golden-template 變體即達 REQ-010 Scenario 1 acceptance。
- spec wording `gd-*` class prefix → codebase 既有 convention `google-*`（spec drift 記錄 in pending_spec_drift；不影響功能）。

### 自評

```
$ python3 plugins/baransu/scripts/baseline-parity-score.py
✓ C1 (w=0.15): 13/13 types complete
✓ C2 (w=0.15): 18/18 new-schema md
✓ C3 (w=0.15): 3/3 presets ≥21 layouts
✓ C4 (w=0.10): 3/3 preset editorial-sanity
✓ C5 (w=0.07): P0/P1/P2/P3 = 6/4/4/2 (total 16)
✓ C6 (w=0.08): 5/5 governance checks
✓ C7 (w=0.07): 3/3 export-brief checks
✓ C8 (w=0.08): 3/3 preset §9
✓ C9 (w=0.05): 6/6 oklch checks
✓ C10 (w=0.05): 3/3 v1.3 debt (M3 advisory)
✓ C11 (w=0.05): version=1.4.0

Overall baseline-parity score: 100.0%
```

---

## v1.2.0 (2026-05-12)

### Features 新增功能

1. **Swiss preset**：`/baransu:design preset swiss` 提供 IKB 主色 + Inter/Helvetica/Noto Sans TC 字體 stack，與既有「紙」/「google-design」preset 同層
2. **`--style` 旗標**：`/baransu:book` 新增 `--style kami | swiss`（預設 kami），僅 `--format ppt` 支援；與 `--format html` 同用會報錯
3. **9 個 slide-core 版式**：cover / section / content-bullets / content-2col / data / kpi-grid / compare / quote / closing，每個含 YAML `applies_to` 供 Stage 2B 動態決策表
4. **GATE-F (class prefix 一致性)**：驗 slide HTML class 走 `kami-*` 或 `swiss-*` 單一 prefix；含 tokens.css preset 註解 tie-break
5. **GATE-G (layout registered)**：驗 `<section data-layout="X">` 對應 `{project_root}/slide-cores/X.html`；缺檔 SKIP（不 FAIL）
6. **移除 `slide-template.html`**：舊版式骨架由 `{project_root}/slide-cores/` 取代

## [1.1.17] — 2026-05-11

### 新增

- **`/baransu:book` skill** — 把任何來源轉成 Kami 主題瀏覽器 HTML 的三階段流程
  - **Acquire**：URL proxy cascade（defuddle.md → r.jina.ai → direct）、`/read` slug、`/learn` digest slug、本地檔案、`--text` 直接輸入
  - **Synthesize**：內容類型自動感知（technical / narrative / research，由 `references/perception-guide.md` 定義分類信號）、抽取 4–8 節結構 + 關鍵主張 + SVG 需求旗標、自動 slug 衝突偵測
  - **Render**：完整依照 `references/golden-template.html` 與 `design/references/paper-preset.md` 生成 Kami HTML；≥1 SVG 圖解（依感知類型決定圖解策略）；含側欄 TOC、章節編號、`.callout` / `.card-grid` / `.tradeoff-row` 等元件
  - **Validate**：`scripts/validate-output.ts` 品質閘（HTML 可解析、`<article>` 結構存在、SVG 平衡、本地資產路徑正確）；`browser-use` 自動驗跑版並儲存截圖至 `.claude/book/{slug}-preview.png`
- **`scripts/install-deps.ts`** — Stage 0 一鍵安裝 markitdown + browser-use（三段 pip fallback，不需手動）
- **`scripts/validate-output.ts`** — TypeScript 品質閘，exit 0/1/2 標準合約
- **`references/perception-guide.md`** — 內容類型分類信號表、各類視覺處理原則、SVG 策略、合成長度限制
- **`references/golden-template.html`** — Kami 黃金模板，含完整 CSS tokens、元件模式、SVG `<defs>` snippet、IntersectionObserver TOC script

### 變更

- `plugins/baransu/.claude-plugin/plugin.json` 版本提升至 1.1.17
- 關鍵字表新增 `book`

[1.1.17]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.16...1.1.17

## [1.1.16] — 2026-05-11

### 變更

- **plugin description / keywords 精簡** — `plugin.json` 與 `marketplace.json` 描述改為單句，keywords 改為 12 個 skill name 的扁平列表

[1.1.16]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.15...1.1.16

## [1.1.15] — 2026-05-07

### 新增

- **`/baransu:write` 首份 voice preset：`yu-guang-zhong-voice.md`** — 余光中 散文 voice profile 初版。基於〈聽聽那冷雨〉(1974) 萃取，捕捉**正向風格錨**（疊字節奏、聽覺擬聲、古典白話交織、句長對照、動詞密集鏈）；負規則延續 `writing-principles.md` 同源論述（拒絕英式中文、不用「被」字被動、不堆抽象名詞）。
  - 結構：風格摘要 + 6 條可執行寫法規則（含「平的 / 余光中」對照表）+ 3 段神韻 sample（疊字+擬聲+古典白話、動詞鏈+短句鎚收、跨段 motif 呼喚）+ 詞彙線索 + anti-AI floor 守則 + 來源 + 後續可擴條目
  - 來源原文已 capture 至 `.claude/read/material/ygzsw007/index.md`（via `/baransu:read --web`，Defuddle Layer 1，4361 字）
  - 啟用方式：`/baransu:write zh voice="yu-guang-zhong" [text]`，loader 走 1.1.14 加入的 `references/{name}-voice.md` 路徑

[1.1.15]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.14...1.1.15

## [1.1.14] — 2026-05-07

### 變更

- **`/baransu:write` 加 voice cue + long-input mode-aware suppression**（輕量版改動，SKILL.md +13/-2 行）
  - Stage 0 後加 **Voice cue 段**：optional `voice="..."` 參數；preset name（讀 `references/{name}-voice.md`）/ 具名作者 / 自由描述三種輸入；不覆蓋 rules 5/7/8（anti-AI 味底線）；Generate 模式忽略
  - Stage 2 Refine 末加 **Long input handling 段**：輸入 ≥ 5 段 OR ≥ 800 字（zh）/ ≥ 500 words（en）時，命中規則只改最影響的一處（mode-aware suppression）；rules 5/7/8 例外，仍每處套用
  - Rule tag examples 末新增 zh `voice 套用` / en `Voice applied`
- **零回歸保證** — 規則本文（zh rules 1-9 / en rules 1-7）零修改；`references/writing-principles.md` 整份零修改；既有 Refine 輸出格式（Before/After/修正說明）三 header 零修改；既有 zh/en prefix 行為零修改；/learn Stage 5 內部呼叫 `/write {LANG}`（不帶 voice）byte-for-byte backward compat。
- **新增結構測試** — `tests/skills/test-write-skill.sh`，14 個 bash 結構斷言（A1-A4 Voice cue 段、B1-B4 Long input handling、C1-C2 Rule tag、D1-D4 backward compat invariants），exit 0/1/2 標準閘門 contract，與既有 `tests/skills/test-{skill}-skill.sh` 命名慣例一致。

[1.1.14]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.13...1.1.14

## [1.1.13] — 2026-05-07

### 變更

- **Skill descriptions 統一三段式格式** — 全部 15 個 SKILL.md 的 `description` 改寫為 `Use When … Do … Trigger On …` 三段結構（analyze / bridge / codex-skill-transfer / design / dev / execute / grade / hunt / learn / read / review / ship / think / triage / write）。對模型 trigger 判斷與人類掃讀都更友善；繁中觸發短語全部保留。
- **codex-skill-transfer 工具映射補完 Plan Mode 差異** — `references/skill-mapping.md` §6 工具映射表新增兩列：
  - `AskUserQuestion` → 標註 Codex 的 `request_user_input` 只在 Plan mode 可用，不能當 drop-in
  - `EnterPlanMode` / `ExitPlanMode` → 明寫 Codex 沒有 skill-callable 等價物（active mode 由 developer message 切換），需改寫成 prompt-driven plan gate
- **Codex 端同步** — `codex/plugins/baransu/` 重生，反映新 description 格式 + plugin.json 版本。

[1.1.13]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.12...1.1.13

## [1.1.12] — 2026-05-07

### 新增 Codex CLI 支援

baransu 從本版起同時發行 Claude Code 與 Codex CLI 兩種變體。Claude 端是源頭，Codex 端是單向衍生產物。

- **Codex 變體目錄** — 整棵 Codex plugin tree 落在 `codex/`，獨立於 Claude 本體（`plugins/baransu/`），互不污染。
- **Repo-root marketplace catalog** — 新增 `.agents/plugins/marketplace.json`，讓使用者直接 `codex plugin marketplace add <git-url>` 即可安裝（不需 `--sparse` 或其他 flag）。
- **轉換工具 `/baransu:codex-skill-transfer`** — 一鍵把 Claude 端的 plugin / skills / marketplace 重生成 Codex 格式：
  - 自動轉 `disable-model-invocation` → `agents/openai.yaml`
  - 改寫 `$ARGUMENTS` 系列、bang-backtick shell injection 為 Codex 認得的自然語言
  - 描述超過 Codex 上限 1024 字元時自動剝除 Claude 觸發片語句子並收斂句尾
  - Plugin mode 自動產出 schema-合規的 marketplace catalog（`source` object 形、必選 `policy.installation` / `policy.authentication`、`category`）+ 巢狀 `plugins/<name>/` layout
- **Codex agent stubs** — `codex/plugins/baransu/.codex-agents-templates/` 內附 12 份 TOML stub，使用者自行複製到 `~/.codex/agents/` 啟用。
- **AGENTS.md** — Codex 版的 project-level instructions 檔，與 `CLAUDE.md` 對應。
- **README** — 新增 Codex CLI 安裝區（HTTPS / SSH / `--ref` pin tag）+「衍生產物別手改」警語。

### 修正

- 修掉 `codex-skill-transfer` SKILL.md 內殘留的 `` !`cmd` `` 字面 pattern，避免 slash-command 解析器把它當成 bash injection 而觸發 `command not found: cmd`。
- 修正 `grade` SKILL.md frontmatter — 描述含裸 colon（`tune_review_due: true`、`(00:00)`）導致 PyYAML 嚴格解析失敗。改用單引號包裹。

[1.1.12]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.4...1.1.12
