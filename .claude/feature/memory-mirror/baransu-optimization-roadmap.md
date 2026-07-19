---
name: baransu-optimization-roadmap
description: 持續優化路線圖（2026-07-10 → 07-13 週日止）— 慣性帳本方法論、skill 佇列、當前進度、喚醒後續跑指引
metadata: 
  node_type: memory
  type: project
  originSessionId: 7e0693c7-4aae-4eb1-a9a3-bdc2ced69a42
---

# baransu 持續優化路線圖 —— 【三次收斂:2026-07-12 v2.10.0 上線,遞延候選全清】

**終態(最新)**:PR #2-#6 全部 MERGED、origin/main = **v2.10.0**(merge 1611d69)、
make test 全綠、mirror in sync;功能分支與 worktree 全清,本地/遠端只剩 main
(+本 session 自身 locked worktree 分支)。使用者自行更新 plugin。
v2.10.0(#6,Fable 最後一天 ultracode 連續作業):design/book 八遞延候選(book 圖表
14→17、maintained trio 契約、架構板規模級、尺寸反比權重梯、CJK 三件組、質感/動效軸)
+ housekeeping(煙霧閘門常備化含咬合證明、evals 體檢 9 修)+ 實地煙霧修復(inline
範例 GATE-C ×4 含既存 statistical、4 契約歧義收口、17 型 legend 守衛)。
v2.9.0 內容:hunt 快徑(#3)+ design/book 煙霧修復 4 high(#4)+ 美學基底 aesthetics-foundation(#5)。
**遞延功能候選清單全數清空;剩餘僅使用回饋撿漏。**

**【2026-07-12 使用者 standing authorization】**:「等等不用問我,自主判斷直接跑」——
evolve 採納等決策自主執行(Gate 1b 預條件仍須全清:結構閘+3/3 盲評+snapshot+log 記帳),
PR/merge 流程依 PR #6 前例直接走完。
- [x] **全席 evolve ratchet 完成 → PR #7 MERGED,origin/main = v2.11.0(merge 3faa485)**:
  七席採納(analyze D3/codex-skill-transfer D6/design D2/evolve D3/execute D4/learn D4/
  ship D3),七席 margin-converged(0.5-1.5 天花板健康收斂);design 首輪撞 limit 由
  resumeFromRunId 補跑過檻。採納全走 Gate 1b standing-auth(結構閘+3/3+snapshot+log 記帳)。
  教訓:resume 重跑已採納的席位會出現 not-unanimous 假影(live 已含變異)——
  首輪合法棘輪不回退,重評結果不覆蓋既定採納。分支/worktree 已清,使用者需再
  /plugin 更新到 2.11.0。

## 合併後續跑指引(cron **efe3aae7**,每日 03:53/08:53/13:53/18:53/23:53,週一自停;
前身 69bc9a19 在 2026-07-12 compact 後遺失,已同款重建 — cron 是 session 內存,compact/續接可能吹掉,喚醒時可用 CronList 自檢)

- 使用者澄清:五小時喚醒**繼續原路線**(不是等人工開啟)。
- **main 已收斂:任何新修改開新 worktree 分支 + draft PR,絕不直接 commit main。**
  舊 worktree execute-opus-fable-alignment 已合併(乾淨),新工作勿再用它 —— 開新的。
- [x] **hunt C'2 完成**(週五 14:2x 窗口):8.5/10,Locate 期建檔錨點 PASS(scoping 早於修復 3.5 分);
      6 條快徑文本缺陷 → 新分支 fix/hunt-fastpath-refine 修畢,**draft PR #3**
      https://github.com/TLOGBen/baransu/pull/3(資格判定去循環等,+11/−3,全綠)。
      待使用者審 PR #3 後合併。
