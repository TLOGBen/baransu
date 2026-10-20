# Third-party notice — $baransu:review

The review principles under `references/principles/` are adapted and restated in this repo's terms from these sources: pstack principles, `correct`, `blast-radius`, `architect` design red flags, and `interrogate` rubric (cursor/plugins, MIT); `codebase-design`, `code-review`, `domain-modeling`, and `tdd` (mattpocock/skills); `ponytail` and `ponytail-review` (DietrichGebert/ponytail, MIT); Fowler, *Refactoring*, ch. 3; Claude Code's built-in `/security-review`.

The security principles — `trust-boundary.md`, `authentication.md`, `access-control.md`, `disclosure.md`, and `security-finding.md` — also adapt Cloudflare's `security-audit` skill ([cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), `skills/security-audit/`, commit `c1c8a8c`, retrieved 2026-10-20), under the MIT License reproduced below.

What was kept, in these principles' own words: the six parts every security finding states (actor, input, intended control, boundary, affected party, result); that same-principal authority or self-impact is not a crossing; that a claimed effect stays within what was shown; the smallest fix at the last trusted decision point; comparing what one component guarantees with what the next assumes; equal-strength controls across sibling routes; failing closed on missing config, flags, or dependencies; search, export, and error differences as oracles; second-order use of stored data; current authorization on restore and import; revocation windows and capability growth; and its agent rules — prompt injection counts only when model output drives a sink, a guardrail prompt is not a control, and action binding is its own failure. What changed: the principles are split by the security property violated rather than by attack domain; review only reads, so the sandboxed execution, coverage ledger, budgets, run profiles, prior-run carry-over, structured findings schema, validators, and report artifacts were not taken; its severity anchors were mapped onto review's 0–5 scale. No upstream file is copied.

```
MIT License

Copyright (c) 2025-2026 Cloudflare, Inc.

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
