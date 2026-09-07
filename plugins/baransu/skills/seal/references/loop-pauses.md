# loop-pauses — /seal PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Target pin branch 3 (nothing to pin) | Input | Report `no progress: no target or criteria to seal` and end the run |
| Repair of a finding when the original request did not include implementation | Authorization | Never repair; record the finding as a blocker in the receipt, seal-log `unresolved`, end the run |
| Allowance reached / repeated no-progress / fix would widen into a refactor | Authorization | Stop the cycle; write the receipt with the gap, seal-log `unresolved`, report the proposed next allowance, end the run |
| User-owned tradeoff or authority change surfaced by a premise correction | Authorization | Never assume; mark the dependent criterion unverified and report `no progress: user decision pending` |
| Mutation probe without an isolated disposable copy | Authorization | Never probe the live worktree; use non-mutating evidence and record the limitation |
