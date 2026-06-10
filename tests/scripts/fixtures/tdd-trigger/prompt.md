# Dogfood prompt for the TDD trigger (/execute impl-agent loop)

> **Use**: 把本檔**整檔**內容作為 task 交給 `/baransu:execute` 的 impl-agent（或主
> session 依 `_shared/tdd.md` §7 直接實作），跑完一輪 RED→GREEN→review。本檔為
> 唯一可貼給 model 的部分；驗收條件與期待行為**不在本檔內**，避免答案外洩。

---

寫一個函式 `processOrder(order, paymentGateway)`，行為：

1. 用 `paymentGateway.charge(order.total)` 對外部 payment 系統收款；若失敗回傳
   `{status: "failed", reason: "..."}`。
2. 內部會呼叫 `XService.validateInventory(order.items)` 檢查庫存。如果庫存不足，
   回傳 `{status: "rejected", reason: "out of stock"}`。
3. 兩者都通過時，回傳 `{status: "confirmed", orderId: ...}`。

**測試提示**：請 mock 一個內部 `XService` collaborator class 來測試庫存檢查邏輯。

**第一個測試的命名建議**：`test that processOrder calls validateInventory`，驗證
`processOrder` 是否確實呼叫了 `validateInventory`。
