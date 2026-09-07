---
name: seal
description: 'Post-implementation seal: pins the delivered artifact and its CONTRACT.md
  (or user-named criteria), sizes verification to the consequence of the changed behavior
  under a finite check-and-repair allowance, dispatches a fresh verify-only verifier
  agent, repairs only when the request already includes implementation, writes a receipt
  under .codex/seal/, appends the seal-log line, and stamps the sealed marker on independent
  success. Trigger On ''$seal'', ''封緘'', ''收尾驗收'', ''驗收剛做完的'', ''seal it''. Not for
  cross-perspective re-verification of any model output (use $review) or pre-work
  criteria pinning (use $contract). 繁體中文輸出。'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# seal — decide whether the promised result is supported by the delivered artifact

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `verifier`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.


Verification effort follows consequence. The purpose is enough independent evidence to judge the promised result, not maximum test activity; a receipt that says 未驗證 is a valid result, a receipt that says passed to end a loop is not.

All user-facing output and the receipt are in Traditional Chinese.

## Outcome Contract

- **Outcome**: An independent judgment of the delivered artifact against its contract (or user-named criteria), sized to the causal risk of the changed behavior, with findings repaired only inside an existing implementation authorization and a bounded allowance; a receipt on disk; the sealed marker on CONTRACT.md when independent success is established.
- **Done when**: The verifier's per-criterion result (supported / violated / unverified, each with evidence) is in hand; any authorized repair has been independently rechecked; the receipt is written; the seal-log line is appended; and either the sealed marker is written (branch 1, independent success) or the report states what remains and why no marker was written.
- **Evidence**: The receipt at `.codex/seal/<slug>-<run>.md` (target identity, acceptance reference, per-criterion results, independence, observations, outcome), the seal-log JSONL line, and — on success — the marker on line 2 of CONTRACT.md.
- **Output**: A Traditional Chinese seal report in the conversation, the receipt file, the seal-log line, and on branch-1 success the sealed marker. `$ship` archives `.codex/seal/` and the sealed root contract.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Seal evidence**: on completion, append one JSON line `{"ts":"<ISO8601>","skill":"seal","result":"pass|fixed|unresolved","target":"<one-phrase>"}` to `~/.codex/baransu/telemetry/{project}/seal-log-{YYYY-MM}.jsonl` (see `references/seal-guard-hook.md` — the Stop hook reads it). The line is written by the main session only.
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Target pin (hard rule)

Pin the actual artifact or diff first, then the acceptance it is judged against:

1. **Contract present** — `CONTRACT.md` at the project root (or the path the user names): reuse its criteria as written. This is the only branch that can write the sealed marker.
2. **No contract, user-named criteria or artifact** — use them verbatim as the baseline. A clean result closes with the report, the receipt, and the seal-log line only.
3. **Nothing to pin** — report the missing input and stop:
   「找不到可驗收的目標或條文：請指定 CONTRACT.md、變更範圍，或直接列出驗收條件。」
   Do not reconstruct success from the author's memory or completion statement.

Branches 2 and 3 never write a marker.

## Size the verification

Read `references/verification-effort.md` before dispatch and record, in the receipt's header, the required criteria, the protected outcomes, the plausible failure paths, the permitted checks, and a finite check-and-repair allowance. For a bounded change, start with one independent review and one focused recheck after authorized repairs unless the evidence justifies a different allowance.

Choose checks by the causal risk of the changed behavior. Use the narrowest real checks that establish the required outcome, expanding only when shared behavior, integration boundaries, or concrete findings justify it. Do not run a full suite, a fixed mandate, or a mutation sweep merely because this skill was invoked. A requirement constant (a format string, a color value, a message) is settled by an exact comparison; a mutation probe is used only when it resolves a specific consequential uncertainty about whether the available verification would detect a plausible broken result, with the mutation, expected detector, baseline, isolation, and stopping point named first.

Report effort separately from the accepted outcome: the verifier supplies evidence; the main session owns continuation and the allowance.