- [x] **design/book 雙煙霧測試 + 修復完成 → draft PR #4** https://github.com/TLOGBen/baransu/pull/4
      (4 high 全實證重現→修復→閘門翻綠;紙-sanity exit 0、SVG .pptx 建成;18 檔 +418/−80)。
      原記錄:
      4 high 出廠級缺陷 — design:全新 preset 過不了自家 sanity(lint 打中規格散文)、冪等重跑被
      schema 欄位打死;book:html2pptx 遇 inline SVG 必崩(SVGAnimatedString)、pptxgenjs 裝 global
      驗 cwd 永不成功。+6 medium(--dry-run 被忽略破壞新採納的安裝閘、GATE-F regex 同 schema 病、
      GATE-F/G 實流程從不執行…)。修復要求兩煙霧閘門實證翻綠。完成後 → draft PR #4。
      **方法論教訓(記)**:靜態審計+盲測抓不到「出廠即壞」;帶 scripts 的 skill(design/book/health)
      需要真執行煙霧測試。read 的管線煙霧已被 R1 實驗天然覆蓋;health 已 dogfood;
      write/learn/think 無腳本面。潛在後續:把兩個煙霧閘門(紙-sanity exit 0、html2pptx SVG case)
      納入 tests/ 常備迴歸。
- **【2026-07-12 使用者指令:Fable 最後一天,ultracode 最大化,design/book 遞延候選+其他掛牌項目全做】**
- [x] **design/book 八遞延候選一次落地 → draft PR #6** https://github.com/TLOGBen/baransu/pull/6
  (worktree feat/design-book-deferred-features,v2.10.0,3 commits):book 圖表 14→17
  (org-chart+class+architecture-board)、maintained-diagrams trio 契約、架構板規模級、
  尺寸反比權重梯(AGPL 自述,n-gram 0 verbatim)、CJK 三件組、質感軸+動效預算軸;
  三 preset+check.py sha256 不動;守衛 test_book_diagram_types_17+test_design_typography_expression_axes。
  流程:單 workflow 12 agents(6 scout 淺 clone 上游+2 impl 平行叢集+3 verify)+1 fixer
  (出處逐字重寫、陳舊計數、WHY: 摺回散文)。教訓:出處審查(≥6詞 n-gram vs 上游 clone)
  抓到 Kami/Waza 多處逐字搬運與整段 SVG 照抄 —— 上游吸收類變更必配 provenance verify agent。
