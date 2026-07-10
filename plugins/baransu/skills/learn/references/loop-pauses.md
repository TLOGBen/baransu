# loop-pauses — /learn PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 1 §2 `--topic` — /read paper-selection prompt (surfaced as-is) | Input | Select the top-ranked paper candidate.「此處採預設：取排序最高候選」 |
| Stage 2 §1 — ask for research topic when invocation lacks `--topic` (「請輸入這批資料的研究主題」) | Input | Derive `$TOPIC` from the input slug / URL keywords; annotate the derived value |
| Stage 2 §3 — scoring table confirmation | Input | Keep all scored sources; annotate |
| Stage 3 §2 — outline confirmation before fill-in | Input | Accept the outline as generated; carry any ⚠️ 需補充調查 markers into the report |
| Stage 4 §3 — gap handling (Stage 2 fallback) asks for additional sources | Input | Skip supplementation; keep the section with its ⚠️ marker; annotate the unfilled gap |
| Stage 4 §3.4 — retreat cap choice（繼續 / 跳過此節） | Input | Option 2 跳過此節 (continuing requires human-supplied sources); annotate the skipped section |
| Stage 2 §4b / Stage 5 §4 — slug ask when non-ASCII topic drops to empty | Input | Derive an English slug from the source slugs / URL keywords; if still empty use `learn-{YYYYMMDD-HHMMSS}`; annotate the derived value |

learn's terminal stops (all-lanes-fail in §3.5; environment failures surfaced by
/read's own Stage 0 on the delegated URL / --topic routes) are error exits, not
PAUSEs — the driver receives an explicit failure message.
