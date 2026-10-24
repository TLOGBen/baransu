# diagrams — the progressive state-diagram page

One HTML page per hypothesis, `diagrams.html`, built from the model and opened for the user after every publish (`pwsh.exe Start-Process` or `wslview` on WSL2, `Start-Process` on Windows, `xdg-open` on Linux, `open` on macOS). Its job is understanding: a person who never met formal methods can say each bug path in one sentence after reading it.

## The four conditions

Each is a yes/no check before publish:

1. Diagram 1 is the happy path only, with at most 7 states.
2. Each next diagram redraws the previous one and adds exactly one part — an actor, a branch, a retry, a concurrent writer — and says which in one sentence above it.
3. The last diagram numbers every path `P1…Pn`, with the same ids as `paths/`.
4. No label is a variable or action name; every label uses the source's own user-facing words.

## Ordering the parts

Add parts in the order a reader needs them to see the first path: the parts that path crosses come before the parts it does not. A part that no path crosses may be left out of the series and named in the scope section.

## Labels

- A state is a condition the reader can observe or cares about: 「簽核中」, 「已付款」, 「付款中，但扣了兩次」. When the reader must see something a label would hide, put it in the label.
- A step is the event that moves the system, in the reader's words: 「主管按核准」, 「背景工作重試」, 「網路斷線」. A step that only reads, and so leaves the label the same, is drawn when a path depends on it; split the state to show it.
- A guard is written in brackets in plain words: 「[金額 ≥ 1000]」.
- A path's broken state uses one marked style and the path number in its label; the legend says what the mark means.

## Page

Start from `templates/diagrams.html`. Mermaid comes from one pinned CDN version; colours are tokens on `:root` with a dark mode; the page works at phone width with a 16px gutter. The page names the generation and sync point it was drawn from and points at the status command; it never shows a live verdict of its own.

## Documents

The same four conditions. Labels use the document's terms. Contradictions, gaps and comparison breaks are numbered paths like bugs. Ambiguities are listed under the last diagram as questions with whom to ask, never drawn as edges.
