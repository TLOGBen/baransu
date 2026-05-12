---
schema-id: equity-report
class-prefix: google-
langs: [zh, en]
templates:
  zh: design-cores/equity-report.html
  en: design-cores/equity-report-en.html
body-sections:
  - id: thesis
    name: 投資論點
    required: true
    note: 2-3 段；Material elevation surface 包覆
  - id: valuation
    name: 估值
    required: true
    note: 多法併呈 → 目標價區間；以 outlined surface 呈現比較表
  - id: risk
    name: 風險
    required: true
    note: 系統性 / 公司特有 / 流動性；chip 樣式
figure-requirements:
  type: quadrant
  axes: [機會, 風險]
  focal: top-left
  count: 1
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: false
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Equity-Report schema — Google-Design (Material 3) preset

適用場景：投研報告（Material surface + elevation tone）。

版面骨架：A4 直式；論點 / 估值 / 風險各包在 rounded surface 卡片內，
SVG quadrant 圖嵌於估值與風險之間，圓角包覆。

必填區塊：見 body-sections（thesis / valuation / risk）。

SVG 圖表角色：強制 1 個 quadrant 圖；採 Kami chevron marker，
2-tier node-width whitelist {128, 144}，無 `<polygon>`。
