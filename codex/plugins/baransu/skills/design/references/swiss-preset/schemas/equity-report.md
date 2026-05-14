---
schema-id: equity-report
class-prefix: swiss-
langs: [zh, en]
templates:
  zh: design-cores/equity-report.html
  en: design-cores/equity-report-en.html
body-sections:
  - id: thesis
    name: 投資論點
    required: true
    note: 2-3 段；無 dropcap（Swiss 走 grid 紀律，非編輯主役）
  - id: valuation
    name: 估值
    required: true
    note: 多法併呈 → 目標價區間（含上下限）
  - id: risk
    name: 風險
    required: true
    note: 系統性 / 公司特有 / 流動性
figure-requirements:
  type: quadrant
  axes: [機會, 風險]
  focal: top-left
  count: 1
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: false           # Swiss 不用 dropcap；class 仍宣告以通過 editorial-sanity gate
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Equity-Report schema — Swiss preset

適用場景：賣方研究 / 買方 pitch / 投研內部 memo（Swiss grid 風格）。

版面骨架：A4 直式，12-column grid，主敘述靠左；估值區走 2 欄資訊區塊，
SVG quadrant 圖跨 8 欄置中，focal 落 top-left「高機會低風險」象限。

必填區塊：見 body-sections（thesis / valuation / risk）。

SVG 圖表角色：強制 1 個 quadrant 圖；採 Kami chevron marker，
2-tier node-width whitelist {128, 144}，單一 focal callout，無 `<polygon>`。
