# Harness 改革線 — 活文件（單一事實源）

> 維護章程：每次階段轉換、每場實驗結束、每月遙測回看後更新本檔。
> 「當前階段」段落永遠反映最新狀態；歷史只增不改。
> 最後更新：2026-07-19 深夜（Phase 1 完結 v3.0.0→v3.0.1；等待 Phase 2 ／ 月回看 2026-08-19）

---

## 一、起因緣由

模型能力逐代增強，baransu 為過去較弱模型所建的 harness（流程鷹架）理論上應該越來越輕。
使用者主力模型為 Opus 4.8 + Sonnet 5（另有 gpt-5.6-sol，Anthropic 環境內不可呼叫）。
原始信念：大型複雜開發必須走 analyze + execute 全套。原始疑問（2026-07-19 提出）：

> Fable 原生 vs Opus+Sonnet 原生 vs 三模型原生 vs 三者只用 analyze vs 三者用 analyze+execute，
> 對大型複雜任務的開發究竟差在哪裡？

衍生核心問題：兩個 skill 還需要嗎？全部？部分？哪些內容已不用提醒模型、哪些還要？
主力組合缺了 p3-f 的哪些行為/理念/模型慣性？

## 二、完整實驗記錄（兩輪，已完結）

**實驗場**：NovelReader（Rust 終端小說閱讀器，legado 3.0 CLI port）。
**題目**：同一份三工作項簡報（A: rule DSL `&` bug／B: 換源進度遷移／C: 搜尋結果摺疊），
基線 bfa0f46，獨立 worktree，Fable 盲評（四維：釘死條數/bug/架構/測試有效率＋突變抽查）。
**完整資料（正本）**：baransu `.claude/experiments/2026-07-19-harness-matrix/`（00–10 號文件＋決策日誌
1,180 行＋diffs＋判決 JSON＋RUNBOOK＋workflows；NovelReader `origin/legado-parity-p3f` 留歷史快照）。
**三冊 book**：baransu `.claude/book/`（harness-model-matrix-experiment / contract-seal-reform / validation-verdict-plain）。

### 第一輪（10 arm 矩陣）判決

- 冠軍 p3-f（Fable 全套）20 釘死/0 引入 med·high/$32.64；亞軍 p3-fos；**墊底 p3-os**（17 釘、全場唯一 HIGH、$11.84）
  輸給 $4.92 的 Opus 裸跑（p1-o，第 4 名）。
- idx+1 章數陷阱抓到 5/10 arm（含 p1-f Fable 單體——自盲實證）；「节」常數轉抄缺陷（p3-os）。
- 核心發現：**品質槓桿是驗收條文的可斷言性，不是流程重量**。p3-fos vs p3-os 同儀式不同結局，
  差異只在條文釘死程度。p2-f 證明同心智自寫自用規格＝同源盲點複製（$16.45 輸給裸跑）。
- 三條路模型：單體全責／前饋設計（警語式 vs 表面設計式）／有牙的反饋環。
- pipeline 淨值公式：審查牙齒（條文可測性×打槍權限）−換手損耗（次數×衰減）。

### 驗證輪（3 arm，R1–R9 改革條款）判決

- **p3-os′（改革全套）：20/20 全釘、0 引入 med·high、突變 6/6 全殺、arch 9.5、$19.29**——原墊底翻身
  追平冠軍、test_eff 反超、成本 59%。改革成功判準達成（事前預測完全命中）。
- **p-min（無 skill：35 行合約＋Sonnet 實作＋單次 seal）：行為面 20/20、0 引入 med·high、$7.27（22%）**
  ——seal 突變抽查當場抓到未釘表面並自修。一頁紙路線實測成立，殘餘缺口＝呼叫點耦合釘死深度。
- p2-os′（純前饋）：18 釘、0 引入 med·high、$5.01——零缺陷但突變殺率 5/8 暴露無審查的深度極限。
- **類別滅絕證據**：idx+1 與常數轉抄兩類缺陷在驗證輪零出現（結構性消滅，非機率壓低）。
- 改革條款全文：實驗目錄 06-reform-spec.md（R1 條文可斷言性閘門／R2 陷阱昇華／R3 常數塊／
  R4 表面清單／R5 儀式裁減／R6 審查任務書／R7 鬆條文升級／R8 執行裁減／R9 final 補強）。

### 理論產出（對談沉澱，見第二冊 book）

