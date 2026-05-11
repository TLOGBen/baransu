# Setup — Windows

## Environment Note

Claude Code typically runs inside WSL2 even on Windows hosts. If you are running Claude Code inside WSL2, use `setup/wsl2.md` instead of this file.

Use this file only if Claude Code is running **natively in PowerShell** (uncommon).

---

## Native PowerShell Setup

### Prerequisites

- Python 3.8 or later — install from [python.org](https://python.org) or via the Microsoft Store.

### Self-Check Commands

```powershell
py --version
py -m pip --version
py -m markitdown --version
```

### markitdown Installation

```powershell
py -m pip install markitdown
```

Or:

```powershell
python -m pip install markitdown
```

Or run the bundled Windows helper script:

```powershell
scripts\install-deps.bat
```

---

## Clipboard

`Get-Clipboard` is built-in in PowerShell. No extra installation needed.

```powershell
Get-Clipboard
```

---

## Chrome Setup

Install the "Claude in Chrome" extension in Chrome. The same extension works across platforms.

---

## Limitation

Native PowerShell execution of Claude Code is less common and may have reduced toolchain support. Most Windows users should use the WSL2 setup for the best compatibility.
