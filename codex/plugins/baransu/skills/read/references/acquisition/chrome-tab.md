# Chrome Tab Acquisition

## Prerequisite Check

Before any MCP calls, verify `$CHROME_AVAILABLE == true` (set during Stage 0 environment detection).

If `$CHROME_AVAILABLE` is `false` or unset:
- Report: "chrome-tab 模式暫時不可用，請改用 URL 模式"
- Stop. Do not attempt MCP calls.

---

## MCP Call Sequence

### Step 1 — List open tabs

```
mcp__claude-in-chrome__tabs_context_mcp
```

This returns a list of open tabs with their IDs, URLs, and titles.

- Identify the active tab (or the first tab if no active tab is marked).
- Record the tab's `url` and `title`.

If this call fails (Chrome not connected or extension not responding):
- Report: "chrome-tab 模式暫時不可用，請改用 URL 模式"
- Do not retry. Stop.

### Step 2 — Extract page text

```
mcp__claude-in-chrome__get_page_text
  tabId: {tab_id}
```

Save the returned text to:

```
.codex/read/raw/{slug}/index.html
```

where `slug` is derived from the tab's `title` using the standard slug rules.

### Step 3 — Extract image URLs (optional)

```
mcp__claude-in-chrome__javascript_tool
  tabId: {tab_id}
  code: "[...document.querySelectorAll('img')].map(i=>i.src).join('\\n')"
```

Use the returned URL list to download relevant images into `raw/{slug}/assets/` if needed.

---

## After Extraction

The extracted content is already saved under `.codex/read/raw/{slug}/index.html` (Step 2). Hand the saved raw file to SKILL.md Stage 2 (Convert) — the Stage 2/3 pipeline (tmp intermediate, image handling, final slug + dedup, frontmatter, index row) applies unchanged. Never convert straight into `material/`.

Set `source_url` in the frontmatter to the tab's `url` (recorded in Step 1).
