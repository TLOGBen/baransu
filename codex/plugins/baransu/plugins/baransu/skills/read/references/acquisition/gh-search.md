# GitHub — Repo Keyword Search Acquisition (`--gh`)

## Search Command

Use `gh search repos` via Bash. **Never substitute the keyword inside a double-quoted Bash string** — `$(…)`, backticks, and `$VAR` expand inside `"…"` and create a shell-injection path. Use the single-quote form below.

### Step 1 — escape single quotes in the keyword

For every literal single quote (`'`) in the user-supplied keyword, replace it with the four characters `'\''`. Call the result `{kw_escaped}`.

| User keyword | `{kw_escaped}` |
|--------------|----------------|
| `context engineering` | `context engineering` |
| `c++ memory` | `c++ memory` |
| `it's safe` | `it'\''s safe` |
| `"foo"; rm -rf /` | `"foo"; rm -rf /` (quotes/`$`/`;` are literal inside single quotes) |

### Step 2 — run literally (single-quoted form)

```bash
gh search repos --limit 9 --sort stars \
  --json name,url,stargazerCount,description,primaryLanguage,updatedAt \
  -- '{kw_escaped}'
```

Single quotes in Bash suppress all expansion (`$VAR`, `$(…)`, backticks, history) — the keyword is passed as a single literal argv element to `gh`.

- `--limit 9` matches `SKILL.md §AskUserQuestion 互動規格` result-slot ceiling (3 rounds × 3 result slots = 9).
- `--sort stars` is the v1 default; ranking is provided by GitHub, not re-ranked locally ("搬運不審判").
- `--` terminates option parsing so a keyword starting with `-` is treated literally.
- Unicode and emoji pass through as UTF-8 bytes; no special handling required beyond Step 1.

---

## Output Schema

`gh search repos --json` returns an array. Normalize each entry to the shared candidate shape:

```json
{
  "url": "{repo url, e.g. https://github.com/owner/repo}",
  "title": "{owner/name}",
  "description": "{repo description, 1-2 lines}",
  "meta": {
    "stars": "{stargazerCount}",
    "language": "{primaryLanguage.name}",
    "description": "{full description}",
    "updatedAt": "{ISO 8601 timestamp}"
  }
}
```

In-memory only; not persisted.

---

## Display to User

See `SKILL.md §AskUserQuestion 互動規格` for capacity, escape, multi-round, termination. This lane uses the spec as-is.

`title` populates `label`; `description` populates AskUserQuestion option `description`; `url` is the value carried forward.

---

## Failure Modes

| Condition | Behaviour |
|-----------|-----------|
| Empty keyword (`/read --gh ""`) | Output 「請提供關鍵字」 and stop. Do not invoke `gh`. |
| `gh` CLI not installed (PATH lookup fails) | Output 「gh CLI 未安裝，請執行 `brew install gh` 或 `apt install gh`」 and stop. Do not fall back to GitHub REST API. |
| `gh search repos` exits non-zero with auth/rate-limit signal (`HTTP 403`, `rate limit`, `authentication`) | Output 「GitHub API rate limit 或認證失敗：{stderr 內容}，請設定 GH_TOKEN 或稍後再試」 and stop. Wording must be distinguishable from the 0-repos message below. |
| `gh search repos` returns empty array `[]` | Output 「GitHub 搜尋無 repo 結果」 and stop. Do not invoke AskUserQuestion. |
| 1 ≤ N ≤ 9 results | Apply SKILL.md round mapping. |
| N ≥ 10 (will not occur with `--limit 9`, but defensively) | Truncate to first 9 by GitHub's native sort order. |

Do not fall back to other lanes. Do not silent-retry.

---

## Handoff

When the user selects one repo, hand its `url` back to `/read`'s existing URL routing. The `github.com` host check in `SKILL.md` Stage 1 §9 routes to `web-static.md` GitHub section.

The existing `raw/{slug}/index.{ext}` → markitdown → `material/{slug}/index.md` chain is unchanged.

The `material/{slug}/index.md` frontmatter must include:

```yaml
acquire_via: "search:gh"
```

If the user picks escape, terminate without writing anything.
