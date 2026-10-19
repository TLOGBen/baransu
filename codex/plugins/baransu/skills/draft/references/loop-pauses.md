# loop-pauses — $baransu:draft PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

$baransu:draft is graded loop=assisted: a driver may run it, and its stops take the defaults below. The sketch stays an uncommitted change, so a defaulted go is reversible.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 4 the user's go on the shape | Input | Take the chosen shape and continue to step 5; annotate 「此處採預設：採用 {base} 形狀，嫁接 {grafts}」 |
| `--deepen` the user's pick among candidates | Input | Pick the candidate rated 強烈建議 with the largest locality gain; when none is rated 強烈建議, report `no progress: no deepening candidate is strongly recommended` and end the run |
| A candidate that would reopen a recorded decision | Authorization | Never take it by default; report `needs input` with the decision record and the friction that argues for reopening it |
