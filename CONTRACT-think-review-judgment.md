# CONTRACT — think 最小修法／承重前提與 review 高嚴重度反證

## 目標
`think` 先給行為完整的最小可靠修法，並在 Full Approach 明說最脆弱承重前提與失敗後果。
`review` 的 HIGH／CRITICAL finding 只有經主動反證仍成立時才能保留。

## 前提（Premises）
- 已驗：Lightweight 固定約 10 行與四個既有輸出欄位（`think/SKILL.md:100-120`）。
- 已驗：Full 固定五節，Approach 尚無承重前提句（`think/SKILL.md:346-373`）。
- 已驗：source think 478 行、生成 Codex think 500 行；本批不得靠新增段落突破 500 行。
- 已驗：review 已有 HIGH／CRITICAL 三證據閘、自然 prose 與固定八欄 receipt（`review/SKILL.md:177-190,258-300`）。

## 可斷言條文
- [ ] A1: Lightweight 先建立滿足已陳述 success、failure 與 edge outcomes 的完整方案集合，再以改動行為、檔案與新 abstraction 最少者作為推薦第一句，優先沿用既有路徑與 primitive。
- [ ] A2: suppress、hide、bypass 或遺失任一已陳述 outcome 的 workaround 不得進入完整方案集合，也不得被稱為最小修法。
- [ ] A3: 只有 repo evidence 證明最小修法無法滿足需求時，才能選下一個最小完整方案，並在既有理由中交代該證據。
- [ ] A4: Lightweight 的 `推薦修法／涉及檔案／風險／驗證方式` 名稱、順序及既有確認方式不變，且不新增 PAUSE。
- [ ] A5: Full 的 Approach 恰有一個下方「承重前提」句，內容由既有 Stage B／E 證據收斂，不重新提問。
- [ ] A6: Full 的五節標題與順序 byte-for-byte 不變；Alignment、Stage G 與批准閘不變。
- [ ] A7: source 與生成 Codex think 均不得超過 500 行。
- [ ] A8: 每個 HIGH／CRITICAL finding 在保留前，先寫一個「若觀察到就會推翻核心 claim」的 prediction，再以不同 evidence source/mechanism 驗證並在自然 prose 描述結果；重讀或改寫同一 citation 不算 independent。
- [ ] A9: 被反證推翻的 finding 必須刪除或降級；沒有可執行 falsifier 者依既有 quality gate 降級／刪除，不得向使用者提問以保住嚴重度。
- [ ] A10: review 不新增 reviewer、dispatch round、固定 finding skeleton、PAUSE 或第九個 receipt 欄位。
- [ ] A11: review final conclusion 不得把所有 finding 換個 tier 後交給使用者自行篩選；必須用自然 prose 明說哪些值得納入、哪些不值得納入及其對 review goal 的一行理由；任一集合為空也要明說。
- [ ] A12: executable verifier 必須計算 source/generated think 行數、解析 4／5／8 exact schema、釘住既有 reviewer／adversarial-once／PAUSE control anchors，並以「較小但不完整 workaround」「同 citation 假反證」「保留提示文字但刪除行為」mutation fixtures 證明會轉紅。

## 錯不起表面（Surface Inventory）
| 表面 | 格式 | 釘死測試 |
|------|------|----------|
| Lightweight 推薦 | 既有四欄；只在完整方案集合中選最小者 | `tests/skills/test-inertia-distillation-contracts.sh` |
| Full Approach | 下方一個精確格式句；五節 schema 不變 | `tests/skills/test-inertia-distillation-contracts.sh` |
| HIGH／CRITICAL finding | 自然 prose；禁止同 citation 假反證 | `tests/skills/test-inertia-distillation-contracts.sh` |
| Review worthiness | 自然 prose；禁止省略值得／不值得的明確處置與理由 | `tests/skills/test-inertia-distillation-contracts.sh` |
| Line/control budget | source/generated ≤500；既有 dispatcher、adversarial、PAUSE 不變 | `tests/skills/test-inertia-distillation-contracts.sh` |
| Sign-off receipt | 既有八欄，禁止第九欄 | `tests/skills/test-plain-language-presentation.sh` |

## Verbatim Constants
```text
推薦修法：|涉及檔案：|風險：|驗證方式：
## Building（要做什麼）
## Not building（明確不做的事）
## Approach（選了哪個方案及理由）
承重前提：{X}；若不成立：{實際後果 Y}；設計如何承受：{Z}。
## Key decisions（關鍵決策）
## Unknowns（已知不知道的事）
files:|scope:|depth:|perspectives:|hard_stops:|new_tests:|doc_debt:|e2e_status:
```
