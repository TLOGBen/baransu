# diagrams — the progressive state-diagram series

Every hypothesis gets a series of static state diagrams, drawn by `$baransu:draw` (`../../draw/SKILL.md`) and listed on one page, `diagrams.html`, opened for the user after every publish (`pwsh.exe Start-Process` or `wslview` on WSL2, `Start-Process` on Windows, `xdg-open` on Linux, `open` on macOS). Its job is understanding: a person who never met formal methods can say each bug path in one sentence after reading it.

## Hand the series to $baransu:draw

Invoke `$baransu:draw` once for the whole series, with:

- `--out .codex/hypothesis/<area>/diagrams/` — the figures live inside the hypothesis, so their hashes are part of it;
- `--quick` and the words 「一個 seed 直出，不用細修」 — one seed, promoted without a judge, no critique loop (the user's decision, 2026-10-24); `$baransu:draw` checks its ledger with `--upto critique-loop`;
- `--lane diagram`, type **State Machine** (`../../draw/references/diagram/type-state.md`), one piece per diagram, named `d1-<slug>.html`, `d2-<slug>.html`, …;
- a brief that states the four conditions below, the states, steps and guards of each diagram in the source's words, and each numbered path with its steps.

`$baransu:draw` never sees the model files and decides nothing about the hypothesis; the brief is its whole input. When it reports done and its ledger check passes, keep in `diagrams/` only the figure files (`d<n>-<slug>.html`) and `docs/brief.md`, which is what a redraw needs; remove the rest of `$baransu:draw`'s working files (`scratch/`, `shots/`, its other `docs/`, generator scripts). They belong to the drawing, not to the hypothesis, and every file kept is hashed on each publish. (The first run kept them all: 116 files, 4 MB, against 6 files and 64 KB after.) When `$baransu:draw` cannot run (its preflight fails), the series is drawn as Mermaid `stateDiagram-v2` blocks in `diagrams.html` instead, and the README says so.

## The four conditions

Each is a yes/no check on what `$baransu:draw` returns, before publish:

1. Diagram 1 is the happy path only, with at most 7 states.
2. Each next diagram redraws the previous one and adds exactly one part — an actor, a branch, a retry, a concurrent writer — and says which in one sentence.
3. The last diagram numbers every path `P1…Pn`, with the same ids as `paths/`.
4. No label is a variable or action name; every label uses the source's own user-facing words.

A figure that fails one is fixed in the brief and drawn again; it is never published as is.

## Ordering the parts

Add parts in the order a reader needs them to see the first path: the parts that path crosses come before the parts it does not. A part that no path crosses may be left out of the series and named in the scope section.

## Labels

- A state is a condition the reader can observe or cares about: 「簽核中」, 「已付款」, 「付款中，但扣了兩次」. When the reader must see something a label would hide, put it in the label.
- A step is the event that moves the system, in the reader's words: 「主管按核准」, 「背景工作重試」, 「網路斷線」. A step that only reads, and so leaves the label the same, is drawn when a path depends on it; split the state to show it.
- A guard is written in brackets in plain words: 「[金額 ≥ 1000]」.
- A path's broken state is marked and labelled with its path number; the legend says what the mark means.

## The page

`diagrams.html`, from `templates/diagrams.html`, is the index: the rules in plain sentences, then each figure in order (an `<iframe>` of `diagrams/d<n>-<slug>.html` with its one-sentence caption), then the paths and the scope. It names the generation and sync point it was drawn from and points at the status command; it never shows a live verdict of its own. Open it in the user's default browser (or through a local HTTP server): a viewer that snapshots the file as `data:` cannot load the relative `<iframe>`s and shows them blank.

## Documents

The same conditions. Labels use the document's terms. Contradictions, gaps and comparison breaks are numbered paths like bugs. Ambiguities are listed under the last figure as questions with whom to ask, never drawn as edges.
