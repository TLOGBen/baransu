# loop-pauses — /read PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2. Every candidate selection below is an **Input** PAUSE.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 1 §1 `--topic` — paper candidate selection (`candidate-selection.md` rounds) | Input | Top-ranked candidate under the lane's native sort order（【推薦】）.「此處採預設：取第 1 名」 |
| Stage 1 §2 `--web` — URL candidate selection | Input | Top-ranked candidate（【推薦】）.「此處採預設：取第 1 名」 |
| Stage 1 §3 `--gh` — repo candidate selection | Input | Top-ranked candidate（【推薦】）.「此處採預設：取第 1 名」 |
| Stage 1 §4 `--x` — tweet candidate selection | Input | Top-ranked candidate（【推薦】）.「此處採預設：取第 1 名」 |

/read's terminal stops (Stage 0 environment failures, `$CHROME_AVAILABLE=false`
for `--x`/`--chrome`, empty keyword, zero search results, zero glob matches) are
error exits, not PAUSEs — the driver receives an explicit failure message.
