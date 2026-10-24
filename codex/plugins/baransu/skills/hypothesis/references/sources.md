# sources — what a hypothesis can be written from

Four inputs, one artifact. Each source kind is an adapter that yields the same four things: the coverage set (what `sync.files` hashes), citations in its own form, the watch patterns (or none), and the rule candidates for the user to confirm.

## Code

Read the entry points and trace control flow before grepping names; map the guarded state first, then every writer of it (the watch patterns come from this map). Citations are `file:line`. Coverage = the files cited. What the model takes as one step is one indivisible step in the code as it runs — inside one transaction, one held lock, or one atomic primitive of the runtime; a check and a write in separate statements are two steps, whatever a comment or a function's name says.

## Symptom (from `$baransu:hunt`)

A `HUNT-YYYY-NNN` id (its case file names the code) or a failure sentence plus a path: the code adapter, with the symptom as the first candidate rule's negation; the resulting paths are handed back to hunt as probes (`templates/path.md` § 給讀者的探針). A model pass is reported as "no such path within scope", never as "the symptom cannot happen".

## One document

Convert with `$baransu:read --save` (PDF, docx, …) into `.codex/read/`; cite and hash the original file a person edits, not the conversion. Extract actors, states, steps, rules; every extracted item carries its quote and location (file, section, page or line) and is ticked by the user one by one. What the document leaves unclear becomes a `questions[]` entry with whom to ask — never filled in. Outputs: contradiction (two rules cannot both hold, with the path that collides them), gap (a state with no exit, or a situation with no stated handling), ambiguity (question). A document read from a URL is cited from its saved copy, which never changes; its README marks 「上游可能已變」 and every `--maintain` fetches it again and compares, so an edited web page cannot stay "in sync" forever.

## Two sources (`--satisfies`)

`<behaviour> --satisfies <rules>`: either side may be a document or code (「程式有沒有滿足 SA」 is the code adapter on the left, the document adapter on the right). The flag turns on from the wording per `../../_shared/auto-flags.md` — 「A 是否滿足 B」「A 有沒有符合 B」「A 涵蓋 B 嗎」 read A as the behaviour and B as the rules — and the first status line states the roles so the user can swap them. The rules side is the specification, the behaviour side the implementation; refinement check — every behaviour step maps to a step the rules allow, and every rules-goal is still reachable. A break is a `refinement-break` path citing both documents. A rules-side goal the behaviour side cannot reach is a break too, recorded as a rule of kind `goal`, verdict `violated` — unless the rules side contradicts that goal itself: then the behaviour side has followed the other reading, which is reported as a note naming the contradiction it resolved and which way, a question for whoever owns the rules, never a rule or a break of the behaviour. Check the rules side's own contradictions before scoring any goal. Both originals are in `sync.files`; either changing makes the area stale.

## What a document hypothesis claims

It checks the documents, not the system: the README's 一句話 says so, and readers' tables treat a document area like any other (it covers document paths, not code paths).
