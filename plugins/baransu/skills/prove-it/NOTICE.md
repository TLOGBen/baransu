# Third-party notice — /baransu:prove-it

`/prove-it` is adapted from the `create-verification-skill` and `maintain-verification-skill` skills in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/create-verification-skill/` and `pstack/skills/maintain-verification-skill/`, retrieved 2026-10-18), by Lauren Tan, under the MIT License reproduced below.

What was kept, in this skill's own words: learning the run from the repo before asking the user; a recipe of launch, doctor, drive, evidence, and cleanup with this repo's real commands; the proof standards (the user's path, the action and the resulting state, side effects, dry-runs checked by observation, mocks only at a production boundary); a feature map with one file per feature in four sections; proving the recipe once before relying on it; and the maintenance pass (index, source readers, one live driver, sorting drift from a recipe gap from a broken app). What changed: the generated project-local skill became a recipe and feature map under the skill's own working directory; the purpose became proving claims in both directions — that a reported problem really fails and that work said to be done really works — with each claim ending proved, disproved, or unreachable on a pinned version; claims about timing or order are driven by making the bad order happen; the record of each run is written for `/review` to read as the author's evidence; the maintenance pass edits only that working directory and ships no PR; the feature-map example was rewritten for an invented app. No upstream file is copied.

`references/formal.md` is adapted from the `create-formal-verification-skill` and `maintain-formal-verification-skill` skills in the same plugin (`pstack/skills/create-formal-verification-skill/` and `pstack/skills/maintain-formal-verification-skill/`, retrieved 2026-10-19), by the same author, under the same license. What was kept, in this file's own words: choosing the target where a break costs most and runs reach least; letting the question choose the tool (a model checker for order, a code-level verifier for every input, generated inputs on the real code when no verifier exists, a proof for every size); the checks of a trustworthy result (true to the code, able to fail, findings stay findings, honest about scope, readable without the tool, cheap to rerun, a coverage record with a sync commit); proving the check on a scratch break before relying on it; and the drift pass with its four outcomes. What changed: the generated project-local skill became a directory under the skill's own working directory, listed in the recipe; an every-case claim is one more kind of claim, ending proved, disproved, or unreachable like the others and recorded for review; the scratch break is made in a throwaway copy; the drift pass runs under `--maintain`.

`references/benchmark.md` is adapted from the `benchmark-checklist` skill in the same plugin (`pstack/skills/benchmark-checklist/`, as of commit `d457567`, 2026-10-19), by the same author, under the same license. What was kept, in this skill's own words: the claim written first, the machine check, the seven questions (limiter, tuning, limits, errors, repeatability, relevance, whether the work happened), the ballpark exception, and the four verdicts. What changed: the verdict feeds this skill's record, the playbook references were dropped, and the example is in Traditional Chinese.

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
