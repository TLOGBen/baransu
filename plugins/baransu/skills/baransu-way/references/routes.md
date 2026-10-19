# Routes

A route is the ordered list of legs a goal of that shape needs. Copy the chosen route's steps into the task list as written, then mark each step this goal does not need `skip: <reason>`. Brackets mark a leg that runs only when its condition holds.

## Bands

| Band | Shape | Closure evidence |
|---|---|---|
| Small | One file, one obvious fix, scope clear | red → green run under `../../_shared/tdd.md` §7 |
| Medium | One feature, a few files | red → green run + review verdict (+ prove-it record when a claim needs a run) |
| Large | Two or more interdependent modules; context rot is real | per slice: red → green run + review verdict |

Never route a task up a band without evidence for it, and never down a band to skip what its shape needs.

## Routes

### Question — how does X work, why is X this way

1. `/how` over the asked-about area.
2. [the question is about motivation, history, or a past decision] `/why` on the same anchor.
3. Answer. [the user wants to be taught step by step] `/teach-me` instead of a plain answer. A picture is `/show-me`, which only the user can call: suggest it, do not run it.

### Small change

1. `/how`, one reading of the file and its callers.
2. Implement under `../../_shared/tdd.md` §7: red, then green.

### Bug — something fails

1. `/how` over the area the symptom lives in.
2. [the failure is a regression, or the area was recently reshaped] `/why` for its history.
3. `/hunt` to the root cause, seeded with steps 1 and 2.
4. Fix under `../../_shared/tdd.md`: the failing reproduction first, then the fix.
5. `/review` of the fix.
6. `/prove-it`: the original reproduction now passes on the user's path.
7. [authorized] `/ship`.

### Feature — direction settled

1. `/how` over every area the feature touches.
2. [the feature reshapes something an earlier decision made] `/why`.
3. [the shape is not obvious: a new module, a change across a seam, state with more than one writer] `/draft`.
4. [step 3 ran] `/review` of the sketch.
5. Build under `../../_shared/tdd.md`, filling the sketch when there is one.
6. `/review` of the change.
7. [a claim only a run settles: it works, a reported problem, a platform, a timing] `/prove-it`.
8. [authorized] `/ship`.

### Direction undecided — whether, which way, what shape of solution

1. `/how` over the areas the idea touches.
2. [the idea revisits an earlier decision] `/why`.
3. `/think`, with the user.
4. [authorized past the plan] `/review` of the plan.
5. Continue as Feature from its step 3.

This is the full chain: think → review → draft → review → build → prove-it + review → ship.

### Restructure — behaviour preserved, shape changes

1. `/how` and `/why` over the area.
2. `/draft`, or `/draft --deepen` when no change is named yet.
3. `/review` of the sketch.
4. Build under `../../_shared/tdd.md`; the existing behaviour tests stay green throughout.
5. `/review` of the change.
6. [behaviour a user reaches was moved] `/prove-it`.

### Large — several interdependent modules

1. `/how` over each module.
2. Chart the effort into slices — through the common suite's wayfinder when installed, detected first — and name the slice that hits the riskiest premise as the pilot.
3. Run the pilot through Feature; re-read the remaining slices after it.
4. Each remaining slice through Feature.

### Skill or prompt change — a SKILL.md, an agent prompt, an instruction or rules file

1. `/how` over the skill and every file that reads it or restates it.
2. `/why` for each clause the change rewrites or removes.
3. [the change is undecided, or a skill is to be added or retired] `/think`.
4. Edit the text, and every copy that mirrors it in the same change; or `/evolve` instead, when the goal is a scored improvement against a rubric.
5. [the repo keeps an eval set or a structural check for it] run it.
6. `/review` of the change.
7. [authorized] `/ship`.

### Making, writing, learning — one leg

Visual piece `/draw` (a whole page goes on to `/ui` in the same turn); UI `/ui`; prose `/write`; a source into the conversation `/read`; a study note `/learn`. Each is one leg: name it and run it.

### Wrap-up

`/ship`. Its targets must be named by the user.
