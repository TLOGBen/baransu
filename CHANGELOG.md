# Changelog

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [3.1.3] - 2026-07-27

### Fixed
- `/codex-skill-transfer` 0.14.2：生成的 `SKILL.md` 或複製的 `references/*.md` 若仍含 `CLAUDE_PLUGIN_ROOT`，transfer report 會逐檔列入需人工檢視。Token 保持原文、不盲改成僅由 Codex hook command 保證提供的 `PLUGIN_ROOT`，避免 delegate 等 skill 在移植後靜默引用不存在的 runtime 變數。

## [3.0.4] - 2026-07-20

### Changed
- **週更本機自動演化（結構軸單軸，standing-auth）**：14/15 skill 體積合格（book 480 行達上限跳過），全數走 diagnostician → 單變因 mutation → 3 盲評收斂護欄（keep = 3/3 strict 且每位 judge delta ≥ 2.0）。**10 採納、0 gate-退回、4 收斂擋下**；`verify-skills.py` + `make test` 全綠。
- 採納曲線（min delta）：seal +5、analyze +4、learn +4、contract +3、evolve +2、health +2、read +2、review +2、ship +2、think +2。
  - `analyze`（dim2 階段連貫）：改寫三處殘留的 pre-R5 多代理審查孤兒引用，Stage 4/5/6 對齊現行 Stage 6 單次 checklist 自審。
  - `contract`（dim3 失敗路徑）：Step 3 寫檔前補 CONTRACT.md 已存在分支——同任務確認後覆寫、異任務停下改名，禁止靜默覆寫。
  - `evolve`（dim4 可執行具體性）：Stage 7 held-out 釘為 Stage 5 盲評機制的逐字重跑（byte-identical panel 副本＋奇偶輪派位），回歸觸發改為可判定投票語言（≥2/3 判舊版較佳）。
  - `health`（dim4）：Step 3 跨 runtime instruction-drift 的 hedge 觸發改為可判定規則。
  - `learn`（dim4）：收窄三處未釘決策規則的 hedge（lane timeout 具約束力、無來源支撐一律排除等）。
  - `read`（dim2）：兩處跨節引用由位置索引改為具名錨點，零增行。
  - `review`（dim2）：Stage 2/3 對調，Grade-scope 表三處前向引用全部轉為後向。
  - `seal`（dim6 高風險紀律）：突變抽查第 5 點升為機制級 gate——注入前留存前像、revert 後逐 byte 確認。
  - `ship`（dim6）：`git add -A` 前插入具名 secret gate，untracked/modified 路徑逐一比對封閉字面 pattern 清單（.env、*.pem、*.key、id_rsa* 等）。
  - `think`（dim1 觸發清晰）：frontmatter description 開頭宣告補上 Evaluation Mode 的 Kill/Keep 單行判決出口。
- 收斂擋下（不採納）：`codex-skill-transfer`（min 1 < 2）、`design`（min 1 < 2）、`write`（min 1 < 2）、`hunt`（非全票，2 位判退步）。

## [3.0.3] - 2026-07-20

### Changed
- `/codex-skill-transfer` 0.13.0：依最新版 Codex hooks/plugin 官方規格，把 plugin-bundled `hooks/hooks.json` 從「只報告、不輸出」升級成 outcome-level mirror。支援的 lifecycle event + `type="command"` handler 會連同 hook scripts、manifest `"hooks": "./hooks/hooks.json"` 一起產出；`SessionEnd` 等無對應事件與非 command handler 逐名報告，絕不偷換語意。報告同步提醒 `/hooks` review/trust。
- `seal-guard` 改為 Claude/Codex 雙 runtime：Claude 維持 exit 2 + stderr；Codex 以官方 `continue:false` JSON 阻擋 Stop。Codex mirror 因此第一次實際攜帶週末新增的 seal miss 機械守衛，而不再只有說明文件。

## [3.0.2] - 2026-07-19

### Changed
- `/contract`, `/seal`: structure pass per official skill-authoring best practices (narrative provenance cut, maintainer boilerplate trimmed) + one evolve ratchet round each (blind 3/3, held-out clean): contract gains the greenfield no-code branch (affirmative G2 declaration, silence non-compliant); seal gains the Baseline suite pre-flight (no-suite degradation to static pin-audit; red-baseline relative attribution).

## [3.0.1] - 2026-07-19

### Changed
- **Telemetry centralized to user scope**: all telemetry ledgers move from per-project `.claude/harness/` to `~/.claude/baransu/telemetry/{project}/{type}-{YYYY-MM}.jsonl` — split by project (git-root basename; cwd folder name when no git) and by month (monthly files are the rotation). Collection is one directory read; `BARANSU_TELEMETRY_DIR` overrides the root. seal-guard hook, `/seal` evidence obligation, and `_shared/selection-telemetry.md` all point at the central layout.

## v3.0.0 (2026-07-19)

**版圖重組：三頻段路由落地——雙塔合一＋雙釘獨立＋修憲 15**。plugin version 2.13.0 → 3.0.0。依據：10-arm harness×model 矩陣實驗＋R1–R9 改革驗證輪（完整記錄與判決在 `.claude/experiments/2026-07-19-harness-matrix/`；核心結論——品質槓桿是驗收條文的可斷言性，不是流程重量；改革版全套 p3-os′ 以 59% 成本追平頂級模型冠軍，一頁合約＋單次 seal 以 22% 成本達成行為面全數達標）。

- **BREAKING：`/baransu:execute` 移除**。其觸發詞（「開始執行」「跑 execute」「依照 analyze 執行」）與全流程併入 `/baransu:analyze`——spec 完成後直通內建執行管線（`analyze/references/execution-pipeline.md`）。舊 `/analyze` spec 要接續執行：改喚 `/baransu:analyze` 即可，Stage 0 會偵測既有 spec 直接進入執行段。
- **新增 `/contract`**：中頻段開工釘——一頁合約四節（目標／可斷言條文／錯不起表面清單／照抄常數塊），判準單一實作於 `_shared/contract-gate.md`（G1–G4＋R7）。
- **新增 `/seal`**：中頻段收工釘——單次窄域審查＋直接修正權，五點任務書（條文逐核／未釘 user-facing 表面掃描／cross-UI 一致性／常數 byte-diff／突變抽查），含 target-pin off-ramp。
- **執行管線 R8 裁剪**：summarize 派發與逐 task ctx 檔移除（agents 直讀 spec）、Red gate 降 advisory、審查退件重派上限 1；worktree 平行組、compile/failure 雙計數不變量、coverage-riding、merge/e2e-fix/final-fixer 收尾鏈全數保留。
- **修憲 14→15**（三處錨同步），附 falsifiable 條款：`/codex-skill-transfer` 遙測三個月零使用即退役回 14。
- **CLAUDE.md 三頻段路由表**：小＝直接實作（tdd.md §7）／中＝contract＋seal／大＝analyze 全管線；不得強迫任務升降頻段。
- **seal-guard hook 隨 plugin 出貨、安裝即生效**（`hooks/seal-guard.sh`＋`hooks/hooks.json` 註冊 Stop）：偵測「本 session 碰了 user-facing 表面卻無 seal 記錄」——**預設阻擋模式**（exit 2 擋停止並回饋繁中指示；`stop_hook_active` 防迴圈早退），`SEAL_GUARD=log|off` 可降級；無論何種模式都 append `.claude/harness/seal-guard.jsonl`（遙測不中斷）。falsifiable 條款：月回看誤擋率過高即把出貨預設降為 log。
- **選用遙測慣例**（`_shared/selection-telemetry.md`）：skill 選用決策記入 `.claude/harness/selection-log.jsonl`，月回看計算誤觸發／漏觸發率——觸發正確率可觀測是本次重組的成功判準。

## v2.13.0 (2026-07-17)

**/think Stage G 交接產物改為七段執行 prompt**。plugin version 2.12.0 → 2.13.0。原本 Option 2 批准後的交接物是「一段話 handoff summary」，下游實作方實際上還得回頭消化五段計畫與審議紀錄。改為直接產出執行者導向的七段骨架 prompt（Role / Goal / Success criteria / Constraints / Tools / Output / Stop rules，不適用的段落省略）：Building → Goal、驗收標準 → Success criteria、約束＋Key decisions＋Not building → Constraints、Unknowns → Stop rules 的 ask-or-stop 觸發。審議紀錄（Stage 記錄、PAUSE/批准軌跡）留在五段計畫作人審軌跡，不進交接物。依據：四管線 A/B 實驗（同一模糊需求 × 4 條規格化路徑 × 隱藏 fixture 盲評）——七段格式與五段計畫執行品質相同（16/17 打平），但產物縮 ~40%（120 行 → 74 行）、規格化省 44% 時間、下游執行 token 也較低。codex 變體同步鏡像。

## v2.12.0 (2026-07-15)

