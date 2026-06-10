# Impl Checklist: contract

前置群組：cut（1d 序列化後實際排在 reroute 之後）

## TASK-contract-01: 可驗證型八技能契約頭

需求追溯：REQ-003
- [x] 八檔（analyze/execute/ship/read/learn/hunt/design/codex-skill-transfer）frontmatter 後、第一個 H2 前出現 Outcome Contract 四行
- [x] Done when 均為命令、檔案存在或可數狀態
- [x] 既有正文零刪改（契約是前置補充，不重寫技能）

Review 結果：advisory
備註：三條驗收標準逐條通過。閘門測試 tests/skills/test-outcome-contract-verifiable.sh 8/8 GREEN（含 mutation 負向驗證：清空 design Done when → 正確 RED exit 1，已還原）。抽樣 analyze/ship/hunt 對照正文：Done when 全部提煉自既有完成定義（analyze Stage 6「One round only」、ship porcelain/push/worktree、hunt 成功格式+HUNT case file），無新發明語義；execute/design/cst 的命令引用（Step 6 Final-Review、check.py、transfer.py）亦逐一對到正文行號。execute 僅檔頭單一 hunk，Goal-Alignment Filter 與 failure_count 章節零變更；八檔 deletions=0。Advisory 一項：verify-skills.py 尚不存在（Wave 3 verify 群產出），新測試目前為唯一可執行閘門且額外驗排序與插入位置（verify-skills.py 規格只查四行齊備非空）→ 屬補充非重複，建議保留並把最終去留路由給 verify 群決定。另記：worktree 內同時存在 book/review/think/write 四檔事件型契約變更（TASK-contract-02 共用 worktree），非本 task 越界；book-stage0 測試紅為 §0 --format guard 缺失，pre-existing、與本 diff 無關。

---

## TASK-contract-02: 事件型四技能契約頭

需求追溯：REQ-003
- [x] think Done when = Stage G 批准事件型表述
- [x] write/book 混合型；review =「報告含八欄 sign-off receipt 且 hard-stops sweep 完成」
- [x] 無「輸出存在」式空殼條件

Review 結果：advisory
備註（重試輪，前輪 packaged confirm (correctness) 兩 findings 均已解）：write Done when 改為「且無 rules 5/7/8（禁對仗句/禁排比/禁名詞化）違反殘留」，逐字可溯源至 write/SKILL.md:84 實存規則句「Voice cue does not override rules 5, 7, 8 (anti-AI 味 floor: 禁對仗句 / 禁排比 / 禁名詞化)」，並對得上 zh rules 5/7/8 條目（L47/L49/L50），em-dash 發明語義已清除（test 與契約 grep 均零命中）。test-contract-02.sh:50-51 斷言同步改為 Before/After＋rules 5/7/8＋禁對仗；reviewer 獨立 mutation 驗證：抹除契約行 rules 5/7/8 → 36/37 exit 1（斷言確實咬合），還原後 37/37 exit 0，write diff 回復 +7/-0。三條驗收標準全勾；think/book/review 三檔零變更（各 +7/-0 同前輪），四檔 deletions=0、frontmatter 未動。Advisory 兩項：(1) 契約「rules 5/7/8」沿用正文 L84 的 zh 編號，en 規則集對應條目實為 5/6/7 — 此編號歧義為正文既有、非契約引入，可留待後續正文整理；(2) verify-skills.py（Wave 3 verify 群）尚不存在，本 gate test 仍為唯一可執行閘門，最終去留由 verify 群決定（同 contract-01 備註）。
