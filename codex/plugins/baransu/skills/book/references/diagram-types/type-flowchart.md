---
name: flowchart
status: ref-only
example: null
---

# Flowchart

**Best for**: 決策邏輯（decision logic）、演算法步驟（algorithms）、面向使用者的分支流程（"Should I…?"）、onboarding routing、support-triage 分流樹。

## Layout conventions

- Shape 帶 type，**顏色不帶 type**：oval（`rx=20`）= start / end；rect（`rx=6`）= step / action；diamond = decision（≤3 個出口）；small filled `--ink` dot（`r=4`）= merge point（分支匯流點）。
- 主流方向 top→down 固定；從 diamond 出去時 Yes 走右、No 走下為慣例，但**每一條 outgoing arrow 都要 label**，不可省略。
- `--brand` 只用在 happy path **或**單一最關鍵 decision 二擇一，不可同時用在多個 decision；其餘節點走 `--ink` / `--color-muted` 描邊與 `--parchment` 底。
- 若兩條 arrow 必須交叉，在其中一條畫一個 small arc jump 標示穿越，避免讀者誤判為連線。

## Anti-patterns

- 用 fill color 區分 node type（例如所有 action 紅、所有 decision 藍）。
  - *Why fails*：Kami 只給三個語意色（`--brand` / `--brand-tint` / `--color-muted`），fill 拿來標 type 會跟 focal 語意衝突，且色盲讀者無法分辨；type 區分本就是 shape 的工作，shape 已做完的事不需顏色再做一次。
- Decision diamond 開出 4 個以上 exit。
  - *Why fails*：人眼在 diamond 上能快速處理的分支上限是 3；4 個以上會逼讀者把 diamond 當 dispatch table 讀，違背 flowchart 「視覺化判斷」的目的，應重構為 nested diamonds。
- 未 label 的 decision 分支。
  - *Why fails*：flowchart 的本質是「在這一步決定了什麼條件」，少了 label 就只剩拓樸結構，讀者必須回去看 prose 才能理解，圖等同失效。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: flowchart`。