**codex-skill-transfer 修懸空 repo 路徑參照**。plugin version 2.11.0 → 2.12.0；skill 0.11.0 → 0.12.0。移植到 Codex 後，skill body 內以 `plugins/baransu/…` 開頭的 repo 根相對參照（reviewer/inspector agent 檔、`_shared` 共享文件、跨 skill 腳本）與 `.claude/` 輸出目錄在 Codex 佈局下懸空——被派的 subagent 被叫去讀不存在的路徑而失去目標。新增 `rewrite_repo_paths`：

- **agent 參照** `plugins/baransu/agents/<name>.md` → `~/.codex/agents/<name>.toml`（含 glob，如 `*-reviewer`）
- **`_shared`／跨 skill** `plugins/baransu/skills/<seg>/…` → 依檔案深度的相對路徑（SKILL.md `../`、references `../../`）；自我參照塌成 skill-root 相對（含剝除 `$VAR/` bash 錨點，如 health collector）
- **`.claude/<dir>` → `.codex/<dir>`**（輸出/設定目錄；`.claude-plugin` 不誤傷）與 `.claude-plugin/plugin.json` → `.codex-plugin/plugin.json`
- 作用面：SKILL.md body、`description` frontmatter、`references/*.md`、逐字複製的 `_shared/*.md`、agent stub TOML（扁平安裝，跳過無錨點的 `_shared` 相對化）
- **豁免**：`codex-skill-transfer` 自身（mapping 文件）與 design `slide-checklist.md`（版本紀律範例）——這些 `plugins/baransu/…` 是描述 repo 本身、非 live 參照
- 重生 `codex/`（Layout A 已提交產物）使修復對 Codex 使用者生效

## v2.11.0 (2026-07-12)

**全席 evolve ratchet 第一輪(v2.10.0 基準)——七席採納**。plugin version 2.10.0 → 2.11.0。nightly-evolve 盲測提案輪(14 skill × 診斷+變異+3 盲評,margin 2.0 守衛;採納走 Gate 1b standing-auth,結構閘 write-verify-restore 全過):

- **analyze D3**:Stage 7 Done-when 閘自身失敗分支明文化(缺 spec 檔→回產出層重生一次;goal/requirement placeholder 絕不自動修,呈使用者確認)
- **codex-skill-transfer D6**:marker-check 拒絕(exit 2)目錄 agent 絕不可自刪——列內容、換目錄或等人類明示路徑;移除「if you are certain」模糊授權
- **design D2**:Export-brief Step 2/3 懸空抽取錨點全解析到 Gen Mode 九節正典 + 每抽取點 if-then fallback
- **evolve D3**:Stage 3 窗口中斷恢復(live≠snapshot 且無採納記錄→先還原記 window-breach-restored 再診斷)
- **execute D4**:§4b per-task commit 釘死暫存範圍(ctx Files + impl 報告檔案;worktree 外絕不 git add -A)
- **learn D4**:四 hedge 改可判定規則(lane timeout 固定、排除=⚠️∧無補源、critical claim 可觀察定義、平行模型綁定)
- **ship D3**:Teardown 腳本遺失/不可執行→保守 GATE_FAIL(不手工替代刪除,保留 worktree 回報)
- 七席 margin-converged(0.5-1.5)= 大修後結構軸天花板健康收斂;design 首輪撞 session limit 由 resume 快取補跑

## v2.10.0 (2026-07-12)

**遞延美學功能一次落地——design/book 八候選連續完成(ultracode 單 workflow,12 agents)**。plugin version 2.9.0 → 2.10.0。上游素材淺 clone 實讀(Kami/diagram-design/guizang/Waza+官方 frontend-design),三視角對抗驗證(美學統一/機械正確性/出處汙染)後收斂:

- **book 圖表目錄 14→17**:新增 `type-org-chart`(含顧問情境矩陣變體,交叉引用 quadrant)、`type-class`(EXTENDS/HAS-A 邊語彙)、`type-architecture-board`(架構板);三檔逐節同構於既有結構契約,inline 範例全過機械閘門(雙 paper-mask、雙射 markers、寬度階、×4 幾何、單焦點、LEGEND、「圖:」)。`svg-rendering-rules` §4.9/§4.10 全表面同步、新增 §4.11。
- **維護型圖表 trio 契約**:`maintained-diagrams.md` —— 與 repo 同生圖表的生命週期契約(trio 工件、意圖塊、證據巡檢與權威鏈、成熟度編碼、匯出紀律、反模式);Kami 概念全文自行表述。
- **架構板規模級**:`type-architecture` 增補 ≤9 節點 → 分板升級 → 姊妹板+意圖檔邊界的三級指引。
- **design 尺寸反比權重梯**:`typography-discipline.md` —— 越大越細/越小越粗、字級下限(guizang AGPL 概念,n-gram 比對 0 verbatim);Waza 系 CJK 文字適配三件組(孤行防護、長詞/在地化字串預試、整段截斷紀律)。
- **表達軸雙軸**:`expression-axes.md` —— 背景質感軸(flat→grain→noise→gradient)與動效預算軸(none/functional/expressive),官方 skill 萃取,INFORM-not-dictate 錨定 aesthetics-foundation 元規則;三 preset 與 check.py 位元組不動(sha256 釘死)。
- **守衛升級**:`test_book_diagram_types_17`(5 檔×陳舊計數措辭掃描)+ `test_design_typography_expression_axes`;下游 `design-token-resolver`/`color-reasoning`/`slide-checklist` 計數殘留(含既存陳舊)全清。

## v2.9.0 (2026-07-11)

**美學基底與出廠修復——design/book 回歸「美學與統一」本心**。plugin version 2.8.0 → 2.9.0。三 PR 合併:

- **PR #5 經典美學基底(盲測全票勝出)**:`design/references/aesthetics-foundation.md`(238 行)——七部經典(Itten/Albers/Arnheim+格式塔/Rams/原研哉/Müller-Brockmann/Tschichold)經 /learn 消化蒸餾為決策規則,每條落名出處;元規則「理論服務於軟弱時刻,永不覆蓋直覺 — Itten」。實驗證據:2 brief × 2 條件盲測 clearly-better ×2 全票;機制=基底提供「brief→專屬材質隱喻→全 token 推導」,無基底側落入體裁先驗;理論致平坦化被反證。Gen Mode 接線(INFORM not dictate,Preset Mode 不讀);book 新視覺結構按需引用。上游吸收:Waza 方向防衛框架、反泛型禁名單、字型配對規則、huashu 採樣→收斂→論證+印墨彩度帶(MIT)、CJK 排印(screen/print line-height 分歧明文)、Kami AI-slop +6 列、diagram-design 7-role 節點表+註解原語(MIT)。
- **PR #4 煙霧測試出廠級修復**:真執行煙霧發現 4 high——全新 preset 過不了自家 sanity(lint 打中規格散文→check.py .md inline-code 豁免)、冪等重跑被 schema 欄打死(殘留 regex 對齊)、html2pptx 遇 inline SVG 必崩(SVGAnimatedString→getAttribute)、pptxgenjs 裝 global 驗 cwd(同境化);+6 medium(--dry-run 真列表化、GATE-F regex、playwright 驗二進位、GATE-F/G 接入實流程+slides-{slug}/ 落盤契約、Preset Mode staged 驗證錨點)。兩煙霧閘門實證翻綠。
- **PR #3 hunt 快徑收口**:C'2 驗證(Locate 期建檔錨點 PASS)回饋——資格判定去循環(路由時跑 blast grep)、relevant 定義、必記路由行、短表五節精確邊界、狀態梯快徑摺疊、建檔逐字引 status 行。

## v2.8.0 (2026-07-10)

**慣性帳本大修——用盲測 A/B 實驗量化「skill 對抗了哪些模型慣性」，據以增重與減重**。plugin version 2.7.7 → 2.8.0。方法論：同一任務三條件盲測（模型直接動手＝金標準／模型+skill／異模型+skill），不知情 examiner 依工件建行為側寫，盲測 judge 產出四欄慣性帳本（skill 解決的／沒解決的／skill 造成的枷鎖／無行為指紋的純紀錄條款），修訂後精簡驗證輪確認收斂。execute 跑了 4 輪（v1→v4）+ 平等 A/B 終局；read/learn/hunt 各 1 輪；write/design/book/health/evolve/think/analyze/review 以注入慣性知識的綜合審計覆蓋。

**核心量化結果（execute，NovelReader 書籤功能 fixture，2×3 模型×方法矩陣，9 工作區）**：
- 對齊目標達成（終審 ×2 一致判 yes）：Opus+v4 ↔ Fable+v4 相似度 82-83，達 Fable 自身噪音底線 81；R1 起點僅 ~50
- Opus 完成定義分 6→10（超越 Fable 直接跑的 8.9）；無 skill 對照組（Opus 直接）C2+C5 雙 FAIL 證實「中層字面主義／揭露不修復」為模型原生慣性，v2+ 的 goal-criteria gate 與 latent-defect 規則精準導正
- Fable 在 v4 下零回歸，且兩模型都主動修復 production FK 潛藏缺陷並寫 reopen 級測試

