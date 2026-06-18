---
name: design
description: "Use When generating a UI/UX design spec or linting an existing DESIGN.md. Do Four modes — gen (guided DESIGN.md) / lint (structure + Kami invariant check) / preset <name> / export-brief (cross-tool prompt-ready brief). Trigger On '/design', '生成設計規格', '設計規格'. Not For: technical-architecture design.md (lowercase, /analyze layer); this skill only ever touches uppercase DESIGN.md (UI visual spec)."
argument-hint: "[lint | preset <name> | <description>]"
user-invocable: true
---

UI/UX design specification skill. This body is English (agent-facing). All user-visible output is **Traditional Chinese (繁體中文)**.

## Outcome Contract

- **Outcome**: The requested mode delivers a complete design-system artifact set, a lint verdict, or a cross-tool brief.
- **Done when**: gen/preset — the five artifacts (`tokens.css` / `DESIGN.md` / `DESIGN.html` / `design-cores/` / `slide-cores/`) are atomically written at project root; lint — `python3 scripts/check.py` exits 0 (clean) or 1 with violations listed; export-brief — `.claude/design/brief-{preset}-{date}.md` is written (or printed with `--stdout`).
- **Evidence**: The mode's completion message (「✅ 已套用…」 / lint pass-fail line with violation list / 「Brief 已寫入…」) and `check.py` exit code.
- **Output**: Project-root design artifacts, a lint report, or a prompt-ready brief markdown file.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Stage 0 — Inject DESIGN.md reference into context files

Before mode dispatch, proactively ensure that CLAUDE.md, AGENT.md, and INSTRUCTION.md (any that exist at the project root) carry a top-of-file reminder to read DESIGN.md when handling UI/UX work.

### Steps

1. Resolve project root: `git rev-parse --show-toplevel`. If the command fails, use the current working directory.

2. For each of the following files — **in this order** — if the file exists at `{root}`:
   - `CLAUDE.md`
   - `AGENT.md`
   - `INSTRUCTION.md`

   a. Read the first 30 lines of the file.
   b. Locate the current baransu design-system block. Two markers identify a block as current-version (v1.3):
      - contains `- slide-cores/` (added in v1.3; the v1.2 inject does not have this line)
      - contains `canonical 36-name vocabulary` (v1.3 schema marker)
   c. Decide the action:
      - **No block found** (normal case — never injected before) → insert the canonical v1.3 block at line 2 (or after the YAML frontmatter / after the first heading — take the earliest reasonable position)
      - **Stale block found** (contains `DESIGN.md` but lacks the v1.3 markers — e.g. leftover v1.2 inject) → **replace** the stale block with the canonical v1.3 block; leave the rest of the file untouched
      - **Current block found** (v1.3 markers all present) → skip silently (idempotent)
   d. Canonical v1.3 block text:

      ```
      When working on any UI/UX content, read the design system at the project root and follow it:
      - DESIGN.md — visual spec (nine-section design system)
      - tokens.css — CSS variables (canonical 36-name vocabulary; first line `/* preset: <slug> */`)
      - design-cores/ — component skeletons consuming the tokens (long-form / gallery / dashboard / 6 elements)
      - slide-cores/ — slide layouts (4 cover variants + 8 non-cover layouts)
      ```

      Stale-block replacement logic: find the first paragraph starting with `When working on any UI/UX` (the run of `-`-prefixed bullets up to the next blank line is its boundary) and replace that whole paragraph with the canonical block.
   e. Output:
      - newly inserted → 「已在 {filename} 開頭插入 DESIGN.md 引用（v1.3）。」
      - upgraded/replaced → 「已將 {filename} 內 v1.2 design 引用 block 升級為 v1.3。」
      - skip → no output.

3. If none of the three files exist → skip silently. Do not create any of them.

This stage is non-blocking and does not affect mode dispatch.

---

## Canonical Token Schema (v1.3)

