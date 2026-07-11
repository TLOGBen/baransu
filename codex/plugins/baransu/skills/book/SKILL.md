---
name: book
description: 'Converts any content source into a beautifully rendered, browser-ready
  HTML document. Runs a three-stage pipeline: Acquire (URL / slug / local path / text)
  → Synthesize (classify content type, extract structure) → Render (Kami-themed HTML
  + SVG, quality-gated). Trigger On ''/book'', ''轉成 book'', ''做成 HTML book'', ''存成
  book''. Not for producing an editable Markdown artifact (use /read for offline source
  capture, /learn for a digested note) — /book only emits rendered browser-ready HTML.'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

Converts any content into a Kami-themed, browser-ready HTML book saved to `.claude/book/{slug}.html`.

**User-facing language**: 繁體中文. All output shown to the user must be in Traditional Chinese.

---

## Outcome Contract

- **Outcome**: Convert any content source (URL / slug / local file / text) through the three stages Acquire → Synthesize → Render into a Kami-themed, browser-openable HTML book.
- **Done when**: The output HTML passes all GATEs of scripts/validate-output.ts (exit 0), and the file lands at `.claude/book/{slug}.html`.
- **Evidence**: The execution result of validate-output.ts (GATE A-E / F / G / J / K / L all green or a legitimate SKIP).
- **Output**: `.claude/book/{slug}.html`; per `--format` additionally includes `.pdf` / `.pptx`.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Constraints

- **Token source = project root**: all visual elements consume tokens from `{project_root}/tokens.css` (written by `/baransu:design preset <style>` or `/baransu:design gen --slug <slug>`) plus the component patterns in `{project_root}/design-cores/long-form.html` (SSOT) or `references/golden-template.html` (fallback). No inline hex colours; use named CSS variables (canonical 38 base names; +5 capability for schema:43).
- **Soft generation inside the hard floor**: the render generates layout within the preset's §9 expression range (Stage 3 §3), using the SSOT template / fallback as reference exemplars rather than a closed class whitelist. The non-negotiable floor is the token boundary — every color routes through the canonical token (38 base names; +5 capability for schema:43), no bare hex. In PPT mode validate-output.ts (GATE-F) mechanically enforces the class-prefix subset of this floor; in html (long-form) mode GATE-F SKIPs, so the floor is guarded by the Stage 3 §3 pre-write checklist instead; the soft §9 range is judged by style-reviewer.
- **SVG required**: a document with 0 SVG diagrams fails the quality gate and must be fixed before completion.
- **Length cap**: final HTML body ≤ 1800 words. Excess goes into a 延伸閱讀 link block.
- **No LLM-generated commentary**: the rendered HTML contains the source content, structured and styled — not Claude's own analysis. The Synthesize stage extracts; the Render stage presents.
- **Partial failure**: if Acquire fails for one of multiple inputs, report the failure per-input and continue with the rest.

## Red Lines (what not to do)

Scan the forbidden zone via the 🛑 visual marker, not by reading through prose. Each item below restates an existing rule; violating it = that output is compromised; each row carries a "why compromised" rationale anchor and the correct approach.

