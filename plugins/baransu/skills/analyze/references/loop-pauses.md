# loop-pauses — /analyze PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 0.C directory-collision AskUserQuestion (resume / 覆寫重建 / -N 後綴) | Input | Take the recommended default (option 1, resume 既有 spec), annotate 「此處採預設：resume 既有 spec」. Never take 覆寫重建 without a human — a deletion is not a default |
| Stage 1 goal.md confirmation AskUserQuestion | Input | Take the recommended default (確認，繼續), annotate 「此處採預設」. The goal seed must come from the driving context; if none was supplied, report `no progress: no goal sentence` and end the run |
| Stage 6 structural-finding pause (structural findings still open after auto-correct + re-verify) | Input | Do not adjudicate on your own (per the Stage 6 loop-mode default sentence): record the structural findings, report them back to the driver, end with LOOP_OUTCOME: blocked |
| Stage 7 handoff AskUserQuestion (下一步) | Input — except option 2, an **Authorization** path | Take option 3 semantics: list the spec dir path, annotate 「此處採預設：手動決定」, end with LOOP_OUTCOME: ok. Never take option 1 — with no user, /review returns control to this same gate, a non-terminating cycle. Never take option 2 — 完全授權 inline execution is satisfiable only by a standing authorization recorded in the driving context, per loop-contract §2 |
