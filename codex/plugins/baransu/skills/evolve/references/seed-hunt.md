# Seed hunt — three bedrocks, one refined

A round's bedrock starts as three independent first versions (seeds) written from one brief; a blind picker ranks them, and only the winner is refined, gated, examined and judged.

## Why seeds

The same brief written twice lands far apart. baransu's `$baransu:draw` 7.5.0 controlled run (20 builders, four subjects, blind judges) and the 2026-10 review bedrock iteration both found the spread between identical runs larger than the effect of any single rule. So the cheap gain is to sample the first version several times and spend the expensive part — the exam and the panel — on the best one. Seeds are text; they stop before Stage 3's structure gate.

## The brief

The diagnostician writes it (Stage 1); it is the seeds' whole view of the round:

- **phenomenon** — the observed pattern in general terms (what kind of thing went wrong, in what kind of situation), never the instance: no file name, prompt wording, answer-key item or other case term;
- **impact** — the outcome the target's user asked for that this fails;
- **root** — the implicated clause verbatim (or `none` after a whole-skill read), its flaw, and the problem the clause was added to solve;
- **verification** — what would show a fix worked, stated as a behaviour, not as an exam item;
- **checkpoint** — when the flaw is a falsified direction: the clause as it read in the latest snapshot before that direction began, and any reference baseline the user named (a simpler skill or tool that does the same job); the seeds study how it did the job and set out from there in a different direction;
- optionally, a method the user named as a reference for this kind of problem; the seeds decide whether and how to use it.

No answer, no proposed wording, no preferred solution. The brief takes the case-term grep before any seed sees it (SKILL.md Stage 3).

## Operations

Each seed chooses one operation and states in `why_kind` why it beats the other three:

- **add** — the phenomenon is one no existing clause explains (`implicated: none`); the addition is a positive definition of what the step is or does, never a prohibition against the observed failure.
- **delete** / **merge** — the skill performs better, or no worse, without the clause or with the two clauses as one. That is proven by the exam (an ablation) or readable from the text alone (a dangling reference, a contradiction, an exact restatement); "reads simpler" is not a reason by itself. A merge names the clause it absorbs, `merge (absorbs: "<clause>")`, and the merged sentence must cover every phenomenon each original explained, none lost, and read more clearly. Several bedrocks may coexist: when no single sentence explains all their phenomena, keep them apart — a forced merge that blurs meaning is a regression.
- **replace** — restating the clause beats adding, deleting and merging for this phenomenon.
- **keep** — none of the above can be shown better; the seed returns `keep` and the reason.

A clause falsified by the evidence — its prescribed work shows in the cost and never in the results, or it was strengthened round after round while its phenomenon never moved — is deleted or restated from its checkpoint in a different direction. A seed that strengthens it once more is not a candidate: adding force to a view that bought nothing only buys more of nothing.

A frequent root is a clause whose subject or object is unstated: the model fills the gap with the cheapest reading — a passive "X is verified" with no verifier, a "cost" with no bearer. The bedrock names who does what to what.

## Dispatch the seeds

1. Start three **evolve-diagnostician** agents in seed mode, in parallel, in one message. Each receives the brief, the target path, the rubric and `references/provenance.md` — no evidence, no exam sheet, no answer key, no `log.md`, no other seed.
2. Each returns `{change_kind, absorbs?, bedrock, why_kind, words}` in the shape in `agents/evolve-diagnostician.md`.
3. Apply each seed to its own scratch copy, `scratch/seed-<a|b|c>.md`, and run Stage 3's subtraction and case-term gates on it. A seed that fails a gate, returns a malformed shape or returns `keep` is recorded and dropped; the pick runs on the rest. One survivor is promoted without a pick; none ends the round as `no-surviving-seed`.

## Pick blind

1. Copy each surviving scratch to `panel/round-<N>/seeds/` under a shuffled letter (`P.md`, `Q.md`, `R.md`); write the letter-to-seed key to `log.md` only after the verdict.
2. Start one fresh **evolve-judge** in rank mode with the brief, the rubric and the lettered files. It never sees the current version, the seed notes, the evidence or the answer keys.
3. The judge scores each seed on the structure dimensions and on how fully it explains the brief's phenomenon, gives each an overall score and one line on why, and ranks them. The highest overall wins; on a tie, the seed whose lowest dimension is higher.
4. Record in `log.md`: the scores per letter, the key, the winner and its margin over the runner-up.

## Promote the winner

The winner alone goes to the structure gate, the exam and the panel; Stage 2 may refine its wording so it applies cleanly. A losing seed is never adopted and never spliced into the winner — a seed is kept or dropped whole. An idea in a losing seed worth trying goes to `log.md` as `deferred_ideas`, where the next round's diagnostician reads it. The picker decides only which seed is examined; keep and restore belong to the panel and the exam.
