# loop-pauses — $baransu:draw PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

$baransu:draw is graded loop=assisted: every checkpoint has a sensible default, but two of them (a full-length video render, a file-overwrite) spend real time or destroy work, so a non-interactive run takes the conservative default and says so in the report.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Plan confirmation — lane, visual type, size preset, what the complexity budget cuts (one message before any file is written) | Input | Proceed with the stated plan; append the plan to the completion report under 「此處採預設：未經確認即照計畫繪製」. |
| Diagram lane — style still at shipped defaults in a branded project (first diagram) | Input | Keep the shipped default skin; annotate 「此處採預設：使用內建配色」. |
| Map lane — a candidate that fails `finalize` more than the repair limit | Input | Stop repairing, deliver the last passing artifact if one exists, otherwise report the failing gate verbatim; never hand-edit the receipt. |
| Motion lane — full-length render (`render.mjs full`) after the contact sheet passes | Authorization | Do **not** render the full film; stop after `beats`/`contact` and report 「全片渲染需人工確認（非互動驅動已停在接觸印樣）」. A 60 fps × 4-subframe render of a long piece can run for an hour; nobody asked for that bill. |
| Any lane — output slug already exists under `.codex/draw/` | Input | Write `<slug>-2/` and count up; never overwrite. Annotate the renamed path. |
| Critique loop — scores still < 8 after three rounds | Input | Deliver with the scorecard and the three open problems listed; do not loop forever. |

Error exits that are not PAUSEs (the driver gets an explicit failure): missing `node`/`python3`/`ffmpeg` for the lane that needs them, a page that defines no `window.seek`, an archify `doctor` failure, and an input path that does not exist.
