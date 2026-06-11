# Test-Driven Development — TDD reference (authoritative for baransu)

> **Scope**: 任何在 baransu 框架下撰寫、修改、或審查測試的觸發點（`/execute` 的
> `impl-agent`、`/execute` 的 `review-agent`、以及 `/think`／`/hunt` 改道後由主 session
> 直接實作的小任務）都把這份文件當作 **「如何設計 Test」單一知識來源**。本檔翻譯/本地化
> 自 mattpocock/skills 的 TDD skill，並以 baransu 既有 RED / GREEN / TDAID 詞彙作 inline gloss。
>
> **Source attribution**: 翻譯自 [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd)
> commit `b843cb5ea74b1fe5e58a0fc23cddef9e66076fb8` (2026-04-30)，原作 Matt Pocock。
>
> **License**: 原作為 MIT License (Copyright © 2026 Matt Pocock)。本檔為衍生著作，沿用
> MIT 授權；保留原始 attribution。
>
> **觸發點**: `impl-agent.md` 通用原則 §1 之前、`review-agent.md` 通用原則 §3 之前，
> 以及 `/think`／`/hunt` 的小任務改道句（指向本檔 §7 的直接實作紀律）。皆以被動引用句指向本檔。

---

## 1. 核心原則（四條主骨）

每條原則先給原文重點、再給 baransu 上下文映射。

### 1.1 Test 驗行為，不驗實作 (test-verifies-behavior)

**原則**: 好的測試透過 public interface 驗證系統做了什麼，不驗系統怎麼做。Code 可以全
換、test 不該動。如果 refactor 內部結構（沒改 behavior）會讓測試 fail，那測試驗的是
implementation、不是 behavior。

**baransu 上下文映射**:
- 在直接實作的 RED→GREEN 循環（§7）中，工項 1 撰寫的紅燈測試必須描述「行為」而非「實作」。
  測試名稱寫成 `test_user_can_checkout_with_valid_cart` 是行為；寫成
  `test_processOrder_calls_validateInventory` 是實作。
- 在 `/execute` 的 TDAID 循環中，`impl-agent` 寫的測試在 `review-agent` Phase 3 的
  test_quality 觀察維度中，會被檢查是否 survive 假想 refactor。
- 反例 (BAD): `expect(mockPayment.process).toHaveBeenCalledWith(cart.total)` — 驗 internal
  call，refactor payment flow 即破。
- 正例 (GOOD): `const result = await checkout(cart, payment); expect(result.status).toBe("confirmed")` —
  驗 observable outcome，refactor 內部 payment service 不影響此測試。

### 1.2 Vertical slicing — 一輪一個 test (no horizontal slicing)

**原則**: 嚴禁先寫一堆 test 再寫一堆 impl（horizontal slicing）。產出的會是「想像出來的
test」，驗 shape 不驗 behavior。**正解是 tracer bullet：一個 test → 一個 impl → 下一輪由
上一輪學到的東西決定**。

**baransu 上下文映射**:
- §7.2 的四工項（紅燈測試 → 確認紅燈 → 綠燈實作 → 確認綠燈）本身就是一個 vertical slice。
- `/execute` 的 TDAID 循環是 **per-task** 的；如果一個 task 有多個 acceptance criteria
  (AC)，`/analyze` 的 design 層應該已經把 cardinality 拆好。`impl-agent` 不重新拆分，照
  design.md 寫；review-agent 在 Phase 3 抓「diff 內是否一次新增 ≥ 2 個 test function 而
  沒有對應拆 cycle」這條 process advisory。
- 反例 (BAD): 一個 task 包含「新增 endpoint A、B、C」，impl-agent 一口氣寫 3 個 test 跑紅、
  再寫 3 個 impl 跑綠 — 中間沒有 tracer bullet 學到任何東西。
- 正例 (GOOD): 一個 task 對映 design.md 一個 AC，impl-agent 寫一個 test、跑紅、寫 impl、
  跑綠；下一個 AC 由下一輪 TDAID 處理。

### 1.3 Mock 只在系統邊界 (mock-at-boundaries)

**原則**: 只在系統邊界 mock — 外部 API（payment、email）、time、randomness、檔案系統
（有時候）。**不要 mock 自己擁有的 class / 內部 collaborator / module**。

**baransu 上下文映射**:
- review-agent 在 Phase 3 的 test_quality 觀察維度中會 grep 測試 body：是否含
  `jest.mock(...)` 對 project-internal 路徑、`unittest.mock.patch(...)` 對 project-internal
  path、或 `expect(internal.method).toHaveBeenCalled` 類斷言。命中即 advisory「mock 內部
  協作者，建議改透過 public interface 驗結果」。
