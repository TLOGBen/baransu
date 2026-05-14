# Academic Paper Search Acquisition

## Empty Keyword Fail-Fast

If `/read --topic ""` (empty keyword): output 「請提供關鍵字」 and stop. Do not invoke `search-papers.py`.

This guard is shared with the other three search-type lanes (`--web` / `--gh` / `--x`) per `requirement.md` REQ-008 Scenario 3 (cross-cutting fail-fast).

---

## Search Command

```bash
python3 "./scripts/search-papers.py" "{keyword}" 2>/dev/null
```

Replace `{keyword}` with the user's search term (quote it to handle spaces).

---

## Output Format

The script outputs a JSON array. Each entry contains:

```json
{
  "title": "Paper Title",
  "authors": ["Author One", "Author Two"],
  "year": 2024,
  "abstract_preview": "First 2–3 sentences of the abstract...",
  "pdf_url": "https://example.com/paper.pdf",
  "doi": "10.1234/example",
  "source": "semantic_scholar"
}
```

Fields `pdf_url` and `doi` may be `null`.

---

## Display to User

Normalize each paper entry to the shared candidate shape:

```json
{
  "url": "{pdf_url or https://doi.org/{doi}}",
  "title": "{title} ({year})",
  "description": "{authors[0]} et al. — {abstract_preview} — [PDF available] or [DOI only]",
  "meta": {
    "authors": "{authors}",
    "year": "{year}",
    "pdf_url": "{pdf_url}",
    "doi": "{doi}",
    "source": "{source}"
  }
}
```

Then present candidates via AskUserQuestion per `SKILL.md §AskUserQuestion 互動規格` — capacity, escape, multi-round, and termination semantics are defined there. This lane uses the spec as-is.

`title` populates the AskUserQuestion `label`; `description` populates the option `description`; `url` is the value carried forward.

---

## User Selection

User selection happens via AskUserQuestion (single-pick semantics; selection terminates the round sequence). The selected paper proceeds through the Acquire → Convert → Organize pipeline; if the user picks the escape option (`「以上都不選」`), terminate with no material output.

For `N = 10` candidates from `search-papers.py` (default), the round mapping in `SKILL.md §AskUserQuestion 互動規格` truncates to the first 9 by `search-papers.py`'s native ranking and presents 3 rounds (3 + 3 + 3 result slots, plus escape per round).

Single-pick replaces the prior multi-select (`1 3 5`) workflow; multi-paper sessions are achieved by re-invoking `/read --topic "keyword"` after each paper finishes.

---

## No Results

If the script outputs an empty JSON array (`[]`):
- Report: "未找到相關論文，請嘗試調整關鍵字"
- Stop.

---

## PDF URL Available Path

When `pdf_url` is non-null:
- Use `pdf_url` as the target URL.
- Route to the web-static.md **PDF URL Routing** flow.
- Slug is derived from the paper title.

## DOI-Only Path

When `pdf_url` is null but `doi` is non-null:
- Construct the URL: `https://doi.org/{doi}`
- Route to the web-static.md **Proxy Cascade** flow (general HTML).
- Note in the `material/{slug}/index.md` frontmatter and in the user-facing report: "已抓取摘要頁面而非全文 PDF"

---

## Frontmatter

The resulting `material/{slug}/index.md` frontmatter must include:

```yaml
acquire_via: "topic"
```

(See `SKILL.md` Stage 3 §6 for the full schema.)
