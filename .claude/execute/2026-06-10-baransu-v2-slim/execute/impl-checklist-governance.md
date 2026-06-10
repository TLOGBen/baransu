# Impl Checklist: governance

前置群組：cut

## TASK-governance-01: rules/anti-patterns.md

需求追溯：REQ-005
- [x] `plugins/baransu/rules/anti-patterns.md` 存在；檔頭自治條款：收斂不堆積＋strip-provenance
- [x] 首批條目：自 CLAUDE.md Non-obvious Invariants 逐條評估，跨技能成立者入容器，技能專屬者留原處並註明分層原則
- [x] 表格三欄式：慣性 / 錯誤示範 / 正確做法
- [x] CLAUDE.md 增一行指向容器（不搬移技能專屬不變量）

Review 結果：advisory
備註：四條驗收標準逐條核對全數滿足；結構檢查 8/8 綠（exit 0）。自治條款兩條皆為可執行判準（折入優先＋禁近義詞；「防止什麼」掙位置＋禁事故敘事與規模數字），且首批 6 條自身符合 strip-provenance。五條 Invariants 分類正確：僅 depth=1 入容器，四條技能專屬（no-skills-array、-D 旗標、failure_count、DESIGN.md 大小寫）於分層原則節點名留原處。CLAUDE.md numstat 1/0 確認。Advisory：條目 3-4（改測試遷就實作、跳過紅燈）與 _shared/tdd.md §6 反模式速查語義重疊，建議容器加一行 cross-ref 指向 tdd.md 以免雙重維護；另 worktree 內 tdd.md 的 /dev 引用移除屬 reroute 群組 diff，與本任務無關，合併時注意歸屬。
