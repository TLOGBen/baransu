---
name: learn
description: 'Use When the user wants a structured learning brief from any content.
  Do Produce a 5-column digest brief per source plus an optional filled outline, from
  URLs / --topic / captured slugs / mixed. Trigger On ''/learn'', ''研究主題'', ''整理筆記'',
  ''學一下''. Not for capturing raw offline Markdown only (→ /read) nor producing a browser-ready
  HTML artifact (→ /book).

  '
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

This skill takes any content source and produces structured learning output via a five-stage pipeline: Collect → Digest → Outline → Fill In → Refine.

**User-facing language**: 繁體中文. All output shown to the user (stage notices, progress, completion reports, error messages) must be in Traditional Chinese.

## Outcome Contract

- **Outcome**: Collected sources are scored, filtered, and turned into a structured learning output for the topic.
- **Done when**: `--brief` path — `.claude/learn/briefs/{$BRIEF_SLUG}.md` exists with the five-column body per `references/brief-format.md`; full path — `.claude/learn/digests/{$DIGEST_SLUG}.md` exists with the `references/digest-frontmatter.md` schema and the refined body.
- **Evidence**: The 繁中 completion notice naming the written file path; the file's frontmatter lists every surviving `$FILTERED_SOURCES` entry (and, for digests, `phases_completed`).
- **Output**: A brief under `.claude/learn/briefs/` or a digest under `.claude/learn/digests/`.
- **Automation**: ultracode=overlap, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

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

- On Windows: run `"./../read/scripts/install-deps.bat"`
- On Linux/macOS/WSL2: run `bash "./../read/scripts/install-deps.sh"`

If installation succeeds: continue.

If installation fails: output 「markitdown 安裝失敗。請手動執行：pip install markitdown」 and stop.

### Orchestration interface (dual-mode)

At Stage 0, read `references/orchestration-interface.md` and pin the dispatch mode
(ultracode detect → record → no mid-run switch); re-apply its adapter contract whenever §3.5
fan-out is triggered. The contract covers: the candidate-pool `{path, lane}` shape, Stage 0
mode pinning, the current four-lane fan-out adapter, and a thin Workflow adapter. Both adapters return the identical
pool shape — Stage 2 scoring never senses the mode; the depth invariant is restated per adapter.
Non-ultracode runs keep current-path semantics unchanged.

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

If the file exists: append `.claude/read/material/{slug}/index.md` to `$SOURCES`.

If the file does not exist: do NOT stop. **Fall through to §3.5 — Bare Topic fan-out fallback** (the input is treated as a bare topic, not a slug typo).

### 3.5. Bare Topic — fan-out fallback

Triggered when §3 matches the syntactic shape of a slug but `.claude/read/material/{slug}/index.md` does not exist. The input is interpreted as a research topic; `/learn` runs an automatic fan-out across four search lanes.

**Lanes** (parallel where possible):

| Lane | Underlying tool | Adapter thinness | Cite path (if thick) |
|------|-----------------|------------------|----------------------|
| `academic` | `../read/scripts/search-papers.py` | Thin (invoke + normalize) | — |
| `web` | search the web tool | Thin (invoke + normalize) | — |
| `gh` | `gh search repos` | **Thick** — before running the gh lane, read `../read/references/acquisition/gh-search.md` §Search Command and apply the Step 1 escape rule to `{topic}`. Must reuse its escape rule (lines specifying single-quote form + `'\''` escape) by **anchor cite**, never fork the literal text. The bare `{topic}` from §3.5 invocation IS the user-supplied keyword for §Search Command Step 1; apply Step 1 escape verbatim before substitution. | `../read/references/acquisition/gh-search.md §Search Command`, §Failure Modes |
| `x` | Chrome MCP via `../read/references/acquisition/web-dynamic.md` WSL2 path | **Thick** — before running the x lane, read both `../read/references/acquisition/x-search.md` and `../read/references/acquisition/web-dynamic.md`, and apply §Schema-level Health Check and §Candidate Extraction verbatim. Must reuse the 5-rule schema-level health check from x-search.md §Schema-level Health Check and the candidate regex from §Candidate Extraction by **anchor cite**, never fork. | `../read/references/acquisition/x-search.md §Search Phase`, §Schema-level Health Check, §Candidate Extraction |

**Lane fail-mode mapping (Theme A)**: All four lanes invoke their underlying tools directly (not via `/read --{lane}`); each ref's Failure Modes / Health Check / No Results sections are reused as **lane-status mapping rules**, not as `/learn`-level stops. Specifically: any condition that the ref says "stop" maps to `{lane}: failed (...)` or `{lane}: 0 hits (no results)` per the three-state surface below; `/learn` never propagates the lane's stop verb.

**Parallelism model**:
- The three single-call lanes (`academic`, `web`, `gh`) launch in fan-out turn 1 as a batch tool-call set together with the X lane's `tabs_create_mcp` first step.
- X lane proceeds in turn 2 (`navigate` to `https://x.com/search?q={url-encoded-topic}`) and turn 3 (`get_page_text` + schema check + candidate regex extract).
- Other 3 lanes return candidates in turn 1; X lane returns in turn 3. Accept the +3 turn startup delay for X — do not spawn sub-agents to flatten it.

**Per-lane timeout** (defaults; implementation may adjust based on observed latency):
- `academic`: 60s (search-papers.py latency)
- `web`: 30s
- `gh`: 30s
- `x`: 45s (Chrome MCP 4-step sequence)

