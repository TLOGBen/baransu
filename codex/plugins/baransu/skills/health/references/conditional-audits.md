# Conditional audits — deep-only and conditional rubrics

Rubrics moved verbatim from `SKILL.md`. Load a section only when the load
condition stated in its `SKILL.md` pointer is met; do not read this file on
the default summary path.

## Contents

- [Long-running agent stop conditions](#long-running-agent-stop-conditions) — projects with loops or autonomous agents (Step 1c)
- [Conversation-derived guidance](#conversation-derived-guidance) — audits that read recent agent conversations (Step 3)
- [Hotspot ownership gaps](#hotspot-ownership-gaps) — deep audit only (Step 3)
- [Stale verifier cache output](#stale-verifier-cache-output) — verifier output pointing at temp paths (Step 3)

## Long-running agent stop conditions

For projects that use loops, autonomous agents, or any long-running agent flow, the project must define explicit stop conditions. An agent that never stops is a budget and safety incident waiting to happen.

Audit for these four hard stop signals; flag the absence of each as a Structural finding:

1. **No progress across two consecutive checkpoints.** Same files touched, same errors logged, no new commits/tests/output. Recommend killing the loop and surfacing the state, not retrying.
2. **Repeated identical failure.** Same stack trace, same error message, same failed assertion three times in a row means the hypothesis is wrong; more attempts will not help.
3. **Cost or token budget exceeded.** Project should declare a per-run budget (tokens, API spend, wall-clock minutes). Loop exits when the budget is hit, not when work is done.
4. **External blockers.** Merge conflict on the target branch, dependency lock the agent cannot resolve, missing credential, network unreachable. Any of these halt the loop and ask the user, not retry forever.

The stop conditions should live in tracked project docs (`AGENTS.md`, the loop's launch script, or a dedicated config), not only in the agent's prompt. Prompts are forgettable; tracked config is enforceable. Recommend hooks (PostToolUse on the relevant tools) over prompt instructions when the project supports them: a hook physically cannot be skipped, a prompt instruction can. Confirm the host's hook coverage before recommending one: some agents only fire PostToolUse for a subset of tools, so a fixup that must run after file edits may belong on a Stop or session-end hook instead.

## Conversation-derived guidance

**Conversation-derived guidance.** When a health audit reads recent agent conversations, do not recommend copying the conversation or a scorecard into docs. Recommend a candidate-matrix pass instead:

| Field | Question |
|---|---|
| Repeated failure | Did this recur across fixes, releases, agents, or user reports? |
| Durable invariant | Can the lesson be stated as a stable rule, not a dated incident summary? |
| Target layer | Should it live in project instructions, a reusable skill, a global rule, or private memory? |
| Verifier | Is there a deterministic command, script, artifact check, or runtime smoke that can enforce it? |
| Redaction risk | Does the lesson require local paths, issue numbers, customer details, machine state, secrets, or unpublished release facts? |

Layering rule: project-specific commands, app names, artifact names, and release rituals stay in the project; reusable workflows belong in shared skills; universal honesty and verification rules belong in global CLAUDE/AGENTS instructions; private user preferences and one-machine facts stay in memory. If the lesson cannot pass the redaction-risk field, keep it out of public guidance.

## Hotspot ownership gaps

**Hotspot ownership gaps.** In a deep audit, read `HOTSPOT OWNERSHIP SURFACE`. If a largest source file exceeds the hotspot threshold and `AGENTS.md` / `CLAUDE.md` / shared instruction files do not name who owns the hotspot, what boundary should stay stable, and which verification command covers it, report a Structural `WARN`. Do not treat documented large files as code rot by size alone; some modules are intentionally large.

## Stale verifier cache output

**Stale verifier cache output.** If validation output points at a deleted temp worktree or non-existent `/tmp` / `/private/tmp` file, parse the captured log with:

```bash
bash "$HEALTH_SCRIPTS_DIR/check-verifier-output.sh" . <log-file>
```

Only use this script for existing command output supplied by the user or generated during the current audit. Do not run project tests just to feed this checker. Known actions include `golangci-lint cache clean`, `go clean -cache -testcache`, and `npm cache verify`; unknown tools get a diagnostic rerun action.
