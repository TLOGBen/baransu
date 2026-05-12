---
name: design
description: "Use When generating a UI/UX design spec or linting an existing DESIGN.md. Do Three modes — gen (guided DESIGN.md), lint (structure + Kami invariant check), preset <name>. Trigger On '/design', '生成設計規格', '設計規格'."
argument-hint: "[lint | preset <name> | <description>]"
user-invocable: true
---

UI/UX design specification skill. This body is English (agent-facing). All user-visible output is **Traditional Chinese (繁體中文)**.

## Stage 0 — Inject DESIGN.md reference into context files

Before mode dispatch, proactively ensure that CLAUDE.md, AGENT.md, and INSTRUCTION.md (any that exist at the project root) carry a top-of-file reminder to read DESIGN.md when handling UI/UX work.

### Steps

1. Resolve project root: `git rev-parse --show-toplevel`. If the command fails, use the current working directory.

2. For each of the following files — **in this order** — if the file exists at `{root}`:
   - `CLAUDE.md`
   - `AGENT.md`
   - `INSTRUCTION.md`

   a. Read the first 20 lines of the file.
   b. If any of those lines contains the string `DESIGN.md` → skip this file silently (idempotent).
   c. If not found → insert the following block at the earliest sensible position after any YAML frontmatter or top-level heading (i.e. after the first `---` block if present, or after the first `# Heading` line, or at line 2 if neither exists):

      ```
      When working on any UI/UX content, read the design system at the project root and follow it:
      - DESIGN.md — visual spec (nine-section design system)
      - tokens.css — CSS variables (canonical 36-name vocabulary; first line `/* preset: <slug> */`)
      - design-cores/ — component skeletons consuming the tokens (long-form / gallery / dashboard / 6 elements)
      - slide-cores/ — slide layouts (4 cover variants + 8 non-cover layouts)
      ```

      The idempotency check in step 2b looks for the literal string `DESIGN.md`, which appears on the first bullet — prior single-line injections are preserved as-is and not re-injected. To upgrade an existing project from the old single-line form, the user must edit it manually.

   d. Output one line per file modified: 「已在 {filename} 開頭插入 DESIGN.md 引用。」

3. If none of the three files exist → skip silently. Do not create any of them.

This stage is non-blocking and does not affect mode dispatch.

---

## Canonical Token Schema (v1.3)

The baransu design system uses a fixed vocabulary of CSS custom-property names that **every** preset's `tokens.css` must define. HTML 骨架 (design-cores/, slide-cores/) consume tokens by these canonical names only — preset-specific token names (e.g. Material `--md-*`, v1.2 `--brand`/`--parchment`) MUST be wrapped as internal aliases that resolve to canonical names.

`scripts/check.py` enforces this schema; gen mode derives values for these 36 names from the interview answers.

### Surface (5)
`--paper` page background • `--surface` card • `--surface-strong` interactive surface • `--dark-surface` dark container • `--deep-dark` dark page

### Accent (2)
`--accent` primary accent (sole chromatic, ≤5% surface) • `--accent-on` foreground on accent fills

### Text hierarchy (5)
`--ink` structural ink alias • `--text-primary` body & heading • `--text-secondary` table headers, secondary • `--text-muted` captions, tertiary • `--text-faint` metadata, placeholder

### Border (2)
`--border` primary divider • `--border-soft` row separator

### Font (3)
`--font-sans` • `--font-serif` (sans alias in sans-only presets) • `--font-mono`

### Shadow (2)
`--shadow-ring` (`0 0 0 1px var(--border)`) • `--shadow-whisper` (elevated hover)

### Spacing — 4pt grid (7)
`--space-xs` `--space-sm` `--space-md` `--space-lg` `--space-xl` `--space-2xl` `--space-3xl`

### Radius (7)
`--radius-xs` `--radius-sm` `--radius-md` `--radius-lg` `--radius-xl` `--radius-2xl` `--radius-hero`

### Layout (3)
`--cover-title-align` (`center` or `left`) • `--grid-columns` (default 12) • `--grid-gutter`

### Semantic (2)
`--delta-up` (metric positive) • `--delta-down` (metric negative)

### tokens.css 第一行為 preset 識別註解

格式：`/* preset: <slug> */`（slug 為 `kami` / `google-design` / `swiss` / gen-slug）。
由 `scripts/check.py` 與 `/baransu:book` GATE-F 解析。

### v1.2 → v1.3 命名禁用清單

下列 v1.2 token 命名在 v1.3 已捨棄；tokens.css 不得定義、DESIGN.md 內文不得引用：

