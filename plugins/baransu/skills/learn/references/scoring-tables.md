# scoring-tables.md — Stage 2 scoring-table output templates

This file holds the two verbatim output templates for SKILL.md Stage 2 §3
(Present scoring table for user confirmation). The two forms are mutually
exclusive per run: use the **lane-grouped form** when §3.5 fan-out was
triggered, the **combined form** otherwise (the layout rule in SKILL.md
Stage 2 §3 decides which). Render the chosen template exactly as written —
do not restructure the headings or table columns.

## Lane-grouped form (when fan-out was triggered)

```
## 消化評分結果

請確認以下評分，並回覆要保留哪些來源。若所有來源均可接受，請回覆「全部保留」。

## academic
| 來源 slug | 多情境適用性 | 預測力 | 通用性 |
|-----------|-------------|--------|--------|
| {slug-a1} | {1-5}       | {1-5}  | {1-5}  |

## web
| 來源 slug | 多情境適用性 | 預測力 | 通用性 |
|-----------|-------------|--------|--------|
| {slug-w1} | {1-5}       | {1-5}  | {1-5}  |

## gh
| 來源 slug | 多情境適用性 | 預測力 | 通用性 |
|-----------|-------------|--------|--------|
| {slug-g1} | {1-5}       | {1-5}  | {1-5}  |

## x
| 來源 slug | 多情境適用性 | 預測力 | 通用性 |
|-----------|-------------|--------|--------|
| {slug-x1} | {1-5}       | {1-5}  | {1-5}  |
```

Sources with `lane=null` group under a `## direct` heading with the same
column structure.

## Combined form (single-lane or non-fan-out inputs)

```
## 消化評分結果

請確認以下評分，並回覆要保留哪些來源。若所有來源均可接受，請回覆「全部保留」。

| 來源 slug | 多情境適用性 | 預測力 | 通用性 |
|-----------|-------------|--------|--------|
| {slug-1}  | {1-5}       | {1-5}  | {1-5}  |
| {slug-2}  | {1-5}       | {1-5}  | {1-5}  |
```