**execute（v1→v4）**：goal.md 準則字面權威 + Step 6 逐條 C{n} 交叉核對（test-green-but-production-inert = 未達成）；latent-defect 規則（小規模在地修復折入當前 task，揭露不換 ✅）；工作文件封閉清單（儀式 15 檔 490 行→9 檔 232 行）；coverage-riding 測試分層（純接線任務免 per-task prove-red，具名 pinning tests + E2E 網承擔；test_weight gate-time 決策入 task-map，事後追認=違規）；red_proof 證據欄（Red gate 不能事後追認）；per-task commit 明文化；persistence 措辭需 reopen 級證明；審計 bug 修復：compile error 無界重試死循環（獨立連續計數 3 次 BLOCKED）、cascade-blocked 遞移傳播、worktree checkout 撞 `.git/worktrees/`（改 `.claude/worktrees/`，實證 git metadata 同目錄樹永髒）、全降級路徑 spec_contradiction 不可達、green_proof 欄名跨檔漂移。

**無 git 專案不再死卡**：execute Step 0 git 探測 + L/XL 單向降級為就地序列執行（不重試不 block）、Step 7 清理失敗走 prune→範圍守衛 rm→續行；ship 探測前置於歸檔搬移、無 git 明確停止；analyze 覆寫重建分支無 git 時自動走 -N 後綴不刪任何東西；think Stage D REPO_ROOT cwd fallback；hunt bisect 非 git 跳過。

**read**：三 run 產出位元組級一致（相似度 90-95）證實核心機制條款對前沿模型無行為指紋——保留為跨 skill 格式契約；修 raw/ 重抓覆寫（`_vN` 版本化）、Chrome 探測改 lazy、SPA 偵測從屬品質檢查＋無 Chrome 明確出口、GET-first PDF 偵測、相對圖址＋重名唯一化、raw/material slug 配對改名、完成前強制完整性 pass（file(1) 驗圖/remote-ref grep=0）、四份 reference 繞管線直寫 material 修正、DOI 僅 --use-proxy 才進 cascade、candidate 多輪可達化、glob 空白檔名、首標題垃圾 slug 防呆。

**learn**：帳本反轉——skill 後勤全贏（工件契約/溯源），思考輸給自由跑（9.4-10 vs 6-9）；批判裝置只在 --brief 路徑。修：批判層四節強制進 digest 路徑（來源矛盾點含裁決＋「查無矛盾」須明說／盲點／信度評分表含可觀察訊號依據／後續調查角度，Refine 分割保護不被洗掉）、引註段落級保留（成文丟 tag=違規）、Refine 右尺寸（/write 長文 change-points 處理、draft 重複檔刪除、無變更合法）、§3.5 fan-out 候選落盤捕獲步（high：原規格 bare-topic 跑不完）、觸發器重置/範圍語意、語言偵測去 shell 化。

**hunt**：三 run 全 0 盲改直取根因——「不追根因」慣性在前沿模型不存在；skill 真值=案例記憶/Scope Blast/測試矩陣/儀器衛生。修：快徑（首儀器定根因+blast≤3 → 壓縮儀式）、迴歸守護端到端保真（helper/內部縫斷言不算——帳本抓到的字面化漏洞）、RED 證據逐字保存、bisect stash push→apply→drop 復原（原規格 stash 後永不 pop）、案例檔 Locate 期建立含 status 生命週期、刪矛盾的 allowed-tools frontmatter、新建 loop-pauses.md。

**輕量群綜合審計（3 high + 37 medium）**：design——google preset 過不了自家 lint（43 違規，check.py Check C/E 修復＋實證三 preset 全綠）、gen 模式自然語言入口死路、Gen 走 staging 原子流、新建 loop-pauses.md；book——PPT 管線 960px 規格必炸（統一 960pt×540pt）、html2pptx 多輸入合併、CJK 空 slug 鏈、fact-verify regex 過寬；write——change-points/「全部」契約補全（learn 消費路徑）、en/zh anti-AI floor 分語言、Generate 綁完整規則集；health——inspector 派發欄位對齊、collect-data.sh no-git/缺檔防呆、新建 loop-pauses.md；evolve——結構閘門改有界寫入→驗證→還原窗口（原規格驗的是快照非變異）、盲測改中性 panel alpha/beta 副本（路徑不再洩底，nightly workflow 同步）、held-out 回歸分支、非 baransu 目標降級閘門。

**think/analyze/review 複檢（15 項跨 skill 收口）**：think Option 1 先落盤 draft 再送 /review、loop-pauses 逐互動點枚舉（Stage G=Authorization）；analyze Stage 6 補 goal.md C{n} 驗證 lane（缺口死在 spec 期）、未檢查 verdict 補消費者、新建 loop-pauses.md、task 模板加測試重量建議欄（riding 鉤子）；review needs-judgment 統一 Authorization、review-agent green_proof 對齊 execute 機械閘門。

**匯流檔案契約**：ship 歸檔白名單補 write；execute Step 7 journal 選擇規則（slug 匹配→mtime 最新＋註明，review 亦為 producer）；loop-contract §4 註冊表補 /design /hunt /health /analyze 四列。

- 驗證：`make test` 全綠（19 結構斷言＋pytest 246+＋全 shell suite）、`make mirror-check` in sync、實驗全紀錄於 9 個 NovelReader 工作區 + 21 個 workflow/agent 回報。
- **同版本後續增補（release 前同 PR 累積）**：C' 驗證輪——learn 9.5/10 追平自由跑金標準（批判層四節實質到位、33 段落級引註過 Refine 保留，judge 判 improved、四 delta 全關）；hunt 9/10 ~7 分鐘（快徑生效、RED 逐字證據、四層端到端迴歸守護、首獵 skip，judge 判 improved 4/5 delta 關閉，殘餘 Locate 期建檔已補錨）。verify-skills.py Gates 10/11（loop-pauses 註冊完整性、green_proof 欄名一致，TDD 18 tests，零豁免執法）。覆蓋完成審計 21 項修復（codex mirror AskUserQuestion 改寫污染守衛、輸出 rmtree 防護、_shared 掃描、final-fixer C{n} 範圍擴充、loop-contract §2 釐清、tdd §7.1 canonical 收回）。evals 14 skill 體檢＋CLAUDE.md 七條新 invariant 入冊＋review target-pin 三表面統一。
- **燃燒窗口增補（2026-07-11）**：**L-class 機械首次實測**（雙獨立群組 utils fixture）——機械全過（正確路徑 worktrees、--no-ff merge、integration_status、閘門式 -D、終態零殘留），挖出 dispatch 工具缺席契約空白 → **serial-absorbed 第三執行模式入契約**（Step 0 tool-list 探測、分類/worktree/merge/清理全保留、角色吸收僅此模式獲准且機械閘門照舊）＋「Agent tool 恆在」偽不變式改寫＋§4a registry-before-add 封 crash-window；**L2 驗證輪 8.5/10 證實新契約可逐字遵循**，再收 8 條細化（證據持久性：/tmp 隔夜蒸發實錘 → output_tail/red_proof 必須落 checklist；§4a 單一表述；git+dispatch 雙缺席優先權；trace 自含性）。**health dogfood**（baransu repo 自審）：7 項 skill 自修（dogfood 邊界、\$HEALTH_SCRIPTS_DIR fallback、哨兵防碰撞、第三 mutation 列、雙向委派檢查、memory 路徑指引、tier 口徑）＋ AGENTS.md 漂移段刪除。**nightly-evolve dogfood ×4 批（14/14 skill ratchet 全覆蓋）**：盲測 panel（中性 alpha/beta、輪次奇偶）與 margin 守衛全程正常，六提案過檻採納——book 安裝閘門、read rename 防巢狀（抓到本輪自引入隱患）、analyze Stage 5 task 編號回填（解前向引用孤兒）、learn \$TEMP_FILES 追蹤式清理、design Gen 驗證錨點歸位（Check B/C 從永不觸發變可觸發）、review Stage 1 量化主張處置去循環；七個 margin 1-1.5 小改被守衛正確擋下（大修後結構軸收斂訊號）。nightly-evolve args 字串容忍（driver 實測坑）。

**review-agent rationale 對齊——收束 v2.7.6 的 leaf doc-debt**。plugin version 2.7.6 → 2.7.7。v2.7.6 因 C7「leaf worker 檔零改動」硬驗收，未一併對齊 `agents/review-agent.md` 的自我禁令理由，留下一筆跨檔不一致的 doc-debt（`review-agent.md:81` 仍寫「subagent depth = 1, cannot dispatch parallel Tasks」，而 `CLAUDE.md:81` 已改「AskUserQuestion 硬缺席」）。本版本以獨立微任務收束。

- **`agents/review-agent.md:81`**：Prohibition 理由由「depth = 1／cannot dispatch parallel Tasks」改為與 `CLAUDE.md:81` 一致的模型判斷式——「call 前自判 /review 非 subagent-safe：其路徑上有不可降級的 AskUserQuestion 點（target-pin），在 subagent 內硬缺席，故會 strand 該點，而非 depth 上限違規」。**行為結論不變**（不呼叫 /review、直接實作四層語意）。
- 版本 2.7.6→2.7.7（4 觸點）、codex mirror regen、`make test` 全綠。

