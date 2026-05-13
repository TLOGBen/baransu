---
schema-id: equity-report
class-prefix: kami-
langs: [zh, en]
templates:
  zh: design-cores/equity-report.html
  en: design-cores/equity-report-en.html
body-sections:
  - id: thesis
    name: 投資論點
    required: true
    note: 2-3 段，首段 dropcap；陳述買賣方向 + 核心邏輯 + 持有期間
  - id: valuation
    name: 估值
    required: true
    note: 多法併呈（DCF / 倍數 / 同業）→ 收斂目標價區間；必含上下限
  - id: risk
    name: 風險
    required: true
    note: 系統性 / 公司特有 / 流動性 三類；每類 1-2 條，配對應減損情境
figure-requirements:
  type: quadrant
  axes: [機會, 風險]   # x = 機會強度，y = 風險程度
  focal: top-left      # 高機會低風險 = focal
  count: 1             # 至少 1 個 SVG quadrant figure
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: true            # 投資論點首段必用 dropcap
  curly: true              # U+201C / U+201D
  widow-orphan: true
  text-wrap: pretty
---

# Equity-Report schema — 紙 preset

適用場景：賣方研究 initiation / update、買方內部 pitch memo、年度檢視。

版面骨架：A4 直式，主敘述靠左對齊；估值區走兩欄表格，
SVG quadrant 圖嵌於估值與風險之間（角度：機會 × 風險），
quadrant focal 落於 top-left「高機會低風險」象限。

必填區塊：見 body-sections（thesis / valuation / risk）。

SVG 圖表角色：強制 1 個 quadrant 圖；採 Kami chevron marker（`M2 1 L8 5 L2 9`），
2-tier node-width whitelist {128, 144}，單一 focal callout rect，無 `<polygon>`。
