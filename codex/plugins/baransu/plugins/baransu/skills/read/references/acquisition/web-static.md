# Web — Static Content Acquisition

## Proxy Cascade

Try each layer in order. Move to the next layer if the result is fewer than 5 non-empty lines or lacks substantive text (word count < 100).

### Layer 1 — Defuddle proxy

```bash
curl -sL "https://defuddle.md/{url}" -o raw/{slug}/index.html
```

Quality checks:
- Word count > 100
- More than 5 non-empty lines

If either check fails, discard the file and proceed to Layer 2.

### Layer 2 — Jina reader

```bash
curl -sL "https://r.jina.ai/{url}" -o raw/{slug}/index.md
```

Note: pass the target URL as-is after the slash. For `http://` URLs, Jina prepends its own scheme automatically — do not double-encode or modify the scheme.

Quality checks: same as Layer 1 (word count > 100, > 5 non-empty lines).

If either check fails, discard the file and proceed to Layer 3.

### Layer 3 — Direct fetch

```bash
curl -sL "{url}" \
  -H "Accept: text/html" \
  -H "User-Agent: Mozilla/5.0" \
  -o raw/{slug}/index.html
```

### All layers fail

If all three layers fail quality checks or return HTTP errors:
- Do NOT create any `raw/{slug}/` files.
- Record the failure.
- Report to the user: what URL was attempted, which layers were tried, and the failure reason for each.

---

## GitHub URL Routing

Pattern detected: `github.com/{owner}/{repo}/blob/{branch}/{path}`

Convert to raw URL:

```
raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
```

Example:
- Input: `https://github.com/owner/repo/blob/main/README.md`
- Converted: `https://raw.githubusercontent.com/owner/repo/main/README.md`

Then fetch with:

```bash
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}" \
  -o raw/{slug}/index.{ext}
```

Alternative for public repos (no auth needed):

```bash
gh api repos/{owner}/{repo}/contents/{path}
```

The `gh api` response is JSON with a `content` field containing base64-encoded file content. Decode with:

```bash
gh api repos/{owner}/{repo}/contents/{path} | python3 -c "import sys,json,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())"
```

For private repos: `gh api` with an authenticated token. If authentication fails, report: "需要 gh auth".

---

## PDF URL Routing

Detection:
- URL ends with `.pdf`, OR
- `curl -sI "{url}" | grep -i "content-type: application/pdf"` matches

Download:

```bash
curl -sL "{url}" -o raw/{slug}/index.pdf
```

Save as `index.pdf`. Use extension `pdf` for the markitdown call:

```bash
markitdown "raw/{slug}/index.pdf" -o material/{slug}/index.md
```
