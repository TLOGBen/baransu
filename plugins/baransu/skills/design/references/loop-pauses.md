# loop-pauses — /design PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

The lint-verdict GATE is not listed: it is a mechanical exit-code gate (`check.py` exit 0/1), not an interaction point.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Gen Mode Step 1 direction questions (AskUserQuestion ×3–5, extreme-commitment axis, chart-capability) | Input | Derive every answer from the driving prompt / initial description. The extreme-commitment axis has NO recommended default by design (「Do not pre-select minimal」) — if the driving context does not name an extreme, abort gen mode with 「非互動執行缺 extreme 答案，gen mode 中止」 rather than substituting one. Chart-capability defaults to 「不宣告」 (its stated skip default). Annotate every substituted answer in the completion message. |
| Preset/Gen Mode 🔴 GATE — destructive overwrite (v1.2 residue detected) | **Authorization** | Hard stop (exit ≠ 0). Standing-authorizable: an explicit `--force` carried in the driving context counts as the recorded standing authorization; without it, never overwrite. |
