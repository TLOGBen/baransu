import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def lean():
    exe = shutil.which("lean")
    if not exe:
        print("missing on PATH: lean")
        return 2
    p = subprocess.run([exe, "GitAccount.lean"], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    out = p.stdout + p.stderr
    if p.returncode == 0 and "sorry" not in out:
        print("lean GitAccount.lean: proved")
        print("\n".join(x for x in out.splitlines() if "depends on axioms" in x))
        return 0
    print(out[-4000:])
    broken = re.search(r"\.lean:\d+:\d+: error", out) or "sorry" in out
    return 1 if broken else 2


def tlc():
    exe = shutil.which("tlc.cmd") or shutil.which("tlc")
    if not exe:
        print("missing on PATH: tlc")
        return 2
    with tempfile.TemporaryDirectory(prefix="quick-", ignore_cleanup_errors=True) as tmp:
        work = Path(tmp)
        for name in ("GitAccount.tla", "GitAccount.cfg"):
            shutil.copy(HERE / name, work / name)
        p = subprocess.run(
            [exe, "-workers", "1", "-deadlock", "-metadir", str(work / "meta"), "-config", "GitAccount.cfg", "GitAccount.tla"],
            cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
        )
    out = p.stdout + p.stderr
    if p.returncode == 0:
        states = re.findall(r"(\d+) distinct states found", out)
        print(f"tlc GitAccount.tla: no error, {states[-1] if states else '?'} distinct states")
        return 0
    print("\n".join(x for x in out.splitlines() if x.startswith("Error:")))
    print(out[-4000:])
    return 1 if p.returncode in (12, 13) else 2


def main():
    codes = [lean(), tlc()]
    return 1 if 1 in codes else 2 if 2 in codes else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"judge crashed: {type(e).__name__}: {e}")
        sys.exit(2)
