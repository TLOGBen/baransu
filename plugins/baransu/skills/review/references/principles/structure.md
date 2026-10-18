# Structure — boundaries where reasons to change differ, nowhere else

**Bedrock.** Put a boundary exactly where things change for different reasons, and nowhere else. Single responsibility, the dependency rule of Clean Architecture, ports and adapters, use cases and facades, and the advice against speculative layers are this one rule at different scales: a seam that separates two reasons to change earns its keep; a seam with nothing varying across it is cost.

1. **Would it look like this if the requirement had been known from the start?** A change bolted onto the old shape — a special case threaded through an existing flow, a flag beside a branch, a workaround needing a paragraph to explain — disagrees with the shape the requirement implies. Name that shape.
2. **One reason to change per module.** A module edited for several unrelated reasons should split by job; one logical change that forces edits across many modules should gather into one.
3. **Dependencies point toward policy.** Business rules do not import frameworks, storage, or transport; an outer layer reaches the core through a use case or facade that speaks the domain's terms.
4. **A port needs two adapters.** A seam is real when something actually varies across it — production and a test double, two providers. One adapter means a hypothetical seam: inline it.
5. **Deep modules.** A small interface over substantial behaviour, judged by what a caller must know: signatures, invariants, ordering, errors. A pass-through method, a wrapper with one caller, or a layer repeating the same methods adds a seam without hiding anything — the deletion test: if deleting it makes complexity vanish, it was a pass-through.
6. **One owner per piece of state.** Two modules writing the same state, or each keeping its copy, diverge.
7. **No leakage.** A representation, policy, or wire type that several modules depend on is one decision spread across them; parse external data into domain types behind the interface and keep storage, framework, and protocol details private. Internals reachable from outside become the interface.
8. **Follow the repo's existing structure.** Its layers, interfaces, and conventions bind new code; deviating needs a reason and a migration, not a preference.
9. **Ambitious in deleting, never in adding.** A restructure that removes more moving parts than it adds is in scope; one that adds layers for flexibility nobody needs is not. Premature abstraction is worse than duplication.
10. **"I would have done it differently" is not a finding.** A structural finding names the concrete cost of the current shape — a disagreement it causes now — not a preferred alternative.
