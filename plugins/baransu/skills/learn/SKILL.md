---
name: learn
description: >
  Trigger /learn when the user wants to study, digest, or create a structured learning brief from any content.
  Inputs: URL (web page, PDF, GitHub file), --topic "keyword" (academic paper search), slug (previously captured
  material in .claude/read/material/{slug}/), or mixed (multiple URLs and/or slugs).
  Produces a concise 5-column digest brief per source and optionally a full structured outline with filled notes.
argument-hint: "[URL... | --topic 'keyword' | slug... | mixed]"
user-invocable: true
---

This skill takes any content source and produces structured learning output via a five-stage pipeline: Collect → Digest → Outline → Fill In → Refine.

**User-facing language**: 繁體中文. All output shown to the user (stage notices, progress, completion reports, error messages) must be in Traditional Chinese.

## Stage 0 — Environment Self-Check

### 1. Python check

Run:

```bash
python3 --version 2>/dev/null
```

If the command fails (exit code non-zero or no output): output 「Python 3.8+ 未安裝，無法繼續。請先安裝 Python: https://python.org」 and stop.

### 2. Platform detection

Run the following checks in order to detect the current platform. Record the result as `$PLATFORM` for use in later stages.

- **WSL2**: `grep -qi microsoft /proc/version 2>/dev/null && echo wsl2` → if prints `wsl2`, set `$PLATFORM=WSL2`
- **macOS**: `uname -s 2>/dev/null | grep -qi darwin && echo macos` → if prints `macos`, set `$PLATFORM=macOS`
- **Windows (PowerShell)**: `[System.Environment]::OSVersion.Platform` returns `Win32NT` → set `$PLATFORM=Windows`
- **Otherwise**: set `$PLATFORM=Linux`

### 3. markitdown check

Run:

```bash
python3 -m markitdown --version 2>/dev/null
```

If this fails (markitdown not installed):

- On Windows: run `"$CLAUDE_SKILL_DIR/scripts/install-deps.bat"`
- On Linux/macOS/WSL2: run `bash "$CLAUDE_SKILL_DIR/scripts/install-deps.sh"`

If installation succeeds: continue.

If installation fails: output 「markitdown 安裝失敗。請手動執行：pip install markitdown」 and stop.

## Stage 1 — Collect

Parse the argument(s) passed to `/learn`. Build a source list `$SOURCES` (ordered list of `.claude/read/material/{slug}/index.md` paths) to pass to Stage 2.

Route each argument as follows (check in order per argument):

### 1. URL input (`http://` or `https://` prefix)

Call `/read <url>` for each URL sequentially. After `/read` completes, the material is available at `.claude/read/material/{slug}/index.md` where `{slug}` is the slug assigned by `/read`. Append that path to `$SOURCES`.

Process multiple URLs one at a time, not in parallel.

### 2. `--topic "keyword"`

Call `/read --topic "keyword"`. The paper-list display and user-selection prompt from `/read` **must surface to the user as-is** — do not hide, automate, or skip the selection step. After the user selects a paper and `/read` completes acquisition, append the resulting `.claude/read/material/{slug}/index.md` path to `$SOURCES`.

Note: the paper selection UI is shown to the user, not performed silently inside /learn.

### 3. Slug input (no `http://`, `https://`, `./`, `/`, `*`, `?` prefix and no `--` prefix)

Do NOT call `/read`. Read `.claude/read/material/{slug}/index.md` directly.

If the file does not exist: output 「slug 不存在，請先執行 /read 擷取」 and stop.

If the file exists: append `.claude/read/material/{slug}/index.md` to `$SOURCES`.

### 4. Mixed input (multiple arguments of different types)

Process each argument sequentially using the rules above (URL → --topic → slug). Each resolved argument appends its material path to `$SOURCES`.

If any individual argument fails (slug not found, /read error), stop immediately with the relevant error message.

### Source list handoff

After all arguments have been processed and `$SOURCES` is complete, output a brief 繁中 progress notice listing the number of sources collected (e.g. 「已收集 N 筆資料，開始消化…」). The `$SOURCES` list is passed as input to Stage 2 — Digest.

## Stage 2 — Digest

Receives `$SOURCES` from Stage 1. Scores each source on three criteria, presents results to the user for confirmation, then either produces the `--brief` output (stop path) or hands off to Stage 3.

### 1. Resolve research topic (`$TOPIC`)

The topic string is needed for the brief filename (slug) and YAML frontmatter.

- If the original invocation included `--topic "keyword"`: set `$TOPIC` to that keyword.
- Otherwise (URL-only or slug-only input): ask the user once:
  「請輸入這批資料的研究主題（用於生成 brief 檔名）：」
  Set `$TOPIC` to the user's reply.

### 2. Score each source

For each entry in `$SOURCES`, read its `index.md` and evaluate it on three criteria using **visual judgment (1–5)**. There is no quantitative formula in v1; scores are assigned by holistic reading.

