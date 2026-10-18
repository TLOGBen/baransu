# Principles — index

Each principle is one statement, why it holds, a numbered pattern of at most ten moves, the test that checks it, and the sign it was skipped. Load a principle when a place in the review meets its trigger. A finding that rests on a principle cites it as `<file> #<n>`, and that move is the second citation only where no place in the target or its contracts speaks. Two principles never conflict: when they seem to, the statement that explains both has not been found yet, and that is a finding about the principles, not a choice between them.

| File | Load when | Purpose |
|---|---|---|
| `goal.md` | Always: every review checks the target against what the user asked for. | Did what was asked, nothing added, nothing narrowed. |
| `single-source.md` | The change alters a name, value, rule, or promise that is stated, listed, or mirrored anywhere else. | One fact, one owner; every statement of it holds. |
| `blast-radius.md` | The change alters behaviour that other code, data, timing, a platform, or a later step relies on. | Each consumer still gets what it needs. |
| `risk.md` | The change writes, deletes, migrates, retries, runs concurrently, or does anything hard to undo. | What a failure costs, and whether it recovers. |
| `evidence.md` | The target claims it ran, passed, measured, or counted something, or a run record exists. | Read the author's record; never produce one. |
| `tests.md` | The change adds, changes, keeps, or relies on a test. | A test proves only what breaking would turn red. |
| `trust-boundary.md` | Data, a credential, or a command crosses into the system from outside it, or leaves it. | Concrete exploitable paths, checked at the boundary. |
| `domain.md` | The target encodes business states, rules, transitions, terms, scenarios, or a model of the domain. | Domain language, invariants, and Given/When/Then behaviour. |
| `structure.md` | The change adds or moves a module, layer, interface, state owner, or dependency. | Boundaries where reasons to change differ, nowhere else. |
| `taste.md` | The change adds or rewrites code, or the repo documents how its code should be written. | The smallest complete change, in the repo's own way. |
| `readability.md` | The change adds indirection, state, names, or comments a reader must hold to follow it. | What a reader must trace and hold to understand it. |
| `performance.md` | The change touches a loop over data, I/O, a query, startup, a hot path, or claims a speed. | Work the change makes the system repeat or wait for. |

Sources, adapted and restated in this repo's terms: pstack principles, `correct`, `blast-radius`, `architect` design red flags, and `interrogate` rubric (cursor/plugins, MIT); `codebase-design`, `code-review`, `domain-modeling`, and `tdd` (mattpocock/skills); `ponytail` and `ponytail-review` (DietrichGebert/ponytail, MIT); Fowler, *Refactoring*, ch. 3; Claude Code's built-in `/security-review`.
