# Goal-Alignment Filter — finding-level governance procedure

Invoked from execution-pipeline.md §4b Phase 2, when the review-tier SWITCH lands on
`packaged confirm (correctness)` or `needs judgment`. "failure escalation
logic below" in this file refers to the failure escalation logic in execution-pipeline.md
§4b Phase 2. Semantics unchanged from the pre-merge /execute skill —
the `failure_count` accounting and the hard invariant are authoritative here.

**Goal-Alignment Filter** (applies to: `packaged confirm (correctness)`, `needs judgment`)

Applicability gate. This sub-step runs ONLY when the SWITCH above landed on
`packaged confirm (correctness)` or `needs judgment`. For `advisory`,
`direct fix`, and `packaged confirm (quality)` the filter is **skipped**
and the original SWITCH outcome stands unchanged.

Spec-contradiction pre-check. Before walking any finding: if
`review.spec_contradiction != false`, skip the filter entirely and go directly
to the failure escalation logic — its spec-contradiction branch marks the task
BLOCKED. A spec-contradiction review must always reach that branch; the
all-findings-downgraded ✅ path below must never absorb it.

Purpose. review-agent is a finding-producing perspective; governance lives
here. Some findings reviewer raises are **off-goal observations** (style,
unrelated polish) that should not block the task. The filter walks each
finding and decides whether it serves the tasks 目標 (read from task-{group}.md) / corresponds
to a task 驗收標準 failure. Off-goal findings are downgraded to advisory
and do not contribute to `failure_count`.

Finding-level loop:

```
FOR each finding F in review.findings:
  # Step 1 — does F correspond to a 驗收標準 failure (semantic coverage)?
  is_acceptance_failure = semantic_match(F.observation, task.驗收標準)
  # Step 2 — does F serve Task.目標?
  serves_goal           = semantic_match(F.observation, task.目標)

  IF is_acceptance_failure:
    # Hard invariant — see below. F keeps its original tier; never downgraded.
    F.downgraded_to_advisory = false
  ELIF serves_goal:
    # On-goal but not acceptance-bound: keep original tier.
    F.downgraded_to_advisory = false
  ELSE:
    # Off-goal observation. Downgrading requires a written construction —
    # {quoted 驗收標準 entries examined, one-line non-coverage reason} —
    # appended to the task's impl-checklist 備註; if it cannot be constructed
    # from quoted text (coverage uncertain), set is_acceptance_failure = true.
    F.downgraded_to_advisory = true
END FOR
```

**Hard invariant — a 驗收標準直接失敗 finding must NOT be downgraded to advisory.**
Any finding whose observation corresponds to a 驗收標準直接失敗
(`is_acceptance_failure == true`) **must not** be downgraded to advisory by
the goal-alignment logic; that finding keeps its original tier and still
counts toward `failure_count` per the original logic. The invariant is R2's
lower bound, not a suggestion. Tie-break: unsure = protected — when semantic
coverage is uncertain, the written construction fails and the finding is
treated as an acceptance failure, never downgraded.

Filter decision criterion: judge by the semantic coverage of the acceptance
criteria, not by literal reference numbers. If a finding's observation
describes some failure condition and the semantics of any entry in
`Task.驗收標準` cover that condition, it is treated as "corresponds to an
acceptance-criterion direct failure" and is protected by the invariant.

Post-step — review-level tier recomputation (re-tier):

```
# After all findings have been classified, recompute the review-level tier.
remaining = [F for F in review.findings if not F.downgraded_to_advisory]

IF every F in review.findings was downgraded to advisory  (remaining is empty):
  # All findings off-goal → review-level tier becomes advisory; task takes the ✅ path.
  review_tier = "advisory"
  failure_count is NOT incremented   # filter absorbed the failure
  mark task ✅
  TaskUpdate: status=completed
  break LOOP

ELSE:
  # At least one finding survives (acceptance failure or on-goal). Keep
  # original tier (correctness / judgment) for routing.
  failure_count += 1
  → go to failure escalation logic below
```
