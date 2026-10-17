---
name: how
description: "Explains how a part of the codebase works, at the level a senior engineer needs to start working in it: runtime flow, key concepts, where things live, gotchas, and which layer owns what. Trigger On '$baransu:how', '這怎麼運作', '帶我看這塊', '這屬於哪一層', 'how does X work', 'walk me through'. Not for why it was built this way ($baransu:why) or a current failure ($baransu:hunt)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# how — a working mental model of the code

Answer "how does X work" the way a senior engineer onboards a colleague onto a subsystem: enough to build a mental model and start changing things with confidence, not so much that it reads like annotated source. `$baransu:why` answers what forces gave the code its shape; `$baransu:how` answers what it does and how the parts connect.

The default this skill corrects: asked how something works, the model either narrates the files it happened to open in order, or lists functions and constants. Both are reference material. An explanation names the few concepts that matter, walks the flow once, and says where the surprises are.

All user-facing output is in Traditional Chinese; keep code identifiers and technical terms in English, and explain a term where it first appears when the reader needs it to follow the flow — not the terms a senior engineer already knows.

## Outcome Contract

- **Outcome**: One explanation of the asked-about code — its purpose, key concepts, runtime flow, file map, and gotchas — grounded in files actually read.
- **Done when**: Every component, call, and file named in the answer was read in this run (by this session or an explorer) and is cited with `file:line`; contradictions between explorers were settled by reading the code; anything that could not be traced is listed under 還沒弄清楚; the answer has been presented.
- **Evidence**: The `file:line` references in the answer, any command or experiment whose result the answer uses, and, when explorers ran, their Files Read lists.
- **Output**: A Traditional Chinese explanation in the conversation, in the shape under Present. No file is written.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Read the entry points, then size what is left

If the scope is ambiguous, state your reading in one line and go; the user can redirect.

Read the entry points yourself first: the file the question names, the command's main file, the function that starts the flow. Then look at what is left to trace.

- **What is left fits in your own reading** — usually true for one module, one function, or a feature that lives in a few files, even when the question is "end to end": keep reading and explain. No agents.
- **What is left splits into two or more distinct slices** — a subsystem across several services, a cross-cutting feature, a whole architecture (the request path, the storage layer, the background jobs, the configuration): dispatch one read-only explorer per slice, 2 to 4 of them (in Codex a native subagent instructed not to write), all in one message, each with `references/explorer-prompt.md` filled in. When the host has no subagents, take the slices one after another yourself.

Running a read-only command (a verifier, a `--help`, a test) or a throwaway experiment in a temporary directory outside the repo is part of reading when the code alone leaves a behaviour uncertain; remove the experiment afterwards and say in the answer which facts came from a run.

## 2. Reconcile

When explorers ran, their findings overlap and sometimes disagree. Merge the overlaps; settle each disagreement by reading the code, not by picking the more confident explorer; join the slices into one picture. Anything you or an explorer could not trace stays open in the answer.

## 3. Present

Use these sections, dropping any that would be empty:

```
### 概觀
一兩段：這是什麼、做什麼、為什麼存在。只讀這段的人也能決定要不要往下讀。

### 關鍵概念
後面要用到的型別、服務或抽象，每個一句定義，不求完整。

### 怎麼運作
最長的一段。走一遍流程：什麼觸發它、一步步發生什麼、資料往哪裡去、在哪裡分岔。
用文字敘述，不寫 pseudocode；每個步驟點出檔案、函式與行號（file:line），讓讀者知道去哪看。

### 東西放在哪
簡短的檔案／目錄對照，只列開始在這裡工作需要的。

### 陷阱
不明顯的行為、容易誤用的地方、看起來該這樣運作其實不是的事。

### 還沒弄清楚
追不到或沒驗證的地方，各一句。沒有就省略這節。
```

How to write it:

- Concrete names over abstractions: "`UserService` calls `AuthClient.refresh()`", not "the service delegates to the client".
- When something is complex, say why it is complex; when it is simple, do not pad it.
- Add a diagram only when several components talk to each other or data moves through stages: mermaid for a sequence or flow whose labels carry the meaning, ASCII for a small relationship. A diagram that repeats the prose is decoration; leave it out.
- The sections above set the shape; `$baransu:write` governs the sentences: its embedded rule sets and Direct language section in `../write/SKILL.md`, and `../write/references/writing-principles.md` (shared section plus the reply language), without its Before/After output.

**Placement questions** ("where should this live", "which layer owns this") are answered from the code's existing layering: which module already owns that concept, and what the nearest precedent is. When the honest answer is a choice with tradeoffs rather than a precedent, say so and point to `$baransu:think`.

**Reasons** surface during any walkthrough ("why does it retry three times?"). Answer what the code does; when the user wants the reason, that is `$baransu:why`.
