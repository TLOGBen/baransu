# CONTRACT — hunt 全症狀根因、單一 probe 與遠端唯讀診斷

## 目標
`hunt` 只有在根因能解釋全部已觀察症狀時才能確認；診斷以一次一個 yes/no probe 推進。
本機無法重現時，交付安全、去秘密、使用者可直接執行的唯讀診斷命令。

## 前提（Premises）
- 已驗：一般 hunt 目前沒有全症狀確認閘；該規則只在 Repeated Regression Mode（`hunt/SKILL.md:220-230`）。
- 已驗：`one instrument at a time` 與每輪 `2–3 instruments` 同時存在（`hunt/SKILL.md:47,142-155`）。
- 已驗：Success 五欄、Handoff 六欄、Fast Path 五段為既有固定契約（`hunt/SKILL.md:83-95,274-310`）。
- 已驗：現有 loop registry 已有 Input／Authorization 分類，但沒有 reporter probe（`hunt/references/loop-pauses.md:8-13`）。

## 可斷言條文
- [ ] A1: Locate 起維護全部已觀察症狀；進入 `confirmed` 前，每項必須映射到因果鏈，或以獨立 evidence citation 證明不共享該因果鏈，並記錄另一事件的 id 與 next action。
- [ ] A2: 只解釋部分症狀的假說不得標記 `confirmed`、`已解決` 或 `已解決（附帶條件說明）`。
- [ ] A3: 一個 `probe` 恰好回答一個 yes/no 假說；任一時刻最多一個 active probe，包含 assertion、query、test、log 或 static hypothesis check。只有不回答假說的 inventory/context scan 可平行。
- [ ] A4: 單一 probe 可含一個 assertion/query/test，或 2–3 個協同 log sites；各 site 使用同一 HUNT-id 與 probe label，且不得測第二個假說。
- [ ] A5: independent cross-confirmation 是第一個 probe 關閉後才執行的第二個 probe，且使用不同 observable layer；觀察到失敗的 test 是唯一同層例外。
- [ ] A6: 無法本機重現時，輸出下方 reporter-probe 精確格式；命令基於已知 shell/runtime、綁定一個已知 target selector，並明列有限的 time、work（rows/bytes）與 output budget。禁止 root/home/全資源 wildcard、follow mode、無界裝置及全域掃描後再截輸出。
- [ ] A7: 外部 symptom/service/path 不得直接插入 shell code；必須使用該 shell 的安全引用／位置參數或先驗證為 literal，並以 Verbatim Constants 的 hostile values 證明不會執行或改寫命令。
- [ ] A8: 等待 reporter 結果只新增一個 Input PAUSE；不得新增 Authorization。非互動且沒有其他唯讀檢查可做時，使用既有 Handoff 並輸出下方 LOOP_OUTCOME。
- [ ] A9: Success 五欄、Handoff 六欄及 Fast Path 五段的名稱、順序與數量 byte-for-byte 不變。
- [ ] A10: 每個 probe 執行前必須列出允許觀察／保存的 exact field names；runtime probe、reporter result、逐字 RED evidence 與 case file 只能保存該集合，且值先遮蔽再落盤，禁止完整 object/payload。case file 仍只使用既有症狀／調查／根因／修復區，不得新增頂層 section 或 frontmatter key。
- [ ] A11: pinning test 必須是 Makefile 可直接執行的 shell file，解析實際 fenced output block 的 exact set/order/count；至少一個 mutation fixture 在「刪除行為但保留說明文字」時轉紅。

## 錯不起表面（Surface Inventory）
| 表面 | 格式 | 釘死測試 |
|------|------|----------|
| 根因事件摘要 | 沿用既有因果摘要；禁止漏掉任何未映射症狀後仍宣告已解決 | `tests/skills/test-hunt-diagnostic-contract.sh` |
| reporter probe | 下方五行精確標籤、單一命令、明示三種有限 budget | `tests/skills/test-hunt-diagnostic-contract.sh` |
| Success／Handoff／Fast Path | 既有 5／6／5 schema，禁止增刪改名 | `tests/skills/test-plain-language-presentation.sh` |
| case file | 既有 section/frontmatter；禁止新增 schema或保存未遮蔽 evidence | `tests/skills/test-hunt-diagnostic-contract.sh` |

## Verbatim Constants
```text
診斷目的：{一個 yes/no 假說}
唯讀命令：{一條可直接複製執行且輸出有上限的命令}
執行界限：target={一個已知 selector}；time={有限值}；work={有限 rows/bytes}；output={有限行數/bytes}
請回傳：{限定欄位或行數}
回傳前遮蔽：{credential/token/cookie/PII/完整 payload/私人路徑}
LOOP_OUTCOME: no progress: reporter probe result required
根因：|修復：|確認方式：|測試矩陣：|迴歸守護：
症狀：|已測試的假說：|已蒐集的證據：|已排除的根因：|尚不知道的事：|建議下一步：
root cause|fix|確認方式|迴歸守護|blast verdicts
'; env; #|$(id)|`id`|<newline>|--help
```
