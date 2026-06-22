## Contents

- Installation
- CLI Basic Usage
- Supported Input Formats
- Known Issues

# markitdown Guide

## Installation

```bash
pip install markitdown
```

Or run the bundled helper:

```bash
bash scripts/install-deps.sh
```

---

## CLI Basic Usage

### Convert a local file

```bash
markitdown "path/to/file.html" -o output.md
```

Always quote paths to handle filenames with spaces or special characters.

### Fetch and convert a URL (static content only)

```bash
markitdown "https://example.com" -o output.md
```

Use this only for pages that return full HTML without JavaScript rendering. For JS-rendered pages, save the content to `raw/` first and pass the file path instead.

### Read from stdin

```bash
cat file.html | markitdown -
```

### The `-o` flag

- `-o output.md`: write the result to the specified file.
- Omit `-o` to print the Markdown to stdout.

---

## Supported Input Formats

| Format | Notes |
|--------|-------|
| HTML | Most common web capture format |
| PDF | Text-based PDFs; scanned PDFs require OCR extras |
| Word (.docx) | Preserves headings and lists |
| Excel (.xlsx) | Converts sheets to Markdown tables |
| PowerPoint (.pptx) | Slide text extracted sequentially |
| Plain text (.txt) | Passed through with minimal transformation |
| ZIP | Extracts and converts contained files |
| Images (PNG, JPG, etc.) | Requires OCR extras (`pip install markitdown[ocr]`) |
| Audio (MP3, WAV, etc.) | Requires audio extras (`pip install markitdown[audio]`) |

---

## Known Issues

### onnxruntime GPU warning in WSL2

On WSL2, markitdown may emit a warning about onnxruntime and GPU availability. This is non-fatal and does not affect output quality.

Suppress it with:

```bash
markitdown "file.html" -o output.md 2>/dev/null
```

Or filter selectively:

```bash
markitdown "file.html" -o output.md 2>&1 | grep -v onnxruntime
```

### data URI images are truncated by default

Inline data-URI images (e.g., `data:image/png;base64,...`) are truncated in the Markdown output. To preserve them:

```bash
markitdown --keep-data-uris "file.html" -o output.md
```

### JS-rendered pages (SPAs)

markitdown fetches the raw static HTML when given a URL. Single-page applications that require JavaScript execution will yield empty or skeleton output.

Correct workflow:
1. Use the browser layer to render the page and extract the HTML text.
2. Save that text to `raw/{slug}/index.html`.
3. Call markitdown with the **file path**, not the original URL:

```bash
markitdown "raw/{slug}/index.html" -o material/{slug}/index.md
```

Never pass the original URL to markitdown after saving via the browser layer — pass the saved file path.
