# loop-pauses — /codex-skill-transfer PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/codex-skill-transfer issues no AskUserQuestion call of its own. Its
interaction points are the mode choice, design choices the checklist surfaces
but cannot make on the author's behalf, edits to a hand-maintained copy, and
the exit-2 refusals of the optional `scripts/transfer.py` helper.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 1 mode not stated | Input | Run Checklist mode (read-only) and write the report — never edit either copy without an explicit request |
| Step 1 unknown source shape | Input | Report `no progress: source matches no known shape` and end the run — never force a shape |
| Step 3 design choice the author owns (bundled-agent option A/B/C, manifest format, omitting a Claude-only component, marketplace layout) | Input | Record it under 待查 with the options and continue the checklist — never auto-pick |
| Port-by-hand edits to an existing hand-maintained Codex copy | **Authorization** | Edit only when the run's instructions explicitly request edits to that copy; otherwise stay in Checklist mode and report the proposed fixes |
| Generate mode: source/output overlap refusal (script exit 2) | Input | Re-invoke once with a fresh scratch directory outside the source tree; if none is derivable, report `no progress: no safe output directory` and end the run — never delete or move the source to make room |
| Generate mode: non-generated output refusal (script exit 2: output exists, non-empty, lacks the generated marker) | **Authorization** | Hard stop. Wiping a directory the script did not generate requires explicit human authorization; report `needs input` (LOOP_OUTCOME: blocked) — never remove the directory on the script's behalf, and never point the script at a hand-maintained copy |
| `context: fork` / `agent:` skill — two Codex paths surfaced for manual selection (skill-mapping.md §5) | Input | Record it under 待查 with the two paths, continue with the remaining sources — never auto-pick a path |
