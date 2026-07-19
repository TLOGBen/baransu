# Pre-SWITCH guard — verify green_proof

Invoked from execution-pipeline.md §4b Phase 2, before the review-tier SWITCH. "The SWITCH below"
in this file refers to that SWITCH in execution-pipeline.md §4b Phase 2. Content moved
from the pre-merge /execute skill; semantics unchanged except the R8 retry cap.

**Pre-SWITCH guard — verify green_proof**: Before entering the SWITCH below and `mark task ✅`, the main skill
must first verify that the `green_proof` field reported by review-agent conforms to the 5-tier
required matrix in `agents/review-agent.md` §3. Durability: `green_proof.output_tail` and `red_proof`
must live in durable locations — the impl-checklist entry or any file under `.codex/execute/` —
evidence parked only in `/tmp` does not satisfy the gate. Verify rules:

```
verify_green_proof(review_result):
  # Step 1 — existence check applies to ALL tiers (including direct fix).
  # All 4 keys must exist in the schema (their value semantics depend on the tier, but the key itself cannot be omitted).
  REQUIRE green_proof.test_command          key present
  REQUIRE green_proof.exit_code             key present (value is an integer)
  REQUIRE green_proof.output_tail           key present
  REQUIRE green_proof.tests_correspondence  key present
  IF any REQUIRE fails:
    return FAIL, reason="green_proof key missing"

  # Step 2 — tier-specific value check.
  IF review_result.tier == "direct fix"
     AND the review report names a cosmetic subtype
     AND the diff shows every modified file is non-executable text (markdown / comment / formatting-only):
    # conditional waiver: the 4 values may be "n/a"/0/""/"n/a"; value contents are not verified.
    # "no behavior change" is the editor's claim — the waiver is earned by the edit's observable
    # surface (checked from the diff), not by the tier classification alone.
    return PASS
  ELSE:
    # every other case — including a direct fix that touches executable text — must supply a real test
    REQUIRE green_proof.test_command          non-empty AND != "n/a"
    REQUIRE green_proof.tests_correspondence  non-empty AND != "n/a"
    REQUIRE green_proof.exit_code == 0        # else Green failed, not a passed review
    REQUIRE green_proof.output_tail           non-empty
    # Evidence must resolve against ground truth — both REQUIREs below are executed via Bash
    # (grep/ls exit code), not judged by the model:
    REQUIRE the test path/name fragment cited in tests_correspondence resolves against the repo/worktree
            # Bash: `grep -rq "<fragment>" <worktree>/tests/ || ls <cited path>` exits 0
    REQUIRE the test file(s) named in test_command exist on disk
            # Bash: `ls <file path extracted from test_command>` exits 0
    IF any REQUIRE fails:
      return FAIL, reason="green_proof incomplete, exit_code != 0, or cited evidence does not resolve against the repo"
    return PASS
```

Verify-result handling:
- `PASS` → enter the SWITCH below and route per the original logic.
- `FAIL` → the review is treated as failed: **skip the Goal-Alignment Filter directly** (because the
  finding injected by verify-fail is process-level — it corresponds to neither the task's acceptance
  criteria nor the task's goal, so if sent into the filter it would be misjudged as an off-goal
  observation and downgraded to advisory, causing the task to be marked ✅ without real test evidence;
  this hole is handled explicitly by this section). Take the following path directly:
    1. `failure_count += 1` (verify-fail counts toward the task-level failure_count, unlike the
       compile-error exclusion rule in §4b Phase 1 — a compile error goes through `compile_error_count`
       and does not count; verify-fail is a process failure at the review stage and counts toward failure_count).
    2. Append the finding `{citation: "green_proof", observation: "<verify reason>", fix:
       "re-dispatch review-agent and require a complete green_proof"}` to review_result.findings.
    3. Re-dispatch impl-agent + review-agent (following the §4b failure-escalation logic: the single
       retry carries smart-friend's correction_strategy; a second failure blocks the task at the R8 cap).
    4. Do not enter the SWITCH below; this round's Phase 2 ends.
