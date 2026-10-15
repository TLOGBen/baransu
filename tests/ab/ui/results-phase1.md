# /ui A/B — phase 1 (2026-10-15)

- Old (arm p): old version: git show 2574bc6:plugins/baransu/skills/ui/SKILL.md
- New: phase 1 — the section "The idea, the argument, and looking at the result" (arm q).
- Builds: one fresh subagent per brief × arm, `build-prompt.md`; screenshots re-taken after all builds with
  draw's `verify-page.mjs` into `shots-final/` (no console errors, no sideways scroll on any of the six).
- Judge: one fresh subagent, `juror-prompt.md`, saw only the shuffled `light-page.png` + `phone-page.png`.
- Mapping (shuffle, no seed): brief-1 A=q B=p · brief-2 A=p B=q · brief-3 A=q B=p.

## Result: new 2 of 3

| Brief | Winner | Judge's reason, short |
| --- | --- | --- |
| brief-1 bicycle repair | **old** | Old put the price board in the hero, answering "how much" on the first screen with LINE right under it. New's 兌悅門 arch was a real, place-specific idea, but it spent the whole first screen (the whole phone viewport) on the arch and pushed the prices below the fold; a wide empty strip on desktop. |
| brief-2 tabdiff | **new** | New showed the claim instead of stating it: a key-pairing diagram, all three outputs as real artifacts, a sharper headline, a full-yellow install band. The judge called old a standard developer-tool layout. New's phone layout clips the pairing diagram and drops the hero table's "After" column. |
| brief-3 poetry day | **new** | New turned facts into pictures: a sky timeline, 40 cells for the 40 slots, a full-width rain band, transit notes; poster presence. Unlabelled colour cells read as taken slots; small desktop body copy; cramped phone timeline. |

## What this says about the phase-1 rules

- The inventory and competitor test worked in all three: each new build's idea came from the subject
  (the city gate, the key pairing, the day's light), and the judge named the idea first in both wins.
- The loss is one failure mode: the idea displaced the visitor's first question. The brief asked for prices,
  hours and booking; the new hero gave the screen to the motif. A phase-2 candidate rule: the first screen
  answers the brief's first question in large type, and the idea carries that answer rather than replacing it.
- The phone check passed in the builders' own critique yet the judge found phone clipping in brief-2
  (the builder had allowed in-block sideways scroll) — candidate: a wide figure on the phone is redrawn
  or stacked, not scrolled.

Limits: one judge, one verdict per brief, so each verdict carries noise; three briefs; judges are models,
not people. The judge's full text is in `.claude/ab/ui-phase1/verdict.md` (local only).

## Round 2 (2026-10-15): new 3 of 3

New arm re-read with three rules added after round 1: the idea carries the visitor's first question and
never replaces it (with a phone rule against sideways-scrolling blocks); name the main story in one sentence
first, and every design choice or visual effect stays only if it serves that story; rank the page and every
screen 6 : 3 : 1 as `/draw`'s `composition.md` does. All three new builds rebuilt from the brief by fresh
subagents; the old builds and their `shots-final/` reused from round 1; a fresh judge with the same prompt.
Mapping (shuffle, no seed): A=q, B=p on all three briefs.

| Brief | Winner | Judge's reason, short |
| --- | --- | --- |
| brief-1 bicycle repair | **new** | The price card is cut as an arch echoing 兌悅門; the three prices, today's open status and a LINE button all sit in the first screen; per-service explanations. Old's lower sections shrink into a narrow left column with the right 40 % empty, and its hours are tiny. |
| brief-2 tabdiff | **new** | The hero argues the whole case at a glance: an eight-line git diff above tabdiff's three keyed rows, a shuffle button, and a pairing diagram; the phone reflows without losing columns. Old's terminal sample leaves an empty band and its phone version cuts columns off. |
| brief-3 poetry day | **new** | Every section tied to this riverside container-market event (dusk horizon timeline, the container wall of 40 slots, the rain band), plus transit routes and a day summary. Old's desktop hero leaves the right half blank and turns into a plain text document. New should still pull the sign-up button into the first screen. |

Reading it: round 1's loss (the idea displacing the first question) did not recur; the judge's reasons for
the old pages now are hierarchy failures (half-empty screens, a narrow column, unreadable hours), which is
what the main-story and 6 : 3 : 1 rules target. Limits: the shuffle put the new page in slot A on all three
briefs, so a first-position preference in the judge cannot be ruled out; one judge, three briefs.
The full verdict is in `.claude/ab/ui-round2/verdict.md` (local only).
