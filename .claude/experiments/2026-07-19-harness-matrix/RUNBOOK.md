# RUNBOOK — 跨機重跑手冊與方法論（harness×model 矩陣實驗）

> 目的：任何一台新機器、新 session，讀完本檔即可（1）重新認知整條改革線、（2）用同一套方法
> 對下一個目標系統重跑實驗。下輪目標已定調：大型複雜系統。

---

## 0. 重新認知入口（新 session 先讀，順序固定）

1. `baransu/.claude/feature/harness-reform.md` — 改革線活文件（起因/兩輪判決/當前階段/目標）
2. 本目錄 `04-final-report.md`（第一輪判決全文）＋ `01-run-log.md`（時間/token/成本總帳）
3. `06-reform-spec.md`（R1–R9 改革條款逐字稿——下輪實驗 arm 的 prompt 直接引用它）
4. `baransu/.claude/feature/phase1-restructure-plan.md`（Phase 1 版圖重組計畫，/review 審查中）
5. 記憶錨點：`~/.claude/projects/-home-vakarve-project-clis-baransu/memory/harness-matrix-experiment-findings.md`
   （新機器無本地記憶時，讀 repo 鏡像 `baransu/.claude/feature/memory-mirror/` 並可據以重建本地 memory）

## 1. 環境拓撲（本輪實況，跨機需自行對應）

| 東西 | 位置 | 備註 |
|------|------|------|
| baransu（plugin 本體＋實驗檔案庫） | `~/project/clis/baransu` | remote: github.com/TLOGBen/baransu |
| 實驗場（第一輪） | `~/project/others/NovelReader` | Rust CLI；優勝分支 `origin/legado-parity-p3f` |
| legado 3.0 參照 | `~/project/others/legado` | 官方 repo 已清空，抓的是 fork |
| workflow 腳本正本 | 本目錄 `workflows/` | 6 支，見 §3 |
| 三冊 book | `baransu/.claude/book/*.html` | 自含式，tokens 已 inline |

新機初始化：clone baransu → `make test` 綠（驗證 python3/pytest 在位）→ 安裝 plugin
（`/plugin marketplace add <repo>` + `/plugin install baransu@baransu`）→ 若要重 render book，
先 `/baransu:design preset 紙`（book 紅線要求 project root 有 tokens.css）；validate 用
`bun run .../book/scripts/validate-output.ts`（npx tsx 缺 cheerio，必踩）。

## 2. 實驗方法論（可整套移植到下一個目標系統）

### 2.1 設計原則（每條都是本輪實際執行過的）

- **事前可證偽預測**：跑之前寫下每 arm 的預測與判準（`00-apriori-predictions.md`、`07-validation-predictions.md`），跑完逐條結算——防事後合理化。
- **同一份簡報**：所有 arm 收到 byte-identical 的 `EXPERIMENT-BRIEF.md`（正本在 `winner-spec/`），內含工作項驗收條件、全域約束、決策日誌協定。
- **每 arm 獨立 worktree + branch**：`.claude/worktrees/exp-{arm}`、branch `exp/{arm}`；基線 commit 統一釘死（本輪 bfa0f46）。
- **決策日誌協定**：每 arm 必寫 `.exp/decision-log.md`——所有決策、spec 缺口、被迫選擇。這是理解「組合讓模型怎樣思考」的原始資料（`decision-logs/` 1,180 行）。
- **循序執行、一次一個 workflow**：主迴圈閒置時 `budget.spent()` 差值 ≈ 該 arm token 成本（記憶體慣例：sequential workflows, lean agents）。
- **盲評去識別化**：`git archive <branch> | tar -x` 到中立目錄，剔除 `.exp/`、`.claude/`、`CONTRACT.md`、`EXPERIMENT-BRIEF.md`、`.gitignore`；`cp -al` 硬連結 `target/` 省編譯；代號 ARM-N；映射表評審不可見（`02-blind-mapping.md`）。
- **盲評四維**：驗收條文釘死/未釘/部分/未達 ＋ bug 獵捕（對抗探針）＋ 架構遵循 0-10 ＋ 測試有效率 0-10（≥3 個突變殺/存活）。信任測試數前先強制 rebuild。
- **成本換算**：從 task output 檔以 regex `"type":\s*"workflow_agent".*?"model":\s*"([^"]+)".*?"tokens":\s*(\d+)`（re.S）抽 per-agent model×tokens；牌價 output/MTok：fable $50、opus $25、sonnet 促銷 $10（至 2026-08-31，正式 $15）。只計 output＝下限估算，跨 arm 方法一致即可相對比較。

