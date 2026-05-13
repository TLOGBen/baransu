---
schema-id: one-pager
class-prefix: kami-
langs: [zh, en]
templates:
  zh: design-cores/one-pager.html
  en: design-cores/one-pager-en.html
body-sections:
  - id: title
    name: 標題
    required: true
    note: 主敘述句，一行內收尾；下接一行 subline
  - id: hero-metric
    name: 核心數字 1
    required: true
    note: 單一巨型數字 + 單位 + 短說明；視覺重心
  - id: context
    name: 上下文
    required: true
    note: 2-3 段、共約 120-180 字，說明來源、假設與限制
  - id: cta
    name: 行動呼籲
    required: true
    note: 一句 imperative + 聯絡管道；底部置中
image-requirements:
  position: "center 35%"   # 若含人像 <img>，採 rule of thirds 對齊
  applies-to: [optional]
editorial-requirements:
  dropcap: false           # One-Pager 強調掃讀，不用 dropcap
  curly: true              # U+201C / U+201D
  widow-orphan: true
  text-wrap: pretty
  page: A4                 # 單頁 print 強制
---

# One-Pager schema — 紙 preset

適用場景：投資人 one-pager、產品 announcement、團隊 status snapshot。

版面骨架：A4 直式單頁，padding ~24mm。頂部標題區佔 ~25%，
中段巨型核心數字佔 ~35%，下半上下文 + 行動呼籲。

必填區塊：見 body-sections（title / hero-metric / context / cta）。

SVG 圖表角色：可選 1 個 sparkline 或 mini-bar 輔助核心數字；不強制。
