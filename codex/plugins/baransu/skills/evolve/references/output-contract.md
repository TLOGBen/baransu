# output-contract — the evolution package

Every run writes its working artifacts under `.claude/evolve/<slug>/`, where `<slug>` is derived from the target skill name. The package is the durable, user-visible record of what changed and why.

## Artifacts

| File | Content |
|------|---------|
| `log.md` | Per-round trace: round #, dimension touched, mutation summary, structure-gate result, judge votes, keep/restore decision. Append-only; every round is one entry. This is the audit trail — a reader can reconstruct exactly which dimension changed each round and why it was kept or restored. |
| `results.tsv` | 9 score columns (`d1`…`d9`) plus a `round` index, one row per round. The score trajectory. Rows carry the round's **diagnostician** scores — the only absolute per-dimension scores produced each round (judges return deltas only); `report.md` labels the trajectory `source: diagnostician (non-blind)`. |
| `convergence.svg` | Score-over-rounds curve. Effective-baseline line steps up only on keeps; restored rounds show as dips that do not lower the baseline. |
| `held-out.md` | Held-out comparison: pre-evolution vs post-evolution score on the held-out prompt set, plus the **evidence-strength** label (see below). |
| `report.md` | Run summary: start/end score, dimensions improved, convergence reason, **effectiveness_mode** (`real-exec` \| `offline-同源` \| `no-benchmark` — one value per run; Gate 3 decides once per run, so this is an enum, not a ratio) plus the Gate 3 reason, and per-axis evidence source. |
| `card.html` | Kami-styled result card. Copy drafted through `/write`, then rendered **only through the `/book` entry** (`--text` / slug mode) — never hand-assembled, never reaching into `book`'s `references/` internals; copy the `/book` output HTML to `.claude/evolve/<slug>/card.html` (`/book` emits HTML, not PNG). Omitted on zero-adoption runs via SKILL.md Stage 7's lighter exit (noted in `report.md`). See §Human-readable delivery. |
| `snapshot/<round>.md` | File-level snapshots (see `safety-gates.md` Gate 2). |

## Human-readable delivery (the output is for a human)

The package is read by a person, not a parser. Two user-facing surfaces MUST be made readable before they reach the user — raw, jargon-dense, jumpy output is a defect, not a deliverable:

- **Convergence summary** (the in-conversation 繁中 wrap-up) and **card copy**: draft through `/write` (zh) first, so the prose is coherent and plain. A reader who did not watch the run should understand *what changed and why* without decoding `dim`/`headroom`/`alpha-beta` jargon. Do not dump the raw round-by-round technical trace at the user as the summary.
- **Result card**: render through the `/book` entry (`--text` / slug mode) — **never hand-assemble HTML**. Hand-built cards drift from the Kami book format and read as jumpy; `/book` is what keeps the format, structure, and SVG conventions correct.

Order: `/write` the copy → feed the refined copy into `/book` → deliver. The card and the summary are *finished* artifacts, not debug dumps. (`log.md` / `results.tsv` stay raw — they are the audit trail, not the human-facing surface.)

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

- start/end total score and per-dimension deltas
- dimensions improved, rounds run, convergence reason
- effectiveness_mode (`real-exec` / `offline-同源` / `no-benchmark`) + the Gate 3 reason + per-axis evidence source
- `results.tsv` score source label (`source: diagnostician (non-blind)`)
- held-out evidence-strength (硬證據 / 題目泛化證據), and 未通過 held-out prominently when the converged version regressed on the held-out set (SKILL.md Stage 7 regression branch)
- any untrusted real-exec runs flagged (with memory-rotation advisory)