## v2.7.6 (2026-07-07)

**Subagent 巢狀 fan-out——被托管 dispatcher 照常派 worker**。plugin version 2.7.5 → 2.7.6。四個會派 subagent 的 dispatcher skill（review/execute/evolve/health）原先隱含「自己被當 subagent 托管時不得再 fan-out」的 dispatcher-level depth=1 假設；探針（run a928109）實測 `Agent` 工具在 subagent 內恆在、`AskUserQuestion` 則硬缺席，故該假設事實錯誤。本版本移除之，並把「工具缺席」的互動降級收編進 loop-contract。經 /analyze→/execute 五組 TDAID 實作、/review 複審。

- **`_shared/loop-contract.md` §Scope/§2 擴充**：新增「被 subagent 托管（AskUserQuestion 工具缺席）」為一種 non-interactive driving context；§2 Input-PAUSE 觸發源涵蓋「工具缺席」，Authorization-PAUSE 明言不因工具缺席弱化（仍硬停／standing-auth，「Cannot ask」不等於「may assume」）；新增偵測原語小節＝**檢視自身工具清單**（非 attempt-and-catch），且只 gate 互動軸、不 gate fan-out。§3 三硬停未動。
- **四 dispatcher SKILL（＋execute/evolve orchestration-interface）**：明述 worker fan-out 不因自身被托管而停用（`Agent` 恆在），並清楚區分 dispatcher-level（可 fan-out）與 leaf-level（不再往下派）兩種 depth 語意；fan-out 與互動能力偵測為兩正交軸，不綁 AskUserQuestion proxy。evolve 歸類為純 fan-out（採納閘＝loop-contract Authorization PAUSE＋standing-auth）。
- **`review/SKILL.md` 四個 AskUserQuestion 點降級**：`:54` target-pin 缺席時 stop 回報 needs-input 不捏造；`:92` domain 缺席時不派 domain-reviewer、不宣稱覆蓋；`:231`/`:292` needs-judgment 缺席時取推薦預設＋標註「此處採預設」＋回報上層。human-present 路徑逐字保留（append-only）。
- **`rules/anti-patterns.md` 首條＋`CLAUDE.md` review-agent invariant** 改模型自主判斷式：事實前提由「depth 硬上限」更正為「AskUserQuestion 硬缺席」，改為呼叫方 call 前自判 subagent-safe，不設機器可檢的旗標／test gate（使用者明選模型自主，殘留風險由降級對映兜底）。
- **不變式保全**：leaf worker agent 檔（evolve-judge／health-inspector-*／review-agent／smart-friend-agent／evolve-diagnostician）git diff 零改動；/analyze 維持不可巢狀。
- **驗證**：fan-out 探針 depth-2 真實通過（並行 2 worker 皆回具名字串）；AskUserQuestion 硬缺席以 tool-list inspection live 觀察；`make test` 全綠、`make mirror-check` in sync、codex mirror 同步 regen。
- **/review 修正**：複審自身 diff 找到 2 項 in-scope 文字缺陷並直接修正——`review/SKILL.md` 降級節自引行號過時（改用 edit-stable Stage 名稱）、`CLAUDE.md` review-agent invariant 理由過度涵蓋 needs-judgment（收窄為僅 target-pin 不可降級）。

## v2.7.5 (2026-07-07)

**覆蓋錯置防護——第 8 條通用行為內核**。plugin version 2.7.4 → 2.7.5。多生態系盲測中唯一一致 partial 的缺陷（被引測試 mock 掉它宣稱要覆蓋的那一層 → 對該層覆蓋率其實為零）補上通用行為提示後升級為 full catch。

- **`_shared/fact-check.md` 新增「Coverage claims」節**：覆蓋宣稱（「已被測試／安全網充足／可安全重構」）不因測試「提到」被改單元就成立——須確認測試驅動**真實**實作並斷言其**實際**行為。符號出現在 mock／stub／spy／fake 建構裡是**反覆蓋**：證明測試刻意把該碼換成替身、一行都沒跑。計數某層覆蓋時排除所有落在 mock 建構內的引用；一支以其名為名卻 mock 掉該層的 spec，對它的覆蓋率是零。跨生態系（`vi.mock`／`jest.mock`／`Mock<>`／`patch`／`Mockito.mock` 皆示意）。
- **think Stage D test-safety-net inventory 同步 mock-awareness 應用點**：層級覆蓋 grep 排除落在 mock/stub/fake 內的 entry-point 引用（「0 unmocked invocations」）。
- **驗證**：Vue/JS 盲測重驗 FD3 3/3 partial→caught、surfaced_vimock 全 true、其餘三缺陷零退步。
- codex mirror 同步 regen。

## v2.7.4 (2026-07-07)

**De-overfit——移除 .NET 專用機器，蒸餾為 7 條跨生態系行為紀律**。plugin version 2.7.3 → 2.7.4。2.7.1–2.7.3 的 review 強化路線偏向了「造一台只會數某個 .NET 專案的機器」；本版本把它拉回通用型模型行為調教。3-agent 平行審計三 skill（think 6 general-keep／8 overfit-generalize、analyze 2／3、review 1 keep／9 generalize／2 remove）找出 41 個硬編生態系標記。

- **移除**：`skills/review/scripts/fact-count.sh` 與 `tests/skills/test-fact-count.sh`（.NET-only：`*.cs`／`*.csproj`／`[TestMethod]`／`class \w+Impl`／dot-prefixed 全寫死；於 2.7.3 引入，本版本移除）。
- **`_shared/fact-check.md` 改寫**：五條 .NET 指令模板 → 生態系無關的計數名詞／驗證原則（語法只當「例如 C 家族／Python／Node…」示意，非必要機器）。
- **think／analyze／review／quality-reviewer 共 11 處 de-.NET 編輯**：還原 `[(Test|TestMethod|Fact)]` 同步補丁、`bin/obj/node_modules` 三元組改為「本 stack 的建置／依賴目錄」、`*.csproj` 枚舉改為「本 stack 的專案／manifest／測試檔標記」、Facade-sign／簽核 domain 詞改為中性示意、修一處懸空 `category` 引用。
- **蒸餾出 7 條通用行為內核**：立場前提先重推導／repo-root 枚舉優先／覆蓋量在被改層／計數名詞紀律／claim-cite＋字面數字＋獨立重驗／分支盤點式測試設計／發出前掃描 fail-closed。
- **多生態系盲測**（不再只用 .NET）：對 Vue/JS 前端造植入四缺陷的計畫盲審——3/3 generality proven。關鍵發現：**移除過擬合腳本後，.NET 回歸反而更強**——腳本版漏掉的框架誤標與 facade 灌水，通用版全抓（模型改用推理推導正確 pattern，而非依賴會被誤用的腳本）。think／analyze 亦以同法補驗，各 3/3 proven。
- codex mirror 同步 regen（含移除的兩檔）。

## v2.7.3 (2026-07-07)

**review 計數名詞紀律機械化——fact-count.sh 執行器**（於 2.7.4 移除，見上）。plugin version 2.7.2 → 2.7.3。針對 review 重驗時「重跑目標自己的指令＝可重現但名詞可能錯」的失敗模式，把五類計數模板做成可執行檔。

- **`skills/review/scripts/fact-count.sh`**：五子指令（檔案／類別／呼叫點／測試案例／框架指紋），前導點硬編、逐專案指紋、排除建置目錄。
- **`_shared/fact-check.md` Executor 節＋SKILL template-authority 規則**：事實表列須由模板／腳本填、重跑目標指令永不算 ✔、偏離模板者標 `✘ (template-deviation)`。
- **後記（誠實）**：此路線被 2.7.4 判定為專案過擬合並移除；其一般性內核（一名詞一指令、獨立重跑、永不重跑目標指令）以純原則形式保留於改寫後的 fact-check.md。

## v2.7.2 (2026-07-07)

**review 事實查核紀律——量化宣稱 ✔/✘ 處置帳本**。plugin version 2.7.1 → 2.7.2。基準盲測顯示弱模型會「背書假前提」（把目標的計數宣稱列為逐條實查為真而未重驗），本版本強制逐條處置。

- **Stage 1 量化宣稱處置帳本**：目標的每個承重計數／存在／覆蓋宣稱進 claim checklist 帶 `✔`/`✘` 處置，嚴禁裸複述；輸出形狀改為含「實查結果」欄的表。
- **Unverified-claims hard-stop 擴充**：目標自寫的 `(verified:)` 標籤不算 in-session 證據；承重宣稱未被獨立重跑、或重跑出不同數字／名詞即命中，釘進需判斷層不可降 advisory。
- **quality-reviewer 重跑令**：計數宣稱須自 repo root 重跑其指令。
- **Stage 1.5 正向觸發**：計畫只要斷言任何狀態轉換／審批路徑即屬 business behavior（即使自稱「純結構重構」），強制建轉移表並對上游流查核。
- codex mirror 同步 regen。

