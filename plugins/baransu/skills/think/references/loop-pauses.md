# loop-pauses — /think PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/think is graded loop=not-drivable — its focusing dialogue is the product; no
recommended default can substitute it. The rows below exist for the cases
loop-contract's Scope still covers (hosted as a subagent, /loop, cron,
Workflow): they tell a non-interactive run how to stop loudly instead of
auto-advancing through the dialogue or the approval gate.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage A alignment rounds (目的 / 約束 / 成功, AskUserQuestion ×3) | Input | No default can substitute the focusing dialogue (the not-drivable rationale): report `no progress: focusing dialogue requires a human` and end the run — never fabricate the user's answers |
| Evaluation mode constraint elicitation (exactly ONE AskUserQuestion round) | Input | Do not ask; apply the skill's own decline path — state that the constraints are unavailable and ground the three reasons in what is observable from the repo |
| Stage G approval (four-option gate) | **Authorization** | Hard stop — never take a default, never treat 【推薦】 as approval; report `needs input` to the driver (LOOP_OUTCOME: blocked). Standing-authorizable only via an approved plan in the driving context that explicitly authorizes this approval, per loop-contract §2 |
| Option 3 re-alignment ask (還有地方要對焦) | Input | Unreachable without a human at Stage G; if reached, report `no progress: re-alignment requires a human` and end the run |