| 標準 | 說明 |
|------|------|
| 多情境適用性 | 此來源的觀點／發現是否能跨越多種場景或領域應用？ |
| 預測力 | 此來源是否提供可驗證的預測或可操作的因果推斷？ |
| 通用性 | 此來源的結論是否具備跨時間、跨族群的穩定性？ |

Scale: 1 = very low, 5 = very high. Each criterion is scored independently.

### 3. Present scoring table for user confirmation

Display the scoring results in a 繁中 table for the user to review:

```
## 消化評分結果

請確認以下評分，並回覆要保留哪些來源。若所有來源均可接受，請回覆「全部保留」。

| 來源 slug | 多情境適用性 | 預測力 | 通用性 |
|-----------|-------------|--------|--------|
| {slug-1}  | {1-5}       | {1-5}  | {1-5}  |
| {slug-2}  | {1-5}       | {1-5}  | {1-5}  |
```

Wait for the user's reply. Build `$FILTERED_SOURCES` from the sources the user confirms to keep.

If `$FILTERED_SOURCES` is empty (user dropped all sources, or all sources were excluded):
Output 「所有來源評分過低，建議補充高品質來源」 and stop.

### 4. `--brief` path (stop path)

If the original invocation included the `--brief` flag:

**a. Read the format contract.**

Read `references/brief-format.md` before writing any output. That file is the authoritative format contract — five-column structure, YAML frontmatter fields, column order, and constraints. Do not deviate from it.

**b. Generate slug for output filename.**

Derive `$BRIEF_SLUG` from `$TOPIC`:
- Lowercase all characters
- Convert to ASCII (transliterate or drop non-ASCII)
- Replace spaces and special characters with hyphens
- Strip leading/trailing hyphens
- Truncate to 60 characters

Example: `$TOPIC = "小樣本場景的泛化策略"` → `$BRIEF_SLUG = "xiao-yang-ben-chang-jing-de-fan-hua-ce-lue"` (or an ASCII approximation).

**c. Produce the five-column brief body.**

Using only `$FILTERED_SOURCES`, populate each of the five columns as specified in `references/brief-format.md`:
- (a) 核心主張列表
- (b) 來源矛盾點
- (c) 缺少資訊/盲點
- (d) 各來源信度評分 — visual credibility score (1–5) per source; quantitative formula deferred (TBD)
- (e) 建議 /think 入場角度

**d. Write the output file.**

Write to `.claude/learn/briefs/{$BRIEF_SLUG}.md`. If a file with the same slug already exists, overwrite it without prompting.

File structure (YAML frontmatter followed by the five-column body):

```yaml
---
topic: "{$TOPIC}"
sources:
  - slug: "{slug}"
    url: "{原始 URL}"
created_at: "{ISO 8601 timestamp}"
type: "brief"
---
```

Followed by the five-column Markdown body per `references/brief-format.md`.

**e. Print completion message and stop.**

Output (繁中):
「brief 已儲存至 .claude/learn/briefs/{$BRIEF_SLUG}.md」

Stage 2 returns here. Do NOT continue to Stage 3, Stage 4, or Stage 5.

### 5. Handoff to Stage 3 (non-`--brief` path only)

If `--brief` was NOT set, pass `$FILTERED_SOURCES` and `$TOPIC` to Stage 3 — Outline.

## Stage 3 — Outline

Receives `$FILTERED_SOURCES` and `$TOPIC` from Stage 2. Builds a structured outline grounded entirely in the filtered sources.

### 1. Extract outline from filtered sources

Read each file in `$FILTERED_SOURCES`. Identify the main claims, findings, arguments, and structural units that together cover the topic.

Organize these into a hierarchical outline (sections and sub-points). Each bullet or point in the outline **must** be followed by a `[source: {slug}]` citation tag referencing the source it was drawn from.

If a bullet or point cannot be grounded in any entry in `$FILTERED_SOURCES` — no source directly supports it — mark it with `⚠️ 需補充調查` immediately after the point text (before any citation tag). Do not silently include unsupported claims.

**Outline format**:

```
## {Section Title}

- {Point} [source: {slug}]
- {Point} [source: {slug}]
  - {Sub-point} [source: {slug}]
- {Unsupported claim} ⚠️ 需補充調查
```

### 2. Present outline to user

Output the outline in 繁體中文. Precede it with the notice:
「大綱已生成，請確認結構後繼續填充。」

Store the outline as `$OUTLINE` for use in Stage 4.

If `$OUTLINE` contains any entries marked `⚠️ 需補充調查`, output the following reminder **before** proceeding:

「以下段落缺乏來源支撐（標記 ⚠️ 需補充調查），可補充 /read 資料後繼續。」

Followed by a list of the affected outline sections (section titles and/or bullet points that carry the `⚠️ 需補充調查` marker).

Pass `$OUTLINE`, `$FILTERED_SOURCES`, and `$TOPIC` to Stage 4 — Fill In.

## Stage 4 — Fill In

