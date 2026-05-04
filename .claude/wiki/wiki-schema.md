# Wiki Schema — LLM Maintenance Protocol

This file defines how an LLM (via `claude -p`) should maintain the `.claude/wiki/` directory.
Read this file before making any changes to `index.md` or `log.md`.

---

## Directory Structure

```
.claude/wiki/
├── wiki-schema.md   ← this file; LLM maintenance protocol
├── index.md         ← 4-column knowledge index (LLM-maintained)
└── log.md           ← append-only sync log (diff baseline)
```

---

## index.md Format

The index uses a 4-column pipe-delimited Markdown table:

```
# Wiki Index

| slug | 標題 | 內容來源 | 分類標籤 |
|------|------|---------|---------|
| some-slug | Some Title | stub:read/some-slug | AI 工程 |
```

### Column definitions

| Column | Description |
|--------|-------------|
| slug | Unique identifier; matches the directory name under `read/` |
| 標題 | Human-readable title; extracted from the first `#` heading in `read/material/{slug}/index.md` |
| 內容來源 | Source pointer — either `stub:read/{slug}` or `digest:learn/digests/{filename}` |
| 分類標籤 | Category tag from the taxonomy below |

### stub entry format

Use when **no digest exists** in `learn/digests/` for this slug:

```
stub:read/{slug}
```

Example: `stub:read/context-engineering-langchain`

### digest entry format

Use when a digest file **exists** under `learn/digests/`:

```
digest:learn/digests/{filename}
```

Example: `digest:learn/digests/llm-wiki-pattern.md`

### How to determine stub vs digest

1. Check if `learn/digests/` contains a file whose name matches or closely corresponds to the slug.
2. If a matching digest file exists → use `digest:learn/digests/{filename}`.
3. If no matching digest file exists → use `stub:read/{slug}`.
4. Two slugs may share the same digest file (e.g., `llm-wiki` and `llm-wiki-v2` both point to `llm-wiki-pattern.md`).

---

## log.md Format

The log is append-only. Each entry uses the following exact format:

```
## [2026-05-04T03:00:00Z] sync | some-slug
```

- Timestamp: ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`)
- Separator: ` sync | ` (space before and after `|`)
- Slug: no trailing whitespace

`wiki-sync.sh` extracts processed slugs using:
```bash
grep -oP '(?<=sync \| )\S+' .claude/wiki/log.md
```

Do **not** deviate from this format or extraction will fail.

---

## Category Taxonomy

Use one of the following values in the 分類標籤 column:

| Tag | Description |
|-----|-------------|
| AI 工程 | AI/LLM engineering, prompt engineering, context management |
| AI 研究 | AI research, model architecture, paradigm shifts |
| 方法論 | Process methodology, workflows, design patterns |
| 系統設計 | System architecture, agent harness design, infrastructure |
| 工具與實踐 | Tooling, CLI, practical implementation guides |

Add new categories only when none of the above fit. Keep the taxonomy stable.

---

## LLM Maintenance Workflow

When `wiki-sync.sh` calls `claude -p` with a new slug, follow these steps:

1. **Read this file** (`wiki-schema.md`) to load the maintenance protocol.
2. **For each new slug**:
   a. Check if `learn/digests/` contains a file matching the slug → determines stub or digest.
   b. Read `read/material/{slug}/index.md` and extract the first `#` heading as the 標題.
   c. Select the appropriate 分類標籤 from the taxonomy above.
3. **Append a row** to `wiki/index.md` with the 4-column format:
   ```
   | {slug} | {title} | {stub_or_digest_path} | {category} |
   ```
4. **Append an entry** to `wiki/log.md`:
   ```
   ## [{ISO8601_UTC}] sync | {slug}
   ```
5. **Do not** modify `wiki-schema.md` or any files under `.claude/analyze/`.
6. **Do not** re-process slugs already present in `log.md`.
