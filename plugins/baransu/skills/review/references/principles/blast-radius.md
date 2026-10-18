# Blast radius — follow the fact through its lifecycle

**Bedrock.** A change reaches as far as the facts it alters travel. Follow each one from where it is born, through everything that reads it, to where its result is finally taken; the breakage a symbol search shows is the smallest part of it.

1. **Find the one fact it is safe because of.** Most risky-looking changes are safe because of a single fact ("this only drops entries already dead"). Find it, state it, and spend the review on it rather than on a long list of maybes.
2. **Look where grep stops.** When each step runs, teardown and unmount, indirect dispatch, a callback's return value, a serialized format, a database column, a feature flag, another language reading the same bytes, code three hops downstream.
3. **Read what takes the result.** Whatever relies on what the change altered — a caller, a later step, a listener, a job — and what it now receives.
4. **A changed signature, return value, or behaviour reaches every caller.** Read each one; a fix applied in one caller while the shared function stays broken is half a fix.
5. **Read the environments it runs in.** Each platform the target claims is a reader of the same code; the author's record of that platform is where it speaks.
6. **Check the pattern, not the instance.** Where the change fixes or introduces a fault, find every other place with the same shape.
7. **State the level each fact reached.** Said so; pointed at the line; walked every branch and shown the bad case cannot be reached; shown by the author's record of this version. A fact left below the level its risk needs is 「coverage lost: needs X」, naming the record that would settle it.
8. **Stop where the next look cannot move the verdict.** Depth follows consequence; `--full` follows each fact to the end of its lifecycle across the whole system.
9. **List what was checked and cleared.** Each place read and found in agreement is reported with why, so the reader sees how far the review reached.
