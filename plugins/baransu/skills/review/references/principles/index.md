# Principles — index

Each principle is one bedrock and at most ten articles that explain it. Load a principle when a place in the review meets its trigger; a finding that rests on a principle cites the article by number, and that article is the second citation. Two principles never disagree: when they seem to, the bedrock that explains both has not been found yet, and that is a finding about the principles, not a choice between them.

| File | Load when | Purpose |
|---|---|---|
| `goal.md` | Always: every review checks the target against what the user asked for. | Did what was asked, nothing added, nothing narrowed. |
| `single-source.md` | The change alters a name, value, rule, or promise that is stated, listed, or mirrored anywhere else. | One fact, one owner; every copy agrees. |
| `blast-radius.md` | The change alters behaviour that other code, data, timing, a platform, or a later step relies on. | Follow each changed fact through its lifecycle. |
| `risk.md` | The change writes, deletes, migrates, retries, runs concurrently, or does anything hard to undo. | What a failure costs, and whether it recovers. |
| `evidence.md` | The target claims it ran, passed, measured, or counted something, or a run record exists. | Read the author's record; never produce one. |
| `tests.md` | The change adds, changes, keeps, or relies on a test. | A test proves only what breaking would turn red. |
| `trust-boundary.md` | Data, a credential, or a command crosses into the system from outside it, or leaves it. | Concrete exploitable paths, checked at the boundary. |
| `domain.md` | The target encodes business states, rules, transitions, terms, or a model of the domain. | The domain's language and invariants, made structural. |
| `structure.md` | The change adds or moves a module, layer, interface, state owner, or dependency. | Boundaries where reasons to change differ, nowhere else. |
| `taste.md` | The change adds or rewrites code, or the repo documents how its code should be written. | The smallest complete change, in the repo's own way. |
| `readability.md` | The change adds indirection, state, names, or comments a reader must hold to follow it. | What a reader must trace and hold to understand it. |
| `performance.md` | The change touches a loop over data, I/O, a query, startup, a hot path, or claims a speed. | Work the change makes the system repeat or wait for. |

Sources, adapted and restated in this repo's terms: pstack principles, `correct`, `blast-radius`, `architect` design red flags, and `interrogate` rubric (cursor/plugins, MIT); `codebase-design`, `code-review`, `domain-modeling`, and `tdd` (mattpocock/skills); `ponytail` and `ponytail-review` (DietrichGebert/ponytail, MIT); Fowler, *Refactoring*, ch. 3; Claude Code's built-in `/security-review`.
