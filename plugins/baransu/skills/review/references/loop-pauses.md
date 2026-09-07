# loop-pauses — /review PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Target or question cannot be pinned | Input | Report `no progress: no target or question to review` and end the run |
| Independent execution unavailable or the session authored the target | Input | Proceed as a same-context self-check and state in the report that no independent pass was earned |
| Extending the review into repeated probes beyond the allowance | Authorization | Do not extend; report the finding as unverified with the observation that would decide it |
| Persisting the report to `.claude/review/<slug>.md` | Input | Persist when the driver named a slug or asked for a file; otherwise keep the conversation report only |
