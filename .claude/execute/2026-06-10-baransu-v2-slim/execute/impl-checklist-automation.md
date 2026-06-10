# Impl Checklist: automation

前置群組：cut（1d 序列化後實際排在 contract 之後）

## TASK-automation-01: _shared/loop-contract.md

需求追溯：REQ-004
- [x] 規則段：Input PAUSE 預設值＋報告標注；Authorization 無條件硬停；覆寫優先序明文（引用 platform-awareness 不複述）
- [x] 三硬停責任分界：驅動方持有上限；技能側可重入＋狀態落盤＋無進展明確回報
- [x] PAUSE 分類表：review/execute/learn 逐互動點標注；think 列「不可 loop 驅動」
- [x] 含「本慣例非官方標準」自宣告

Review 結果：advisory
備註：四條驗收標準全數通過；reviewer 獨立重跑 25 條結構斷言 25/25（exit 0）。抽查 review Stage 7 兩互動點、learn 6 互動點（Stage 1 §2 / 2 §1 / 2 §3 / 3 §2 / 4 §3 / 4 §3.4）逐一與 SKILL.md 現況一致；grep 確認 execute SKILL.md 無 AskUserQuestion，Step 0/§4b/§4d/Step 5 枚舉屬實（E2E 失敗路徑全自動，如實標 autonomous，與 ctx 舉例不同係忠於現況、屬正確）；platform-awareness 為路徑引用＋Delta 段，未複述分類；needs judgment=Authorization 判定正確（Stage 7 明文 Do not change behavior without user consent，loop 下不可以預設吞掉裁決）。Advisory：25 條結構斷言僅 inline 執行未持久化為測試腳本（對照 automation-02 已持久化 test-orchestration-interface.sh），建議後續補 tests/skills/test-loop-contract.sh 以利 SKILL.md 變動時重驗分類表。

---

## TASK-automation-02: 三技能 orchestration-interface references

需求追溯：REQ-004
- [x] 各技能 references/orchestration-interface.md：回傳同形契約（review=findings schema；execute=review-agent 形狀，filter/failure_count 章節零 diff；learn={path,lane} 形狀）
- [x] Stage 0 模式釘死＋偵測退化方案
- [x] depth 不變量兩段各一次（grep 每檔 ≥2）
- [x] Workflow 段只派發收集，不複製業務規則
- [x] SKILL.md 本文僅增 ≤10 行指針段

Review 結果：advisory
備註：15/15 green（exit 0）。同形契約逐項對照通過 — review 五欄位與 SKILL.md Stage 4 行 94 逐欄一致、Stage 7 四 tier 語彙一致；execute 五 tier＋green_proof 四 key 與 agents/review-agent.md §3 一致，T5 awk 抽取 Phase 2 / Goal-Alignment Filter / Failure escalation 三段與 HEAD 逐位元比對通過；learn {path,lane}＋lane 語彙（academic|web|gh|x，§1/§2/§3 為 null）＋url 精確去重與 SKILL.md §3.5 行 132-133 一致。Stage 0 釘死＋退化方案三檔皆備；depth 語句每檔恰 2 次；指針段各 7 行（≤10）；execute 指針插在 cross-cutting principles 段、避開 §4b 守護章節。Advisory（不影響驗收）：learn 主流程 §3.5 候選 tuple 為 {path,lane} 但去重 key 為 url 的語義落差為 pre-existing（reference 忠實鏡像並引用主流程，未新增矛盾）。

---

## TASK-automation-03: 12 技能雙軸標注

需求追溯：REQ-004
- [x] 12 檔契約區塊第五行「Automation: 」標注，分級與計畫表一致
- [x] 不使用非標準 frontmatter 欄位
- [x] hunt/analyze 加 Workflow 提示句與 loop-mode 預設值句

Review 結果：advisory
備註：三條驗收標準全數通過。reviewer 重跑 test-automation-annotation.sh GREEN（exit 0），並逐檔核對 12 檔 diff：分級與計畫表逐檔一致（review/execute/learn=overlap+drivable、hunt/analyze/cst=assist+assisted、think=neutral+not-drivable、ship=neutral+assisted、write/read/book/design=neutral+drivable，後四者在計畫表 drivable/assisted 容許域內）；標注均插在 Output bullet 後第五行，既有四行零改動；12 檔 diff 全在本文、frontmatter 零觸碰（測試另以 regex 防 automation/ultracode/loop 鍵洩漏）。PAUSE 語義自洽驗證：write 無任何互動點、read（--web/--gh/--x/--topic 候選選取）/book（Stage 0 對齊批次、fact-verify、圖片確認）/design（gen 方向問題；v1.2 覆蓋走 --force flag 非互動）互動點均屬 Input PAUSE 可預設替代 → drivable 合理；ship 涉 push（外部不可逆副作用）→ assisted 符合 ctx 明文。review/execute/learn 9 行 diff 中 8 行為 automation-02 已審查的指針段，本 task 僅各貢獻 1 行（execute 實質僅增一行，符合 500 行約束）。test-orchestration-interface.sh 15/15、test-outcome-contract-verifiable.sh 均綠。pre-existing 紅 book-stage0 經 reviewer 獨立 stash 比對 HEAD 同紅，與本 task 無關。Advisory：(1) E2E verify-skills.py 屬 TASK-verify-01 尚未落地，C4 全量 E2E 待該 task 補上，本 task 邊界條件已由 test-automation-annotation.sh 覆蓋；(2) ship SKILL.md 本文明示「No user confirmation required」、技能內無 Authorization PAUSE 點，assisted 分級語義繫於 push 外部授權政策而非技能內互動點，loop-contract.md 分類表未枚舉 ship——建議後續在 loop-contract 補一行 ship push 語義註記以免兩文件語義漂移。
