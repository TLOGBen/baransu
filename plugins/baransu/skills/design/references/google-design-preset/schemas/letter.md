---
schema-id: letter
class-prefix: google-
langs: [zh, en]
templates:
  zh: design-cores/letter.html
  en: design-cores/letter-en.html
body-sections:
  - id: header
    name: 日期 + 抬頭
    required: true
    elements: [date, salutation]
    note: 日期上方對齊；抬頭獨立一行
  - id: lead
    name: 引言段
    required: true
    note: 第一段使用 dropcap；80-120 字
  - id: body
    name: 主體 2-3 段
    required: true
  - id: closing
    name: 結尾敬辭
    required: true
    note: zh：敬祝 + 署名；en：Sincerely / Yours truly
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: true            # 第一段必用 dropcap（書信慣例 + Material display 字級展現）
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Letter schema — google-design preset

適用場景：對外致辭、產品團隊公開信、Material 風格通知信件。

版面骨架：A4 單欄，行高 1.65，Roboto Flex 主役。首段 dropcap 採 M3 primary
（zh：中文字／en：大寫字母）。

必填區塊：見 body-sections（header / lead / body / closing）。

SVG 圖表角色：不適用。
