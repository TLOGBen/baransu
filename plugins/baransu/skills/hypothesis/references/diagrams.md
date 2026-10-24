# diagrams — the progressive state-diagram series

Every hypothesis gets a series of static state diagrams on one page, `diagrams.html`, opened for the user after every publish (`pwsh.exe Start-Process` or `wslview` on WSL2, `Start-Process` on Windows, `xdg-open` on Linux, `open` on macOS). Its job is understanding: a person who never met formal methods can say each bug path in one sentence after reading it. At this stage a diagram is for reading the rules, not a finished figure, so it is text that changes with the model.

## Write the series as Mermaid

Each diagram is one Mermaid `stateDiagram-v2` block in `diagrams.html` (`templates/diagrams.html` loads a pinned Mermaid). Mermaid's own grammar sets three habits:

- name a state with words as `state "主管已核准" as approved` and use the short id in transitions;
- keep `;` out of every label — Mermaid reads it as the end of a statement and scatters the rest as stray nodes — and keep a transition's label free of a second `:`, which is the label separator;
- mark a path's broken state with a `classDef` (for example `classDef bad stroke:#b42318`) and name it in the legend.

Before publish, open the page in a browser and check that every block drew: no 「Syntax error」, no stray nodes outside the diagram. A figure polished for a presentation is `/baransu:draw`'s, asked for by hand; it is not part of a hypothesis.

## The four conditions

Each is a yes/no check on the series, before publish:

1. Diagram 1 is the happy path only, with at most 7 states.
2. Each next diagram redraws the previous one and adds exactly one part — an actor, a branch, a retry, a concurrent writer — and says which in one sentence.
3. The last diagram numbers every path `P1…Pn`, with the same ids as `paths/`.
4. No label is a variable or action name; every label uses the source's own user-facing words.

A diagram that fails one is rewritten; it is never published as is.

## Ordering the parts

Add parts in the order a reader needs them to see the first path: the parts that path crosses come before the parts it does not. A part that no path crosses may be left out of the series and named in the scope section.

## Labels

- A state is a condition the reader can observe or cares about: 「簽核中」, 「已付款」, 「付款中，但扣了兩次」. When the reader must see something a label would hide, put it in the label.
- A step is the event that moves the system, in the reader's words: 「主管按核准」, 「背景工作重試」, 「網路斷線」. A step that only reads, and so leaves the label the same, is drawn when a path depends on it; split the state to show it.
- A guard is written in brackets in plain words: 「[金額 ≥ 1000]」.
- A path's broken state is marked and labelled with its path number; the legend says what the mark means.

## The page

`diagrams.html`, from `templates/diagrams.html`, is the index: the rules in plain sentences, then each diagram in order (its Mermaid block with its one-sentence caption), then the paths and the scope. It names the generation and sync point it was drawn from and points at the status command; it never shows a live verdict of its own. Open it in the user's default browser; Mermaid draws in the page, so no server is needed.

## Documents

The same conditions. Labels use the document's terms. Contradictions, gaps and comparison breaks are numbered paths like bugs. Ambiguities are listed under the last figure as questions with whom to ask, never drawn as edges.
