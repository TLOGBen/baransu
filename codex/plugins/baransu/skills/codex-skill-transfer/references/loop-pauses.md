# loop-pauses — /codex-skill-transfer PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/codex-skill-transfer issues no AskUserQuestion call of its own. Its
interaction points are refusal and choice surfaces around `scripts/transfer.py`
(exit-2 refusals) plus the manual-selection surfaces the transfer report opens.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Step 1 unknown source shape (script exit 2; marketplace-catalog conversion is manual per `marketplace-mapping.md`) | Input | Report `no progress: source matches no automated mode` and end the run — never force a mode |
| Step 2 source/output overlap refusal (script exit 2) | Input | Re-invoke once with the documented sibling output directory (`codex/` at repo root for baransu); if no sanctioned sibling is derivable, report `no progress: no safe output directory` and end the run — never delete or move the source to make room |
| Step 2 non-generated output refusal (script exit 2: output exists, non-empty, lacks the generated marker) | **Authorization** | Hard stop. Wiping a directory the script did not generate requires explicit human authorization; report `needs input` (LOOP_OUTCOME: blocked) — never remove the directory on the script's behalf |
| `context: fork` / `agent:` skill skipped — three Codex paths surfaced for manual selection (skill-mapping.md §5) | Input | Keep the skip: record it under the report's 需人工檢視 section with the three paths, continue porting the remaining sources — never auto-pick a path |
| Step 2 inline (in-conversation) port mode | — (not reachable) | Inline mode exists only on explicit user request; a non-interactive run always uses the script |
