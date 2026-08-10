# CONTRACT — evolve／health 蒸餾候選矩陣

## 目標
外部 repo、release log、事故、對話或 memory 的靈感，在進入長期 skill／規則前先通過同一份五問矩陣。
一次性、錯層、無驗證或帶專案私貨的候選必須延後、改道或拒絕，不得污染共用治理資產。

## 前提（Premises）
- 已驗：health deep conversation path 已內嵌五問與 layering rule（`health/references/conditional-audits.md:27-39`）。
- 已驗：evolve 尚無 candidate admission gate，且 Stage 0 解析 target 後即建立 durable workdir/snapshot（`evolve/SKILL.md:32-37`）。
- 已驗：evolve 的 single-asset／single-variable 與既有 artifact schema 不允許順手修改其他 owner layer（`evolve/SKILL.md:25-30`、`evolve/references/output-contract.md`）。
- 已驗：Codex transfer 會複製 `_shared` reference，且 mirror 必須由來源生成，不得手改。

## 可斷言條文
- [ ] A1: 五問只有一份 shared authority；evolve 與 health 只引用，不得各自保留複製表格。
- [ ] A2: Recurrence 只能由獨立案例成立；同一對話重複敘述不算第二次發生。候選可用「獨立 recurrence」，或「一個可重現失敗 + red-on-absence behavioral verifier」通過此問；兩者皆無者不得 PROMOTE。
- [ ] A3: 每個候選必須選定一個下方四種 owner layer；Verifier 是正交問題，不是 layer。owner 不是目前目標時只能 REROUTE，不得順手寫入該層。
- [ ] A4: Verifier 必須在候選行為缺失時轉紅；只 grep 到新增文字不得算充分 verifier。
- [ ] A5: project/customer 名稱、私人路徑、issue/build 編號、秘密、機器狀態及未公開 release 資訊必須先去除；無法分離時不得進 public/shared guidance。
- [ ] A6: evolve 只在候選源自 conversation、incident、external repo/release log 或 private memory 時執行矩陣；普通 rubric wording/structure run 不觸發。
- [ ] A7: 對 A6 所列、會觸發矩陣的候選，判斷發生在任何 workdir、snapshot、panel 或 report 寫入前，且只有 `PROMOTE: shared-skill`、target 正確者可進 Stage 1；普通 rubric wording/structure run 沿用既有流程。
- [ ] A8: REROUTE／DEFER／REJECT 是不修改其他層的 off-ramp；不得新增 PAUSE、artifact 或 results/report 欄位。
- [ ] A9: health 只在 deep audit 的 conversation-derived guidance 路徑執行矩陣；處置寫入既有 finding prose，DEFER／REJECT 不得建議寫入 durable docs。
- [ ] A10: `evolve/references/output-contract.md:7-15,44-50` 所列完整 artifact set（`log.md/results.tsv/convergence.svg/held-out.md/report.md/card.html/snapshot/<round>.md`）與 `report.md` required fields 不變；health 既有 report schema 不變，不在本合約複製第二份 schema。
- [ ] A11: executable verifier 必須確認 shared authority 恰有五問、四種處置與四種 owner layers，Evolve gate 位於 durable write 前且只作用於 A6 候選，並解析既有 output-contract 的 exact artifact filename set 與 required-field anchors；保留複製表格、普通 run 被誤擋、刪除任一 artifact 或 required field 時必須轉紅。

## 錯不起表面（Surface Inventory）
| 表面 | 格式 | 釘死測試 |
|------|------|----------|
| evolve admission/off-ramp | 下方「候選處置」單行；只限 A6 候選且禁止先寫 durable artifact | `tests/skills/test-distillation-candidate-matrix.sh` |
| health conversation finding | 同一「候選處置」單行置於既有 prose；禁止另增 report field | `tests/skills/test-distillation-candidate-matrix.sh` |
| shared authority | 恰好五問、四種處置、四個 owner layers；Verifier 正交 | `tests/skills/test-distillation-candidate-matrix.sh` |
| artifact schema | 引用 output-contract.md:7-15,44-50 的 exact 七種 artifact set 與 required fields，禁止增刪改寫 | `tests/skills/test-distillation-candidate-matrix.sh` |

## Verbatim Constants
```text
Recurrence evidence
Durable invariant
Target layer
Verifier
Project/private contamination
PROMOTE|REROUTE|DEFER|REJECT
project|shared-skill|global-rule|private-memory
候選處置：{PROMOTE|REROUTE|DEFER|REJECT} — {一行理由}
```
