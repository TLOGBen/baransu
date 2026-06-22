## Contents

- Local-First Fetch (default)
- Proxy Cascade (`--use-proxy` opt-in only)
- GitHub URL Routing
- PDF URL Routing

# Web — Static Content Acquisition

## Local-First Fetch (default)

This is the default path. The URL is fetched directly from this machine and extraction happens locally (markitdown in Stage 2) — the URL is never sent to any third-party proxy unless the user explicitly passed `--use-proxy`.

```bash
curl -sL "{url}" \
  -H "Accept: text/html" \
  -H "User-Agent: Mozilla/5.0" \
  -o raw/{slug}/index.html
```

Quality checks:
- Word count > 100
- More than 5 non-empty lines

Routing after the checks:

- **Checks pass** → continue to Stage 2 (Convert) with the local file.
- **Checks fail, `--use-proxy` NOT passed** → do NOT silently fall back to a proxy. Discard the file, record the failure, and report to the user: 「本地抓取品質不足：{url}。可改用 --use-proxy（內容會經第三方代理）或 --chrome（瀏覽器抓取）。」
- **Checks fail, `--use-proxy` passed** → run the Hard Rule check below, then proceed to the Proxy Cascade.

## Proxy Cascade (`--use-proxy` opt-in only)

The cascade sends the URL to third-party services (defuddle.md, r.jina.ai). It runs only when the user explicitly passed `--use-proxy` and the direct fetch above failed quality checks.

### Hard rule — never proxy authenticated or internal URLs

Even with `--use-proxy`, a URL must NEVER be sent to any proxy if it matches any of:

- Credentials embedded in the URL (`user:pass@host`)
- Query parameters carrying secrets or session material (`token=`, `key=`, `apikey=`, `api_key=`, `access_token=`, `sig=`, `signature=`, `session=`)
- Private or internal hosts: `localhost`, `127.0.0.1`, `*.local`, `*.internal`, RFC1918 addresses (`10.*`, `172.16-31.*`, `192.168.*`), or single-label intranet hostnames
- Any URL the user has indicated requires login

If matched: skip the cascade entirely and output 「此 URL 屬於認證或內部資源，禁止送往代理服務。請改用 --chrome 以登入態瀏覽器抓取。」

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

### All layers fail

If the direct fetch and (when permitted) both proxy layers fail quality checks or return HTTP errors:
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
