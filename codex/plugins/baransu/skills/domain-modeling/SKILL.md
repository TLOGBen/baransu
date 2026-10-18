---
name: domain-modeling
description: "Builds and sharpens a project's domain model while the user designs: challenges and settles terms in CONTEXT.md and records decisions as ADRs under docs/adr/. Trigger On '$baransu:domain-modeling', '詞彙表', '名詞定義', '統一用詞', '記一筆 ADR', 'glossary'. Not for choosing which way to build ($baransu:think)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# domain-modeling — keep the project's words and decisions on disk

Actively build and sharpen the project's domain model while the user designs. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and the decisions down the moment they crystallise. Merely *reading* `CONTEXT.md` for vocabulary is not this skill — any skill can do that in one line. This skill is for when the model is being changed, not just consumed.

## Outcome Contract

- **Outcome**: The project's domain language and its hard-to-reverse decisions are on disk as they settle: every term resolved in the session sits in the right `CONTEXT.md` in the glossary format, every conflict, fuzzy word, or code contradiction surfaced was either resolved or left outside the glossary as a named open question, and an ADR exists for each qualifying decision the user accepted one for.
- **Done when**: each resolved term was written into `CONTEXT.md` when it was resolved, not batched at the end; each unresolved term is named back to the user with the one-sentence answer an SME must give; every ADR offered met all three conditions, and every one the user accepted is written under the right `docs/adr/` with the next free number; the closing message lists each file changed with one line each.
- **Evidence**: The diffs of `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/` files; the file:line citation behind every term drawn from code; the open-question list.
- **Output**: Created or updated `CONTEXT.md`, `CONTEXT-MAP.md` (multi-context repos only), and `docs/adr/NNNN-<slug>.md` in the user's project; Traditional Chinese conversation.
- **Automation**: ultracode=neutral, loop=not-drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## User-facing language

All user-facing output is in Traditional Chinese unless the user explicitly asks for another language. Newly authored human-readable headings and prose in `CONTEXT.md`, `CONTEXT-MAP.md`, and ADRs default to Traditional Chinese as well. When extending an existing glossary or ADR set, keep its established document language; canonical domain terms always win. Code, identifiers, commands, and quoted source text stay as written.

## Division of labour with $baransu:think

`$baransu:think` deliberates: it restates, takes a stance, and writes only its own plan under `.codex/think/`, never a project file. When its restatement leans on the glossary, or its plan names a decision that meets the three ADR conditions, it points here. This skill owns `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/`: it writes them, and it does not take a stance on which way to build or write a plan. When the conversation turns into choosing a direction, say that the question belongs to `$baransu:think` and keep this skill to the words and the records.

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Infer which structure applies: a `CONTEXT-MAP.md` means read it to find the contexts; only a root `CONTEXT.md` means a single context; neither means create a root `CONTEXT.md` when the first term is resolved. When several contexts exist, infer which one the current topic belongs to; if that is unclear, ask.

Create files lazily: only when there is something to write. No `CONTEXT.md` yet — create it when the first term is resolved. No `docs/adr/` yet — create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately — for example 「詞彙表把『取消』定義成 X，但你這裡的意思像是 Y。是哪一個？」

### Sharpen fuzzy language

When the user uses a vague or overloaded term, propose a precise canonical one — for example 「你說的『帳號』是指 Customer 還是 User？這兩個是不同的東西。」

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. Surface a contradiction when one appears — for example 「程式碼是整張 Order 一起取消，但你剛說可以部分取消。哪個才對？」

When the model is drawn from an existing system, find the data first — schemas, DDL, record layouts, and message shapes are more truthful than the procedural code — then map who touches each structure. A term enters the glossary from the structure it names, cited by file:line. Admit only business rules: a rule that would be the same in any language is a business rule; a rule that exists only because of the technology is not. When the code and the user disagree and neither is confirmed, the term waits outside the glossary as an open question carrying the one-sentence answer an SME must give; never settle it by guessing.

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Do not batch these up; capture them as they happen, in the format in `references/context-format.md`.

`CONTEXT.md` is totally devoid of implementation details. It is not a spec, a scratch pad, or a store for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Offer to create an ADR only when all three are true:

1. **Hard to reverse**: changing your mind later has a meaningful cost.
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and one was picked for specific reasons.

If any of the three is missing, skip the ADR. Write it only after the user accepts the offer, in the format in `references/adr-format.md`.
