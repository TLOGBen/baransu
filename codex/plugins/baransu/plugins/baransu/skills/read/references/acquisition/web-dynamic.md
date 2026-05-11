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

## WSL2 Path (platform == WSL2)

Use the Claude-in-Chrome MCP tools.

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

Save the returned text to `raw/{slug}/index.html`.

### Step 5 — Extract image URLs (optional)

```
mcp__claude-in-chrome__javascript_tool
  code: "document.querySelectorAll('img').map(i=>i.src).join('\\n')"
```

Use the returned list to download relevant images into `raw/{slug}/assets/` if needed.

---

## Non-WSL2 CDP Proxy Path

Use a local headless Chrome CDP wrapper running on port 3456.

### Step 1 — Open new tab

```bash
curl -s "http://localhost:3456/new?url={encoded_url}"
```

Returns: `{"id": "target_id"}`

Encode the URL before inserting it into the query string.

### Step 2 — Wait for page load

```bash
curl -s "http://localhost:3456/eval?target={id}" \
  -d 'document.readyState'
```

Repeat until the value is `"complete"`.

### Step 3 — Extract page text

```bash
curl -X POST "http://localhost:3456/eval?target={id}" \
  -d 'document.body.innerText'
```

Save the result to `raw/{slug}/index.html`.

### Step 4 — Extract image URLs (optional)

```bash
curl -X POST "http://localhost:3456/eval?target={id}" \
  -d "document.querySelectorAll('img').map(i=>i.src).join('\\n')"
```

Use the returned list to download images into `raw/{slug}/assets/` if needed.

---

## After Browser Extraction

Once `raw/{slug}/index.html` is saved, convert with markitdown using the **file path**, not the original URL:

```bash
markitdown "raw/{slug}/index.html" -o material/{slug}/index.md
```
