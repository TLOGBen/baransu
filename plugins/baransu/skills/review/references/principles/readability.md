# Readability — what a reader must trace and hold

**Bedrock.** Maintainability is the work a reader must do to understand the code: the layers to trace between a question and its answer, and the state to hold in mind while tracing. A change is readable when a new reader can answer "where does X come from?" and "what can change X?" quickly.

1. **Count layers to trace.** Each indirection between the question and the answer must compress something; a wrapper, adapter, or helper that only forwards adds a layer without saving one.
2. **Count state to hold.** Prefer returned values over mutation, locals over fields, fields over module state, module state over globals; derive a value instead of keeping two copies in sync.
3. **Name the invariant once, at the boundary,** not in every consumer, so the reader learns it in one place.
4. **Names say what a thing is or holds,** in the domain's words and the codebase's own vocabulary. A name that needs a comment to decode is the finding; if no honest name comes, the design is murky.
5. **Comments carry only the why the code cannot show.** A comment narrating what the code does, a stale comment, or a workaround explained at paragraph length points at code that should change instead.
6. **Split by job, not by length.** A function doing several unrelated jobs is hard to read and test; helpers that exist only to make a function shorter add layers.
7. **Ad-hoc branches tangle a flow.** A special case inserted into an unrelated path, or a feature check scattered across shared code, makes every later reader carry it.
8. **Prose follows the same rule.** Docs, messages, and comments use the short everyday word, the real symbol name, one name per thing, and one reading per sentence.
9. **Before adding a layer or a piece of state,** ask whether it reduces reader load elsewhere by at least as much.
