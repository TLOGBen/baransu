# loop-pauses — /hypothesis under a non-interactive driver

Registered in `../../_shared/loop-contract.md` §4 (Gate 10 in `scripts/verify-skills.py`). Enumerated from this skill's `SKILL.md`; re-verify when it changes.

## Pauses

Exactly three, all Input PAUSEs in the loop contract's classes, and none has a default:

| Where | PAUSE | Without the person |
|---|---|---|
| §3 Confirm the rules, on a first write | Input — the rules a hypothesis will hold the source to are the user's to agree | Nothing is published; the caller reports 「需要人確認規則」 and the run ends `LOOP_OUTCOME: no progress: rules need confirmation`. |
| §4 The never-happens list, on a first write | Input — the person who knows the source is the half of seen faithful an agent cannot replace | Nothing is published; the agent's refutation is kept, the caller reports 「需要人看不可能清單」 and the run ends `LOOP_OUTCOME: no progress: never-happens list needs the person`. |
| `--maintain`, a change that may have changed a promise but the "why" reading found no evidence | Input — only the person can say a promise changed on purpose | The area stays unpublished, so readers keep seeing `stale`; the report lists the questions; the run ends `LOOP_OUTCOME: no progress: promise evidence required`. |

## Never a pause

The `no-effect`, `model-update` and `bug-candidate` outcomes, reruns, the refutation of the never-happens list by a fresh agent (seen faithful), publishing, and showing the diagrams all run unattended; after the first write, the agent's refutation alone carries seen faithful. A failing check is a finding, not a pause.