**Soft-failure invariant**:
- Any single lane failure (timeout / API error / 0 results / schema-check fail / Chrome unavailable) does NOT stop the other lanes.
- At least 1 lane returning ≥1 candidate is sufficient to continue to Stage 2.
- All four lanes failing → first emit the per-lane status surface (the three-state lines below) so the user sees which lanes were `0 hits (no results)` vs `failed (timeout|api_error|...)`, then output 「所有 lane 均無結果，請嘗試其他關鍵字或手動跑 /read」 and stop. The aggregate message MUST NOT replace the per-lane breakdown — both appear, in that order.
- This invariant differs from `/read --web|--gh|--x` (which stops on any failure) by design: `/read` is interactive single-source, `/learn` is automated multi-source.

**Lane status surface** (one line per lane, three states):
- `{lane}: N hits` (success with N candidates)
- `{lane}: 0 hits (no results)` (lane ran successfully but returned empty)
- `{lane}: failed (timeout|api_error|chrome_unavailable|schema_check_fail|cli_missing)` (transient or environmental failure)

The three-state form ensures the user can distinguish a real zero-result from a transient failure that may warrant a manual retry.

**Candidate pool merging**:
- Each lane's candidates are written into `$SOURCES` as `{path, lane}` tuples (the `lane` field carries `academic|web|gh|x`; for inputs from §1/§2/§3, the `lane` field is `null`).
- Deduplicate across lanes by `url` exact-string equality (no fuzzy normalization; trailing slash / query string differences are kept distinct, Stage 2 will surface them and the user can drop duplicates during the trim step).

**Disambiguation note** (slug vs topic):
- `/learn react` (single word, slug shape, slug-file exists) → §3 reads existing material.
- `/learn react` (slug-file does NOT exist) → §3.5 fan-out on topic "react".
- `/learn react hooks` (multi-arg, slug shape per arg) → handled by §4 mixed input rule: each argument is processed individually. `react` → §3 → fan-out (if missing); `hooks` → §3 → fan-out (if missing). To search a multi-word topic explicitly as one query, use `/learn --topic "react hooks"`. The §4 reading is authoritative; multi-word bare input is NOT auto-joined into a single fan-out topic.
- `/learn ./typo.md` (path prefix `./`) → fails §3 explicitly; behaviour outside the slug branch — currently no §1/§2 routing for local paths in `/learn`. Treat as user error: output 「未識別輸入：{input}」 and stop. Do NOT fall through to §3.5 for inputs with explicit path prefixes.
- `/learn` (no argument) or `/learn ""` (empty string argument) → output 「請提供 URL、--topic 「關鍵字」或 slug」 and stop. Do NOT enter §3.5 fan-out with an empty topic (would trigger four no-op searches).
- `/learn --brief slug-not-found` → §3 falls through to §3.5 fan-out using slug as topic; the `--brief` flag is honored at Stage 2's stop path regardless of how Stage 1 resolved sources (i.e. brief output is generated from fan-out's filtered candidates).
- `/learn --brief` (flag only, no topic) → output 「請提供 URL、--topic 「關鍵字」或 slug」 and stop. Same as no-argument case.

### 4. Mixed input (multiple arguments of different types)

Process each argument sequentially using the rules above (URL → --topic → slug → §3.5 fan-out). Each resolved argument appends its material paths (with `lane` tuples) to `$SOURCES`.

If any individual argument fails after fallback (e.g. fan-out also returns nothing), stop immediately with the relevant error message.

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

For each entry in `$SOURCES`, read its `index.md` and evaluate it on three criteria. Each criterion is scored independently on a 1–5 scale by reading the source's `index.md`; assign the level whose anchor signal is the highest one observable in the text. The anchor scales below pin each level to an observable signal in `index.md`, converting the judgment into a decision rule applied without further discretion (when a source falls between two anchors, assign the lower of the two).

| Criterion | Meaning |
|------|------|
| 多情境適用性 | Can this source's viewpoint / findings be applied across multiple scenarios or domains? |
| 預測力 | Does this source offer verifiable predictions or actionable causal inferences? |
| 通用性 | Are this source's conclusions stable across time and across populations? |

**Anchor scale — 多情境適用性** (1–5; level = highest observable signal in `index.md`):
- 1 = applies to a single named case only.
- 3 = generalizes to one adjacent domain.
- 5 = states a domain-independent mechanism with ≥2 distinct example domains in the text.
- (2 and 4 = between the adjacent anchors above.)

**Anchor scale — 預測力** (1–5; level = highest observable signal in `index.md`):
- 1 = no claims.
- 3 = qualitative directional claim.
- 5 = quantified/falsifiable prediction with stated conditions.
- (2 and 4 = between the adjacent anchors above.)

**Anchor scale — 通用性** (1–5; level = highest observable signal in `index.md`):
- 1 = single-population snapshot.
- 3 = holds across one stated boundary.
- 5 = replicated across time and population in the source.
- (2 and 4 = between the adjacent anchors above.)

### 3. Present scoring table for user confirmation

Display the scoring results in a 繁中 table for the user to review.

**Layout rule**: count distinct **non-null** `lane` values in `$SOURCES`.
- 0 distinct (all sources have `lane=null`, i.e. URL/slug-only inputs from §1/§2/§3): combined form, no lane attribution needed.
- ≥1 distinct (any source has non-null `lane`, even if only one lane survived a fan-out): **lane-grouped form**. Each non-null lane gets its own sub-table; sources with `lane=null` group under a `## direct` heading. This preserves fan-out provenance even when the user-facing pool is small.

**Lane-grouped form** (when fan-out was triggered):

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

Each per-lane sub-table caps at the lane's hit count (no further truncation). Scoring uses the per-criterion anchor scales in §2; for high-volume pools (>20 candidates) the per-cell judgment is necessarily coarser — this is the accepted trade-off for keeping the spec uniform across lanes.

**Combined form** (single-lane or non-fan-out inputs):

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
