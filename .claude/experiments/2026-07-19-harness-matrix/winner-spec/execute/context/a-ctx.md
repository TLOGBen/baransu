# Context: task-a（規則 DSL `&` 自身選擇器）

```yaml
Goal: >
  規則 DSL 的 `&` 自身選擇器可用：extract_within / select_within 對 `&` 不再
  EmptySelector（元素自身為候選）；bonus：extract_doc / select_nodes /
  extract_all_doc 將 `&` 視為文件根元素。對應驗收 C1–C7（= 簡報 A1–A7）。

Requirements:
  - "REQ-001: 元素層 `&` —— 在 Selector::parse 之前辨識 `&`，以當前元素為候選；accessor / regex / || fallback 照常"
  - "REQ-002: document 層 `&` 以 doc.root_element() 為候選，不報錯（bonus）"
  - "注意：程式碼註解中的舊 REQ 編號屬前一輪 spec，與本 spec 無關"

Scenarios:
  - "extract_within(el, \"&\") == Some(自身 text)（el 例：<a href=\"/x\">第1章 起</a>）"
  - "extract_within(el, \"&@href\") == Some(\"/x\")；&@html / &@outerHtml 取自身對應值"
  - "extract_within(el, \"&##第##Ch.\") == Some(\"Ch.1章 起\")"
  - "\"em.missing || &\" 落到自身；\"& || em.x\" 自身先中（& 任意位置）"
  - "select_within(el, \"&\") == Ok(vec![el])"
  - "既有 catalog::service::rule::tests 4 條一字不改、全過"
  - "extract_doc(&doc, \"&\") 回根元素整體 text（parse_fragment(\"<p>alpha</p><p>beta</p>\") 同含 alpha/beta）；select_nodes / extract_all_doc 各 len==1"

Task: |
  TASK-a-01: 元素層 `&` 自身選擇器修復（REQ-001, test_weight: full）
  驗收標準：
  - [ ] extract_within(el, "&") 回自身 text（C1）；&@href/&@html/&@outerHtml 回自身對應值（C2）；&##re##rep 套用取代（C3）
  - [ ] "em.missing || &" 與 "& || em.x" 皆正確解析（C4）—— 關鍵：& 與非 & alternative 混用時，非 & 者仍走 parse，且 parse 必須延後到該 alternative 輪到時才發生
  - [ ] select_within(el, "&") 回 Ok(vec![el])（C5）
  - [ ] 既有 catalog::service::rule::tests 4 條原樣通過（C6）
  - [ ] & 取值為空 → 落入下一 alternative；全空回 Ok(None)（邊界）

  TASK-a-02: document 層 `&` 視為根元素（bonus C7）（REQ-002, test_weight: full）
  驗收標準：
  - [ ] extract_doc(&doc, "&") 回根元素整體 text（C7）
  - [ ] select_nodes(&doc, "&") 回 vec![doc.root_element()]（長度 1）（C7）
  - [ ] extract_all_doc(&doc, "&") 回單元素向量（C7）
  - [ ] 非 & 規則於三入口行為與既有測試完全不變（C6）

Design: >
  唯一根因：extract_within（rule.rs:145）在 `alt.selector == "&"` 自身檢查之前就呼叫
  Selector::parse。修法 = 把 parse 移入「非 &」分支；& 分支 candidate = Some(ctx)
  完全不 parse。select_within 現況完全沒有 & 分支 —— 補上回 vec![ctx]。doc 層三入口
  同模式、候選改 doc.root_element()。不改 parse_rule / parse_alt（"&" 非空、能通過
  parse_alt；" & " 會被 trim 成 "&"）。read_accessor / apply_replace 沿用。

Test: >
  RED 先行。斷言具名值（見 spec test.md E2E 表 A 列）：具體字串 / len / element id，
  禁止 is_ok 式斷言。fixture 用 Html::parse_fragment + selector 選出元素。
  邊界：& 取值空 → fallback 下一 alternative；&@不存在attr → 空字串不 panic；
  " & " trim 後仍走自身分支。首要交付釘死：C1 測試在修復前必 Err、修復後 Some。

Constraints:
  - "catalog service 層：禁 import rusqlite / 任何 dao 模組（CLAUDE.md 分層硬規則）"
  - "既有 4 條 rule::tests 一字不改（C6 = 簡報 A6）"
  - "不動 select_within 的 dead_code 註記以外性質 —— 該 fn 之 dead_code 警告屬預期，不可為消警告而改動其它處；不引入新警告"
  - "禁止網路測試；不碰 book-sources/、.claude/skills/"
  - "|| 語意不變：第一個非空結果勝出；& 只是候選節點來源的特例"

Files:
  - src/catalog/service/rule.rs
```
