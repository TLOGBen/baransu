# baransu Phase 1 版圖重組計畫（修訂版 v2 — /review 發現全數折入，Stage G 已批准）

對焦結論:目的＝觸發體驗優先／約束＝上限可鬆綁＋可大拆／成功＝觸發正確率可觀測（決策日誌遙測、一個月回看）。
審查記錄:`.claude/review/2026-07-19-phase1-restructure-plan.html`（arch+quality 兩席＋對抗輪；F1–F8 修訂已全數寫入本版）。

## Building（要做什麼）

落地後的可觀察成果：使用者輸入 `/baransu:contract` 得到一頁合約流程（四節：目標／可斷言條文／錯不起表面／照抄常數）；輸入 `/baransu:seal` 得到單次窄域審查（五行任務書＋直接修正權；需含 target-pin off-ramp——無可審 diff 時停下報告，不憑空造靶）；輸入 `/baransu:analyze` 直通大頻段管線（R1–R9 改革版規格→逐 task 實作審查→final 常數比對，**原 execute 流程經 R8 裁剪後內含**，中途 PAUSE 閘保留）；`/baransu:execute` 這個名字消失，其觸發詞由 analyze 承接，**CHANGELOG 3.0.0 標 breaking change 並指引改用 `/baransu:analyze`**；`make test` 全綠、上限錨改 15（實為三處：verify-skills 常數＋docstring＋CLAUDE.md ceiling 句）、CLAUDE.md 換三頻段路由表、版本 bump 3.0.0。

**合併的能力去留清單（F3 定案）**——R8 只裁實驗判死的儀式：summarize-agent、逐 task ctx 檔、Red gate 降 advisory、重試上限降 1。以下四組機件**全數保留**（各有 CLAUDE.md 不變量或實體對應，且未被實驗判死）：worktree 平行組（承載 no-git 一路降級與 `.claude/worktrees/` 不變量）、三振計數（`failure_count` 排除 compile error）、coverage-riding 的 `test_weight` 派發、merge-agent／e2e-fix-agent／final-fixer 三收尾 agent。

**合併爆炸半徑（F6 補列，不只 910 行 SKILL.md）**：execute 家族 8 個 agent 提示檔的流程引用、`execute/references/` 三檔歸屬（Gate 11 `GREEN_PROOF_FILES` 硬編碼路徑）、loop-pauses 註冊表的 execute 列、CLAUDE.md 四條以 execute 具名的 Non-obvious Invariants 改寫。

**合併產物結構（F7 定案）**：execute 流程文本降入 analyze 的 `references/`，SKILL.md body 維持 500 行 advisory 上限內——body 只留路由與閘門。

## Not building（明確不做的事）

- 不退役 codex-skill-transfer：實查 28 條專屬測試（verified: `grep -c "def test_" tests/scripts/test_codex_skill_transfer.py` → 「28」），非弱持有，退役無證據支撐
- ~~不建阻擋模式預設~~（2026-07-19 使用者再裁定覆蓋 F2 原案）：seal-guard **隨 plugin 出貨、安裝即生效、預設阻擋**（`stop_hook_active` 防迴圈；`SEAL_GUARD=log|off` 降級；任何模式都落 jsonl 遙測）。falsifiable：月回看誤擋率過高即降回 log 預設
- 不在本段跑 Phase 2 雙系統實驗：大頻段合併管線的實戰品質留給下一場獨立實驗
- 不動 review／hunt／think 等其餘 skill 的本體：只加易混淆交叉列
- 不建自動遙測分析管線：選用決策記錄先落決策日誌慣例，人工月回看

## Approach（選了哪個方案及理由）

