# Third-party notice — $baransu:hypothesis

`references/formal.md` and `references/maintain.md` are adapted from the `create-formal-verification-skill` and `maintain-formal-verification-skill` skills in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/create-formal-verification-skill/` and `pstack/skills/maintain-formal-verification-skill/`, retrieved 2026-10-19), by Lauren Tan, under the MIT License reproduced below. They reached this skill through `prove-it/references/formal.md` (baransu 8.15.0), which they replace.

What was kept, in this skill's own words: choosing the target where a break costs most and tests reach least; letting the question choose the tool; the checks of a trustworthy result (true to the source, able to fail, findings stay findings, honest about scope, readable without the tool, cheap to rerun, a coverage record with a sync point); proving a check on a scratch break before relying on it; and the drift pass with its four outcomes. What changed: a hypothesis is its own artifact with one owner (this skill) and read-only readers, instead of a check inside another skill; every hypothesis is a formal model, with no property-based fallback; a check must also be seen succeeding (a goal reached, and unreachable with one transition removed); freshness is a content hash computed by a script at read time, never a stored flag; every part left unformalized carries a reason record in one of seven classes; the trigger list is enumerated with visible signals and not-triggers; inputs include documents and two-source comparisons; and drift is read for what the source does and why it changed.

`references/diagrams.md` takes its label rules from the `statechart` skill in the same plugin (`pstack/skills/statechart/`, retrieved 2026-10-24), by the same author, under the same license: states labelled with what the reader can observe, steps with the event that moves the system, no variable or action names, and each bug drawn as a numbered path. What changed: the chart is a progressive series that adds one part per diagram, built from this skill's own model, and no script or file of that skill is used. No upstream file is copied.

```
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
