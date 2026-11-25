import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PLUGIN = ROOT / "codex" / "plugins" / "baransu"
BUNDLE = PLUGIN / "hooks" / "lint.mjs"
HOOKS = PLUGIN / "hooks" / "hooks.json"
FIXTURE = ROOT / ".claude" / "prove-it" / "fixtures" / "codex-lint" / "checks.toml"
COMMAND = 'node "${PLUGIN_ROOT}/hooks/lint.mjs"'
FIELDS = {"hook_event_name", "session_id", "turn_id", "transcript_path", "cwd", "source", "prompt", "agent_id",
          "agent_type", "tool_name", "tool_input", "tool_use_id", "tool_response", "last_assistant_message"}
CODE = re.compile(r"\b[A-Z]{2,3}-\d+\b")
MARK = re.compile(r"^([✖⚠⏸ℹ] [\w.-]+)：", re.M)
SHELL = re.compile(r"^(\w+)\|(?:ps|sh)\|")
FILES = {"A.java": "class A {}\n", "notes.txt": "notes\n", "PLAN.md": "# Plan\n", "keep/x.txt": "x\n", "tmp.txt": "tmp\n"}


class Stale(Exception):
    pass


def registered(hooks, event, tool):
    for group in hooks.get("hooks", {}).get(event, []):
        matcher = group.get("matcher")
        if matcher and not (tool and re.search(matcher, tool)):
            continue
        for h in group.get("hooks", []):
            if h.get("command") == COMMAND:
                return True
            if "lint.mjs" in h.get("command", ""):
                raise Stale(f"hooks.json runs lint.mjs for {event} as {h.get('command')!r}, the replay expects {COMMAND!r}")
    return False


def fill(v, names):
    if isinstance(v, str):
        for k, s in names.items():
            v = v.replace("{" + k + "}", s)
        return v
    if isinstance(v, dict):
        return {k: fill(x, names) for k, x in v.items()}
    if isinstance(v, list):
        return [fill(x, names) for x in v]
    return v


def read_back(out):
    if not isinstance(out, dict):
        raise Stale(f"hook answered {out!r}, not one JSON object")
    spec = out.get("hookSpecificOutput") or {}
    text = " ".join(str(x) for x in (out.get("reason"), spec.get("permissionDecisionReason"), spec.get("additionalContext")) if x)
    decision = out.get("decision") or spec.get("permissionDecision") or ("context" if spec.get("additionalContext") else "none")
    return {"decision": decision, "codes": sorted(set(CODE.findall(text))), "marks": sorted(set(MARK.findall(text)))}


def state_of(data, session, proj):
    lint = data / "lint"
    saved = json.loads((lint / f"{session}.json").read_text("utf-8"))
    p = proj.as_posix()
    held = sorted(SHELL.sub(r"\1|<shell>|", h["key"].replace(p, "<P>").replace(p.lower(), "<P>")) for h in saved.get("lint", {}).get("held", []))
    return {"pending": len(saved.get("pending", {})), "held": held, "steps": saved.get("lint", {}).get("steps", {}),
            "locks": len(list(lint.glob("*.lock")))}


def journey(spec, hooks, node, git):
    tmp = Path(tempfile.mkdtemp(prefix="codex-lint-replay-"))
    try:
        proj, data, home = tmp / "proj", tmp / "data", tmp / "codex-home"
        for name, text in FILES.items():
            (proj / name).parent.mkdir(parents=True, exist_ok=True)
            (proj / name).write_text(text, "utf-8")
        sets = proj / ".claude" / "lint" / "sets" / "local"
        sets.mkdir(parents=True)
        shutil.copyfile(FIXTURE, sets / "checks.toml")
        (proj / ".claude" / "lint" / "config.toml").write_text('[[extends]]\nset = "sets/local/checks.toml"\n', "utf-8")
        subprocess.run([git, "init", "-q"], cwd=proj, check=True)
        home.mkdir()
        trust = f"[projects.'{proj.as_posix()}']\ntrust_level = \"trusted\"\n" if spec.get("trusted") else ""
        (home / "config.toml").write_text(trust, "utf-8")
        transcript = tmp / "rollout.jsonl"
        transcript.write_text("", "utf-8")
        session = spec["session"]
        names = {"cwd": str(proj), "transcript": str(transcript), "session": session}
        env = {**{k: v for k, v in os.environ.items() if k != "BARANSU_LINT_DEBUG"},
               "PLUGIN_ROOT": str(PLUGIN), "PLUGIN_DATA": str(data), "CODEX_HOME": str(home)}
        reds = []
        for n, step in enumerate(spec["steps"], 1):
            if "rollout" in step:
                with transcript.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(step["rollout"]) + "\n")
                continue
            if "write" in step:
                (proj / step["write"]).write_text(step["text"], "utf-8")
                continue
            payload = fill(step["hook"], names)
            extra = set(payload) - FIELDS
            if extra:
                raise Stale(f"{spec['id']} step {n}: payload field the adapter does not read: {sorted(extra)}")
            event = payload.get("hook_event_name")
            if not registered(hooks, event, payload.get("tool_name")):
                got = {"decision": "not-run", "codes": []}
            else:
                r = subprocess.run([node, str(BUNDLE)], input=json.dumps(payload).encode("utf-8"), capture_output=True,
                                   cwd=proj, env=env, timeout=120)
                if r.returncode != 0:
                    raise Stale(f"{spec['id']} step {n}: hook exited {r.returncode}: {r.stderr.decode('utf-8', 'replace')[:300]}")
                try:
                    got = read_back(json.loads(r.stdout.decode("utf-8")))
                except json.JSONDecodeError:
                    raise Stale(f"{spec['id']} step {n}: hook printed no JSON: {r.stdout[:200]!r}")
            want = step["expect"]
            if got != want:
                reds.append(f"red {spec['id']} step {n} {event}: expected {json.dumps(want, ensure_ascii=False)}, got {json.dumps(got, ensure_ascii=False)}")
        if "state" in spec:
            got = state_of(data, session, proj)
            if got != spec["state"]:
                reds.append(f"red {spec['id']} state: expected {json.dumps(spec['state'])}, got {json.dumps(got)}")
        return reds
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    node, git = shutil.which("node"), shutil.which("git")
    if not node or not git:
        print(f"stale: missing {'node' if not node else 'git'} on PATH")
        return 2
    for f in (BUNDLE, HOOKS, FIXTURE):
        if not f.is_file():
            print(f"stale: missing {f.relative_to(ROOT).as_posix()}")
            return 2
    try:
        hooks = json.loads(HOOKS.read_text("utf-8"))
        specs = [json.loads(p.read_text("utf-8")) for p in sorted((HERE / "journeys").glob("*.json"))]
    except json.JSONDecodeError as e:
        print(f"stale: malformed JSON: {e}")
        return 2
    only = set(sys.argv[1:])
    failed = False
    for spec in specs:
        if only and spec["id"] not in only:
            continue
        try:
            reds = journey(spec, hooks, node, git)
        except (Stale, KeyError, subprocess.SubprocessError) as e:
            print(f"stale {spec.get('id')}: {e}")
            return 2
        for line in reds:
            print(line)
        failed = failed or bool(reds)
        if not reds:
            print(f"ok {spec['id']}: {spec['promise']}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"judge crashed: {type(e).__name__}: {e}")
        sys.exit(2)
