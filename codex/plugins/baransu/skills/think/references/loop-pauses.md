# loop-pauses — $baransu:think PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

$baransu:think is graded loop=not-drivable — the restatement dialogue is the product; no recommended default can substitute it. The rows below tell a non-interactive run how to stop loudly instead of auto-advancing.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Restatement questions (one at a time, each fixing a guessed phrase) | Input | No default can substitute the dialogue: report `no progress: restatement requires a human` and end the run |
| Restatement confirmation | Input | Report `no progress: restatement confirmation requires a human` and end the run |
| A choice that is genuinely the user's (value, budget, authority boundary) before the stance | Authorization | Never assume; report `no progress: user-owned choice pending` and end the run |
| Which-section-is-wrong question after pushback | Input | Report `no progress: pushback needs the user to name the section` and end the run |