| 🛑 Anti-pattern | Why it's compromised (rationale anchor) | Correct approach (authoritative reference) |
|----------|---------------------|--------------------------|
| 🛑 Using inline / bare hex colors instead of canonical tokens | Breaks the GATE-F canonical-token list (38 base names; +5 capability for schema:43) — the hard safety floor the soft generation lives inside — regressing to generic AI feel | every color routes through a canonical-name variable; the layout may be generated within the §9 range but never with bare hex (§3.3, Constraints; perception-guide Anti-Slop Blacklist #7) |
| 🛑 Using `rgba()` for SVG fill / stroke | WeasyPrint composites the alpha into a double-rectangle ghost-border, distorting the PDF | SVG fill/stroke must always be a solid hex token (§3.4, svg-rendering-rules §4.1) |
| 🛑 Free-styling node widths outside the 3-step whitelist | Mixing all 3 whitelist steps in one diagram is an anti-slop fail and breaks the diagram rhythm | node width limited to {128/144/160}, at most 2 steps per diagram (svg-rendering-rules §4.7) |
| 🛑 Silently producing an empty page / skeleton when Acquire fails | Disguises failure as a successful output, leaving the user with an empty shell | report each failure clearly, do not produce an empty shell (Gotchas SPA, Constraints Partial failure) |
| 🛑 Falling back to `find` / sibling-skill paths when `tokens.css` is missing | Violates the invariant that the sole token source = project root | tokens.css missing → abort and prompt to run `/baransu:design preset` first (Gotchas Missing project-root tokens, §3.1) |
| 🛑 Skipping a Core Asset step (freezing before verifying) | The 4-step protocol's ordering guarantees "freeze only when there's no AI slop"; skipping bypasses quality confirmation | Ask → Generate/Search → Verify → Freeze strictly in order (§3.5) |
| 🛑 Writing Claude's self-assessment / commentary / analysis into the HTML | The output should be structured source content, not the model's own argumentation | Synthesize extracts, Render presents; do not smuggle in LLM commentary (Constraints No LLM-generated commentary) |

## Stage 0 — Environment Self-Check

> This SKILL.md adopts Fact-Verification Principle #0 (see the Stage 2A §0 "Fact-Verification Principle #0" section below): before synthesizing long-form text, whenever a concrete product / version / person-name + title pattern is detected, search the web verification is forced; 0 results triggers a user-question block.

### 1. Design context soft-read

Runs before all other Stage 0 steps. Follows the same soft-read pattern as /design / /analyze, bringing the current preset's design philosophy into context as advisory framing.

1. Resolve project root: `git rev-parse --show-toplevel 2>/dev/null`; on failure use cwd.
2. Attempt to read the following files (all best-effort, **failing all of them does not abort Stage 0**, only a stderr warning):
   - `{project_root}/DESIGN.md`: the current preset's nine-section design spec, **including §9's expression-range fields** (承諾的極端 / 空間原則 / 不對稱·重疊允許度 / 欄寬上限 / 強調色紀律) when present. Read into context for later Stage 2A typography selection and as the soft-range input the Stage 3 §3 render generates layout within.
   - `{project_root}/tokens.css` first line: parse the preset slug (e.g. `/* preset: kami */` → `kami`), store as the `$STYLE` prepared value (later overridden if the user explicitly passes `--style`, otherwise this value is kept).
3. If `DESIGN.md` exists → stderr `已載入 DESIGN.md，視覺規格已參考（preset=$STYLE）`.
4. If `DESIGN.md` does not exist → stderr `未找到 DESIGN.md；建議先跑 /baransu:design preset <name>。本次 /book 將使用 fallback 模板，視覺風格可能與 preset 不一致`, then continue.

The DESIGN.md content read in this step is, in Stage 4, passed to the style-reviewer as a spec anchor depending on whether the user triggers `/baransu:review --include=style`; in the normal /book flow it serves only as a generation-time advisory and affects no gate.

### 2. --format flag parsing

Parse the `--format` flag in the user's invocation:

- Supported values: `html` | `pdf` | `ppt` | `all`
- If `--format` is not provided: default to `html`
- If the value is invalid (not html/pdf/ppt/all): output 「`--format` 值不合法。支援：html | pdf | ppt | all」 and stop (do not call install-deps.ts)
- Set `$FORMAT` for use by all later Stages

### 3. --style flag parsing

Parse the `--style` flag in the user's invocation (v1.3 PPT + HTML dual mode):

- Supported values: `kami` | `google-design` | `swiss` | user-supplied gen slug (pattern `/^[a-z][a-z0-9-]{1,15}$/`, must have run `/baransu:design gen --slug <slug>` first)
- If `--style` is not provided: parse from `{project_root}/tokens.css` first line `/* preset: <slug> */`; if neither is present, default to `kami`
- Invalid value: output 「--style 不合法。支援 v1.3 三 preset 或已註冊 gen slug」 and stop
- HTML mode dynamically reads the template from `{project_root}/design-cores/long-form.html`; PPT mode dynamically reads the layout from `{project_root}/slide-cores/`
- Set `$STYLE` for use by later Stages (Stage 3 tokens.css tie-break / GATE-F prefix matching reads `$STYLE`)

### 4. Python check

```bash
python3 --version 2>/dev/null
```

If this fails: output 「Python 3.8+ 未安裝，無法繼續。請先安裝 Python: https://python.org」 and stop.

### 5. Platform detection

- **WSL2**: `grep -qi microsoft /proc/version 2>/dev/null && echo wsl2` → set `$PLATFORM=WSL2`
- **macOS**: `uname -s 2>/dev/null | grep -qi darwin && echo macos` → set `$PLATFORM=macOS`
- **Otherwise**: set `$PLATFORM=Linux`

### 6. Dependency install (markitdown included)

Installing packages mutates the local environment, so the installer never runs unconditionally. Gate it with an explicit probe → if-then flow:

1. **Probe first (list, no install)**: run the format-aware installer in dry-run/probe mode to list the packages this `$FORMAT` would newly install (the script already probes `python3 -m markitdown --version` itself, so no separate manual markitdown check is needed):

```bash
npx tsx "./scripts/install-deps.ts" --format $FORMAT --dry-run
```

If the script does not support `--dry-run` (it exits non-zero with an unknown-flag error), fall back to probing each `$FORMAT`-required dependency directly — `python3 -m markitdown --version`; plus WeasyPrint when `$FORMAT` contains `pdf`; plus playwright + pptxgenjs when `$FORMAT` contains `ppt` — and assemble the miss list yourself. Either way, store the would-be-installed packages as `$INSTALL_LIST`.

2. **IF `$INSTALL_LIST` is empty** → every dependency is already present; skip installation entirely and continue to §7.

3. **IF `$INSTALL_LIST` is non-empty AND the run is interactive** → 🔴 CHECKPOINT — install confirmation: via `numbered-options question`, reveal the exact list before touching the environment: 「本次 --format {$FORMAT} 需要新安裝以下套件：{$INSTALL_LIST}。要安裝並繼續嗎？（安裝並繼續 / 中止本次 /book）」. Only after the user confirms, run the real install:

```bash
npx tsx "./scripts/install-deps.ts" --format $FORMAT
```

If the user declines: output 「已取消安裝，/book 中止。」 and stop.

4. **IF `$INSTALL_LIST` is non-empty AND the run is driven non-interactively** (/loop, cron, Workflow) → this is an **Input PAUSE** (classification: `references/loop-pauses.md`): take the default (安裝並繼續) without stopping — the non-interactive path must never hard-stop here, preserving the Outcome Contract's loop=drivable — run the same real install command, and **annotate the actually-installed package list in the Stage 4 completion report** (one line: 「本次自動安裝套件：{$INSTALL_LIST}」).

If the real install returns a non-zero exit code:
- Output the error message (the script has already listed details) and stop; do not enter Stage 1
- If `$FORMAT` contains `pdf`: confirm WeasyPrint is available
- If `$FORMAT` contains `ppt`: confirm playwright + pptxgenjs are available

### 7. Output directory

Ensure `.claude/book/` exists relative to the project root:

```bash
mkdir -p ".claude/book"
```

---

## Stage 0b — 🔴 CHECKPOINT — Pre-interview Gate (audience / hard-constraint front-loading)

**Before** Stage 1 acquires `$RAW_CONTENT`, first suppress 50% of the uncertainty. Pattern aligned with /design Gen Mode Step 1: use a **single direct user question with numbered options (stop for the user's reply) batch** (4 questions presented together, not blocking question-by-question) to align audience, purpose, style leaning, and hard constraints.

### Skip conditions (the whole section is skipped if any one holds)

- The `--auto` or `--no-interview` flag is present
- The run is driven non-interactively (/loop, cron, Workflow) — same default as `--auto`; see `references/loop-pauses.md`
- The input is a `/read` slug / `/learn` digest slug (audience + purpose are already implicit in the original capture metadata)
- The input is `--text "…"` with word count < 200 (an extremely short inline is not worth asking about)

When skipping, print one stderr line: 「Stage 0b skipped: {reason}」, then continue to Stage 1.

### Interview questions (batched, 4 questions presented together)

1. **Audience** — 「主要讀者是誰？（例如：技術同儕 / 產品 PM / 非技術主管 / 公開讀者 / 自己備忘）」
2. **Purpose and duration** — 「這份 book 的使用情境？（例如：5 分鐘速讀 / 30 分鐘深讀 / 簡報前置 / 長期參考文件）」
3. **Style leaning** — 「視覺密度偏哪邊？（例如：高密度技術文件 / 留白敘事散文 / 多圖表 research 報告 / 隨 preset 預設）」
4. **Hard constraints** — 「有沒有必須 / 不要的元素？（例如：必含某段內文、不要 SVG diagram、限定字數、特定 callout 數）」

Unanswered / 「隨預設」 always follows the preset's existing default and is not separately stored. Answered content is written into `$INTERVIEW_BRIEF` (plain text 4-8 lines), prepended as advisory framing before Stage 2A §1 classification, and **does not override** the existing A/B/C classification logic in `references/perception-guide.md` (on conflict, perception-guide wins; the brief is only a nudge).

### Completion output

One line: 「訪談完成：受眾={...} / 用途={...} / 風格={...} / 約束={...}，進入 Stage 1。」

---

## Stage 1 — Acquire

Route the input argument to the correct acquisition path. The goal is to produce a
**plain-text or Markdown body** stored in a temp variable `$RAW_CONTENT`.

### 1. URL (`http://` or `https://` prefix)

Follow the same proxy cascade as `/read` Stage 1 §9:

```
Layer 1: curl -sL "https://defuddle.md/{url}" → check word count > 100 and lines > 5
Layer 2: curl -sL "https://r.jina.ai/{url}"   → same quality checks
Layer 3: curl -sL "{url}" -H "User-Agent: Mozilla/5.0"
```

Store the best result in a temp file `/tmp/book-raw-{slug}.{ext}`, where `{slug}` here is an **initial working slug** — the URL's host + path stem (as /read uses), since the definitive `$SLUG` does not exist yet at Stage 1; Stage 2A §5's derived `$SLUG` supersedes this working slug for all output paths.
Convert to Markdown via `markitdown "/tmp/book-raw-{slug}.{ext}" -o "/tmp/book-body-{slug}.md" 2>/dev/null`.
Set `$RAW_CONTENT` to the content of `/tmp/book-body-{slug}.md`.

If all three layers fail or produce < 100 words:
- output 「Acquire 失敗：{url} 無法取得內容。請改用 --text「貼入文字」或確認 URL 是否可公開存取。」 and stop.

### 2. `/read` slug or `/learn` digest slug

If the input matches the slug pattern (no `http://`, `./`, `/`, `*` prefix and no `--` prefix):

Check the following paths in order:
1. `.claude/learn/digests/{slug}.md`
2. `.claude/read/material/{slug}/index.md`

If found: read the file; set `$RAW_CONTENT` to its body (strip YAML frontmatter).
If not found: first check whether the input is actually a local file (`test -e "{input}"` — a bare filename like `notes.md` matches this slug pattern too); if it exists, route to §3 (local file). Only when it is neither a known slug nor an existing file: treat as a bare topic → go to §4 (plain text).

### 3. Local file path (`./`, `/`, or existing file)

```bash
test -e "{input}" && echo "exists" || echo "missing"
```

If exists: run `markitdown "{input}" -o "/tmp/book-body-local.md" 2>/dev/null`; set `$RAW_CONTENT`.
If missing: output 「找不到檔案：{input}」 and stop.

### 4. Plain text / bare topic

If the input is a bare topic (no URL, no file, no known slug): set `$RAW_CONTENT = input` directly.
This enables `/book "agent 協作方式"` where the user types the content inline.

### 5. `--text "…"` flag

User can pass `--text "…"` to explicitly force plain-text mode regardless of input shape.
Set `$RAW_CONTENT` to the quoted string.

### Acquire completion

Output one progress line:
「已取得內容（{word_count} 詞），開始分析…」

---

## Stage 2A — Synthesize (long-form, all formats)

Receives `$RAW_CONTENT`. Produces `$STRUCTURE` (a JSON-like outline) and `$CONTENT_TYPE`.

### 0. Fact-Verification Principle #0

**Purpose**: run a fact gate before long-form synthesis enters §1 classification, preventing hallucinated concrete specs (fabricated version numbers, fabricated person titles) from being written into the final HTML.

**Trigger regex** (soft-match against the full `$RAW_CONTENT`; not all hits are required and a miss is not an error — it only serves as a signal to trigger search the web):

```
/([A-Z][a-zA-Z]+\s+((MCP|SDK|CLI|API)\s+v?\d+(\.\d+)*|v\d+(\.\d+)+))|([A-Z][a-z]+\s+[A-Z][a-z]+(\s|,)+(CEO|CTO|founder|engineer))/
```

Explanation:
- First-half alternation: product name (capitalized word) + **either** an MCP/SDK/CLI/API token followed by a version number **or** a `v`-prefixed dotted version → matches such as 「Linear MCP v3.4.7」「Anthropic SDK 0.39」「Claude v2.1」. The middle group is deliberately non-optional: a bare capitalized-word + number (「Stage 3」「Python 3」「Windows 11」「Chapter 4」) must NOT trigger — those benign patterns saturate normal technical prose.
- Second-half alternation: person name (two capitalized words) + space or comma + title (CEO/CTO/founder/engineer) → matches such as 「Jane Doe, CTO」.

**Dedup and cap before the flow**: dedup the matched hits (identical strings verify once), then keep at most the **3 most-specific** hits (longest match first — a fully-versioned product string outranks a looser one). Hits beyond the cap are listed in the completion report as unverified, not searched.

**Flow on hit** (for each surviving `{hit}`):

1. **Sanitize `{hit}` before query**: first strip all `"` (`U+0022`) characters inside `{hit}` (the regex captures legitimate identifier/version strings, which normally contain no quote; if present it is noise or adversarial input). The sanitized `{hit_clean}` is then passed to the next step.
2. Run `search the web`, query template: `"{hit_clean}" release notes` or `"{hit_clean}" announcement` (for person-name hits use `"{hit_clean}" announcement` / `"{hit_clean}" interview` instead).
3. If search the web returns **0 results** → 🛑 STOP — Fact-verify pending: via `numbered-options question` show: 「Fact-verify pending: '{hit_clean}' 在 search the web 0 結果。選擇：強制繼續 / 改用 `--text` 餵已驗證版本 / 中止本次 /book」. Wait for the user's choice before deciding whether to enter §1. This is an **Input PAUSE** (classification: `references/loop-pauses.md`): under a non-interactive driver, take 強制繼續 and annotate the unverified hit in the completion report.
4. If search the web returns **≥ 1 result** → treat as fact-verifiable, continue, but still add the hit to the 「Sources」 list at the end of `$STRUCTURE` (handled together in the Stage 2A §4 extract phase).

**Flow on no hit**: enter §1 classification directly.

**Boundary**: the regex is a soft trigger, not a hard match — a miss does not mean the content is necessarily true, and the pattern will be expanded in the future based on telemetry results. **Test fixture**: the string `Linear MCP v3.4.7 released 2025-09-15` is fabricated and is expected to trigger the regex, return 0 search the web results, and go through the ask flow (must not silently continue).

### 1. Classify content type

Read `references/perception-guide.md` once here — it contains the full taxonomy (Technical / Narrative / Research), each category's visual-treatment strategy, SVG strategy, and synthesis length caps (4–8 sections, ≤1800 words). Then run a keyword + structure scan over `$RAW_CONTENT` and resolve `$CONTENT_TYPE` by an explicit threshold rule rather than by judging whether the boundary "feels" clear:

1. Score each of the three candidate categories (`technical` / `narrative` / `research`) by counting the number of **distinct** matched signals (keyword hits, structural cues) for that category in `$RAW_CONTENT`.
2. Rank the three categories by signal count. Let `top` = highest count, `second` = next-highest count.
3. **IF** `top ≥ 2` **AND** `top − second ≥ 2` (the leading category clears the minimum signal floor of 2 distinct signals AND leads the runner-up by a margin of ≥ 2 distinct signals) → assign `$CONTENT_TYPE` to the top category directly.
4. **ELSE** (the lead is within the margin, i.e. `top − second < 2`, **OR** no category reaches the minimum floor, i.e. `top < 2`) → use the perception-guide taxonomy to break the tie and assign `$CONTENT_TYPE`.

### 2. Decide $CONTENT_TYPE

Based on the §1 signal counts (and, on the tie-break branch, the perception-guide taxonomy), assign `$CONTENT_TYPE` to one of:
- `technical` — code, how-to, architecture, tool guides
- `narrative` — essays, opinions, threads, stories
- `research` — analyses, reports, multi-source synthesis

Output one line: 「內容類型偵測：{$CONTENT_TYPE}」

### 3. Two-layer decision tree (Layer 1 content type → Layer 2 diagram structure)

The Stage 2A selection splits into two layers, **the order must not be reversed**:

- **Layer 1 (content type → HTML layout density)**: the `$CONTENT_TYPE` already produced by §2 (A=`technical` / B=`narrative` / C=`research`) determines the whole HTML's layout style — whether the TOC is expanded, number of cards, density, callout style, etc., all given separately for the A/B/C categories by `references/perception-guide.md` (already read in §1). Take the layout density and visual-treatment rules corresponding to that $CONTENT_TYPE.
- **Layer 2 (14-type selection → per-section diagram structure)**: each section containing a diagram independently looks up the Stage 3 §4 「14 型 selection 表」, picking one diagram type based on that section's data shape (architecture / flowchart / sequence / ... / statistical).

The two axes are orthogonal: Layer 1 controls layout, Layer 2 controls each section's SVG structure; do Layer 1 first, then Layer 2, deciding each section independently without inheriting the previous section's choice.

### 4. Extract structure

From `$RAW_CONTENT`, extract:
- **Title** (first `# ` heading, or infer from opening sentence)
- **Kicker** (2–4 word category label)
- **Subtitle** (one-sentence summary of the whole piece)
- **4–8 sections**, each with:
  - Section heading
  - 1–3 key claims (concrete, specific — no vague summaries)
  - Whether this section benefits from an SVG diagram

Store as `$STRUCTURE`.

Apply synthesis length limits from the perception guide. Remaining content → reference as 延伸閱讀 at the bottom.

### 5. Determine slug

Derive `$SLUG` from the title:
- Lowercase all characters
- Replace spaces and non-ASCII with hyphens
- Collapse consecutive hyphens
- Strip leading/trailing hyphens
- Truncate to 60 chars
- **Empty-slug fallback** (an all-CJK title — the common case for 繁中 content — reduces to the empty string): fall back in order to (1) a romanized/translated ASCII rendering of the title, (2) the source URL's path stem (as /read does), (3) a date-stamped `book-{YYYYMMDD}` slug. Never emit `.claude/book/.html`.

Check `.claude/book/` for existing files with the same slug.
If a collision exists: append `_v2`, `_v3`, etc., and **output one Traditional-Chinese notice line so the renamed output is not silent** (notify, not a blocking PAUSE): 「偵測到既有 {slug}.html，本次另存為 {slug}_v2.html（如要覆寫請刪除舊檔後重跑）」, then continue.

**$SLUG is derived only once in Stage 2A; Stage 2B and all Render steps inherit the same $SLUG and do not re-derive it.**

---

## Stage 2B — Synthesize (slides, only --format ppt or all)

Runs only when `$FORMAT` ∈ {`ppt`, `all`}; produces `$STRUCTURE_SLIDES` (6–12 slides, first page fixed as `cover`, last page conditionally `closing`). **The layout is not hard-coded**: dynamically read the YAML front-matter registration decision table of `{project_root}/slide-cores/*.html`, assigning layout_type via first-match + positional override.

**Rule details (10-row decision table / closing condition recognition / graceful degradation / `$STRUCTURE_SLIDES` schema) → read `references/slide-synthesis.md`.**

---

## Stage 3 — Render

Produces a complete HTML file at `.claude/book/{$SLUG}.html`.

### 1. Read the design system

Before generating any HTML:

1. **Sole token source**: read `{project_root}/tokens.css` (written by `/baransu:design preset <style>`; this skill only reads, never modifies). This rule **applies to both** `--format ppt` and `--format html`.
   - If `{project_root}/tokens.css` **does not exist** → error 「請先跑 `/baransu:design preset <style>`（kami / google-design / swiss）」 and **abort Stage 3**.
   - tokens.css begins with a preset-identifying comment (`/* preset: kami */` / `/* preset: google-design */` / `/* preset: swiss */` or a user-supplied gen slug), for the `$STYLE` variable parsed in Stage 0 to do a tie-break comparison in GATE-F.
2. **v1.3 long-form template SSOT dynamic read**: prefer reading `{project_root}/design-cores/long-form.html`, treating `<section data-slot="long-form-body">` as the body insertion point.
   - File **exists but fails to read** (malformed / chmod 000 / 0 bytes) → **hard fail**, no silent fallback; stderr 「long-form.html 讀取失敗：{原因}」, abort Stage 3.
   - File **does not exist** → fall back to `references/golden-template.html` (the v1.2 Kami-style built-in template); stderr warning 「current preset 為 {style} 但 fallback 到 Kami template，class prefix 可能不一致；建議先跑 /baransu:design preset {style}」; continue producing output. (Note: GATE-F runs in PPT mode only and SKIPs on long-form html, so this prefix inconsistency is NOT mechanically detected on the html path — the §3 pre-write checklist and style-reviewer are the only guards there.)

On this fallback path, the golden template has no `<section data-slot="long-form-body">` marker — treat the inside of its `<article class="paper">` element as the body insertion point that §2's `data-slot` section otherwise provides.

The long-form.html slot is a show-by-example contract — the slot demonstrates 6+ section types (heading / paragraph / quote / code / SVG / list), and serves as a *reference exemplar* for generation, **not a fixed class whitelist that the output is limited to**. Token values are provided by `{project_root}/tokens.css`; the template references canonical names (var(--paper) / var(--accent) etc.), and any layout the render generates must likewise route every color through those canonical tokens — no bare hex (this is the unchanged hard safety floor; see §3).

🔴 GATE — before starting to produce HTML, you MUST re-read the 「Output Anti-Slop Blacklist」 and 「Quantified Type Scale」 sections of `references/perception-guide.md` as a render-time standing instruction (Stage 2A §1 read the file early; by render time those rules sit far back in context — refreshing the two render-critical sections immediately before HTML production prevents regressing to generic-AI-feel output).

### 2. Generate HTML structure

Produce the full HTML document using the SSOT template loaded in §1 step 2:

```
<head> with linked tokens.css (use {project_root}/tokens.css; fill {{TITLE}})
<nav class="<slug>-toc"> with <a href="#sN"> for each section
<main>
  <header class="<slug>-cover"> with kicker, h1, subtitle, meta
  <section data-slot="long-form-body">
    <!-- Replace this section's innerHTML with rendered body sections -->
    <section id="sN"> for each section (4–8 sections)
  </section>
  <footer class="<slug>-footer">
</main>
```

`<slug>` is the preset prefix read from `tokens.css` line 1 (kami / google / swiss / gen slug). All class names in output must use that prefix; GATE-F guards consistency in PPT mode only — on long-form html it SKIPs, so the §3 pre-write checklist is the guard.

### 3. Section content rules

For each section from `$STRUCTURE`:

- Open with `<h2><span class="sec-num">0N</span>{Section Title}</h2>`
- Write 1–3 paragraphs expanding the key claims using language from `$RAW_CONTENT`
- Immediately follow with a `<figure class="diagram">` block containing an SVG if the section was flagged for it
- Select a component by the section's data shape, not by feel: a warning/caveat/aside → `.callout`; 3+ parallel sibling items of equal weight → `.card-grid`; a head-to-head of 2+ options across shared dimensions → `table.cmp`; an explicit cost/benefit pair → `.tradeoff-row`; otherwise use plain `<p>`.

**Section rhythm standing instruction (render-time hard rule, not vibes)**: when applying the components above, resolve every "generous" / "tight" / "airy" treatment to a number in `references/perception-guide.md` Quantified Type Scale, never to vibes. Three highest-leverage values are binding at render time — each constrains how existing `long-form.html` template classes / tokens are *used* (no new CSS, no new token):

1. **Inter-section vertical gap = 3xl 80–120pt** between long-doc `<section>` blocks — drive it with the existing spacing token at the 3xl step; never inherit the browser-default margin.
2. **Reading-body line-height locked 1.50–1.55** (CJK on screen may relax to 1.55–1.65); **`≥ 1.70` is banned** (reads as floating web-prose, not print).
3. **Reading column capped 680px / max body width 760px** — wider than this is a slop signal, not "generous".

**Soft generation within bounds (replaces the old fixed-class-whitelist rule)**: the render reads three inputs — `{project_root}/tokens.css`, the current preset's `DESIGN.md` **§9 expression range** (loaded in Stage 0 §1), and the **current article context** (`$STRUCTURE` + `$RAW_CONTENT` + the Stage 0b interview brief) — and **GENERATES** the layout for each section inside the hard safety floor. The output is **NOT limited to a fixed class whitelist that must pre-exist in the SSOT template**; the SSOT template and `references/golden-template.html` are reference exemplars, not the closed set of permissible classes. Within the §9 expression range (its 不對稱/重疊允許度 soft cap, 空間原則 symmetry/grid basis, 欄寬上限) the render may compose section layout to fit the article context (e.g. an asymmetric or break-grid arrangement when §9 permits it), so two different articles under the same preset can differ in layout while staying stylistically consistent. When composing novel visual structure not covered by preset tokens / SSOT templates, the 構成/獨特性 rules of `../design/references/aesthetics-foundation.md` apply — read that file on demand before improvising the layout.

**§9-missing conservative fallback**: when the preset's §9 lacks the expression-range fields (an older preset not yet upgraded), the render does **not** improvise without a range — it falls back to a **conservative symmetric layout** (symmetric spatial basis, the default single-column reading rhythm), generating nothing beyond what the conservative baseline requires.

**Hard floor (unchanged safety boundary the soft generation lives inside)**: regardless of how the layout is generated, **all colors go through canonical tokens (the canonical 38 base names; +5 capability for schema:43) — no bare hex** anywhere in the output. The generated layout is bounded by, never exempt from, this floor; validate-output.ts guards the class-prefix subset in PPT mode (GATE-F — SKIPs on long-form html, where the pre-write checklist below is the guard) and style-reviewer judges the soft §9 range. If a needed component truly has no token-backed expression, prefer plain `<p>` over inventing a bare-hex color.

🔴 GATE — pre-render visual self-check (pre-write checklist): **before** writing the HTML to file in Stage 3 §7, go through the following seven-line binary checklist item by item (each restates an existing reference rule, not a new rule). Any ✗ → fix it then Write, do not write to disk directly; only enter §7 when all seven are ✓.

1. **Inter-section spacing** — is each pair of adjacent `<section>` driven by the 3xl spacing token (80–120pt), not browser-default margin? (§3 render-time hard rule #1)
2. **Reading line-height** — is body line-height ∈ [1.50, 1.55] (CJK screens may relax to 1.65), with no `≥ 1.70` anywhere in the text? (§3 render-time hard rule #2)
3. **Reading column width** — is the reading column ≤ 680px and max body width ≤ 760px? (§3 render-time hard rule #3)
4. **Single accent** — only one chromatic accent (`var(--accent)`) used, accent-painted area ≤ 5% of body, and emphasis is "color OR weight, not both" — with the narrowly-scoped **declared-statistical-chart container exception**: inside a section whose `statistical` chart resolved to the Declared branch of the chart-capability check documented in this file's §4 SVG generation spec below, the chart's own `<figure>`/SVG container may use its multi-color palette without counting against this check; every other element — including that same section's own prose/caption outside the `<figure>` boundary — still must pass unmodified? (perception-guide Anti-Slop #8)
5. **SVG focal + alignment** — each SVG has ≤ 2 `data-role="focal"`, and all coordinates / widths / spacing are multiples of 4? (svg-rendering-rules §4.7)
6. **figcaption** — does each `<figcaption>` pass the perception-guide Anti-Slop #5 pass test (carrying one of: trade-off / next step / a dimension the figure doesn't directly show), rather than merely restating the title or node name? (perception-guide Anti-Slop #5)
7. **Hard-floor color scan** — scanning the generated HTML: zero matches for the bare-hex pattern `#[0-9a-fA-F]{3,8}` outside `<svg>…</svg>` blocks (every non-SVG color routes through a `var(--…)` canonical token; hex inside `<svg>` is legal only when resolved via `references/design-token-resolver.md`), and zero occurrences of `rgba(` inside any `<svg>` block? Any hit → fix before Write. (§3 hard floor; svg-rendering-rules §4.1)

### 4. SVG generation spec

Takes effect only when the long-form HTML contains `<figure class="diagram">`. The spec includes: color tokens (canonical names + Kami hex defaults), the required `<defs>` / marker / two-layer paper-mask, type tag, legend strip, 4px alignment and the 3-step node-width whitelist (128/144/160), embedded-font correction, the 14-type diagram first-match decision tree, and the 14-type selection table (including `status: complete | ref-only`).

**Full rules → read `references/svg-rendering-rules.md`.** SVG fill / stroke **must not use `rgba()`**; node width is limited to 3 steps (128/144/160); focal nodes are marked via `data-role="focal"`, capped at 2 per SVG. Per-type SVG specs live in `references/diagram-types/type-*.md`, selected via that file's §4.10 routing table (its ToC lists §4.9/§4.10 up top).
Token hex resolution (three-layer fallback: project-root tokens.css → built-in presets → per-type derived) → read `references/design-token-resolver.md` before resolving any SVG/CSS hex.

**Statistical-type color-capability degrade (undeclared-style fallback)**: when Layer 2 resolves a section to the `statistical` type (§4.9/§4.10), before writing that section's SVG, Render checks `{project_root}/tokens.css` line 1's header for the `; chart-capability: <N>` field written by `/baransu:design` (declared vs undeclared per `design/scripts/check.py`'s `_parse_chart_capability_header` contract):

- **Declared** (field present) → before writing the section's SVG, Render reads `references/color-reasoning.md` (the categorical / ordinal / sequential / diverging / status color-job distinction, plus the dual-axis / rainbow-gradient / identity-color-without-legend anti-patterns) and applies its guidance when choosing the section's palette, then validates the chosen colors via `color_distance.py`'s CVD-separation check (TASK-shared-01, already wired).
- **Undeclared** (the default; no field present — matching every invocation that never ran `--chart-capability`) → apply this degrade so the section never emits an undeclared multi-color palette. Pick **exactly one** of the two branches below per section — they are mutually exclusive, never mixed, never guessed past the content shape, and together cover every case with no silent gap between them (不開豁免):
  - Content expressible as a single trend / single data series (exactly one line, one bar family, depth conveyed by shade alone) → **L1**: fall back to the existing single-hue `--accent` ramp already used by every other diagram type — no new token, no new color.
  - Content that must distinguish 2 or more mutually-unrelated identities (independent series — including exactly 2 — that do not share a common trend/comparison axis and cannot be told apart by shade depth alone) → **L2**: degrade to small-multiples (render N separate single-accent diagrams, one per series, laid out side by side) or a `table.cmp` comparison table, whichever the section's existing §3 component-selection rule already picks for that content shape. This threshold starts at 2, not 3 — an exactly-2-series undeclared section is never left unrouted between L1 and L2.

### 5. Core Asset Protocol (image acquisition)

Whenever any stage needs to fetch a raster / photographic / logo / UI mockup image, follow the 4 steps below **strictly in order**. **Steps must run in order; skipping = fail and abort.** (Skipping a step is treated as a fail and aborts; e.g. freezing before verifying.) The protocol is **interactive-only**: under a non-interactive driver (/loop, cron, Workflow) no default can substitute the step-1 confirmation or the step-3 visual confirm — do not enter the protocol at all; skip raster image acquisition entirely and emit SVG-only output (the SVG-required Constraint already guarantees diagrams). See `references/loop-pauses.md`.

1. **Ask** — 🔴 CHECKPOINT — image-purpose confirmation (may not advance to step 2 without confirmation): confirm with the user the image's purpose, composition, required elements, and forbidden elements (avoid AI slop: six fingers, distorted text, watermark, page chrome). May not enter step 2 before confirmation is obtained.
2. **Generate OR Search** — pick one:
   - **Generate**: run **Codex CLI image-gen**, with the brief produced by `/baransu:design export-brief` then fed in via stdin. Example:
     ```bash
     codex prompt --stdin < .claude/design/brief-{preset}-{date}.md \
       --suffix "請生成符合上述 design brief 的封面圖，no title, no footer, no page chrome, no logo, no border"
     ```
   - **Search**: call `search the web` to find ready-made resources; **accept only CC licenses** (CC0 / CC-BY / CC-BY-SA), everything else falls back to the Generate branch.
3. **Verify** — the renderer embeds the image into the long-form HTML preview, and the user visually confirms composition, layout alignment, no AI slop, no watermark; if it fails, fall back to step 2 and rerun.
4. **Freeze** — commit the image file to `.claude/book/{slug}/assets/`, and write a `meta.json` containing `source` (generate / search), `prompt` (required on the Generate path), `license` (required on the Search path), and a `verified_at` timestamp. After freezing the image is treated as immutable; to change it → start over from step 1.

### 6. Multi-format pipeline (PDF / PPTX)

Takes effect only when `$FORMAT` ∈ {`pdf`, `ppt`, `all`}.

- **PDF**: inject `@page` + hidden `.toc-wrap` + serif `body { font-family: var(--font-serif) }` into the HTML, save the patched HTML, call `python3 -m weasyprint`. On failure → warning, do not abort.
- **PPTX**: per `$STRUCTURE_SLIDES`, take the skeleton from `{project_root}/slide-cores/<layout-id>.html`; write one HTML per slide to `.claude/book/slides-{$SLUG}/slide-{NN}.html` (zero-padded deck order — the fixed on-disk contract Stage 4's PPT-mode validation reads back) with a `960pt × 540pt` `<body>` (the unit is **pt** — 960px fails html2pptx's LAYOUT_WIDE dimension validation) + per slide `<section class="{prefix}-slide" data-layout=...>`; before calling, verify three items (`width:960pt` / a prefixed `section[data-layout]` slide present / no `background-image`); once passed, call `node html2pptx.js` **once with all per-slide files** (multiple inputs append slides to one .pptx).

**Detailed steps (HTML preprocessing / verification items / failure handling) → read `references/render-pipelines.md`.**
### 7. Write the output file

Write the complete HTML to `.claude/book/{$SLUG}.html`.

Do not write partial content — write the full file in one operation.

---

## Stage 4 — Validate & Report

### 1. Run quality gate

```bash
npx tsx "./scripts/validate-output.ts" ".claude/book/{$SLUG}.html"
```

Exit codes:
- `0` (GATE PASS): proceed to completion report
- `1` (GATE FAIL): three-stage fallback:
  - **Trigger condition**: validate-output.ts returns exit 1.
  - **First-line fix**: read the failure lines printed to stdout, fix only the failing element and rewrite the file, then rerun the quality gate once.
  - **Still-failing fallback**: 🛑 STOP — quality gate failed a second time, human intervention: if exit 1 still on the second run, output 「品質閘第二次失敗，請手動開啟 .claude/book/{$SLUG}.html 確認問題。」 and stop (do not enter the completion report).
- `2` (usage error): script invocation was wrong — fix and re-run

**PPT-mode addition (`$FORMAT` contains `ppt`)**: after the long-form gate above, additionally run the validator over **each per-slide HTML** written by Stage 3 §6 (`.claude/book/slides-{$SLUG}/slide-*.html`):

```bash
for f in .claude/book/slides-{$SLUG}/slide-*.html; do
  npx tsx "./scripts/validate-output.ts" "$f"
done
```

Every slide must exit 0. The slide files are where GATE-F (class prefix) and GATE-G (layout registration) actually fire — the long-form HTML SKIPs both (mode=non-ppt), so omitting this loop means PPT gating never ran and the Outcome Contract's 「GATE F/G all green or legitimate SKIP」 is satisfied only vacuously. A failing slide follows the same three-stage fallback as above (first-line fix → rerun once → 🛑 STOP).

### 2. Visual render verification + completion report

After GATE PASS, run a Playwright headless render (producing a preview screenshot + JSON probe) and output the final completion report.

**Detailed spec → read `references/validation.md`** (including how to call `verify-render.py`, the probe JSON schema, interpretation rules, and the full report template).

The final user-visible output's fixed format (core lines):

```
✅ 已儲存：
  HTML / PDF（若 format 含 pdf）/ PPT（若 format 含 ppt）/ 預覽 PNG
內容類型：{$CONTENT_TYPE}
SVG 圖解：{N} 張
字數：約 {word_count} 詞
```

---

## Gotchas

- **SPA / login walls**: X.com, LinkedIn, paywalled pages often fail the proxy cascade. Report the failure clearly; don't silently produce an empty or skeleton page.
- **markitdown escaped underscores in URLs**: when markitdown converts HTML, it sometimes escapes `_` to `\_` inside image URLs. Run a cleanup pass on all `![...](\url)` patterns before processing.
- **SVG path closure**: always close `<path>` elements with `/>`; validate-output.ts checks SVG tag balance but not path syntax. Keep SVG shapes simple (lines, rects, circles, ellipses, simple paths).
- **Missing project-root tokens**: if `{project_root}/tokens.css` is absent, Stage 3 aborts with 「請先跑 `/baransu:design preset <style>`（kami / google-design / swiss）或 `/baransu:design gen --slug <slug>`」 — **do not** fall back to `find` or sibling-skill paths. Fallback to `references/golden-template.html` is allowed only when long-form.html is absent (see §3.1).

## Validator division of labor

Verification splits into two tiers with opposite authority — **the hard floor blocks; the soft range advises**. Soft generation (Stage 3 §3) lives *inside* the hard floor and is *judged against* the soft range; a soft-range objection never blocks, a hard-floor violation always does.

- **Hard floor — blocking boundary**: **token-only / no-rgba (in SVG) / accent ≤5% / PDF-safe**. `scripts/validate-output.ts` mechanically enforces the gated subset — token-only via GATE-F class-prefix (PPT mode only; SKIPs on long-form html), PDF-safe via GATE-K + the html2pptx pre-checks (likewise PPT-mode); any gate violation = GATE FAIL (blocking). **No gate scans no-rgba, accent ≤5%, or bare-hex color literals today** — those hard-floor items are caught only by the Stage 3 §3 pre-write checklist, so self-check them before writing (coverage table: `references/validation.md`).
- **Soft range — non-blocking opinion**: `style-reviewer` plus mechanical heuristics (**bare hex**, a **second accent**, **column width** past the §9 欄寬上限 ceiling) — advisory, recorded in the review, never blocks output.
- Full detail (hard-floor→gate coverage mapping, follow-up note, gate-internal trust boundary, REQ-003 Scenario 2 automated evidence) → read `references/validation.md`.
