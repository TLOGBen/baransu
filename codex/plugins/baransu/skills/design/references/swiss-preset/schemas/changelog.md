---
schema-id: changelog
class-prefix: swiss-
langs: [zh, en]
templates:
  zh: design-cores/changelog.html
  en: design-cores/changelog-en.html
body-sections:
  - id: header
    name: 標題 + 專案說明
    required: true
    note: 專案名 + 一句說明 + semantic version 規則註記
  - id: releases
    name: 版本列表
    required: true
    note: 倒序 semantic version；每 release 含 added / changed / removed / fixed
    item-structure:
      version: "MAJOR.MINOR.PATCH"
      date: "YYYY-MM-DD"
      groups: [added, changed, removed, fixed]
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: false
  curly: true
  widow-orphan: true
  text-wrap: pretty
---

# Changelog schema — Swiss preset

適用場景：軟體 / 設計系統 / API 版本紀錄。

版面骨架：A4 直式，12-column grid；左 3 欄擺版號 + 日期，右 9 欄
擺 added / changed / removed / fixed 四 group。多層巢狀 `<ul>`。

必填區塊：見 body-sections（header / releases）。

SVG 圖表角色：不適用。Kami invariant：全文件無 `<polygon>`。
