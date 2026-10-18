# Single source

Every fact has one owner, and every other statement of it holds with that owner: none says the opposite, and every place whose job is to state it states the new fact, not the old one and not nothing.

**Why:** A change that looks right from the file it touched must be right for the whole repo. The next contributor sees only the files it opened and copies the nearest example, so the places the change did not open are where it goes wrong.

**Pattern:**
1. **List what changed before searching.** Each name, value, rule, signature, output, and promise the change alters, from its first edit to its last, not from what seemed to matter.
2. **Search every form the fact takes.** Its name, its old value or output, and the words a description of it would use — in code and prose, tables, examples, expected results, evals, docs, and mirrors such as a second platform's copy.
3. **Judge a stale place as failing** even beside a sentence stating the new fact: that place now says both.
4. **Judge a silent place as failing when stating the fact is its job.** A table that lists the behaviours, a list of the steps, a description of the flow, or an example of the output that leaves out the new part tells its reader the old story.
5. **Read the untouched lines of a changed file.** They were written against the old fact.
6. **Find the owner of each contract the target uses.** A library's API, a schema, a protocol, a specification the target implements, and the loader or adapter that reads a touched file each own a shape; the target holds with it or the target is wrong.
7. **Fix the list, not the copy.** When copies drifted, the bedrock is one list the others derive from, or a build that fails when they differ.
8. **Derive from the authoritative schema.** A type, table, or list written by hand beside a file that already owns the shape is a second owner.
9. **Keep one way to do one task.** A new way beside an old one that still works gains callers on both sides; migrate every caller and delete the old way in the same change, unless outside users depend on it.
10. **Treat one rule applied two ways as two owners,** even when neither copy is wrong yet.

**The test:** For each changed fact, can you list every place that states or should state it, and does each one say the new fact?

**You skipped this when** the review read only the diff hunks, or searched only the new name and never the old one.

Distinct from `blast-radius.md`, which follows what consumes the fact; this one follows what states it.
