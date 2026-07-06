# Mini cases — 帳單狀態機測案集（domain dry-run fixture）

> Fixture for the /review domain-grounding semantic dry run. 7 cases; TC-05 and
> TC-06 carry deliberately illegal initial states (unreachable per mini-spec.md).

| 案號 | 初始狀態（建置方式） | 事件 | 預期結果 |
|---|---|---|---|
| TC-01 | 待付款（新建帳單） | 付款成功 | 狀態變為 已付款 |
| TC-02 | 待付款（新建帳單，到期日設為昨日） | 逾期日到 | 狀態變為 逾期 |
| TC-03 | 逾期（由 TC-02 路徑建置） | 付款成功 | 狀態變為 已付款 |
| TC-04 | 逾期（逾期天數 190，主管已核准） | 轉呆帳 | 狀態變為 呆帳 |
| TC-05 | 呆帳（新建帳單後直接 UPDATE 狀態為 呆帳，逾期天數 0，無逾期紀錄） | 付款成功 | 系統拒絕，狀態維持 呆帳 |
| TC-06 | 逾期（直接 INSERT 狀態為 逾期，但到期日設為下個月） | 付款成功 | 狀態變為 已付款 |
| TC-07 | 待付款（到期日設為今日，當日付款） | 付款成功 | 狀態變為 已付款 |

備註：TC-05 之建置為「待付款 → 呆帳」直跳（未經 逾期）；TC-06 之「逾期但
到期日未到」不滿足 2.2 的前置條件。兩者皆需手動改 DB 才能建置。
