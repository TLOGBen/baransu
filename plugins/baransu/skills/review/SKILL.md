---
name: review
description: 'Independent re-verification of a concrete artifact, diff, or directly quoted claim: dispatches a fresh, narrow-context verifier — with additional perspective agents only for distinct consequential risks — never edits the target, and reports examined scope, findings with evidence, independence, and remaining limits; a clean review is a valid result. Trigger On 「看一下」「看看」「幫我看」「check 一下」「review 一下」, or casual "take a look at X". Not for auditing the user''s own project agent-config (route to /health) or closing a contract-banded task (use /seal). 繁體中文輸出。'
---

# review — find consequential defects in the user's actual target

Find consequential defects in the user's actual target; a clean review is a valid result（「乾淨的 review 也是有效的 review」）. Review-only means no edits.

All user-facing output is in Traditional Chinese.

## Outcome Contract

- **Outcome**: One independent re-verification of the pinned target against its review question, converging into a report of examined scope, findings with evidence, independence, and remaining limits.
- **Done when**: The target and question are pinned, the verifier has returned, each retained finding carries a location, trigger, supported consequence, and evidence, and the report states independence and limits; zero findings with stated scope is a complete result.
- **Evidence**: The verifier's returned observations and, for every retained finding, its evidence; the independence statement.
- **Output**: A Traditional Chinese review report in the conversation; `.claude/review/<slug>.md` when persistence is useful or requested (`/ship` archives that directory).
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## Pin the target and the question

Pin the supplied artifact, diff, or directly quoted claim and the review question. Inspect the real target and its relevant upstream and downstream context. Do not invent a diff base, a target, or a claim from an author's completion statement; if none can be pinned, ask for it and stop.

Review-only means no target, test, contract, configuration, or working-tree edits, including obvious typos and automatic formatting. A proposed fix remains a finding. Creating a requested separate review report does not authorize changing the reviewed material.

Reuse acceptance criteria when present (a `CONTRACT.md`, or criteria the user names); a contract is not a prerequisite for an ordinary review. Select the evidence and perspectives by causal risk, not fixed line-count tiers or an automatic multi-perspective fan-out.

## Dispatch an independent verifier

Load `${CLAUDE_PLUGIN_ROOT}/agents/verifier.md` completely and dispatch a fresh, narrow-context verifier with the target, the question, the acceptance when present, the permitted read and probe scope, and the raw evidence. Do not supply the author's defense or desired verdict. Use additional independent perspectives only for distinct consequential risks: the perspective agents under `${CLAUDE_PLUGIN_ROOT}/agents/` (architecture, quality, security, style, domain) are available for that, one per distinct risk, never as a default fan-out.

If independent execution is unavailable, or the current session authored the target, disclose the limitation. A same-context self-check can still find defects, but cannot earn an independent pass. Never assume a tool or model exists because it worked in another session.

## Judge the evidence

Verify consequential counts against the exact noun and scope claimed, per `../_shared/fact-check.md`; coverage is measured against real executed paths, and mocking the claimed layer does not test that layer. For business behavior, distinguish upstream-reachable states and authoritative requirements from what the target happens to accept.

Retain findings with a concrete location, triggering condition, supported consequence, and relevant evidence. Test a plausible disconfirming explanation for a severe claim; do not inflate confidence or severity from repeated agreement, and treat shared model agreement as one source, not independent ground truth.

Consolidate against the review goal. Separate defects, unknowns, and optional improvements; say which surviving findings are worth acting on and which are not, with a one-line reason each. Do not recommend a new mechanism without naming the consequential failure it addresses. Do not suppress a contradiction to your own earlier authoring decision by declaring it off-goal.

If reviewing a workflow or a skill, distinguish human-owned purpose from compensation for a model failure. Evaluate the actual failure conditions and enforcement surface; shorter instructions or a stronger model are not evidence that a long-run protection is obsolete. Do not promote a short scenario probe into a reliability claim for an hours-long coupled task.

Before extending a review into repeated probes, read `../seal/references/verification-effort.md`. A finding's validity does not itself authorize extra rounds, fixes, or a broader target.

## Report

### Plain-language presentation contract

- Make the immediate context explicit: what was reviewed, against which question, and how independent the check was.
- Explain each retained finding in plain Traditional Chinese: where it is, what triggers it, its practical impact, and the concrete next step the user can take.
- Keep each English technical term, but explain it in plain Traditional Chinese at its first use, in the same sentence or immediately after it.
- Do not add facts that the evidence has not established. This is presentation-only: it adds no PAUSE and does not replace the report's scope / findings / evidence / independence / limits shape.

Report examined scope, findings, evidence, independence, and remaining limits. No findings is not universal correctness; no tests is not an exempt layer; an absent required observation is unverified, not passed. Write `.claude/review/<slug>.md` (slug from the reviewed target) only when persistence is useful or the user asks; otherwise the conversation report is the deliverable.

Close with one line the user can act on:
「review 完成：{N} 項有後果的發現（{M} 項值得處理）、{U} 項未驗證；獨立性：{獨立／同 context 自檢}。」

## Not-for boundaries

- Auditing the user's project agent configuration and AI-maintainability → `/health`.
- Closing a contract-banded task with a receipt and the sealed marker → `/seal`.
- Verifying baransu's own skill structure → `scripts/verify-skills.py`.
