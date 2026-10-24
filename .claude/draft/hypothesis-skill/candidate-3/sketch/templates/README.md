---
# Reader interface: scripts/hypothesis-status.py parses only this frontmatter and the 規則 table.
schema: 1
area: approval-withdraw
claim: "撤回和核准同時按，不能付錢給已撤回的單"
status: disproved            # proved | disproved | draft | unformalizable
revision: 4                  # +1 on every swap; optimistic-concurrency check at step 8
trigger: H1                  # H1–H8 row, or none
origin: user                 # user | hunt:<case id> | review | maintain
sources:                     # one entry per source; pair = two entries with roles rules / behaviour
  - role: subject            # subject | rules | behaviour
    kind: code
    covers: [src/approval/service.ts, src/approval/payment.ts]
    commit: a1b2c3d
  # - role: rules
  #   kind: document
  #   path: docs/SA-訂單簽核-v2.pdf
  #   version: "v2"
  #   sha256: "…"
  #   snapshot: sources/sa-v2.md
  #   snapshot_sha256: "…"
  #   converter: "markitdown 0.x"
tool:
  name: tlc                  # a file name under references/tools/
  version: "TLC2 2.19"
  cwd: model
  command: java -cp "$TLA2TOOLS" tlc2.TLC -metadir "$HYP_TMP" -config check.cfg Approval.tla
  bounds: "金額 {500, 2000, 9000}；最多送出 3 次；角色 主管、財務"
  explored: 425 distinct states
gates:                       # each: pass | fail | not-run
  true_to_source: pass
  seen_failing: pass
  seen_succeeding: pass
  scope_stated: pass
  findings_sorted: pass
---

# {claim}

{one plain sentence: what this hypothesis promises, and the harm if it breaks}

## 規則

| id | 規則（白話） | 類型 | 引用 | 結果 |
|---|---|---|---|---|
| R1 | 付了多少錢，每個該簽的人都核准過這個金額 | 不能發生 | `service.ts:121-140` | violated → Bug 1 |
| G1 | 2000 元的單，主管和財務都簽過後會付款 | 要做得到 | `service.ts:121`、`payment.ts:30` | holds |

## 範圍與假設

{bounds in plain words; assumptions; what the model leaves out}

## 對應表

| 模型元素 | 規則表項目 | 引用 |
|---|---|---|
| `WithdrawRead` | 撤回：讀狀態並檢查 | `service.ts:88` |

## 嚴格檢查紀錄

| 關卡 | 怎麼做的 | 結果 |
|---|---|---|
| 看過它失敗 | R2：把 `service.ts:95` 的狀態檢查拿掉（mutate-R2.cfg） | 抓到 |
| 看過它成功 | G1 可達；拿掉「財務核准」後 G1 不可達（reach-G1-*.cfg） | 符合 |

## 發現

### Bug 1 — {harm in one sentence}

{the 劇本: numbered steps in the source's words, each with its citation; for documents 矛盾/缺漏/精化失敗 with quoted passages}

## 要問的問題

| # | 原文與位置 | 兩種讀法 | 要問誰 |
|---|---|---|---|

## 沒有形式化的部分

| 哪一段 | 原因 | 具體情況 | 要什麼才能形式化／現在改走 |
|---|---|---|---|
| `mailer.ts:12` 寄通知信 | 無法建模 | 外部郵件服務 | 有可控的假郵件服務／紅綠測試 |

## 怎麼重跑

{each cfg or harness command, what result each should give: check, mutate-*, reach-*}

## 維護紀錄

| 日期 | 同步點 從 → 到 | 結果 | 摘要 |
|---|---|---|---|
