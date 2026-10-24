# usage — 呼叫端就是規格

這個形狀的拉力：**讓最常見的呼叫端變成一行**。寫假說的是使用者（偶爾），讀假說的是 `/review`、`/hunt`、紅綠的確認綠燈、`/prove-it`、`/health`（每次改動都會讀）。所以讀的那一側被設計成：

> 讀者只跑一個指令、讀一張表、照狀態查表做事。不開 README、不比 commit、不做判斷。

這個指令是 `/hypothesis` 自己附的唯讀腳本：

```
python3 "$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis-status.py" --diff HEAD
```

它回答四件事——**誰涵蓋這些檔案、還同步嗎、說了什麼、過了沒**——而且「過了沒」只在「還同步」時才印得出來。過期的假說，腳本根本不印它當時的結論，讀者想誤讀也誤讀不了。

---

## 呼叫點 1：使用者對程式下指令（寫下）

```
> /baransu:hypothesis src/approval/ 這個簽核模組不能出錯
```

`/hypothesis` 的流程（各步細節在 `sketch/SKILL.md`）：

1. 先跑同一支狀態腳本：`hypothesis-status.py --files src/approval/`。已經有一份 `proved` 的假說涵蓋它 → 符合「不觸發」第 5 條，改成重跑它，不另寫一份。
2. 讀程式，對照觸發清單 H1–H8：同一份 `status` 有 3 個寫入者（H1）、≥3 個狀態且轉移有條件（H3）、付款（H6）。
3. 跟使用者確認白話規則（一句一條，不准有變數名）：

```
我打算寫成假說的規則（請確認或改）：
R1 付款金額，一定等於主管和財務核准當下的金額。
R2 撤回之後，不會再付款。
R3 一張申請不會卡在沒有人能動的狀態。
G1（目標）一張 2000 元的申請，可以一路走到付款。
不打算形式化的部分：
- 寄通知信（src/approval/notify.ts:12）— 無法建模：外部郵件服務。改走紅綠測試。
```

4. 寫模型、跑 TLC、看它失敗（壞掉的變體）、看它成功（G1 可達；拿掉 `Approve` 轉移後 G1 不可達）。
5. 最後一步才寫 `hypothesis.json`（讀者唯一看的檔），然後打開 `diagrams.html`。

使用者看到的收尾一行：

```
hypothesis 完成：approval｜3 條規則，2 條被推翻（P1、P2）、1 條成立｜TLC 2.19，425 個狀態｜範圍：3 種金額、最多送 3 次｜同步：a1b2c3d｜圖：.claude/hypothesis/approval/diagrams.html
```

---

## 呼叫點 2：`/hunt` 碰到偶發症狀

使用者回報：「有時候撤回了還是付款了。」hunt 在 Tool Scan 走到新的一列（H1–H3 類偶發、或加 log 後症狀變了）：

```
| formal model（/hypothesis） | 所有交錯順序 | H1–H3 偶發症狀；加了 log 後行為改變 |
```

hunt 先跑一行：

```
$ hypothesis-status.py --files src/approval/withdraw.ts src/approval/pay.ts
area      state      rules  sync     why
approval  disproved  3      a1b2c3d  -
exit 1
```

查表（`references/reading.md` 的狀態 × 讀者表）：`disproved` 給 hunt 的動作是「把每條編號路徑變成一個 yes/no 探針」。hunt 再跑：

```
$ hypothesis-status.py --paths approval
P2  R2  disproved  撤回和主管核准同時按下，撤回先寫入、核准後寫入，付款照付  counterexamples/P2.md
```

hunt 的下一個探針直接從 P2 劇本來：「`withdraw.ts:33` 寫入 `withdrawn` 之後，`approve.ts:58` 的檢查有沒有重新讀狀態？是／否」。

沒有任何假說涵蓋（`exit 10`）時，hunt 叫 `/hypothesis` 帶著症狀去寫一份：

```
/baransu:hypothesis --symptom "撤回後仍付款，偶發" src/approval/
```

`proved` 時的動作也寫死在表上：**模型通過不能拿來丟掉線索**——hunt 只記「模型在這個範圍內沒找到這條路徑」，然後檢查範圍外（`--scope approval` 印出範圍）。

hunt 自己的一般因果猜測，一律叫「推測」，不叫假說。

---

## 呼叫點 3：讀者——`/review` 與紅綠確認綠燈

### `/review`

reviewer 在排 walk 之前跑：

```
$ hypothesis-status.py --diff main
area      state  rules  sync     why
approval  stale  3      a1b2c3d  changed: src/approval/approve.ts; new-writer: src/jobs/auto-approve.ts
exit 1
```

查表：`stale` 給 review 的動作是兩件，都不用判斷：

1. 回報一條固定格式的發現：「假說 approval 已過期：`approve.ts` 改過，`auto-approve.ts` 是新的寫入者。需要 `/hypothesis --maintain approval`。」——**不寫「通過」**。
2. 把每條規則當成 walk 上的必答題：

