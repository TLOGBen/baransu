# loop-pauses — /ship PAUSE classification

PAUSE vocabulary and semantics: `../../_shared/loop-contract.md` §2. This file enumerates only /ship's own interaction points.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 4 push (`git push origin {branch}`) | **Authorization** | Hard stop. Under loop drive, never auto-push unless a standing user authorization is recorded in the driving context (e.g. the loop prompt or approved plan explicitly authorizes push); absent that record, report `needs input` to the driver |

/ship's push step is interaction-free in human-present sessions (Step 4 pushes
unconditionally), but pushing publishes state beyond the local repo — under a
non-interactive driver it carries Authorization-PAUSE weight.