## v2.7.1 (2026-07-07)

**think／analyze 行為紀律強化——讓 Opus 逼近 Fable**。plugin version 2.7.0 → 2.7.1。以 headless A/B 盲測（skill 快照當作業指令、匿名甲乙輪換盲評）診斷弱模型（Opus）跑 baransu 時相對強模型（Fable）的行為缺口，將缺口釘到 SKILL.md 指令縫並修補。

- **think（11 處）**：Stage D 頂層 ls 枚舉＋repo-root 搜尋紀律（缺席／計數宣稱不得來自子目錄搜尋）、立場前提重推導（Stage B 依賴的存在／計數前提於 Stage D 逐條以指令重推導、被推翻即改立場）、測試安全網盤點（覆蓋量在被改層而非下游 callee）、`(verified:)` 標籤須帶指令＋輸出引文且 prose 數字＝引文數字、計數名詞紀律（檔案／類別／呼叫點／測試案例各綁 pattern）、發出前掃描（五段每個數字重檢名詞是否仍符）。
- **analyze（5 處）**：goal Criteria 編號化（C1/C2…可機械追溯）、E2E 表每列一具名分支＋經 file:line 驗證的入口點、整合斷言禁同義反覆（「全綠／有回應」無具名值即拒）、邊界條件綁「製造該風險的 task」＋冗餘掃描、Stage 6 Agent 1 審查擴充為查可達性／業務語意／主流程完整（非僅錨點存在）。
- **成效**：think Opus 對 Fable 由懸殊差距收斂至同版對決近平手（探索完整性 2→8、決策密度反超）；analyze 測試質量六維全面提升。
- codex mirror 同步 regen。

## v2.7.0 (2026-07-06)

**/review 取得 domain 驗證能力**。plugin version 2.6.0 → 2.7.0（新視角屬功能新增，minor bump）。對「聲稱業務行為」的 target（測案集、業務 spec、聲稱狀態機行為的變更），/review 具備業務狀態可達性驗證：

- **review SKILL.md Stage 1.5 — Domain grounding**：target 聲稱業務行為時，dispatch 前先物化「狀態 × 事件 × 前置條件」轉移表；來源權威排序固定為 spec／上游狀態產生流程 **高於** 被測代碼；每列標注 `(verified: <source>)` 或 `(inferred: 未實查)`；來源不足時最多一輪 AskUserQuestion，仍不足則不派 domain-reviewer 且報告不得聲稱 domain 覆蓋（Hard stops 強制）。
- **第五視角 `agents/domain-reviewer.md`**：僅產出兩類 findings——F1 非自然情境點名（初始狀態無合法路徑可達，去留由人決定、不建議逕行刪除）、F2 覆蓋缺口清單（合法組合枚舉對照案例集）；雙重引用義務（轉移表列＋案例位置）、缺一自棄；與 quality-reviewer 的 dead-code reachability 明確分道。
- **Domain exception**：domain 激活不受 LOC tier 壓縮——≤100 LOC quick-pass 上限不會擠掉它，在 tier 選擇之外加派。
- **發行面同步**：CLAUDE.md agents 註解清單（Perspective 行）加入 domain-reviewer.md；版本 touchpoints 四處（plugin.json／marketplace.json／codex mirror manifest／codex-transfer 測試斷言）同步；新增 `tests/fixtures/domain-dryrun/` 迷你乾跑 fixture（一頁狀態機 spec＋7 測案含 2 個蓄意非法初始狀態＋乾跑結果）。
- codex mirror 同步 regen。

## v2.6.0 (2026-07-06)

**バランス 全面審計＋28 項修復掃除**。plugin version 2.5.21 → 2.6.0。36-agent ultracode 審計（18 審計員＋18 對抗驗證員）以「複雜度必須證明價值」為準繩檢視全部 14 skills＋agents＋_shared＋驗證基建，28 項 act 級發現由 15 個檔案所有權互斥的修復代理一次落地（net −264 行）：

- **移除 log-only 機制**：execute 的 Goal-Alignment Filter Metric 遙測（計數器穿四檔、無消費者）全數移除；book token-resolver 不再寫入不存在的 final-report.md；design Gen Mode Step 4 死 checkpoint（Stage 0 已注入、答案必被丟棄）整段刪除。
- **修復漂移矛盾**：learn brief-format.md（覆寫 vs .bak、TBD 公式）以 SKILL.md 為準單源化（132→54 行）；evolve safety-gates Gate 4 改為 Stage 3 唯一許可的 repo-mode 呼叫形式（原列損壞形式，可能假 gate 還原好變異）；book 文內驗證器聲明改為與 validate-output.ts 實際覆蓋一致（no-rgba／accent≤5% 非機械 gate）。
- **條件化 orchestration-interface 讀取**（review／execute／evolve／learn 四 skill 鏡像同一句式）：僅在 Workflow 驅動或 system-reminder 確認 ultracode 時讀取；預設互動路徑跳過、不寫 mode record。
- **強制 reference 讀取降級**：read 的 markitdown-guide／storage-protocol、learn 的 digest-frontmatter、health 的 baseline-principles 全文讀取改為 checklist-only＋失敗路徑指引;health Step 3 不再重跑 collect-data.sh 已執行的兩個腳本。
- **loop/harness 補洞**：write／book／read 新增 references/loop-pauses.md（含無頭預設）；review loop-pauses 補 Stage 1 target-pinning 列；analyze Stage 0.C resume 選項加【推薦】；loop-contract §1 評級理由裁剪＋§3 新增機器可查的 `LOOP_OUTCOME: ok | blocked | no-progress` 終行義務（取代 rc 信任——6/29 假綠的直接對策）＋§4 registry 與實存 loop-pauses 檔案同步（9 列）；全部 loop-pauses 前言統一為單行指回 §2。
- **hunt 記憶迴圈修復**：hunt-search.py 預設同時搜 `.claude/hunt-report/` 與 `.claude/archived/`（/ship 歸檔後案例仍可檢索），glob 涵蓋 /ship 撞名改名產生的 `*.md-{ts}`。
- **ship Step 1 detect 重寫**：python3/pathlib 單行取代裸 `find`＋unquoted word-splitting——在 zsh harness（不分詞、空 glob 中止整塊、find 可被劫持）下原寫法必然回空。
- **agents 瘦身**：architecture-reviewer §Language 53→9 行；impl-agent／review-agent 的 tdd.md 全文強制讀改為 `${CLAUDE_PLUGIN_ROOT}` 解析＋節選讀取（安裝版插件原路徑根本不存在）。
- **發行衛生**：刪除三個 *-workspace 評測殘骸（71 檔、~1.3M）及繞行它們的 skip 分支；transfer.py copy_aux 排除 node_modules（每週 regen 少拷 ~9.5M／1200 檔，鏡像瘦 73%）＋新增排除測試。
- **read**：Non-WSL2 CDP 死分支（依賴不存在的 port-3456 wrapper）刪除；四條搜尋 lane 候選選擇補【推薦】預設。
- 對照審計報告：`.claude/review/baransu-balance-audit-20260706.md`（28 act／65 advisory／8 dropped／91 keep）。

## v2.5.21 (2026-07-06)

**Fable-parity 真空點填補**。plugin version 2.5.20 → 2.5.21。把 Fable 5 的四個流程型思考模式編碼成步驟（非條款），讓 Sonnet/Opus 跑 baransu 時獲得接近 Fable 的行為紀律；步驟語言逐字改編官方遷移指南片段，intent-first 措辭（Fable 上無害重述、其他模型上是補強）。經 /think 五段計畫＋/review 雙視角（architecture＋quality）＋對抗輪複審後實作：

- **`_shared/tdd.md`**：§7.3 新增「gate 外的意外＝新 red」泛化段（含 §7.3 carve-out：gate 內結果依原表處理；一次 clean re-run 不算解釋）；新增 §7.5「宣告完成前：證據審計＋fresh-eyes 複核」（每個 claim 對到本 session tool-result；以陌生人視角重讀 diff＋重跑最窄驗證）；attribution 標注 §7.3 泛化段與 §7.5 為 baransu 原創、非上游衍生。
- **`_shared/output-journal.md`**：Required sections 新增第 4 項「學習記錄」——條件式（有 lesson 才寫、禁空段），格式 one lesson＋why it mattered，不記 repo/CLAUDE.md 已載明者。
- **`execute/references/output-formats.md`**：final-report Task 表新增「證據」欄，✅ 列必引 Pre-SWITCH green_proof 欄位（報告帶證據引用；守門仍在 Pre-SWITCH，Step 7 僅序列化）。
- review 修正折入：落點縮窄（execute SKILL.md 守門一字未動）、fable-patterns.md 不發行（對映表＋官方片段逐字引文留 `.claude/think/fable-parity-gaps.md` 附錄）、「對映表＝人工驗收 checklist、make test＝迴歸守護」術語校正。
- codex mirror 同步 regen。

## v2.5.20 (2026-07-03)