v1.3 fixed vocabulary: the 36 canonical token names are **required** in every preset's `tokens.css`; HTML skeletons reference tokens only through these names, and preset-specific names (Material `--md-*` / v1.2 `--brand`) are mapped as aliases. Full schema (surface 5 / accent 2 / text 5 / border 2 / font 3 / shadow 2 / space 7 / radius 7 / layout 3 / semantic 2) + the v1.2 banned-name list → **read `references/canonical-tokens.md`**.

The first line of `tokens.css`, `/* preset: <slug> */`, identifies the preset; it is parsed by `scripts/check.py` and `/baransu:book` GATE-F.


## Mode Dispatch (v1.3, v1.4 export-brief)

Parse the first token of the user's input (after `/design`):

| First token | Mode |
|-------------|------|
| `lint` (lowercase exact match) | Lint mode |
| `preset` | Preset mode (second token = preset name) |
| `gen` | Gen mode (requires `--slug <slug>`) |
| `export-brief` | Export-brief mode (v1.4 — see §Export-brief Mode) |
| anything else (or no input) | Gen mode (legacy alias — but `--slug` is still mandatory) |

Case-sensitive. `Lint` or `LINT` do not match lint mode. `export-brief` must be lowercase exact match.

In `preset` mode, the second token is the preset name:

| Second token | Preset route |
|--------------|--------------|
| `紙` | Kami preset (warm parchment, ink-blue, serif) — slug `kami` |
| `google-design` | Google Material 3 preset — slug `google-design` |
| `swiss` | Swiss preset (IKB accent, sans-serif) — slug `swiss` |

v1.3 unified routing — all three presets share the same atomic staging pipeline (Step 3) and all produce 5 artifacts (tokens.css / DESIGN.md / DESIGN.html / design-cores/ / slide-cores/). The two v1.2 shared directories `references/cores/` and `references/slide-cores/` are removed (deprecated); all skeletons have moved into each preset's own `references/<name>-preset/{design-cores,slide-cores}/`.

### Decision checkpoint map

This skill has three hard-stops — honor each before crossing it:

| Checkpoint | Type | Where | Pass condition |
|------------|------|-------|----------------|
| destructive overwrite | 🔴 GATE | Preset Mode Step 3 (v1.2 residue detection) | `--force` present, or no v1.2 residue → else STOP (exit ≠ 0) |
| gen direction Q / CLAUDE.md write | 🔴 CHECKPOINT | Gen Mode Step 1 + Step 4 | user has answered the AskUserQuestion |
| lint verdict | 🔴 GATE | Lint Mode | `check.py` exit 0 → continue; exit 1 → report violations + stop |

---

## Preset Mode

Apply a named preset as the complete DESIGN.md.

### Step 1 — Parse preset name

Extract the second token after `preset` as the preset name.

If no name is provided → output error + list available presets (see Step 2 for listing logic):
「錯誤：preset 模式需要名稱，例如：/design preset 紙」

### Step 2 — Locate preset directory

Presets are folders at: `{skill_dir}/references/{name}-preset/`

Each preset directory contains (the v1.3 full artifact set):
- `DESIGN.md` — the design specification (required)
- `tokens.css` — canonical 36-name CSS variables; first line `/* preset: <slug> */`
- `design-cores/` — 21 component skeletons (long-form / gallery / dashboard + document-type letter / resume / one-pager / portfolio / equity-report / changelog, each with an -en bilingual variant + card / metric / quote-callout / data-table / section-title / tag-button), class prefix `<slug>-*`
- `slide-cores/` — 21 layouts (4 cover variants: cover / cover-data / cover-quote / cover-section + 17 non-cover), class prefix `<slug>-*`
- `<slug>-sanity.sh` — preset-private sanity script (紙 preset only; v1.3 moved the Kami ten invariants here)

