# Web — Keyword Search Acquisition (`--web`)

## Search Command

Use the **WebSearch** built-in tool (not a shell command). Pass the user-provided keyword verbatim:

```
WebSearch(query: "{keyword}")
```

The tool returns a list of search result entries; treat the order as authoritative ranking.

---

## Output Schema

Normalize each WebSearch entry to the shared candidate shape:

```json
{
  "url": "{result URL}",
  "title": "{20-char truncated label}",
  "description": "{1-2 line snippet}",
  "meta": {
    "source_domain": "{hostname extracted from URL}",
    "snippet": "{full snippet text from WebSearch}"
  }
}
```

The candidate list is held in-memory only; not persisted.

---

## Display to User

See `SKILL.md §AskUserQuestion 互動規格` for capacity, escape, multi-round, and termination semantics. This lane uses the spec as-is — do not redefine.

The candidate's `title` populates the AskUserQuestion `label`; `description` populates the option `description`; `url` is the value carried forward.

---

## Failure Modes

| Condition | Behaviour |
|-----------|-----------|
| Empty keyword (`/read --web ""`) | Output 「請提供關鍵字」 and stop. Do not invoke WebSearch. |
| WebSearch returns 0 results | Output 「web 搜尋無結果，建議改關鍵字」 and stop. Do not invoke AskUserQuestion. Do not write `raw/` or `material/`. |
| WebSearch throws (API error / rate limit / geo-restriction / key missing) | Output 「web 搜尋呼叫失敗：{原因}」 and stop. Wording must be distinguishable from the 0-results message above. |
| 1 ≤ N ≤ 9 results | Apply SKILL.md round mapping (N≤3 → 1 round; 4-6 → 2; 7-9 → 3). Do not 3-round-pad small N. |
| N ≥ 10 results | Truncate to first 9 by WebSearch's native order (no re-ranking — preserve "搬運不審判"). 3 rounds. |

Do not fall back to other lanes. Do not silent-retry.

---

## Handoff

When the user selects one URL, hand it back to `/read`'s existing URL routing in `SKILL.md` Stage 1 §9:
- `github.com` / `raw.githubusercontent.com` host → web-static.md GitHub section
- `.pdf` URL or `content-type: application/pdf` → web-static.md PDF URL section
- SPA detected (response < 500 bytes or feature strings) → web-dynamic.md
- Otherwise → web-static.md Local-First Fetch flow（代理需 --use-proxy 顯式開啟）

The existing `raw/{slug}/index.{ext}` → markitdown → `material/{slug}/index.md` chain is unchanged.

The `material/{slug}/index.md` frontmatter must include:

```yaml
acquire_via: "search:web"
```

(See SKILL.md Stage 3 §6 for the full frontmatter schema; this lane only adds the `acquire_via` value.)

If the user picks the escape option ("以上都不選"), terminate without writing anything.
