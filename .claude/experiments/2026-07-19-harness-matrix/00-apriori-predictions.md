# 事前預測（實驗執行前落筆，不得事後修改）

日期：2026-07-19。實驗者：Claude Fable 5（主迴圈編排）。
本檔在任何 arm 開跑之前寫定，作為可證偽的理論預測記錄。

## 實驗設計

3×3 矩陣，每 arm 一個獨立 worktree（自 bfa0f46 分支），同一份 EXPERIMENT-BRIEF.md
（三個工作項：A = rule DSL `&` self-selector bug、B = 換源進度遷移、C = 多源搜尋摺疊）。

- 模型軸：F = Fable 單模型；OS = Opus 主導 + Sonnet 實作（使用者日常組合的代表，
  gpt-5.6-sol 不可用故僅以 Anthropic 系代表）；FOS = Fable 規劃 + Sonnet 實作 + Opus 審查
- 流程軸：P1 = 原生（無 harness）；P2 = analyze spec 後直接實作；P3 = analyze + execute 式
  TDAID 編排（Red/Green + 四層語意 review + final coverage 核對，用 baransu 實際 agent 契約）

評分權重（使用者指定）：實現完整度 + 最少 bug ≫ 時間 ≫ token。
追加維度：原先架構遵循度（DDD 4-context × 5-layer 不變量）、測試有效率（突變抽查）。

## 主指標理論排序（完整度 + 最少 bug）

```
P3-F ≧ P3-FOS > P2-F ≈ P1-F > P3-OS > P2-OS ≈ P2-FOS > P1-FOS > P1-OS
```

## 假說

- **H1（交互作用，本實驗核心）**：harness 邊際價值與實作者模型強度成反比。
  Fable 實作的 arm，P1→P3 品質增益小（預測 ≤1 個 criteria 差距）；Sonnet 實作的
  arm，P1→P3 增益大（預測 ≥2-3 個 criteria / bug 差距）。P1-OS 與 P3-OS 之間
  是全場最大 spread。
- **H2（架構遵循度）**：遵循度主要由「誰讀懂 CLAUDE.md」決定 — Fable arm 即使
  原生也高遵循；Sonnet 原生（實作端）最易違規；spec 的存在（P2/P3）能把
  不變量外部化、顯著拉高 Sonnet arm 的遵循度。
- **H3（測試有效率）**：P3 的 Red gate（先失敗再實作）使測試有效率全面最高，
  與模型軸大致無關；P1 原生 arm 最可能出現「事後補測試、殺不死突變」。
- **H4（風險點預測）**：項目 B 的三個隱形陷阱 — idx 非稠密（第N章 ≠ idx N-1）、
  abort-before-tx 語意、scroll_offset 重置 — 是 bug 的主要來源；P1-OS 最可能踩
  idx 陷阱。項目 C 的陷阱是摺疊後 Enter 選錯 hit（index 映射錯位）與 StatusLine
  相對位置破壞。項目 A 的陷阱是只修 extract_within 而漏 select_within（A5）。
- **H5（效率）**：token 消耗 P3 ≈ 2-3× P1；時間 P3 ≈ 2× P1。P1-F 預測是
  時間與 token 雙料最省。

## 加權總冠軍預測

P3-F。但若 P1-F / P2-F 的品質與 P3-F 打平（主指標差 0），則效率權重使
P1-F / P2-F 勝出 —— 該結果將直接支持「模型變強、harness 應變輕」的路線。

## 決策日誌協定（因果分析基礎）

每 arm 每 agent 強制寫 `<worktree>/.exp/decision-log.md`（情境／選項／決定／理由／
spec-gap）。實驗後逐 arm 對照「決策 → 結果」，識別哪些決策點真正造成品質差異，
避免優化不存在的流程環節。
