# safety-gates — the red lines evolve never crosses

evolve mutates SKILL.md files on disk and spawns subagents that *run* the skill under test. Both are dangerous by default. These gates are non-negotiable; cite this file from every stage that writes, rolls back, or executes.

## Gate 1 — Adoption is an Authorization PAUSE (never an Input PAUSE)

Writing a kept mutation back into the target SKILL.md is an **Authorization PAUSE** as defined in `_shared/loop-contract.md §2`: it is never satisfied by a default substitution. This is the load-bearing safety property of the whole skill. The required authorization is given one of two ways — interactively, or as a standing authorization recorded in the driving context.

- **Interactive use**: present the diff + score delta, wait for explicit user adoption. No standing authorization, no auto-write.
- **Non-interactive drive WITHOUT a standing authorization** (e.g. bare `/ultracode`, a loop/cron prompt that does not mention adoption): an Input PAUSE would legally degrade to "take the recommended default" — that path is forbidden here. Adoption MUST halt and report `needs input`. evolve never writes a mutation to disk on a default.
- **Non-interactive drive WITH a standing authorization** (the loop/cron prompt or approved plan explicitly authorizes adoption / the evolve→ship sweep): auto-adopt is permitted, but ONLY for changes that clear **every** precondition below. A change failing any precondition is restored (Gate 2), never written. This is explicit up-front human authorization, not a default substitution.
  1. **Structure gate passes** (Gate 4) — exit 0, no `⚠️ ADVISORY`.
  2. **Blind-judge bar tightened to 3/3** strict_improvement (not the interactive 2/3) — automation has no human backstop, so the panel must be unanimous.
  3. **File-level snapshot retained** (Gate 2) for one-command rollback.
  4. **Audit**: every auto-adopted change is logged to `log.md` with `decision: standing-auth auto-adopt`, the votes, and the snapshot path.
  5. **End-state verification is the final arbiter**: after the run's adoptions, the driver's end-state check (`make test` / structure gate) decides go/no-go for downstream steps (e.g. /ship). A red end-state must block the ship and surface the failing files, not proceed.

Diagnosis, mutation-into-a-scratch-copy, scoring, and rollback are *not* Authorization PAUSEs — only the write-back of an adopted change is.

## Gate 2 — Rollback is file-level, never git-level

The snapshot/restore mechanism touches exactly one file: the target SKILL.md.

- **Snapshot**: before mutating, copy the target file's bytes to `.claude/evolve/<slug>/snapshot/<round>.md`.
- **Restore**: write the snapshot bytes back to the target path.
- **Forbidden**: `git reset --hard`, `git stash`, `git clean`, `git checkout -- <path>`, or any git command that can touch the working tree beyond the single target file. The user is, by definition, mid-edit on a skill; the working tree is dirty as a matter of course. A repo-wide git rollback would eat their other uncommitted work (`rules/anti-patterns.md` Worktree Safety).
- **Restore failure** is an irreversible-risk event: abort the run, preserve state, report. Never continue in an uncertain state.

## Gate 3 — real-exec is a trust + capability dual gate

The effectiveness axis prefers running the skill under test, but only through both gates, in order:

1. **Capability gate** — is the skill non-interactive and runnable unattended? Skills with `AskUserQuestion` / approval gates (think, review, analyze, …) fail this gate and are forced offline. This is a capability fact, not a flaw.
2. **Trust gate** — only if the capability gate passes: is the target a skill the user themselves specified, living under the user's own plugin path, AND does its body contain none of the destructive patterns below? Unknown-origin / third-party / pattern-hit skills are forced offline.

Destructive-pattern denylist (any hit → forced offline, reason disclosed in the report):
`rm `, `git push`, `git reset`, `git clean`, `> ` (truncating redirect), `curl`/`wget`/network fetch, `sudo`, credential/secret tokens.

When real-exec does run, mark that run **untrusted** in the report and advise post-run memory rotation, per `skills/health/SKILL.md` §third-party/subagent supply-chain stance. The capability gate asks "can it run?"; the trust gate asks "should it?" — never collapse the two.

## Gate 4 — Structure gate before keep

No mutation is adopted unless it passes the structure gate, regardless of score:

- Run `python3 scripts/verify-skills.py <skill_dir>` (or repo-mode for whole-repo invariants).
- **Pass** = exit code 0 **AND** stdout contains no `⚠️ ADVISORY` line. Body-line advisory over-limit returns exit 0 but emits `⚠️ ADVISORY`; evolve MUST read stdout for that line and treat it as a structure-gate failure (a score gain that bloats the body past advisory is not kept).
- A structure-gate failure forces restore (Gate 2), no matter how high the rubric score rose. Score never overrides structure — the gate is a sequential precondition to keep, not a parallel vote.
