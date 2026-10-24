# usage — 呼叫端就是規格

這個形狀的重點是：**變的東西只有兩樣，各自有一個 port**。

- **來源 port**（`references/sources/`）：怎麼讀、怎麼引用、同步點是什麼、怎麼判斷過期、「改壞的版本」長什麼樣、反例怎麼對回來源。adapter：`code`、`document`、`pair`。其中 `pair` 是組合型 adapter，包住另外兩個。
- **工具 port**（`references/tools/`）：模型用什麼語言寫、怎麼跑、怎麼表達「不能發生」和「做得到」、結果怎麼讀回來。adapter：`tlc`（預設）、`kani`（H7 的代表）。

核心只有一條：規則 → 模型 → 嚴格檢查 → 圖組 → 判定 → 原因紀錄。核心只講兩邊共用的表單（`references/ports.md`）：規則表、步驟表、對應表、改壞紀錄、正規化路徑。核心不講 TLC，也不講 `file:line`。

下面每個呼叫點都標出「這次綁了哪兩個 adapter」。這就是 SKILL.md 第 0 步要做的事。

---

## 1. 使用者對程式叫用（H1／H3）

```
/baransu:hypothesis src/approval/ 撤回和核准同時按，不能付錢給已撤回的單
```

- **綁定**：來源 `code`（參數是 repo 裡的路徑），工具 `tlc`（H1：同一份狀態有兩個寫入者，規則是順序問題）。
- **第 1 步，抽規則表**：`code` adapter 從進入點往下讀控制流程，交出步驟表。每一步都有 `file:line`、執行者、是不是不可分割。

  | 步驟 | 執行者 | 引用 | 不可分割 |
  |---|---|---|---|
  | 撤回：讀狀態並檢查 | 申請人 | `src/approval/service.ts:88` | 否，和下一步之間沒有鎖 |
  | 撤回：寫入 withdrawn | 申請人 | `src/approval/service.ts:95` | — |
  | 核准：讀下一個該簽的角色 | 簽核人 | `src/approval/service.ts:121` | 否 |
  | … | | | |

- **第 2 步，跟使用者確認規則**（給使用者看的文字）：

  ```
  我讀到的規則，請確認或改正：
  R1（不能發生）付了多少錢，每個該簽的人都核准過「這個金額」。 ← service.ts:121–140
  R2（不能發生）撤回的單不能付款。 ← service.ts:88–95、payment.ts:30
  R3（不能發生）卡在簽核中卻沒有人能動。 ← service.ts:150
  G1（要做得到）一張 2000 元的單，主管和財務都簽過後會付款。 ← service.ts:121、payment.ts:30
  沒有寫進模型的部分：寄通知信（mailer.ts:12）——無法建模：外部郵件服務。
  ```

- **第 3 到 5 步**：`tlc` adapter 寫 `model/Approval.tla`，每個動作上方用註解寫引用。核心依序跑嚴格檢查：
  1. 對應表完整
  2. 每條 R 都看過它在改壞版本上失敗
  3. G1 做得到，而且拿掉「財務核准」這個轉移之後，G1 就做不到
  4. 範圍寫明
- **第 6 步**：TLC 交出違反 R2 的路徑。`code` adapter 逐步對回程式，每一步程式都走得到，所以這是 bug，不是模型錯。
- **第 7 步**：開啟 `.claude/hypothesis/approval-withdraw/page.html`。第 1 張圖只有正常流程（草稿 → 簽核中 → 核准 → 付款）；第 2 張加上「退回」；第 3 張加上「撤回」；第 4 張把 Bug 1–3 的路徑編號。
- **結尾一行**：

  ```
  hypothesis 完成：approval-withdraw；3 條規則，1 條成立、2 條被推翻（Bug 1、Bug 2）；工具 TLC 2.19，範圍：金額 {500,2000,9000}、最多送 3 次，共 425 個狀態；同步點 a1b2c3d；圖：.claude/hypothesis/approval-withdraw/page.html
  ```

