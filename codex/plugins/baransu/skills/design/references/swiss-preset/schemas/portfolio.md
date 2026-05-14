---
schema-id: portfolio
class-prefix: swiss-
langs: [zh, en]
templates:
  zh: design-cores/portfolio.html
  en: design-cores/portfolio-en.html
body-sections:
  - id: cover
    name: 封面 + about
    required: true
    elements: [hero-portrait, name, tagline, about-paragraph]
    note: Swiss 不使用 dropcap，但 about-paragraph 仍應顯眼（17px lead）
  - id: works
    name: 作品 grid
    required: true
    items: 4-6
    schema-per-item:
      - thumbnail
      - title
      - year
      - role
      - one-line-summary
  - id: contact
    name: 聯絡
    required: true
image-requirements:
  position: "center 35%"
  shape: portrait-3x4
  applies-to: [cover.hero-portrait, works.*.thumbnail]
editorial-requirements:
  dropcap: false           # Swiss 風格不用 dropcap（靠 lead-paragraph 而非首字裝飾）
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Portfolio schema — swiss preset

適用場景：設計工作室、攝影、品牌作品集。

版面骨架：嚴格 12 欄 grid；作品縮圖 8×3 cards。

必填區塊：見 body-sections。

SVG 圖表角色：流程圖、grid overlay 可選。
