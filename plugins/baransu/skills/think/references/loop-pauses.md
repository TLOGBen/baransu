# loop-pauses — /think PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/think is graded loop=not-drivable — its focusing dialogue is the product; no
recommended default can substitute it. The rows below exist for the cases
loop-contract's Scope still covers (hosted as a subagent, /loop, cron,
Workflow): they tell a non-interactive run how to stop loudly instead of
auto-advancing through the dialogue or the confirmation gate.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Alignment rounds (Route 3, Steps 1-3: 目的 / 約束 / 成功, AskUserQuestion ×3) | Input | No default can substitute the focusing dialogue (the not-drivable rationale): report `no progress: focusing dialogue requires a human` and end the run |
| Constraint elicitation (Route 1, Step 1: when user provides < 3 constraints) | Input | Do not ask; ground the verdict only in the constraints already visible in the conversation and repo — flag the thin evidence base in the verdict |
| Verdict / handoff confirmation (all routes, final AskUserQuestion) | Input | Report `no progress: verdict confirmation requires a human` and end the run |
