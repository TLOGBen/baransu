# Third-party notice — $baransu:health

The mistake-class rules in `SKILL.md` Step 0 and the mistake-class pass are adapted from the `correct` skill in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/correct/`, as of commit `d457567`, 2026-10-19), by Lauren Tan, under the MIT License reproduced below.

What was kept, in this skill's own words: a class counts once it has happened twice; fixing each class at the highest level that works, from architecture through types, a check whose error names the fix, and tests, to documentation last for judgment calls; proving each new check fails on a real past mistake; a ratchet when the pattern is already common; the rule table pairing each rule with what enforces it, where a rule that existed but went unenforced is a repeat, and a rule is dropped once its mistake cannot happen. What changed: it is a focused pass of this audit rather than a separate skill; findings are offered, never applied by this skill; the fix runs as ordinary implementation closed by `$baransu:review` and committed through `$baransu:ship`; a class whose past state cannot be named is deferred; corrections come from this skill's existing conversation-signal collector.

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
