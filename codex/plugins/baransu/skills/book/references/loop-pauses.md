# loop-pauses — /book PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Stage 0b 🔴 pre-interview gate (4-question AskUserQuestion batch) | Input | Skip the interview (same behavior as `--auto`); every unanswered question follows the preset's existing default. Annotate 「此處採預設：跳過訪談，全依 preset 預設」. |
| Stage 2A §0 🛑 fact-verify pending (WebSearch 0 results → AskUserQuestion, 3 options) | Input | Take 強制繼續 and continue to §1; annotate every unverified hit in the completion report: 「此處採預設：強制繼續，'{hit_clean}' 未經 WebSearch 驗證」. |
| Stage 3 §5 Core Asset Protocol — step 1 🔴 image-purpose confirmation + step 3 user visual confirm | Input | The protocol is interactive-only — no default can substitute a human visual confirmation. Default = do not enter the protocol: skip raster / photographic image acquisition entirely and emit SVG-only output (the SVG-required Constraint already guarantees diagrams). Annotate 「此處採預設：非互動驅動，略過 Core Asset 圖片取得，輸出僅含 SVG」. |

/book's remaining stops are error exits, not PAUSEs — the driver receives an explicit failure message: Stage 0 environment failures, Stage 1 acquire failures, Stage 3 §1 missing `tokens.css` abort, and the Stage 4 §1 🛑 second consecutive GATE FAIL. The Stage 2A §5 slug collision is a notify line, not a PAUSE.