### 2.2 執行順序（一輪的完整迴圈）

1. 選目標系統、定基線 commit、研究缺口 → 挑 3 個工作項寫進 brief（含可斷言驗收條件）
2. 寫事前預測（可證偽、含判準）
3. 每 arm：開 worktree → 複製 brief → 啟動對應 workflow（§3）→ 等完成 → 記 run-log（時間/tokens/agents）
4. 全 arm 完成 → 去識別化 → 盲評 workflow → 解盲 → 判決 JSON + 最終報告
5. 成本結算 → 事前預測結算 → 歸檔到 baransu `.claude/experiments/<date>-<name>/`

## 3. Workflow 腳本清單（正本在 `workflows/`）

| 腳本 | 用途 | 適用 arm |
|------|------|----------|
| `exp-arm-chain-*.js` | 通用循序鏈：steps 陣列逐個 agent 執行（單體/雙段 arm） | p1-f、p1-o、p2-* |
| `exp-arm-combo-*.js` | 腳本代派工：lead 出結構化派工單（schema）→ 腳本生 worker → lead 整合 | p1-os、p1-fos |
| `exp-arm-execute-*.js` | 全套管線 v1：spec → 逐 task impl/review 迴圈（TIER_SCHEMA）→ final（FINAL_SCHEMA） | p3-*（第一輪） |
| `exp-arm-execute-v2-*.js` | 全套管線 v2（R1–R9 改革版，plain agents） | p3-os′ |
| `exp-blind-judging-*.js` | 盲評 v1（第一輪 10 arm 分批） | 第一輪 |
| `exp-blind-judging-v2-*.js` | 盲評 v2（3 arm 平行，驗證輪） | ARM-11/12/13 |

p-min 不用腳本：三步手動派 agent（opus 一頁合約 35 行 → sonnet 實作 → opus 冷腦 seal）。

### 3.1 Workflow 已知坑（每個都實際踩過）

- **`args` 可能以 JSON 字串抵達**：每支腳本開頭都要 `const A = typeof args === 'string' ? JSON.parse(args) : args`。
- **workflow 巢狀 agent 不能再生 subagent**（無 Agent 工具）：需要委派的組合改用「腳本代派工」模式（combo 腳本）。
- **`Date.now()` / `Math.random()` / 無參數 `new Date()` 在腳本內會 throw**（resume 相容）：時間戳事後蓋或走 args 傳入。
- **重啟前先 TaskStop 舊 run**；resume 用 `{scriptPath, resumeFromRunId}`，未變更前綴的 agent() 走快取。
- **判空結果先讀 transcript 的 journal.jsonl**，不要假設快取非空。

### 3.2 環境已知坑（非 workflow）

- zsh 不做字串分詞：`$batch` 迴圈會靜默失敗，寫明確的 per-arm 迴圈。
- auto-mode 分類器會擋複合 git 指令（branch/push/reset 串接）：拆成單指令。
- `git reset --hard` 會連未提交的使用者編輯一起消滅：動主分支前先 `git status` 盤點。
- execute worktree 永遠在 `.claude/worktrees/`，絕不可放 `.git/worktrees/`（git 內部 metadata，會永久髒）。
- 實驗記錄若只在分支上，working tree 還原用 `git archive <branch> <path> | tar -x`。

## 4. 下一輪（Phase 2：大型複雜系統）需要沿用/新造的東西

**直接沿用**：盲評基建（去識別化流程＋四維判準＋突變抽查）、事前預測紀律、決策日誌協定、
成本抽取法、循序執行慣例、R1–R9 條款文本（arm prompt 引用 `06-reform-spec.md`）。

**需新造**：跨系統簡報（雙 repo 同改 wire format 的 E2E 情境）、「分形合約＋邊界所有人」
的合約模板（頂層合約鎖介面常數，各系統子合約各鎖表面；共享常數升格為 checked-in 工件）、
跨系統盲評判準（介面相容性維度）。

**對打組合（草案）**：分形合約＋seal×2（每系統一次）vs 改革版全套管線×2 vs 裸跑×2。
權重沿用：實現內容最多＆bug 最少 > 時間 > token。