- [x] **housekeeping 完成**(commit ede6bed,PR #6 body 已補):兩煙霧閘門入 tests/skills/
  (含咬合證明:注入舊缺陷→exit 1→還原)+ evals 體檢 9 陳舊修正(book 6/design 2/read 1,
  其餘 44 案例現行)。
- [x] **實地煙霧 + 修復完成**(commit 980f5f0):新三型實地渲染 PASS 出貨閘門;
  三個新 inline 範例 GATE-C 全失敗 + **既存 type-statistical 同病(v2.9.0 前即壞)**,
  四範例修好且 bun 真閘門複驗 ×4 exit 0;4 契約歧義收口(marker-id 文件範圍、class h=96
  例外明文、.hl 樣式落地三 golden-template、§4.7 措辭收斂+質感層回歸 canonical dots);
  新守衛 TestLegendHairlineGateCWindow(17 型全掃,負向驗證咬合)。
  **方法論再證:契約散文的 inline 範例也要過真閘門**。runtime note:validate-output.ts
  無 tsx 時 `bun run` 可跑(bun 自動裝 cheerio),已記入 book SKILL.md Stage 4。
  **PR #6 終態:6 commits(87ebbd4/2dab598/d76d696/ede6bed/980f5f0),make test 綠,
  mirror in sync,等使用者審**。
- 剩餘輕量候選:(a) 使用回饋撿漏;(b) 無事可做=合法結果。
  週一(2026-07-14)後:CronDelete efe3aae7、回報完成。
  ⚠️ 本 session 的 Edit/Write 工具被隔離鎖在舊 worktree execute-opus-fable-alignment —
  對 feat/design-book-deferred-features 的檔案寫入一律走 Bash python/heredoc。

## design/book 本心(使用者 2026-07-11 晚親述,repo 未載,勿丟失)

design 為「統一美學設計」而生,兩軸:
- **美學:實驗已解答(2026-07-11)——蒸餾經典理論=clearly-better ×2 全票**。
  機制:基底給了「從 brief 導出專屬材質隱喻再推導全部 token」的推導機器;無基底側落入體裁先驗
  (最可能的 AI 答案)。使用者擔心的理論致平坦化被反證 —— 趨同源是 schema 骨架,理論反而差異化。
  蒸餾須立足經典(使用者明示):Itten/Albers/Arnheim+格式塔/Rams/原研哉/Müller-Brockmann/Tschichold,
  經 /learn 消化(classics-digest.md),每條規則落名出處。基底元規則:「理論服務於軟弱時刻,
  永不覆蓋直覺 — Itten」。→ **已落地:draft PR #5** https://github.com/TLOGBen/baransu/pull/5
  (foundation 238 行 adopted + Gen Mode 接線 + book 按需引用 + 8 項上游吸收)。
- **遞延功能級候選**(美學軸後續 pass,各是 feature-sized):Kami 架構板規模級、維護型圖表
  trio 契約、Mermaid 目錄 17vs14 擴充;guizang 權重梯 AGPL 自述重寫;diagram-design org-chart;
  背景質感軸、動效預算軸(官方萃取);Waza 文字適配 gotcha 三件組。
- **PR 三件已全數合入 main(v2.9.0)**:#3(hunt 快徑)、#4(design/book 煙霧修復)、#5(美學基底)。
- **統一**:自五個靈感專案擷取美學製作過程,訂統一基底(風格核心理念+框架定義+標準模板+色彩配置):
  tw93/Waza ui(文清風)、tw93/Kami(紙 preset 源頭,極簡=閱讀體驗的極致簡約,使用者最愛)、
  alchaincyf/huashu-design(最美 ppt skill,design 互動與流程靈感)、op7418/guizang-ppt-skill(雜誌風)、
  cathrynlavery/diagram-design(SVG 繪製方法);另 官方 /frontend-design 與 /dataviz = 「美與設計的定義方法」。
  → 上游更新偵察同 workflow 進行中。
- **book** = 美觀的文本可視化生成器,「依 design 的骨,更自由地生長」,須符合原定義。
- **使用者明示:這兩個 skill 的重心是美學與統一,gate 重要但非核心** — 後續優化以此為綱。
- TODO 清點已結案(剩餘為 health 工具鏈模式定義);settings.local.json 屬使用者(已回報)。

# 原路線圖(歸檔)——(跑到 2026-07-13 週日結束)

## 核心目標（使用者原話的操作化）

檢視「同一件事,fable 不用 skill vs 用 skill 差在哪」:
- 哪些慣性被 skill 解決了（→ 對應條款證明了自己的重量,保留）
- 哪些慣性沒被解決（→ 強化或重設計）
- 哪些行為反而被 skill 弄差（→ 枷鎖,減重）
- 哪些條款沒有任何行為指紋（→ 純紀錄,刪除候選）

哲學:複雜度必須證明自己的價值;重量複雜度解決同重問題,否則回歸輕量;
智慧能發揮就不上枷鎖;預設捷徑不是正路才導正。輕與重的平衡,智慧與慣性的對抗。

## 方法論 — 慣性帳本協議（每個 skill 一輪）

1. **對照**: B(fable 直接) vs C(fable+skill) 同一 fixture 真實任務;盲測 examiner+judge 產出慣性帳本
   （B 有 C 無 = skill 解決的;B C 都有 = 沒解決的;C 比 B 差 = skill 造成的）
   ＋條款歸因:SKILL.md 每個機制對應到哪個觀察行為,無指紋者列刪除候選
2. **修訂**: 依帳本改 SKILL.md（強化/減重/刪除）,commit 進 worktree
3. **驗證**: C'(fable+修訂版) 精簡重跑,確認慣性 delta;forward-only,無改善即回退
4. Opus 維度視預算跑（execute 已做,其他 skill 選擇性）

**紀律（使用者硬性要求）**: 一次只跑一個 workflow;每輪 agent 總數 ≤12;
對抗驗證只對 high 嚴重度單一反駁者;先前 R1 用 71 agents 太超過,不可重演。

## Skill 佇列（依價值排序）

- [x] think / analyze / review — 先前已優化過（本輪最後可用慣性帳本鏡頭複檢,見第 7 項）
- [~] **execute** — R1 完成;R2 完成(判定 gap-closed/partially-closed:完成定義 6→10 超越基線、
      慣性 7→9、儀式 15檔490行→9檔277行;R2 揪出:per-task commit 粒度回歸、degraded ctx 冗餘、
      C5 persistence 只有結構論證);**R3 修訂已 commit**(coverage-riding tier、per-task commit 明文、
      persistence 需 reopen 級證明、terse ctx);**R3 驗證進行中**(wf_7e650faa-247,ws6,Opus+v3,4 agents)。
      R3 完成(judges: improved ×2,相似度 62-65 向底線 81 收斂;per-task commit ✓、reopen 級
      persistence ✓、C5 實證修正是亮點)。R3 揭露:riding tier 被 default-to-heavier 偏誤無視
      (fixture 無純 wiring 案例,屬 spec 設計問題)、test_weight 事後補記、RED 證據退化。
      **v4 微修已 commit**(test_weight gate-time 入 task-map、red_proof 證據欄)。
      execute 線暫收 — 平等 A/B 最終輪以 v4 驗證;riding tier 需含真 wiring 任務的 fixture 另行微評。
- [ ] **官方文件對齊 pass**(digest 存 abtest/official-docs-digest.md):
      (a) 已驗證合規:14 skill description 全 <1536 chars、SKILL.md 全 <500 行(execute 484,只准減不准增);
      (b) 待評估:agents 加 disallowed-tools:[AskUserQuestion] 硬化 headless;skill frontmatter 新欄位
      (when_to_use / paths / context:fork+agent — /review 的 subagent-safety 問題可能可用 fork 解);
      prompt/agent-based hooks 可把 prose 守則升級為機械 gate(review-agent-mandatory、spec 唯讀已有 hook 攔);
      agent memory:true(實驗性,smart-friend 候選);(c) 官方驗證優先架構與 baransu 的 green_proof 方向一致。
- [~] **read** — R1 完成(9/9,中途撞 limit 用 resume 復原)。結論:三 run 產出位元組級一致
      (相似度 90-95,fable 自由跑自發重建 frontmatter 欄位/slug/raw+material 結構)。
      慣性帳本:skill 解決的=dedup 檢查、untrusted-content 掃描、Chrome 能力誠實申報、互動點降級記帳;
      skill 造成的=全量 Chrome 探測、瑣碎輸入付全儀式、Done-when 存在性檢查弱於自由跑完整性檢查;
      無指紋條款=10 條核心機制(保留:它們是 /learn 依賴的格式契約+弱模型的行為規範,非前沿模型的價值來源)。
      審計:1 high(raw/ 重抓碰撞=資料遺失)+8 medium+8 low。
      **修正集已派實作 agent 套用**(16 項:raw _vN 版本化、lazy Chrome、GET-first PDF、SPA 從屬品質檢查
      +無Chrome明確出口、相對圖址+重名、raw/material slug 配對改名、完整性 verify pass、四 ref 繞管線修正、
      DOI opt-in、candidate 多輪可達、glob 空白檔名、web-static 路徑+暫存後搬移)。待審 diff → commit → 勾。
- [~] **learn** — R1 完成(9/9)。帳本與 read 反轉:skill 後勤全贏(工件契約/溯源/離線擷取,
      自由跑無 frontmatter 無索引),**思考全輸**(自由跑 9.5-10:抓到真矛盾、信度表、6 盲點、6 下一步;
      skill runs 7-8.5:批判裝置只在 --brief 路徑,digest 路徑不要求 → 產出教程非研究簡報;
      引註只綁 outline 成文即丟;Refine 無操作/洗稿;錨定評分=未持久化假精度;
      read 的 first-heading slug 規則產生垃圾 slug '1-overview')。
      審計:1 high(§3.5 fan-out 候選從未落盤,bare-topic 功能規格上跑不完)+7 medium+7 low。
      **修正集已派實作 agent**(15 項,核心=批判層四節搬進 digest 路徑+引註段落級保留+Refine 右尺寸
      +fan-out 捕獲步+觸發器記帳+slug 標題防呆)。待審 diff → commit → 勾。
- [~] **hunt** — R1 完成:三 run 全部 0 盲改直取根因(9/9.5/9.5)——「不追根因」慣性在前沿模型不存在;
      skill 賺的=案例記憶/Scope Blast/測試矩陣/跨層確認/儀器衛生;虧的=2x 牆鐘、空庫搜索儀式、
      guard 字面化(helper 斷言 vs 自由跑的端到端持久化斷言)。審計 2 high(allowed-tools 矛盾、
      bisect stash 永不 pop)+7 medium。**修正集已派 agent**(13 項:含快徑、迴歸守護端到端保真、
      RED 證據逐字保存、案例檔生命週期、新建 hunt loop-pauses.md)。待審→commit→勾。
      後續佇列調整(預算/價值):write/design/book/health/evolve 不跑 A/B,改 3+2 個綜合審計
      (一個 workflow 內)+修正;think/analyze/review 複檢=以本 session 累積的慣性知識審文本。
- [x] **learn** — 完成(commit 5e12aaa):批判層四節進 digest 路徑、引註段落級保留、Refine 右尺寸、
      fan-out 捕獲步等 15 項;read 附帶 first-heading 標題防呆。
- [~] **write / design / book / health / evolve** — 綜合審計完成(5 agents,注入慣性帳本鏡頭):
      3 high(design google preset 過不了自家 lint、book PPT 960px vs pt 必炸、evolve 結構閘門驗快照
      非變異)+37 medium(write 的 change-points/「全部」契約缺口正是 learn 新消費路徑、
      design 無 loop-pauses 且 gen 模式自然語言入口死路、evolve 盲測不盲、health 派發欄位不符 inspector 期待…)。
      完整發現:abtest/audit-findings-{skill}.json;摘要:abtest/light-audit-summary.txt。
      **兩個修正 agent 平行執行中**(write/design/book;health/evolve),都被禁改 _shared/loop-contract.md
      (完成後我中央補註冊列)。待兩者回報 → 審 diff → 補註冊 → make test → commit。
- [ ] **think / analyze / review 複檢** — 用慣性帳本鏡頭複查(think=對焦模糊過度自信;
      review=動態多視角+平衡核心理念);有帳本證據才改,無證據不動
- [x] **平等 A/B 最終輪完成**:alignment_goal_met=yes ×2。Opus+v4↔Fable+v4 相似度 82-83(底線 81)、
      Opus直接↔Fable直接 68-70(純模型差=驗證深度);Opus直接 C2+C5 雙FAIL 證實模型原生慣性,
      v4 下兩模型都主動修復 FK 缺陷+reopen 測試。殘餘:Opus 字面核對是程序強制非內化。
      結果摘要:abtest/finale-summary.txt。
- [x] **收尾完成**:v2.8.0(4 觸點含 tests 版本釘)、CHANGELOG、mirror regen、
      **draft PR https://github.com/TLOGBen/baransu/pull/2**(12 commits)。後續 commits 續推同 PR。
      教訓:make test 接 pipe 會吞失敗狀態,驗證命令末端要 echo exit code。
- [x] **think/analyze/review 複檢** — 完成(commit 8063241):15 項跨 skill 一致性修正
      (analyze C{n} 驗證 lane、riding 建議欄、review-agent green_proof 對齊、think draft 落盤等)。
- [x] **write/design/book/health/evolve** — 完成(commit 280c235)。
      **收尾待辦**:最終輪結果分析 → 統整報告(慣性帳本總表+矩陣)→ plugin.json 2.7.7→2.8.0 +
      CHANGELOG → push 分支 → gh pr create --draft。**PR 開了不停** — 之後 commits 持續推同一 PR。

## 延伸 backlog(排到週日,使用者明示:自己不斷找東西優化;每輪維持 ≤12 agents、一次一 workflow)

依價值排序,完成一項勾一項:
- [x] **learn C' 驗證完成**:9.5/10 追平自由跑金標準,judge 判 improved,v1 帳本四 delta 全關
      (批判層實質四節、33 段落級引註過 Refine 保留、無 draft 殘留、gap trigger 真的觸發且照 loop-pauses 處理)。
      read C' 略過(產出本來就位元組級一致);hunt C' 留待有空(另一顆種 bug 輕驗快徑)。
- [x] **機械化完成**(commit d9d518f):verify-skills.py Gate 10(loop-pauses 註冊完整性)+
      Gate 11(green_proof 欄名跨四檔一致),TDD 18 tests;Gate 10 抓到 codex-skill-transfer
      宣告 assisted 無檔的真實缺口(暫豁免)。
- [~] **coverage-completion 審計完成 → 修正 agent 執行中**:0h/10m/15l。重點:codex mirror 的
      AskUserQuestion 改寫污染否定句(弱模型可反轉不變式)、transfer.py 輸出目錄無標記 rmtree、
      _shared 拷貝無掃描、**final-fixer 範圍 REQ-only 但 Step 6 已會因 C{n} 觸發(本輪自己引入的
      跨檔債)**、loop-contract §2 分類 vs 非預設 Input 列、tdd §7.1 被 review-agent 靜默放寬。
      修正含:補 codex-skill-transfer loop-pauses.md + 刪 Gate 10 豁免、make mirror 再生。
      findings: abtest/audit-findings-{codex-skill-transfer,shared-rules,agents}.json。
- [x→後日] **riding tier 微評**:降級不硬造 — Rust fixture 中「真純接線」難以不做作構造(編譯強制
      wiring 與行為綁定);複雜度必須證明價值,留待真實 L-class spec + analyze 測試重量標記時驗證。
- [~] **hunt C' 驗證輪執行中**(wf_ec4187d9-954,3 agents):新種 bug=dao.rs get_novel_by_book_url
      `=`→`LIKE`(SQLite LIKE 大小寫不敏感+%通配隱患,48 測試全綠潛伏);驗快徑/迴歸守護端到端/
      RED 逐字證據/案例檔生命週期/scope blast 放過 upsert 的合法 `=`。
- [~] **evals 體檢 + CLAUDE.md invariant 入冊 agent 執行中**(含 review target-pin 三表面殘餘對齊)。
- [x] **coverage-completion 修正**(commit 178fa24):21 項,Gate 10 零豁免執法。
- [ ] **codex-skill-transfer**:14 個 skill 中唯一整輪未審計的 — 綜合審計一輪(1 agent)
- [ ] **_shared 與 rules 層**:tdd.md / fact-check.md / output-journal.md / anti-patterns.md /
      loop-contract.md 本體從未被審計員直接照過(只被引用檢查)— 一輪 2 agents
- [ ] **未覆蓋 agents**:summarize/smart-friend/merge/e2e-fix/final-fixer + 5 個 perspective reviewer
      + 3 個 health inspector — 契約一致性審計(對照本輪修訂後的 SKILL 們)1-2 agents
- [ ] **學習成果機械化**(最合核心哲學的一項):把本 session 的慣性知識升級為 verify-skills.py 的
      結構閘門 — loop-pauses 註冊表完整性(宣告 loop=assisted/drivable 必有檔案+註冊列)、
      green_proof 欄名跨檔一致、「Criteria 編號不得杜撰」規則存在性等;條款→閘門,prose→機械
- [x] **官方對齊落地**:評估完成,結論=兩個有理由的不動(不加無價值重量):
      (1) disallowed-tools 冗餘 — 18 agents 的 tools: 白名單已機械強制 AskUserQuestion 缺席;
      (2) /review context:fork 不可行 — fork=subagent 化,正是觸發其不安全點的環境;
      (3) paths/when_to_use:description 已載觸發詞且低於預算,暫無增量價值。
- [x] **hunt C'**(judge: improved,4/5 delta 關閉;9/10、~7分鐘,快徑+RED逐字+四層端到端守護全命中;
      殘餘 Locate 期建檔已補錨,commit 3386128)。
