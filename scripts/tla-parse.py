"""Check one TLA+ module before TLC sees it. Exit 0 when it passes; non-zero with the reason when it does not.

1. SANY parses it, the way TLC will read it: from the module's own folder, by bare file name (SANY rejects a path
   with folders as a module-name mismatch, and resolves EXTENDS from the working folder).
2. No definition both primes a variable and lists it in its top-level UNCHANGED: the two contradict, so the action
   can never be taken, and neither SANY nor TLC says so (TLC just explores fewer states). A variable primed in one
   branch of IF ... THEN UNCHANGED ... ELSE is not top-level and is left alone.

Used by .claude/lint/checks/tla-parses.toml. Both checks come from mistakes made on 2026-11-03.
"""
import re
import subprocess
import sys
from pathlib import Path

JAR = Path.home() / ".local" / "share" / "formal" / "tla" / "tla2tools.jar"
DEF = re.compile(r"^([A-Za-z_]\w*)\s*(\([^)]*\))?\s*==")
TUPLE = re.compile(r"^([A-Za-z_]\w*)\s*==\s*<<(.*?)>>\s*$", re.S)


def sany(path: Path) -> str | None:
    out = subprocess.run(["java", "-cp", str(JAR), "tla2sany.SANY", path.name], cwd=path.parent,
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if out.returncode == 0:
        return None
    lines = [l for l in (out.stdout + out.stderr).splitlines() if l.strip() and not l.startswith("Picked up")]
    return "\n".join(lines[-12:])


def definitions(text: str) -> list[tuple[str, int, str]]:
    """Each top-level definition: name, first line number, body (comments removed)."""
    text = re.sub(r"\(\*.*?\*\)", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    lines = [re.sub(r"\\\*.*$", "", l) for l in text.splitlines()]
    defs, cur = [], None
    for i, line in enumerate(lines, 1):
        m = DEF.match(line)
        if m or line.startswith("====") or re.match(r"^(VARIABLES?|CONSTANTS?|EXTENDS)\b", line):
            if cur:
                defs.append(cur)
            cur = (m.group(1), i, [line]) if m else None
        elif cur:
            cur[2].append(line)
    if cur:
        defs.append(cur)
    return [(n, i, "\n".join(body)) for n, i, body in defs]


def contradictions(text: str) -> list[str]:
    defs = definitions(text)
    tuples = {}
    for name, _, body in defs:
        m = TUPLE.match(body.strip())
        if m:
            tuples[name] = [t.strip() for t in m.group(2).replace("\n", " ").split(",") if t.strip()]

    def expand(names, seen=()):
        for n in names:
            if n in tuples and n not in seen:
                yield from expand(tuples[n], seen + (n,))
            else:
                yield n

    # A variable primed in a definition this one uses (Step == n' = n + 1) is primed here too.
    names = {n for n, _, _ in defs}
    direct = {n: set(re.findall(r"\b([A-Za-z_]\w*)'", b)) for n, _, b in defs}
    uses = {n: set(re.findall(r"\b([A-Za-z_]\w*)\b", b.split("==", 1)[1])) & names - {n} for n, _, b in defs}

    def primes(n, seen=()):
        out = set(direct.get(n, ()))
        for u in uses.get(n, ()):
            if u not in seen:
                out |= primes(u, seen + (n,))
        return out

    found = []
    for name, start, body in defs:
        lines = body.splitlines()
        conj = [len(l) - len(l.lstrip()) for l in lines[1:] if l.lstrip().startswith("/\\")]
        if not conj:
            continue
        top = min(conj)
        unchanged = []
        for k, l in enumerate(lines):
            if len(l) - len(l.lstrip()) == top and l.lstrip().startswith("/\\ UNCHANGED"):
                chunk = l
                j = k
                while "<<" in chunk and ">>" not in chunk and j + 1 < len(lines):
                    j += 1
                    chunk += " " + lines[j]
                inner = re.search(r"UNCHANGED\s*(<<(.*?)>>|([A-Za-z_]\w*))", chunk, re.S)
                if inner:
                    unchanged += [t.strip() for t in (inner.group(2) or inner.group(3)).split(",") if t.strip()]
        clash = sorted(primes(name) & set(expand(unchanged)))
        if clash:
            found.append(f"line {start}: {name} primes {', '.join(clash)} and also lists it in UNCHANGED — the action can never be taken")
    return found


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: tla-parse.py <file.tla>")
        return 2
    path = Path(sys.argv[1]).resolve()
    err = sany(path)
    if err:
        print(err)
        return 1
    clash = contradictions(path.read_text(encoding="utf-8"))
    if clash:
        print("\n".join(clash))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