`--brand` / `--brand-light` / `--brand-tint` / `--brand-tint-strong` / `--parchment` / `--ivory` / `--olive` / `--warm-sand` / `--stone` / `--near-black` / `--dark-warm` / `--charcoal` / `--sans` / `--serif` / `--mono`

---

## Mode Dispatch (v1.3)

Parse the first token of the user's input (after `/design`):

| First token | Mode |
|-------------|------|
| `lint` (lowercase exact match) | Lint mode |
| `preset` | Preset mode (second token = preset name) |
| `gen` | Gen mode (requires `--slug <slug>`) |
| anything else (or no input) | Gen mode (legacy alias — but `--slug` 仍強制) |

Case-sensitive. `Lint` or `LINT` do not match lint mode.

`preset` 模式第二 token 為 preset 名：

| Second token | Preset route |
|--------------|--------------|
| `紙` | Kami preset (warm parchment, ink-blue, serif) — slug `kami` |
| `google-design` | Google Material 3 preset — slug `google-design` |
| `swiss` | Swiss preset (IKB accent, sans-serif) — slug `swiss` |

v1.3 統一 routing — 三 preset 共用相同 atomic staging pipeline（Step 3），全部產出 5 份 artifact（tokens.css / DESIGN.md / DESIGN.html / design-cores/ / slide-cores/）。v1.2 共用 `references/cores/` 與 `references/slide-cores/` 兩目錄已廢除，所有骨架均移至各 preset 內部 `references/<name>-preset/{design-cores,slide-cores}/`。

---

## Gen Mode (v1.3 — slug 強制)

Generate a custom-preset full artifact suite via guided questions.

### Step 0 — Validate `--slug <slug>`

Gen mode 強制要求 `--slug <slug>` 參數，未提供時直接 reject：

- pattern `/^[a-z][a-z0-9-]{1,15}$/`（小寫起始、2–16 字元、僅 a-z 0-9 連字號）
- 撞名清單動態 derive 自 `{skill_dir}/references/` 下實存 `*-preset/` 目錄名稱
  - v1.3 含：`kami`（display name 紙）、`google-design`、`swiss`
- 撞名 → stderr 印「slug 撞既存 preset 名 (reserved: kami / google-design / swiss)」，命令中止
- pattern 不合 → stderr 印「slug 不合 pattern /^[a-z][a-z0-9-]{1,15}$/」，命令中止

slug 通過後用於：tokens.css 第一行 preset header（`/* preset: <slug> */`）、design-cores/ + slide-cores/ class prefix（`<slug>-*`）、所有 HTML 內部命名。

Gen mode 後續流程（訪談 → derive tokens → atomic staging → mv）與 Preset Mode 等價，差異僅在 source-of-truth：preset 從 `references/<name>-preset/` 拷貝；gen 從訪談結果即時生成。

### Step 1 — Ask direction questions

Use AskUserQuestion to ask 3–5 design direction questions. Suggested questions (adapt based on what the user already provided):

1. **氛圍與風格** — 「這個介面的整體氛圍是什麼？（例如：溫潤手感紙張、現代冷調、活潑色彩、極簡留白）」
2. **色彩方向** — 「主色調的方向是什麼？有沒有需要傳達的品牌色或情感色？」
3. **元件展現** — 「按鈕、卡片、輸入框的視覺個性偏向哪種風格？（例如：有框線、無框填色、柔化陰影、扁平）」
4. **排版個性** — 「文字排版偏向哪種感覺？（例如：宋體古典、無襯線現代、等寬工程、混搭）」
5. **使用場景** — 「這個介面主要在什麼情境下使用？（例如：桌機閱讀、行動操作、資訊密集後台、展示型落地頁）」

Skip questions that were already answered in the user's initial input.

### Step 2 — Generate DESIGN.md

If `{project_root}/DESIGN.md` already exists, overwrite it without prompting.

Use `git rev-parse --show-toplevel` to find the project root. If the command fails, use the current working directory.

Write `{project_root}/DESIGN.md` with the full nine-section structure:

```
# Design System: [Project Title]

## 1. Visual Theme & Atmosphere
## 2. Color Palette & Roles
## 3. Typography Rules
## 4. Component Stylings
## 5. Layout & Spacing
## 6. Iconography & Imagery
## 7. Motion & Animation
## 8. Do / Don't
## 9. AI Prompt Guide
```

Each section must be substantive — no placeholder text. Base content on the user's answers. Section 2 must include hex codes for every named color. Section 9 must be a single reproducible AI prompt summarizing the design system.