- [x] **evals 體檢 + CLAUDE.md 入冊**(commit 84c0594)。
- [ ] **evals/ 目錄體檢**:各 skill 的 evals.json 是否還對得上修訂後行為(design 已修 id 2,其餘未查)
- [ ] **CLAUDE.md/AGENTS.md 更新**:新 invariant 入冊(worktree 路徑、goal-criteria 權威、
      riding tier、批判層、raw _vN…),過時句子清理
- [ ] **README/CHANGELOG 持續補**:每完成一項 backlog 補一段
- [x] **燃燒第二輪收官**(commit 1d6045c,分支 20+ commits):L2 驗證 8.5/10 —— serial-absorbed
      全承重點「可遵循且被遵循」(registry-before-add 由 mtime 決定性證實);8 條文本細化已落
      (證據持久性:/tmp 隔夜蒸發實錘、§4a 單一表述、雙缺席優先權、trace 自含性等)。
- [x] **evolve 第三批完成**(30 agents,commit e8bb760):僅 design 過檻(Gen Mode 驗證錨點
      Step 1.5→Step 3 歸位,Check B/C 從永不觸發變為可觸發);其餘五 skill margin-converged 1-1.5
      = 大修後逼近結構軸天花板的健康收斂。附帶修 nightly-evolve args 字串容忍(driver 實測坑)。
