---
schema-id: changelog
class-prefix: google-
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

# Changelog schema — Google-Design (Material 3) preset

適用場景：產品 / 設計系統 / SDK 版本紀錄（Material surface 風格）。

版面骨架：每個 release 為 rounded surface 卡片，
內含 4 個 outlined `<section>`（Added / Changed / Removed / Fixed），
group 標題以 chip 樣式呈現。多層巢狀 `<ul>`。

必填區塊：見 body-sections（header / releases）。

SVG 圖表角色：不適用。Kami invariant：全文件無 `<polygon>`。
