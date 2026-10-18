# Taste

The best code is the code never written. A change solves the whole problem with the least new code, in the way this repo already writes code.

**Why:** Everything a change adds is something a reader must read, a test must cover, and a maintainer must fix later. The repo's own way is the one the next contributor will copy.

**Pattern:**
1. **Hold the change to the repo's documented standards first.** `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, coding-standards files, and lint configs are places; a change that breaks one is cited by file and rule. Where a documented standard endorses something the moves below would flag, the standard wins. Anything a tool already enforces is the tool's job.
2. **Climb the ladder.** Does it need to exist? Is it already in this codebase? Does the standard library or platform do it? Does an installed dependency? Can it be one line a reader gets at a glance? Only then, the minimum new code. Name the rung the change skipped.
3. **Delete before adding.** Dead code, an unused option or parameter, a speculative feature, a stub, a near-copy that must change with its twin, a new dependency for a few lines.
4. **Reuse what exists.** New code that re-implements a helper the repo already has is a finding; name the existing path.
5. **Label smells as judgement calls.** Mysterious name; duplicated code; feature envy; data clumps; primitive obsession; repeated switches on one type; shotgun surgery; divergent change; speculative generality; message chains; middle man; refused bequest. Each is "possible X" with its fix, never a hard violation.
6. **Never cut what the goal carries.** Validation at trust boundaries, handling that prevents data loss, security, accessibility, calibration real hardware needs, anything the user asked for.
7. **Be lazy about the solution, never about the change.** A minimal change still reaches every caller, test, and fixture it breaks.
8. **Accept a shortcut that says its limit.** A marked shortcut naming its ceiling and its upgrade trigger is a decision; an unmarked one, or one past its ceiling, is a finding.
9. **Report taste only with its cost.** A finding of taste names what the current form costs a reader, a tester, or a maintainer; a preference with no cost is not reported.

**The test:** Could the same behaviour be delivered with fewer new lines, using something the repo or platform already has, without dropping anything the goal carries?

**You skipped this when** the change adds a helper the repo already has, or a dependency for something the standard library does.

Distinct from `structure.md`, which judges where boundaries go; this one judges how much code fills them.