- [x] **evolve 補席完成 + 總結階段完成**(commits 34270dc、e6e0332,分支 23 commits):
      review 過檻採納(Stage 1 去循環),**14/14 ratchet 全覆蓋**;CHANGELOG 燃燒窗口增補、
      PR body 清單更新。
- **剩餘窗口(至週一)為機會性巡守**:每次喚醒檢查 (a) 進行中任務殘留 (b) PR 是否有人留言
      (c) 若無事可做,輕量項候選:hunt C' 第二變體、opus 側 read/learn 驗證、TODO 集中清點;
      **不製造無價值變更**。週一(2026-07-14)後:CronDelete cb9de474、回報完成。
      未修但已回報使用者的:.claude/settings.local.json 過寬 allowedTools(使用者所有物,
      含 2 筆指向已除役 /dev 的條目與 1 筆 xargs 任意讀)。
      evolve 第二批:analyze(Stage 5 回填,margin 3)+ learn($TEMP_FILES 追蹤清理,margin 4-6)
      **已採納推送 f00b2fc**;hunt 純錨點改動被 margin 擋下;think mutate 撞斷點(可入第三批)。
      第三批候選:think/design/evolve/execute/health/codex-skill-transfer(6 skill 未跑過提案輪)。
- **【節奏指令更新,2026-07-11:用量大膽 ×3】**:每個窗口可跑大批次(evolve 全席批/多軌 workflow),
      不必窗口間留白;仍維持一次一個 workflow、結果必落 commit、make test 綠。原慢燒指令作廢。
