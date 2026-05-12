---
schema-id: resume
class-prefix: kami-
langs: [zh, en]
templates:
  zh: design-cores/resume.html
  en: design-cores/resume-en.html
body-sections:
  - id: header
    name: 頭部姓名 + 聯絡
    required: true
    elements: [name, role, location, email, phone, links]
  - id: summary
    name: 摘要
    required: true
    note: 80-120 字一段，不使用 dropcap（履歷強調掃讀效率）
  - id: experience
    name: 經歷
    required: true
    note: 反序排列，每職位 3-5 條成果項 (action + metric)
  - id: education
    name: 學歷
    required: true
  - id: skills
    name: 技能
    required: true
    note: 分類列出（語言 / 框架 / 工具）
  - id: projects
    name: 專案
    required: false
    note: 補充欄目；含連結
image-requirements:
  position: "center 35%"   # 人像 <img> rule of thirds 對齊（眼線位於上 1/3）
  shape: square            # 或 portrait-3x4
  applies-to: [header.portrait]
editorial-requirements:
  dropcap: false           # 履歷不用 dropcap
  curly: true              # U+201C / U+201D
  widow-orphan: true       # text-wrap: pretty
  text-wrap: pretty
---

# Resume schema — 紙 preset

適用場景：個人求職、顧問 profile、學術 CV。

版面骨架：單欄 A4，左側固定欄留白約 220px，主欄 padding 56px。
頭部含人像（rule of thirds），其下姓名 + 一行職銜 + 三行聯絡。

必填區塊：見 body-sections（header / summary / experience / education / skills）。

SVG 圖表角色：可選 sparkline 顯示時間軸；不強制。
