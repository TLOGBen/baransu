# baransu v2.0.0 瘦身改版 — /think 最終計畫（修訂版，已折入 /review 發現）

對焦結論（Stage A 三輪）：
- 目的：治理瘦身，路線層可動 — 檢討規則膨脹、16 技能裁併、orchestration 押注部分收回；Waza 機制移植為副產品。
- 約束：零聖牛、用使用證據裁決（你的實際使用：grade/triage/bridge 沒在用、dev 用最少、其餘 12 個常用）；直接破壞性改版、不留別名；新增約束 — 你常用 ultracode，存活技能須評估與 Workflow 編排、/loop 驅動的搭配。
- 成功：裁＋建一次到位，一個版本內出貨，結構性驗收。

兩篇 X 文（mvanhorn《WTF Is a Loop?》、addyosmani《Loop Engineering》）折入的三個方向：
1. loop 的價值全在內部回饋與硬停止（迭代上限／無進展偵測／預算上限）— 沒心跳沒回饋的 harness 正是該裁的「為 loop 而 loop」。
2. 「It's not loops. It's skills.」— 資產是 loop 呼叫的 skill 庫；baransu 的 12 個存活技能要成為 loop 可呼叫的單位。
3. maker/checker 分離 + 狀態落盤 — Done when 要可被外部驗證者判定，狀態走 .claude/<skill>/ 工件。

---

## Building（要做什麼）

baransu v2.0.0。完成後的可觀察狀態：

1. 技能 16 → 12：移除 grade / triage / bridge / dev。
2. 裁併證據（修正後）：harness 的三個 telemetry hooks（user-prompt-submit.py / post-tool-use.py / stop.py）設計上註冊於使用者層 settings.json（INV-1 禁止 plugin.json 帶 hooks）；實測本機 settings.json 無 hooks 鍵、crontab 無排程、telemetry.jsonl 從未收集 — 自癒迴路從未運轉。升級註記：曾安裝 harness 者需自 settings.json 移除三個 hook 條目。
3. 刪除面（全列舉）：4 個技能目錄、hooks 3 檔（903 行；保留 hooks.json + wiki-sync.sh，已驗證與被裁資產零耦合）、scripts 9 檔（2,889 行，含零引用死碼 baseline-parity-score.py；逐檔列名刪除）、agents/investigator-agent.md、_shared 三份遙測 schema（telemetry-schema / grade-triage-schema / state-json-schema，消費者全在被裁面）、對應測試（34 檔中約 28 檔耦合被裁面）。
4. 發行面全掃（新增步驟，root-cause 修法）：dev 與 harness 名稱遍布發行面，逐一處理 —
   - agents/review-agent.md:71：cosmetic path 語義錨定 dev Stage 0 → 改錨到 _shared/tdd.md（實質耦合，必改）
   - think/SKILL.md:175、381 與 hunt/SKILL.md:230：交接改道（見第 6 點）
   - _shared/tdd.md §8 觸發點表：去 dev 化
   - ship/SKILL.md：.claude/dev/ 歸檔通道移除
   - codex-skill-transfer/scripts/transfer.py:819 註解、SKILL.md:116 的 health_check.py 舉例：一行編輯
   - CLAUDE.md 技能表、README 兩條工作流鏈（/think→/dev→/ship、/hunt→/dev）
   - plugin.json 與 marketplace.json：description「16 governance skills」→ 12、keywords/tags 去 dev/tdd 殘留
   - codex/ 鏡像：裁併後以 /codex-skill-transfer 重產整份（鏡像內含 16 技能與鏡像交接點）
5. 12 個存活 SKILL.md 加 Outcome Contract 四行（Outcome / Done when / Evidence / Output）：
   - Done when 以可驗證條件為預設（命令、檔案存在、可數狀態），使技能可被 /goal 式外部驗證者判定；
   - 逃生門：think/write/book 等審美或事件型技能允許「事件型 done」（如核准事件）與人工檢核點列舉，不逼假可驗證。
6. dev 交接改道：think:381 與 hunt:230 改為「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」。不開新檔 tdd-gate.md — 閘門文字併入既有 _shared/tdd.md（它已是自宣告的 TDD 單一知識源，消費者含存活的 impl-agent / review-agent）。「compile error 不計入 failure_count」不變量的唯一事實源維持在 execute/SKILL.md:161,537，tdd.md 只引用不複製。
   - 明文承認語義降級：dev 刪除後，小任務的 TDD 硬閘從 workflow-enforced（TaskCreate 四工項＋紅燈確認）降為 discipline-suggested（文件紀律）。此降級寫入 release notes。
