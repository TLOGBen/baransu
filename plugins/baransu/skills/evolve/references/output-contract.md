# output-contract — the evolution package

Every run writes its working artifacts under `.claude/evolve/<slug>/`, where `<slug>` is derived from the target skill name. The package is the durable, user-visible record of what changed and why.

## Artifacts

| File | Content |
|------|---------|
| `log.md` | Per-round trace: round #, dimension touched, mutation summary, structure-gate result, judge votes, keep/restore decision. Append-only; every round is one entry. This is the audit trail — a reader can reconstruct exactly which dimension changed each round and why it was kept or restored. |
| `results.tsv` | 9 score columns (`d1`…`d9`) plus a `round` index, one row per round. The score trajectory. |
| `convergence.svg` | Score-over-rounds curve. Effective-baseline line steps up only on keeps; restored rounds show as dips that do not lower the baseline. |
| `held-out.md` | Held-out comparison: pre-evolution vs post-evolution score on the held-out prompt set, plus the **evidence-strength** label (see below). |
| `report.md` | Run summary: start/end score, dimensions improved, convergence reason, **dry_run ratio** (fraction of effectiveness scoring that fell back to offline), and per-axis evidence source. |
| `card.png` | Kami-styled result card. Rendered **only through the `/book` entry** (`--text` / slug mode); never by reaching into `book`'s `references/` internals. |
| `snapshot/<round>.md` | File-level snapshots (see `safety-gates.md` Gate 2). |

## Held-out independence layer (REQ-004)

The `test-prompts` set is split into **train** (drives mutation/scoring during the loop) and **held-out** (final validation only). Held-out must add at least one layer of independence so it defends against *rubric* overfitting, not merely *prompt* overfitting:

- **Default**: a **separate judge pool** — held-out is scored by judges that do not overlap with the train-loop judges.
- **Options** (user-selectable): a **different rubric dimension weighting**, or **human ground-truth** sampling where the user fixes what "pass" means.

The held-out **pass criteria** are confirmed by the user, not auto-generated, to avoid the same-model question-the-questions-and-score-them backdoor.

### Evidence-strength field (required)

`held-out.md` MUST carry one of:

- **硬證據 (hard evidence)** — an independence layer was applied; the held-out gain reflects generalization beyond the training prompts AND beyond the training scoring ruler.
- **題目泛化證據 (prompt-generalization evidence)** — no independence layer was applied (held-out still uses the same rubric/judges). The result shows generalization to new prompts only and does **not** defend against rubric overfitting. The report states this explicitly.

Never label a same-ruler held-out result as 硬證據.

## report.md required fields

- start/end total score and per-dimension deltas
- dimensions improved, rounds run, convergence reason
- dry_run ratio + per-axis evidence source (`real-exec` / `offline-同源`)
- held-out evidence-strength (硬證據 / 題目泛化證據)
- any untrusted real-exec runs flagged (with memory-rotation advisory)
