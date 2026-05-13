---
schema-id: letter
class-prefix: swiss-
langs: [zh, en]
templates:
  zh: design-cores/letter.html
  en: design-cores/letter-en.html
body-sections:
  - id: header
    name: 日期 + 抬頭
    required: true
    elements: [date, salutation]
    note: 日期 flush-left；抬頭獨立一行
  - id: lead
    name: 引言段
    required: true
    note: 第一段使用 dropcap；80-120 字
  - id: body
    name: 主體 2-3 段
    required: true
    note: 每段一個論點
  - id: closing
    name: 結尾敬辭
    required: true
    note: zh：敬祝 + 署名；en：Sincerely / Yours truly + signature
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: true            # 第一段必用 dropcap（Swiss 仍保留書信慣例）
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Letter schema — swiss preset

適用場景：對外致辭、客戶通知、Swiss 風格極簡公開信。

版面骨架：A4 單欄 flush-left，行高 1.65，sans-serif 為主。
首段 dropcap 採 IKB accent（zh：中文字／en：大寫字母）。

必填區塊：見 body-sections（header / lead / body / closing）。

SVG 圖表角色：不適用。
