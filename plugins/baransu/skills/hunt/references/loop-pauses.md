# loop-pauses — /hunt PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/hunt is loop=assisted: diagnosis advances automatically, but the fix itself
waits for the driver — the checkpoint rows below define exactly where.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Scope Blast step 3 — resolving an `unsure` match decision | Input | leave + annotate the match line 「此處採預設」 in the case file's Scope Blast section |
| Scope Blast — fixing unrelated bugs surfaced during the blast | **Authorization** | Never fix. List them in the case file, annotate that they await user approval |
| Bisect Mode step 1 — repo has zero tags, known-good ref needed | Input | Pick the oldest commit touching the symptom file, label the choice 「此處採預設」 in the case file |
| Loop-mode "report fix before applying" checkpoint (Hard Rules note) | **Authorization** | Stop after root-cause confirmation: emit the Success-format report with the proposed diff and end with `LOOP_OUTCOME: blocked（待人工核可修復）` per `../../_shared/loop-contract.md` |
