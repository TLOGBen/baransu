---
schema-id: portfolio
class-prefix: kami-
langs: [zh, en]
templates:
  zh: design-cores/portfolio.html
  en: design-cores/portfolio-en.html
body-sections:
  - id: cover
    name: 封面 + about
    required: true
    elements: [hero-portrait, name, tagline, about-paragraph]
    note: about-paragraph 首段使用 dropcap
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
    elements: [email, phone, location, social-links]
image-requirements:
  position: "center 35%"   # 封面人像 + 作品 thumbnail 皆採 rule of thirds
  shape: portrait-3x4      # 封面；作品 thumbnail 為 4x3 landscape
  applies-to: [cover.hero-portrait, works.*.thumbnail]
editorial-requirements:
  dropcap: true            # 套用於 about-paragraph 首段
  curly: true              # U+201C / U+201D
  widow-orphan: true
  text-wrap: pretty
---

# Portfolio schema — 紙 preset

適用場景：個人作品集、設計師 / 攝影師 / 工作室自介。

版面骨架：兩欄 grid，作品區域為 2×2 至 3×2 cards；
封面採大圖人像 + 短 about；聯絡置於頁尾。

必填區塊：見 body-sections（cover / works / contact）。

SVG 圖表角色：作品內可含 process 圖、time-line；不強制。