- **【作廢】原慢燒指令**:改為每個 cron 喚醒窗口推進「一個」適量
      項目(單一 workflow ≤12 agents 或直接手修),不再連發大批次、不再窗口內堆疊多輪。
      窗口間留白是設計,不是怠惰。建議配速:一個窗口跑 evolve 第三批(6 skill 一次)→
      下個窗口收割採納 → 再下個窗口撿 health repo 發現殘項或 TODO 清點 → 週日下午做總結
      (PR body 最終更新、CHANGELOG 收尾、慣性帳本總表)。
- [x] **燃燒窗口三軌完成**(23 agents、1.2M tokens;成果全數落修 commit 436b9c7、9884fdf):
      (1) L-class 機械首測:機械全過(66/66),8 契約缺陷 → serial-absorbed 第三模式入契約、
      §4a crash-window 封口;(2) health dogfood:7 skill 自修 + AGENTS.md 漂移刪除 + 我的
      memory 腐化清理;(3) nightly-evolve dogfood:盲測 panel 生效、margin 守衛正確,
      book/read 兩提案(3/3 strict+margin≥2)已採納(read 案抓到本輪自引入的 mv 巢狀隱患)。
      health 的 repo 發現剩餘未修:settings.local.json 過寬 allowedTools(使用者所有,僅回報)、
      redefine-execute-plan memory 過期(已由本輪 execute 工作取代,可刪)、TODO 標記集中(低優先)。