- 反例 (BAD): `jest.mock('./userRepository')` — mock 自己擁有的內部模組。
- 正例 (GOOD): `jest.mock('stripe')` — mock 外部 SDK；`jest.useFakeTimers()` — mock 系統
  邊界（time）。

### 1.4 Refactor only when GREEN

**原則**: 紅燈時不准 refactor 結構。先把測試弄綠，再考慮重構。

**baransu 上下文映射**:
- §7.2 工項 3（撰寫綠燈實作）的規則「寫足以讓紅燈測試通過的最小實作、不添加測試未要求
  的內容」直接落實此原則。
- `/execute` `impl-agent.md` 通用原則 §4 已強制：「Refactor 最多執行一次；未收到
  `refactor_mode: true` 時不主動 Refactor」。Refactor 由 review-agent 在 Phase 3 評估後
  附 `refactor_mode: true` 觸發第二次 dispatch。
- 反例 (BAD): RED 階段同時改 test 與既有 impl 結構，混淆失敗來源。
- 正例 (GOOD): RED 階段只改 test 檔；GREEN 階段只寫足以通過的 impl；refactor 由
  `review-agent` 評估 quality tier 後再啟動。

---

## 2. Interface 設計：可測試性的前置條件

好的 interface 讓測試自然，差的 interface 讓測試痛苦。三條 interface design 原則：

### 2.1 Accept dependencies, don't create them

```
GOOD: function processOrder(order, paymentGateway) { ... }
BAD:  function processOrder(order) { const gateway = new StripeGateway(); ... }
```

依賴注入讓 system boundary mock 自然；內部建構讓測試只能用 monkey-patch。

### 2.2 Return results, don't produce side effects

```
GOOD: function calculateDiscount(cart): Discount { ... }
BAD:  function applyDiscount(cart): void { cart.total -= discount; }
```

返回值可斷言；副作用必須額外設計觀測點。

### 2.3 Small surface area

方法越少、參數越少，測試越簡單。

---

## 3. Deep modules — 小介面包深邏輯

來自 *A Philosophy of Software Design*（Ousterhout）。

```
Deep module    = Small interface + Deep implementation   ← 偏好
Shallow module = Large interface + Thin implementation   ← 避免
```

設計時自問：
- 能減少方法數量嗎？
- 能簡化參數嗎？
- 能把更多複雜度藏進實作裡嗎？

deep module 的測試焦點集中在 public interface 行為；shallow module 反之，每個 thin
方法都得個別測，測試表面積爆炸。

---

## 4. SDK-style API — 可 mock 性的副效果

在系統邊界（外部 API integration）偏好 SDK-style 介面，避免 generic fetcher：

```
GOOD: const api = {
        getUser: (id) => fetch(`/users/${id}`),
        getOrders: (userId) => fetch(`/users/${userId}/orders`),
        createOrder: (data) => fetch('/orders', {...}),
      };
BAD:  const api = {
        fetch: (endpoint, options) => fetch(endpoint, options),
      };
```

SDK-style 的好處：
- 每個 mock 回單一形狀 — 不需要 conditional 邏輯。
- 測試 setup 看出該 test 觸碰哪些 endpoint。
- 可 per-endpoint type-safe。

---

## 5. Refactor candidates — 綠燈後再做

GREEN 確認後才看下面的清單：

- **Duplication** → 抽 function / class
- **Long methods** → 拆成 private helpers（測試仍打 public interface）
- **Shallow modules** → 合併或加深
- **Feature envy** → 把邏輯搬到 data 所在處
- **Primitive obsession** → 引入 value object
- **Existing code 被新 code 揭露的問題** → 留下記錄、決定是否本輪處理

每次 refactor 後跑一次測試，確保仍綠。

---

## 6. 反模式速查（Anti-patterns）

| 訊號 | 為什麼壞 |
|---|---|
| Test 名稱寫 "X calls Y" | 描述 HOW 不描述 WHAT；refactor 即破。 |
| Test mock 自己的 module / class | 偶合 implementation 細節；不驗 behavior。 |
| 一輪寫多個 test 再寫多個 impl | Horizontal slicing；產出想像出來的 test。 |
| Test pass 只是因為 spy 計數對 | 驗 internal call；不驗 observable outcome。 |
| Test 透過 `db.query(...)` 直接驗結果 | 跳 interface；不寫 retrieve API 反而繞過去查 DB。 |
| RED 階段同時 refactor 既有 impl | 混淆失敗來源；違反「refactor only when GREEN」。 |

跨技能行為反模式（含紅綠紀律條目）見 `../../rules/anti-patterns.md`；本表僅收 test 設計層反模式。

---

## 7. 直接實作時的紅綠閘（文件紀律）

