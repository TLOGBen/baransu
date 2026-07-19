# loop-pauses — /contract PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 3 contract confirmation (one round) | Input | Take the default (contract as written), annotate 「此處採預設：合約未經人工確認即釘死」 in the contract header comment; every criterion still passes the G1 gate before writing |
| Step 2 over-length off-ramp (contract would exceed 60 lines → route to /analyze) | Input | Do not write a long contract; report `no progress: task exceeds contract band, route to /analyze` and end the run |
