# Risk

Every step that changes state will one day fail, repeat, or race. The goal includes what happens then: the system converges to the right state, loses nothing it was trusted with, and shows the failure where it happened.

**Why:** Crashes, restarts, retries, and concurrent actors are normal. If a partial run changes the next run's outcome, or a failure is swallowed, every incident becomes a debugging session and some become data loss.

**Pattern:**
1. **Ask what a repeat does.** If the step runs twice, or the previous run stopped at any point, does it reach the same end state? Derive each step from the state that exists, not from what the last run meant to do.
2. **Make leftovers recognisable.** A lock, a temporary file, a half-written record, or a claimed job left by a crashed run is judged stale by evidence that holds wherever the run could have stopped.
3. **Ask what a second writer does.** State two actors can write is shared. Separate it first; serialise it structurally only when one shared writer is a real invariant. A convention is not concurrency control, and check-then-write is a race.
4. **Never let a replacing write destroy.** One malformed entry must not turn a whole file into "corrupt, start over"; a write goes to a temporary path and is renamed into place; an unknown version is refused, not overwritten; related writes land together or not at all.
5. **Name the recovery before an irreversible step.** A deletion, a migration, a send, or a publish says how it is undone, or why it need not be.
6. **Surface a failure where it happens.** A swallowed error, a silent fallback to a default, a clamped value, or discarded state moves the failure somewhere harder to find.
7. **Keep a guard only for a legitimate state.** If the system may be in that state, handling it is the fix; if the state should never exist, the guard hides what produced it.
8. **Judge scale against the expected load.** One person running a script and many processes at once fail differently: state that only grows, work every process repeats, per-process state that must be shared. Name the load assumed.
9. **Weigh each risk honestly.** Its trigger, its `file:line`, how likely, how costly. A shortcut the author marked with its limit and upgrade trigger is a decision until the expected load crosses that limit.

**The test:** For each state-changing step: what if it runs twice, what if it dies halfway, what if two run at once — and does each answer end in the right state with the failure visible?

**You skipped this when** the review judged only the success path of a write, a migration, or a retry loop.
