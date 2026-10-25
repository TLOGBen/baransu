# loop-pauses — $baransu:prove-it PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

$baransu:prove-it is graded loop=assisted: a driver may run it on this machine. Starting the app, building the recipe, and driving it locally need no stop; anything that reaches outside this machine does.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| A step with an effect outside this machine — sending a message, deploying, charging, publishing, writing shared data | Authorization | Standing-authorizable only when the driving context names that effect and its target; otherwise do not run the step, record the claim as unreachable with the effect as its prerequisite, and report `needs input` |
| A test mode that would make such a step local | Input | Use it only when its skipping of the outside effect was seen in this run; otherwise treat the step as the row above |
| The repo does not build or start as it is | Input | Report `no progress: the base does not build or start` with the precise failure and end the run |
| A claim whose prerequisite is out of reach (auth, platform, external state) | Input | Record it unreachable with the prerequisite and the route tried, and continue with the other claims |
| Recipe gap — the app works but the drive cannot reach it | Input | Fix the recipe and drive again before any verdict, as the skill does when a person is present |
| An every-case claim no hypothesis covers, and no one is there to confirm the rules `$baransu:hypothesis` writes for it | Input | `$baransu:hypothesis` goes on with the rules as written and marks its report 未經確認 (`../../hypothesis/references/loop-pauses.md`); read the claim against it as usual, carry 未經確認 into this claim's verdict, and continue with the other claims |