Stage B 方案 2 修訂版：雙釘獨立（觸發體驗優先的直接結論——「名字即觸發器」係由對焦目的推導 (inferred: 實驗未含觸發表現對照格，其驗證落在本計畫自身的遙測判準上)；實驗結論 skill 殘餘本體＝注意力假肢 (verified: 08-reform-article)）＋雙塔合一（**實驗判死的是交接工件——ctx 檔／summarize／常數轉抄鏈，且驗證輪冠軍組態 p3-os′ 本來就是單一連續管線；合併是把已驗證形態搬回 baransu**）＋上限 14→15（合併回收一格後僅需一格，修憲幅度最小）。不選最小方案（全併入為模式）因觸發詞彙弱化牴觸目的；不選 16 格方案因保留死縫且修憲幅度加倍。已接受邊界：合併後大頻段品質未經實驗驗證（Phase 2 承擔）；execute 名字消失的習慣斷裂由 description 關鍵詞＋CHANGELOG breaking-change 指引緩解。

實驗證據錨:驗證輪 p3-os′（R1–R9 全套）20/20 全釘、**0 引入 med/high**、突變 6/6 全殺、$19.29（冠軍 59% 成本）；p-min（一頁合約＋單 seal）行為面 20/20、**0 引入 med/high**、$7.27。記錄正本於 baransu `.claude/experiments/2026-07-19-harness-matrix/`（01 run-log、09 validation-verdicts）。

## Key decisions（關鍵決策）

1. **上限 14→15 而非退役 codex**：證據不支持退役（28 條專屬測試、CHANGELOG 提及 86 次；使用率 inferred: 未實查）；修憲附 falsifiable 條款——遙測若證實其三個月零使用即退役回 14。取捨：以裁換建剛性讓渡一格，換不誤殺活資產。
2. **合併保留 /analyze 名字**：沿用觸發習慣與 analyze 側文件錨點，不造新名；execute 側錨點（agents 引用、references 歸屬、CLAUDE.md 不變量）按爆炸半徑清單逐項遷移。取捨：名字語意（analyze≠執行）略有擴張，靠 description 首句補正。
3. **R1 條文閘門文本放 _shared 單一實作**：contract 與 analyze 兩處引用同一份，防雙真相源。
4. **分段落地採 count-neutral 重切（F1 定案）**：①合併＋第一釘（/contract）＋Gates 10/11 錨點同段遷移——skill 數 14 進 14 出，常數不動，make test 全綠；②第二釘（/seal）＋修憲 14→15（三處錨同段改）——15 對 15 全綠；③版本 3.0.0＋三頻段路由表＋CHANGELOG＋純文件錨。每段 make test 全綠為闖關條件，任一段失敗不進下段。**落地走 feature branch + PR**（平行 session 活躍於 main，實測有碰撞風險）。
5. **遙測即決策日誌，機制錨＝seal-guard hook（出貨即生效，預設阻擋——2026-07-19 使用者再裁定）**：skill 選用決策記一筆進 _shared 慣例；「該用未用」由 hook 落日誌補洞——量測循環依賴解除，符合「無錨條款不得入冊」。一個月後回看誤觸發／漏觸發率——成功判準落地。

## Unknowns（已知不知道的事）

- 大頻段合併管線的實戰品質：Phase 2 大型複雜系統實驗判定；owner＝下一場實驗
- codex-skill-transfer 真實使用率：遙測三個月；owner＝月回看
- seal-guard 預設阻擋是否需降回「僅記錄」：視誤擋率；owner＝月回看
- 舊 `/analyze` spec／顯式 `/baransu:execute` 呼叫的殘留工作流如何導向合併後入口：需 3.0.0 實際發布後觀察；owner＝月回看

## 附:Stage E 攻擊角度（已折入對策）

①910 行合併手術風險→count-neutral 分段＋每段 make test＋references 降置；②execute 觸發習慣斷裂→description 承接觸發詞＋CHANGELOG breaking-change；③contract/think/analyze 三向誤觸發→易混淆表劃界＋遙測；④seal 漏觸發→seal-guard hook 出貨即生效（預設阻擋，SEAL_GUARD 可降級）；⑤Gates 10/11 錨點與手術同段遷移（審查修正：它們本身是手術對象，非現成安全網）。規模旗標:中大型（約 14+ 檔案、零新服務、零新依賴）。