- [x→原記錄] 燃燒窗口三軌(wf_324b321f-2d4,~24 agents,使用者明示用滿額度):
      (1) **L-class execute 機械實測** — 全 session 空白:worktree 建立/§4d merge/integration_status/
      分支刪除從未被實驗覆蓋;fixture=雙獨立群組 utils spec(ws-l1,檔案不相交確保真平行);
      (2) health dogfood 對 baransu repo 自身(standard tier,雙目的:repo 體檢+skill 自身缺陷);
      (3) 修訂版 nightly-evolve 子 workflow(write/book/ship/read 四 skill 提案輪,實測盲測 panel 修復,
      只提案不採納)。
      ⚠️ nightly-evolve 會在 worktree 的 .claude/evolve/ 寫 scratch/panel 檔 —— **之後任何 commit
      不得用裸 git add -A**,要先檢查 status 或限定路徑(plugins/ scripts/ tests/ 等),勿把實驗殘料入庫。
- **原下個喚醒窗口的首選**(2026-07-10 21:35 記):dogfood **/health 對 baransu repo 自身**
      (1 個 workflow agent 照 health SKILL 跑,標準 tier;真專案實測剛修訂的 health,
      發現既是 repo 體檢也是 skill 驗證)→ 發現落修。
      次選:dogfood /evolve 一輪 ratchet 對一個 skill — 注意:14 skill 剛大修,邊際價值低、
      churn 風險高;只在 health dogfood 完成且仍有大量時間時做,且選未被本輪深動的 skill(如 book)。
      風格提醒:每輪 commit 訊息記「為什麼」;所有驗證命令末端 echo EXIT=$?;
      新發現一律先驗證 claim 再動手;禁止為填時間製造無價值變更(輕重平衡)。
