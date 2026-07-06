# Dry-run result — domain grounding semantic walk (2026-07-06)

> Manual semantic check of the /review domain-grounding pipeline (Stage 1.5 +
> domain-reviewer mission) against this fixture. No skill was invoked; the flow
> was walked by hand to verify the pipeline semantics land: F1 unnatural-scenario
> naming and F2 coverage-gap enumeration. This is the E2E table row-2 landing at
> fixture level (TASK-release-01).

## 1. Stage 1.5 — trigger + transition table

Trigger check: target (mini-cases.md) is a test-case set asserting bill states,
transitions, and preconditions → claims business behavior → Stage 1.5 triggers.

Source ranking: mini-spec.md is the only source (spec outranks code under test;
no code under test exists in this fixture) → all rows `verified`.

| Row | 現態 | 事件 | 前置條件 | 次態 | Source |
|---|---|---|---|---|---|
| R1 | 待付款 | 付款成功 | — | 已付款 | (verified: mini-spec.md §2.1) |
| R2 | 待付款 | 逾期日到 | 到期日已過且未付款 | 逾期 | (verified: mini-spec.md §2.2) |
| R3 | 待付款 | 取消帳單 | 尚未收到付款 | 已取消 | (verified: mini-spec.md §2.3) |
| R4 | 逾期 | 付款成功 | — | 已付款 | (verified: mini-spec.md §2.4) |
| R5 | 逾期 | 轉呆帳 | 逾期天數 ≥ 180 且經主管核准 | 呆帳 | (verified: mini-spec.md §2.5) |

Global invariant G1: 呆帳必經逾期，不存在 待付款→呆帳 直達路徑
(verified: mini-spec.md §3). Entry state: 新建帳單 = 待付款 (verified: §1).

## 2. F1 — unnatural scenarios (business-state reachability)

Exactly the 2 deliberately illegal cases were caught, no false positives:

1. **TC-05**（mini-cases.md 表列 TC-05）— 初始狀態「呆帳、逾期天數 0、無逾期
   紀錄」。呆帳唯一合法入徑為 R5（現態必須是 逾期，且逾期天數 ≥ 180）；G1 亦
   明文排除 待付款→呆帳 直跳。非自然情境——正常流程到不了此初始狀態，需手動改
   DB 才能建置。由人決定去留：本案驗證「呆帳帳單拒收付款」，可能是蓄意的防禦
   性測試。Citations: R5 + G1；mini-cases.md TC-05。
2. **TC-06**（mini-cases.md 表列 TC-06）— 初始狀態「逾期、但到期日在未來」。
   逾期唯一合法入徑為 R2，前置條件「到期日已過」被違反。非自然情境——正常流程
   到不了此初始狀態，需手動改 DB 才能建置。由人決定去留。Citations: R2；
   mini-cases.md TC-06。

Legal cases confirmed legal: TC-01→R1、TC-02→R2、TC-03→R4、TC-04→R5（190 ≥ 180
且已核准，前置條件滿足）、TC-07→R1（到期日當日邊界，仍屬 R1）。

## 3. F2 — coverage gaps (legal combinations vs case set)

Enumeration of legal state × event rows against the 7 cases:

| Row | Covered by | Gap? |
|---|---|---|
| R1 | TC-01, TC-07 | — |
| R2 | TC-02 | — |
| R3 | — | **缺口** |
| R4 | TC-03（TC-06 初始狀態非法，不計入覆蓋） | — |
| R5 | TC-04（僅前置條件滿足側） | 前置條件拒絕側缺口 |

Gaps found (≥1 required; 2 found):

1. **R3 未覆蓋**：合法組合「待付款 × 取消帳單 → 已取消」無任何測案。
   Citation: R3 (verified: mini-spec.md §2.3)。
2. **R5 前置條件拒絕側未覆蓋**：TC-04 只驗證 逾期天數 ≥ 180 的成功轉列；
   「逾期天數 < 180 時 轉呆帳 應被拒絕」無測案。
   Citation: R5 (verified: mini-spec.md §2.5)。

Balance note (per domain-reviewer principles): both gaps propose bounded new
work (one case each), harm of not fixing is an unguarded legal transition /
precondition boundary, and both serve this review's goal (verify the case set
covers the spec's state machine) — reported as findings, not downgraded.

## 4. Outcome

- Transition table materialized before dispatch: yes (5 rows + G1, all verified)
- Unnatural scenarios named: 2/2 (TC-05, TC-06) — matches the fixture's planted
  illegal cases exactly
- Coverage gaps found: 2 (≥1 required)
- Pipeline semantics F1（非自然情境點名）+ F2（覆蓋缺口清單）both land: PASS
