# usage — 用法就是規格

這個形狀只有三個入口：

| 入口 | 誰叫 | 做什麼 | 寫檔？ |
|---|---|---|---|
| `/baransu:hypothesis [任何東西] [--maintain]` | 使用者、或其他 skill 提議後由模型叫 | 寫下、重跑或維護假說；自己判斷給的是程式、症狀、文件還是兩份文件 | 只寫 `.claude/hypothesis/` |
| `hypothesis.py status [檔案…]` | 讀者：`/review`、`/health`、`/hunt`，以及 `/hypothesis` 自己 | 哪些假說涵蓋這些檔案、各自現在的狀態、它們的規則 | 不寫、不跑模型 |
| `hypothesis.py check [檔案…或 area…]` | 讀者：`/prove-it`、紅綠的確認綠燈、`/draft` 的完成條件 | 重跑涵蓋這些檔案的模型，印出現在的判定 | 不寫 |

讀者只學兩行指令和一個標題：規則和發現的一行摘要都印在腳本輸出裡；只有要逐步重現一條路徑的讀者（`/hunt`、`/prove-it`），才去開 README 的 `## 發現`。讀者**不需要知道**：模型用什麼語言、TLC 怎麼叫、同步點是 commit 還是文件雜湊、涵蓋對照表長什麼樣、README 其他章節、舊位置 `.claude/prove-it/formal/` 存不存在。

腳本路徑在讀者的 SKILL.md 裡寫成 `python3 "$CLAUDE_SKILL_DIR/../hypothesis/scripts/hypothesis.py"`，下面簡寫為 `hypothesis.py`。

---

## 1. 使用者對程式叫用

```
> /baransu:hypothesis src/approval/
```

skill 自己判斷：路徑是程式目錄 → 程式輸入；`status src/approval/` 沒有任何涵蓋它的假說 → 新寫；讀到 `status` 欄位被 `submit()`、`withdraw()`、`approve()` 三處修改、三個狀態以上有條件轉移 → 落在 H3（也碰到 H1）。

畫面（節錄）：

```
hypothesis：程式輸入 src/approval/（H3 多步驟狀態機、H1 併發），新寫 area「approval」

先確認規則，一句一條（安全規則各配一條目標）：
  R1 安全｜付出去的錢，一定等於最後一次核准時的金額
  R2 安全｜撤回之後，不會再付款
  R3 安全｜送出後一定有人能處理，不會卡住
  R4 目標｜金額 ≥1000 的單子，經理和財務都核准後會付款
  R5 目標｜金額 <1000 的單子，經理核准後會付款
  不形式化：寄通知信（src/approval/notify.py:12-30）— 無法建模：外部郵件服務
這樣對嗎？要改哪一條？
```

使用者回「對」。之後不再問，直到結尾：

```
hypothesis 完成：approval 不成立（3 條路徑）
  P1 → R1｜送出、經理核准、退回改金額、再送出：舊核准還在，照舊金額付款
  P2 → R2｜撤回和核准同時按：撤回生效，款項照付
  P3 → R3｜財務核准時單子剛好被退回：停在「審核中」沒人能處理
  看過它失敗：3 個壞版本都被抓到；看過它成功：拿掉「財務核准」後 R4 到不了
  範圍：金額 {500, 2000, 9000}、最多送出 3 次；TLC 2.19，425 個狀態，<1 秒
  圖：.claude/hypothesis/approval/page.html（已打開）
  同步於 3f2a1c9；1 筆未形式化（寄通知信）
```

沒有 `--maintain`、沒有 `--tool`、沒有 `--doc`。第二次在同一個路徑叫用：

```
> /baransu:hypothesis src/approval/
hypothesis：approval 仍同步（3f2a1c9 之後涵蓋的檔案沒變）→ 只重跑：不成立，P1–P3 照舊
```

程式改過之後叫用，同一個指令自動走維護（`--maintain` 的觸發條件成立，照 `_shared/auto-flags.md` 說一次）：

```
hypothesis：自動開啟 --maintain：src/approval/service.py 在 3f2a1c9 之後改過
  service.py:41-58 Submit 現在會清掉舊核准 → 模型不再描述程式 → 照程式更新
  重跑：R1 成立；壞版本（拿掉清除）仍被抓到 → 同步點移到 8c01d2e
hypothesis 完成：approval 不成立（P2、P3）；P1 已不再發生
```

---

## 2. `/hunt` 在偶發症狀上叫用

hunt 的 Tool Scan 多一列「形式模型（/hypothesis）｜所有交錯順序、所有狀態路徑｜偶發、加了 log 行為就變、症狀落在 `../hypothesis/references/formal.md` 的 H1–H3」。hunt 在 Locate 階段把案件檔交出去：

```
/hunt：症狀「偶爾撤回後還是付款了」落在 H1（撤回與核准是兩個寫入者）→ 請 /hypothesis 寫成假說
> /baransu:hypothesis HUNT-2026-014
```

`/hypothesis` 看到 `HUNT-` 開頭 → 症狀輸入：讀案件檔的觀察症狀與已定位的檔案，規則從症狀反推（「撤回之後，不會再付款」），一樣跟使用者確認。完成後 hunt 讀：

