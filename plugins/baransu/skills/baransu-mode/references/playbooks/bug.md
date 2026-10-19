# Bug — something fails

**You own the evidence chain. The steps do the work.**

1. `/how` over the area the symptom lives in.
2. [the failure is a regression, or `git log` shows the area changed recently] `/why` on the same anchor.
3. `/hunt` to the root cause, seeded with steps 1 and 2; hunt's own gates decide the fix and its regression guard.
4. `/review` of the fix.
5. `/prove-it`: the original trigger, driven on the user's path, now gives the right result.
6. [the authorization names a version-control endpoint] `/ship` with the targets the user named.

**Reply:** what was broken, the root cause in one sentence, the fix, the review verdict, and the prove-it record path with the failing-then-passing evidence quoted.
