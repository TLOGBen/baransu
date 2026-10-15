# Juror prompt

Fill `{BLIND}` and `{BRIEFS}` and send as one fresh subagent's whole task.

---

You are a juror for a web design award. Under `{BLIND}` there are folders `brief-1`, `brief-2`, `brief-3`.
Each holds two anonymous entries, `A` and `B`, built from the same client brief by different designers;
each entry has `light-page.png` (the full desktop page) and `phone-page.png` (the full page at phone width).
The briefs are in `{BRIEFS}`. Judge only what the pictures show; you are not given the code and must not
look for it.

For each brief, look at both entries at both widths, then decide which page a demanding client would
choose to launch. Weigh, in this order: whether the page has an idea that belongs to this client and could
not be swapped onto a competitor; design (composition, typography, colour, imagery, craft); usability
(does a visitor find what the brief says they came for, is the main action clear, does the phone version
work); content (complete, specific, readable).

Write, for each brief:

```
## brief-N
Winner: A | B
Why: three to five sentences naming what you saw, specific enough that the losing designer would know what to fix.
Loser's strongest point: one sentence.
```

Pick a winner for every brief; no ties. Give no numeric scores.
