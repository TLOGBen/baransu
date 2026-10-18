# Performance — work the change makes the system repeat or wait for

**Bedrock.** Performance is the work a path does relative to the work its result needs, at the load the system actually carries. A change disagrees with it when it makes the system repeat work, wait for work it does not need, or grow without bound — judged from the code, and measured only through the author's record.

1. **Name the expected load first.** One person running a script and many users or processes at once have different hot paths; state the load the repo implies (README, deploy config) and judge against it.
2. **Repeated work.** A query per item, the same I/O or computation inside a loop, work every process repeats, a value recomputed on every render or call when it could be computed once.
3. **Growth.** O(n²) on input that can be large, a list or cache that only grows, memory held by a long-lived closure that captures more than it needs.
4. **Needless waiting.** Independent operations run one after another, blocking work added to startup or a request path, a lock held across slow I/O.
5. **Size it by share.** A piece that takes a small share of the end-to-end path can only save that share; a big slowdown on the user's path is a problem, a small win in a cold path is a suggestion.
6. **A claimed speed needs its record.** A number in the target carries its run count, its spread, and the limiter that bounds it, from the author's run; a speed claim without that is 「coverage lost」, never confirmed or refuted by reading alone.
7. **A measured number can measure the wrong thing.** Errors, cached or skipped work, lazy code nobody consumed, or an untuned side each produce a number for work that never happened; the record shows which were ruled out.
8. **Do not trade correctness or clarity for unmeasured speed.** An optimisation with no record of the need is excess under `goal.md` article 3.
