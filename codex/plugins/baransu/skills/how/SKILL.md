---
name: how
description: "Explains how a part of the codebase works, at the level a senior engineer needs to start working in it: architecture, runtime flow, and which layer owns what. Trigger On '$baransu:how', '這怎麼運作', '帶我看這塊', '這屬於哪一層', 'how does X work', 'walk me through'. Not for why it was built this way ($baransu:why), a current failure ($baransu:hunt), a paced lesson ($baransu:teach-me), or a picture ($baransu:draw)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# how — a working mental model of the code

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

## 1. Explain

Start one read-only subagent (told not to write; on a host without subagents, do it yourself) that explores and explains in one pass. Give it the user's question and this brief:

> You are writing an architectural explanation for a senior engineer. Explore the codebase and write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model. They should understand the architecture well enough to start working in it confidently. You have read-only access to the codebase. Write it in Traditional Chinese, keeping code identifiers in English.

## 2. Present

Present the subagent's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Outcome Contract

- **Outcome**: One explanation of the asked-about code that leaves a senior engineer able to start working in it.
- **Done when**: The subagent's explanation has been presented.
- **Evidence**: The files the explanation names.
- **Output**: A Traditional Chinese explanation in the conversation. No file is written.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.
