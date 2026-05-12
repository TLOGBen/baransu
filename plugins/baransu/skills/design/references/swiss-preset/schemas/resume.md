---
schema-id: resume
class-prefix: swiss-
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
    note: 100 字內單段；無 dropcap（Swiss 偏好均一字級）
  - id: experience
    name: 經歷
    required: true
    note: 反序，每職位 3-5 條 bullet
  - id: education
    name: 學歷
    required: true
  - id: skills
    name: 技能
    required: true
    note: 分類列出
  - id: projects
    name: 專案
    required: false
image-requirements:
  position: "center 35%"   # 人像 rule of thirds
  shape: square
  applies-to: [header.portrait]
editorial-requirements:
  dropcap: false
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Resume schema — swiss preset

適用場景：技術職、設計職、Swiss 風格極簡 CV。

版面骨架：grid-based，左側 sidebar 含 portrait + 聯絡，主欄 1fr。

必填區塊：見 body-sections。

SVG 圖表角色：可選 timeline；不強制。
