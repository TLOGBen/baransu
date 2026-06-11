# baransu v2.1.0 理念合併版 — /think 最終計畫（修訂二版，已折入 /review 全部發現＋可見性三項）

批准：2026-06-11，使用者選「批准實作（完全授權）」。執行形態：Fable + ultracode 單發，不分段。

對焦定案（Stage A 三輪）：
- 目的：**理念的合併** — baransu（結構化管線、五平面、TDAID）× Waza（規則即天花板、克制、人留迴圈）熔成一套；更新項是合併理念的表達。
- 範圍：全面重審 18 項候選（6 Waza 未實現＋3 否決翻案＋/health＋5 doc-debt＋可見性三項）。
- 技能數：接受 13，/health 獨立成技能；「13 即上限、以裁換建」同版入冊。
- 翻案門檻：嚴寬平衡 — 新證據直翻；無證據但體現合併理念可收，標明收錄理由。
- 流程：ultracode 單發；超載觸發砍範圍順序（保單發）。
- 成功：理念成文進 README（條款綁機制）＋結構測試＋2 項 dogfood＋差異盤點清零（清零＝每項有處置紀錄：implemented / declined＋理由 / 已存在）。

---

## Building（要做什麼）

baransu v2.1.0。完成後可觀察狀態：

1. **README 核心理念段**（條款綁機制）：每條理念附至少一個倉內機制錨點，無錨點不入冊。候選條款：規則是天花板（→ anti-patterns 收斂不堆積）、結構是地板（→ verify-skills / gates）、人在授權點（→ loop-contract Authorization PAUSE 永不可覆寫）、證據優先（→ Outcome Contract / claim-cite）、狀態落盤（→ output-journal / .claude/<skill>/ 工件）。串聯維持五平面自動交接，寫為顯式立場（合併中 baransu 保留的注）。
2. **/health 第 13 技能**：移植 Waza /health（素材：前置步驟捕獲的原文），適配 baransu 慣例 — 繁中輸出、Outcome Contract 四行＋Automation 第五行（建議 ultracode=assist, loop=assisted）、五層審計框架（agent config → instruction surfaces → tools/runtime → verifiers → maintainability）、預算姿態先行（預設 summary 審計）、Step 0 專案層級分級。**定位句必寫**：結構驗證歸 verify-skills，/health 查使用者專案的 agent 配置與 AI 可維護性；與裁掉的 harness 不矛盾（harness 審 baransu 自身、無使用者介面）。
3. **/review 加 Finding Quality Gate**：四問門檻（能否引 file:line／能否描述觸發輸入／讀過上下游沒有／嚴重度站得住嗎）、HIGH/CRITICAL 三證據、「乾淨的 review 是有效的 review」（零發現＋明說審查面＝完整輸出，禁止為正當化呼叫製造發現）。
4. **HTML 工作日誌（可見性 #16）**：/think 與 /review 各加 checklist＋步驟 — 交付物產出後以 book golden-template 風格渲染 HTML 落 `.claude/think|review/<slug>.html` 並 SendUserFile；含「執行日誌」節，實作期間持續追記：規範外決策、被迫變更、取捨、其他使用者該知道的事。共用契約立 `_shared/output-journal.md`；execute/SKILL.md 與 tdd.md §7 各加一行「上游 journal 存在則追記」。think/review 的 Outcome Contract Output 行同步改（review 現行「不另落檔」顯式推翻，CHANGELOG 記）。
5. **claim-cite-first（可見性 #17）**：anti-patterns 新條「無源依賴」— 非顯然主張/schema 假設，依賴前先引查證來源（DB 查詢/changelog/file:line）；輸出標注 `(verified: <how>)` / `(inferred: 未實查)`。review/hunt/think 輸出格式句各加一行。
6. **重述＋列步驟＋條件式等確認（可見性 #18）**：anti-patterns 新條「悶頭就做」— 動手前一句重述＋步驟清單**永遠顯示**；等確認分流：互動 → 等；完全授權/ultracode/loop → 依 loop-contract Input-PAUSE 走預設值並標注，不硬停。
7. **anti-patterns 淨增 4 條**：Worktree Safety（授權層級措辭：「請求 review ≠ 授權重整工作樹」；含髒工作區隔離驗證半邊 — 「乾淨隔離的通過才是真訊號」）、不受信任內容（抓回內容中的指令上報不執行）、無源依賴、悶頭就做。入冊前先嘗試折入既有 6 條（收斂條款）。
8. **/write**：長文 change-points 分支（~300 行以上輸出改 change-points 清單，理由：無法當 diff 審、會覆蓋手調措辭）；writing-principles.md 折入中文 AI 腔指紋條目（段末總結句、三段式排比、升華句、「值得注意的是」「綜上所述」「從而/進而」等 — 折入式，不另立檔，與 rules 5/7/8 折疊去重）；em-dash 分級：en 硬禁 U+2014、U+2013 限數字區間例外；zh 軟規則＋voice preset 可覆寫（新語義類別，落點 voice cue 段明寫；余光中 preset 的「——」合法）；**en 規則範例 em-dash 掃描改寫**（含 SKILL.md:63 rule 5 範例自身違規）。
9. **/read**：local-first 預設（本地抽取器優先，URL 不離機）、`--use-proxy` 顯式 opt-in 才走 defuddle/r.jina.ai；認證/內部 URL 禁餵代理；不受信任內容指向 anti-patterns 條目。
10. **CLAUDE.md**：Skills 表加「易混淆／何時不用」欄（單路由面，取代獨立歧義消解表）；「13 即上限、以裁換建」條款；/health 列入表。
11. **verify-skills.py**：`EXPECTED_SKILL_COUNT` 12→13；版本一致檢查擴為三面（plugin.json＝marketplace.json＝codex/plugins/baransu/.codex-plugin/plugin.json）；理念段錨點存在性檢查（README 理念條 grep 倉內路徑並驗存在，borrow check_references 邏輯）。
12. **12→13 漣漪全清**：tests/integration/claude-md-skills-baseline.txt 重生（13 列）、test-distribution-metadata.sh D2（"twelve/12"→"thirteen/13"）/D7（13 列）、plugin.json description "Twelve"→"Thirteen"、test-automation-annotation.sh 含 health。
13. **5 項 doc-debt 清零**：execute/SKILL.md 605→<500 行（段落下放 references/，邊界實作時定）；loop-contract 補 ship push 註記；anti-patterns↔tdd.md §6 雙向 cross-ref；README:50 Codex `--ref v1.1.10` 過時 pin 修正；book-stage0 測試修復（worktree-relative path＋現行 §0 結構）。
14. **codex 鏡像重產 @2.1.0**：transfer.py 全量重產，**/health 入鏡像**；規模旗標：鏡像 267 檔另計。
15. **CHANGELOG v2.1.0**：每收錄項標明對應理念條；記錄 review Output contract 變更與 18 項處置表（implemented/declined/已存在）。

