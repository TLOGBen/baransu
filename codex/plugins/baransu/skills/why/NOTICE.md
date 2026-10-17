# Third-party notice — $baransu:why

`$baransu:why` is adapted from the `why` skill in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/why/`, retrieved 2026-10-17), by Lauren Tan, under the MIT License reproduced below.

What was kept, in this skill's own words: the five confidence tiers and their phrasing rules, the investigator report shape, the coverage rule that every source is searched or its skip is explained, and the answer's sections. What changed: the Cursor MCP discovery and the seven vendor categories became four evidence classes found on a Claude Code / Codex machine (repo record, agent decision record, connected doc sources, upstream material); the model-assignment rule file and the separate synthesizer agent were dropped, so the main session weighs the evidence; investigators run as read-only agents, and only for classes outside the local files. The vendor playbooks (Linear, Notion, Slack, Datadog, Sentry, Databricks) are not included. No upstream file is copied.

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