- skill 三種假肢解剖：知識（已內化→蒸發）／流程（零效果→退役）／注意力（殘餘本體→微型化）。
- 觸發形式光譜：CLAUDE.md（常駐不變量）／hook（機械時機）／skill（語意時機＋具名詞彙）／模型自主。
- 尺度外推：跨系統＝分形合約＋邊界所有人＋常數升格共享工件；SA 文件情境＝ingestion 翻譯階段，
  「宣稱完成」→「提交證據包」。
- 選用穩健性：不追求選得準，追求選錯便宜＋選漏可偵測（seal-guard hook 設計已完成，見對談）。
- 混用代數：規格層×審查層各挑一個尺寸；同層雙容器＝雙真相源（禁）；審查堆疊＝責任稀釋+1（禁）。

## 二b、Phase 1 落地記錄（2026-07-19，已完結）

**決策鏈**：/think Full mode 對焦 → 五節計畫 → /review（兩席＋對抗輪：F1 分段自鎖／F2 量測循環／
F3 機件去留／F5「0 bug」hard-stop 等 4+4+1）→ 使用者四裁定全採推薦 → 修訂版 v2 即 Stage G 批准。
過程中使用者三次即時再裁定，逐步激進化：hook 範本 → 直接隨 plugin 出貨 → **預設阻擋模式**；
遙測 log 由 per-project 散落改為**集中 user scope**（v3.0.1）。

**三段 count-neutral 手術**（branch `feat/phase1-restructure`，fork 執行者＋主迴圈每段獨立複驗）：
- `93d775f` 段①：execute 併入 analyze（R8 裁剪文本降 `references/execution-pipeline.md`，body 455 行）
  ＋/contract＋`_shared/contract-gate.md` 單一實作＋Gates 10/11 錨同段遷移——14 進 14 出全綠。
- `6c094dd` 段②：/seal（五點任務書＋直接修正權＋target-pin off-ramp）＋修憲 14→15
  （verify-skills×3＋CLAUDE.md×2 含 falsifiable 條款＋README×2＋測試×2）——15 對 15 全綠。
- `edc67cf` 段③：v3.0.0＋三頻段路由表＋CHANGELOG breaking（/execute 移除）＋seal-guard hook
  出貨即生效（`stop_hook_active` 防迴圈、`SEAL_GUARD=log|off` 降級、任何模式落 jsonl）
  ＋`_shared/selection-telemetry.md`＋listing 8007→6857。

**品質鏈 dogfood**：/seal 五點跑在全 branch diff 上——雙突變抽查真做（刪 /seal 表列→測試叫；
破壞防迴圈→測試叫）。最終 /review 兩席（98 檔 deep）：**兩席獨立收斂 seal-log 生產端懸空**
（hook/測試/文件三方都預期 /seal 寫證據檔，唯獨 SKILL.md 沒這條指令——不修則合規使用者收工必被
誤擋、污染月回看數據）＋Phase 3 懸空錨×8＋⚠️ 路徑漏歸零 compile 計數＋AGENTS.md fourteen 殘留
＋5 advisory；全數直修於 `68df868`（含 G9/G10 補測試釘死）。merge `70b1438` → main，全綠 push。

**v3.0.1 補丁**（`a07da46`）：遙測帳本集中 `~/.claude/baransu/telemetry/{專案}/{類型}-{YYYY-MM}.jsonl`
——專案切分（git-root basename，無 git 取資料夾名）、月切檔即輪替、回收＝讀一個目錄、
`BARANSU_TELEMETRY_DIR` 測試覆蓋。user-scope 規則檔 `~/.claude/rules/common/baransu-telemetry.md` 同步。

**過程教訓（值得留給 Phase 2）**：
1. T5 守護段對 HEAD 零 diff 的設計實地驗證——審查修正落地時先紅（未提交的守護段改動）、commit 即綠，「守護段改動必須經審查」的機制語意成立。
2. make mirror 會洗掉直接寫進鏡像的內容——分發面差異必須寫進單一來源隨 mirror 出貨（Distribution note 事件）。
3. zsh 空 glob（nomatch）第二次咬人（/ship 歸檔迴圈）——與 RUNBOOK 已知坑同族，shell 迴圈一律改 python。
4. 兩位獨立審查員對同一結構缺口收斂（seal-log 生產端）＝「consumer 齊備、producer 缺席」是合成系統的高發縫型，Phase 2 跨系統實驗直接把它列為檢查面。

