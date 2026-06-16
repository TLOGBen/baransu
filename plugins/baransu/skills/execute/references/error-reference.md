# Error Reference — condition / detection point / action lookup

Lookup table for SKILL.md error handling across all steps. Content moved
verbatim from SKILL.md; semantics unchanged.

| Condition | Detection point | Action |
|-----------|-----------------|--------|
| Spec dir missing | Step 0 | Stop; tell user to run /analyze |
| Spec file missing | Step 0 | List gaps; escalate; stop |
| Red gate not passed ⚠️ | §4b Phase 2 | BLOCKED (wrong test); escalate |
| Compile error ❌ | §4b Phase 2 | Retry; does NOT count toward failure_count |
| Impl failure (correctness/judgment) | §4b Phase 3 | failure_count++; retry |
| failure_count == 2 | §4b escalation | Dispatch smart-friend; retry |
| failure_count == 3 | §4b escalation | BLOCKED |
| Spec contradiction | review-agent output | BLOCKED; escalate |
| Merge semantic conflict ❌ | §4d | BLOCKED downstream; escalate |
| Merge Green broken × 3 | §4d | BLOCKED downstream; escalate |
| E2E fails | Step 5 | e2e-fix-agents (one cluster per agent); one re-run |
| E2E still fails after fix | Step 5 | Record ❌; continue to Step 6 |
| Final-Review needs_fixer: true | Step 6 | final-fixer once; one re-review |
| Final-Review still needs_fixer: true | Step 6 | Record remaining gaps as BLOCKED; proceed |
| Write attempt to analyze dir | All steps | Immediate structural blocker; escalate |
| Filter downgraded finding to advisory | §4b Phase 3 | Normal path; counted in metric, does not increment failure_count |
| Invariant violation: 驗收標準失敗 finding wrongly downgraded | §4b Phase 3 filter sub-step | Structural blocker; escalate (hard invariant breach) |
