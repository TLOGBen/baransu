# loop-pauses — /contract PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 3 presentation of the contract (no ceremonial reconfirmation) | Input | Write the contract as grounded, annotate 「此處採預設：合約未經人工確認即釘死」 in the 決策與修正 section |
| Step 3 unresolved decision that is the user's (changed outcome, authority boundary, user-owned tradeoff) | Authorization | Never assume; leave the dependent criterion marked 待證 and report `no progress: user-owned decision pending` |
| Step 3 existing unsealed contract belonging to a different task | Authorization | Do not overwrite; report `no progress: different task at target path, name a new path` and end the run |
| Task exceeds one contract band (several interdependent modules) | Input | Do not write an oversized contract; report `no progress: slice into contract-band slices` and end the run |
