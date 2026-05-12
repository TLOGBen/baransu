---
schema-id: letter
class-prefix: kami-
langs: [zh, en]
templates:
  zh: design-cores/letter.html
  en: design-cores/letter-en.html
body-sections:
  - id: header
    name: 日期 + 抬頭
    required: true
    elements: [date, salutation]
    note: 日期靠右，抬頭獨立一行（zh：敬啟者／某某先生女士；en：Dear ...）
  - id: lead
    name: 引言段
    required: true
    note: 第一段使用 dropcap；80-120 字交代來意
  - id: body
    name: 主體 2-3 段
    required: true
    note: 每段一個論點，段間留白 1 line-height
  - id: closing
    name: 結尾敬辭
    required: true
    note: zh：敬祝 + 署名 + 日期；en：Sincerely / Yours truly + signature
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: true            # 第一段必用 dropcap（編輯傳統）
  curly: true              # U+201C / U+201D
  widow-orphan: true
  text-wrap: pretty
---

# Letter schema — 紙 preset

適用場景：給投資人／客戶／團隊的正式書信、年度致辭、開放信。

版面骨架：A4 單欄，左右 padding ~32mm，行高 1.7，襯線體擔當主役。
首段 dropcap（zh 用中文字、en 用大寫字母），錨定閱讀起點。

必填區塊：見 body-sections（header / lead / body / closing）。

SVG 圖表角色：不適用；書信純文字。
