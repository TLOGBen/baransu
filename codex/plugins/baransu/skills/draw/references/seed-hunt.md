# Seed hunt — three first versions, one refined

A diagram, a component or a film starts as three independent first versions (seeds), built in parallel up to the point where the piece can be seen; a blind judge picks one, and only that one is refined, checked and finished. A map runs no seeds: its content is the repository's facts and its layout comes from `finalize`.

## Why seeds

The 7.5.0 controlled run (20 builders, four subjects, blind judges) found that the same brief built twice under the same conditions lands far apart: one subject's two identical runs ranked 4th and 5th of five, another's 1st and 3rd. Neither stricter step instructions nor the mechanism examples moved quality in a consistent direction; the spread between runs did. So the cheapest gain is to sample the first version several times and spend the refinement on the best one, not to add rules. A seed stops before the expensive part (motion, the critique loop, rendering), which keeps the extra cost to the drafting stage.

## Where the seeds stop

A seed runs every applicable step after `seed-hunt` and before the pick step, in `references/steps.json` order, with its step commands, and then stops:

| Form | Pick step | What a seed has when it stops |
|---|---|---|
| diagram | `seed-pick` | the rendered diagram file (`diagram-markup`, CJK labels when they apply), or a mechanism still (`mech-still`) |
| component | `seed-pick` | every component's composed rest frame in both themes (`component-rest-frame`); a mechanism seed has invented its own object, parts, geometry and card |
| film | `seed-pick-film` | the style guide, storyboard, camera plan and every key rendered as a still (`keys-bookends`, `keys-layout`) |

A seed never animates, never runs the critique loop and never renders a master. Several pieces: each seed builds all of them, and the pick is made on the whole set, so the pieces keep one look.

## Dispatch the seeds

1. Make `scratch/seed-a/`, `scratch/seed-b/` and `scratch/seed-c/`, and copy `docs/brief.md` into each seed's `docs/`. Nothing else is shared: no notes, no direction, no assigned style. The spread comes from independent sampling, not from steering.
2. Spawn three Codex subagents in parallel with `spawn_agent`, each in a clean context (`fork_turns="none"` on the v2 tool, `fork_context=false` on v1) and each given the same task: the skill folder, its own seed folder as `<out>` (step commands use `--log "<out>/scratch/seed-<x>"`), the instruction to run every applicable step from the first after `seed-hunt` up to the pick step and stop there, never to open a sibling seed folder, and to finish with `docs/seed_note.md`: the idea in one sentence (for a mechanism, the invented object) and the paths of its captures. Wait for all three with `wait_agent` before the pick.
3. When subagents are unavailable (no `spawn_agent` in the session, or `agents.enabled = false`), build the three seeds one after another in this session, each from the brief alone, without opening an earlier seed while building the next; record `seeds: sequential` in `docs/seed_hunt.md`, because the seeds are then less independent.
4. A request for something quick (快速, 草圖, quick sketch, `--quick`, 「一個 seed 直出」) runs one seed; `docs/seed_hunt.md` records `seeds: 1 (quick request)` and the pick step promotes it without a judge. A seed that fails (its build breaks, its subagent stops early) is recorded and dropped; the pick runs on the rest.

The `first-version` milestone is still due within the hour: when the hour comes before the pick, send the first seed that opens (its path under `scratch/`), and say the pick is still to come.

## Pick blind

1. Copy each surviving seed's captures to `shots/seeds/` under a shuffled letter (`shots/seeds/P.png`, `Q.png`, `R.png`, …); the letter-to-seed key is written to `docs/seed_hunt.md` only after the verdict.
2. Spawn one judge subagent with `spawn_agent` in a clean context (`fork_turns="none"`), passing the brief, the captures under their shuffled letters, and the scorecard rows that can be judged from stills: the shared card and the form and approach rows (`critique-shared-scorecard`, `critique-rows-{form}`, `critique-rows-{approach}`); wait for its verdict with `wait_agent`. It never sees the seed folders, their notes or their logs. When subagents are unavailable, judge the captures yourself in that order and record `judge: self`.
3. The judge scores each seed on those rows, gives each an overall 1–10 and one line on why, and ranks them. The highest overall wins; on a tie, the seed whose lowest row is higher.
4. Write the verdict to `docs/seed_hunt.md`: the scores per letter, the ranking, the key, the winner, and any idea from a losing seed worth trying in the critique loop. A losing seed's parts are never spliced into the winner: a seed is kept or dropped whole.

## Promote the winner

1. Copy the winning seed's files into the output folder, except `docs/brief.md`, `docs/progress.md` and `docs/lookups.log`.
2. Append the winner's `docs/lookups.log` lines to the output folder's `docs/lookups.log`, so `ledger-check.py` finds a record for every step the seed ran.
3. The losing seeds stay under `scratch/`: never delivered, never scanned by the ledger.
4. Continue in the output folder from the step after the pick step; the refinement, the motion, the critique loop and the finish run on the winner only. The completion report names the seed count, how they ran, and the winner's margin.
