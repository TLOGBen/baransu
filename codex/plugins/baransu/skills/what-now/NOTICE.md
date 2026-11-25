# Third-party notice — $baransu:what-now

`$baransu:what-now` is adapted from the `ketchup` skill in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/ketchup/`, as of commit `d457567`, 2026-10-19), by Lauren Tan, under the MIT License reproduced below.

What was kept: the upstream text — catching up from the user's last message, the read-only gather, what counts as an action item, the reply order (one opening sentence, pictures, one line per request, then the calls), the shapes for one item, shared calls, and options, and the rules for visuals — and, from the upstream frontmatter, invocation by the user only on Claude Code (this Codex copy omits that Claude-only key). What changed: the skill is renamed `$baransu:what-now`; the voice is `$baransu:huh`'s instead of `/bro`'s; visuals draw on `$baransu:show-me`'s views instead of `/visualize`; word budgets are restated as Traditional Chinese character budgets and the examples are in Traditional Chinese; the PR-body playbook reference was dropped; a Traditional Chinese output line, an Outcome Contract, and Not-for boundaries were added in this repo's format.

The `--video` section is adapted from the `ketchup-video` skill in the same plugin (`pstack/skills/ketchup-video/`, as of commit `ab1f702`, 2026-10-27), by the same author, under the same license. What was kept, in this skill's own words: the window starting at the last user message before the call, the reply shape (opening sentence, video, one line of remaining work, the calls), naming options by the video's names, the slide rules, the reading-time hold of one second per three words, and checking one frame per slide in the rendered file. What changed: the video is a flag on `$baransu:what-now` instead of its own skill, the render goes through `$baransu:draw`'s film lane, and the hold for Chinese is counted in characters.

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