```
$ hypothesis-status.py --rules approval
# approval  state=stale  — verdicts hidden: stale
R1  safety  ?  付款金額，一定等於主管和財務核准當下的金額。
R2  safety  ?  撤回之後，不會再付款。
R3  safety  ?  一張申請不會卡在沒有人能動的狀態。
```

注意第三欄是 `?`：狀態不是 `proved`／`disproved` 時，腳本把當時的結論藏起來。reviewer 拿到的是「問題」，不是「答案」。

review 永遠不寫 `.claude/hypothesis/`；它能做的最多是在輸出裡寫 `coverage lost: needs /hypothesis`。

### 紅綠確認綠燈（`_shared/tdd.md` §7.2 第 4 步）

```
$ hypothesis-status.py --diff <task-base>
```

綠燈規則只有一句：**每一列都是 `proved`，或一列都沒有（exit 0 或 10）**。其他一律是紅：

- `stale` → 紅，並且**馬上自動**叫 `/hypothesis --maintain <area>`，回來再跑同一行；印出 `proved` 綠燈才過。改了涵蓋檔案，假說必然過期——這是設計，不是 bug；`--maintain` 的「沒有影響」是最便宜的出口。
- `disproved` → 紅：定義完成沒達到。
- `draft`／`broken`／`legacy` → 紅，回報原因（`legacy` 與搬過來還沒維護的，原因都是「嚴格檢查未完成」）。

無人模式下，`--maintain` 只會在「承諾看起來是刻意改的、卻找不到證據」時停下來；這時綠燈維持紅，回報「卡住」和要問的問題。

`/draft` 寫「完成 = 假說 approval 被證明」時，驗收指令就是 `hypothesis-status.py --area approval`，exit 0 才算完成。

### `/prove-it`

```
$ hypothesis-status.py --files <claim 涵蓋的檔案> --json
```

- `proved`／`disproved` → 用 `--check approval` 印出的固定指令重跑模型（工具版本鎖定），結果寫進 prove-it 自己的紀錄；`disproved` 再到真的 app 用強制順序重現 P1、P2。
- `stale` → 紀錄寫「過期」，不給 proved，並且**自動**叫 `/hypothesis --maintain <area>`，維護完再跑一次。
- `draft` → 紀錄寫「未完成」，不給 proved。
- `legacy`（`.claude/prove-it/formal/<area>/` 還沒搬家）→ 照 8.15.0 的舊作法跑舊位置，但結果最多是「嚴格檢查未完成」，**不能拿來宣告完成**：那份檢查從沒做過「看過它成功」。

### `/health`

```
$ hypothesis-status.py --all
```

驗證覆蓋層列出每一列不是 `proved`／`disproved` 的假說。

---

## 呼叫點 4：兩份文件對照（精化）

```
> /baransu:hypothesis docs/SD-簽核.docx --satisfies docs/SA-簽核.pdf
```

方向寫在旗標上：`--satisfies` 前面那份是**行為**，後面那份是**規則**。不會搞反。

1. 兩份都先過 `/read --save`，轉成 Markdown 存在 `.claude/read/`；同步點雜湊的是**原檔**（使用者會改的是原檔）。
2. 從 SA 抽規則、從 SD 抽流程，每一條都附原文和位置，給使用者逐條確認。
3. 精化檢查：SD 的每一步都要是 SA 允許的一步。

```
hypothesis 完成：approval-sd-vs-sa｜精化不成立：P1（SD 3.2 節，金額 ≥1000 沒有財務關卡，SA 第 4 頁要求加簽）
矛盾 1｜缺漏 1｜模糊 1（要問：業務窗口——核准綁的是金額還是版本？）
圖：.claude/hypothesis/approval-sd-vs-sa/diagrams.html
```

之後 SA 改版，任何讀者跑 `--all` 都會看到：

```
approval-sd-vs-sa  stale  4  SA@v1.2  changed: docs/SA-簽核.pdf
```

---

## 最小指令面（全部）

寫的一側（只有 `/hypothesis` 自己）：

```
/baransu:hypothesis <path|module|question>             # 程式
/baransu:hypothesis --symptom "<症狀>" <path>            # hunt 交辦
/baransu:hypothesis <doc>                                # 單份文件：矛盾、缺漏、模糊
/baransu:hypothesis <behaviour-doc> --satisfies <rules-doc>   # 精化對照
/baransu:hypothesis --maintain [<area>]                  # 四類維護；第一次會提議搬舊位置
```

讀的一側（任何 skill、任何人，唯讀）：

```
hypothesis-status.py --diff <base> | --files <p>... | --area <a> | --all   [--json]
hypothesis-status.py --rules <a> | --paths <a> | --scope <a> | --check <a>
```

`/baransu:hypothesis --status ...` 只是叫這支腳本，讓使用者也有同一張表。
