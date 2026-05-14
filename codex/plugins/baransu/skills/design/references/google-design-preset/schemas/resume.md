---
schema-id: resume
class-prefix: google-
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
    note: 100 字內單段；無 dropcap
  - id: experience
    name: 經歷
    required: true
  - id: education
    name: 學歷
    required: true
  - id: skills
    name: 技能
    required: true
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

# Resume schema — google-design preset

適用場景：Material 3 風格 CV，產品 / 工程職位。

版面骨架：Material card-based，elevation 0–1 為主。

必填區塊：見 body-sections。

SVG 圖表角色：可選 chip-cluster 顯示技能矩陣。
