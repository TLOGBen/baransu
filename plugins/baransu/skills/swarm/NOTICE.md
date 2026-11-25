# Third-party notice — /baransu:swarm

`/swarm` is this repo's own design. Its decision log (the "The decision log" section, the audit and the reviewer on another model in "Report", and `scripts/log.mjs`) is adapted from the `show-me-your-work` skill in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/show-me-your-work/`, as of commit `2f87c85`, 2026-11-16), by Lauren Tan, under the MIT License reproduced below.

What was kept, in this skill's own words: one append-only TSV log with the six columns `ts`, `phase`, `decision`, `why`, `evidence`, `result`; evidence as a pointer, never prose; logging forks, checkpoints, pivots and blockers rather than every action; a superseding row for a wrong call; a `start` row when a new session picks the work up; auditing the rows against the session's own transcript before handing back; a reviewer on another vendor's model reading the trail; and the closing Attention section naming that model. What changed: the log lives under `.claude/swarm/<slug>/`, it also holds every decision the queen takes for the user to review before shipping, the user gets the new rows each time the crew changes, and `scripts/log.mjs` is a Node program written for this repo that does what the upstream `scripts/log.sh` does (time stamp, header, one-line cells, formula guard); no upstream text or code is copied.

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
