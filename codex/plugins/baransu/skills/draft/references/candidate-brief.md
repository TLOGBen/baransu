# candidate-brief — what each designer receives and returns

Each designer works alone: it receives this brief and nothing about the other candidates or the session's preference. The brief carries the goal, the grounding by path, the constraints every shape must honour, the principle files (`../../review/references/principles/structure.md`, `taste.md`, `readability.md`), the designer's pull, and its output location.

## What the designer is told

You are one of several designers drawing the shape of the same change. Draw the best shape you can under your pull; do not hedge toward what another designer might draw. The differences between candidates are what the choice is made from, and a safe middle defeats it.

- **Usage first.** Write two or three real call sites, in the repo's own code, before any type. The usage is the specification; the types are derived from it, and where they disagree the types change.
- **Data structures first among the types.** Trace each main way the data is read or written through the structure. An answer of "we will add an index or a cache later" means the structure is wrong.
- **Depth.** Keep the interface small and pull complexity into the callee. No transport or wire types on the interface: external data is parsed into domain types behind it.
- **State.** If two actors might write the same state, ask what happens; unless the answer is "nothing", give each its own and merge where it is read.
- **Visible boundaries.** Bodies raise the not-implemented error; tricky logic is pseudocode in comments; doc comments state intent and invariants.
- **Invariants in types** before checks, and checks before prose.
- **Short call chains.** Following one flow should not take more than three files.
- **Every step twice.** For each operation, ask what happens if it runs twice or stops halfway.

## What the designer returns

At its output location:

1. The usage: the call sites.
2. The sketch: types, signatures, module map, unimplemented bodies.
3. For each seam: what hides behind it, what varies across it, and its adapters.
4. Who owns each piece of state.
5. The trade-offs, each as 「我們接受 X，換到 Y」, and the alternatives it considered and dropped.
6. The ways this shape can fail — the traps its working-out found.
