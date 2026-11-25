import sys

MIN_PYTHON = (3, 11)
if sys.version_info < MIN_PYTHON:
    print(f"run.py needs Python {'.'.join(map(str, MIN_PYTHON))} or newer (it reads check.toml with tomllib); "
          f"this is {sys.version.split()[0]}", file=sys.stderr)
    sys.exit(2)

import argparse
import datetime
import difflib
import fnmatch
import hashlib
import json
import math
import os
import re
import shutil
import signal
import subprocess
import time
import tomllib
from pathlib import Path
from types import SimpleNamespace

VERSION = "1"
QUICK_LIMIT = 420
QUICK_TIER_LIMIT = 600
FULL_TIMEOUT = 3600
DEFAULT_RUNS = 5
REPLAY_MIN_RUNS = 5
REPLAY_KINDS = ("replays", "codex-replays")
PYTHONS = ("python", "python3")
TAIL = 15
RECORD = "record.json"
SKIP_DIRS = {"results", "traces", "states", "__pycache__"}
SKIP_NAMES = ("*.bin", "*_TTrace_*", "*.pyc", RECORD)
NOISE = tuple(re.compile(p) for p in (
    r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}",
    r"\b\d{1,2}:\d{2}:\d{2}\b",
    r"(?i)\b\d+(\.\d+)?\s*(ms|msec|s|sec|secs|seconds?|mins?|minutes?)\b",
    r"(?i)states generated",
    r"(?i)\bseed\b",
    r"(?i)\bpid\b",
    r"(?i)\bfinished in\b",
    r"(?i)\belapsed\b",
))
EXIT_STATE = {0: "ok", 1: "failing"}
STATE_EXIT = {"ok": 0, "failing": 1}


def find_root():
    me = Path(__file__).resolve()
    if me.parent.name == "verify" and me.parent.parent.name == ".claude":
        return me.parents[2]
    here = Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / ".claude").is_dir():
            return p
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip()).resolve()
    except OSError:
        pass
    return here


def git_head(root):
    try:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    except OSError:
        return None


def load(root):
    checks = []
    trees = (
        ("hypothesis", root / ".claude" / "hypothesis"),
        ("codex-hypothesis", root / ".codex" / "hypothesis"),
        ("replays", root / ".claude" / "prove-it" / "replays"),
        ("codex-replays", root / ".codex" / "prove-it" / "replays"),
    )
    for kind, base in trees:
        for path in sorted(base.glob("*/check.toml")):
            folder = path.parent
            try:
                data = tomllib.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
                checks.append(SimpleNamespace(kind=kind, cid="*", folder=folder, spec={}, error=f"check.toml unreadable: {e}"))
                continue
            specs = data.get("check", [])
            if not isinstance(specs, list):
                checks.append(SimpleNamespace(kind=kind, cid="*", folder=folder, spec={}, error="check.toml must use [[check]] tables"))
                continue
            seen = set()
            for spec in specs:
                cid = spec.get("id")
                if isinstance(spec.get("covers"), str):
                    spec["covers"] = [spec["covers"]]
                lacking = [k for k in ("id", "promise", "covers", "cmd") if not spec.get(k)]
                error = None
                if lacking:
                    error = "check.toml lacks " + ", ".join(lacking)
                elif cid in seen:
                    error = "duplicate id in check.toml"
                elif spec.get("tier", "quick") not in ("quick", "full"):
                    error = "tier must be quick or full"
                seen.add(cid)
                checks.append(SimpleNamespace(kind=kind, cid=cid, folder=folder, spec=spec, error=error))
    kinds = {}
    for c in checks:
        kinds.setdefault(c.folder.name, set()).add(c.kind)
    for c in checks:
        prefix = f"{c.kind}:" if len(kinds[c.folder.name]) > 1 else ""
        c.id = f"{prefix}{c.folder.name}/{c.cid}"
    return checks


def skipped(rel):
    return any(p in SKIP_DIRS for p in rel.parts[:-1]) or any(fnmatch.fnmatch(rel.name, g) for g in SKIP_NAMES)


def expand(pattern):
    return pattern + "/*" if pattern == "**" or pattern.endswith("/**") else pattern


def covered(root, c):
    names = set()
    for pattern in c.spec["covers"]:
        for p in root.glob(expand(pattern)):
            if p.is_file():
                names.add(p.resolve().relative_to(root).as_posix())
    return names


def content_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def code_files(root, c, names):
    own = rel(root, c.folder) + "/"
    return {n: content_hash(root / n) for n in sorted(names) if not n.startswith(own)}


