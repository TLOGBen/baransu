# /ui A/B blind comparison kit

Compares two versions of `plugins/baransu/skills/ui/SKILL.md` by what they build, not by how they read.
Each brief is built once per version by a fresh subagent; a separate judge in a fresh context sees only
anonymised screenshots and picks a winner per brief. Manual harness: not part of `make test`.

## Files

| File | Role |
| --- | --- |
| `briefs.md` | Three client briefs, none with photographs of its own |
| `build-prompt.md` | The prompt each builder subagent gets (one per brief × version) |
| `juror-prompt.md` | The prompt the judge gets; it sees `blind/` only |
| `shuffle.py` | Copies screenshots into `blind/brief-N/{A,B}/` at random and writes `mapping.json` beside, never inside, `blind/` |
| `results-*.md` | One report per comparison round |

## Run

Run directory: `.claude/ab/<round>/` in the repo root (local only: gitignored, and `/ship` leaves it in place).

1. Put the two skill versions side by side under neutral names, so a builder cannot tell which is which:
   `git show <old-commit>:plugins/baransu/skills/ui/SKILL.md > .claude/ab/<round>/skills/p/SKILL.md` and
   copy the working tree's file to `.claude/ab/<round>/skills/q/SKILL.md`. Record which is which in
   `.claude/ab/<round>/arms.json` (`{"p": "old", "q": "new"}`).
2. For each brief N and each arm X, dispatch a fresh subagent with `build-prompt.md`, its placeholders
   filled; output goes to `.claude/ab/<round>/build/brief-N/X/`.
3. Re-take every build's screenshots yourself once all builds are done (a builder's own `shots/` may predate its last edit), with draw's seeded script (never a fresh browser — it locks the Windows account):
   `node plugins/baransu/skills/draw/scripts/motion/verify-page.mjs <page>.html --out .claude/ab/<round>/build/brief-N/X/shots-final`.
4. `python3 tests/ab/ui/shuffle.py .claude/ab/<round> --shots shots-final` → `blind/` plus `mapping.json`.
5. Dispatch one fresh judge with `juror-prompt.md` pointed at `blind/`; save its verdict as `verdict.md`.
6. Unmask with `mapping.json` and `arms.json`, and write `tests/ab/ui/results-<round>.md`: per brief the winner,
   the judge's reasons, and the overall count. Ship rule for phase 1: the new version wins at least 2 of 3.

Limits: one judge per brief, so a single verdict carries noise; judges are models, not people.
