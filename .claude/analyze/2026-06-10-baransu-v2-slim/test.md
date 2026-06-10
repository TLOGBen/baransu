# Test Strategy

## E2E 測試策略

| 場景 | 起點 | 終點 | 對應 Criteria |
|------|------|------|--------------|
| 結構完整性一條命令 | `python3 scripts/verify-skills.py` | exit 0，輸出 12 技能逐項通過（含契約四行、第五行 Automation 標注、官方 frontmatter 細目） | C1, C2, C3, C4, C6 |
| 驗證器可證偽 | 對負向 fixture stub 執行 verify-skills.py | exit 1，指名違規項 | C6 |
| 插件可安裝 | `claude plugin validate`（或 /plugin validate） | 通過，無 schema 錯誤 | C8 |
| pytest import 健康檢查 | `python3 -m pytest tests/scripts/ --collect-only`（Wave 1 刪除後即跑） | 無 import error；conftest/fixture 無殘缺 | C7 |
| 修剪後套件 | 逐一執行存活測試（bash tests/.../*.sh、pytest tests/scripts/） | 全綠，無 skip 掩蓋；存活清單落盤 | C7 |
| 殘留掃描 | word-boundary grep 發行面（以 Wave 1 刪除後狀態為基準） | 僅同形字樣（人工分類清單為證） | C2 |

## 整合測試策略

| 測試目標 | 涉及層 | 關鍵驗證點 |
|---------|--------|-----------|
| manifest ↔ 技能目錄一致 | 發行 metadata × 技能層 | 兩 manifest 描述 12 技能、keywords 乾淨、version 2.0.0 同步；目錄數=12 |
| repo scripts/ 新建 | 執行層 | repo 根 scripts/ 存在、verify-skills.py 可直接以 python3 執行；plugins/baransu/scripts/ 不存在 |
| Outcome Contract 齊備 | 技能層 × 驗證器 | verify-skills.py 逐檔斷言四行非空＋Done-when 非空；負向 fixture 缺行 → exit 1 |
| anti-patterns 容器就位 | rules × 文件層 | rules/anti-patterns.md 存在；自治條款（收斂不堆積、strip-provenance）明文；首批 5-8 條來自 CLAUDE.md Non-obvious Invariants 逐條評估；三欄表完整 |
| CLAUDE.md 表 ↔ baseline | 文件 × 測試層 | test-claude-md-skills-table.sh 以重生後 baseline 通過；表 12 列 |
| baseline 重生序列 | distribution × verify | distribution-01 完成 CLAUDE.md 表同步 → verify-02 重生 baseline → 重跑該測試（時序依賴明文，不可倒置） |
| review-agent 錨點改掛後 execute 管線語義 | 代理層 × 技能層 | review-agent.md 的 cosmetic 四分類引用 _shared/tdd.md 對應段落；execute/SKILL.md 的 Goal-Alignment Filter 與 failure_count 章節零變更（diff 為證） |
| tdd.md 整併後消費者 | _shared × agents | impl-agent/review-agent 對 tdd.md 的既有引用行不變；tdd.md §8 觸發表僅剩存活消費者；test_tdd_trigger.sh 修剪後通過 |
| wiki-sync 不受波及 | hooks | hooks.json 內容不變；wiki-sync.sh 零 diff |
| codex/ 鏡像 parity | codex/ × 技能層 | codex/ 技能目錄數=12；鏡像內 think/hunt 交接點與 plugins/ 版本一致（抽查比對） |
| loop-contract ↔ 全域規則分層 | _shared × 使用者全域 rules | 明文「驅動上下文覆寫平台預設；Authorization 不可覆寫」（引用 platform-awareness 而非第三份編碼）；三硬停責任分界 ≥3 項明文；PAUSE 分類表覆蓋 review/execute/learn 全部互動點；含「本慣例非官方標準」自宣告 |

## 關鍵邊界條件

- word-boundary 掃描必須排除同形誤報（upgrade/downgrade/gradient/bridging 行文）；分類結果落盤為清單，不得以「grep 無輸出」單獨作為 C2 證據 — REQ-001
- 改道內容驗證：reroute-02 的 7 處改寫點（think:381/175、hunt:230、review:210、ship、review-agent:71、codex-skill-transfer 兩處）改寫後須引用「_shared/tdd.md」或「直接實作」語式；grep 零 `baransu:dev` 與 `\.claude/dev` 功能性引用 — REQ-002
- test-settings-registration.sh 是既有紅燈（斷言對象即被裁 hooks），刪除它不得記為「修復」；存活測試出現非預期紅燈須先判定根因（既有 vs 裁併破壞），不得為過閘改斷言語義 — REQ-005
- 契約頭對兩種 frontmatter 風格（think 極簡式 / read-learn 完整式）都要通過 verify-skills.py 解析；官方細目（name ≤64 小寫連字符、description 非空 ≤1024、第三人稱啟發式）納入檢查 — REQ-003, REQ-005
- 事件型 Done when（think/write/book）不得寫成空殼條件（「輸出存在」不合格）；驗證器只查四行齊備與非空，語義品質由 spec review 把關 — REQ-003
- 雙模 depth 不變量：review/execute/learn 各自的 references/orchestration-interface.md 內，depth 限制語句於兩個 adapter 段各出現一次（grep 計數每檔 ≥2）— REQ-004
- 自動化標注覆蓋：12 檔契約區塊第五行均含「Automation:」且值非空（缺漏 → verify-skills exit 1）— REQ-004
- depth 違反的「行為層」偵測（agent 實際呼叫 skill）不納入 verify-skills.py 自動驗證 — 文字層計數可自動，行為層留給 spec review 與 execute 既有測試 — REQ-004
- failure_count compile-error 規則在全倉的權威表述恰好一處（execute/SKILL.md），tdd.md 僅引用 — REQ-002
- ship 的歸檔通道移除 .claude/dev/ 後，對其餘目錄（tmp/analyze/execute/think）的歸檔行為不變 — REQ-002
- codex/ 重產是原子動作：失敗即阻塞出貨（C8 不達成），不手補 — REQ-005
- 刪除 28 個測試檔後，pytest 對 tests/scripts/ 的收集不得因 conftest 或 fixture 殘缺而報 import error — REQ-005
- SKILL.md >500 行為 advisory 清單（execute 既有超限戶），不影響 exit code — REQ-005