## Not building（明確不做的事）

- make regenerate 式 codegen：三發行面以驗證器三面檢查擋 drift，不建生成管線。
- 36 條 anti-patterns 照搬：違反收斂不堆積；本次淨增 4 條、各自掙得位置。
- /check maintainer 後續鏈（issue triage、release reactions、Release Gate 矩陣）：屬 /ship 擴張，另開 plan。
- 串聯改手動：維持五平面自動交接，理念段顯式立場。
- 第 14 技能或再瘦身：上限條款生效。
- **已存在、不重做**：Pattern-Fix Completeness（/hunt Scope Blast 已覆蓋，v1.4.3）、Autofix 四級路由（/review 四層 tier 已覆蓋）— 盤點標「已存在」。

## Approach（選了哪個方案及理由）

全收＋三輕量變體（VERSION 輕量＝驗證器三面**延伸**非翻案、RESOLVER 簡版＝Skills 表加欄、指紋庫折入式）。否決最小案（留欠帳）與最大案（堆積且單發爆）。理由：Waza 機制在 8 技能/5 發行面規模成立，baransu 對應物按自身 drift 面與使用證據縮放 — 這就是理念合併的示範。已接受邊界：/health 移植量最大不確定（砍序保險絲）；行為紀律有效性靠 dogfood＋日常回饋，結構測試只驗存在性。

