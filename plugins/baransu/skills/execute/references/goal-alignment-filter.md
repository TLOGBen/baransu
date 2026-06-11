# Goal-Alignment Filter — finding-level governance procedure

Invoked from SKILL.md §4b Phase 3, when the review-tier SWITCH lands on
`packaged confirm (correctness)` or `needs judgment`. 「failure escalation
logic below」 in this file refers to the failure escalation logic in SKILL.md
§4b Phase 3. Content moved verbatim from SKILL.md; semantics unchanged —
the `failure_count` accounting and the hard invariant are authoritative here.

**Goal-Alignment Filter** (applies to: `packaged confirm (correctness)`, `needs judgment`)

Applicability gate. This sub-step runs ONLY when the SWITCH above landed on
`packaged confirm (correctness)` or `needs judgment`. For `advisory`,
`direct fix`, and `packaged confirm (quality)` the filter is **skipped**
and the original SWITCH outcome stands unchanged.

Purpose. review-agent is a finding-producing perspective; governance lives
here. Some findings reviewer raises are **off-goal observations** (style,
unrelated polish) that should not block the task. The filter walks each
finding and decides whether it serves `ctx.md → Task.目標` / corresponds
to a `Task.驗收標準` failure. Off-goal findings are downgraded to advisory
and do not contribute to `failure_count`.

Finding-level loop:

```
# Initial counter accumulation: every finding observed feeds the metric.
total_findings_count += len(findings)

FOR each finding F in review.findings:
  # Step 1 — does F correspond to a 驗收標準 failure (semantic coverage)?
  is_acceptance_failure = semantic_match(F.observation, ctx.Task.驗收標準)
  # Step 2 — does F serve Task.目標?
  serves_goal           = semantic_match(F.observation, ctx.Task.目標)

  IF is_acceptance_failure:
    # Hard invariant — see below. F keeps its original tier; never downgraded.
    F.downgraded_to_advisory = false
  ELIF serves_goal:
    # On-goal but not acceptance-bound: keep original tier.
    F.downgraded_to_advisory = false
  ELSE:
    # Off-goal observation. Downgrade to advisory.
    F.downgraded_to_advisory = true
    downgraded_to_advisory_count += 1
END FOR
```

**Hard invariant — 驗收標準直接失敗 finding 不可 downgrade 為 advisory.**
Any finding whose observation corresponds to a 驗收標準直接失敗
(`is_acceptance_failure == true`) **不可**被 goal-alignment 邏輯
downgrade 為 advisory；該 finding 維持原 tier，並依原邏輯計入
`failure_count`。invariant 是 R2 的下界，不是建議。

Filter 判斷準則：以驗收標準語意覆蓋範圍判斷，而非字面引用編號。若
finding 的 observation 描述了某個失敗條件，而 `Task.驗收標準` 任一
條目的語意涵蓋此條件，即視為「對應驗收標準直接失敗」並受 invariant
保護 — 即使 finding 文字不只字面引用驗收標準編號（例如 finding 寫
「authentication middleware 未掛載」、驗收標準寫「endpoint 必須要求
授權」即構成語意覆蓋）。

Post-step — review-level tier 重新計算 (re-tier):

```
# After all findings have been classified, recompute the review-level tier.
remaining = [F for F in review.findings if not F.downgraded_to_advisory]

IF every F in review.findings was downgraded to advisory  (remaining is empty):
  # All findings off-goal → review-level tier 改 advisory；task 走 ✅ 路徑。
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

`total_findings_count` and `downgraded_to_advisory_count` are the source
of truth for the matching `goal_alignment_filter_metric` block in Step 7's
`final-report.md`; both counters live across the task's full TDAID loop
and are emitted at report time.
