# Third-party notice — $baransu:draft

`$baransu:draft` is adapted from three sources, retrieved 2026-10-19, each under the MIT License reproduced below. No upstream file is copied.

- **`architect` and `arena`** in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/architect/` with its `references/runner-prompt.md`, `references/rationale-template.md` and `references/design-red-flags.md`, and `pstack/skills/arena/`), by Lauren Tan. Kept, in this skill's own words: grounding before sketching; usage before types; a sketch of types and signatures with unimplemented bodies; designing at least twice with whole-shape alternatives from independent runners told not to hedge; screening against design red flags with the next contributor imagined as an agent that sees one file; comparing on interface depth; picking a base and grafting by hand, with convergence and divergence read as signals; the sketch as the contract during implementation, with deviations raised; scrapping on a pattern of friction and redrawing smaller; the rationale page. Changed: no human-free default — the turn stops for the user's go on the shape; the runners' models come from what the host can run rather than a rule file; the red flags are the review principles this plugin already keeps (`structure.md`, `taste.md`, `readability.md`), not a separate list; implementation follows this plugin's red/green discipline.
- **`codebase-design`** (with `DEEPENING.md` and `DESIGN-IT-TWICE.md`) and **`improve-codebase-architecture`** in [mattpocock/skills](https://github.com/mattpocock/skills) (`skills/engineering/`), by Matt Pocock. Kept: the deep-module vocabulary (module, interface as everything a caller must know, depth, seam, adapter, leverage, locality) and the deletion test, as the review principles already state them; giving each parallel designer a different pull (smallest interface, most common caller, ports and adapters); comparing on depth, locality and seam placement; and the deepening scan — scope by recent change, friction signs, deletion test, candidates with strength, recorded decisions not reopened without cause, the user's pick. Changed: no HTML report — before and after pictures go through this plugin's drawing skills; the picked candidate goes through this skill's own drawing and screening.
- **`ponytail`** in [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), by Dietrich Gebert. Its smallest-complete-change ladder and never-cut list reach this skill through the `taste.md` principle, which already restates them; this skill adds no separate copy.

```
MIT License

Copyright (c) 2026 Lauren Tan
Copyright (c) 2026 Matt Pocock
Copyright (c) 2026 DietrichGebert

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