**health 新增「baseline working-principles coverage」檢查 + 通用理念改為 user scope**。plugin version 2.5.19 → 2.5.20；health skill 1.0.0 → 1.1.0。

- **health**：新增 `references/baseline-principles.md`（六條通用工作理念範本＋以「語意涵蓋」判定的檢查清單）。Structural lane 增設一段：比對 user scope（`~/.claude/CLAUDE.md` + rules）與專案 scope（`CLAUDE.md`/`AGENTS.md`）是否涵蓋這些理念，缺項按 tier 報 WARN／informational，經確認（INV-4）後從範本補上——通用原則寫 user scope、專案特定寫專案。定位為 advisory baseline，不會硬性 FAIL 或自動套用。
- **CLAUDE.md／AGENTS.md**：通用理念與風格（Think Before Coding／Simplicity First／Surgical Changes／Goal-Driven Execution／First Principles／Adversarial Review）自專案根 `CLAUDE.md` 上移至 user scope `~/.claude/CLAUDE.md`；專案端只留 バランス 身分理念（plugin-specific）。AGENTS.md 同步移除通用理念並修正 single-source 指向。
- codex mirror 同步 regen（含新 reference 與 SKILL.md 檢查段）。

## v2.5.19 (2026-07-03)

**全 skill 並行 evolve 一輪 sweep**。plugin version 2.5.18 → 2.5.19。承 v2.5.18 已完整棘輪的 think／review／execute，對其餘 11 支各跑一輪 `/evolve`（並行：14 mutator＋盲評，Opus）——每支經 structure gate＋**3/3 盲評全票**＋整體 make test 綠三重驗證後採納。全部為真缺陷修復而非文字打磨：

- **read**（d2）：圖片本地化誤用 initial slug 複製造成孤兒，搬到 Stage 3 用 final-slug，`./assets` 連結才解得開。
- **evolve**（d2）：Stage 6 not-kept 路徑補「遞增 no-progress 計數器」，補齊 Stage 7 N=3 收斂所依賴的計數生命週期。
- **book**（d5）：Red Lines 第 3 列理由與其正確做法欄自相矛盾（"超過 3 步" vs 上限 2 步/圖），對齊 SSOT。
- **learn**（d3）：`/write` 輸出缺 `**After:**` 標記時 fallback 為原文，不寫出空 digest。
- **write**（d3）：無關鍵詞的文件路徑路由到 Proofread（對齊 argument-hint），不再默默落回 Generate。
- **ship**（d3）：Step 5 補 `BRANCH_DELETE_FAILED` 明確狀態行＋手動復原指令。
- **health**（d3）：Step 1b MCP 探測本身跑不動時記 `live=unknown`，不誤報 server down。
- **codex-skill-transfer**（d3）：Step 1 補 no-match/marketplace-root 分支（transfer.py exit 2 不寫檔）。
- **analyze**（d3）：Stage 6 純措辭層未解發現記入 Stage 7 交接行，不靜默丟棄。
- **hunt**（d4）：Scope-Blast 閘「locking test」→「regression test」，四類 bug 都指對 artifact。
- **design**（d4）：Stage 0 插入位置由 hedge 改為確定性優先序。

think／review／execute 本輪 diagnostician 一致回報 **MARGINAL**（已收斂，殘餘為量測噪音或凍結欄位缺陷），正確 no-op。codex/ 鏡像經 `transfer.py` 重產（11 支同步）。

## v2.5.18 (2026-07-03)

**官方文件對標的全 skill 優化 rollup**。plugin version 2.5.17 → 2.5.18。以 2026 最新官方文件（code.claude.com skills／sub-agents／hooks／settings／plugins、docs.claude.com authoring best-practices、anthropics/skills spec v1.1、engineering blog）為基準，先展開 13 份官方來源的雙 brief（`.claude/learn/briefs/`），再經 `/think` 差距分析＋`/review` 三 perspective 審計（19 findings 全採納）產出 83 項優化計畫，逐批落地：

- **集合層（B1–B6 批次）**：14 條 description 全面第三人稱化（保觸發詞 byte-identical，總量 7,198→7,176 字元）；`verify-skills.py` 新增 5 項機制檢查（name==目錄名／無 XML tags／無保留字／per-skill desc+when_to_use ≤1536 硬檢查＋總量 advisory／plugin agents 禁 hooks·mcpServers·permissionMode），各附負向 fixture；`_shared/loop-contract.md` 補置頂 TOC；13 skill 補 `evals/` 觸發 routing fixture＋跨 skill routing 套件；6 skill 補 `references/loop-pauses.md` 一跳指標。
- **逐 skill 外科手術（14 commits）**：compaction-window 前移 load-bearing 段落、degrees-of-freedom 分級、引用深度攤平、referencing 檔案 TOC、術語一致化；`/ship` worktree 拆除鏈腳本化（`cleanup-worktree.sh`，argc/realpath/GUARD_REFUSED 防護＋fixture-repo shell test）；`/health` 三 inspector plugin-scoped 識別碼＋checker scripts 首獲 pytest 覆蓋；`/hunt` `hunt-search.py` 移入 `scripts/`＋pytest 釘現行行為。
- **`/evolve` 棘輪（think／review／execute）**：think 4 輪採納（89→~93.5，Evaluation 約束抽取閘＋裁決收束＋影響區塊證據紀律＋Step 0 soft-read 豁免）、review 3 輪（85→~90，pre-dispatch off-ramp＋/hunt·/read 路由＋mode-pin 重錨）、execute 5 輪（93→~94，error-miss fallback＋target_branch 釘定＋blocked-group merge 排除＋WIP-commit 閘＋TaskUpdate status 對映）；全部 3/3 盲評＋structure gate＋held-out 獨立層驗證，evolve 包落於 `.claude/evolve/`。
- codex/ 鏡像經 `transfer.py` 重產（think／review／execute／evolve 四支同步演化後內容）。
- **未竟**：11 支 skill 已過 Phase 5 優化但未進 evolve 棘輪（Fable 5 額度耗盡，execute r5 判評＋held-out 改於 Opus 完成）；13 項 behavior-semantic 變更與全面 description 格式重構延後為 `pending_findings`（見 `.claude/impl/`）。

## v2.5.17 (2026-07-02)

**Evidence-discipline transplant**。plugin version 2.5.16 → 2.5.17。從三個內建 skill（`/simplify`、`/verify`、`/code-review`）萃取反慣性紀律，就地改寫 16 處——`/review`（7 項：目標先落盤具體化、dispatcher==author 揭露、returned-set 收據、real-surface E2E 定義、direct-fix 條件式豁免）、`/analyze`（5 項：per-question verdicts、finding 錨點確認、修正後 clean-context 覆驗、`ls` 實測交付宣告、requirement↔test 覆蓋線）、`/execute`（4 項＋tdd.md §7.1 cosmetic 收斂為兩類：green_proof 落地 REQUIRE、條件式 direct-fix waiver、final-review 即跑證據、e2e_evidence 塊、off-goal 降級書面構造）。無新 stage／tier／工件，淨增趨近零。

### Notes

- codex/ 鏡像經 `transfer.py` 重產，補齊 v2.5.16 遞延的 `/design`／`/book` 內容轉譯與 v2.5.15 的 mechanism-necessity 段落（前次僅同步版本號）。

## v2.5.16 (2026-07-02)

**`/design` + `/book` 吸收 dataviz 色彩推理層，新增統計圖表類型**。plugin version 2.5.15 → 2.5.16。

### Added — 新增

- **`/book` 第 14 型「統計圖表」**：`svg-rendering-rules.md` §4.9/§4.10 由 13 型擴充為 14 型；同時修好一個既有、與本次無關的懸空引用（§4.9 原有 7 條指向 Candlestick／Waterfall／Donut／Bar／Line／Grouped Bar 等資料形狀的列從未接上任何 §4.10 參考檔），統一導向新的統計圖表類型。既有 13 型的判斷順序、視覺規格皆不受影響（既有型態優先）。
- **色彩距離驗證工具**：新增 `plugins/baransu/skills/_shared/scripts/color_distance.py`，獨立實作 Machado-Oliveira-Fernandes(2009) 色盲模擬 + CIE76 ΔE 計算，回傳建議而非阻斷判定；被 `/design`（設計期烘焙）與 `/book`（執行期驗證子集）共用。
- **`/design` 圖表分類色能力宣告**：`check.py` 新增獨立於 `schema:43` 的 `CHART_CAPABILITY` 版本層級（`--chart-cat-1`～`--chart-cat-6`）；preset/gen 流程新增宣告入口，宣告後 `tokens.css` 產出對應規範命名，未宣告時行為與現有完全一致。
- **色彩推理參考文件**：新增 `references/color-reasoning.md`，體例仿 `/write` 的 `writing-principles.md`（模型預設會犯的錯／為什麼錯／正確做法），涵蓋雙軸圖表、彩虹漸層、身份色無圖例等反面教材，僅統計圖表類型生成時讀取。
- **`perception-guide.md` 宣告感知單一 accent 例外**：Anti-Slop #8 新增容器範圍例外——已宣告能力的風格，統計圖表容器內的多色被放行，容器外仍受單一 accent 規則約束；未宣告或 `tokens.css` 缺失／格式錯誤時一律 fail-closed。

