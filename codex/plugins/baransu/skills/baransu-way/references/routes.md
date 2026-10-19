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

1. `$baransu:how` over the asked-about area.
2. [the question is about motivation, history, or a past decision] `$baransu:why` on the same anchor.
3. Answer. [the user wants to be taught step by step] `$baransu:teach-me` instead of a plain answer. A picture is `$baransu:show-me`, which only the user can call: suggest it, do not run it.

### Small change

1. `$baransu:how`, one reading of the file and its callers.
2. Implement under `../../_shared/tdd.md` §7: red, then green.

### Bug — something fails

1. `$baransu:how` over the area the symptom lives in.
2. [the failure is a regression, or the area was recently reshaped] `$baransu:why` for its history.
3. `$baransu:hunt` to the root cause, seeded with steps 1 and 2.
4. Fix under `../../_shared/tdd.md`: the failing reproduction first, then the fix.
5. `$baransu:review` of the fix.
6. `$baransu:prove-it`: the original reproduction now passes on the user's path.
7. [authorized] `$baransu:ship`.

### Feature — direction settled

1. `$baransu:how` over every area the feature touches.
2. [the feature reshapes something an earlier decision made] `$baransu:why`.
3. [the shape is not obvious: a new module, a change across a seam, state with more than one writer] `$baransu:draft`.
4. [step 3 ran] `$baransu:review` of the sketch.
5. Build under `../../_shared/tdd.md`, filling the sketch when there is one.
6. `$baransu:review` of the change.
7. [a claim only a run settles: it works, a reported problem, a platform, a timing] `$baransu:prove-it`.
8. [authorized] `$baransu:ship`.

### Direction undecided — whether, which way, what shape of solution

1. `$baransu:how` over the areas the idea touches.
2. [the idea revisits an earlier decision] `$baransu:why`.
3. `$baransu:think`, with the user.
4. [authorized past the plan] `$baransu:review` of the plan.
5. Continue as Feature from its step 3.

This is the full chain: think → review → draft → review → build → prove-it + review → ship.

### Restructure — behaviour preserved, shape changes

1. `$baransu:how` and `$baransu:why` over the area.
2. `$baransu:draft`, or `$baransu:draft --deepen` when no change is named yet.
3. `$baransu:review` of the sketch.
4. Build under `../../_shared/tdd.md`; the existing behaviour tests stay green throughout.
5. `$baransu:review` of the change.
6. [behaviour a user reaches was moved] `$baransu:prove-it`.

### Large — several interdependent modules

1. `$baransu:how` over each module.
2. Chart the effort into slices — through the common suite's wayfinder when installed, detected first — and name the slice that hits the riskiest premise as the pilot.
3. Run the pilot through Feature; re-read the remaining slices after it.
4. Each remaining slice through Feature.

### Making, writing, learning — one leg

Visual piece `$baransu:draw` (a whole page goes on to `$baransu:ui` in the same turn); UI `$baransu:ui`; prose `$baransu:write`; a source into the conversation `$baransu:read`; a study note `$baransu:learn`. Each is one leg: name it and run it.

### Wrap-up

`$baransu:ship`. Its targets must be named by the user.
