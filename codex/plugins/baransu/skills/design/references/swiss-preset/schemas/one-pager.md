---
schema-id: one-pager
class-prefix: swiss-
langs: [zh, en]
templates:
  zh: design-cores/one-pager.html
  en: design-cores/one-pager-en.html
body-sections:
  - id: title
    name: 標題
    required: true
    note: flush-left，sans-serif，一行收尾
  - id: hero-metric
    name: 核心數字 1
    required: true
    note: 單一大字，IKB accent；不裝飾
  - id: context
    name: 上下文
    required: true
    note: 2-3 段、120-180 字；grid-aligned
  - id: cta
    name: 行動呼籲
    required: true
    note: 一句 imperative + 聯絡資訊；底部 flush-left
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: false           # Swiss 偏好均一字級，無 dropcap
  curly: true
  widow-orphan: true
  text-wrap: pretty
  page: A4
---

# One-Pager schema — swiss preset

適用場景：產品 spec sheet、研究摘要、會議 brief、Swiss 風格極簡 announcement。

版面骨架：A4 直式單頁，grid 12 欄，padding ~24mm。標題上 1/4、
hero-metric 中 1/3、context + CTA 下 1/2。

必填區塊：見 body-sections（title / hero-metric / context / cta）。

SVG 圖表角色：可選 1 個 bar/line；不強制。
