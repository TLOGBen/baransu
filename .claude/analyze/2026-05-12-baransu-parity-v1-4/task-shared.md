# Tasks: shared

**前置群組**：無（基底群組，最先跑）

## TASK-shared-01: 三 preset DESIGN.md §9 三要素擴充

**需求追溯**：REQ-008
**目標**：紙 / swiss / google-design 三 preset 的 `DESIGN.md §9` 完整含 (a) 焦點上限 1-2 / (b) accent hex 設計理據 / (c) 我不是什麼（≥ 5 條）。
**驗收標準**：
- [ ] 三 preset 各自 DESIGN.md §9 含三 sub-heading（焦點 / hex 理據 / 我不是什麼）
- [ ] 「我不是什麼」每 preset ≥ 5 條 `no X` 條目，內容對齊各 preset 反例
- [ ] hex 理據含 HSL 或 oklch 拆解（每 accent token 一條）

### 步驟

#### 規格層改動
- [ ] 讀 `plugins/baransu/skills/design/references/紙-preset/DESIGN.md` §9 既有內容
- [ ] 在 §9 內補三 sub-heading 段；hex 拆解：`#1B365D = H 211°, S 55%, L 24%` + `oklch(0.32 0.08 256)` advisory
- [ ] 「我不是什麼」紙 preset 條目：no cool accent / no oklch in attribute / no italics / no gradient bg / no second accent
- [ ] swiss preset DESIGN.md §9 同等補完；hex 用 `#002FA7`（IKB），「我不是什麼」對齊 Swiss invariant（DESIGN.md root 已有 10 invariant）
- [ ] google-design preset DESIGN.md §9 同等補完；accent 對齊該 preset 的 token 命名

#### 驗證
- [ ] grep `^### \(a\)` / `^### \(b\)` / `^### \(c\)` 三 sub-heading 在三檔皆存在
- [ ] 「我不是什麼」段條目用 `wc -l` 確認 ≥ 5

---

## TASK-shared-02: 三 preset DESIGN.md §2 oklch advisory footnote

**需求追溯**：REQ-009
**目標**：三 preset DESIGN.md §2 表的 accent token 旁標 `oklch(...)` 等價值，並加 footnote 說明 advisory 性質。
**驗收標準**：
- [ ] 三 preset DESIGN.md §2 表的 `--accent`（及任何含 accent 角色的 token）row 含「`#hex → oklch(...)`」格式
- [ ] §2 結尾含 footnote 文字（≥ 30 字）明示「oklch 為 advisory；WeasyPrint print pipeline 仍以 hex 為準」
- [ ] tokens.css / design-cores HTML 不出現 `oklch(` 字串

### 步驟

#### 規格層改動
- [ ] 對每 preset DESIGN.md §2 表，在 `--accent` row 後加 oklch 等價值（用 hex-to-oklch 線上 / 本地工具計算）
- [ ] 在 §2 表後加 markdown footnote block

#### 驗證
- [ ] `grep -r "oklch(" plugins/baransu/skills/design/references/*-preset/tokens.css` 命中 = 0
- [ ] `grep -r "oklch(" plugins/baransu/skills/design/references/*-preset/design-cores/` 命中 = 0
- [ ] `grep -c "oklch(" plugins/baransu/skills/design/references/紙-preset/DESIGN.md` ≥ 1

---

## TASK-shared-03: canonical-tokens.md 加 perfect fourth 1.333 scale 註解 + 三 preset tokens.css 調整

**需求追溯**：REQ-003
**目標**：對齊 guizang 印刷學 perfect fourth scale；三 preset font scale 校正到 H1:Body ≈ 2.37×、H2:H3 ≈ 1.333×。
**驗收標準**：
- [ ] `canonical-tokens.md` 含 modular scale 段（明示 1.333 為設計目標）
- [ ] 三 preset `tokens.css` 對應 `--font-h1` / `--font-h2` / `--font-h3` / `--font-body` 對外比例符合 1.333× chain
- [ ] v1.2 殘留的 2.2× / 1.24× 舊比例不存在

### 步驟

#### 規格層
- [ ] 在 `design/references/canonical-tokens.md` 加「Modular Scale」段，明示 perfect fourth `r=1.333`，列計算範例

#### 模板層
- [ ] 計算每 preset 的 4 個字級數值；舉例（紙 preset body=16px）：H3=21.3、H2=28.4、H1=37.9（取整 21 / 28 / 38）
- [ ] 改 `紙-preset/tokens.css` 對應 4 個 CSS variable
- [ ] swiss-preset / google-design-preset tokens.css 同等調整

#### 驗證
- [ ] grep 三 tokens.css 計算比例（用 python one-liner 解析 `--font-*` 值算比例），全在 ±0.05 容差內
