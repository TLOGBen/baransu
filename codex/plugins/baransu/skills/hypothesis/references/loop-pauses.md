# loop-pauses — $baransu:hypothesis under a non-interactive driver

Registered in `../../_shared/loop-contract.md` §4 (Gate 10 in `scripts/verify-skills.py`). Enumerated from this skill's `SKILL.md`; re-verify when it changes.

## Pauses

Exactly two, both Input PAUSEs in the loop contract's classes, and neither has a default:

| Where | PAUSE | Without the person |
|---|---|---|
| §3 Confirm the rules, on a first write | Input — the rules a hypothesis will hold the source to are the user's to agree | Nothing is published; the caller reports 「需要人確認規則」 and the run ends `LOOP_OUTCOME: no progress: rules need confirmation`. |
| `--maintain`, a change that may have changed a promise but the "why" reading found no evidence | Input — only the person can say a promise changed on purpose | The area stays unpublished, so readers keep seeing `stale`; the report lists the questions; the run ends `LOOP_OUTCOME: no progress: promise evidence required`. |

## Never a pause

The `no-effect`, `model-update` and `bug-candidate` outcomes, reruns, publishing, and opening the page all run unattended. A failing check is a finding, not a pause.
