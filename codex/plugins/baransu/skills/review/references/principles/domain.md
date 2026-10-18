# Domain

Code that encodes a business domain holds with that domain: it uses the domain's words for the domain's concepts, keeps each concept's rules in the one place that owns them, makes states the business cannot reach impossible to write, and states its behaviour as examples the business would recognise.

**Why:** A structure that matches the domain deletes branches and makes invalid states unrepresentable; scattered conditionals let every new feature add one more case and one more chance to disagree. Choosing the model at write time is cheap; recovering it later reads as a refactor and gets deferred.

**Pattern:**
1. **Use the domain's own words.** A term in the code, a test name, or a message that conflicts with the project's glossary or with how the request uses it fails to hold. One concept under two names, or one name for two concepts, is the root.
2. **Change the model where the meaning changes.** A bounded context ends where a term's meaning shifts; one model stretched across two contexts disagrees with one of them. Contexts meet through explicit translation, not shared internals.
3. **Let the aggregate guard its invariant.** A rule that must always hold is enforced by the one module that owns that state; a second writer, or a caller that has to remember the rule, splits it.
4. **Keep entities and values apart.** A thing with identity across changes is an entity; a thing defined only by its attributes is a value, immutable and compared by value.
5. **Model it, do not branch on it.** A state machine instead of scattered booleans and phase checks; a typed model instead of a loose map; a lookup, union, or registry instead of an if/else chain that grows one branch per feature.
6. **Organise by knowledge, not by step.** Modules named load, validate, transform, save repeat one domain's rules across every step; a module owns a body of domain knowledge.
7. **State behaviour as Given / When / Then.** A scenario names a state (Given), an event (When), and the outcome the business observes (Then), in the domain's words, from the user's side, one behaviour each, declarative — what happens, not which buttons are clicked. The agreed examples are the specification: a test or spec whose steps read as implementation, or whose Then asserts internals instead of the outcome, fails to hold with the behaviour it names.
8. **Make every Given reachable, and cover the table.** A scenario's Given is reachable from a legal start through legal transitions, judged against a transition table from the spec or upstream state-producing paths — never from the code under test; a case no legal path reaches is 「非自然情境」, and a human decides whether it stays. Legal state × event combinations no scenario covers are listed against the table's rows.
9. **Cite the domain source.** A domain finding cites the glossary, spec, or transition-table row it rests on and the code or case location; without a source for the rule, raise the question instead of guessing it.
10. **Respect recorded decisions.** An ADR or plan is a place; a change that contradicts one surfaces it only when the friction is real enough to reopen it.

**The test:** Could a domain expert read the names, the states, and the scenarios and recognise their business — and is there any state the code allows that the business cannot reach?

**You skipped this when** a new feature grew an existing if/else chain by one branch, a second boolean must stay in sync with the first, or a scenario's Then checks a field instead of an outcome.
