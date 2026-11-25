import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    p = subprocess.run([sys.executable, "check.py", "--quick"], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    out = p.stdout + p.stderr
    lines = [re.sub(r"\s+\d+(\.\d+)?s$", "", x) for x in out.splitlines()]
    print("\n".join(re.sub(r"; \d+s;", ";", x) for x in lines))
    if p.returncode == 0:
        return 0
    mismatch = any(x.startswith("BAD") and "(expected" in x for x in lines)
    trouble = any(x.startswith("BAD") and "(expected" not in x for x in lines) or "budget spent" in out or "Traceback" in out
    return 1 if mismatch and not trouble else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"judge crashed: {type(e).__name__}: {e}")
        sys.exit(2)
