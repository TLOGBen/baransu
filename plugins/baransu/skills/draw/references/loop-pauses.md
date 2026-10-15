# loop-pauses — /draw PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/draw is graded loop=assisted. It does not stop to ask in any run, interactive or not: form, approach, size and direction are decided from the content and stated in the 開工狀態行 (`SKILL.md` § The flow, step `brief-and-status-line`), and the build starts in the same turn. The rows below are the points where a run meets a decision it cannot make from the content; each has a default a non-interactive run takes and annotates.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Motion lane — asset manifest (`assets/manifest.json` from `grab.mjs`, or the user's files) listed before production | Input | Proceed only when every asset the brief names as *real* is present; a brand-affecting default (a replaced logo, a changed brand colour, an invented metric) is never taken — see the error exits below. |
| Map lane — a candidate that fails `finalize` more than the repair limit | Input | Stop repairing, deliver the last passing artifact if one exists, otherwise report the failing gate verbatim; never hand-edit the receipt. |
| Any lane — output slug already exists under `.claude/draw/` | Input | Write `<slug>-2/` and count up; never overwrite. Annotate the renamed path. |
| Critique loop — a row still < 8 | Input | Keep running rounds: there is no round cap, and running time is not a reason to stop. A row that has not improved over two consecutive rounds is stalled (`critique-loop.md` § A stalled row moves on): it is named under 「未做到的」 with its last score and reason and the rounds go to the rows still rising. A row that cannot reach 8 for a reason outside the build (a real asset that was not supplied, an environment where the check cannot run) is named the same way. |
| Check and deliver — `assemble-page` (the /ui hand-off on a `needs-page` request) | Input | /ui is `loop=not-drivable` (its interactive plan is its product), so a non-interactive run does not invoke it. Default: deliver every checked component and `docs/ui_brief.md` (the page brief, the component paths, the page file name `<page-name>.html`), skip the hand-off, annotate 「此處採預設：頁面待 /ui 互動組頁」, and name the page under 「未做到的」 with the command that finishes it (`/ui` with `docs/ui_brief.md`). `ledger-check.py` then reports `assemble-page` as not reached; the report quotes that line, and every other check must pass. An interactive run invokes /ui in the same turn as usual. |

Time is not a PAUSE either: the first version sent within the first hour and the progress line for a step past twice its expected time are messages, never waits; under a driver they go into the run's output and into `docs/first_version.md` / `docs/progress.md` (steps `first-version`, `progress-notes`), and the build continues.

No Authorization PAUSE remains. Former pauses and why they are gone:

- **Plan confirmation.** Replaced by the 開工狀態行: stated, never waited on. Choosing the form, approach and size is the skill's job.
- **Diagram style-guide gate.** The shipped default skin (or a saved profile) is used; branding is read through `onboarding.md` only when the user names a brand.
- **Stills of every shot / a reference that reads two ways.** Both readings are rendered, one is chosen, and the reason is logged in `docs/review_log.md`; the stills' critique is round 0.
- **Full-length render.** It was an Authorization PAUSE because of its running time. Running time is not a reason to stop: the render writes only into the run's own output folder, overwrites nothing, sends nothing, and is part of the deliverable. The gate before it is quality — the contact sheet scoring 8+ — and it applies the same way with or without a human.

Error exits that are not PAUSEs (the driver gets an explicit failure): missing `node`/`python3`/`ffmpeg` for the lane that needs them after `doctor.mjs --install` could not install them, a page that defines no `window.seek`, an archify `doctor` failure, an input path that does not exist, and — any lane — a brief that names a real asset or fact (a screenshot, a logo, a track, a metric, a date) that was not supplied: an empty three-second shot is still a wrong film, so the run stops and names the missing asset instead of drawing around it. This is the one stop an interactive run makes too; the completion report's 「提問」 line names it.
