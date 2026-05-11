# Clipboard Acquisition

## Platform Clipboard Commands

Try commands in order for the detected platform. Use the first command that succeeds (exit code 0 and non-empty output).

### WSL2 / Linux

```bash
# Primary
xclip -selection clipboard -o 2>/dev/null

# Fallback
xsel --clipboard --output 2>/dev/null
```

If both fail (tools not installed or clipboard empty), report the error and stop.

### macOS

```bash
pbpaste
```

Built-in; no extra installation needed.

### Windows (native PowerShell)

```powershell
powershell.exe -Command "Get-Clipboard"
```

---

## Saving Clipboard Content

Write the clipboard text to:

```
raw/{slug}/index.txt
```

where `slug = clipboard-{YYYYMMDD-HHMMSS}` using the current local timestamp.

Example slug: `clipboard-20260425-220000`

Use a timestamp-based slug because there is no title or URL to derive one from.

---

## Conversion Note

Clipboard text that is already valid Markdown is acceptable input to markitdown. The conversion output may look identical or nearly identical to the input — this is expected behavior, not an error. Proceed normally through the Convert → Organize pipeline regardless.
