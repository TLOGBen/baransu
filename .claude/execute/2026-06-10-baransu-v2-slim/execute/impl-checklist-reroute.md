# Impl Checklist: reroute

前置群組：cut

## TASK-reroute-01: tdd.md 整併為唯一知識源

需求追溯：REQ-002
- [x] tdd.md 含「直接實作時的紅綠閘」段落（自建紅綠 task list、先紅後綠、紅燈確認再實作）
- [x] tdd.md scope 行與 §8 觸發點表僅列存活消費者（impl-agent、review-agent、think/hunt 改道句）
- [x] 「compile error 不計入 failure_count」在 tdd.md 中僅以「見 execute/SKILL.md」形式出現，全倉權威表述恰一處
- [x] 不存在 tdd-gate.md

Review 結果：advisory
備註：四條驗收標準逐條核對通過（29/29 結構斷言，exit 0）。§7 標題即明示「文件紀律」、內文明文 discipline-suggested 且承認「沒有 orchestrator 替你把關」，無 workflow-enforced 偽裝；§7.3 表與 git 歷史 dev TASK-02/04 閘門表語義逐項對齊（紅燈通過即停、綠燈二連敗即停改建議 /think、compile error 不計重試）。failure_count 在 tdd.md 恰一行且為「見 execute/SKILL.md；僅引用、不複製」形式，全倉權威唯 execute/SKILL.md（:161/:537）。舊 §7 自檢清單遷入 §7.4 未重複；§1.1/§1.2/§1.4 映射由 /dev 改錨 §7，收斂無堆積。advisory 觀察：(1) §7.4 自檢清單巢於 §7 之下，字面上像僅限直接實作路徑（impl-agent 引用整檔仍可達，無功能影響）；(2) 歷史 dev Stage 0 的「Do not ask the user — classify based on the task description alone」一句未隨遷（分類自主性語義輕微流失）；(3) 共用 worktree 含本 task 範圍外髒狀態：CLAUDE.md +1 行與 untracked plugins/baransu/rules/anti-patterns.md（mtime 16:09-16:10，疑為 governance 群並行產出），merge 波次需正確歸屬；(4) test_tdd_trigger.sh 現紅兩處（:48 dev 引用斷言、check2 dev/SKILL.md 存在性）均屬 verify 群修剪範圍，checks 3/4（impl-agent/review-agent 斷言）保留且通過。

---

## TASK-reroute-02: 四處交接與錨點改道

需求追溯：REQ-002
- [x] think/SKILL.md:381 與 :175：小任務 → 「直接實作，依 _shared/tdd.md 紀律自建紅綠 task list」
- [x] hunt/SKILL.md:230：同上改道
- [x] review/SKILL.md:210：regression-first 歸屬句改為「/baransu:execute 或依 tdd.md 的直接實作」
- [x] ship/SKILL.md：.claude/dev/ 自歸檔清單移除，其餘目錄行為不變
- [x] agents/review-agent.md:71：cosmetic 四分類錨點改掛 tdd.md 對應段；execute/SKILL.md 零 diff
- [x] codex-skill-transfer/SKILL.md:116 舉例與 scripts/transfer.py:819 註解改寫（換存活例子）
- [x] word-boundary grep `baransu:dev` 與 `\.claude/dev` 確認 plugins/ 內零殘留

Review 結果：advisory
備註：七條驗收標準逐條核對通過；Green 獨立重跑 28/28、exit 0。重點驗證：(a) 三處改道語式與 release notes 遷移指引一致，hunt/think Stage G 均含固定語式並指向 tdd.md §7（§7 已存在於 reroute-01 產出）；(b) review-agent:71 錨點由 dev/SKILL.md Stage 0 改掛 tdd.md §7.1，與 b09b093 原 dev Stage 0 四分類逐項同序同義對齊，分類邏輯與「markdown-only 歸純格式」備註原樣保留，僅換錨點；(c) ship 的 find 清單、歸檔迴圈、description 三處同步移除 dev，tmp/analyze/execute/think 四目錄行為零變更；(d) execute/SKILL.md 零 diff（git diff --quiet 通過），compile-error/failure_count 權威表述仍唯一在 execute/SKILL.md，本 task 未新增複本；(e) codex-skill-transfer 換用之存活例（design/scripts/check.py、read/scripts/search-papers.py）實檔存在。advisory 觀察：(1) think:175 stage 總覽用英文「direct implementation per _shared/tdd.md」而非固定繁中語式 — 該行為 ASCII 管線總覽、英文 body 慣例，:381 實際交接點已含完整固定語式，語義一致；(2) design preset 三套 HTML 樣本仍含 /dev 字樣（dashboard.html 樣本表格列、gallery.html 註解「+ /dev review」）— 非功能性樣本內容，gallery.html 註解屬輕度行文殘留，已由 impl 回報路由至 C2 終掃分類，建議終掃時一併改寫；(3) plugin.json「16 governance skills」與 keywords dev 屬 distribution 群範圍，impl 已正確回報待路由、未越權修改。
