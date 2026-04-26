---
name: read
description: >
  Trigger /read when the user wants to capture, archive, or convert any content to offline-readable Markdown.
  Inputs: URL (web page, PDF, GitHub file), local file path, glob pattern (e.g. ./docs/*.pdf),
  --chrome (active Chrome tab), --clipboard (clipboard text), --topic "keyword" (academic paper search).
  Saves raw original to .claude/read/raw/{slug}/ and converted Markdown to .claude/read/material/{slug}/index.md.
  Supports markitdown auto-install, WSL2/Linux/macOS/Windows, Chrome soft dependency (degraded mode if unavailable).
argument-hint: "[URL | path | glob | --topic 'keyword' | --web 'keyword' | --gh 'keyword' | --x 'keyword' | --chrome | --clipboard]"
user-invocable: true
---

This skill captures any content source and converts it to clean, offline-readable Markdown via a three-stage pipeline: Acquire → Convert → Organize.

**User-facing language**: 繁體中文. All output shown to the user (stage notices, completion reports, error messages) must be in Traditional Chinese.

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

Refer to `references/setup/{platform}.md` for platform-specific troubleshooting.

### 4. Chrome check (soft dependency)

Try calling `mcp__claude-in-chrome__tabs_context_mcp`.

- If succeeds: set `$CHROME_AVAILABLE=true`
- If fails or tool unavailable: set `$CHROME_AVAILABLE=false`; output 「Chrome 未連線，--chrome 模式暫時停用，其他輸入類型仍可使用。」

This is NOT an early exit. Proceed to Stage 1 regardless.

## Stage 1 — Input Detection & Acquire Routing

Parse the argument(s) passed to `/read`. Route as follows (check in order):

### 1. `--topic "keyword"`

Read `references/acquisition/academic-search.md`.

Display paper list and wait for user selection. After selection, continue with the selected paper's PDF URL or DOI URL as described in that reference.

### 2. `--web "keyword"`

Read `references/acquisition/web-search.md`.

Use the WebSearch tool to fetch candidate URLs, present them via AskUserQuestion (per `§AskUserQuestion 互動規格`), then route the selected URL through `/read`'s existing URL routing (§9).

### 3. `--gh "keyword"`

Read `references/acquisition/gh-search.md`.

Run `gh search repos` to fetch candidate repos, present them via AskUserQuestion, then route the selected GitHub URL through web-static.md GitHub section.

### 4. `--x "keyword"`

If `$CHROME_AVAILABLE=false`: output 「Chrome 未連線，--x 模式無法使用」 and stop.

Otherwise: Read `references/acquisition/x-search.md`. The lane delegates to `web-dynamic.md` WSL2 path for Chrome MCP navigation, runs schema-level health check, extracts tweet URLs via regex, presents them via AskUserQuestion, then routes the selected tweet URL through existing URL routing.

### 5. `--chrome`

If `$CHROME_AVAILABLE=false`: output 「chrome-tab 模式暫時不可用，請改用 URL 模式」 and stop.

Otherwise: Read `references/acquisition/chrome-tab.md` and follow the MCP call sequence described there.

### 6. `--clipboard`

Read `references/acquisition/clipboard.md` and follow the platform clipboard commands described there.

### 7. Glob pattern

Detected when input contains `*`, `?`, or `[`.

Read `references/acquisition/local-file.md` (glob section). Each matched file runs stages 1–3 independently. If zero matches, output 「無匹配項目：{pattern}」 and stop.

### 8. Local path

Run `test -e "{input}"` to verify the path exists.

If exists: Read `references/acquisition/local-file.md` (single-path section).

### 9. URL

Starts with `http://` or `https://`. Apply URL pattern routing:

- `github.com` or `raw.githubusercontent.com` in hostname → Read `references/acquisition/web-static.md` (GitHub section)
- URL ends with `.pdf` OR HEAD request `curl -sI "{url}" | grep -i "content-type: application/pdf"` matches → Read `references/acquisition/web-static.md` (PDF URL section)
- Other URLs → attempt proxy cascade (Read `references/acquisition/web-static.md`); after proxy cascade completes, check if result is < 500 bytes or contains SPA feature strings (`<app-root`, `<div id="root"`, `__NEXT_DATA__`, `window.__NUXT__`); if SPA detected → Read `references/acquisition/web-dynamic.md`

### 10. Unrecognized input

Output 「無法識別輸入：{input}。請使用 URL、本地路徑、glob、--chrome、--clipboard、--topic、--web、--gh 或 --x。」

---

### After Acquire

All acquired content must be saved to `.claude/read/raw/{slug}/index.{ext}` before proceeding to Stage 2. Images found during acquisition are downloaded to `.claude/read/raw/{slug}/assets/`.

Generate an initial slug from the URL path's last segment or filename stem using slug rules: lowercase, ASCII, hyphens, max 60 chars.

## Stage 2 — Convert

### 1. Confirm CLI syntax

Read `references/conversion/markitdown-guide.md` to confirm CLI syntax.

### 2. Run markitdown

```bash
markitdown ".claude/read/raw/{slug}/index.{ext}" -o "/tmp/{slug}-convert.md" 2>/dev/null
```

Always use quoted paths. Suppress onnxruntime warnings with `2>/dev/null`.

### 3. Check output

If `/tmp/{slug}-convert.md` is empty (0 bytes) or missing: record 「{slug}: markitdown 轉換失敗，raw/ 已保留」; skip to report; do NOT create a `material/` entry for this item.

### 4. Image handling

Extract image URLs from the converted markdown:

```bash
grep -oE '!\[.*?\]\((https?://[^)]+)\)' /tmp/{slug}-convert.md | grep -oE 'https?://[^)]+' | sort -u
```

Also check raw/ HTML for `<img src=` tags to catch images markitdown may have dropped.

For each image URL:

- If relative path: resolve against the source URL to form absolute URL
- Download:
  ```bash
  curl -sL "{img_url}" -H "Referer: {source_url}" -o ".claude/read/raw/{slug}/assets/{filename}" 2>/dev/null
  ```
- On failure: record `[image download failed: {img_url}]` as a note; do NOT stop

Copy successfully downloaded images to `.claude/read/material/{slug}/assets/` (create directory first).

In the converted markdown, replace each original image URL reference with `./assets/{filename}`.

## Stage 3 — Organize

### 1. Read storage protocol

Read `references/storage-protocol.md` for slug rules and frontmatter format.

### 2. Extract title

Find the first `# ` heading in `/tmp/{slug}-convert.md`. If none, use the URL path's last segment or filename stem.

### 3. Generate final slug

Apply slug rules to the title: lowercase, ASCII, hyphens, max 60 chars.

### 4. Dedup check

Read `.claude/read/index.md` (if it exists):

- Search for `source_url` column matching the original URL
- If found: find the highest existing `_vN` suffix for that source_url → use `_v{N+1}` as new slug suffix
- If a different URL produces the same title-slug: also append `_v2`

### 5. Create directories

```bash
mkdir -p ".claude/read/material/{final-slug}/assets"
```

### 6. Write `material/{final-slug}/index.md`

Write with frontmatter followed by the full converted markdown content (with image paths already replaced in Stage 2):

```yaml
---
source_url: "{original URL or 'local:{path}' for local files}"
title: "{extracted title}"
captured_at: "{ISO 8601 timestamp}"
conversion_tool: "markitdown {version}"
slug: "{final-slug}"
platform: "{$PLATFORM value}"
acquire_via: "{search:web|search:gh|search:x|topic|chrome|clipboard|url|local}"
---
```

### 7. Update `.claude/read/index.md`

If the file does not exist, create it with header:

```markdown
# Read Index

| source_url | slug | title | captured_at |
|-----------|------|-------|------------|
```

Append row: `| {source_url} | {final-slug} | {title} | {captured_at} |`

### 8. Completion report (繁體中文)

```
✅ 已儲存：.claude/read/material/{final-slug}/index.md
圖片：{N} 張已儲存，{M} 張失敗
{if M > 0: 失敗清單：[url1, url2, ...]}
轉換工具：markitdown {version}
```

For glob batches of 10+ items, compress to: `成功 N 筆，失敗 M 筆` without listing each path.

## AskUserQuestion 互動規格

This section is the single source of truth for keyword-search lanes that present candidates via AskUserQuestion. The four lanes — `--web`, `--gh`, `--x`, and the upgraded `--topic` — share this spec; their reference files (`web-search.md`, `gh-search.md`, `x-search.md`, `academic-search.md`) reference this section instead of redefining its rules.

### Capacity

- AskUserQuestion's hard ceiling is **4 options per round**.
- Every round reserves **1 slot for an escape option** (label: `「以上都不選」`). The remaining 3 slots are usable for results.
- Maximum result slots across the worst case = 3 rounds × 3 result slots = **9**.

### Result-count to round mapping

| Result count `N` | Rounds | Per-round result slots |
|------------------|--------|------------------------|
| `N ≤ 3` | 1 | `N` (each result slot fills, plus escape) |
| `4 ≤ N ≤ 6` | 2 | 3, then `N - 3` |
| `7 ≤ N ≤ 9` | 3 | 3, 3, then `N - 6` |
| `N ≥ 10` | 3 | 3, 3, 3 (truncated to first 9 by lane's native sort order; no local re-ranking) |

Each round always carries the escape option in addition to its result slots.

### Multi-round semantics

- The user picks a single result. Selection in any round **terminates the sequence** (single-pick semantics) — the orchestrator does not advance to subsequent rounds for that lane invocation.
- The `acquire` phase processes only the single picked candidate.

### Escape behaviour

- Selecting `「以上都不選」` in any round terminates the lane immediately.
- No `material/{slug}/` is produced; no `raw/{slug}/` is retained for the search-page intermediate.
- The orchestrator outputs `「使用者放棄選擇」` and stops.

### Cross-lane invariant

- Lanes do **not** apply 1-5 scoring or re-rank candidates locally.
- Lane-side schema-level health checks (e.g. `--x` substring guards) are acquire-stage failures — not candidate scoring — and apply before this section's flow runs.

## Constraints

- **No LLM post-processing**: The converted markdown content is markitdown's raw output. Never summarize, rewrite, translate, or annotate the content.
- **raw/ is immutable**: Once `raw/{slug}/` is written, never modify it. It is the original archive.
- **chrome-tab in degraded mode**: When `$CHROME_AVAILABLE=false`, always report unavailability — never attempt to call chrome MCP tools.
- **Partial failure does not stop the pipeline**: Image failures, individual glob items failing, or convert failures are recorded and reported; the successful items complete normally.
- **Completion report is compact**: Show path + counts + failure list only. Never print the full converted markdown content to the user.

## Gotchas

- **onnxruntime GPU warning**: Non-fatal. Appears on WSL2 with NVIDIA drivers. Use `2>/dev/null` when calling markitdown CLI to suppress.
- **markitdown accepts file path, not live URL**: After Acquire saves content to `raw/`, always pass the local `raw/{slug}/index.{ext}` path to markitdown — not the original URL. Exception: for PDF URLs, markitdown can accept the URL directly if you prefer; still save to raw/ first.
- **SPA false positive** (`<div id="root">` in static HTML): upgrading to browser layer will produce richer content. This is acceptable behavior.
- **Windows environment**: Call `install-deps.bat` not `install-deps.sh`. Platform detection in Stage 0 determines which to call.
- **Slug collision naming**: Use `_v2`, `_v3` etc. — never `_1`, `_2`. The dedup logic in Stage 3 and index.md use the `_vN` convention consistently.
- **Clipboard text that is already Markdown**: markitdown will accept it and output may look identical to input. This is normal behavior, not a failure.
- **Glob expands to zero matches**: Report 「無匹配項目：{pattern}」 immediately. Do not attempt Acquire.
