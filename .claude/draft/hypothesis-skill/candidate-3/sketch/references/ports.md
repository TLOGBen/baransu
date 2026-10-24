# ports — the two seams and the forms that cross them

(unimplemented) Intent: the only file both sides of each seam read. The core (SKILL.md steps 1–9) speaks these forms; an adapter takes them in or hands them back. A field not listed here does not cross a seam.

## The source port

(unimplemented) Every file under `sources/` has exactly these sections, in this order; a missing section is a broken adapter.

| Section | The adapter answers | Hands back |
|---|---|---|
| Recognize | Is this argument mine? | yes / no, and the normalized source reference |
| Read | How is it read into text the citations point at? | readable text, plus the snapshot to keep, if any |
| Cite | What does one citation look like, and how is it checked to resolve? | citation form; `resolves(citation) → bool` as a procedure |
| Extract | What is a step, an actor, a state, an indivisible step, in this kind? | a filled claim sheet |
| Sync point | What fixes the version the hypothesis describes? | the `sources[]` entry fields for the README |
| Stale | When is the source past its sync point? | the rule, mirrored as one function in `scripts/hypothesis-status.py` |
| Mutate | What is a broken variant of this source, per safety rule? | mutation records |
| Replay | Can the source take every step of a trace? | finding (in this kind's vocabulary) or model-wrong, per trace |
| Findings vocabulary | What a finding is called and how it is told | names and the telling form |
| Diff since sync | What changed since the sync point? | change list for `references/maintain.md` |

## The tool port

(unimplemented) Every file under `tools/` has exactly these sections, in this order.

| Section | The adapter answers | Hands back |
|---|---|---|
| Capability | Which claim shapes, languages, bound kinds; how to tell it is installed | capability record |
| Pin | How the version is read and written down | `tool.version` |
| Encode | How the claim sheet becomes model files; how a citation is written into the model | files under `model/`, coverage-map rows |
| Safety | How a "must never" rule is stated | — |
| Reachability | How "seen succeeding" is shown: goal reachable, and unreachable once one transition is removed | gate-3 evidence |
| Realize a mutation | How a mutation record becomes a run that must fail | gate-2 evidence |
| Run | The one command; where its scratch output goes (never under the artifact) | `tool.command`, `tool.cwd` |
| Read the result | Output → per-rule result, normalized traces, size of space explored | results |
| Bounds | How the scope is stated, and what changes with `--unbounded` | `tool.bounds` |

## Claim sheet

(unimplemented) The source-neutral intermediate between Extract and Encode. Fields:
- `actors[]` — name in the source's words
- `states[]` — name, citation
- `steps[]` — id, actor, from/to or effect, guard, citation(s), `atomic: yes | no (reason)`
- `rules[]` — id (`R*` safety, `G*` goal, `F*` refinement), plain sentence, kind, citations, paired goal for each safety rule
- `left_out[]` — part, reason class (→ reason record)
- `questions[]` — ambiguity: the passage, the two readings, who can answer
- `glossary[]` — model name → plain label (the page uses only plain labels)
- `shape` — `transition-system` | `every-input`

## Coverage map row

(unimplemented) `model element` → `claim-sheet item` → `citation`. One row per action, variable, constant bound, and property. A model element with no row fails gate 1.

## Mutation record

(unimplemented) `rule`, `citation` of the place broken, `what changed` in the source's words, `how realized` (tool side), `caught: yes | no`. Made by the source adapter, realized by the tool adapter; never applied to the person's working tree.

## Trace

(unimplemented) Normalized counterexample. Two shapes, both carry citations through the coverage map:
- `path` — ordered `(step id, state summary in glossary labels)`; from a transition-system tool
- `witness` — `(input assignment, failing check citation, call path)`; from an every-input tool

## Verdict values

(unimplemented) Per rule: `holds` | `violated` | `vacuous` (goal not reachable, or still reachable with a transition removed) | `not-run`. Per hypothesis (README `status`): `proved` | `disproved` | `draft` | `unformalizable`. Derived, never stored: `stale`, `legacy`.

## Writing the artifact

(unimplemented) Build in `.claude/hypothesis/.staging/<area>-<run-id>/`; swap into place only at step 8, after comparing the on-disk README's `revision` with the one read at start. Readers ignore `.staging/`.

## Admitting an adapter

(unimplemented) A new adapter ships only after it passes the known-answer exam for its kind — source: the approval exam rewritten in that kind; tool: naive / fixed / lazy variants of one small subject in its language — kept in `evals/`. Until admitted, a run that needs it ends `unformalizable`, reason class 沒有工具, detail "adapter not admitted".