### Notes

- 紙／swiss／google-design 三個既有 preset 均未宣告此能力，回歸驗證確認行為零改變（`check.py` Check A-F、`validate-output.ts` GATE 結果皆 byte-for-byte 一致）。
- 測試從 83 條成長到 220 條（79 subtests），`make test` 全綠。
- **codex/ 樹本次僅同步版本號**（4 處：`plugin.json` ×2 + `marketplace.json` + `test_codex_skill_transfer.py` 硬編斷言），`/design`／`/book` SKILL.md 的內容尚未透過 `/codex-skill-transfer` 重新轉譯——下次動到 codex port 時需補跑。

## v2.5.15 (2026-06-25)

「機制必要性」原則 + loaded-context 自審慣性 gotchas。`/think` Stage E 與 `/review` Stage 6 新增「Mechanism necessity」段：新增機制前必須證明它在解決問題／推進目標，而非只留一個「我這裡失敗了」的 log；失敗路徑能跳過的規則不算預防。`/analyze` 新增 Gotchas 段（Option 2 同 session 交接違反 never-share-context）、`/execute` 新增 [loaded-orchestrator self-review trap] gotcha（驗證職能必須 fresh-context 隔離，orchestrator 不得自任）。雙樹同步。

## v2.5.14 (2026-06-23)

evolve 打磨 /design SKILL.md — gen 極端承諾軸補 extreme→value lookup table（dim4）+ 新增 named Design Invariants I1–I5 區塊（dim5）；雙樹同步。

## v2.5.13 (2026-06-23)

**`/design` Gen Mode 表現力升級 + `/book` 軟生成**。plugin version 2.5.12 → 2.5.13。雙樹（plugins/ + codex/）同步。

### Added — 新增

- **capability tokens（+5）併入 canonical，版本閘控**：`check.py` 拆 `BASE_TOKENS`(38) + `CAPABILITY_TOKENS`(5)（`--ease` / `--duration` / `--stagger-step` / `--font-display` / `--shadow-drama`）；Check B 改版本感知——無 `schema:` → 38 base、`schema: 43` → 38 base +5 capability。count 字串述為 `38(+5)`，version-pinned test 對 38 與 43 各斷言一次。
- **`/design` Gen Mode extreme-commitment 軸**：以單一「極端承諾」prompt（記憶點 + 承諾哪一個極端）取代中性強度滑桿；`極簡 minimal` 為平等極端而非預設安全值。所選極端同時驅動兩條衍生線——capability-token 值衍生 + DESIGN.md §9 expression-range 撰寫。
- **DESIGN.md §9 expression-range**：承諾的極端 / 空間原則 / 不對稱·重疊允許度 / 欄寬上限 / 強調色紀律，作為 `/book` 軟生成的軟範圍輸入。

### Changed — 變更

- **`/book` 軟生成 + validator 分層**：Stage 3 §3 由「固定 class 白名單」改為在 §9 表現範圍內**生成** section layout（§9 缺欄位則保守對稱 fallback）；硬地板（canonical token / no bare hex）不變，由 `validate-output.ts` 阻斷，軟範圍由 style-reviewer 評但不阻斷。Validator division of labor 明列 hard floor（阻斷）/ soft range（意見）兩層。

### Synced — 同步

- 雙樹（plugins/ + codex/）同步：8 個 canonical/asset 鏡像檔位元組一致；design / book SKILL.md 重放語意變更（保留 codex port marker：0.1.0-codex / AGENTS.md / ask-directly）。
- bump 四發行面 + version-pinned 硬編斷言（plugin.json ×2 + marketplace.json + CHANGELOG + test_codex_skill_transfer）。

## v2.5.12 (2026-06-23)

**`/design` + `/book` 美學與正確性修正**。plugin version 2.5.11 → 2.5.12。雙樹（plugins/ + codex/）同步。

### Fixed — 修正

- **`/book` Kami fallback golden-template 重寫**：從 v1.2 上游 token 名（`--parchment` / `--brand`…）改用 v1.3 canonical 名（`--paper` / `--accent`…，hex 不變），讓注入的 canonical `tokens.css` 能真正驅動配色。
- 同步修好該模板違反 skill 自身規範的三處：標題字重 700 → 500（Kami 不變量 #5）、h1 字級 28px → 38px（模組級數 hero）、正文行高 1.75 → 1.65（`/book` §3 禁用 ≥1.70）、figcaption 斜體移除（Kami 不變量 #10）。
- chrome 標籤（kicker / 編號 pill / meta / TOC / footer）從裸 `sans-serif` + `Arial` 改用 `var(--font-mono)` 印刷標籤調，去除襯線 preset 中的 generic-sans slop。A/B Playwright 截圖 + `validate-output.ts` GATE PASS 驗證。
- **canonical token 數量四處不一致修正**：全倉 `36` → `38`（以 `check.py` 的 `CANONICAL_TOKENS` 實際長度為準），同步修 `check.py` 註解的「19+ names」；Stage 0 inject 版本標記與 root `CLAUDE.md` 一併對齊。
- **`/design` SKILL.md 過時交叉引用修正**：移除「`check.py` legacy mode 被 `/book` validate-output.ts 在 GATE-F 呼叫」的不實描述（validator 自行實作 GATE-F prefix 檢查）。

### Changed — 變更

- 三支 `/book` golden-template（kami / swiss / gd）補上 `prefers-reduced-motion` 守門（既有 `scroll-behavior: smooth` + transitions 的無障礙缺口）。
- Kami `tokens.css` 間距註解不再宣稱嚴格「4pt grid」（3/5/10 為刻意手調步階）。

## v2.5.11 (2026-06-22)

**README 精簡 + 移除 LICENSE**。plugin version 2.5.10 → 2.5.11。

### Changed — 變更

- README 改寫為極簡版：核心理念錨點表 + 14 skill 用途簡表 + 安裝；安裝 URL 改為 GitHub 新家。
- `/book` 介紹移除「Kami」字樣。

### Removed — 移除

- 移除 `LICENSE` 檔與 `plugin.json` / codex 鏡像的 `"license"` 欄位（repo 移至公開 GitHub 後不再標註授權）。

## v2.5.10 (2026-06-22)

**reference ToC sweep + book 可達性修補**。plugin version 2.5.9 → 2.5.10。

依官方最佳實踐(/learn 摘要 + 並行稽核)落實 reference hygiene:官方規則要求 >100 行的 reference 檔須有目錄(ToC)。

### Changed — 變更

- **33 個 >100 行 reference 檔補上「章節層級(`##`)」ToC**(9 個 skill:book/codex-skill-transfer/design/execute/learn/read/write)。採只列 `##` 章節,避免如 slide-checklist 把 70 個小標題全列成雜訊(只列 19 章節)。
- **book diagram-types 可達性修補**:`svg-rendering-rules.md` 的 diagram 查表(§4.9/§4.10)原落在第 167 行、超過 `head -100` 範圍;新增的頂端 ToC 已把 §4.9/§4.10 列在前 12 行內,並在 book SKILL.md 補一行指標直指 `references/diagram-types/`。保留巢狀(just-in-time disclosure),不搬檔。
- **排除 3 個 preset `DESIGN.md` 範本檔**(google-design/swiss/紙):它們會被原封不動複製到使用者專案,加 ToC 會污染產出。
- codex 鏡像隨之重產同步。

## v2.5.9 (2026-06-23)

**每日 cron 自動演化 round 7:護欄下 7 達標、gate 後採納 6/14**。plugin version 2.5.8 → 2.5.9。

由 4:07 AM cron(standing authorization)非互動觸發,收斂護欄(margin≥2.0 + body<480)。14 skill 全評估,7 個過 blind margin 門檻,其中 learn 在 `make test` 結構 gate 被擋下(mutation 在 Outcome Contract 前插入 Invariants H2,違反「Outcome Contract 必為首個 H2」紅線),依「gate 為仲裁」原則退回 base,最終採納 6 個。採納曲線 14→14→14→5→6→2→6。

### Changed — 變更

- **採納 6 skill(margin≥2.0、blind 3/3、過 make test)**:analyze(Dim 6 把覆寫重建的刪除範圍釘成單一計算路徑 + path-scope guard)、book(Dim 4 把元件選用改成 data-shape→component 確定判準)、design(Dim 2 把 Gen Step 1.5 移到 Step 1 後消除前向引用)、hunt、read、write。
- **gate 退回 1 skill**:learn(blind 過關但破壞首個-H2 結構紅線,退回 base)。
- **保留 7 skill(收斂)**:codex-skill-transfer(非全票)、evolve/execute/health/review/think margin 1、ship margin 0.9。皆未改動。
- codex 鏡像隨採納重產同步。
- 本輪後每日 cron 轉為每週 /schedule 雲端例行。

## v2.5.8 (2026-06-22)

