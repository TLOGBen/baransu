# loop-pauses — /seal PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Target-pin off-ramp (no materializable diff / contract / named artifact) | Authorization | Hard stop: report `needs-input`（「無可審工件」）upward; never fabricate a target, never seal from conversation memory |
| In-band direct fixes (unpinned surface, constant drift, minimal criteria-violation fix + pinning test) | Input | Standing-authorized by the skill's mandate: apply the fix, pair it with a pinning test, re-run to green, annotate 「此處採預設：帶內修正已直接套用」 in the report |
| Out-of-band findings (architectural rework, redesign, files outside the diff) | Authorization | Never apply; list in the report as pending and route to /review or /hunt |
| Mutation probe revert failure (working tree cannot be restored cleanly) | Authorization | Hard stop: report the dirty state verbatim; never commit or continue over probe residue |
