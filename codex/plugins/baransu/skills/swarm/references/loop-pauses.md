# loop-pauses — $baransu:swarm PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

$baransu:swarm is graded loop=assisted: a driver may run it, and its stops take the defaults below. Bees never commit unless the user asked, so their changes stay reviewable.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| A question for the queen | Input | Answer it from the board, the interfaces written down, and the repo; resume the bee; record the answer in its task line |
| A question for the user — a value, a budget, an authorization | Authorization | Never assume; the task stays `blocked` with the question on the board, every other task keeps going, and the run reports `needs input` with the question |
| A destructive, irreversible or permission-held step a bee reported | Authorization | Never work around it; the run reports `needs input` with the exact step |