小任務不經 `/execute` 管線、由主 session 直接實作時（例如 `/think` 核可方案或 `/hunt`
診斷收斂後的單一變更點），紅綠閘以**文件紀律（discipline-suggested）**形式運作：沒有
orchestrator 替你把關，實作者依本節自建紅綠 task list、先紅後綠、紅燈確認後才寫實作。
若核可方案已有上游工作日誌（`.claude/think/*.html`），實作期間的規範外決策依
`output-journal.md` 契約追記至該日誌的「執行日誌」節。

### 7.1 先分類：TDD 或 cosmetic

cosmetic = 變更對 runtime 行為無語義影響，僅限四類：

- comment edits（註解修改）
- dead import removal（dead import 移除）
- identifier rename with no behavior change（identifier rename 無行為變更）
- pure formatting（純格式調整）

不確定時一律走 TDD path。分類一旦做出即為最終，不在執行中途重新分類。
cosmetic path 直接實作、不寫測試；TDD path 進入 §7.2。

### 7.2 自建紅綠 task list（四工項）

執行前先建立完整 task list，讓完成準則自始可見。四工項本身就是一個 vertical slice（§1.2）：

1. 撰寫紅燈測試 — 只針對新行為撰寫（§1.1）；不為既有行為寫測試
2. 確認紅燈 — 執行測試，預期失敗
3. 撰寫綠燈實作 — 寫足以讓紅燈測試通過的最小實作，不添加測試未要求的內容（§1.4）
4. 確認綠燈 — 執行測試，全數通過且無回歸

順序不可換：紅燈未確認前不得進入實作；綠燈階段不得修改測試（測試即 spec）。

### 7.3 閘門判定

**確認紅燈**：

| 結果 | 行動 |
|---|---|
| 測試失敗 | 紅燈確認，進入綠燈實作。 |
| 測試通過 | 停。測試驗的是既有行為、不是新行為；改寫測試後重新確認紅燈。 |
| compile error | 測試本身語法有誤；修正測試後從工項 1 重來，不算入綠燈重試次數。 |

**確認綠燈**：

| 結果 | 行動 |
|---|---|
| 全數通過、無回歸 | 綠燈確認，完成。 |
| 測試失敗（第 1 次） | 修改實作後直接重跑。 |
| 測試失敗（第 2 次） | 停。方向有疑慮時回 `/think` 重新對焦後再試。 |
| compile error | 修正後重跑；不算入重試次數。 |

在 `/execute` 的 TDAID 管線中，compile error 與 `failure_count` 的計數權威規則見 `plugins/baransu/skills/execute/SKILL.md`；本檔僅引用、不複製規則內文。

### 7.4 Per-cycle 自檢清單

每輪 RED→GREEN 結束時，自問：

```
[ ] Test 描述 behavior、不描述 implementation
[ ] Test 只用 public interface
[ ] Test 在內部 refactor 後仍會 pass
[ ] Code 是 minimal、夠通過此 test 而已
[ ] 沒添加未被任何 test 要求的功能
```

---

## 8. baransu-specific 觸發點記錄

本檔被以下觸發點引用：

| 觸發點 | 引用位置 | 引用句 |
|---|---|---|
| `/execute` impl-agent | `plugins/baransu/agents/impl-agent.md` 通用原則 §1 Red gate 之前 | 「撰寫測試之前請閱讀 `plugins/baransu/skills/_shared/tdd.md`。」 |
| `/execute` review-agent | `plugins/baransu/agents/review-agent.md` 通用原則 §3 之前 | 「Review 之前請閱讀 `plugins/baransu/skills/_shared/tdd.md`，並依其原則檢查 test 品質。」 |
| `/think` 小任務改道 | `plugins/baransu/skills/think/SKILL.md` Stage G 下游分流 | 小任務改道至本檔 §7：由主 session 依文件紀律自建紅綠 task list 直接實作。 |
| `/hunt` 修復改道 | `plugins/baransu/skills/hunt/SKILL.md` 修復建議分流 | 單一變更點修復改道至本檔 §7 的直接實作紀律。 |

review-agent 在 Phase 3 除依本檔原則檢查 test 品質外，必須回報 green_proof 四欄位（見
`plugins/baransu/agents/review-agent.md` 通用原則 §3 與 5-tier 必填矩陣）。

---

## 9. 原文章節對照表

對外 cross-reference 時引用本檔章節 + mattpocock 原文章節：

| 本檔章節 | mattpocock 原文 |
|---|---|
| §1.1 test-verifies-behavior | SKILL.md "Philosophy" 段、tests.md 全文 |
| §1.2 vertical slicing | SKILL.md "Anti-Pattern: Horizontal Slices" |
| §1.3 mock-at-boundaries | mocking.md |
| §1.4 refactor only when GREEN | SKILL.md "Refactor" 段 |
| §2 Interface design | interface-design.md |
| §3 Deep modules | deep-modules.md |
| §5 Refactor candidates | refactoring.md |
