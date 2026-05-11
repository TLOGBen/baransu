---
name: er
status: ref-only
example: null
---

# ER / Data Model

**Best for**: database schema、API resource 關係、domain model、aggregate boundary、跨服務資料 ownership map。

## Layout conventions

- Layer 3 derived token：`entity-key` = `--brand-tint`（v1 ground truth `#EEF2F7`），`entity-attr` = `--parchment`（v1 ground truth `#faf9f5`）；皆預計算為 solid hex，不得出現 alpha-channel CSS 函式形式，參見 `references/design-token-resolver.md`。
- 每個 entity 為兩段式 box：**header** = type tag（`ENTITY`）+ entity 名（`--font-sans`），底色走 `entity-key`；**body** = field list（`--font-mono`，每行一個），底色走 `entity-attr`；PK 前綴 `#`，FK 前綴 `→`。
- Relationship 為 entity 之間的線，**兩端各標 cardinality**（`1` / `N` / `0..1` / `1..*`），`--font-mono` 8px，距 entity 邊 10–12px；可選的關係 label（"has"、"belongs to"）置於線中央。
- 相關 entity 群聚靠近，rearrange 直到大多數 relationship 為直線（不糾結）；`--brand` 只用在 aggregate root 或模型的中心 entity，一張圖一個。

## Anti-patterns

- 在數十個 FK 的模型上每條 FK 都畫 arrow。
  - *Why fails*：線數量會以 O(entities²) 暴增，視覺變 hairball；ER 圖的價值是讓人在 5 秒內看出 cluster 邊界，FK 太多時應改以 cluster 分組或拆 sub-diagram。
- 同一條 relationship 的兩端 cardinality 標注不一致（如一端 `1`、另一端忘記標）。
  - *Why fails*：cardinality 是 relationship 唯一回答的問題，缺一端等於宣告未定義；讀者會在「是 1:N 還是 N:M」之間反覆推敲，圖的決策力為零。
- 為了視覺整齊把 field 強制 padding 成等高 box。
  - *Why fails*：natural height 本就應 by content；padding 補白會讓 entity 大小錯位 imply 「這個 entity 比較重要」，但實際只是 field 數差異，誤導讀者建立錯誤心智模型。

## Examples

**Status: ref-only**. example HTML 待 v2-N 補。/book 遇此型時 fallback 通用 SVG primitives，final-report 標 `degraded-type: er`。