**每日 cron 自動演化 round 6:收斂明顯,僅採納 2/14**。plugin version 2.5.7 → 2.5.8。

由 4:07 AM cron(standing authorization)非互動觸發,收斂護欄(margin≥2.0 + body<480)。14 skill 全評估,僅 2 個達標採納,12 個保留(收斂)。採納曲線 14→14→14→5→6→2,趨近收斂。

### Changed — 變更

- **採納 2 skill(margin≥2.0、blind 3/3)**:analyze(Actionable-Specificity 把 Stage 6「findings 仍 substantial」hedge 釘成 wording/structural 二分判準)、hunt(單變量精修)。
- **保留 12 skill(收斂)**:book/codex-skill-transfer/design/evolve/execute/health/review/write margin 1、think 1.5;learn/read/ship 非全票。皆未改動。
- codex 鏡像隨採納重產同步。

## v2.5.7 (2026-06-21)

**每日 cron 自動演化 round 5:護欄下採納 6/14**。plugin version 2.5.6 → 2.5.7。

由 4:07 AM cron(standing authorization)非互動觸發,套用收斂護欄(margin≥2.0 + body<480)。14 skill 全評估,6 個達標採納,8 個保留(收斂)。

### Changed — 變更

- **採納 6 skill(margin≥2.0、blind 3/3)**:analyze(Failure-Mode-Encoding 補 Stage 0.C 目錄已存在 if-then,margin 5)、codex-skill-transfer(Actionable-Specificity 把報告 hedge 改為 MUST append Next-port follow-ups)、evolve(High-Risk-Action 把 real-exec 破壞性樣式改成硬性 if-then 禁止)、execute / review / write(各 1 個單變量精修)。
- **保留 8 skill(收斂)**:book/design/health/learn/ship/think margin 1;hunt、read 非全票。皆未改動。
- codex 鏡像隨採納重產同步。

## v2.5.6 (2026-06-20)

**每日 cron 自動演化 round 4:收斂護欄首次生效,只採納 5/14**。plugin version 2.5.5 → 2.5.6。

由 4:07 AM cron(standing authorization)非互動觸發。本輪起套用 v2.5.5 新增的收斂護欄(`scripts/nightly-evolve.workflow.js`:margin≥2.0 + body<480 行),14 skill 全評估,僅 5 個達標自動採納,9 個因邊際過小或非全票而保留(收斂)。

### Changed — 變更

- **採納 5 skill(margin≥2.0、blind 3/3)**:codex-skill-transfer(Trigger-Clarity 補 reverse-port not-for)、evolve(Actionable-Specificity 把 3/3 收緊條件釘到 Stage 4 real-exec 標籤)、learn / think / write(各 1 個單變量精修,多為原地改寫)。
- **保留 9 skill(收斂)**:book(margin 1.5)、execute(1.5)、design/health/hunt/review(1.0)、ship(0.7)邊際過小;analyze、read 非全票(2/3)。皆未採納、未改動。
- codex 鏡像隨採納重產同步。

## v2.5.5 (2026-06-19)

**每日 cron 自動演化 round 3:全 14 skill 結構軸再精修(standing-auth 自動採納)**。plugin version 2.5.4 → 2.5.5。

由 4:07 AM cron(standing authorization)非互動觸發;全 14 skill 經盲評 **3/3** 自動採納,結構閘 + `make test` 全綠後上 main。本輪無 API 中斷,一次跑完。

### Changed — 變更

- **全 14 skill 結構軸(dims 1–6)第三輪演化**(blind 3/3),各 1 個單變量改動:Failure-Mode-Encoding 補 if-then(analyze 補審查員未完成路徑、codex-skill-transfer 補 mode 誤判路徑)、Stage-Coherence 補 stage 分隔(book)、High-Risk-Action 把 rm -rf 目標後綴釘死(design)等。
- codex 鏡像隨之重產同步。

## v2.5.4 (2026-06-18)

**每日 cron 自動演化 round 2:全 14 skill 結構軸再精修(standing-auth 自動採納)**。plugin version 2.5.3 → 2.5.4。

由 4:07 AM cron(standing authorization)非互動觸發 evolve→codex→ship sweep;全 14 skill 經盲評 **3/3** 自動採納,結構閘 + `make test` 全綠後上 main。

### Changed — 變更

- **全 14 skill 結構軸(dims 1–6)第二輪演化**(blind 3/3):Trigger-Clarity 補 not-for 邊界(analyze/design/execute/hunt/…)、Failure-Mode-Encoding 補 if-then 復原(codex-skill-transfer/think/…)、High-Risk-Action 補 mutation-isolation 不變式(evolve)、Actionable-Specificity 釘死門檻規則(book/…)等,各 1 個單變量改動。
- codex 鏡像隨之重產同步。

### Notes

- hunt/book/think 首輪 mutate 遇暫時性 API 連線中斷掉出,經單獨 retry workflow 補齊,最終 14/14 全數採納。

## v2.5.3 (2026-06-17)

**`/evolve` 非互動 standing-authorization 自動採納 + 全 14 skill 結構軸演化精修**。plugin version 2.5.2 → 2.5.3。

### Added — 新增

1. **standing-authorization 自動採納(Loop/Ultracode 不中途停)**:`/evolve` Stage 6 採納仍是 Authorization PAUSE,但新增與 `/ship` push 一致的 carve-out —— 當 driving context(loop/cron 提示或核准計畫)明確授權採納/整條 evolve→ship 時,非互動執行可自動採納,但僅限通過**全部** Gate-1 前置條件的變更:結構閘通過、盲評門檻收緊為 **3/3**(非互動無人兜底)、保留 file-level snapshot、`log.md` 記 `decision: standing-auth auto-adopt`;任一條件未過即還原、不寫回。`make test` 為下游(/ship)的最終 go/no-go。互動式 session 維持硬停不變;無授權的裸 `/ultracode` 仍硬停 `needs input`。
2. **loop-contract §2 標準授權語意**:Authorization PAUSE 重述為「不得以預設替代滿足;授權可由互動當下給出,或由 driving context 預先記錄的 standing authorization 給出(僅限該 skill 的 `loop-pauses.md` 標記為 standing-authorizable 者)」。standing authorization 屬「預先的明確人類授權」,非 default substitution。

### Changed — 變更

- **全 14 skill 結構軸(dims 1–6)演化精修**(blind panel 3/3 採納):Trigger Clarity 補 not-for 邊界 ×7(book/evolve/learn/read/review/ship/think)、High-Risk Action Discipline 補 rm/git 破壞性守衛 ×4(design/execute/health/hunt)、Actionable Specificity 把未錨定 hedge 改為釘死規則 ×3(analyze/codex-skill-transfer/write)。
- `evolve/references/{safety-gates,loop-pauses}.md`、`evolve/SKILL.md` Stage 6 + Constraints:同步 standing-authorization 採納語意。

### Notes

- codex 鏡像待 `/codex-skill-transfer` 重產同步。

## v2.5.2 (2026-06-17)

**`/evolve` 升級 ultracode 支援:`assist` → `overlap`,並補齊 loop 支援行為**。plugin version 2.5.1 → 2.5.2。

### Added — 新增

1. **`/evolve` ultracode=overlap 雙模 orchestration interface**:新增 `evolve/references/orchestration-interface.md`,為 Stage 5 三盲評委定義雙 adapter(現行平行 Task ↔ thin Workflow),回傳同構 `{better, strict_improvement, per_dimension_deltas}` 投票;Stage 5 計票與 Stage 6 keep/restore 不感知模式。depth 不變句逐 adapter 重述(評委與 diagnostician 為 depth-1 leaf,不呼叫 skill、不再派子代)。SKILL.md 新增 ≤10 行 pointer 區塊與 Stage 0 mode pinning 指引。
2. **`/evolve` loop 支援行為**:新增 `/evolve` 的 PAUSE 分類 —— Stage 0.4 無 benchmark 為 Input PAUSE(預設走 structure-axis-only),Stage 6 採納寫回為 **Authorization PAUSE**(硬停、回報 `needs input`、絕不自動寫回)。評級由 `assist/assisted` 改為 `overlap/drivable`(與 /review 同型:採納硬停與 drivability 並存)。

### Changed — 變更

- **`loop-contract.md §4` 重構為 per-skill registry(locality)**:各 skill 的 PAUSE 分類表自 `_shared/loop-contract.md` 搬到各自的 `references/loop-pauses.md`(review/execute/learn/ship/evolve/think),§4 改為指向各檔的 registry;§1–§3(vocabulary、PAUSE semantics、hard stops)仍共用。改一個 skill 的互動點只動該 skill 的檔,不再動共用檔。
- `tests/skills/test-automation-annotation.sh`:evolve 重評級為 `overlap/drivable`。
- `tests/skills/test-orchestration-interface.sh`:測試迴圈加入 evolve(T1–T4 全綠)。

### Notes

- codex 鏡像待 `/codex-skill-transfer` 重產同步(orchestration-interface、loop-contract、SKILL.md 與版本號)。

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
