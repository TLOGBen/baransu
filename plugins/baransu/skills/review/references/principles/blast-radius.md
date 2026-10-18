# Blast radius

A change reaches as far as the facts it alters travel. Follow each one from where it is born, through everything that reads it, to where its result is finally taken, and check that each consumer still gets what it needs.

**Why:** Listing callers takes a second; the breakage a symbol search shows is the smallest part. What breaks is a consumer that relied on something the change no longer gives — a value, a state, a moment, an environment — and no line anywhere says the opposite.

**Pattern:**
1. **Find the one fact it is safe because of.** Most risky-looking changes are safe because of a single fact ("this only drops entries already dead"). State it and spend the review on it rather than on a long list of maybes.
2. **Write down what each consumer needs, then check it gets it.** Read what the consumer does with the fact — the line that uses the value, the step that starts from the state, the check that waits on the moment — and derive the need from that code; the second citation is that line and the need it implies.
3. **Look where grep stops.** When each step runs, teardown and unmount, indirect dispatch, a callback's return value, a serialized format, a database column, a feature flag, another language reading the same bytes, code three hops downstream.
4. **Read every caller of a changed signature, return value, or behaviour.** A fix applied in one caller while the shared function stays broken is half a fix.
5. **Read the environments it runs in.** Each platform the target claims is a consumer of the same code; the author's record of that platform is where it speaks.
6. **Check the pattern, not the instance.** Where the change fixes or introduces a fault, find every other place with the same shape.
7. **State the level each fact reached.** Said so; pointed at the line; walked every branch and shown the bad case cannot be reached; shown by the author's record of this version. A fact below the level its risk needs is uncertain, naming what would settle it — 「coverage lost: needs X」 when only a run could.
8. **Stop where the next look cannot move the verdict.** Depth follows consequence; `--full` follows each fact to the end of its lifecycle across the whole system.
9. **List what was walked and held.** Each place read and found to hold is reported with what was read, so the reader sees how far the review reached.

**The test:** For each consumer of a changed fact, can you say in one sentence what it needs and point at the line where it gets it?

**You skipped this when** the review lists the callers but never says what any of them needs, or judges a place from a quote without reading what it does.

Distinct from `single-source.md`, which follows what states the fact; this one follows what consumes it.
