# Structure

Put a boundary exactly where things change for different reasons, and nowhere else. Single responsibility, the dependency rule of Clean Architecture, ports and adapters, use cases and facades, and the advice against speculative layers are this one rule at different scales.

**Why:** A seam that separates two reasons to change earns its keep: each side changes alone. A seam with nothing varying across it is cost — one more layer to trace, one more place for a rule to drift — and a missing seam makes one change edit many modules.

**Pattern:**
1. **Ask whether it would look like this if the requirement had been known from the start.** A change bolted onto the old shape — a special case threaded through an existing flow, a flag beside a branch, a workaround that needs a paragraph to explain — fails to hold with the shape the requirement implies. Name that shape.
2. **Give each module one reason to change.** A module edited for several unrelated reasons splits by job; one logical change that forces edits across many modules gathers into one.
3. **Point dependencies toward policy.** Business rules do not import frameworks, storage, or transport; an outer layer reaches the core through a use case or facade that speaks the domain's terms.
4. **Ask a port for two adapters.** A seam is real when something actually varies across it — production and a test double, two providers. One adapter is a hypothetical seam: inline it.
5. **Prefer deep modules.** A small interface over substantial behaviour, judged by everything a caller must know: signatures, invariants, ordering, errors. Apply the deletion test: if deleting a module makes complexity vanish, it was a pass-through; if complexity reappears across its callers, it was earning its keep.
6. **Give each piece of state one owner.** Two modules writing the same state, or each keeping its own copy, diverge.
7. **Stop leakage at the interface.** Parse external data into domain types behind the interface; keep storage, framework, and protocol details private. A representation several modules depend on is one decision spread across them, and internals reachable from outside become the interface.
8. **Follow the repo's existing structure.** Its layers, interfaces, and conventions bind new code; deviating needs a reason and a migration, not a preference.
9. **Be ambitious in deleting, never in adding.** A restructure that removes more moving parts than it adds is in scope; one that adds layers for flexibility nobody needs is not. Premature abstraction is worse than duplication.
10. **Name the cost, not the preference.** "I would have done it differently" is not a finding; a structural finding names what the current shape fails to hold with now.

**The test:** For each boundary the change adds or crosses: what varies across it, and would deleting it make complexity vanish or reappear?

**You skipped this when** an interface has one implementation "for later", or one feature's edits are spread across several layers that each only pass the call on.
