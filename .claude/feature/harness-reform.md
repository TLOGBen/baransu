# Harness 改革線 — 活文件（單一事實源）

> 維護章程：每次階段轉換、每場實驗結束、每月遙測回看後更新本檔。
> 「當前階段」段落永遠反映最新狀態；歷史只增不改。
> 最後更新：2026-07-19（Phase 1 計畫送 /review 複審中）

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
**完整資料**：NovelReader repo `origin/legado-parity-p3f` 分支
`.claude/experiments/2026-07-19-harness-matrix/`（00–10 號文件＋決策日誌 1,180 行＋diffs＋判決 JSON）。
**三冊 book**：baransu `.claude/book/`（harness-model-matrix-experiment / contract-seal-reform / validation-verdict-plain）。

### 第一輪（10 arm 矩陣）判決

- 冠軍 p3-f（Fable 全套）20 釘死/0 bug/$32.64；亞軍 p3-fos；**墊底 p3-os**（17 釘、全場唯一 HIGH、$11.84）
  輸給 $4.92 的 Opus 裸跑（p1-o，第 4 名）。
- idx+1 章數陷阱抓到 5/10 arm（含 p1-f Fable 單體——自盲實證）；「节」常數轉抄缺陷（p3-os）。
- 核心發現：**品質槓桿是驗收條文的可斷言性，不是流程重量**。p3-fos vs p3-os 同儀式不同結局，
  差異只在條文釘死程度。p2-f 證明同心智自寫自用規格＝同源盲點複製（$16.45 輸給裸跑）。
- 三條路模型：單體全責／前饋設計（警語式 vs 表面設計式）／有牙的反饋環。
- pipeline 淨值公式：審查牙齒（條文可測性×打槍權限）−換手損耗（次數×衰減）。

### 驗證輪（3 arm，R1–R9 改革條款）判決

- **p3-os′（改革全套）：20/20 全釘、0 bug、突變 6/6 全殺、arch 9.5、$19.29**——原墊底翻身
  追平冠軍、test_eff 反超、成本 59%。改革成功判準達成（事前預測完全命中）。
- **p-min（無 skill：35 行合約＋Sonnet 實作＋單次 seal）：行為面 20/20、0 bug、$7.27（22%）**
  ——seal 突變抽查當場抓到未釘表面並自修。一頁紙路線實測成立，殘餘缺口＝呼叫點耦合釘死深度。
- p2-os′（純前饋）：18 釘、0 bug、$5.01——零缺陷但突變殺率 5/8 暴露無審查的深度極限。
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

## 三、當前階段

**Phase 1 — 版圖重組落地（進行中）**

- /think Full mode 已跑完（對焦：觸發體驗優先／上限可鬆綁＋可大拆／成功＝觸發正確率可觀測）。
- 五節計畫草稿：baransu `.claude/think/skill-restructure-phase1-draft.md`。
  核心：新增 `/contract` `/seal` 獨立微型 skill＋analyze/execute 合併為單一大頻段管線（保留
  /analyze 名）＋上限 14→15 小幅修憲（不退役 codex-skill-transfer——實查 28 專屬測試非弱持有）＋
  R1 文本進 _shared 單一實作＋分段落地（雙釘→合併→憲法→版本 3.0.0，每段 make test 全綠）。
- **狀態：Stage G 選項 1——計畫已送 /review，architecture + quality 兩視角審查員執行中**；
  審後回 Stage G 閘由使用者裁決。dispatcher==author 規則生效（相牴 findings 不得自降級）。

## 四、之後階段

| 階段 | 內容 | 觸發條件 |
|------|------|----------|
| Phase 1（本階段） | 版圖重組手術＋seal-guard hook 範本（opt-in）＋遙測慣例落 _shared | /review 過＋Stage G 批准 |
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
| Phase 1 計畫草稿 | baransu `.claude/feature/phase1-restructure-plan.md` |
| 優勝程式碼（第一輪 p3-f） | NovelReader `origin/legado-parity-p3f` 分支（等與 origin/main 新進展 reconcile） |
| 記憶錨點 | `~/.claude/projects/-home-vakarve-project-clis-baransu/memory/harness-matrix-experiment-findings.md` |

## 七、未結事項（非本線但實驗發現）

- NovelReader `reader.rs` idx-vs-position pre-existing 缺陷：三位盲評兩輪共六次標記，換源進度
  功能會放大觸發率——NovelReader backlog 首位。
- 第一輪優勝成果（項目 A/C 遠端仍缺、項目 B 比對器可接 target_idx 縫）待與使用者活躍開發的
  origin/main reconcile——分支保存於 origin/legado-parity-p3f。
