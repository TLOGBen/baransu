# X (Twitter) — Search Acquisition (`--x`)

This lane is a **thin shell**. It does not implement Chrome navigation itself — it delegates to `web-dynamic.md`.

## Search Phase

Build the search URL by URL-encoding the keyword:

```
target_url = "https://x.com/search?q={url-encoded-keyword}"
```

Then **follow `references/acquisition/web-dynamic.md` WSL2 Path Steps 1–4** (`tabs_create_mcp` → `navigate` → wait for load → `get_page_text`) using `target_url` as the navigation target.

The returned page text is held **in process memory only** for health check + candidate extraction. **Do not write it to `raw/`** at this stage. The search page never becomes a `material/{slug}/index.md`; only the user-selected tweet URL does (that happens at the Collect Phase via `web-dynamic.md`'s own raw-write).

> **Why a shell?** `web-dynamic.md` already specifies the canonical Chrome MCP sequence. Re-implementing it here would duplicate maintenance and let the two flows drift. This lane only contributes (a) the X URL builder, (b) the schema-level health check, (c) the candidate-extraction regex, (d) the handoff back to the URL pipeline.

If `--x ""` (empty keyword): output 「請提供關鍵字」 and stop. Do not invoke navigation.

If `$CHROME_AVAILABLE=false`: output 「Chrome 未連線，--x 模式無法使用」 and stop (mirrors `--chrome` degraded-mode rule).

---

## Schema-level Health Check

After `get_page_text` returns, before any candidate extraction or AskUserQuestion, check the in-memory page text against the rules below. Any rule failure → fail-fast with the matching message and stop. Discard the in-memory text. Do not write anything to `raw/`; do not invoke AskUserQuestion.

| Rule | Substring / Condition | Fail-fast message |
|------|----------------------|-------------------|
| 1 | text contains `"Log in to Twitter"` | 「X 未登入，請以 `--chrome` 開分頁手動登入後重試」 |
| 2 | text contains `"Sign in to X"` | 「X 未登入，請以 `--chrome` 開分頁手動登入後重試」 |
| 3 | text contains `"Something went wrong"` | 「X 暫時拒絕請求，稍後再試」 |
| 4 | text contains `"Rate limit exceeded"` | 「X 暫時拒絕請求，稍後再試」 |
| 5 | text length < 500 characters | 「X 搜尋結果為空或未渲染完成」 |

This is schema-level shape inspection only — not content evaluation. The in-memory page text is never persisted regardless of pass/fail; only the user-selected tweet URL eventually becomes a `material/`, preserving the "採集者只搬運不審判" invariant + the "raw/ is immutable" rule (see SKILL.md `Constraints`).

---

## Candidate Extraction

If health check passes, extract tweet-status URLs from the page text using regex:

```
https://x\.com/[^/]+/status/\d+
```

Deduplicate by exact URL. The regex is selector-free (does not depend on volatile DOM structure); the URL form `https://x.com/{handle}/status/{id}` is X's stable status URL contract.

If the regex matches **0 candidates**: output 「X 搜尋無可選 tweet（DOM 結構可能已變）」 and stop. Treat as acquire-stage failure (same response shape as a failed health check).

Each candidate is normalized to the shared shape:

```json
{
  "url": "{tweet status URL}",
  "title": "{handle/status_id}",
  "description": "{first 100 chars of surrounding context, if extractable; else handle name}",
  "meta": {
    "author_handle": "{handle from URL}",
    "tweet_excerpt": "{up to 100 chars}"
  }
}
```

---

## Display to User

See `SKILL.md §AskUserQuestion 互動規格` for capacity, escape, multi-round, termination. This lane uses the spec as-is.

---

## Collect Phase

When the user selects one tweet URL, hand it back to `/read`'s existing URL routing in `SKILL.md` Stage 1 §9. **Do not force Chrome MCP at this stage** — the URL is a regular tweet status URL; routing will detect SPA characteristics and route to `web-dynamic.md` automatically.

This staging — Chrome MCP mandatory at search phase, optional (auto-routed) at collect phase — is `KD2: --x 階段化 Chrome MCP`.

The `material/{slug}/index.md` frontmatter must include:

```yaml
acquire_via: "search:x"
```

If the user picks escape, terminate without writing anything.
