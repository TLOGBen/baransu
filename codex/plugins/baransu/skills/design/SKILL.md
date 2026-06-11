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

## Outcome Contract

- **Outcome**: The requested mode delivers a complete design-system artifact set, a lint verdict, or a cross-tool brief.
- **Done when**: gen/preset — the five artifacts (`tokens.css` / `DESIGN.md` / `DESIGN.html` / `design-cores/` / `slide-cores/`) are atomically written at project root; lint — `python3 scripts/check.py` exits 0 (clean) or 1 with violations listed; export-brief — `.claude/design/brief-{preset}-{date}.md` is written (or printed with `--stdout`).
- **Evidence**: The mode's completion message (「✅ 已套用…」 / lint pass-fail line with violation list / 「Brief 已寫入…」) and `check.py` exit code.
- **Output**: Project-root design artifacts, a lint report, or a prompt-ready brief markdown file.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Stage 0 — Inject DESIGN.md reference into context files

Before mode dispatch, proactively ensure that AGENTS.md, AGENT.md, and INSTRUCTION.md (any that exist at the project root) carry a top-of-file reminder to read DESIGN.md when handling UI/UX work.

### Steps

1. Resolve project root: `git rev-parse --show-toplevel`. If the command fails, use the current working directory.

2. For each of the following files — **in this order** — if the file exists at `{root}`:
   - `AGENTS.md`
   - `AGENT.md`
   - `INSTRUCTION.md`

   a. Read the first 30 lines of the file.
   b. Locate the current baransu design-system block. Two markers identify a block as current-version (v1.3):
      - 含 `- slide-cores/`（v1.3 加入；v1.2 inject 沒有此行）
      - 含 `canonical 36-name vocabulary`（v1.3 schema marker）
   c. Decide action：
      - **No block found**（一般完全沒被注入過）→ insert canonical v1.3 block at line 2（或在 YAML frontmatter 後 / first heading 後 — 取最早合理位置）
      - **Stale block found**（含 `DESIGN.md` 但缺 v1.3 markers — 例如 v1.2 inject 殘留）→ **替換** stale block 為 canonical v1.3 block；保留檔案其他內容不動
      - **Current block found**（v1.3 markers 齊備）→ skip silently（idempotent）
   d. Canonical v1.3 block 文字：

      ```
      When working on any UI/UX content, read the design system at the project root and follow it:
      - DESIGN.md — visual spec (nine-section design system)
      - tokens.css — CSS variables (canonical 36-name vocabulary; first line `/* preset: <slug> */`)
      - design-cores/ — component skeletons consuming the tokens (long-form / gallery / dashboard / 6 elements)
      - slide-cores/ — slide layouts (4 cover variants + 8 non-cover layouts)
      ```

      Stale-block 替換邏輯：找到第一個含 `When working on any UI/UX` 起始的段落（連續以 `-` 開頭的 bullet 直到空行為界），整段替換為 canonical block。
   e. Output：
      - 新插入 → 「已在 {filename} 開頭插入 DESIGN.md 引用（v1.3）。」
      - 升級替換 → 「已將 {filename} 內 v1.2 design 引用 block 升級為 v1.3。」
      - skip → 不輸出。

3. If none of the three files exist → skip silently. Do not create any of them.

This stage is non-blocking and does not affect mode dispatch.

---

## Canonical Token Schema (v1.3)

v1.3 fixed vocabulary：36 canonical token names 由所有 preset 的 `tokens.css` **必填**；HTML 骨架只透過這些 names 引用 token，preset-specific names（Material `--md-*` / v1.2 `--brand`）以 alias 形式映射。完整 schema（surface 5 / accent 2 / text 5 / border 2 / font 3 / shadow 2 / space 7 / radius 7 / layout 3 / semantic 2）+ v1.2 banned 命名清單 → **讀 `references/canonical-tokens.md`**。

`tokens.css` 第一行 `/* preset: <slug> */` 識別 preset；由 `scripts/check.py` 與 `/baransu:book` GATE-F 解析。


## Mode Dispatch (v1.3, v1.4 export-brief)

Parse the first token of the user's input (after `/design`):

| First token | Mode |
|-------------|------|
| `lint` (lowercase exact match) | Lint mode |
| `preset` | Preset mode (second token = preset name) |
| `gen` | Gen mode (requires `--slug <slug>`) |
| `export-brief` | Export-brief mode (v1.4 — see §Export-brief Mode) |
| anything else (or no input) | Gen mode (legacy alias — but `--slug` 仍強制) |

