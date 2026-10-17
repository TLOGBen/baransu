# Third-party notice — /baransu:how

`/how` is adapted from the `how` skill in Cursor's pstack plugin ([cursor/plugins](https://github.com/cursor/plugins), `pstack/skills/how/`, retrieved 2026-10-17), by Lauren Tan, under the MIT License reproduced below.

What was kept, in this skill's own words: answering a narrow question directly and splitting a broad one into 2 to 4 explored slices, the explorer report shape, and the answer's sections (overview, key concepts, how it works, where things live, gotchas). What changed: the model-assignment rule file was dropped; the main session reads the entry points first and decides the split from what is left, instead of sizing the question up front; a narrow question is answered by the main session instead of a spawned explainer; explorers are read-only agents and the main session reconciles their findings; read-only runs and throwaway experiments count as reading; an open-questions section was added; placement questions defer to `/think` when they are a tradeoff. No upstream file is copied.

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