7. 新增 _shared/loop-contract.md：技能被 /loop、cron、automation、Workflow 驅動時 — Input PAUSE 走預設值並在報告標注假設；Authorization PAUSE 任何情況維持硬停；宣告三硬停（迭代上限、無進展偵測、預算上限）的承接方式；狀態落盤沿用 .claude/<skill>/ 慣例。附 per-skill PAUSE 分類表（至少 review/execute/learn 逐互動點標注 Input vs Authorization）。
8. 新增 rules/anti-patterns.md 容器：含「收斂不堆積」自治條款與 strip-provenance 規則；首批填入 baransu 既有 Non-obvious Invariants 中跨技能成立者。
9. 新增 scripts/verify-skills.py：檢查 frontmatter（同時容納倉內兩種風格）、引用檔存在、被裁名稱零殘留（規格寫死掃描 glob 與排除規則：正文/agents/manifests 掃，git 歷史不掃）、雙 manifest 版本一致、Outcome Contract 四行齊備且 Done-when 非空。配一個負向 fixture 測試（違規 SKILL stub → 預期 exit 1），堵驗證器自證循環。
10. 自動化相容雙軸標注（ultracode 編排 × loop 驅動）寫入各 SKILL.md frontmatter：

| 分級 | 技能 | 處理 |
|------|------|------|
| 重疊・改造 | review、execute、learn | 雙模 — 範圍待裁決（見 Unknowns 首項） |
| 增益・輕改 | hunt、analyze、codex-skill-transfer | 加「ultracode 時可派 Workflow」提示；hunt/analyze 補 loop-mode 預設值 |
| 中立・標注 | think、write、ship、read、book、design | 人在迴圈或單線本質；think 標注「不可 loop 驅動」（對焦無法用預設值替代） |

驗收：verify-skills.py 綠燈（含負向 fixture）＋ /plugin validate ＋ 修剪後測試套件通過（附存活測試清單）＋ bump 2.0.0 出貨。

## Not building（明確不做的事）

- 不重建任何事後遙測 loop：不留半套 schema「以備將來」；要 loop 用官方 /loop + /goal + cron + Workflow 拉動，git 歷史是回收站。
- 不做版本 codegen（Waza 的 VERSION + make regenerate）：兩個 manifest 的 drift 面太小，驗證器加版本一致檢查即可。
- 不做 /health 對應物：能力擴張另開 plan。
- 不留 deprecation stub / 別名：破壞性改版已拍板。
- 不重寫 TDAID 與五平面語義：execute 只動相容標注與（若批准的）薄 adapter 章節，不動現行 subagent 迴圈邏輯。
- 不在本次把 12 技能全面改造成 loop 原生：只交付 loop-contract 與可驗證 Done-when 兩個地基；逐技能 automation 深度整合等真實 loop 需求出現再做（loop 由真實重複工作拉動，不由基礎設施推動）。

## Approach（選了哪個方案及理由）

「證據裁併＋ultracode/loop 地基一次到位」。否決的替代案：「先裁後建分兩版」要把 manifest 與文件改兩遍、全量驗證跑兩次；「只裁不建」省下不到三成工時卻丟掉 Waza 研究一半收穫。官方優先：結構驗證疊在 /plugin validate 上只補它不管的層；編排用 Workflow 官方原語；loop 心跳交給官方 /loop 與 cron 而非自製 hooks。已接受邊界：(1) 放棄事後遙測，賭 ultracode 事中驗證＋loop-ready 地基足夠；(2) TDD 硬閘對小任務降級為文件紀律（已明文承認）；(3) think 永久不可 loop 驅動 — 對焦的價值就在人，這是設計立場不是缺口。

## Key decisions（關鍵決策）

1. harness 全刪、不留遙測底座：settings 無 hooks 鍵＋crontab 空＋telemetry 從未收集；loop 判準（心跳＋內部回饋＋真實工作拉動）一條不滿足。取捨：放棄 scripts 2,889 行＋hooks 903 行沉沒成本。
2. dev 裁技能、閘門文字併入既有 _shared/tdd.md（不開新檔）：同一責任不開兩個 home；failure_count 不變量唯一事實源留在 execute/SKILL.md。取捨：小任務 TDD 閘從 workflow-enforced 降為 discipline-suggested，明文寫入 release notes 讓使用者知情。
3. 自動化相容採雙軸標注；雙模具體範圍是本計畫唯一待裁決項（三選項：單一介面＋薄 adapter【推薦】／全部延後／全雙模實作）。無論選哪個，finding schema 同形、depth 不變量逐模重述、Stage 0 模式釘死三件事都是前置條件。
4. 驅動上下文覆寫平台預設（原 Unknown #4 升格）：loop/cron/Workflow 驅動時，loop-contract 的 Input-PAUSE-走預設值規則覆寫全域 platform-awareness 的 supervised 預設；Authorization PAUSE 任何情況不可覆寫。取捨：與全域規則形成顯式分層而非默契。
5. Done when 必須可驗證（含事件型逃生門）：使 12 技能天然成為 /goal 與 loop 的合格被呼叫單位。取捨：移植工作量比照抄 Waza 四行頭大。
6. 驗收即驗證器＋負向 fixture：驗證器本身要能被證明會翻紅，否則驗收是自證循環。

