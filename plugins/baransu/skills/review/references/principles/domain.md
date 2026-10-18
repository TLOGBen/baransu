# Domain — the domain's language and invariants, made structural

**Bedrock.** Code that encodes a business domain agrees with that domain: it uses the domain's words for the domain's concepts, keeps each concept's rules in the one place that owns them, and makes states the business cannot reach impossible to write rather than checked after the fact.

1. **The domain's own words.** A term in the code, a test name, or a message that conflicts with the project's glossary or with how the request uses it is a disagreement. One concept under two names, or one name for two concepts, is the root.
2. **Bounded contexts.** Where the meaning of a term changes, the model changes; one model stretched across two contexts disagrees with one of them. Contexts meet through explicit translation, not shared internals.
3. **Aggregates guard invariants.** A rule that must always hold is enforced by the one module that owns that state; a second writer, or a caller that has to remember the rule, splits it.
4. **Entities and values.** A thing with identity across changes is an entity; a thing defined only by its attributes is a value, immutable and compared by value. Mixing them leaks identity bugs.
5. **Model it, not branch on it.** A state machine instead of scattered booleans and phase checks; a typed model instead of a loose map; a lookup, union, or registry instead of an if/else chain that grows one branch per feature. A second boolean that must stay in sync with the first is the sign.
6. **Organise by knowledge, not by step.** Modules named load / validate / transform / save repeat one domain's rules across every step; a module owns a body of domain knowledge.
7. **Business-state reachability.** For a claimed scenario or test case, its initial state is reachable from a legal start through legal transitions, judged against a transition table from the spec or upstream state-producing paths — never from the code under test. A case no legal path reaches is 「非自然情境」, and a human decides whether it stays.
8. **Coverage of the transition table.** Legal state × event combinations the cases do not cover are listed against the table's rows.
9. **Cite twice.** A domain finding cites the glossary, spec, or transition-table row it rests on and the code or case location; without a source for the domain rule, report the question instead of guessing it.
10. **Decisions already recorded** in an ADR or plan are places too; a change that contradicts one surfaces it only when the friction is real enough to reopen it.
