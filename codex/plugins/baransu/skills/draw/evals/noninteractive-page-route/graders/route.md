---
type: llm
---

PASS if: The route description keeps map with needs-page, requires finalizing and delivering the map plus ui_brief.md after reading the hand-off rules, does not invoke ui, and reports page assembly deferred. It distinguishes the lookup ledger from page completion: require the real run to quote its actual checker output (this description-only case need not produce that output), explain that a missing lookup record fails and a complete lookup ledger may pass without a page; never interpret lookup PASS as assembled-page success.

FAIL if any required routing or exit behavior is missing or contradicted, or if it asserts that ledger-check must report assemble-page not reached.