```
$ hypothesis.py status src/approval/service.py
approval	不成立	同步於 3f2a1c9	.claude/hypothesis/approval/README.md
  R2 安全｜撤回之後，不會再付款	不成立
  P2 → R2｜撤回和核准同時按：撤回生效，款項照付
```

hunt 把 P2 轉成一個 yes/no 探針（「經理核准執行到 `service.py:77` 時撤回，`paid` 會變 true 嗎？」），每一步引用 README `## 發現` 裡 P2 的 `file:line`。模型通過時，hunt 不能拿它來丟掉線索——這條寫在 hunt，不寫在這裡。

使用者在 hunt 裡說「不用寫假說」時，只有這一種情況讀者自己留紀錄，一行，格式固定：

```
未形式化：src/approval/service.py:60-90｜使用者決定不做｜「先不要，趕上線」｜使用者改口時｜hunt 推測
```

---

## 3. 讀者消化產物：`/prove-it` 與 `/review`

**`/prove-it`**——宣稱「撤回跟核准怎麼交錯都不會付款」，涵蓋檔案落在某份假說：

```
$ hypothesis.py check src/approval/service.py
approval	不成立	同步於 3f2a1c9；TLC 2.19，425 個狀態	.claude/hypothesis/approval/README.md
  R1 成立  R2 不成立  R3 成立  R4 成立  R5 成立
  P2 → R2｜撤回和核准同時按：撤回生效，款項照付
exit 1
```

prove-it 照 README `## 發現` P2 的步驟，在真的 app 裡用強制順序重現，寫進它自己的紀錄。如果輸出是：

```
approval	過期	src/approval/service.py 在 8c01d2e 之後改過	.claude/hypothesis/approval/README.md
exit 2
```

prove-it 的判定就是「過期」，交回 `/hypothesis`；腳本在過期時根本不印「成立」，所以讀者沒辦法誤報通過。

**`/review`**——改動碰到 `src/approval/service.py`：

```
$ hypothesis.py status src/approval/service.py
approval	過期	src/approval/service.py 在 8c01d2e 之後改過	.claude/hypothesis/approval/README.md
  R1 安全｜付出去的錢，一定等於最後一次核准時的金額
  …
```

過期時規則照印（review 要拿來出題），但不印任何一條的成立與否；同步時才在每條規則後面印它的判定。

review 把每條規則變成必答題（「這次改動之後，R1 還成立嗎？引用證據」），並回報「coverage stale: needs /hypothesis」。review 不寫、不跑模型。

**紅綠的確認綠燈**：`hypothesis.py check`（不帶參數 = 涵蓋工作區改動的所有假說），exit 0 才算綠。

**`/draft`**：完成條件寫成「`hypothesis.py check approval` 印出成立」。

**`/health`**：`hypothesis.py status`，把 `過期`、`舊位置` 的列放進驗證覆蓋那一層。

---

## 4. 兩份文件對照

```
> /baransu:hypothesis docs/SA-簽核-v1.2.docx docs/SD-簽核-v0.9.docx
```

兩個參數都是文件 → 對照輸入。哪份是規則、哪份是行為，依文件層級自動排：RFP／需求訪談／會議紀錄 → SA → SD，上游當規則、下游當行為；分不出來才問一句。先用 `/read --save` 把兩份轉成 Markdown，再抽流程。

```
hypothesis：文件對照，規則＝SA v1.2，行為＝SD v0.9，新寫 area「approval-sa-sd」
抽出的規則（每條附原文）：
  R1 安全｜金額 ≥1000 要財務加簽　— SA §3.2 p.4「凡金額達新臺幣壹仟元以上者，應會簽財務」
  …
模糊（不准自己補，列成問題）：
  Q1 核准綁的是金額還是版本？— SA §3.4 p.5「核准後如有修改，應重新送簽」沒說改什麼算修改 → 問業務窗口
這樣對嗎？
```

```
hypothesis 完成：approval-sa-sd 不成立
  P1 → R1（精化不成立）｜SD 的「快速核准」直接進付款，跳過財務 — SD §5.1 p.12
  Q1 待釐清（R3 的對錯取決於答案）
  圖：.claude/hypothesis/approval-sa-sd/page.html（已打開，可直接拿去會議）
  同步於 SA v1.2 9f3e1a…、SD v0.9 4c77b0…
```

單一文件（`/baransu:hypothesis docs/需求訪談-0812.md`）走同一條路，只是沒有「行為」那一份，發現分成矛盾、缺漏、模糊三種。

---

## 5. 舊位置 `.claude/prove-it/formal/`

任何一次叫用 `/hypothesis`，只要看到舊位置有 area，就在第一行提議搬：

```
hypothesis：發現 1 份舊位置的形式檢查（.claude/prove-it/formal/approval/），要搬到 .claude/hypothesis/ 嗎？搬的時候會重新看過它失敗一次。
```

搬之前，`status` 把它列為 `舊位置`，`/prove-it` 照它今天的作法跟舊 README 的指令跑。