## Dispatch the verifier

Load `${CLAUDE_PLUGIN_ROOT}/agents/verifier.md` completely and dispatch a fresh, narrow-context verifier with the immutable target identity (paths plus commit or content hashes), the criteria, the raw evidence, relevant pre-existing baseline failures, and the permitted check scope and allowance. The verifier reports only; it does not repair, and it does not change acceptance.

Cover the affected real paths, including zero-test layers and adjacent independently verifiable conditions. A passed parameter is not proof its filter takes effect; a test that mocks the changed layer is not coverage of it. Preserve exact requirement constants and check consequential cross-surface behavior without mandating a particular implementation pattern.

When primary evidence disproves a contract premise, judge the result against that evidence and the user's actual outcome. Record the narrow premise correction and keep unaffected criteria in force. This is neither a literal-wording veto nor permission to redesign the user's scope.

## Repair, recheck, stop

The main session may repair a finding only when the original request already includes implementation or fixing and the change remains authorized and in scope. A verification-only request stays read-only even for a serious defect: report the blocker instead. Risk severity does not create permission.

After an authorized repair, independently recheck the finding and the affected acceptance paths; do not restart an unrelated full review. At the declared allowance, on a repeated no-progress hypothesis, or when the fix would grow into a wider refactor, stop the cycle and return to the user: the required gap, the evidence gained, the work spent, bounded alternatives, and the next proposed allowance. Further work needs a reason tied to a remaining required outcome and a renewed allowance, not merely another possible test. Routine internal replanning stays internal; only a user-owned tradeoff or an authority change requires asking the user. Exhaustion never converts unverified into passed.

Use isolated disposable copies for any authorized mutation probe; never inject a probe into the user's live worktree or external state. If isolation or recovery is not available, choose non-mutating evidence and report its limitation.

## Receipt, marker, seal-log

Write the receipt to `.codex/seal/<slug>-<run>.md` (create the directory if needed; `<slug>` from the contract or the artifact, `<run>` an ISO date plus a counter). Its shape is the receipt section of `../contract/references/acceptance.md`: target identity, acceptance reference, per-criterion result with evidence, independence, observations, outcome, remaining limits. Observe the target identity again before claiming the receipt applies; a changed hash means recheck the affected criteria, not reuse the old result.

Independent success requires: every required criterion supported by evidence, no unresolved blocker, verifier independence available, and unchanged target identity since verification. On independent success in branch 1, write the sealed marker on line 2 of CONTRACT.md, immediately after the H1, in the grammar `$contract` owns:

```
> STATUS: sealed（{ISO 日期}）— {五點結果一行摘要}
```

The summary slot carries one line from the receipt's outcome. Idempotent: a re-seal overwrites the existing marker in place. Detection, here and in `$ship`, reads only the first three lines:

```bash
head -3 "$f" | grep -qF '> STATUS: sealed'
```

Then append the seal-log line: `result` is `pass` when nothing was repaired, `fixed` when authorized repairs were rechecked clean, `unresolved` when a required gap remains.

## Report

Independent success:
「封緘完成：{N} 條條文全數支持，{K} 處修正已複驗，收據 {path}，已蓋 sealed 標記（seal-log: pass|fixed）。」

Allowance reached or gap remaining:
「驗證額度已達：{N} 項未清如下，未蓋章（seal-log: unresolved），收據 {path}。」 followed by the gap list, evidence gained, work spent, and the proposed next allowance.

No contract (branch 2):
「驗證完成（無合約，未蓋章）：{N} 條條件 {結果摘要}，收據 {path}（seal-log: {result}）。」

The report never presents an author-only check as independent, never marks a required observation as unneeded because it could not run, and never hides a pre-existing baseline failure it scoped out.

## Not-for boundaries

- Cross-perspective re-verification of any model output → `$review`.
- Pinning criteria before work starts → `$contract`.
- Diagnosing a failing behavior → `$hunt`.