## 2. `/hunt` 在偶發症狀上呼叫（H1–H3，或加了 log 後行為改變）

hunt 的 Tool Scan 多一列：

| Tool | Observable layer | When to use |
|---|---|---|
| `/baransu:hypothesis` | Every interleaving of the steps | Intermittent symptom on shared state, retry/cancel, multi-step status (H1–H3), or the side-effect rule fired |

hunt 的呼叫：

```
/baransu:hypothesis src/approval/ --seed .claude/hunt-report/HUNT-2026-014.md
```

- `--seed` 不是來源。它是**主張的起點**：症狀清單和 hunt 的推測。來源仍然是 `code`。所以 hunt 掛勾不需要新的 adapter，只是核心多一個輸入欄位。
- hypothesis 照第 1 節的流程走完；規則確認那一步，hunt 正在跑的話由 hunt 轉給使用者。
- hunt 讀回結果，只讀不寫：

  ```
  python3 "$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis-status.py" --area approval-withdraw --json
  ```

  拿到 `findings[].trace`（正規化路徑，每一步都帶引用）。hunt 把每一條路徑轉成 yes/no 探針，寫進**自己的** case file：

  ```
  診斷目的：撤回在 service.ts:88 讀到 pending 之後、:95 寫入之前，核准能不能在 :121 完成？
  ```

- 模型通過，不能拿來丟掉線索。hunt 的推測不在 H1–H8 裡時，hypothesis 回一筆原因紀錄（例如「無法建模：硬體時序」）。hunt 照同一份 schema（`references/reason-record.md`）把它抄進 case file，探針照常繼續。

## 3. 讀者使用產物

### `/prove-it`：證明它

prove-it 的第 3 步在開始跑之前，先問一次涵蓋：

```
python3 "$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis-status.py" --covering src/approval/service.ts --json
```

```json
[{"area": "approval-withdraw", "status": "disproved", "stale": false,
  "sync": [{"role": "subject", "kind": "code", "commit": "a1b2c3d"}],
  "tool": {"name": "tlc", "version": "2.19",
           "command": "java -XX:+UseParallelGC -cp \"$TLA2TOOLS\" tlc2.TLC -metadir \"$HYP_TMP\" -config Naive.cfg Approval.tla",
           "cwd": ".claude/hypothesis/approval-withdraw/model"},
  "findings": [{"id": "Bug 2", "rule": "R2", "trace": ["…"]}]}]
```

- `stale: true` 的話，結果是「過期」，交回 `/hypothesis --maintain`，不給「通過」。這個判斷寫在腳本裡，四個讀者呼叫的是同一段程式。
- 重跑時，`$HYP_TMP` 指向 prove-it 自己的暫存目錄。工具 port 規定：重跑不准在產物目錄裡寫任何東西（TLC 預設會在當下目錄留 `states/`）。
- 反例照 `trace` 在真的 app 裡用強制順序重現。結果寫進 prove-it 自己的紀錄，引用 `area` 和同步點。

### `/review`：每條規則變成必答題

- review 對每個改到的檔案呼叫 `--covering`。命中的假說，每條 R 變成一個 walk 上的問題：「這次改動之後，R2 還成立嗎？證據？」
- `stale: true` 或改動落在涵蓋範圍內卻沒有重跑過，回報 `coverage lost: needs /hypothesis`。review 不寫假說。

### 紅綠的確認綠燈、`/draft`

- `/draft` 可以寫「完成 = 假說 approval-withdraw 為 proved」。
- 綠燈步驟對這次改動的檔案呼叫 `--covering`，把每個命中的 `tool.command` 重跑一次。`stale` 不算綠。

### `/health`

- 驗證覆蓋那一層呼叫 `hypothesis-status.py --all --json`，列出 `stale: true` 和 `legacy: true`（還在 `.claude/prove-it/formal/` 的舊檢查）。

## 4. 兩份文件對照（精化檢查）