## 三、當前階段

**Phase 1 已完結（v3.0.1 在 origin/main）——目前處於遙測累積期**

- 落地全程見 §二b。使用者側下一動作：`git pull` ＋ 重裝 plugin 吃 3.0.1。
- 遙測累積中：起算 2026-07-19，帳本在 `~/.claude/baransu/telemetry/`；月回看 2026-08-19 前後
  （三個決策：雙釘假設驗證／seal-guard 阻擋去留／codex-skill-transfer 退役條款）。
- Phase 2（大型複雜系統實驗）擇期開跑——方法論與腳本備妥於 RUNBOOK。

## 四、之後階段

| 階段 | 內容 | 觸發條件 |
|------|------|----------|
| ~~Phase 1~~（✅ 2026-07-19 完成） | 版圖重組手術＋seal-guard hook 出貨即生效（預設阻擋，SEAL_GUARD 可降級）＋遙測慣例落 _shared | /review 過＋Stage G 批准 |
| Phase 2 | 大頻段實驗：拿**大型複雜系統**開刀（使用者已定調；候選形態＝跨雙系統同改 wire format 的 E2E 情境），「分形合約＋邊界所有人」對打「改革版全套」；復用盲評基建與事前預測紀律 | Phase 1 落地後擇期 |
| Phase 3 | 遙測月回看：skill 選用誤觸發／漏觸發率、codex-skill-transfer 使用率（三個月零使用則退役回 14）、seal-guard 是否轉預設 | 落地滿一個月 |

## 五、所有目標（判準錨定）

1. **觸發正確率可觀測**（Phase 1 成功判準）：選用決策進決策日誌遙測，月回看有帳可查。
2. **兩類缺陷維持絕種**：idx+1 型、常數轉抄型在真實使用中不再出現（seal 突變抽查為偵測面）。
3. **三頻段路由證據補完**：小（既有共識）／中（本輪定讞）／大（Phase 2 補判）。
4. **baransu 轉型軌跡**：從「執行編排器」走向「慣例＋驗證器」——skill 縮為注意力假肢，
   機械閘（verify-skills、validate-output）原地保留並持續強化。
5. **成本紀律**：中頻段日常任務的品質保險成本 ≤ 任務本體的 30%（p-min 實測錨：$7.27 vs 裸跑 $5）。

## 六、關鍵檔案索引

| 內容 | 位置 |
|------|------|
| 實驗全記錄（兩輪，正本） | baransu `.claude/experiments/2026-07-19-harness-matrix/`（00–10 號文件＋decision-logs＋diffs＋winner-spec；NovelReader `origin/legado-parity-p3f` 分支留歷史快照） |
| 改革條款 R1–R9 | 同上 `06-reform-spec.md` |
| 三冊 book | baransu `.claude/book/{harness-model-matrix-experiment,contract-seal-reform,validation-verdict-plain}.html` |
| Phase 1 批准版計畫（v2＋阻擋修正案） | baransu `.claude/feature/phase1-restructure-plan.md` |
| 跨機重跑手冊（方法論＋workflow 腳本＋已知坑） | baransu `.claude/experiments/2026-07-19-harness-matrix/RUNBOOK.md` ＋ `workflows/`（6 支腳本正本） |
| 記憶鏡像（機器本地 memory 的 repo 副本） | baransu `.claude/feature/memory-mirror/`（正本在各機 `~/.claude/projects/.../memory/`；每次 ship 時同步） |
| 優勝程式碼（第一輪 p3-f） | NovelReader `origin/legado-parity-p3f` 分支（等與 origin/main 新進展 reconcile） |
| /review 日誌（計畫審＋終審） | baransu `.claude/archived/2026-07-19-phase1-{restructure-plan,final-diff}.html`（/ship 歸檔，local） |
| 記憶錨點 | `~/.claude/projects/-home-vakarve-project-clis-baransu/memory/harness-matrix-experiment-findings.md` |

## 七、未結事項（非本線但實驗發現）

- NovelReader `reader.rs` idx-vs-position pre-existing 缺陷：三位盲評兩輪共六次標記，換源進度
  功能會放大觸發率——NovelReader backlog 首位。
- 第一輪優勝成果（項目 A/C 遠端仍缺、項目 B 比對器可接 target_idx 縫）待與使用者活躍開發的
  origin/main reconcile——分支保存於 origin/legado-parity-p3f。
