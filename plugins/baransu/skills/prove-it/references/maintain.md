# maintain — keeping the recipe and feature map honest

A feature map rots the moment the app changes. This pass keeps `.claude/prove-it/` true to the app. The unit of rigor is the feature: every feature file is covered from source and every feature is driven live once, without proving every sentence.

Adapted from pstack's `maintain-verification-skill`; see the skill's `NOTICE.md`.

## Outcome

Say which one, with the coverage reached:

- **clean** — every feature was covered from source and driven live; nothing needed fixing.
- **changed** — proven corrections to the map or the recipe, each driven again before it was kept.
- **blocked** — coverage could not finish, or a correction could not be proved; name exactly what blocked it.

## Edit scope

Edit only `.claude/prove-it/` — the recipe, the feature map, and any helper scripts it owns. Never edit product code: behaviour the map describes that the app no longer has is either the map being out of date (fix the map) or the app being broken (report it, and leave the map describing what the app should do).

## Pass

1. **Index.** Read the map's README and its sibling files; fix missing, extra, duplicate, or dead entries.
2. **From source.** For each feature file, read how the feature works from the code and flag where the file no longer matches, with citations; each reader returns the feature in brief, its entry points in source, the likely drift or none, and one recipe for driving it live. Readers never drive the app and never edit. Several features can be read in parallel by read-only subagents.
3. **Reconcile.** Merge overlapping drives into as few app states as practical. Spot-check cited drift. Look through recent changes for user-facing surfaces the map lacks — name a concrete source path before calling one missing.
4. **Live.** Required even when the source looks clean; one coordinator does all driving, following the recipe's own launch model. Hold three rules throughout: run the doctor before the first drive and after anything surprising, and reset or relaunch where the doctor cannot see the fault; evidence captured so far survives every cleanup, checked at its location; nothing a drive started outlives its use. A doctor failure caused by the recipe itself is drift: fix it and retry once before calling the pass blocked. A feature that cannot be reached is recorded with its prerequisite and the route tried; if the map omits that prerequisite, that is drift too.
5. **Sort.** Wrong or missing description from the user's side → fix the map. Working behaviour the drive cannot reach → fix the recipe, and drive it again before keeping the fix. Behaviour that is actually broken → a finding for the user, kept out of the map.

Keep short run notes — features covered, unreachable prerequisites, confirmed drift, outcome — in a scratch location; they are not committed.
