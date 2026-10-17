# loop-pauses — $baransu:ship PAUSE classification

PAUSE vocabulary and semantics: `../../_shared/loop-contract.md` §2. This file enumerates only $baransu:ship's own interaction points.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 4 pushes (`git push origin {branch}` and each target push) | **Authorization** | Hard stop. Under loop drive, never auto-push unless a standing user authorization is recorded in the driving context (e.g. the loop prompt or approved plan explicitly authorizes push); absent that record, report `needs input` to the driver |
| Step 2b pull conflict (local unpushed commits collide with the remote) | **Input** | Stop-and-report default: abort the merge, restore the stash, report `needs input`; never commit or push |
| Contradicting-intent conflict (Step 2b item 4, or a Step 4 target merge) | **Input** | Stop-and-report default: never pick a side; Step 2b leaves the conflict and the stash entry in the working tree, a target merge is aborted; report `needs input` with the file, the hunk and what each side wants |
| Step 3 commit identity undecidable (empty history, or no single recent author fits the remote) | **Input** | Stop-and-report default: never fall back to the machine's git config; report `needs input` with the candidate identities and the remote; never commit |

$baransu:ship's push step is interaction-free in human-present sessions (Step 4 pushes
unconditionally), but pushing publishes state beyond the local repo — under a
non-interactive driver it carries Authorization-PAUSE weight.
