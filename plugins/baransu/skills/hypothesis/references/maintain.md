# maintain — bringing a hypothesis back in line, on demand

A check can keep passing while it describes code that no longer exists; that pass is the dangerous case. This pass runs when invoked with `--maintain` — by a person, or by a skill that reads hypotheses when the code they cover changed — never folded into another hypothesis's run.

1. **Run it as it is.** Run the README's full command once before changing anything, and record the result. A pass says only that the old description still holds.
2. **Read every change** to the covered files since the version the README names — with each commit message when the source is in git, otherwise by comparing the two versions. Look for covered code that moved or was renamed, new code that writes the guarded state, and a new outside state the covered code reads. Sort each change:
   - **no effect** — nothing the model describes changed (judged against the model, not the commit message);
   - **no longer describes** — a step split, a branch added, a check moved, a new path to the guarded state: the model must change;
   - **promise changed on purpose** — the rule must change, citing the evidence (a doc comment, a test, a changelog, a commit message), with old and new wording;
   - **promise may be broken** — the code changed with no such evidence: a failure that follows is a bug candidate.
3. **Update from the code**, before rerunning, never shaped by what passes. Keep the scope unless the change makes it wrong; say so if you must reduce it.
4. **Rerun.** A pass: in a scratch copy, break the new code the way the rule guards against, and see it caught. A failure: walk the trace against the code; a step the code cannot take is a model error, otherwise it is a bug — name the change that brought it.
5. **Record**: move the README's version forward to the one you checked; leave it where it was for anything you could not bring in line, and say why.

Each hypothesis ends with one outcome: in step, updated, bug, or blocked (with the reason). Updated and bug can both hold.
