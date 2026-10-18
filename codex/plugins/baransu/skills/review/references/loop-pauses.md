# loop-pauses — $baransu:review PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Target, goal, or scope cannot be pinned | Input | Report `no progress: no target, goal, or scope to review` and end the run |
| Independent execution unavailable or the session authored the target | Input | Proceed as a same-context self-check and state in the report that no independent pass was earned |
| Widening the target or scope beyond what was pinned | Authorization | Do not widen; report the claim as unverified with the outcome at risk and the record that would decide it |
| Persisting the report to `.codex/review/<slug>.md` | Input | Persist when the driver named a slug or asked for a file; otherwise keep the conversation report only |
