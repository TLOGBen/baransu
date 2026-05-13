---
schema-id: one-pager
class-prefix: google-
langs: [zh, en]
templates:
  zh: design-cores/one-pager.html
  en: design-cores/one-pager-en.html
body-sections:
  - id: title
    name: 標題
    required: true
    note: Roboto Display medium，一行收尾
  - id: hero-metric
    name: 核心數字 1
    required: true
    note: 單一大字，M3 primary container 包裹
  - id: context
    name: 上下文
    required: true
    note: 2-3 段、120-180 字；surface tone
  - id: cta
    name: 行動呼籲
    required: true
    note: filled tonal button + 聯絡聯結；底部
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: false           # M3 強調 ratio + 動作層級，不使用 dropcap
  curly: true
  widow-orphan: true
  text-wrap: pretty
  page: A4
---

# One-Pager schema — google-design preset

適用場景：產品 launch one-pager、團隊 OKR snapshot、Material 風格 announcement。

版面骨架：A4 直式單頁，padding ~24mm。Title chip + hero-metric card + context surface +
CTA filled button 四層 Material 元件堆疊。

必填區塊：見 body-sections（title / hero-metric / context / cta）。

SVG 圖表角色：可選 1 個 sparkline，配合 M3 secondary color。