```
/baransu:hypothesis docs/SD-訂單簽核-v3.docx --against docs/SA-訂單簽核-v2.pdf
```

- **綁定**：來源 `pair`。`pair` 用 `document` adapter 讀兩份文件，`--against` 後面那份當**規則**（SA），前面那份當**行為**（SD）。工具 `tlc`：SA 寫成規格模組，SD 寫成實作模組，加一條精化對應。
- 兩份文件都先交給 `/read --save` 轉成 Markdown，快照存到 `sources/`，同步點記錄每份文件的版本加原檔雜湊。
- 每一條引用都是「原文 + 位置」，而且核心會機械檢查：引用的原文必須逐字出現在快照裡，找不到就是對應表不完整。
- **產出**：

  ```
  SD 沒有滿足 SA：
  反例 1（精化失敗）SA §4.2「金額 ≥ 1000 需經財務加簽」（SA-訂單簽核-v2.pdf，第 7 頁）
    SD 的走法：送出 → 主管核准 → 付款（SD §3.1 流程圖下方說明，第 12 頁）
    SD 在這條路上沒有財務關卡。
  模糊問題（要問誰）：
  Q1 SD §3.4「核准後不可修改」：指的是金額還是整份單？→ 請 SA 作者確認
  ```

- 同一個 `pair` adapter 也接受「文件對程式」：`/baransu:hypothesis src/approval/ --against docs/SA.pdf`。行為那邊換成 `code` adapter，核心不動。

### 單一文件（找矛盾、缺漏、模糊）

```
/baransu:hypothesis docs/需求訪談-簽核.md
```

- 綁定 `document` + `tlc`。發現的類別換成文件的用詞：**矛盾**（兩條規則撞在一起，附走法）、**缺漏**（狀態沒有出路，或某種情況沒交代）、**模糊**（列成要問誰的問題，不自己補）。
- 已知答案考題：「撤回後可重送」對上「撤回為終止狀態」→ 矛盾；被退回之後沒寫能做什麼 → 缺漏；核准綁金額還是版本 → 模糊。

## 5. 維護與搬家

```
/baransu:hypothesis --maintain              # 全部假說
/baransu:hypothesis --maintain approval-withdraw
```

- 依每份來源的 adapter 列出同步點之後的改動：程式看 `git diff <commit>..HEAD -- <covers>`，再加上一次「誰還會寫這份狀態」的搜尋；文件看新版轉出的 Markdown 跟快照的差異。
- 每處改動歸成四類：沒有影響／模型已經不描述來源／承諾是刻意改的／承諾可能被破壞。
- 每份假說的結果是 `in sync`、`updated`、`bug` 或 `blocked`。更新之後，要再看過一次它會失敗，同步點才往前移。
- 第一次執行時，發現 `.claude/prove-it/formal/<area>/` 就提議搬家。使用者同意後用 `git mv` 搬到 `.claude/hypothesis/<area>/`，README 改成新的 schema。搬過來的假說狀態是 `draft`，直到補上「看過它成功」和圖組。在那之前，`/prove-it` 照樣讀舊位置（`hypothesis-status.py` 把它列成 `legacy: true`）。

## 6. 無法寫成假說

```
/baransu:hypothesis src/codec/Decoder.cs 解碼器對任何輸入都不能越界
```

- H7，語言是 C#。工具 port 裡沒有任何 adapter 宣告支援 C# 的程式碼層驗證，所以結果是「無法寫成假說」，不退回性質測試。
- 照樣寫出 `.claude/hypothesis/decoder-bounds/README.md`，`status: unformalizable`，裡面只有一筆原因紀錄：

  | 哪一段 | 原因 | 具體情況 | 要什麼才能形式化 | 現在改走 |
  |---|---|---|---|---|
  | `src/codec/Decoder.cs:40-118` | 沒有工具 | 沒有已收錄的 C# 程式碼層驗證器 adapter | 收錄一個通過考題的 C# 驗證器 adapter | 紅綠測試 |
