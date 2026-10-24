# sources — what changes when the input is code, a symptom, a document, or two documents

(unimplemented) One adapter per input kind. Each answers the same five questions so SKILL.md §2–§7 never branch on the kind: how the source is read, how a citation is written, what a step is, what kinds of finding exist, and which files go into `covers`. Everything downstream — the README contract, `status`, `check`, the page — is the same for every kind.

## Code

(unimplemented)
- Read: entry points first, then control flow, then the data each step writes.
- Cite: `path:line` or `path:line-line`.
- Step: what the code does without yielding (one statement, one transaction, one lock-held block).
- Findings: `bug` — a counterexample every step of which the code can take.
- Covers: every file a map row cites.

## Symptom

(unimplemented)
- Read: the hunt case file's observed symptoms and located files (or the user's sentence), then proceed as Code on those files.
- Rules: derived from the symptom's wrong result, stated as what must never happen; the symptom is quoted in README §Claim.
- Findings: as Code; a path that reproduces the observed symptom is marked as such so `/hunt` can probe it first.
- A model that passes is reported as "the modelled part does not explain the symptom", never as "no bug".

## Document

(unimplemented)
- Read: through `/read --save`; cite the original, not the converted copy.
- Cite: the passage quoted, plus file, section, and page or line.
- Step: what the document describes as one act by one role; an order the document does not state is an ambiguity, not a choice.
- Findings: `contradiction` (two rules that cannot both hold, with the walk where they collide), `gap` (a state with no way out, or a case the document does not say how to handle), `ambiguity` (a question and who should answer it).
- Covers: the original files; their sync point is the content hash, with the document's own version label kept beside it. A URL source is covered through its immutable `raw/` copy and marked "upstream may have moved" in README §範圍與假設; `--maintain` refetches it and compares.

## Comparison

(unimplemented)
- Order: upstream is rules, downstream is behaviour — RFP, requirement interview or meeting notes → SA → SD; ask only when the two are at the same level or unlabeled.
- Model: the rules document as the spec, the behaviour document as the implementation, and a refinement mapping between their states written as its own map rows, each side cited.
- Findings: `refinement` — a behaviour the downstream document allows that the upstream rules forbid, with the walk; plus each document's own contradictions, gaps and ambiguities.
- Covers: both originals.
