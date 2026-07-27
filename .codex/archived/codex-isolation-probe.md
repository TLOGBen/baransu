# Codex subagent isolation probe

- Date: 2026-07-27
- Runtime: native collaboration subagent with `fork_turns: "none"`
- Parent-only fact tested: the latest user message explicitly requested
  `$baransu:review`.
- Prompt: ask the child to name the explicitly requested skill, or answer
  `CLEAN_CONTEXT` when parent context is unavailable.
- Result: `No skill was explicitly requested.`
- Conclusion: the child did not receive the parent conversation. Native
  subagents with `fork_turns: "none"` are sufficiently isolated for this
  `/review` dispatch.

The child did not emit the requested literal fallback, but its answer denied
the parent-only fact. Future reviews should continue passing the complete target,
claim checklist, goal, fact table, and exact bundled-agent definition explicitly.