Skeletons reference tokens by canonical token name, and the preset's `tokens.css` supplies the concrete values. Every skeleton's class prefix matches the preset slug on the first line of tokens.css (guarded by lint Check C).

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

**v1.2 residue detection** (before the atomic write):

Either condition counts as v1.2 residue:
1. `{project_root}/tokens.css` exists but its first line does not match the regex `/^\/\* preset: [a-z][a-z0-9-]{1,15} \*\/$/`
2. `{project_root}/tokens.css` does not exist, but any of `design-cores/` / `slide-cores/` / `DESIGN.md` exists

🔴 **GATE — destructive overwrite**: this branch can overwrite the user's existing project-root artifacts (tokens.css / DESIGN.md / design-cores/ / slide-cores/). STOP and do not proceed without confirmation.

If v1.2 residue is detected and the `--force` flag is absent → print to stderr 「將覆蓋 v1.2 artifact，建議 `git stash` 或備份；以 `--force` 確認繼續」 and abort the command (exit ≠ 0). **Without `--force` present, you must not bypass this GATE and write directly.**

If the first line of `tokens.css` matches the regex → treat it as a v1.3 header and atomic-overwrite directly without reporting residue (idempotent).

**v1.3 unified routing** — every preset copies the complete three-layer artifact set:

| Preset name | Source dir | preset header |
|-------------|------------|---------------|
| `紙` | `{skill_dir}/references/紙-preset/` | `/* preset: kami */` |
| `google-design` | `{skill_dir}/references/google-design-preset/` | `/* preset: google-design */` |
| `swiss` | `{skill_dir}/references/swiss-preset/` | `/* preset: swiss */` |

The v1.2 shared directories `references/cores/` and `references/slide-cores/` are removed/deprecated (they live inside swiss-preset). All presets share the canonical 36-token list (see §Canonical Token Schema); the HTML skeletons distinguish their class prefixes with `kami-*` / `google-*` / `swiss-*` but the token references are identical.

**Atomic staging flow** — the 5 artifacts are first written to `.tmp/design-staging/`, then atomic-mv'd to the project root once all succeed:

**Precondition (root-resolution guard, runs before step 1)**: if `{project_root}` resolved from `git rev-parse --show-toplevel` is empty or the command failed (and the cwd fallback is also empty or `/`), STOP with stderr 「無法解析 project root，中止以避免 rm -rf 誤刪」 and exit ≠ 0 — never run any `rm -rf` with an empty or root-level `{project_root}`. **Additionally (target-suffix pin, runs after the root check, before any rm -rf below)**: for each `rm -rf` command in this flow (steps 1, 9, 10), assemble its full target path and assert it equals exactly `{project_root}/.tmp/design-staging` or `{project_root}/.tmp/design-old`, with the `.tmp/...` literal segment non-empty — i.e. if the assembled `rm -rf` path does not end in the literal `/.tmp/design-staging` or `/.tmp/design-old`, STOP with stderr 「rm -rf 目標路徑非預期，中止」 and exit ≠ 0. This closes the gap where the root-only check validates `{project_root}` non-emptiness but never the appended `.tmp` subpath, so a malformed or empty suffix can never let `rm -rf` strike `{project_root}` itself.

```
1. rm -rf {project_root}/.tmp/design-staging/   # 自動清前次失敗殘留
2. mkdir -p {project_root}/.tmp/design-staging/
3. Write staging/tokens.css (從 source tokens.css 完整 copy，第一行已含 preset header)
4. Write staging/DESIGN.md
5. Render staging/DESIGN.html (從 DESIGN.md + tokens.css 產出視覺預覽)
6. Copy staging/design-cores/ (21 檔: long-form + gallery + dashboard + 6 文件型雙語骨架 + 6 通用元件)
7. Copy staging/slide-cores/ (21 檔: 4 cover variants + 17 非 cover 既有 layout)
8. (紙 preset only) Copy staging/紙-sanity.sh
9. Atomic move: mv project_root 既有 v1.3 artifact 到 .tmp/design-old/ → mv staging/* 到 project root → rm -rf .tmp/design-old/
10. rm -rf .tmp/design-staging/
```

