# page — the diagram series a person reads before they trust the verdict

(unimplemented) Intent: derived from the model and the README, rebuilt whenever either is; never edited by hand.

## The series

(unimplemented) The four conditions, each checkable by reading the page:
1. Diagram 1 is the happy path only, at most seven states.
2. Each next diagram adds exactly one part (a role, a branch, a retry, a concurrent actor) and names it in its caption.
3. The last diagram numbers each bug path (P1, P2 …) on the edges it takes, matching README `findings`.
4. No label is a variable or action name; labels are the source's words.

## Labels

(unimplemented) Adapted from pstack `statechart`: states are nouns a user would say, edges are what a person does or what happens; guards in plain words; one label per thing across all diagrams.

## For documents

(unimplemented) Same series; contradiction paths and gap states are marked like bug paths; each ambiguity is shown as a forked edge with its question beside it, so the page can be used in a meeting as is.

## Page structure

(unimplemented) See `templates/page.html`. One file, Mermaid pinned by version, every diagram followed by its text form so the page still reads when the script cannot load.

## Open it

(unimplemented) As `/show-me` does: the environment's opener (`wslview` or `pwsh.exe Start-Process` on WSL2, `Start-Process` on Windows, `xdg-open`, `open`); print the path only when no opener exists.
