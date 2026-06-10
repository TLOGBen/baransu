# Impl Checklist: distribution

前置群組：cut, reroute, contract, automation

## TASK-distribution-01: manifests／CLAUDE.md／README 同步

需求追溯：REQ-001, REQ-005
- [x] plugin.json：description 16→12 技能改寫；keywords 去 dev/tdd/harness；version = 2.0.0
- [x] marketplace.json：description/tags 同步；版本一致
- [x] CLAUDE.md：技能表 12 列；Layout 更新；Non-obvious Invariants 修訂；harness 敘述全面修訂
- [x] README：技能清單與兩條工作流鏈改道
- [x] release-notes-draft.md（.claude/execute/ 工件）三段：(a) 16→12＋升級指示 (b) 閘門降級記錄 (c) 新治理資產
- [x] `claude plugin validate` 通過

Review 結果：advisory
備註：reviewer 獨立重跑全綠（test-distribution-metadata.sh 11/11、exit 0；claude plugin validate 通過）。獨立 word-boundary 掃描（case-insensitive）四個發行面：grade/triage/bridge/baransu:dev/dev/harness 零命中；tdd 僅以 tdd.md 檔名出現 7 處，與 residue-scan-classification.md 逐項吻合。CLAUDE.md 表 12 列與 skills/ 目錄一致；Layout agents 清單含 style-reviewer.md 與實際目錄一致；failure_count 與 anti-patterns 指針行均保留。release notes 三段齊備，三個 hook 條目名稱正確（user-prompt-submit.py/post-tool-use.py/stop.py）。README 改道句與 think/hunt SKILL.md 改道語式一致（均指向 _shared/tdd.md §7）。Advisory：(1) README:50 Codex 安裝範例釘 `--ref v1.1.10`，相對 2.0.0 已過時（可於 TASK-distribution-02 或定稿時更新）；(2) scripts/verify-skills.py 尚未落盤（verify 群交付），release notes 第三節為前瞻引用；(3) test-claude-md-skills-table.sh 現紅為設計中間態，baseline 重生屬 verify-02，impl 已通知。

---

## TASK-distribution-02: codex/ 鏡像重產

需求追溯：REQ-005
- [x] /codex-skill-transfer 全量重產（原子；失敗即阻塞不手補）
- [x] codex/ 技能目錄數 = 12；無 grade/triage/bridge/dev
- [x] 抽查 think/hunt 鏡像交接點與 plugins/ 一致

Review 結果：advisory
備註：reviewer 獨立重跑 transfer.py（plugins/baransu → /tmp/codex-reverify）exit 0、stderr 0 bytes（無 skip/manual-review），`diff -r` 與 staged codex/ byte 級全等（exit 0）— 原子重產且無手補，強於抽查的全量 parity 證明。鏡像 12 技能目錄（_shared 非技能）、grade/triage/bridge/dev 四目錄不存在；鏡像 plugin.json version=2.0.0。交接句逐字一致：think:389↔codex:396、think:21↔28、hunt:241↔245（均含 _shared/tdd.md §7 改道語式、零 baransu:dev）；think:183↔190 的 AskUserQuestion→「ask the user directly」為 transfer.py 確定性 Codex 改寫，非偏差。staged diff 50 路徑全部位於 codex/（4A/9D/37M，刪除恰為 dev/grade/triage/bridge＋investigator stub＋三 schema）。word-boundary 殘留掃描：baransu:dev 零命中；grade/triage/bridge 命中均為同形字（support-triage、Grade scope、color grade、Codex CLI bridge）或來源側鏡像例句。Advisory：(1) parity 驗證未持久化為回歸測試腳本（對照 contract-02/reroute-02 有落盤）；(2) 三處來源側陳舊例句被忠實鏡像 — agent-mapping.md:30 引 /triage investigator-agent 為例、design preset dashboard.html 樣本列 /grade /triage /bridge、transfer.py:422 註解 grade/CRON.md — 皆非功能性指向，且修 codex/ 會違反原子鏡像約束，應回源頭 plugins/ 處理。
