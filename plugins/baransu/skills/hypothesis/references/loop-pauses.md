# loop-pauses — /hypothesis under a non-interactive driver

Registered in `../_shared/loop-contract.md` §4 (Gate 10 in `scripts/verify-skills.py`).

## Pauses

(unimplemented) — Exactly two, in the loop-contract's classes:
- **Input PAUSE — promise evidence.** `--maintain` sorted a change as possibly `promise-changed` but found no evidence (doc comment, test, changelog, commit message, document revision). Default: none — it may not be resolved as `no-effect` or `promise-changed` without the person; the area stays unpublished (readers keep seeing `stale`), the report lists the questions, and the run ends `LOOP_OUTCOME: no progress: promise evidence required`.
- **Input PAUSE — rule confirmation.** A first write (§3) reached rule confirmation. Default: none; nothing is published; the caller reports 「需要人確認規則」.

## Never a pause

(unimplemented) — `no-effect`, `model-update` and `bug-candidate` outcomes, reruns, publishing, opening the page: all run unattended. A failing check is a finding, not a pause.
