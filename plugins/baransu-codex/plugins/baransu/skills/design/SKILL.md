---
name: design
description: Use When generating a UI/UX design spec or linting an existing DESIGN.md.
  Do Three modes — gen (guided DESIGN.md), lint (structure + Kami invariant check),
  preset <name>. Trigger On '/design', '生成設計規格', '設計規格'.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
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
   c. If not found → insert the following line at the earliest sensible position after any YAML frontmatter or top-level heading (i.e. after the first `---` block if present, or after the first `# Heading` line, or at line 2 if neither exists):

      ```
      When working on any UI/UX content, read DESIGN.md at the project root and follow the overall design system defined there.
      ```

   d. Output one line per file modified: 「已在 {filename} 開頭插入 DESIGN.md 引用。」

3. If none of the three files exist → skip silently. Do not create any of them.

This stage is non-blocking and does not affect mode dispatch.

---

## Mode Dispatch

Parse the first token of the user's input (after `/design`):

| First token | Mode |
|-------------|------|
| `lint` (lowercase exact match) | Lint mode |
| `preset` | Preset mode (second token = preset name) |
| anything else (or no input) | Gen mode (default) |

Case-sensitive. `Lint` or `LINT` do not match lint mode — they enter gen mode.

---

## Gen Mode

Generate a full DESIGN.md via guided questions.

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

### Step 3 — Offer CLAUDE.md injection (optional)

After writing DESIGN.md, ask the user:

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

## Lint Mode

Check an existing DESIGN.md for structural completeness and Kami invariant compliance.

### Step 1 — Check file exists

Use `git rev-parse --show-toplevel` to find the project root. Check if `{project_root}/DESIGN.md` exists.

If DESIGN.md does not exist → output error and stop:
「找不到 DESIGN.md，請先執行 /design gen」
Do not switch to gen mode.

### Step 2 — Read DESIGN.md

Read `{project_root}/DESIGN.md` into context.

### Step 3 — Check nine-section completeness

Verify the file contains all nine level-2 headings:

1. `## 1. Visual Theme & Atmosphere`
2. `## 2. Color Palette & Roles`
3. `## 3. Typography Rules`
4. `## 4. Component Stylings`
5. `## 5. Layout & Spacing`
6. `## 6. Iconography & Imagery`
7. `## 7. Motion & Animation`
8. `## 8. Do / Don't`
9. `## 9. AI Prompt Guide`

Missing sections: report each by number and name, explain what it should contain.

### Step 4 — Check Kami ten invariants

Check against the following ten invariants. Report violations by invariant name and number:

| # | Invariant | Rule |
|---|-----------|------|
| 1 | 禁用純白 | Background colors must not be pure white (`#ffffff` or `rgb(255,255,255)`). Warm near-white variants are acceptable. |
| 2 | 暖調限定 | Color palette must stay in warm or neutral tones. Cool grays, blue-tinted whites, or purely desaturated colors violate this. |
| 3 | 襯線層次 | Typography hierarchy must use serif fonts (Charter, Georgia, Palatino, or equivalent) for at least the primary heading or body role. Pure sans-serif stacks for all roles violate this. |
| 4 | 無硬陰影 | Component shadows must use soft, diffused shadows (e.g. `box-shadow: 0 2px 8px rgba(...)`). Hard pixel-offset shadows or `drop-shadow` with no blur violate this. |
| 5 | 禁用 rgba 標記 | Color definitions in the spec must use hex codes or named tokens. Inline `rgba(...)` values in the color palette section violate this. |
| 6 | 墨藍主色 | The primary brand/accent color must be a deep ink-blue (`#1B365D` or perceptually equivalent). Purely saturated primary colors (red, green, orange) violate this unless the project explicitly overrides this invariant. |
| 7 | 羊皮紙底色 | The primary background must be a warm parchment tone (similar to `#f5f4ed`). Pure white or cool-gray backgrounds violate this. |
| 8 | 中文字型 | If Chinese text is used, the typography section must include a Chinese font stack (TsangerJinKai02, Noto Serif TC, or equivalent). Missing Chinese font spec when Chinese content is present violates this. |
| 9 | AI 提示完整性 | Section 9 (AI Prompt Guide) must be a complete, stand-alone prompt that can reproduce the design system in a fresh context. One-word labels or empty sections violate this. |
| 10 | 九段俱全 | All nine sections must be present (from the completeness check above). This invariant is the summary gate. |

### Step 5 — Output report

If all nine sections present and no Kami invariant violations:
「✅ DESIGN.md 通過 lint：九段俱全，Kami 十不變量無違規。」

If there are issues, output a structured report:

```
## DESIGN.md Lint 報告

### 缺少段落
- Section N: [名稱] — 應包含：[說明]

### Kami 不變量違規
- 不變量 N（[名稱]）：[具體違規描述，引用 DESIGN.md 中的具體內容]
```

---

## Preset Mode

Apply a named preset as the complete DESIGN.md.

### Step 1 — Parse preset name

Extract the second token after `preset` as the preset name.

If no name is provided → output error + list available presets (see Step 2 for listing logic):
「錯誤：preset 模式需要名稱，例如：/design preset 紙」

### Step 2 — Locate preset file

Preset files are stored at: `{skill_dir}/references/{name}-preset.md`

Where `{skill_dir}` is the directory containing this SKILL.md file.

Scan `references/` for files matching `*-preset.md`. Build the available preset list by stripping the `-preset.md` suffix.

If the requested preset name does not match any file → output error + list:
```
錯誤：找不到 preset「{name}」。
可用 preset：{list}
```
If no preset files exist: 「目前無可用 preset。」

### Step 3 — Apply preset

Use `git rev-parse --show-toplevel` to find the project root.

If `{project_root}/DESIGN.md` already exists:
Output one line: 「已存在 DESIGN.md，將以「{name}」preset 覆寫。」
Then proceed to write without further confirmation.

Write the contents of `references/{name}-preset.md` to `{project_root}/DESIGN.md`.

Output: 「✅ 已套用「{name}」preset，DESIGN.md 已寫入 {project_root}/DESIGN.md」

---

## Error Handling

| Error | Behavior |
|-------|----------|
| lint: DESIGN.md not found | Report error + suggest `/design gen`; stop |
| preset: no name given | Report error + list available presets |
| preset: unknown name | Report error + list available presets |
| preset: references/ empty | Report「目前無可用 preset」 |
| git rev-parse fails (non-repo) | Use current working directory as project root |
| CLAUDE.md already contains DESIGN.md | Skip append (idempotent) |
| gen: DESIGN.md already exists | Overwrite without prompting |
