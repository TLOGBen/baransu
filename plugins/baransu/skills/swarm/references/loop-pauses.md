# loop-pauses — /swarm PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/swarm is graded loop=assisted: a driver may run it, and its stops take the defaults below. A swarm ends before anything ships and bees never commit unless the user asked, so the queen decides and records nearly everything; the user reviews the records before shipping.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| A question for the queen — approach, design, taste, or a step inside the run | Input | The queen decides it, records what she chose, why and the alternative in the decision log, and answers and resumes the bee through the board program |
| What the user meant — their words read two ways that would change different files | Input | Stop-and-report default: no default can exist, since only the user knows what they meant; never pick a reading. The task stays `blocked` with the question on the board (`ask user`), every other task keeps going, and the run reports `needs input` with the question and both readings |
| A step that cannot be undone or reaches outside the run — deleting data the run did not make, an account, a deploy, a message to anyone | Authorization | Never take it; the task stays `blocked` with the step on the board, every other task keeps going, and the run reports `needs input` with the step |
| A host permission prompt holding a step the queen approved | Input | Not a decision: the queen approves the step; the run reports where the prompt is waiting and, when it repeats, the exact allow rule, without editing the user's settings |