Case-sensitive. `Lint` or `LINT` do not match lint mode. `export-brief` must be lowercase exact match.

`preset` 模式第二 token 為 preset 名：

| Second token | Preset route |
|--------------|--------------|
| `紙` | Kami preset (warm parchment, ink-blue, serif) — slug `kami` |
| `google-design` | Google Material 3 preset — slug `google-design` |
| `swiss` | Swiss preset (IKB accent, sans-serif) — slug `swiss` |

v1.3 統一 routing — 三 preset 共用相同 atomic staging pipeline（Step 3），全部產出 5 份 artifact（tokens.css / DESIGN.md / DESIGN.html / design-cores/ / slide-cores/）。v1.2 共用 `references/cores/` 與 `references/slide-cores/` 兩目錄已廢除，所有骨架均移至各 preset 內部 `references/<name>-preset/{design-cores,slide-cores}/`。

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

**規格 → 讀 `references/render-design-html.md`**（與 Gen Mode Step 3 共用同份規格）。

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

Use ask the user directly to ask 3–5 design direction questions. Suggested questions (adapt based on what the user already provided):

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

**規格 → 讀 `references/render-design-html.md`**（含 7-section structure + 技術需求 + 寫入位置 + 成功訊息）。


### Step 4 — Offer AGENTS.md injection (optional)

After writing DESIGN.md and DESIGN.html, ask the user:

```
ask the user directly:
  question: "是否將設計語境寫入專案 AGENTS.md？"
  header: "DESIGN.md 已完成"
  options:
    1. label: "寫入 AGENTS.md"
       description: "在專案 AGENTS.md 追加一行，標注 DESIGN.md 的設計語境，讓非 baransu session 也能繼承。"
    2. label: "不需要"
       description: "只保留 DESIGN.md，不修改 AGENTS.md。"
```

If user chooses to write:
1. Run `grep -q "DESIGN.md" {project_root}/AGENTS.md 2>/dev/null`
2. If the string already exists → skip (idempotent), output 「AGENTS.md 已包含 DESIGN.md 引用，跳過。」
3. If not found → append one line to AGENTS.md:
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
| **D. DESIGN.md 九段 + canonical 引用** | 九段標題全在（canonical list lives in `scripts/check.py` Check D），且內文不含 v1.2 token 命名 | 缺段、順序顛倒、或內文含 v1.2 命名即 fail |
| **E. long-form.html slot 唯一** | `design-cores/long-form.html` 含且僅含一個 `<section data-slot="long-form-body">` | 多個或零個皆 fail |
| **F. dashboard.html 純靜態** | `design-cores/dashboard.html` 不含 `<script>` 或外部 `src=http(s)://` | 任一出現即 fail |

### 輸出

- 全通過：`✅ /design lint pass — 5 file(s) checked, no violations.` + exit 0
- 任一 fail：`❌ N violation(s) in M file(s):` + 每項 `L<line> [#<inv> <name>] <msg>` + exit 1
- 結構錯（spec dir 不存在）：exit 2

### Kami sanity 守護

紙 preset 自帶的 `紙-sanity.sh` 是獨立工具（lint mode 不跑），自動定位 `check.py` 後以 legacy per-file mode 逐檔跑 DESIGN.md + design-cores/ + slide-cores/，套用 check.py 內建的 Kami 十不變量規則（warm-tones / italics / heading-weight 等），並附帶 schemas 存在性、object-position、editorial-sanity 等延伸檢查。其他 preset 不繼承此 sanity，保留 lint mode preset-agnostic 性質。

---

## Export-brief Mode (v1.4)

Cross-tool brief packaging — 打包當下 preset 的 DESIGN.md + tokens.css + design-cores 結構為單一 prompt-ready 純文字 markdown，可餵 Codex CLI / ChatGPT Images 2.0 端做 cross-tool image-gen。

### Invocation

```
/baransu:design export-brief            # 寫到 {project_root}/.claude/design/brief-{preset}-{date}.md
/baransu:design export-brief --stdout   # 印到 stdout，不寫檔
```

### Input

- 當下 preset：從 `{project_root}/tokens.css` 首行 `/* preset: <slug> */` 註解解析。
  - tokens.css 不存在或首行不符 regex → stderr 印「找不到 preset header；請先跑 `/baransu:design preset <name>`」+ exit ≠ 0。

### Output

