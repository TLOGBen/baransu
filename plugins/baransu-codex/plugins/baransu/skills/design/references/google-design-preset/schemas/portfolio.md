---
schema-id: portfolio
class-prefix: google-
langs: [zh, en]
templates:
  zh: design-cores/portfolio.html
  en: design-cores/portfolio-en.html
body-sections:
  - id: cover
    name: 封面 + about
    required: true
    elements: [hero-portrait, name, tagline, about-paragraph]
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
  dropcap: true            # about-paragraph 首段套 Material display-medium 風格 dropcap
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Portfolio schema — google-design preset

適用場景：產品設計師作品集、UX case study 集合。

版面骨架：Material 3 grid，作品為 elevation-1 cards；
封面 hero 採 large-text + portrait。

必填區塊：見 body-sections。

SVG 圖表角色：case study 內常含 user-flow / journey-map。
