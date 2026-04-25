# Academic Paper Search Acquisition

## Search Command

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/search-papers.py" "{keyword}" 2>/dev/null
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
  "source": "arxiv"
}
```

Fields `pdf_url` and `doi` may be `null`.

---

## Display to User

Show a numbered list. For each entry:

```
{N}. {title} ({year}) — {authors[0]} et al.
   {abstract_preview}
   [PDF available] or [DOI only]
```

Use `[PDF available]` if `pdf_url` is non-null. Use `[DOI only]` if only `doi` is available.

---

## User Selection

Ask the user to input the number(s) of papers to capture. Accept space-separated values for multiple selections (e.g., `1 3 5`).

Process each selected paper independently through the full Acquire → Convert → Organize pipeline.

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

## Multiple Selection

Each selected paper runs independently:
- Its own slug (derived from paper title).
- Its own `raw/{slug}/` and `material/{slug}/` directories.
- Its own row appended to `.claude/read/index.md`.

Process papers sequentially to avoid index append collisions.
