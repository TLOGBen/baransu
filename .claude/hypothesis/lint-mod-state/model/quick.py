import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
USAGE = "usage: python quick.py CONFIG.cfg MODULE.tla"


def main():
    if len(sys.argv) != 3:
        print(USAGE)
        return 2
    cfg, module = sys.argv[1], sys.argv[2]
    tlc = shutil.which("tlc.cmd") or shutil.which("tlc")
    if not tlc:
        print("missing on PATH: tlc")
        return 2
    with tempfile.TemporaryDirectory(prefix="quick-", ignore_cleanup_errors=True) as tmp:
        work = Path(tmp)
        for f in HERE.glob("*.tla"):
            if "_TTrace_" not in f.name:
                shutil.copy(f, work / f.name)
        shutil.copy(HERE / cfg, work / cfg)
        p = subprocess.run(
            [tlc, "-workers", "1", "-deadlock", "-metadir", str(work / "meta"), "-config", cfg, module],
            cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
        )
    out = p.stdout + p.stderr
    if p.returncode == 0:
        states = re.findall(r"(\d+) distinct states found", out)
        print(f"{module} {cfg}: no error, {states[-1] if states else '?'} distinct states")
        return 0
    print("\n".join(x for x in out.splitlines() if x.startswith("Error:")))
    print(out[-4000:])
    return 1 if p.returncode in (12, 13) else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"judge crashed: {type(e).__name__}: {e}")
        sys.exit(2)