If any stage fails amid an IO fail / SIGTERM / SIGINT → keep the staging dir, leave the project root unchanged, exit ≠ 0.

**Completion message**: 「✅ 已套用「{name}」preset；project root 5 份 artifact 已 atomic 寫入。」

### Step 4 — Render DESIGN.html

**Spec → read `references/render-design-html.md`** (shares the same spec as Gen Mode Step 3).

---

## Gen Mode (v1.3 — slug mandatory)

Generate a custom-preset full artifact suite via guided questions.

### Step 0 — Validate `--slug <slug>`

Gen mode mandatorily requires the `--slug <slug>` argument; reject outright when it is not provided:

- pattern `/^[a-z][a-z0-9-]{1,15}$/` (lowercase start, 2–16 chars, only a-z 0-9 hyphen)
- the collision list is dynamically derived from the `*-preset/` directory names actually present under `{skill_dir}/references/`
  - v1.3 includes: `kami` (display name 紙), `google-design`, `swiss`
- name collision → print to stderr 「slug 撞既存 preset 名 (reserved: kami / google-design / swiss)」 and abort the command
- pattern mismatch → print to stderr 「slug 不合 pattern /^[a-z][a-z0-9-]{1,15}$/」 and abort the command

Once the slug passes, it is used for: the tokens.css first-line preset header (`/* preset: <slug> */`), the design-cores/ + slide-cores/ class prefix (`<slug>-*`), and all HTML-internal naming.

The rest of the gen-mode flow (interview → derive tokens → atomic staging → mv) shares the same pipeline as Preset Mode. The only difference is the source-of-truth: preset copies the whole set from `references/<name>-preset/`; gen does not author its 5 artifacts from thin air but instead **clones the closest existing preset as the donor skeleton** and rewrites it.

#### Gen Mode Step 1.5 — Donor-clone the 21+21 skeletons (closed step)

The 21 `design-cores/` + 21 `slide-cores/` skeletons are NEVER authored from scratch by the LLM. They are derived from a donor preset so the gen output inherits the SSOT skeleton structure (DOM / slot / object-position) rather than improvising HTML.

**Donor selection rule** — pick the donor from the Step 1 atmosphere answer:

| Step 1 atmosphere answer | Donor preset | Donor dir |
|--------------------|--------------|-----------|
| 暖紙 / 手感紙張 / 古典 / 溫潤 | `kami` | `references/紙-preset/` |
| 現代冷調 / 極簡 / 工程 / 中性 | `swiss` | `references/swiss-preset/` |
| Material / 活潑色彩 / 卡片陰影 / app 介面 | `google-design` | `references/google-design-preset/` |

When the answer straddles two, prefer `swiss` (most preset-agnostic skeleton).

