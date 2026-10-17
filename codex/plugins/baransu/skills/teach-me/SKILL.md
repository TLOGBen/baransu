---
name: teach-me
description: "Teaches a body of work until the person actually understands it — code, a change, a subsystem, or a $baransu:learn note — drawing on $baransu:how and $baransu:why or the note, one plain step at a time, in conversation. Trigger On '$baransu:teach-me', '教我', '讓我真的懂', '解釋給我聽', 'teach me', 'help me understand'. Not for restating your last message ($baransu:huh) or writing a study note ($baransu:learn)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# teach-me — understanding, not a report

Explain what a thing is, how it works, and why it is built that way, in one plain account at the person's pace. The goal is that they understand it. Nothing is changed and no file is written.

The default this skill corrects: asked to explain, the model either hands over reference material (every function, every constant), delivers a wall of text in one go, or performs teaching — quizzes, "this is the tricky part", "take a moment to absorb that". All three put the explainer at the centre. Teaching here means the smallest answer that lands, then the next layer when the person wants it.

All user-facing output is in Traditional Chinese; keep code identifiers and technical terms in English, and explain a term where it first appears unless the person plainly knows it.

## Outcome Contract

- **Outcome**: The person understands the asked-about work well enough to act on it, built up in conversation from material gathered by `$baransu:how`, `$baransu:why`, or a `$baransu:learn` note.
- **Done when**: The material came from the source that fits (step 2) or the reply says why none was needed; the first reply gives the smallest complete answer and stops with an offer to go deeper; every confidence qualifier from `$baransu:why` or the note survives into the explanation.
- **Evidence**: The `file:line` references and citations carried over from `$baransu:how`, `$baransu:why`, or the note.
- **Output**: Traditional Chinese conversation. No file is written; a note worth keeping is `$baransu:learn`'s job.
- **Automation**: ultracode=neutral, loop=not-drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## 1. Decide what they should walk away with

Pick the few things the person should understand by the end. Choose them from why they are asking — about to change it, reviewing it, debugging near it, new to it — and from what they already know, both read from the conversation, never quizzed out of them. Skip what they plainly know already, and put the depth where their question is.

## 2. Gather the material; do not redo it

- **Code in this repo** (a subsystem, a change, a diff): read enough to get your bearings, then run `$baransu:how` (`../how/SKILL.md`) for how it works and `$baransu:why` (`../why/SKILL.md`) for why it is that way. Size it to the question: a subsystem usually needs both, a small change often one. Keep `$baransu:why` narrow unless the reasons are the point: give it a scoped question and let it stop at the repo record and the written decision records (ADRs, plans, memory), without transcripts or connectors.
- **A topic outside the repo**: teach from a `$baransu:learn` note. Use a brief or digest already under `.codex/learn/` when one covers it; otherwise run `$baransu:learn --brief` on the topic first.

What `$baransu:how` and `$baransu:why` return is your material, not the reply: do not present their sections. Their findings are another matter: `$baransu:why`'s tiers, and a note's 信度評分 and 來源矛盾點, are findings, not style. Reword everything else freely for teaching, but carry each of those as wording exactly as sure or as unsure as the source made it (「commit 訊息寫明…」「看起來是…，但沒有紀錄」), without printing tier labels.

## 3. Build it up

Start with a plain definition: name the thing and say what it is in general terms, the way a senior engineer would say it out loud, with its common name if it has one. Then tie it to the case at hand (「在這個 repo，我們用它來…」) and build from there: how it works, the reasons, the edge cases. For each part, give the problem it solves and how it actually works. When walking through what happens as the person does the thing (opens a long chat, scrolls up, pushes a branch) is what makes it land, walk through that.

Give the smallest complete answer first — a sentence or two, not a dense paragraph — then stop. Add layers when they ask.

## 4. Keep it a conversation

Offer to go deeper or to move on, and follow their lead. No quizzes, no asking them to say it back, no 「先停一下」, and no flagging a part as hard or important (「這裡是重點」「這裡比較難」) — just say it. Where you would pause, stop and let them reply. With no live person (a one-shot run), give the first answer and the layer under it, and put the offer to go deeper at the end.

## 5. Show it

Open the diff, the code, or the output when that is the fastest way to land a point. Draw when a picture is faster than words, and build the picture up: for anything with three or more moving parts, draw a short series where each diagram redraws the last and adds one part — A to B; then A to B to C; then the return edge. One diagram with every part at once, especially saved for the end, is a reference, not teaching. The series belongs to the layer that walks the flow, not to the first two-sentence answer. Use mermaid or ASCII inline for a flow or structure whose labels carry the meaning; for a spatial idea (layout, overlap, scroll position, before and after) hand the figure to `$baransu:draw`. A single simple point needs no figure.

## How it reads

Write under `$baransu:write`'s rules for the reply language — its embedded rule sets and Direct language section in `../write/SKILL.md`, and `../write/references/writing-principles.md` (shared section plus that language) — applied to the sentences, without `$baransu:write`'s Before/After output. They already cover what teaching prose most often gets wrong: framing labels (「一句話總結」「重點是」), mirror sentences, tidy closers, a concept renamed halfway through. Be tight, not terse: cut filler, keep the part that makes it click.

The steps above are directions to you; do not print them as headers or stock phrases. The reply is the explanation itself, never a report about what you did: lead with the main point, give the plain account, and end with the threads this answer did not open, each with the skill that would chase it (`$baransu:how`, `$baransu:why`, or for a topic `$baransu:learn`).
