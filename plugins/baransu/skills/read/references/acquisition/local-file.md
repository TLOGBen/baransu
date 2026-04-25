# Local File Acquisition

## Single Path

When the input is a single file path:

1. Verify the file exists:

```bash
test -f "{path}" || { echo "File not found: {path}"; exit 1; }
```

2. Determine the original file extension from the path.

3. Copy the file to `raw/{slug}/index.{ext}` preserving the original extension:

```bash
cp "{path}" "raw/{slug}/index.{ext}"
```

4. Derive the slug from the filename stem (see Slug Rules below).

5. Proceed with the standard Convert → Organize pipeline.

---

## Glob Expansion

When the input contains glob characters (`*`, `?`, `[...]`):

1. Expand the glob:

```bash
files=($(ls {pattern} 2>/dev/null))
```

2. If no files match, report: "無匹配項目：{pattern}" and stop. Do not create any `raw/` directories.

3. For each matched file, run the full pipeline independently:
   - Each file gets its own slug derived from its filename stem.
   - Each file produces its own `raw/{slug}/` and `material/{slug}/` directories.
   - Each file appends its own row to `.claude/read/index.md`.

Process files sequentially to avoid index append collisions.

---

## Slug Rules for Local Files

Use the filename stem (the filename without its extension) as the slug input.

Apply the standard slug rules:
1. Lowercase.
2. Replace non-ASCII characters and non-hyphen punctuation with hyphens.
3. Replace spaces with hyphens.
4. Collapse consecutive hyphens into a single hyphen.
5. Strip leading and trailing hyphens.
6. Truncate to a maximum of 60 characters.

Examples:
- `report_2026.pdf` → stem `report_2026` → slug `report-2026`
- `My Notes (Draft).docx` → stem `My Notes (Draft)` → slug `my-notes-draft`
- `README.md` → stem `README` → slug `readme`
