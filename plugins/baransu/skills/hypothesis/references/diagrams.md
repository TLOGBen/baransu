# diagrams — the progressive state-diagram page

One HTML page per area, `diagrams.html`, built from the model, opened for the user after every publish the way `/show-me` opens its page (`wslview` or `pwsh.exe Start-Process` on WSL2, `xdg-open`, `open`).

## The four conditions

(unimplemented) — Checked before publish, each a yes/no:
1. Diagram 1 is the happy path only, ≤ 7 states.
2. Each next diagram adds exactly one part (an actor, a branch, a retry, a concurrent writer) and says which in one sentence.
3. The last diagram numbers every bug path `P1…Pn`, the same ids as `paths/`.
4. No label is a variable name or action name; labels are the source's user-facing words.

## Ordering the parts

(unimplemented) — Add parts in the order a reader needs them to see the first bug path: the parts a path crosses come before parts it does not.

## Labels

(unimplemented) — Naming rules for states and events (statechart conventions: states are conditions, events are what happened, guards in brackets in plain words).

## Page

(unimplemented) — Structure in `templates/diagrams.html`; Mermaid from one pinned CDN version with an `integrity` hash; tokens on `:root` with dark mode; works at phone width. The page states the generation and sync point it was drawn from and points at the status command; it never shows a live pass.

## Documents

(unimplemented) — Same four conditions; labels are the document's terms; contradiction, gap and refinement-break paths numbered alike; ambiguities listed under the last diagram as questions, not drawn as edges.
