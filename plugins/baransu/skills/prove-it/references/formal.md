# formal — proving a claim for every case in a scope

A run of the app shows the cases it drove. Some claims are about every case: every order in which steps can interleave, every input up to a size, every input at all. A run can only sample those, so they are settled by a formal check — a check that covers every case in a stated scope — kept beside the recipe under `.claude/prove-it/formal/`. The user must be able to trust its verdict and act on it without learning the verification language.

## When a claim needs one

The claim promises something for all cases, a break harms users, and runs rarely reach the case that breaks it: a state machine that must never reach a bad state, a retry or cancel that must leave the data as it was, two writers that must not lose an update, a lock, a parser, arithmetic that must not overflow, an invariant a data structure must keep. When the user names no claim, pick the strongest such promise in the code the claims touch, not the easiest one to verify. A claim a run can settle does not get one.

## Let the question choose the tool

Choose the cheapest tool that answers the claim, say why, and prefer one the repo's developers can install and run:

- **Can steps happen in a bad order?** A model checker over a small model of the design; TLA+ is the default in any language.
- **Does the code itself hold for every input?** A verifier that runs on the code, for memory safety, overflow, or an invariant of a data structure. When no such verifier exists for the language, say so and test the real code with generated inputs (property-based testing), never a hand-written model of the function.
- **Must it hold at every size, where a bound is not enough?** A proof.

## What makes the check trustworthy

- **True to the code.** Every part of the model or harness cites the `file:line` it stands for; what the check treats as one indivisible step is one indivisible step in the code; names are this repo's.
- **Able to fail.** Each property is seen failing once on a broken variant of the code it guards — a removed check, a reordered step — made in a throwaway copy or worktree and dropped afterwards. A check never seen failing proves nothing.
- **Findings stay findings.** When the current code breaks the property, replay the counterexample against the real code step by step. A step the code cannot take means the model is wrong: fix the model and say what was wrong. When every step can happen, it is a bug: tell it as a short sequence of steps in the code's words, with the harm in one sentence. Never weaken the property or the model until it passes.
- **Honest about scope.** State the bounds, the assumptions, and what is left out. A pass covers the model within its bounds, not the system.
- **Readable without the tool.** The property and the harm are one plain sentence each.
- **Cheap to rerun.** One command, a pinned tool version, short enough to run on every change that touches the covered code.

## Where it lives

One directory per checked area, `.claude/prove-it/formal/<area>/`, listed in the recipe. Its `README.md` holds the property and the harm, the tool and why, the bounds and assumptions, the command, the coverage map (the files and functions each part of the model stands for), and the sync commit — the last commit at which the model was confirmed to describe that code. The sync commit moves only after that confirmation. The model files sit beside it.

## Prove it before relying on it

Follow the README once, cold, as the next run would: break the property in a throwaway copy of the real code, confirm the check catches it, drop the break, and confirm the check is back where it started — passing, or failing only on the findings being reported. A check that was never run this way is a draft.

## Verdict and record

The claim ends as the run's claims do: **proved** — the property holds within the stated bounds; **disproved** — a counterexample every step of which the code can take; **unreachable** — no tool fits, or the code could not be modelled, with what blocked it. The record adds the tool and its version, the bounds, the size of the space explored, the sync commit, and the broken variant that showed the check can fail.

## Keeping it in step (`--maintain`)

A check that keeps passing while the code it describes has changed looks like a proof and is not one. For each check, read every change to its covered code since the sync commit — including covered functions that were renamed, split or moved, and new code that writes the state it guards — and sort each change:

- **No effect** — it alters nothing the model describes; judged against the model, not the commit message.
- **The model no longer describes the code** — a step split in two, a branch added or removed, a check moved, a new path to the guarded state: update the model from the code before rerunning, never from what makes it pass.
- **The promise changed on purpose** — a doc comment, test, changelog or commit message says so: change the property, citing that evidence, with its old and new wording.
- **The promise may be broken** — no such evidence: a failure that follows is a bug candidate.

Run each check once as it is before changing anything, then after updating: a pass is shown able to fail again on the new code; a failure is replayed as above. Each check ends **in sync**, **updated**, **bug**, or **blocked** — updated and bug can both hold. Move the sync commit to the commit checked, except for a blocked check. Edit only the verification files; a fix to product code is the user's, in a change of its own.