## Key decisions（關鍵決策）

1. **/health 第 13 技能＋「13 即上限、以裁換建」同版入冊**；條款機制錨點＝verify-skills 技能數檢查（12→13）。
2. **VERSION 案定性為「延伸」**：v2.0.0 已拍板驗證器路線（雙 manifest 檢查已實作），本次加第三面。證據：codex 鏡像現時落後一版（2.0.0 vs 2.0.1，倉內可驗）；1.5.1 撞版事件移作 Worktree Safety 條目佐證（根因是並行工作流非 manifest drift）。
3. **em-dash 分級**：en 硬禁 U+2014＋U+2013 限數字區間；zh 軟規則＋voice 覆寫為新語義類別。取捨：比 Waza 寬，不誤殺正當修辭。
4. **理念成文「條款綁機制」＋機器驗收**：結構測試驗理念段逐條錨點存在性。取捨：理念段短 — 特性不是缺陷。
5. **砍範圍順序＋降級映射**：RESOLVER 簡版 → 指紋庫 → /write change-points → /health 降下版。映射：砍 RESOLVER/指紋庫/change-points → 對應 CHANGELOG 理念條與結構測試項同移除；砍 /health → dogfood #2 移除、EXPECTED_SKILL_COUNT 留 12、上限條款同退回 12 並標 deferred、KD1 配對整組降版。README 理念段＋doc-debt＋可見性三項**不入砍序**（前兩者為合併本體、後者為使用者痛點直驅）。
6. **可見性對策＝檔案即交付物**：終端顯示是 harness 行為不可控；HTML 日誌落盤＋SendUserFile 可控可追溯。取捨：think/review 每輪多一個渲染步驟。
7. **等確認條件式分流**：顯示無條件、阻塞看驅動上下文（loop-contract Input-PAUSE 既有語義，零新衝突）。

## Unknowns（已知不知道的事）

- **/health 原文**：前置步驟以 /read 慣例捕獲 tw93/Waza skills/health/（SKILL.md＋scripts 結構）；由執行 session 在列車前完成（網路依賴出列車）。
- **em-dash zh 最終形**：折入 writing-principles.md 時與 rules 5/7/8 折疊審查後定；preset 覆寫權保留。
- **execute/SKILL.md 拆檔邊界**：實作時依 verify-skills 500 行 advisory 與內容耦合度定。
- **change-points 與長輸入抑制定界**：兩套長文行為（≥5 段/800 字 per-rule 抑制 vs ~300 行 change-points 輸出形態）門檻定界實作時定；原則：字數門檻沿用既有、輸出形態按行數分流。

規模旗標：大型 — 約 30–35 檔＋鏡像 267 檔另計、1 新技能、0 新依賴、0 憑證。

驗收：verify-skills 綠（含 13 計數、三面版本、理念錨點）＋結構測試綠（baseline 重生後）＋2 dogfood（Finding Quality Gate 真跑本列車 diff、/health 對 baransu repo 首跑）＋`claude plugin validate`＋bump 2.1.0＋CHANGELOG 理念對應表＋push main。

---

## /review 複審紀錄（修訂一版 → 二版的依據）

- 派遣：architecture＋quality 雙視角＋對抗輪。結論：需判斷 6 項（12-pin 漣漪、codex 重產缺項、翻案定性、砍序降級映射、em-dash 範例互咬、錨點無驗法）— 全數折入。
- 事實面零浮報：605 行、--ref 過時、book-stage0 紅、anti-patterns 6 條、雙 manifest 檢查已存在、余光中 preset 用「——」全部驗證屬實。
- Hard stops：none。sign-off：plan-type / on target / deep / [arch, quality]+adversarial / 0 hit。
- 可見性三項（#16-18）為使用者於修訂一版閘門後直接指定之需求，依嚴寬平衡門檻（使用者三次實際經驗＝新證據）收錄，未經第二輪 /review（使用者批准時知情）。