### Step 3 — Render DESIGN.html

After writing DESIGN.md, produce a self-contained `{project_root}/DESIGN.html` that **uses the design system's own tokens to demonstrate itself** — not Kami or any external template.

The HTML should contain:

1. **Sticky sidebar TOC** — nine-section links, styled in the design system's primary/background colors
2. **Color palette section** — one colored `<div>` swatch per named color with hex label; background of each swatch is the actual color
3. **Typography section** — live text samples in the specified font stacks (headings, body, captions); use `@font-face` or safe web-font fallbacks — no CDN links
4. **Component stylings section** — brief visual descriptions or code snippets, keeping the language from DESIGN.md
5. **Do / Don't section** — a two-column comparison table using green/red accent for pass/fail
6. **AI Prompt Guide section** — a copy-ready `<code>` block with the full reproducer prompt
7. **Remaining sections** — rendered as standard `<h2>` + prose

Technical requirements:
- Fully offline (no external scripts, no CDN fonts)
- Single file, no external assets
- Valid HTML5 with `<meta charset="utf-8">` and `<meta name="viewport">`
- The page's own background/text/accent colors must match Section 2 of DESIGN.md

Write the complete HTML to `{project_root}/DESIGN.html`. If the file already exists, overwrite it.

Output one line: 「✅ 已產出 DESIGN.html（設計系統視覺預覽，可直接用瀏覽器開啟）」

### Step 4 — Offer CLAUDE.md injection (optional)

After writing DESIGN.md and DESIGN.html, ask the user:

```
AskUserQuestion:
  question: "是否將設計語境寫入專案 CLAUDE.md？"
  header: "DESIGN.md 已完成"
  options:
    1. label: "寫入 CLAUDE.md"
       description: "在專案 CLAUDE.md 追加一行，標注 DESIGN.md 的設計語境，讓非 baransu session 也能繼承。"
    2. label: "不需要"
       description: "只保留 DESIGN.md，不修改 CLAUDE.md。"
```

If user chooses to write:
1. Run `grep -q "DESIGN.md" {project_root}/CLAUDE.md 2>/dev/null`
2. If the string already exists → skip (idempotent), output 「CLAUDE.md 已包含 DESIGN.md 引用，跳過。」
3. If not found → append one line to CLAUDE.md:
   `> 設計語境：參見 DESIGN.md（根目錄，UI 視覺規格）`

---

## Lint Mode (v1.3 — 結構 + 一致性 6 項檢查)

v1.2 「Kami 十不變量」已從 lint mode 移出，改為紙 preset 自帶 `紙-sanity.sh` 守護（紙 preset apply 時複製到 project root）。lint mode 在 v1.3 為 preset-agnostic 結構檢查。

### 執行

呼叫 `python3 {skill_dir}/scripts/check.py [project_root]`（無 args 時用 cwd）。check.py 自動偵測 project root 模式（含 tokens.css 或 DESIGN.md 即視為 project root）並跑 6 項檢查。

### 檢查項目（Check A–F）

| Check | 規則 | Fail 條件 |
|-------|------|----------|
| **A. 5 份 artifact 齊全** | tokens.css / DESIGN.md / DESIGN.html / design-cores/ / slide-cores/ 五項皆在 | 任一缺即 fail；Check A fail 即終止，不再跑 B-F |
| **B. tokens.css 含全套 canonical** | 36 canonical names 全有（見 §Canonical Token Schema） | 缺任一 canonical name 或含 v1.2 banned token（`--brand` / `--parchment` 等）即 fail |
| **C. cross-artifact prefix 一致** | design-cores/ + slide-cores/ 內 class prefix 全等於 tokens.css 第一行 preset slug | 單檔混 prefix 或 prefix 與 tokens header 不符即 fail |
| **D. DESIGN.md 九段 + canonical 引用** | 九段標題全在（見 design.md Appendix B），且內文不含 v1.2 token 命名 | 缺段、順序顛倒、或內文含 v1.2 命名即 fail |
| **E. long-form.html slot 唯一** | `design-cores/long-form.html` 含且僅含一個 `<section data-slot="long-form-body">` | 多個或零個皆 fail |
| **F. dashboard.html 純靜態** | `design-cores/dashboard.html` 不含 `<script>` 或外部 `src=http(s)://` | 任一出現即 fail |

### 輸出

- 全通過：`✅ /design lint pass — 5 file(s) checked, no violations.` + exit 0
- 任一 fail：`❌ N violation(s) in M file(s):` + 每項 `L<line> [#<inv> <name>] <msg>` + exit 1
- 結構錯（spec dir 不存在）：exit 2