Receives `$OUTLINE`, `$FILTERED_SOURCES`, and `$TOPIC` from Stage 3. Writes prose for each outline section, checks for gap triggers after each section, and falls back to Stage 2 when gaps are detected.

### 1. Write prose section by section

For each section in `$OUTLINE`, write a paragraph or set of paragraphs that expand the bullet points into coherent prose. Use only information grounded in `$FILTERED_SOURCES`. Unsupported claims (marked `⚠️ 需補充調查` in the outline) may be excluded or noted as areas requiring additional research.

Track the number of times you revise any single section. This count is used by the gap trigger checks below.

### 2. Gap trigger checks (after each section)

After completing each section's prose, check all three gap triggers. If **any** trigger fires, execute the gap-handling procedure (§3 below) before writing the next section.

**Trigger 1 — Repeated edits**: the same section has been reworked ≥ 2 times (same content revised repeatedly without settling).

**Trigger 2 — Single-source dependency**: a critical claim in the section is supported by only one source (only one entry in `$FILTERED_SOURCES` backs it).

**Trigger 3 — Core concept opacity**: after writing the section, you cannot explain the core concept in one sentence.

### 3. Gap handling — Stage 2 fallback

When a gap trigger fires for a section:

1. Output a 繁中 notice identifying the trigger and section:
   「[第N節] 偵測到缺口（{觸發原因}），回退至 Stage 2 補充來源。」

2. Return to Stage 2 — Digest with the following scoped call: present the user with the gap description and ask them to provide additional sources (URLs or slugs) for that section specifically. Re-run Stage 2 scoring on these new sources only. Append accepted sources to `$FILTERED_SOURCES`.

3. Track the number of consecutive retreats for this section in `$RETREAT_COUNT[section]`.

4. **Consecutive retreat cap**: if `$RETREAT_COUNT[section]` reaches 2, stop retreating and ask the user:
   「[第N節] 已連續回退 2 次仍無法補齊缺口。請選擇：\n1. 繼續（提供更多來源）\n2. 跳過此節」
   - If the user selects 1 (continue): accept new sources and resume fill-in for this section; reset `$RETREAT_COUNT[section]` to 0.
   - If the user selects 2 (skip): omit this section from the draft and proceed to the next section.

### 4. Handoff to Stage 5

After all sections have been written (or skipped), collect the full prose into `$DRAFT`. Pass `$DRAFT` and `$TOPIC` to Stage 5 — Refine.

## Stage 5 — Refine

Receives `$DRAFT` and `$TOPIC` from Stage 4. Polishes the draft via `/write`, extracts the refined output, and writes the final digest file.

### 1. Language detection

Inspect `$DRAFT` for the presence of any CJK character. Use the following check:

```bash
echo "$DRAFT" | grep -qP '[\x{4e00}-\x{9fff}\x{3040}-\x{309f}\x{30a0}-\x{30ff}\x{ac00}-\x{d7af}]'
```

- If the grep matches (exit code 0): set `$LANG=zh`
- Otherwise: set `$LANG=en`

The threshold is one character — a single CJK character is sufficient to trigger `$LANG=zh`.

### 2. Call /write in Refine mode

Call `/write {$LANG}` passing `$DRAFT` as the input. The explicit language prefix (`zh` or `en`) is always provided — do NOT omit the prefix or rely on `/write` auto-detection.

`/write` returns output in the Refine format:

```
**Before:**
[original text verbatim]

**After:**
[revised text]

**修正說明：**
- [rule tag]: [change description]
```

### 3. Extract the After segment

From `/write`'s output, extract only the content between `**After:**` and the next `**修正說明：**` heading. Discard the `**Before:**` section and the `**修正說明：**` section entirely. The extracted text is the final digest body; store it as `$REFINED_BODY`.

### 4. Derive digest slug

Derive `$DIGEST_SLUG` from `$TOPIC` using the same derivation as `$BRIEF_SLUG` in Stage 2:
- Lowercase all characters
- Convert to ASCII (transliterate or drop non-ASCII)
- Replace spaces and special characters with hyphens
- Strip leading/trailing hyphens
- Truncate to 60 characters

### 5. Write digest file

Read `references/digest-frontmatter.md` for the authoritative YAML frontmatter schema before writing. Do not deviate from it.

Write to `.claude/learn/digests/{$DIGEST_SLUG}.md`. If a file with the same slug already exists, overwrite it without prompting.

File structure:

```yaml
---
topic: "{$TOPIC}"
sources:
  - slug: "{slug}"
    url: "{原始 URL}"
created_at: "{ISO 8601 timestamp}"
language: "{$LANG}"
phases_completed:
  - collect
  - digest
  - outline
  - fill_in
  - refine
---
```

Followed by `$REFINED_BODY` as the Markdown body.

The `sources` array must list every source in `$FILTERED_SOURCES` (the sources that survived Stage 2 scoring). The `language` field must be exactly `"zh"` or `"en"` — the value of `$LANG`.

### 6. Completion notice

Output (繁中):
「digest 已儲存至 .claude/learn/digests/{$DIGEST_SLUG}.md」
