# Setup — Linux

## Prerequisites

- Python 3.8 or later
- pip3
- git

## Self-Check Commands

```bash
python3 --version
pip3 --version
python3 -m markitdown --version
```

Expected: Python 3.8+, pip present, markitdown version printed.

## markitdown Installation

```bash
pip3 install markitdown
```

Or:

```bash
python3 -m pip install markitdown
```

## Chrome Setup

### Option A — Chrome + Claude-in-Chrome Extension

1. Install Google Chrome for Linux.
2. Install the "Claude in Chrome" extension.
3. The extension connects via a local port. Test: run `mcp__claude-in-chrome__tabs_context_mcp`.

### Option B — CDP Proxy (no Chrome extension)

Install a headless Chrome CDP wrapper on port 3456. Any wrapper that exposes:

- `GET /new?url={url}` → opens a tab, returns `{"id": "..."}` 
- `POST /eval?target={id}` with body = JS expression → evaluates and returns result

See `references/acquisition/web-dynamic.md` for the full API usage.

## Clipboard Support

Install `xclip` for clipboard access:

```bash
sudo apt install xclip
# or for xsel:
sudo apt install xsel
```

The skill tries `xclip` first, then `xsel` as fallback.
