# Goal

The user's goal is the first place every change must hold with: each thing it asks for has an edit that delivers it, each edit serves something it asks for, and what is delivered is what was asked — not narrower, not wider.

**Why:** A change can be correct, clean, and tested and still be the wrong change. Everything else a review checks is measured against this; a target that passes every other principle and misses the goal has failed.

**Pattern:**
1. **Take the goal from its source.** Acceptance the user named, a plan's Building and Not building, an issue or spec the commits cite; otherwise the request in its own words. The author's summary of the request is the target's claim, never the goal.
2. **Cite the goal beside the code that does it.** A logic error is this at line scale: the code against what its name, its contract, or the goal says it does — off-by-one, an inverted condition, a missing `await`, an error swallowed instead of surfaced, an edge (empty, zero, one, last, maximum, rounding, time zone, concurrent, timeout, partial failure) the goal covers and the code does not.
3. **Name what was added that nobody asked for.** A guard for a state no caller produces, error handling that hides instead of fails, an option nobody requested, validation repeated behind a boundary that already validates. "Safer" alone is not a reason. Risk: 超出需求.
4. **Name what was narrowed.** The happy path only, a requirement silently shrunk, the hard part left as a TODO or an "out of scope" the request never granted. Cite the dropped part beside the request's wording. Risk: 需求被縮小.
5. **Give every finding a concrete case.** This input or this situation leads to this wrong result. "This could be null" without the call that makes it null is not a finding.
6. **State impact from the consumer's side.** The user is whoever consumes the result: an end user for a product, the caller for a library, the next engineer for code.
7. **Treat a plan as a target.** Its sections are places: Building against Not building, Approach against Key decisions, each Unknown with its question, why deferring is safe, and who decides when.
8. **Do not let a note close a gap.** A gap the author listed, an earlier version that shared it, or a sibling that fails the same way makes it known, not designed.
9. **Leave waivers to the user.** A goal item the reviewer thinks is wrong is raised as a question, and the target is still checked against the item as written: a departure from the request or a written contract is a problem as `index.md` defines, that text its second citation; where the departure improves on the contract, its bedrock brings the contract in line with the code. A departure that breaks what a user relies on stays a problem however the contract is rewritten; changing the text never closes it.

**The test:** Put the goal's words in one column and the edits in another. Does every goal item have its edit, every edit its goal item, and does each pair describe the same behaviour?

**You skipped this when** the report judges the code against the author's commit message, or every finding is about quality and none says whether the asked-for thing was done.
