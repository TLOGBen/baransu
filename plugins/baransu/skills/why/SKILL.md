---
name: why
description: "Explains why code or a design decision has its current shape, from the commits, PR discussions and other records behind it; cites what the authors wrote, marks inferences, names what the record does not answer. Trigger On '/why', '為什麼這樣寫', '當初為什麼', '這段的由來', 'design rationale'. Not for a current failure (/hunt), how it runs (/how), or whether to change it (/think)."
argument-hint: "<file:line | symbol | decision> [question]"
user-invocable: true
---

# why — the reasons behind the shape

Answer from the record, not the code: read the commits and PR discussions that introduced the target and each later change, and other sources — plans under `.claude/`, ADRs, memory, session transcripts, connected docs — if that trail is thin. Cite what the authors wrote, mark your own inferences as inferences, and say what the record does not answer.

Answer in Traditional Chinese.

## Outcome Contract

- **Outcome**: A cited answer to one "why" question about the target.
- **Done when**: Every reason stated as the authors' carries a citation; every inference is marked as one; what the record does not answer is said.
- **Evidence**: The citations (commit hash, PR number, `file:line`, plan or transcript path, doc URL).
- **Output**: A Traditional Chinese answer in the conversation. No file is written.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.