### Kami sanity 守護

紙 preset 自帶的 `紙-sanity.sh` 是獨立工具（lint mode 不跑），呼叫 `python3 check.py --rules 紙-sanity-rules.json` 走 legacy per-file mode + Kami 十不變量規則（warm-tones / italics / heading-weight 等）。其他 preset 不繼承此 sanity，保留 lint mode preset-agnostic 性質。

---

## Preset Mode

Apply a named preset as the complete DESIGN.md.

### Step 1 — Parse preset name

Extract the second token after `preset` as the preset name.

If no name is provided → output error + list available presets (see Step 2 for listing logic):
「錯誤：preset 模式需要名稱，例如：/design preset 紙」

### Step 2 — Locate preset directory

Presets are folders at: `{skill_dir}/references/{name}-preset/`

Each preset directory contains (v1.3 完整 artifact set)：
- `DESIGN.md` — the design specification (required)
- `tokens.css` — canonical 36-name CSS variables; first line `/* preset: <slug> */`
- `design-cores/` — 9 個元件骨架（long-form / gallery / dashboard / 6 elements），class prefix `<slug>-*`
- `slide-cores/` — 12 個 layout（4 cover variants + 8 非 cover），class prefix `<slug>-*`
- `<slug>-sanity.sh` — preset 私有 sanity script（紙 preset only，v1.3 將 Kami 十不變量移此）

骨架使用 canonical token 名引用，preset 的 `tokens.css` 提供具體值。所有骨架 class prefix 與 tokens.css 第一行 preset slug 一致（由 lint Check C 守護）。

Where `{skill_dir}` is the directory containing this SKILL.md file.

Scan `references/` for directories matching `*-preset/` that contain a `DESIGN.md`. Build the available preset list by stripping the `-preset` suffix from each directory name.

Fallback: if no `*-preset/` directories exist, also scan for legacy `*-preset.md` files (backwards-compat).

If the requested preset name does not match any directory (or legacy file) → output error + list:
```
錯誤：找不到 preset「{name}」。
可用 preset：{list}
```
If no presets exist: 「目前無可用 preset。」

### Step 3 — Apply preset (v1.3 — atomic staging + v1.2 detection)

Use `git rev-parse --show-toplevel` to find the project root.

**v1.2 殘留偵測**（atomic 寫入前）：

兩條件任一即視為 v1.2 殘留：
1. `{project_root}/tokens.css` 存在但第一行不符 regex `/^\/\* preset: [a-z][a-z0-9-]{1,15} \*\/$/`
2. `{project_root}/tokens.css` 不存在，但 `design-cores/` / `slide-cores/` / `DESIGN.md` 任一存在

偵測到 v1.2 殘留且未加 `--force` flag → stderr 印「將覆蓋 v1.2 artifact，建議 `git stash` 或備份；以 `--force` 確認繼續」，命令中止（exit ≠ 0）。

`tokens.css` 第一行符合 regex → 視為 v1.3 header，直接 atomic 覆寫不報殘留（idempotent）。

**v1.3 統一 routing** — 每個 preset 都複製完整三層 artifact：

| Preset name | Source dir | preset header |
|-------------|------------|---------------|
| `紙` | `{skill_dir}/references/紙-preset/` | `/* preset: kami */` |
| `google-design` | `{skill_dir}/references/google-design-preset/` | `/* preset: google-design */` |
| `swiss` | `{skill_dir}/references/swiss-preset/` | `/* preset: swiss */` |

v1.2 共用目錄 `references/cores/` 與 `references/slide-cores/` 已廢除（屬於 swiss-preset 內部）。所有 preset 共用 canonical 36 token 名單（見 §Canonical Token Schema），HTML 骨架 class prefix 用 `kami-*` / `google-*` / `swiss-*` 區分但 token 引用一致。

**Atomic staging 流程** — 5 份 artifact 先寫到 `.tmp/design-staging/`，全部成功後 atomic mv 到 project root：

```
1. rm -rf {project_root}/.tmp/design-staging/   # 自動清前次失敗殘留
2. mkdir -p {project_root}/.tmp/design-staging/
3. Write staging/tokens.css (從 source tokens.css 完整 copy，第一行已含 preset header)
4. Write staging/DESIGN.md
5. Render staging/DESIGN.html (從 DESIGN.md + tokens.css 產出視覺預覽)
6. Copy staging/design-cores/ (9 檔: long-form + gallery + dashboard + 6 元件)
7. Copy staging/slide-cores/ (12 檔: 4 cover variants + 8 非 cover 既有 layout)
8. (紙 preset only) Copy staging/紙-sanity.sh
9. Atomic move: mv project_root 既有 v1.3 artifact 到 .tmp/design-old/ → mv staging/* 到 project root → rm -rf .tmp/design-old/
10. rm -rf .tmp/design-staging/
```

