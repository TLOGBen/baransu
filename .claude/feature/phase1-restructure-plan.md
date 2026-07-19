# baransu Phase 1 版圖重組計畫（/think 五節草稿，待 /review）

對焦結論:目的＝觸發體驗優先／約束＝上限可鬆綁＋可大拆／成功＝觸發正確率可觀測（決策日誌遙測、一個月回看）。

## Building（要做什麼）

落地後的可觀察成果：使用者輸入 `/baransu:contract` 得到一頁合約流程（四節：目標／可斷言條文／錯不起表面／照抄常數）；輸入 `/baransu:seal` 得到單次窄域審查（五行任務書＋直接修正權）；輸入 `/baransu:analyze` 直通大頻段管線（R1–R9 改革版規格→逐 task 實作審查→final 常數比對，原 execute 全流程內含，中途 PAUSE 閘保留）；`/baransu:execute` 這個名字消失，其觸發詞由 analyze 承接；`make test` 全綠、上限錨改 15、CLAUDE.md 換三頻段路由表、版本 bump 3.0.0。

## Not building（明確不做的事）

- 不退役 codex-skill-transfer：實查 28 條專屬測試（verified: `grep -c "def test_" tests/scripts/test_codex_skill_transfer.py` → 「28」），非弱持有，退役無證據支撐
- 不預設啟用 seal-guard hook：只出貨範本（opt-in），等一個月遙測的漏觸發率再決定
- 不在本段跑 Phase 2 雙系統實驗：大頻段合併管線的實戰品質留給下一場獨立實驗
- 不動 review／hunt／think 等其餘 skill 的本體：只加易混淆交叉列
- 不建自動遙測分析管線：選用決策記錄先落決策日誌慣例，人工月回看

## Approach（選了哪個方案及理由）

Stage B 方案 2 修訂版：雙釘獨立（觸發體驗優先的直接結論——名字即觸發器，實驗結論 skill 殘餘本體＝注意力假肢）＋雙塔合一（analyze→execute 交接縫是實驗判死的儀式，大頻段本該一條管線）＋上限 14→15（合併回收一格後僅需一格，修憲幅度最小）。不選最小方案（全併入為模式）因觸發詞彙弱化牴觸目的；不選 16 格方案因保留死縫且修憲幅度加倍。已接受邊界：合併後大頻段品質未經實驗驗證（Phase 2 承擔）；execute 名字消失的習慣斷裂由 description 關鍵詞緩解。

實驗證據錨:驗證輪 p3-os′（R1–R9 全套）20/20 全釘、0 bug、突變 6/6 全殺、$19.29（冠軍 59% 成本）；p-min（一頁合約＋單 seal）行為面 20/20、0 bug、$7.27。記錄於 NovelReader repo `.claude/experiments/2026-07-19-harness-matrix/`（01 run-log、09 validation-verdicts）。

## Key decisions（關鍵決策）

1. **上限 14→15 而非退役 codex**：證據不支持退役（28 條專屬測試、CHANGELOG 提及 86 次；使用率 inferred: 未實查）；修憲附 falsifiable 條款——遙測若證實其三個月零使用即退役回 14。取捨：以裁換建剛性讓渡一格，換不誤殺活資產。
2. **合併保留 /analyze 名字**：沿用觸發習慣與全部文件錨點，不造新名。取捨：名字語意（analyze≠執行）略有擴張，靠 description 首句補正。
3. **R1 條文閘門文本放 _shared 單一實作**：contract 與 analyze 兩處引用同一份，防雙真相源。
4. **分段落地順序固定**：雙釘→合併→憲法與測試→版本；每段 make test 全綠為闖關條件，任一段失敗不進下段。
5. **遙測即決策日誌**：每次 skill 選用（或該用未用）記一筆進 _shared 新慣例，一個月後回看誤觸發／漏觸發率——成功判準落地。

## Unknowns（已知不知道的事）

- 大頻段合併管線的實戰品質：Phase 2 雙系統實驗判定；owner＝下一場實驗
- codex-skill-transfer 真實使用率：遙測三個月；owner＝月回看
- seal-guard hook 是否轉預設啟用：視漏觸發率；owner＝月回看

## 附:Stage E 攻擊角度（已折入對策）

①910 行合併手術風險→分段落地＋每段 make test；②execute 觸發習慣斷裂→description 承接觸發詞；③contract/think/analyze 三向誤觸發→易混淆表劃界＋遙測；④seal 漏觸發→hook 範本 opt-in；⑤Gates 10/11（loop-pauses 註冊、green_proof 四鍵）為合併後 skill 的機械安全網。規模旗標:中大型（約 14+ 檔案、零新服務、零新依賴）。
