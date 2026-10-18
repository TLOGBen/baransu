# Taste — the smallest complete change, in the repo's own way

**Bedrock.** The best code is the code never written. A change solves the whole problem with the least new code, in the way this repo already writes code; everything it adds is something a reader must read, a test must cover, and a maintainer must fix later.

1. **The repo's documented standards come first.** `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, coding-standards files, and lint configs are places; a change that breaks one is a disagreement, cited by file and rule. Where a documented standard endorses something the articles below would flag, the standard wins. Anything a tool already enforces is the tool's job.
2. **The ladder.** Does it need to exist? Is it already in this codebase? Does the standard library or platform do it? Does an installed dependency? Can it be one line a reader gets at a glance? Only then the minimum new code. Name the rung the change skipped.
3. **Delete before adding.** Dead code, an unused option or parameter, a speculative feature, a stub, a near-copy that must change with its twin, a new dependency for a few lines.
4. **Reuse what exists.** New code that re-implements a helper the repo already has is a finding; name the existing path.
5. **Smells are judgement calls, labelled as such.** Mysterious name; duplicated code; feature envy; data clumps; primitive obsession; repeated switches on one type; shotgun surgery; divergent change; speculative generality; message chains; middle man; refused bequest. Each is "possible X" with its fix, never a hard violation.
6. **Never cut what the goal carries.** Validation at trust boundaries, handling that prevents data loss, security, accessibility, calibration real hardware needs, anything the user asked for.
7. **Lazy about the solution, never about the change.** A minimal change still reaches every caller, test, and fixture it breaks.
8. **A shortcut is honest when it says its limit.** A marked shortcut naming its ceiling and its upgrade trigger is a decision; an unmarked one, or one past its ceiling, is a finding.
9. **No style taste without a cost.** A finding of taste names what the current form costs a reader, a tester, or a maintainer; a preference with no cost is not reported.
