# Tasks: a（規則 DSL `&` 自身選擇器）
**前置群組**：無

> 唯一觸及檔案：`src/catalog/service/rule.rs`（catalog service 層 —— 禁 import rusqlite / dao）。
> 既有 4 條 `rule::tests` 一字不改（C6）。程式碼註解中的舊 REQ 編號與本 spec 無關。

## TASK-a-01: 元素層 `&` 自身選擇器修復

**需求追溯**：REQ-001
**測試重量建議**：full
**目標**：`extract_within` 與 `select_within` 對 `&` alternative 不再呼叫 `Selector::parse`，直接以當前元素為候選；accessor / regex / `||` fallback 語意照常。
**驗收標準**：
- [ ] `extract_within(el, "&")` 回自身 text（C1）；`&@href`/`&@html`/`&@outerHtml` 回自身對應值（C2）；`&##re##rep` 套用取代（C3）
- [ ] `"em.missing || &"` 與 `"& || em.x"` 皆正確解析（C4）—— 關鍵：`&` 與非 `&` alternative 混用時，非 `&` 者仍走 parse，且 parse 必須延後到該 alternative 輪到時才發生
- [ ] `select_within(el, "&")` 回 `Ok(vec![el])`（C5）
- [ ] 既有 `catalog::service::rule::tests` 4 條原樣通過（C6）
- [ ] `&` 取值為空 → 落入下一 alternative；全空回 `Ok(None)`（邊界）

### 步驟

#### 修復 extract_within（rule.rs:142 起）
- [ ] 將 `Selector::parse` 移入「`alt.selector != "&"`」分支；`&` 分支 `candidate = Some(ctx)`，完全不 parse
- [ ] 確認 `read_accessor` / `apply_replace` 對 `&` 候選照常執行（現有程式已如此，僅 parse 時序錯誤）

#### 修復 select_within（rule.rs:111 起）
- [ ] 增加 `&` 分支：回 `vec![ctx]`（非空即 return）；非 `&` 分支照舊

#### 測試（RED 先行）
- [ ] 新增測試模組區段：以 `Html::parse_fragment("<a href=\"/x\">第1章 起</a>")` + selector 選出 `<a>` 作 fixture
- [ ] 逐條覆蓋上列驗收標準；斷言具名值（見 test.md E2E 表 A 列），不得只斷言 `is_ok`

---

## TASK-a-02: document 層 `&` 視為根元素（bonus C7）

**需求追溯**：REQ-002
**測試重量建議**：full
**目標**：`extract_doc` / `select_nodes` / `extract_all_doc` 對 `&` alternative 以 `doc.root_element()` 為候選節點，不報錯。
**驗收標準**：
- [ ] `extract_doc(&doc, "&")` 回根元素整體 text（C7）
- [ ] `select_nodes(&doc, "&")` 回 `vec![doc.root_element()]`（長度 1）（C7）
- [ ] `extract_all_doc(&doc, "&")` 回單元素向量（C7）
- [ ] 非 `&` 規則於三入口行為與既有測試完全不變（C6）

### 步驟

#### 實作
- [ ] 三個 doc 層入口各加 `&` 分支：候選 = `doc.root_element()`；非 `&` 分支照舊延後 parse
- [ ] 保持 `||` 語意：`&` 於任一位置皆可（與 TASK-a-01 同模式）

#### 測試
- [ ] `Html::parse_fragment("<p>alpha</p><p>beta</p>")`：斷言 `extract_doc` 結果同時含 `"alpha"` 與 `"beta"`；`select_nodes` / `extract_all_doc` 各 `len == 1`
