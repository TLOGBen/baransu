# sources — what a hypothesis can be written from

Four inputs, one artifact. Each source kind is an adapter that yields the same four things: the coverage set (what `sync.files` hashes), citations in its own form, the watch patterns (or none), and the rule candidates for the user to confirm.

## Code

(unimplemented) — Read the entry points and trace control flow before grepping names; map the guarded state first, then every writer of it (the watch patterns come from this map). Citations are `file:line`. Coverage = the files cited. One indivisible step in the code (one transaction, one CAS, one synchronous block) = one model step.

## Symptom (from `/hunt`)

(unimplemented) — `--symptom "<text>" <path>`: the code adapter, with the symptom as the first candidate rule's negation; the resulting paths are handed back to hunt as probes (`templates/path.md` § 給讀者的探針). A model pass is reported as "no such path within scope", never as "the symptom cannot happen".

## One document

(unimplemented) — Convert with `/read --save` (PDF, docx, …) into `.claude/read/`; hash the original file. Extract actors, states, steps, rules; every extracted item carries its quote and location (file, section, page or line) and is ticked by the user one by one. What the document leaves unclear becomes a `questions[]` entry with whom to ask — never filled in. Outputs: contradiction (two rules cannot both hold, with the path that collides them), gap (a state with no exit, or a situation with no stated handling), ambiguity (question).

## Two documents (`--satisfies`)

(unimplemented) — `<behaviour-doc> --satisfies <rules-doc>`: the rules document is the specification, the behaviour document the implementation; refinement check — every behaviour step maps to a step the rules allow, and every rules-goal is still reachable. A break is a `refinement-break` path citing both documents. Both originals are in `sync.files`; either changing makes the area stale.

## What a document hypothesis claims

(unimplemented) — It checks the documents, not the system: the README's 一句話 says so, and readers' tables treat a document area like any other (it covers document paths, not code paths).
