# Goal — the first place every change must agree with

**Bedrock.** The user's goal is the first place a change must agree with. Each thing the goal asks for has an edit that delivers it, each edit serves something the goal asks for, and the delivered behaviour is the asked behaviour, not a narrower or wider one.

1. **The goal's source.** Acceptance the user named, a plan's Building and Not building, an issue or spec the commits cite, when present; otherwise the request in its own words. The author's summary of the request is the target's claim, never the goal.
2. **Did it do what was asked?** Cite the goal's words beside the code that does them. A logic error is this disagreement at line scale: the code against what its name, its contract, or the goal says it does — off-by-one, an inverted condition, a missing `await`, an error swallowed instead of surfaced, an edge (empty, zero, one, last, maximum, rounding, time zone, concurrent, timeout, partial failure) the goal covers and the code does not.
3. **Did it add what was not asked?** A guard for a state no caller produces, error handling that hides instead of fails, an option nobody requested, validation repeated behind a boundary that already validates. Cite it and the cost it carries. "Safer" alone is not a reason.
4. **Did it solve a smaller problem than asked?** The happy path only, a requirement silently narrowed, the hard part left as a TODO or an "out of scope" the request never granted. Cite the dropped part beside the request's wording.
5. **Every finding has a concrete case.** This input or this situation leads to this wrong result. A finding whose trigger cannot be stated — "this could be null" without the call that makes it null — is not a finding.
6. **The user is whoever consumes the result.** An end user for a product, the caller for a library, the next engineer for code. Impact is stated from their side.
7. **A plan is a target too.** Its sections are places: Building against Not building, Approach against Key decisions, each Unknown carrying its question, why deferring is safe, and who decides when.
8. **A note admitting a gap does not close it.** A gap the author listed, an earlier version that shared it, or a sibling that fails the same way makes the gap known, not designed.
9. **Only the user waives part of the goal.** A reviewer who thinks a goal item is wrong reports that as a question, and still checks the target against it.
