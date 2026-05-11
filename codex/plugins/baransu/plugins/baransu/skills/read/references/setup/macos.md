# Setup — macOS

## Prerequisites

- Python 3.8 or later (install via Homebrew: `brew install python`)
- pip3 (bundled with Homebrew Python)

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

If using system Python (not Homebrew), install to user directory to avoid permission issues:

```bash
pip3 install --user markitdown
```

## Chrome Setup

1. Install Google Chrome for macOS.
2. Install the "Claude in Chrome" extension.
3. Test connectivity: run `mcp__claude-in-chrome__tabs_context_mcp`.

## Clipboard

`pbpaste` is built-in on macOS. No extra installation is needed.

```bash
pbpaste  # prints clipboard contents to stdout
```

## Common Issues

### Apple Silicon (M1/M2/M3)

markitdown installs ARM-native wheels on Apple Silicon. This is expected and works correctly — no special flags needed.

### pip install fails due to SSL error

```bash
pip3 install --trusted-host pypi.org markitdown
```

### Homebrew Python conflicts with system Python

Use the full path if needed:

```bash
/opt/homebrew/bin/python3 -m pip install markitdown
```
