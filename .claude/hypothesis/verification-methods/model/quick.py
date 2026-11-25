import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    p = subprocess.run([sys.executable, "check.py", *sys.argv[1:]], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    out = p.stdout + p.stderr
    print(out.rstrip())
    if p.returncode == 0:
        return 0
    return 1 if p.returncode == 1 and re.search(r"R1 plain  broken by [1-9]", out) else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"judge crashed: {type(e).__name__}: {e}")
        sys.exit(2)
