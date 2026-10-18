# Performance

Performance is the work a path does relative to the work its result needs, at the load the system actually carries. A change fails to hold with it when it makes the system repeat work, wait for work it does not need, or grow without bound.

**Why:** Slowness enters through a loop that queries, a step that blocks, or a cache that never empties, and it shows up only at load. Reading finds the shape; only a record of a run can confirm a number.

**Pattern:**
1. **Name the expected load first.** One person running a script and many users or processes at once have different hot paths; state the load the repo implies (README, deploy config) and judge against it.
2. **Find repeated work.** A query per item, the same I/O or computation inside a loop, work every process repeats, a value recomputed on every call when it could be computed once.
3. **Find unbounded growth.** O(n²) on input that can be large, a list or cache that only grows, memory held by a long-lived closure that captures more than it needs.
4. **Find needless waiting.** Independent operations run one after another, blocking work added to startup or a request path, a lock held across slow I/O.
5. **Size it by its share.** A piece that takes a small share of the end-to-end path can save only that share; a big slowdown on the user's path is a problem, a small win in a cold path is a suggestion.
6. **Ask a claimed speed for its record.** A number in the target carries its run count, its spread, and the limiter that bounds it, from the author's run; a speed claim without that is 「coverage lost」, never confirmed or refuted by reading alone.
7. **Suspect a number of measuring the wrong thing.** Errors, cached or skipped work, lazy code nobody consumed, or an untuned side each produce a number for work that never happened; the record shows which were ruled out.
8. **Do not trade correctness or clarity for unmeasured speed.** An optimisation with no record of the need is excess under `goal.md` #3.

**The test:** At the expected load, what does this path repeat, wait for, or accumulate that its result does not need?

**You skipped this when** a loop over user data issues one query per item, or a speed claim in the target was accepted without a record.
