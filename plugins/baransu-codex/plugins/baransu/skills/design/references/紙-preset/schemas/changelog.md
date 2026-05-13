---
schema-id: changelog
class-prefix: kami-
langs: [zh, en]
templates:
  zh: design-cores/changelog.html
  en: design-cores/changelog-en.html
body-sections:
  - id: header
    name: 標題 + 專案說明
    required: true
    note: 專案名 + 一句說明 + 版本約束（semantic version 規則註記）
  - id: releases
    name: 版本列表
    required: true
    note: 依時間倒序列出 semantic version；每 release 含 added / changed / removed / fixed 四分類
    item-structure:
      version: "MAJOR.MINOR.PATCH"
      date: "YYYY-MM-DD"
      groups: [added, changed, removed, fixed]
image-requirements:
  position: "center 35%"
  applies-to: [optional]
editorial-requirements:
  dropcap: false           # changelog 強調掃讀，不用 dropcap visual；但仍宣告 .kami-dropcap class 以通過 sanity gate
  curly: true              # U+201C / U+201D
  widow-orphan: true
  text-wrap: pretty
---

# Changelog schema — 紙 preset

適用場景：軟體 / 設計系統 / API 版本紀錄；公開發行 changelog。

版面骨架：A4 直式單欄；版本以 `<ul>` 多層巢狀組織：
頂層 `<ul.kami-changelog-list>` → 每 release `<li>` → 內含 4 個
`<section.kami-changelog-group>`（Added / Changed / Removed / Fixed），
每 group 內 `<ul>` 條列。

必填區塊：見 body-sections（header / releases）。

SVG 圖表角色：不適用；純文字版本紀錄。Kami invariant：全文件無 `<polygon>`。
