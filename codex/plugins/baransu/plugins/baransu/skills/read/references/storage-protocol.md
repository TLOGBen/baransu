# Storage Protocol

## Directory Structure

All captured content lives under `.claude/read/` relative to the repository root.

```
.claude/read/
  index.md               # master index (append-only)
  raw/{slug}/
    index.{ext}          # original fetched content (immutable)
    assets/              # downloaded assets (immutable)
  material/{slug}/
    index.md             # converted Markdown output
    assets/              # asset copies or references
```

### `raw/{slug}/` — Immutable original

- `index.{ext}`: the original fetched/downloaded file. Extension matches the source format: `.html`, `.pdf`, `.txt`, `.docx`, etc.
- `assets/`: any downloaded assets (images, attachments) belonging to that capture.
- **Immutability rule**: once `raw/{slug}/` is written, never modify or delete its contents. It is the permanent record of the original source state.

### `material/{slug}/` — Processed output

- `index.md`: Markdown result from markitdown conversion. Contains YAML frontmatter (see below) followed by the converted body.
- `assets/`: copied or referenced asset files used in the Markdown body.

---

## YAML Frontmatter for `material/{slug}/index.md`

Every `material/{slug}/index.md` begins with this frontmatter block:

```yaml
---
source_url: "https://..."
title: "Page Title"
captured_at: "2026-04-25T22:00:00+08:00"
conversion_tool: "markitdown 0.x.x"
slug: "page-title"
platform: "WSL2"
---
```

Field notes:
- `source_url`: the original URL or file path that was captured.
- `title`: page title, filename stem, or best-available description.
- `captured_at`: ISO 8601 timestamp with timezone at moment of capture.
- `conversion_tool`: include the actual version number from `python3 -m markitdown --version`.
- `slug`: the slug used for this capture's directory name.
- `platform`: detected platform string (`WSL2`, `Linux`, `macOS`, `Windows`).

---

## `.claude/read/index.md` — Master Index

Format: a Markdown table with four columns.

```markdown
| source_url | slug | title | captured_at |
|------------|------|-------|-------------|
| https://example.com/page | page-title | Page Title | 2026-04-25T22:00:00+08:00 |
```

Rules:
- Create the file with the header row if it does not exist.
- Always **append** a new row; never overwrite existing rows.
- One row per capture. Multiple captures of the same URL get separate rows (with versioned slugs).

---

## Slug Generation Rules

Given a page title (preferred) or the final path segment of the URL:

1. Lowercase the entire string.
2. Replace all non-ASCII characters and non-hyphen punctuation with hyphens.
3. Replace spaces with hyphens.
4. Collapse consecutive hyphens into a single hyphen.
5. Strip leading and trailing hyphens.
6. Truncate to a maximum of 60 characters (cut at a hyphen boundary if possible).

Examples:
- `"My Page Title"` → `my-page-title`
- `"React 18 — What's New?"` → `react-18-whats-new`
- `"https://example.com/docs/getting-started"` → `getting-started`

---

## Dedup Flow

Before creating a new capture, check for conflicts in `.claude/read/index.md`:

1. Read `.claude/read/index.md` (if it does not exist, no dedup needed — proceed).
2. Search for an existing row where `source_url` matches the incoming URL exactly.
   - **Match found**: find the highest existing `_vN` suffix on that slug (e.g., `my-page_v2`). Use `_v{N+1}` as the new slug. If no `_vN` suffix exists yet, the new slug is `{base-slug}_v2`.
3. If no `source_url` match, check whether the generated slug already exists (title collision with a different URL).
   - **Slug collision with different URL**: append `_v2` to the new slug.
4. If neither conflict exists, use the slug as generated.
