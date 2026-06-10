# Acceptance spec for tdd-trigger dogfood (REVIEWER-ONLY)

> **DO NOT PASTE TO THE MODEL**：本檔列出期待行為與驗收條件，**內含答案**。
> 給 model 看到等於告訴答案；只有人類 reviewer / `check_acceptance.sh` 該讀本檔。
> 給 model 的 prompt 是 `prompt.md`，不是本檔。

---

## Purpose

驗證存活的兩觸發點（`/execute` 的 `impl-agent`、`/execute` 的 `review-agent`）真的引用了
`plugins/baransu/skills/_shared/tdd.md`，並在 mattpocock 違反誘惑下仍寫出符合原則的 test。

## How to run

1. 把 `prompt.md` 整檔作為 task 交給 `/baransu:execute` 的 impl-agent
   （或主 session 依 `_shared/tdd.md` §7 直接實作）。
2. 等 RED→GREEN→review 跑完後，產出 test 檔案。
3. 對該 test 檔案跑 `bash check_acceptance.sh <test_file_path> [<review_report_path>]`。

## 期待 mattpocock-aligned 行為

讀過 `_shared/tdd.md` 的 model（無論主 session 還是 impl-agent）應該抗住兩條 lure：

- **抗 lure 1（mock-internal）**：應該 mock `paymentGateway`（系統邊界、外部 SDK），但
  **不該** mock 內部 `XService`。應該透過 public interface（呼叫 `processOrder` + assert
  回傳值）驗庫存邏輯。
- **抗 lure 2（HOW-style 命名）**：test 名稱應描述行為，例如
  `test_processOrder_returns_rejected_when_stock_insufficient` 或
  `test_user_gets_out_of_stock_response_for_insufficient_inventory`。**不該**寫成
  `test_processOrder_calls_validateInventory`（這描述的是 implementation）。

## Acceptance（由 check_acceptance.sh 自動驗）

- **(b1) test 名稱描述行為**：grep test function/case 名稱不含 `calls_`/`uses_`/
  `invokes_`（underscore 形式）也不含 `calls`/`uses`/`invokes`（sentence 形式，case-insensitive）
  等 HOW-style pattern。
- **(b2) test body 不 mock 內部協作者**：grep test body 不含對 `XService` 的 mock /
  patch / spy / class-extension fake，也不含 lowercase 實例 spy。應透過 public interface
  驗結果。
- **(c) review-agent green_proof 4 欄位齊備**：review-agent 回報結構含 `test_command`
  非 "n/a"、`exit_code = 0`、`output_tail` 非空、`tests_correspondence` 非空且引用
  task spec 中已存在的 test 路徑/名稱片段。

## Informational（記錄不阻擋）

- **(a)** impl-agent（或主 session 直接實作）在撰寫紅燈測試前的回應是否出現對
  `_shared/tdd.md` 某條原則的引用文字。記錄到 dogfood log 供觀察 verbosity 是否需
  調整、不作為 acceptance。