## Unknowns（已知不知道的事）

- 雙模範圍：已裁決（2026-06-10）— 選 A「單一介面＋薄 adapter」：定義單一內部介面（派 N 視角、回同形 finding schema、depth 不變量逐模重述、Stage 0 釘死模式），Workflow 路徑作為介面後的薄 adapter 章節寫進 review/execute/learn 三技能 SKILL.md；附 per-skill PAUSE 分類表。
- ultracode 的可靠偵測方式：system-reminder 格式是否穩定可判？實作 session 第一步實測；不可靠則退化為使用者顯式聲明。
- 測試套件編輯清單的精確邊界（已從「是否觸發」收斂為「怎麼改」）：test-claude-md-skills-table.sh 重生 baseline（CLAUDE.md 表格從 14 列改 12 列）；test_tdd_trigger.sh 修剪 dev 觸發點、保留 impl/review-agent 部分；test-settings-registration.sh 刪除（其斷言對象即被裁 hooks，且今天本來就紅）。實作時逐檔確認其餘 ~25 檔的刪/留。
- 存活 6 個中立技能的 PAUSE 分類是否也要入表：第一版只強制 review/execute/learn，其餘視 loop 實際使用再補。

規模旗標：大型 — 刪約 70+ 檔（含 codex/ 鏡像重產前的舊檔）、改約 25 檔、新增 4 檔（verify-skills.py、anti-patterns.md、loop-contract.md、負向 fixture 測試）。無新服務、無新依賴、無憑證需求。

---

# /review 複審結果（對上述計畫前一版）

**結論：需要你的判斷**（已透過上述修訂折入大部分發現；唯一待裁決：雙模範圍）

- 派遣：architecture + quality 兩視角（乾淨 context、互不知情）＋ adversarial 一輪。security/style 未啟用（計畫不觸 auth/外部輸入，非視覺產物）。
- 正面結論：harness 懸空、schema 邊界、12 技能算術等核心事實聲稱經兩條獨立證據路徑驗證屬實，幻覺率低；wiki-sync 與被裁資產零耦合（可保留）。
- 實質缺口（均已折入修訂版）：
  1. 證據句引錯 seam（hooks 註冊點在 settings.json 不在 hooks.json）→ 已改寫＋升級註記。
  2. dev 耦合面遠超「兩處」（review-agent.md:71 實質耦合、codex/ 鏡像、manifests「16 skills」、README 工作流鏈…）→ 已全列舉＋新增「發行面全掃」步驟。
  3. tdd-gate.md 與既有 _shared/tdd.md 同責兩 home、failure_count 三重編碼風險、閘門語義降級未承認 → 已取消新檔、併入 tdd.md、明文承認降級。
  4. 雙模兩個未列失效模式（finding schema 同形性、depth 不變量換位）＋PAUSE 分類缺盤點 → 列為前置條件＋待裁決。
  5. 驗收鏈失效（test-settings-registration 今天就紅、裁後存活測試近乎空集、驗證器自證循環）→ 驗收改寫＋負向 fixture。
  6. 數字浮報（3,800 行為 scripts+hooks 重複計算）→ 已校正為 2,889+903。
- Hard-stops sweep：1 hit — unverified claims（前版 claim「僅兩處硬編碼」倉級不成立），已依規則釘住並在修訂版以全列舉取代。其餘（destructive auto-execution / unknown identifier / dependency changes / injection）均 not hit。
- E2E：n/a（plan 型目標）。

```
files:         N/A for plan-type
scope:         drift: 前版範圍估算漏掃發行面（codex/、manifests、README、tests）→ 修訂版已補
depth:         standard
perspectives:  [arch, quality] + adversarial: yes
hard_stops:    1 hit ([unverified claims — 前版 claim 2])
new_tests:     1（verify-skills 負向 fixture）
doc_debt:      閘門語義降級須記入 2.0.0 release notes
e2e_status:    n/a
```