IO fail / SIGTERM / SIGINT 中任一階段失敗 → 保留 staging dir、project root 不變、exit ≠ 0。

**Completion message**：「✅ 已套用「{name}」preset；project root 5 份 artifact 已 atomic 寫入。」

### Step 4 — Render DESIGN.html

After writing DESIGN.md, produce a self-contained `{project_root}/DESIGN.html` that **uses the design system's own tokens to demonstrate itself** — not Kami or any external template.

The HTML should contain:

1. **Sticky sidebar TOC** — nine-section links, styled in the design system's primary/background colors
2. **Color palette section** — one colored `<div>` swatch per named color with hex label; background of each swatch is the actual color
3. **Typography section** — live text samples in the specified font stacks (headings, body, captions); use `@font-face` or safe web-font fallbacks — no CDN links
4. **Component stylings section** — brief visual descriptions or code snippets, keeping the language from DESIGN.md
5. **Do / Don't section** — a two-column comparison table using green/red accent for pass/fail
6. **AI Prompt Guide section** — a copy-ready `<code>` block with the full reproducer prompt
7. **Remaining sections** — rendered as standard `<h2>` + prose

Technical requirements:
- Fully offline (no external scripts, no CDN fonts)
- Single file, no external assets
- Valid HTML5 with `<meta charset="utf-8">` and `<meta name="viewport">`
- The page's own background/text/accent colors must match Section 2 of DESIGN.md

Write the complete HTML to `{project_root}/DESIGN.html`. If the file already exists, overwrite it.

Output one line: 「✅ 已產出 DESIGN.html（設計系統視覺預覽，可直接用瀏覽器開啟）」

---

## check.py 工具 (v1.3)

`scripts/check.py` 提供兩個模式：

**v1.3 project-root mode**（無 args 或 arg = project root）：跑 Check A–F 結構+一致性檢查（見 Lint Mode 段）。

**Legacy per-file mode**（arg = 單檔或 dir）：保留 v1.2 generic lint 規則（cool-gray blocklist / italics / heading-weight / line-height / shadow-blur）供 /book GATE-F interop + 紙 preset sanity script 使用。

Exit codes: 0 = clean, 1 = violations, 2 = structural error.

---

## Validator 分工 (v1.3)

- `scripts/check.py` (project-root mode)：A 5 artifact 齊全 / B 36 canonical 全套 + v1.2 banned 偵測 / C cross-artifact prefix 一致 / D DESIGN.md 九段 + canonical 引用 / E long-form slot 唯一 / F dashboard 純靜態
- `scripts/check.py` (legacy per-file mode)：給 `/book` validate-output.ts 在 GATE-F 路徑呼叫，sanity script 用以驗證 Kami 十不變量
- `/book` 端 `validate-output.ts` GATE-F（class prefix 白名單動態擴展為 `{kami, google, swiss}` + tokens.css 第一行 slug）+ GATE-G（filesystem dynamic read）

---

## Error Handling

| Error | Behavior |
|-------|----------|
| lint: DESIGN.md not found | Report error + suggest `/design gen`; stop |
| preset: no name given | Report error + list available presets |
| preset: unknown name | Report error + list available presets |
| preset: references/ empty | Report「目前無可用 preset」 |
| preset: `references/<name>-preset/{tokens.css,DESIGN.md,design-cores/,slide-cores/}` 任一缺失 | Report「preset 不完整 (plugin damaged)：缺 {path}」and abort |
| preset: v1.2 殘留偵測 + 無 --force | stderr warning + exit ≠ 0 |
| preset: copy write failure (permission / disk full / EPERM / ENOSPC) | Report「copy 失敗：{path} 寫入錯誤」and abort；保留 staging |
| preset: atomic mv 失敗 | 同上；project root 維持前一狀態 |
| gen: --slug missing / pattern fail / reserved word collision | stderr 對應錯誤訊息 and abort |
| git rev-parse fails (non-repo) | Use current working directory as project root |
| CLAUDE.md already contains DESIGN.md | Skip append (idempotent) |
| gen: DESIGN.md already exists | Overwrite without prompting |
| preset: DESIGN.html already exists | Overwrite without prompting |
| gen: DESIGN.html already exists | Overwrite without prompting |
