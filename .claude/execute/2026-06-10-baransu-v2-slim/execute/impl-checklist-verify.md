# Impl Checklist: verify

前置群組：reroute, contract, automation, governance, distribution（baseline 重生需在 CLAUDE.md 表更新後）

## TASK-verify-01: scripts/verify-skills.py＋負向 fixture

需求追溯：REQ-005
- [x] 檢查項：目錄數 12；frontmatter 兩風格＋官方細目（name ≤64 小寫連字符、description 非空 ≤1024、第三人稱）；references 存在且一層深；被裁名稱零功能殘留（word-boundary、glob 與排除規則內嵌）；雙 manifest 版本一致；契約四行＋第五行 Automation 標注
- [x] advisory：SKILL.md >500 行清單（不影響 exit code）— execute 605 行列出，exit 仍 0
- [x] exit 0/1/2 語義；違規收集後一次輸出 — reviewer mutation 抽查三面（契約行刪除 / manifest 版本漂移 / 殘留注入）均 exit 1 且批次輸出；structural probe（無 frontmatter stub）exit 2 並指名路徑
- [x] tests/scripts/test_verify_skills.py：正向 exit 0＋負向 fixture exit 1 — pytest 8/8 通過（TDD 先紅依 impl 回報 6 failed，檔案尚未入 git 無法獨立稽核歷史）
- [x] 對當前倉執行綠燈 — python3 scripts/verify-skills.py exit 0，輸出涵蓋全部 7 檢查面＋白名單分類計數

Review 結果：advisory
備註：三處「檢查器過嚴」修正逐一驗證屬正當：(1) design SKILL.md:90/153 為 v1.2 已廢除目錄的歷史說明句，references/cores 與 references/slide-cores 確實不存在，跳過存在性檢查正確；(2) learn 跨技能 anchor-cite 五個目標檔（read/references/acquisition/{gh,x}-search.md 等）全部實際存在；(3) marketplace.json 版本確實只存在於 metadata.version（plugin entry 無 version 欄），2.0.0 與 plugin.json 一致。advisory 觀察：(a) 跨技能 reference fallback 以「任一 sibling 命中」放行，精度略寬（任一技能恰有同名路徑即可遮蔽缺檔）；(b) REF_DEPRECATION_LINE_RE 以行內 deprecated/removed 字樣整行跳查，未來新增含該字樣的活引用行會被略過；(c) exit 2 structural 路徑無自動化測試（reviewer 手動 probe 通過）。三項均不影響本 task 驗收。impl 回報之 tdd-trigger fixtures / table 測試殘名屬 TASK-verify-02 範圍，未越界擅修，正確。

---

## TASK-verify-02: 存活測試修剪

需求追溯：REQ-005
- [x] baseline 重生為 12 技能列；test-claude-md-skills-table.sh 斷言改 12 並通過
- [x] test_tdd_trigger.sh 與 fixtures：移除 dev 觸發點，保留 impl-agent/review-agent 斷言並通過
- [x] 存活套件清單落盤；全綠

Review 結果：advisory
備註：reviewer 重跑驗證——table 測試 43/43 綠（baseline 12 列與 worktree CLAUDE.md 表逐列 byte-level 一致）；tdd_trigger ALL CHECKS PASSED（dev 斷言移除反映 skills/dev 已實際刪除、tdd.md 零 dev 引用；保留斷言仍 grep 實檔有檢驗力；lure/anti-leak 不變）。book-stage0 pre-existing 判定獨立複驗成立：b09b093 版測試對乾淨主 repo 原樣執行即紅（T1–T5 同組失敗）、SKILL_MD 寫死主 repo 絕對路徑（L10）、本波次 book/SKILL.md diff 僅 +8 行。pytest：20 passed（含 verify-01 後到的 test_verify_skills 8 項），僅 2 紅為 ctx 明列 pre-existing（test_check_design）。advisory：(1) surviving-tests-run.md 為時點記錄（14 collected），verify-01 落地後現為 22 collected，可選擇性補註；(2) book-stage0 修復建議另開 task（路徑改 worktree-relative＋斷言對齊現行 §0 結構）。
