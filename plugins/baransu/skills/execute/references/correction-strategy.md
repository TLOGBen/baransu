# Composite correction_strategy — schema and assembly rules

Built by the orchestrator in SKILL.md §4b failure escalation (at
`failure_count == 2`, from smart-friend output) and passed to the next
impl-agent dispatch. Content moved verbatim from SKILL.md; semantics unchanged.

**Composite `correction_strategy`** (built by orchestrator from smart-friend output for the next impl dispatch):

```
correction_strategy:
  text: |
    [broader guidance from smart-friend]
    {smart-friend.broader_guidance}
    [/broader guidance]

    {smart-friend.correction_strategy}
  investigate_files: {smart-friend.investigate_files}   # passed through as-is; absent → []
```

Rules:
- `broader_guidance` is **prepended** to `text` wrapped in the paired markers
  `[broader guidance from smart-friend]` ... `[/broader guidance]` so newlines
  or special characters in the over-scope note cannot bleed into the body.
  Both markers MUST appear (paired); never emit one without the other.
- If `smart-friend.broader_guidance` is empty (`""` or absent), still wrap the
  empty string with the paired markers — downstream parsing relies on the pair.
- `investigate_files` is forwarded verbatim; orchestrator does not filter it.
- This composite schema is consumed by **`agents/impl-agent.md` 通用原則 5
  (`correction_strategy`)**, which mandates Read-before-Red-gate on every
  path in `investigate_files`. Field names here MUST match that schema
  exactly; any drift is a cross-file invariant violation.
