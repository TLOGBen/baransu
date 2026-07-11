## Contents

- SPA Detection Criteria
- Chrome MCP Path (any platform, requires $CHROME_AVAILABLE)
- After Browser Extraction

# Web — Dynamic Content Acquisition (SPA / JS-Rendered)

## SPA Detection Criteria

Trigger the browser layer if the static fetch result matches any of the following:

| Condition | Signal |
|-----------|--------|
| Response body size < 500 bytes | Likely empty shell |
| Contains `<app-root` | Angular SPA |
| Contains `<div id="root"` | React SPA |
| Contains `__NEXT_DATA__` | Next.js (SSR/SPA) |
| Contains `window.__NUXT__` | Nuxt SPA |

Check static fetch result before invoking browser tools. Do not trigger the browser layer for pages that pass static quality checks.

---

## Chrome MCP Path (any platform, requires $CHROME_AVAILABLE)

Use the Claude-in-Chrome MCP tools. This path works on every platform with the Claude-in-Chrome extension connected (`$CHROME_AVAILABLE=true`).

### Step 1 — Create a new tab

```
mcp__claude-in-chrome__tabs_create_mcp
```

### Step 2 — Navigate to the URL

```
mcp__claude-in-chrome__navigate
  url: "{target_url}"
```

### Step 3 — Wait for page load

Wait 2–3 seconds, or until the page's network activity is idle. If the MCP tool supports a `waitUntil: networkidle` option, use it.

### Step 4 — Extract page text

```
mcp__claude-in-chrome__get_page_text
```

Save the returned text to `.claude/read/raw/{slug}/index.html`.

### Step 5 — Extract image URLs (optional)

```
mcp__claude-in-chrome__javascript_tool
  code: "[...document.querySelectorAll('img')].map(i=>i.src).join('\\n')"
```

Use the returned list to download relevant images into `raw/{slug}/assets/` if needed.

---

## After Browser Extraction

Save the extracted content under `.claude/read/raw/{slug}/index.html` (done in Step 4), then hand the saved raw file to SKILL.md Stage 2 (Convert) — the Stage 2/3 pipeline (tmp intermediate, image handling, final slug + dedup, frontmatter, index row) applies unchanged. Never convert straight into `material/`, and always pass markitdown the **file path**, not the original URL.