def read_records(c):
    try:
        data = json.loads((c.folder / RECORD).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def read_record(c, key):
    entry = read_records(c).get(c.cid)
    return entry.get(key) if isinstance(entry, dict) else None


def write_record(root, c, key, value):
    data = read_records(c)
    data.setdefault(c.cid, {})[key] = value
    (c.folder / RECORD).write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return rel(root, c.folder / RECORD)


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def since_synced(root, c, names):
    record = read_record(c, "synced")
    if record is None:
        return None
    old, now = record.get("files", {}), code_files(root, c, names)
    notes = []
    for n in sorted(set(old) | set(now)):
        if old.get(n) != now.get(n):
            kind = "added" if n not in old else "removed" if n not in now else "changed"
            notes.append(f"{kind} since synced {record.get('when', '?')}: {n}")
    return notes


def fingerprint(root, c, names):
    names = set(names)
    for p in c.folder.rglob("*"):
        if p.is_file() and not skipped(p.relative_to(c.folder)):
            names.add(p.resolve().relative_to(root).as_posix())
    files = {n: content_hash(root / n) for n in sorted(names)}
    digest = hashlib.sha256("".join(f"{n}\0{h}\n" for n, h in files.items()).encode()).hexdigest()
    return digest, files


def inspect(root, c):
    if c.error:
        return c.error, None, None, None
    try:
        names = covered(root, c)
        if not names:
            return "covers match no file", None, None, None
        drift = since_synced(root, c, names)
        digest, files = fingerprint(root, c, names)
    except (OSError, ValueError, NotImplementedError) as e:
        return f"covers cannot be read: {e}", None, None, None
    return None, drift, digest, files


def results_dir(root):
    return root / ".claude" / "verify" / "results"


def stamp_path(root, c, ext):
    return results_dir(root) / f"{c.kind}__{c.folder.name}__{c.cid}.{ext}"


def read_stamp(root, c):
    try:
        return json.loads(stamp_path(root, c, "json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_stamp(root, c, code, secs, out, digest, files):
    d = results_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    if not (d / ".gitignore").exists():
        (d / ".gitignore").write_text("*\n", encoding="utf-8", newline="\n")
    stamp = {
        "id": c.id,
        "exit": code,
        "seconds": round(secs, 1),
        "when": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "head": git_head(root),
        "fingerprint": digest,
        "files": files,
    }
    stamp_path(root, c, "json").write_text(json.dumps(stamp, indent=1), encoding="utf-8", newline="\n")
    stamp_path(root, c, "log").write_text(out, encoding="utf-8", newline="\n")


def rel(root, p):
    return p.relative_to(root).as_posix()


def state_of(root, c):
    problem, drift, digest, files = inspect(root, c)
    if problem:
        return "broken-judge", None, [problem]
    stamp = read_stamp(root, c)
    if read_record(c, "admitted") is None:
        return "draft", stamp, [f"not admitted: `run.py sync {c.id}` once the judge describes this code, then `run.py admit {c.id}`"]
    if drift is None:
        return "never-synced", stamp, [f"run `run.py sync {c.id}` once the judge describes this code"]
    if drift:
        return "stale", stamp, drift
    if stamp is None:
        return "never-run", None, []
    if stamp.get("fingerprint") != digest:
        old = stamp.get("files", {})
        own = rel(root, c.folder) + "/"
        notes = []
        for n in sorted(set(old) | set(files)):
            if old.get(n) != files.get(n):
                kind = "added" if n not in old else "removed" if n not in files else "changed"
                notes.append(("judge " if n.startswith(own) else "") + f"{kind}: {n}")
        return "stale", stamp, notes
    state = EXIT_STATE.get(stamp.get("exit"), "broken-judge")
    notes = [] if state == "ok" else [f"log: {rel(root, stamp_path(root, c, 'log'))}"]
    return state, stamp, notes


def kill_tree(proc):
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def execute(root, c):
    cwd = (c.folder / c.spec.get("cwd", ".")).resolve()
    missing = [t for t in c.spec.get("needs", []) if t not in PYTHONS and not shutil.which(t)]
    if missing:
        return 2, 0.0, f"missing on PATH: {', '.join(missing)}\n"
    cmd = [str(x) for x in c.spec["cmd"]]
    if cmd[0] in PYTHONS:
        cmd[0] = sys.executable
    elif "/" in cmd[0] or "\\" in cmd[0]:
        if (cwd / cmd[0]).exists():
            cmd[0] = str(cwd / cmd[0])
    else:
        cmd[0] = shutil.which(cmd[0]) or cmd[0]
    tier = c.spec.get("tier", "quick")
    timeout = c.spec.get("timeout", QUICK_LIMIT if tier == "quick" else FULL_TIMEOUT)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    group = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    start = time.monotonic()
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **group)
    except OSError as e:
        return 2, 0.0, f"cannot start {cmd[0]} in {cwd}: {e}\n"
    try:
        raw, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_tree(proc)
        try:
            raw, _ = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            raw = b""
        out = (raw or b"").decode("utf-8", "replace")
        return 2, time.monotonic() - start, out + f"\ntimed out after {timeout}s; process tree killed\n"
    out = (raw or b"").decode("utf-8", "replace")
    code = proc.returncode
    return (code if code in (0, 1) else 2), time.monotonic() - start, out


def line(state, c, secs, notes=()):
    shown = "-" if secs is None else f"{secs:.1f}s"
    promise = str(c.spec.get("promise", "")).strip().splitlines()
    print(f"{state} {c.id} {shown} {promise[0] if promise else ''}".rstrip())
    for n in notes:
        print(f"  {n}")


def tail(out):
    return [f"| {x}" for x in out.rstrip().splitlines()[-TAIL:]]


def summary(states, ungated=()):
    counts = {}
    for s in states + list(ungated):
        counts[s] = counts.get(s, 0) + 1
    codes = [STATE_EXIT.get(s, 2) for s in states] + [1 for s in ungated if s == "failing"]
    code = 1 if 1 in codes else 2 if 2 in codes else 0
    parts = ", ".join(f"{v} {k}" for k, v in counts.items()) or "no checks"
    quiet = [s for s in ungated if s != "failing"]
    aside = f" ({len(quiet)} draft or full, not counted)" if quiet else ""
    print(f"{len(states) + len(ungated)} checks: {parts} -> exit {code}{aside}")
    return code


def full_tier(c):
    return c.spec.get("tier", "quick") == "full"


def gating(c, state):
    return state == "failing" or (state != "draft" and not full_tier(c))


def select(checks, ids, tier):
    if ids:
        names = lambda c: (c.id, c.folder.name, f"{c.kind}:{c.folder.name}")
        chosen = [c for c in checks if any(n in ids for n in names(c))]
        unknown = [i for i in ids if not any(i in names(c) for c in checks)]
        return chosen, unknown
    return [c for c in checks if c.error or tier == "full" or c.spec.get("tier", "quick") == tier], []


def cmd_status(root, checks, ids):
    chosen, unknown = select(checks, ids, "full")
    states, ungated = [], []
    for c in chosen:
        state, stamp, notes = state_of(root, c)
        if full_tier(c) and state not in ("failing", "draft"):
            notes = ["full tier: not counted in the exit"] + notes
        line(state, c, stamp.get("seconds") if stamp else None, notes)
        (states if gating(c, state) else ungated).append(state)
    for i in unknown:
        print(f"unknown {i}")
        states.append("unknown")
    return summary(states, ungated)


def cmd_run(root, checks, ids, tier):
    chosen, unknown = select(checks, ids, tier)
    states, ungated = [], []
    for c in chosen:
        if not ids and not c.error and read_record(c, "admitted") is None:
            line("draft", c, None, [f"not admitted; run it by name: `run.py {tier} {c.id}`"])
            ungated.append("draft")
            continue
        problem, drift, digest, files = inspect(root, c)
        if problem:
            line("broken-judge", c, None, [problem])
            states.append("broken-judge")
            continue
        code, secs, out = execute(root, c)
        write_stamp(root, c, code, secs, out, digest, files)
        state = EXIT_STATE.get(code, "broken-judge")
        notes = [] if code == 0 else tail(out) + [f"log: {rel(root, stamp_path(root, c, 'log'))}"]
        if state == "ok" and drift is None:
            state, notes = "never-synced", [f"run `run.py sync {c.id}` once the judge describes this code"]
        elif state == "ok" and drift:
            state, notes = "stale", drift
        line(state, c, secs, notes)
        states.append(state)
    for i in unknown:
        print(f"unknown {i}")
        states.append("unknown")
    return summary(states, ungated)


def normalize(out):
    return [x.rstrip() for x in out.splitlines() if x.strip() and not any(r.search(x) for r in NOISE)]


def cmd_admit(root, checks, ident):
    found = [c for c in checks if c.id == ident]
    if len(found) != 1:
        print(f"unknown {ident}")
        return 2
    c = found[0]
    if c.error:
        print(f"refused {c.id}: {c.error}")
        return 2
    adm = c.spec.get("admission", {})
    lacking = [k for k in ("promise", "source", "covers", "cmd") if not c.spec.get(k)]
    lacking += [f"admission.{k}" for k in ("fault", "red") if not adm.get(k)]
    if lacking:
        print(f"refused {c.id}: a promise, a judge that went red on a planted fault, and a fingerprint, or nothing; lacks {', '.join(lacking)}")
        return 2
    problem, drift, digest, files = inspect(root, c)
    if problem:
        print(f"refused {c.id}: {problem}")
        return 2
    if drift is None:
        print(f"refused {c.id}: never synced; run `run.py sync {c.id}` once the judge describes this code")
        return 2
    if drift:
        print("\n".join(f"  {n}" for n in drift))
        print(f"refused {c.id}: the covered files changed since synced; bring the judge in step, then `run.py sync {c.id}`")
        return 2
    runs = max(1, int(adm.get("runs", DEFAULT_RUNS)))
    if c.kind in REPLAY_KINDS and runs < REPLAY_MIN_RUNS:
        print(f"refused {c.id}: a replay is admitted on at least {REPLAY_MIN_RUNS} identical runs; runs = {runs}")
        return 2
    seen, times = [], []
    for i in range(runs):
        code, secs, out = execute(root, c)
        times.append(secs)
        print(f"run {i + 1}/{runs} exit {code} {secs:.1f}s")
        if code != 0:
            write_stamp(root, c, code, secs, out, digest, files)
            print("\n".join(tail(out)))
            print(f"refused {c.id}: run {i + 1} exited {code}")
            return code
        seen.append(normalize(out))
        if seen[-1] != seen[0]:
            diff = list(difflib.unified_diff(seen[0], seen[-1], "run 1", f"run {i + 1}", lineterm="", n=0))
            print("\n".join(diff[:20]))
            print(f"refused {c.id}: output differs between runs; make the judge deterministic or add its noise to NOISE")
            return 2
    worst = math.ceil(max(times))
    if c.spec.get("tier", "quick") == "quick":
        if worst > QUICK_LIMIT:
            print(f"refused {c.id}: {worst}s is over the {QUICK_LIMIT}s a quick check may take; cut a smaller scope, do not loosen the limit")
            return 2
        others = sum(int((read_record(o, "admitted") or {}).get("seconds", 0)) for o in checks
                     if o is not c and not o.error and o.spec.get("tier", "quick") == "quick")
        if others + worst > QUICK_TIER_LIMIT:
            print(f"refused {c.id}: the quick tier would take {others + worst}s, over {QUICK_TIER_LIMIT}s; cut a smaller scope or move a check to full")
            return 2
    write_stamp(root, c, 0, times[-1], out, digest, files)
    where = write_record(root, c, "admitted", {"when": now_iso(), "head": git_head(root), "runs": runs, "identical": True, "seconds": worst})
    print(f"admitted {c.id}: {runs} runs, identical output, {worst}s at worst; recorded in {where}")
    return 0


def cmd_sync(root, checks, ids):
    if not ids:
        print("sync names the checks it brings in step: run.py sync <id>…")
        return 2
    chosen, unknown = select(checks, ids, "full")
    code = 2 if unknown else 0
    for i in unknown:
        print(f"unknown {i}")
    for c in chosen:
        if c.error:
            print(f"refused {c.id}: {c.error}")
            code = 2
            continue
        names = covered(root, c)
        if not names:
            print(f"refused {c.id}: covers match no file")
            code = 2
            continue
        files = code_files(root, c, names)
        where = write_record(root, c, "synced", {"when": now_iso(), "head": git_head(root), "files": files})
        print(f"synced {c.id}: {len(files)} covered files recorded in {where}")
    return code


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="run.py", description="Rerun the project's admitted verifications and report 0 ok, 1 code broken, 2 judge stale or missing.")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("status", "quick", "full", "sync"):
        sub.add_parser(name).add_argument("ids", nargs="*")
    sub.add_parser("admit").add_argument("id")
    a = ap.parse_args()
    root = find_root()
    checks = load(root)
    if a.command == "status":
        return cmd_status(root, checks, a.ids)
    if a.command == "sync":
        return cmd_sync(root, checks, a.ids)
    if a.command == "admit":
        return cmd_admit(root, checks, a.id)
    return cmd_run(root, checks, a.ids, a.command)


if __name__ == "__main__":
    sys.exit(main())
