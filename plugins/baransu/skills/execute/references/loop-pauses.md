# loop-pauses — /execute PAUSE classification

Per-skill PAUSE classification for non-interactive drivers. The cross-cutting
vocabulary and semantics live in `../../_shared/loop-contract.md` (§1 vocabulary,
§2 PAUSE semantics, §3 hard stops); this file enumerates only /execute's own
interaction points. Re-verify when this skill's SKILL.md changes its interaction
points.

/execute has no AskUserQuestion. Its user-touch points are escalation notices;
by design it never stops early except Step 0.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 0 — spec dir missing or spec files incomplete → stop + escalate | **Authorization** | Hard stop. No default can substitute a missing /analyze spec |
| §4b task BLOCKED escalations (Red gate ⚠️ / persistent compile error / failure_count ≥ 3 / spec contradiction) | Input | Record BLOCKED, continue unblocked work (per skill's never-stop-early rule), annotate in final-report.md |
| §4d merge escalation (semantic conflict ❌ / Green broken ×3) | Input | Mark downstream groups BLOCKED, continue remaining steps, annotate in final-report.md |
| Step 5 E2E failure path | — (autonomous) | No interaction point in current SKILL.md: e2e-fix-agents once, one re-run, else record ❌ and proceed to Step 6 |