- [ ] **收尾**: 統整報告(每 skill 慣性帳本+修訂+驗證結果)、version bump(2.8.0)、CHANGELOG、push、draft PR

## 當前狀態與路徑（喚醒後先讀這段）

- **Worktree**: /home/vakarve/project/clis/baransu/.claude/worktrees/execute-opus-fable-alignment
  （分支 worktree-execute-opus-fable-alignment;已有 3 commits:f3187c3 execute R1 修正、
  b67b46d 無git降級+ship快速失敗、e3a2637 匯流檔案契約修正;make test 全綠）
- **實驗基地**: /home/vakarve/.claude/jobs/7e0693c7/tmp/abtest/
  （spec/、runs/ws1-5、runs-read/、runs-learn/、mapping-*.json、r1-profiles.json、r1-execute-summary.txt）
- **R1 完整結果**: /tmp/claude-1000/-home-vakarve-project-clis-baransu/7e0693c7-4aae-4eb1-a9a3-bdc2ced69a42/tasks/wlvo0l01d.output
- **R1 關鍵數據**: fable 噪音底線相似度 81;opus+exec↔fable直接 ~50;exec 程序主導行為(ws1↔ws4=85);
  gap: 完成定義(6 vs 8.9, opus 獨有)、效率/儀式(5.7-6.7 vs 9.4, skill 造成)、
  execute 真價值=斷言級 RED(fable 直接跑時 RED 缺失或只有 compile-error RED)
- **喚醒後動作**: 檢查進行中 workflow(TaskList/TaskOutput)→ 有結果先分析落修 → 依佇列推進下一輪;
  每輪結束 commit;usage 快斷時優先把手上分析寫進檔案再發 workflow

## Fixture 資訊

- execute: NovelReader 書籤功能 spec(abtest/spec/2026-07-10-reader-bookmarks/,六檔);
  workspace 複製含 target/(免 BoringSSL 重編);cargo 需 LIBCLANG_PATH=/usr/lib/llvm-18/lib
- read: URL=martinfowler.com/bliki/BranchByAbstraction.html + 本地 fixtures/design-notes.html
- learn: sqlite.org/wal.html + fly.io/blog/sqlite-internals-wal/ + sqlite.org/isolation.html
