# AGENTS.md — fixture agent guidance

This file intentionally carries substantial standalone guidance and never
delegates to any other instruction file, so check_agent_context.py reports
the instruction-drift finding for this project.

## Working agreements

- Keep changes small and focused on a single concern.
- Prefer explicit configuration over implicit defaults.
- Record every decision in the pull-request description.
- Never commit secrets, tokens, or credentials.
- Ask before running anything destructive.

## Review expectations

- Every change needs a second pair of eyes before merge.
- Reviewers check naming, error handling, and input validation.
- Large diffs are split into reviewable slices first.

## Communication

- Surface blockers early instead of retrying silently.
- Summarize outcomes at the end of each working session.
- Escalate disagreements to the project owner with context.
