# output-contract — the evolution package

Every run writes its working artifacts under `.codex/evolve/<slug>/`, where `<slug>` is derived from the target skill name. The package is the durable, user-visible record of what changed and why.

## Artifacts

| File | Content |
|------|---------|
| `log.md` | Per-round trace, append-only, one entry per round: round #, the **finding** (phenomenon + evidence / impact / implicated clause / flaw / origin + source / verification / brief), the **seeds** (each seed's operation, `why_kind` and gate result; the picker's per-letter scores, the letter key, the winner and its margin; `deferred_ideas` from losing seeds), the winner's bedrock with `change_kind` and words before → after, subtraction-, case-term- and structure-gate results, the exam sheet path, judge votes, the ablation label (`未經消融` when it applies), decision (`kept` / `restored` / `no-finding` / `append-only-refused` / `case-term-refused` / `no-surviving-seed` / `user-declined` / `standing-auth auto-adopt` / `window-breach-restored`). This is the audit trail — and the next run's clause provenance: a reader can reconstruct which clause changed each round, what it was for, and why it was kept or restored. |
| `decisions.tsv` | One line per decision for the whole run, tab-separated: `ts`, `phase`, `decision`, `why`, `evidence` (a pointer that resolves: file:line, panel or exam path, commit, decisions row), `result`. Covers every seed pick, gate refusal, keep/restore and adoption, every user instruction that changed the run mid-way (a rule, the benchmark, the success bar), the exam template hash, and every contaminated-exam rerun. Stage 7 reconciles it: each pointer resolves, each `log.md` keep/restore has its line, each run-changing user instruction in the conversation has one; mismatches go to `report.md`. |
| `exam/` | Present when the exam ran (`exam.md`): `template.md` and its hash, `versions/<round>/` read-only copies, the raw outputs per prompt and run, `round-<N>.md` exam sheets, `contaminated/` (reference only, never scored). Answer keys and `case-terms.txt` sit beside it and never leave the scorer and the panel. |
| `results.tsv` | 9 score columns (`d1`…`d9`) plus `round` and `words` (body word count), one row per round. The score trajectory. Rows carry the round's **diagnostician** scores — the only absolute per-dimension scores produced each round (judges return deltas only); `report.md` labels the trajectory `source: diagnostician (non-blind)`. |
| `convergence.svg` | Score-over-rounds curve. Effective-baseline line steps up only on keeps; restored rounds show as dips that do not lower the baseline. |
| `held-out.md` | Held-out comparison: pre-evolution vs post-evolution score on the held-out prompt set, plus the **evidence-strength** label (see below). |
| `report.md` | Run summary: start/end score and word count, change-kind tally (replace / delete / add / refused), dimensions improved, convergence reason, **effectiveness_mode** (`real-exec` \| `offline-同源` \| `no-benchmark` — one value per run; Gate 3 decides once per run, so this is an enum, not a ratio) plus the Gate 3 reason, and per-axis evidence source. |
| `card.html` | Result card. Copy drafted through `$baransu:write`, then rendered **only through the `$baransu:draw` page lane** — never hand-assembled, never reaching into `draw`'s `references/` internals; copy the `$baransu:draw` output HTML to `.codex/evolve/<slug>/card.html` (`$baransu:draw` emits HTML, not PNG). Omitted on zero-adoption runs via SKILL.md Stage 7's lighter exit (noted in `report.md`). See §Human-readable delivery. |
| `snapshot/<round>.md` | File-level snapshots (see `safety-gates.md` Gate 2). |

## Human-readable delivery (the output is for a human)

The package is read by a person, not a parser. Two user-facing surfaces MUST be made readable before they reach the user — raw, jargon-dense, jumpy output is a defect, not a deliverable:

- **Convergence summary** (the in-conversation 繁中 wrap-up) and **card copy**: draft through `$baransu:write` (zh) first, so the prose is coherent and plain. A reader who did not watch the run should understand *what changed and why* without decoding `dim`/`headroom`/`alpha-beta` jargon. Do not dump the raw round-by-round technical trace at the user as the summary.
- **Result card**: render through the `$baransu:draw` page lane — **never hand-assemble HTML**. Hand-built cards drift and read as jumpy; `$baransu:draw` is what keeps the format, structure, and figure conventions correct.

Order: `$baransu:write` the copy → feed the refined copy into `$baransu:draw` → deliver. The card and the summary are *finished* artifacts, not debug dumps. (`log.md` / `results.tsv` stay raw — they are the audit trail, not the human-facing surface.)

## Held-out independence layer (REQ-004)

The `test-prompts` set is split into **train** (drives mutation/scoring during the loop) and **held-out** (final validation only).

- **Baseline (not an independence layer)**: held-out is scored by fresh judges that did not serve in the train loop. Since judges are single-use, this is definitionally true of every run — it changes the prompts but not the ruler (same rubric, same judge type), so it defends only against *prompt* overfitting.
- **Independence layers** (user-selectable, each changes the ruler): a **different rubric dimension weighting**, or **human ground-truth** sampling where the user fixes what "pass" means. Only a ruler change defends against *rubric* overfitting.

The held-out **pass criteria** are confirmed by the user, not auto-generated, to avoid the same-model question-the-questions-and-score-them backdoor. (Non-interactive default per `loop-pauses.md`: benchmark-supplied criteria, baseline path, label capped at 題目泛化證據.)

### Evidence-strength field (required)

`held-out.md` MUST carry one of:

- **硬證據 (hard evidence)** — a ruler-changing independence layer was applied (different rubric weighting or human ground-truth); the held-out gain reflects generalization beyond the training prompts AND beyond the training scoring ruler. A fresh-judge pool alone never qualifies.
- **題目泛化證據 (prompt-generalization evidence)** — the baseline path (fresh judges, same rubric). The result shows generalization to new prompts only and does **not** defend against rubric overfitting. The report states this explicitly.

Never label a same-ruler held-out result as 硬證據.

## report.md required fields

- start/end total score and per-dimension deltas; start/end body word count
- change-kind tally: rounds kept by `replace` / `delete` / `merge` / `add`, and rounds refused at the subtraction or case-term gate
- dimensions improved, rounds run, convergence reason
- effectiveness_mode (`real-exec` / `offline-同源` / `no-benchmark`) + the Gate 3 reason + per-axis evidence source
- when the exam ran: start/end recall, items found in only one run, penalties, mean tokens and wall time, and the noise band; any contaminated rerun
- seeds: per round, the winner's margin over the runner-up; every kept `delete`/`merge` still labelled `未經消融`
- the `decisions.tsv` reconciliation result, with each mismatch
- `results.tsv` score source label (`source: diagnostician (non-blind)`)
- held-out evidence-strength (硬證據 / 題目泛化證據), and 未通過 held-out prominently when the converged version regressed on the held-out set (SKILL.md Stage 7 regression branch)
- any untrusted real-exec runs flagged (with memory-rotation advisory)