- **預設**：markdown 寫到 `{project_root}/.claude/design/brief-{preset}-{date}.md`（`{date}` 為 ISO `YYYY-MM-DD`）；若 `.claude/design/` 不存在則自動建立。
- **`--stdout`**：純 markdown 區塊直接印到 stdout，不落地。

### Step-by-step assembly

#### Step 1 — 解析 preset
- 讀 `{project_root}/tokens.css` 首行。
- 解析 `/* preset: <slug> */` 註解，取得 `$PRESET`（`kami` / `swiss` / `google-design`，或 user 透過 `gen --slug` 自製的 slug）。
- **Canonical regex (path-traversal hardening)**：首行必須完全符合 `^/\* preset: [a-z][a-z0-9-]{1,15} \*/$`（同 Gen Mode line 130 規格）。`<slug>` 字元類別僅 `[a-z0-9-]`，禁止 `/` `.` `..` 等 path 元素 — 因 `$PRESET` 後續直接拼進 output 檔名 `brief-{preset}-{date}.md`。
- 若 `tokens.css` 不存在或首行 regex 不符 → stderr 印「未找到 tokens.css 或無 preset 註解；請先跑 `/baransu:design preset <name>`」並 exit 1。

#### Step 2 — 讀 source files
- `{project_root}/DESIGN.md`（全文，供 §9 hex 理據 + §G editorial + §J 引述截取）。
- `{project_root}/tokens.css`（全文；額外解析 `--accent` / `--paper` / `--surface` 的 hex 值，**動態取值**，不寫死）。
- `{project_root}/design-cores/*.html`（檔名清單 + 每檔開頭 30 行 inline `<style>`，作為結構摘要原料）。
- `{skill_dir}/references/{$PRESET}-preset/image-prompts.md`（全文，供 §J 負面尾巴與 fallback 引述）。
- `{skill_dir}/references/{$PRESET}-preset/schemas/*.md`（檔名清單，僅取名稱不展開全文）。

#### Step 3 — 組裝 brief（markdown 區塊）
- **Section A — Preset header**：preset 名稱 + 一句哲學 caption（從 DESIGN.md §1 截取）。
- **Section B — §9 hex 理據**：截 `DESIGN.md §9 (a) 焦點 / (b) hex 設計理據 / (c) 我不是什麼` 三小節。所有 hex 值由 Step 2 從**當前 `tokens.css` 動態解析**，**不得**寫死 Kami `#1B365D`；若 `$PRESET=swiss` 則 `--accent: #002FA7`、`$PRESET=google-design` 則 `--accent: #6750A4`（皆由 tokens.css 解析而來，切 preset 重跑時自動跟著切）。
- **Section C — §J 負面尾巴**：從 `image-prompts.md` 取「no title, no footer, no page chrome, no logo, no border」字串 + 三段 fallback 引述。
- **Section D — §G editorial 規格**：dropcap 3-line / `text-wrap: pretty` / curly quotes（Kami spec quotation；**禁** straight quotes）。
- **Section E — design-cores 結構摘要**：每個 schema 一行 + 每個 slide-core 一行（從 Step 2 蒐集的 file list 鋪成）。
- **Section F — Codex CLI bridge wording**：純文字指引（不實作 MCP），含 invocation 範例：

  ```
  ## Codex CLI bridge usage
  Pipe this brief to Codex's image-gen prompt input:
  $ codex prompt --stdin < brief-{preset}-{date}.md
  Then append your image-specific prompt suffix.
  ```

#### Step 4 — 輸出
- **預設**：寫到 `{project_root}/.claude/design/brief-{preset}-{date}.md`，`{date}` 為 ISO `YYYY-MM-DD`；目錄不存在則自動 `mkdir -p`。
- **`--stdout`**：印到 stdout，不寫檔。
- **成功訊息**（寫檔模式）：「Brief 已寫入 {path}（{word_count} 詞）。可餵 Codex CLI 端做 image-gen prompt。」

> **B20 邊界**：brief 內所有 hex 值 MUST 從 Step 2 解析自當前 preset 的 `tokens.css`；切 preset 後重跑 export-brief，hex pointers 必須自動跟著切換（驗收見 REQ-007 Scenario 3）。

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

詳細條目 → 讀 `references/error-codes.md`。常見：
- preset name 不在 enum / v1.2 殘留無 `--force` → stderr + exit ≠ 0
- staging IO fail / atomic mv fail → 保留 staging、project root 不變
- gen --slug missing / pattern fail / 撞名 → reject
- lint 任一 check fail → 列具體 violation + exit 1

