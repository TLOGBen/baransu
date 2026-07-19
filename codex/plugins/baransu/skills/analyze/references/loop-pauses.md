# loop-pauses — /analyze PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.
Covers both halves of the skill: the spec stages (0–7) and the execution pipeline (`execution-pipeline.md`, which has no AskUserQuestion — its user-touch points are escalation notices and by design it never stops early except pipeline Step 0).

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 0.C directory-collision AskUserQuestion (resume / 覆寫重建 / -N 後綴) | Input | Take the recommended default (option 1, resume 既有 spec), annotate 「此處採預設：resume 既有 spec」. Never take 覆寫重建 without a human — a deletion is not a default |
| Stage 1 goal.md confirmation AskUserQuestion | Input | Take the recommended default (確認，繼續), annotate 「此處採預設」. The goal seed must come from the driving context; if none was supplied, report `no progress: no goal sentence` and end the run |
| Stage 6 self-review structural pause (structural findings still open after the single correction round) | Input | Do not adjudicate on your own (per the Stage 6 loop-mode default sentence): record the structural findings, report them back to the driver, end with LOOP_OUTCOME: blocked |
| Stage 7 handoff AskUserQuestion (下一步) | Input — except option 2, an **Authorization** path | Take option 3 semantics: list the spec dir path, annotate 「此處採預設：手動決定」, end with LOOP_OUTCOME: ok. Never take option 1 — with no user, /review returns control to this same gate, a non-terminating cycle. Never take option 2 — 完全授權 inline execution is satisfiable only by a standing authorization recorded in the driving context, per loop-contract §2 |
| Pipeline Step 0 — spec dir missing or spec files incomplete → stop + escalate | **Authorization** | Hard stop. No default can substitute a missing spec |
| Pipeline §4b task BLOCKED escalations (persistent compile error / failure_count ≥ 2 / spec contradiction) | Input | Record BLOCKED, continue unblocked work (per the pipeline's never-stop-early rule), annotate in final-report.md |
| Pipeline §4d merge escalation (semantic conflict ❌ / Green broken ×3) | Input | Mark downstream groups BLOCKED, continue remaining steps, annotate in final-report.md |
| Pipeline Step 5 E2E failure path | — (autonomous) | No interaction point: e2e-fix-agents once, one re-run, else record ❌ and proceed to Step 6 |
