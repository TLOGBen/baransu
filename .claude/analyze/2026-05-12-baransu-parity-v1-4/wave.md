# Wave Plan

> 8 group 群組剛好打在 /analyze cap 上限；wave.md 作排序概述。**單 wave 模型**——所有群組順序依「前置群組」field 排程，不切實體兩波 PR。

## 群組依賴圖

```
shared ────────┬──→ svg ───────────────┐
               │                       │
               ├──→ editorial ─→ schemas─┐
               │                         │
               └──→ layouts ─────────────┤
                                         │
                                         ↓
                                checklist-governance
                                         │
                                         ↓
                                    cross-tool
                                         │
                                         ↓
                                     finalize
```

## 群組摘要

| 順位 | 群組 | REQ 對應 | 關鍵交付 |
|------|------|---------|---------|
| 1 | **shared** | REQ-008 / REQ-009 / REQ-003-partial | 三 preset DESIGN.md §9 / §2 / canonical-tokens scale |
| 2 | **svg** | REQ-001 | 13 diagram-type complete + validator strict gate |
| 3 | **editorial** | REQ-004 | text-wrap pretty + dropcap + curly + editorial-sanity.sh |
| 4 | **schemas** | REQ-002 | 6 新 schema × 3 preset × zh/en + sanity object-position lint |
| 5 | **layouts** | REQ-003 主軸 | slide-cores 22 layout × 3 preset + validate-swiss-deck |
| 6 | **checklist-governance** | REQ-005 / REQ-006 | checklist 15-20 條 + Fact-verify + Core Asset Protocol |
| 7 | **cross-tool** | REQ-007 / REQ-010-partial (M2) | export-brief mode + design-token-resolver / golden-template 三 preset 升級 |
| 8 | **finalize** | REQ-010 (M1/M3) / REQ-011 / REQ-012 | smoke-test fixture regen + Stage 整數化 + score 腳本 + plugin v1.4.0 bump |

## 不切兩波的原因

8 group 已是上限，但群組之間是**鏈式單向依賴**（無 fan-out 平行波），單 wave 順序執行即可；強切兩波只是儀式不增效率。/execute 可依「前置群組」field 串行 / 局部平行（同層級的 editorial + svg 可平行；schemas 必等 editorial）。

## 建議的 milestone gate（非 task）

- **M-65**：shared + svg + editorial 完成（≈ Milestone 2「視覺辨識度」打到 75%）
- **M-82**：+ schemas + layouts（≈ Milestone 3「Slide 多樣性 + 多文件類型」打到 82%）
- **M-95**：+ checklist-governance + cross-tool + finalize（最終 ≥ 90% baseline-parity-score）

每個 milestone 跑一次 `python3 scripts/baseline-parity-score.py` 看當下加權 %，作為非阻斷的進度指標。
