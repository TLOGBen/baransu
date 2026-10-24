# diagrams — the page a person reads

(unimplemented) Intent: turn the claim sheet and the traces into one HTML page that lets the person say the bug path in one sentence. Reads only port forms (claim sheet, glossary, traces), so it does not change when a tool or a source kind is added.

## The four conditions

(unimplemented) Diagram 1 is the happy path only, at most 7 states; each next diagram adds exactly one part (an actor, a step group, an exit); bug paths are numbered on the last one; no label is a variable or action name — labels come from the glossary.

## Choosing the parts and their order

(unimplemented) The happy path is the goal rule's shortest trace; parts are added in the order the rules need them, the part a finding goes through last.

## Path traces and witness traces

(unimplemented) A `path` trace is drawn as numbered edges over the state diagram. A `witness` trace is drawn as the call path with the failing check and the input that reaches it; the progressive series is over the call path's branches.

## Page structure

(unimplemented) Follow `../templates/page.html`. Mermaid from a pinned CDN version; labels in the source's language.

## Opening it

(unimplemented) Open with what the environment provides (`pwsh.exe Start-Process`, `wslview`, `xdg-open`, `open`); do not just print the path.
