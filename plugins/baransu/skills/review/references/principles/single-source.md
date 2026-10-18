# Single source — one fact, one owner

**Bedrock.** Every fact has one owner, and every other statement of it is either derived from that owner or agrees with it. A change that looks right from the file it touched must be right for the whole repo; the places it did not open are where it goes wrong.

1. **List what changed before searching.** Each name, value, rule, signature, output, and promise the change alters, taken from its first edit to its last, not from what seemed to matter.
2. **Search every form the fact takes.** Its name, its old value or output, and the words a description of it would use — in code and prose, tables, examples, expected results, evals, docs, and mirrors such as a second platform's copy.
3. **A place still stating the old fact is a disagreement** even beside a sentence stating the new one: that place now says both.
4. **The untouched lines of a changed file are in scope.** They were written against the old fact.
5. **Contracts have owners outside the target.** A library's API, a schema, a protocol, or a specification the target implements owns its shape; the target agrees with it or the target is wrong.
6. **A hand-synced list is the root, not the instance.** When copies drifted once, the bedrock is one list the others derive from, or a build that fails when they differ — not a corrected copy.
7. **Derive from the authoritative schema.** A type, table, or list hand-written beside a file that already owns the shape is a second owner.
8. **Two ways to do one task is two owners.** A new way beside an old one that still works gains callers on both sides; migrate every caller and delete the old way in the same change, unless outside users depend on it.
9. **The same rule applied differently in two places** is one rule with two owners, even when neither copy is wrong yet.