**Per-file transform** (input = donor dir's `design-cores/` + `slide-cores/`; output = 42 files staged):

- (a) Replace every class prefix `<donor>-*` (`kami-*` / `swiss-*` / `google-*`) with `<slug>-*` across the whole file.
- (b) Replace the donor `tokens.css` literal values with the values derived from the Step 1 interview; keep the canonical 36 token NAMES unchanged (only the values change).
- (c) Keep the donor's DOM structure / `data-slot` / `object-position` / object-fit untouched — these are SSOT-tuned, not gen-time decisions.

Output of this step feeds Step 3's atomic staging (`Copy staging/design-cores/` + `slide-cores/`) exactly as the preset path does. No new skeleton source is invented — gen only re-skins an existing donor.

### Step 1 — Ask direction questions

🔴 **CHECKPOINT — wait for the user's answers before continuing.** Do not draft DESIGN.md until the AskUserQuestion replies are in hand.

Use AskUserQuestion to ask 3–5 design direction questions. Suggested questions (adapt based on what the user already provided):

1. **Atmosphere & style** — 「這個介面的整體氛圍是什麼？（例如：溫潤手感紙張、現代冷調、活潑色彩、極簡留白）」
2. **Color direction** — 「主色調的方向是什麼？有沒有需要傳達的品牌色或情感色？」
3. **Component expression** — 「按鈕、卡片、輸入框的視覺個性偏向哪種風格？（例如：有框線、無框填色、柔化陰影、扁平）」
4. **Typography personality** — 「文字排版偏向哪種感覺？（例如：宋體古典、無襯線現代、等寬工程、混搭）」
5. **Use scenario** — 「這個介面主要在什麼情境下使用？（例如：桌機閱讀、行動操作、資訊密集後台、展示型落地頁）」

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

**Numeric anchors (a gen-mode custom-preset DESIGN.md must land hard numeric values, otherwise §2/§3/§5 degrade into a thresholdless AI-generic spec)** — the definition of "substantive" is upgraded from "not a placeholder" to "each segment below hits a named, measurable numeric value":
- §2 Color: color count ≤3–4 (1 primary + 1 secondary + 1 accent + grayscale), accent coverage ≤5% of the surface; body-text contrast ≥4.5:1, large text ≥3:1.
- §3 Typography: type scale perfect-fourth `r=1.333` (h1:body ≈ 2.37, h2:h3 ≈ 1.333); Chinese body line-height 1.5–1.55, forbid ≥1.6; reading column `max-width` ≤65ch.
- §5 Layout: whitespace ≥40% of total area; spacing follows a 4pt grid (multiples).

→ For the source of the numeric thresholds and the post-render self-check method, see `references/render-design-html.md §可驗品質門檻`; for the type-scale formula and tolerances, see `references/canonical-tokens.md §Modular Scale` (not re-transcribing the full table here — keeping the body lean).

**Gen-mode donor-clone failure branch** (three-tiered — resilience specific to the gen output path; the preset path's atomic/lint fallback does not cover this newly-generated path):

- **Trigger condition**: after the donor-clone, some `design-cores/` / `slide-cores/` file's class prefix still mixes in a donor prefix (`kami-*` / `swiss-*` / `google-*`), so lint Check C (cross-artifact prefix consistency) will fail.
- **First-line fix**: run a full `sed` over that file replacing the leftover donor prefix → `<slug>-` (patching the gap from Step 1.5 (a)), then re-run Check C to confirm it passes.
- **Still-fails fallback** (the donor skeleton itself lacks some canonical token alias; the prefix is clean but Check B still fails): fall back to preset mode applying that donor preset, and tell the user plainly 「gen slug `<slug>` 已降級為 `<donor>` preset」. 🔴 **Do not silently produce a half artifact set** — better to downgrade and report than to write out an incomplete skeleton that fails lint.

### Step 3 — Render DESIGN.html

**Spec → read `references/render-design-html.md`** (includes the 7-section structure + technical requirements + write location + success message).


### Step 4 — Offer CLAUDE.md injection (optional)

🔴 **CHECKPOINT — wait for the user's answer before writing to CLAUDE.md.** This step mutates the project's CLAUDE.md; do not append the line until the user chooses 「寫入 CLAUDE.md」.

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

## Lint Mode (v1.3 — structure + consistency, 6 checks)

The v1.2 「Kami 十不變量」 have been moved out of lint mode and are now guarded by the 紙 preset's own `紙-sanity.sh` (copied to the project root when the 紙 preset is applied). In v1.3 lint mode is a preset-agnostic structure check.

### Execution

Call `python3 {skill_dir}/scripts/check.py [project_root]` (uses cwd when no args). check.py auto-detects project-root mode (anything containing tokens.css or DESIGN.md is treated as a project root) and runs the 6 checks.

### Check items (Check A–F)

| Check | Rule | Fail condition |
|-------|------|----------|
| **A. 5 artifacts complete** | tokens.css / DESIGN.md / DESIGN.html / design-cores/ / slide-cores/ all five present | any one missing → fail; on Check A fail, terminate and do not run B-F |
| **B. tokens.css contains the full canonical set** | all 36 canonical names present (see §Canonical Token Schema) | missing any canonical name, or containing a v1.2 banned token (`--brand` / `--parchment` etc.) → fail |
| **C. cross-artifact prefix consistency** | class prefixes inside design-cores/ + slide-cores/ all equal the preset slug on the first line of tokens.css | a single file mixing prefixes, or a prefix not matching the tokens header → fail |
| **D. DESIGN.md nine sections + canonical references** | all nine section headings present (canonical list lives in `scripts/check.py` Check D), and the body contains no v1.2 token naming | a missing section, reversed order, or v1.2 naming in the body → fail |
| **E. long-form.html slot unique** | `design-cores/long-form.html` contains exactly one `<section data-slot="long-form-body">` | more than one or zero → fail |
| **F. dashboard.html purely static** | `design-cores/dashboard.html` contains no `<script>` or external `src=http(s)://` | any occurrence → fail |

### Output

- all pass: `✅ /design lint pass — 5 file(s) checked, no violations.` + exit 0
- any fail: `❌ N violation(s) in M file(s):` + each item `L<line> [#<inv> <name>] <msg>` + exit 1
- structural error (spec dir does not exist): exit 2

### Kami sanity guard

The 紙 preset's bundled `紙-sanity.sh` is a standalone tool (lint mode does not run it). It auto-locates `check.py` and then runs DESIGN.md + design-cores/ + slide-cores/ file by file in legacy per-file mode, applying check.py's built-in Kami ten-invariant rules (warm-tones / italics / heading-weight etc.) plus extended checks for schema existence, object-position, editorial-sanity, and so on. Other presets do not inherit this sanity, preserving lint mode's preset-agnostic nature.

### Slide + long-form design rules and failure branches

When authoring or reviewing slide-cores / long-form output, or interpreting a `check.py` violation code, read the rule catalogue **before** patching the template:

- Slide + long-form lint rules with three-column **現象 → 根因 → 做法** fallbacks, graded P0-S (Swiss-locked) / P0-A (all-preset) / P0-B (baransu self-discipline) / P1 (fail) / P2 (warning) / P3 (advisory) → **read `references/slide-checklist.md`**. Each entry pairs a trigger condition with a one-line fix and the rationale for why the rule exists — consult it when a lint code fires or a template choice is ambiguous, do not re-derive the fix from memory.
- Reference-honesty caveat: some P2 / P3 / P0-B `做法` columns describe **proposed / observed tooling** (observation items, not necessarily implemented yet), not runnable fixes. The only runnable verification mechanisms are `check.py` (A–F + legacy per-file) and, on the book side, `book/scripts/validate-swiss-deck.mjs` / `validate-output.ts`. When a `做法` cites a script that does not exist yet, treat it as a future observation item — do not build the missing file.

---

## Export-brief Mode (v1.4)

Cross-tool brief packaging — package the current preset's DESIGN.md + tokens.css + design-cores structure into a single prompt-ready plain-text markdown, ready to feed Codex CLI / ChatGPT Images 2.0 for cross-tool image-gen.

### Invocation

```
/baransu:design export-brief            # 寫到 {project_root}/.claude/design/brief-{preset}-{date}.md
/baransu:design export-brief --stdout   # 印到 stdout，不寫檔
```

### Input

- Current preset: parsed from the first line `/* preset: <slug> */` comment of `{project_root}/tokens.css`.
  - tokens.css missing or first line not matching the regex → print to stderr 「找不到 preset header；請先跑 `/baransu:design preset <name>`」 + exit ≠ 0.

### Output

- **Default**: markdown written to `{project_root}/.claude/design/brief-{preset}-{date}.md` (`{date}` is ISO `YYYY-MM-DD`); auto-created if `.claude/design/` does not exist.
- **`--stdout`**: the plain markdown block is printed directly to stdout, not persisted.

### Step-by-step assembly

#### Step 1 — Parse the preset
- Read the first line of `{project_root}/tokens.css`.
- Parse the `/* preset: <slug> */` comment to obtain `$PRESET` (`kami` / `swiss` / `google-design`, or a slug the user custom-built via `gen --slug`).
- **Canonical regex (path-traversal hardening)**: the first line must fully match `^/\* preset: [a-z][a-z0-9-]{1,15} \*/$` (same spec as Gen Mode line 130). The `<slug>` character class is only `[a-z0-9-]`, forbidding path elements like `/` `.` `..` — because `$PRESET` is subsequently concatenated directly into the output filename `brief-{preset}-{date}.md`.
- If `tokens.css` does not exist or the first-line regex does not match → print to stderr 「未找到 tokens.css 或無 preset 註解；請先跑 `/baransu:design preset <name>`」 and exit 1.

#### Step 2 — Read source files
- `{project_root}/DESIGN.md` (full text, for §9 hex rationale + §G editorial + §J quote extraction).
- `{project_root}/tokens.css` (full text; additionally parse the hex values of `--accent` / `--paper` / `--surface`, **read dynamically**, not hard-coded).
- `{project_root}/design-cores/*.html` (the filename list + the first 30 lines of inline `<style>` per file, as raw material for the structure summary).
- `{skill_dir}/references/{$PRESET}-preset/image-prompts.md` (full text, for the §J negative tail and fallback quotes).
- `{skill_dir}/references/{$PRESET}-preset/schemas/*.md` (filename list; take names only, do not expand the full text).

#### Step 3 — Assemble the brief (markdown block)
- **Section A — Preset header**: preset name + a one-sentence philosophy caption (extracted from DESIGN.md §1).
- **Section B — §9 hex rationale**: extract the three subsections `DESIGN.md §9 (a) 焦點 / (b) hex 設計理據 / (c) 我不是什麼`. All hex values are **dynamically parsed from the current `tokens.css`** by Step 2; **do not** hard-code Kami `#1B365D`; if `$PRESET=swiss` then `--accent: #002FA7`, if `$PRESET=google-design` then `--accent: #6750A4` (all derived from tokens.css parsing, switching automatically when the preset is switched and re-run).
- **Section C — §J negative tail**: take the string 「no title, no footer, no page chrome, no logo, no border」 from `image-prompts.md` + three fallback quotes.
- **Section D — §G editorial spec**: dropcap 3-line / `text-wrap: pretty` / curly quotes (Kami spec quotation; **forbid** straight quotes).
- **Section E — design-cores structure summary**: one line per schema + one line per slide-core (laid out from the file list gathered in Step 2).
- **Section F — Codex CLI bridge wording**: plain-text guidance (no MCP implementation), including an invocation example:

  ```
  ## Codex CLI bridge usage
  Pipe this brief to Codex's image-gen prompt input:
  $ codex prompt --stdin < brief-{preset}-{date}.md
  Then append your image-specific prompt suffix.
  ```

#### Step 4 — Output
- **Default**: write to `{project_root}/.claude/design/brief-{preset}-{date}.md`, `{date}` is ISO `YYYY-MM-DD`; `mkdir -p` automatically if the directory does not exist.
- **`--stdout`**: print to stdout, no file written.
- **Success message** (file-write mode): 「Brief 已寫入 {path}（{word_count} 詞）。可餵 Codex CLI 端做 image-gen prompt。」

> **B20 boundary**: all hex values in the brief MUST be parsed by Step 2 from the current preset's `tokens.css`; after switching preset and re-running export-brief, the hex pointers must switch automatically (acceptance: see REQ-007 Scenario 3).

---

## check.py tool (v1.3)

`scripts/check.py` provides two modes:

**v1.3 project-root mode** (no args, or arg = project root): runs the Check A–F structure + consistency checks (see the Lint Mode section).

**Legacy per-file mode** (arg = a single file or dir): retains the v1.2 generic lint rules (cool-gray blocklist / italics / heading-weight / line-height / shadow-blur) for /book GATE-F interop + 紙 preset sanity script use.

Exit codes: 0 = clean, 1 = violations, 2 = structural error.

---

## Validator division of labor (v1.3)

- `scripts/check.py` (project-root mode): A 5 artifacts complete / B full 36 canonical + v1.2 banned detection / C cross-artifact prefix consistency / D DESIGN.md nine sections + canonical references / E long-form slot unique / F dashboard purely static
- `scripts/check.py` (legacy per-file mode): called by `/book` validate-output.ts on the GATE-F path; used by the sanity script to verify the Kami ten invariants
- On the `/book` side, `validate-output.ts` GATE-F (class prefix allowlist dynamically expanded to `{kami, google, swiss}` + first-line slug of tokens.css) + GATE-G (filesystem dynamic read)

### Slide-core image handling (PPT only)

When a slide-core carries an `<img>` / `background-image`, set the per-layout `object-fit` / `object-position` defaults (e.g. portrait focus `center 35%`, data charts `contain`) and append the verbatim negative tail `no title, no footer, no page chrome, no logo, no border` to any external image-gen prompt → **read `references/slide-image-prompts.md`** (scope: `--format ppt` slide-cores only; long-form is exempt). Pull the per-layout values and prompt templates from that file — do not invent crop ratios.

---

## Anti-patterns (skill-operation blacklist)

🔴 Operator red lines for this skill — each entry is `❌ don't do X → because Y (failure consequence) → ✅ do Z instead`. Honoring the GATEs/CHECKPOINTs in §Decision checkpoint map is mandatory; the entries below name the specific traps that bypass them.

- ❌ Don't write to project root while the 🔴 GATE — destructive overwrite is firing (v1.2 residue detected, no `--force`) → because it destroys the user's existing artifacts (tokens.css / DESIGN.md / design-cores/ / slide-cores/) with no backup, irreversibly → ✅ honor the GATE: only write when `--force` is present or no residue exists (Preset Mode Step 3).
- ❌ Don't leave placeholder hex or invent color values in DESIGN.md §2 → because it breaks lint Check B/D (canonical reference) and export-brief's dynamic hex resolution, which reads each named color from the live `tokens.css` → ✅ give every named color a real hex; never hard-code Kami `#1B365D` into a non-Kami preset's output.
- ❌ Don't write the 5 artifacts straight to project root, skipping atomic staging → because an IO interrupt (SIGTERM/SIGINT) mid-write leaves a half-applied artifact set with no rollback → ✅ always stage to `.tmp/design-staging/` first, then atomic-mv only after all 5 succeed (Preset/Gen Mode Step 3).
- ❌ Don't treat `lint` / `Lint` / `LINT` as synonyms → because Mode Dispatch is case-sensitive: only lowercase `lint` enters lint mode, and the others silently fall through to gen mode → ✅ match `lint` (lowercase exact) before dispatching.
- ❌ Don't confuse `DESIGN.md` (uppercase, UI visual spec, this skill) with `design.md` (lowercase, `/analyze` technical layer) → because writing to the wrong one corrupts an unrelated artifact and the lint Check D nine-section gate will not catch it → ✅ this skill only ever reads/writes uppercase `DESIGN.md` at project root.

---

## Error Handling

Detailed entries → read `references/error-codes.md`. Common cases:
- preset name not in the enum / v1.2 residue without `--force` → stderr + exit ≠ 0
- staging IO fail / atomic mv fail → keep staging, leave the project root unchanged
- gen --slug missing / pattern fail / name collision → reject
- any lint check fails → list the specific violation + exit 1
