# Setup — WSL2

## Prerequisites

- Python 3.8 or later
- pip3
- git
- gh CLI (optional; needed for private GitHub repo access)

## Self-Check Commands

Run these to verify the environment is ready:

```bash
python3 --version
pip3 --version  # or: python3 -m pip --version
python3 -m markitdown --version 2>&1 | grep -v onnxruntime | head -1
grep -qi microsoft /proc/version && echo "WSL2 detected" || echo "Not WSL2"
```

Expected: Python 3.8+, pip present, markitdown version printed, "WSL2 detected".

## markitdown Installation

```bash
pip3 install markitdown
```

Or run the bundled helper script:

```bash
bash scripts/install-deps.sh
```

## Chrome Setup

1. Install the "Claude in Chrome" extension in Windows Chrome.
2. WSL2 runs in NAT mode by default — Windows automatically forwards WSL2 ports. No extra `.wslconfig` changes are needed.
3. Test connectivity: run `mcp__claude-in-chrome__tabs_context_mcp`. If it returns tab data, Chrome is connected.

## Common Issues

### onnxruntime GPU warning

Symptom: markitdown prints a warning about onnxruntime GPU availability.

This is non-fatal. Suppress with:

```bash
markitdown "file.html" -o output.md 2>/dev/null
# or filter selectively:
markitdown "file.html" -o output.md 2>&1 | grep -v onnxruntime
```

### pip not found

Try the module form:

```bash
python3 -m pip install markitdown
```

### gh CLI not installed

For public GitHub repos, `gh` is not required — use `raw.githubusercontent.com` directly. For private repos, install gh and authenticate:

```bash
gh auth login
```
