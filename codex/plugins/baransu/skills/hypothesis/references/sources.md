# sources — what a hypothesis can be written from

Several inputs, one artifact. A design question (`../SKILL.md` §2) has its own procedure in `design.md`; the design it chooses is then read through one of the adapters below — the code when it is what the code already does, § A sketch otherwise. Each source kind is an adapter that yields the same four things: the coverage set (what `sync.files` hashes), citations in its own form, the watch patterns (or none), and the rule candidates for the user to confirm.

## Code

Read the entry points and trace control flow before grepping names; map the guarded state first, then every writer of it (the watch patterns come from this map). Citations are `file:line`. Coverage = the files cited. What the model takes as one step is one indivisible step in the code as it runs — inside one transaction, one held lock, or one atomic primitive of the runtime; a check and a write in separate statements are two steps, whatever a comment or a function's name says.

## Symptom (from `$baransu:hunt`)

A `HUNT-YYYY-NNN` id (its case file names the code) or a failure sentence plus a path: the code adapter, with the symptom as the first candidate rule's negation; the resulting paths are handed back to hunt as probes (`templates/path.md` § 給讀者的探針). A model pass is reported as "no such path within scope", never as "the symptom cannot happen".

## Sources that move

A source the area cannot rely on staying where it is — a page read from a URL, a file under a working dir `$baransu:ship` archives (`.codex/think/`, `.codex/draft/`, any dir in its archive allowlist), a file as it was at an earlier commit, or a working record that keeps growing — is copied into the area's `sources/`, and the copy is what is cited and hashed.

Whether the copy follows its original is decided by one question: does the hypothesis claim something about the original's current content, or about the content at one moment, kept as evidence? A plan or a spec the area checks is current content: `sync.originals` maps the copy to it, and the status script reports the area `stale` when the original still exists and differs from the copy. A past commit (§ A past commit) or a record cited for what it showed then is a moment: no `sync.originals` entry, so a later edit of the original is not a change of this source — mapping it would leave the area stale from the moment it is published. A URL has no local original: its README marks 「來源可能已變」, and every `--maintain` run fetches it again and compares; between runs nothing notices an edit to the page.

## A past commit

Code as it was at a commit is read with `git show <sha>:<path>` and copied to `sources/<sha>/<path>`; that copy is cited and hashed, with no `sync.originals` entry. The commit is named in the README and in `roles`.

## A sketch (from `$baransu:draft`)

A design-time hypothesis models the sketch's declared contract — its types, signatures, doc comments and pseudocode — not code that runs. A step is indivisible when the sketch declares it so (a transaction, a lock, a compare-and-swap in a signature or an invariant comment); a step the sketch leaves open is a question for the person who chose the shape, run every reading per `formal.md` § Strict, 1. Seen failing breaks the model's copy of a declared guard, since there is no code to break. Nothing is handed to `$baransu:prove-it`: nothing runs yet. Filling the bodies makes it stale, and `--maintain` redraws the model from the real code.

## One document

Convert with `$baransu:read --save` (PDF, docx, …) into `.codex/read/`; cite and hash the original file a person edits, not the conversion. Extract actors, states, steps, rules; every extracted item carries its quote and location (file, section, page or line) and is ticked by the user one by one. What the document leaves unclear becomes a `questions[]` entry with whom to ask — never filled in. Outputs: contradiction (two rules cannot both hold, with the path that collides them), gap (a state with no exit, or a situation with no stated handling), ambiguity (question). A document read from a URL is a source that moves (§ Sources that move).

## Two sources (`--satisfies`)

`<behaviour> --satisfies <rules>`: either side may be a document or code (「程式有沒有滿足 SA」 is the code adapter on the left, the document adapter on the right). The flag turns on from the wording per `../../_shared/auto-flags.md` — 「A 是否滿足 B」「A 有沒有符合 B」「A 涵蓋 B 嗎」 read A as the behaviour and B as the rules — and the first status line states the roles so the user can swap them. The rules side is the specification, the behaviour side the implementation; refinement check — every behaviour step maps to a step the rules allow, and every rules-goal is still reachable. A break is a `refinement-break` path citing both documents. A rules-side goal the behaviour side cannot reach is a break too, recorded as a rule of kind `goal`, verdict `violated` — unless the rules side contradicts that goal itself: then the behaviour side has followed the other reading, which is reported as a note naming the contradiction it resolved and which way, a question for whoever owns the rules, never a rule or a break of the behaviour. Check the rules side's own contradictions before scoring any goal. Both originals are in `sync.files`; either changing makes the area stale.

**Code against code** — a refactor checked against the commit before it — needs the behaviour of each side, not one side's rules, so it is compared, not mapped:

1. **Two models, drawn blind.** Each side is modelled by its own agent, given only that side's source (the past one from `sources/<sha>/`), the scope and the rules — never the other side, never how to abstract. Each model lives under `model/<role>/` and passes all three evidence gates on its own.
2. **Compare what a user can observe, both ways, at small bounds.** Project every state of each model onto the variables a user sees (stored data, each process's view, each operation's outcome) and compare the reachable projected states and projected changes in both directions — the tool's full state graph (TLC `-dump dot`) makes this a set comparison. Small bounds keep that graph small: split them so each kind of contention is exercised once (two processes of one thread, one process of two threads) and say so.
3. **Every difference goes back to the source.** A difference is a modelling error on one side or a change in behaviour; read both sources to decide which. A modelling error is fixed from its source and the comparison runs again; a change in behaviour is a finding — the comparison rule below is 被打破, with the difference as its path — never smoothed away by editing a model. Equal behaviour is claimed only once the comparison shows no difference, and only within the bounds compared, which the README names: a difference that needs more copies than the bounds hold is not seen.
4. **Record the comparison as a rule.** 「兩邊使用者看得到的變化一樣」 is a safety rule of the area; the differences seen before the models were fixed, or a variant of one side, are its seen-failing evidence. The other rules are each side's own, checked at the full bounds as part of that side's gates in step 1, before the comparison.
5. **Say what was not compared.** Liveness rules are reported per side under each side's own fairness assumptions, each cited from its own source (`formal.md` § Strict, 1), since the two sides may justify them differently. A platform or environment only the new code runs on has no old behaviour to compare against: list it in `left_out`.

## What a document hypothesis claims

It checks the documents, not the system: the README's 一句話 says so, and readers' tables treat a document area like any other (it covers document paths, not code paths).
