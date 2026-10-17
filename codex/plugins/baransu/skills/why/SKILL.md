---
name: why
description: "Explains why code or a design decision has its current shape, from repo history, agent plans and transcripts, and connected docs; each claim cited and tiered, gaps named. Trigger On '$baransu:why', '為什麼這樣寫', '當初為什麼', '這段的由來', 'design rationale'. Not for a current failure ($baransu:hunt), how it runs ($baransu:how), or whether to change it ($baransu:think)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# why — the reasons behind the shape

Code shows what it does, not why it exists. The reasons sit in commits, PR threads, plans, conversations and docs, and every one of those records is partial. This skill collects what the record actually says about a target, keeps it apart from what can only be inferred, and says plainly where the record runs out. `$baransu:how` answers what the code does; `$baransu:why` answers what forces gave it this shape.

The default this skill corrects: given a "why" question, the model reads the code, finds a tidy reason that would justify it, and states that reason as fact. A confident guess is worse than an honest gap, because the user will act on it.

All user-facing output is in Traditional Chinese; keep the five tier labels (Direct / Supported / Inferred / Speculative / Unknown) in English.

## Outcome Contract

- **Outcome**: A cited answer to one "why" question about a pinned target, every claim placed in one confidence tier, with the sources searched and the gaps named.
- **Done when**: The code anchor is built; every evidence class in `references/sources.md` has a line saying it was searched, why it was not, or that its investigator did not return; every claim in 找到什麼 has a citation; 不知道什麼 names concrete searches that came back empty (or says why the record was complete); the answer has been presented.
- **Evidence**: The citations themselves (commit hash, PR number, `file:line`, plan path, transcript file and line, doc URL) and the 查了哪些來源 list.
- **Output**: A Traditional Chinese answer in the conversation, in the shape under Present. No file is written.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`.

## 1. Pin the target and the question

The target is a piece of code, a pattern, a feature, a config value, or a named decision. The question is what the user wants explained: a design choice, a tradeoff, a threshold, an edge case it guards, an outside constraint, code that looks dead, or the whole history.

If the target is vague, take the best reading from the conversation (open files, recent edits, what was just discussed), state that reading in one line so the user can redirect, and proceed. If the user's question carries a guess ("I assume this is for performance?"), treat the guess as one hypothesis to test, never as the answer to confirm.

## 2. Build the code anchor

Before searching anywhere else, collect: file paths and line ranges, the key symbols, the commits that last touched the target, the PR numbers in those commit subjects, and any ticket IDs. The usual commands:

```bash
git blame -L <start>,<end> -- <file>
git log --follow --oneline -- <file>
git log -S '<exact string>' --oneline -- <file>   # commits that added or removed it
git log -1 --format=%B <commit>
gh pr view <number> --json title,body,comments,reviews,closingIssuesReferences
```

When the target has been deleted (the question is why something was removed), anchor on the removal instead: `git log --all --diff-filter=D --oneline -- <old path>` finds the commit that deleted it, and `git show <commit>^:<old path>` shows its last version; in 程式在哪, give that commit and the old paths.

Note the dates of the commits that matter, and any session link a commit carries (a `Claude-Session:` trailer or a session URL in the message): the dates bound the transcript search, and a session link says where the deliberation happened.

## 3. Search the evidence, nearest first

`references/sources.md` lists the four evidence classes and how to search each: the repo record, the agent decision record, connected doc sources, and upstream material. Search them in that order, because each is cheaper and closer to the code than the next:

1. Search classes 1 and 2 yourself, in this session. They are local files; no agent is needed.
2. Go further only when what you found points further — a ticket or doc link, a person or meeting named, a workaround for a dependency, two sources disagreeing about something a check can settle — or when classes 1 and 2 left the question without a Direct answer. A Direct answer written only by an agent still leaves the user's own reason unknown; say so in 不知道什麼 rather than searching wider for it unless something points there. Class 4 (one upstream page, or a quick reproduction in a temporary directory) you do yourself. Class 3 means searching connectors: dispatch one read-only investigator per connector worth searching (in Codex a native subagent instructed not to write; it keeps shell, file and connector access), all in one message, each with `references/investigator-prompt.md` filled in. When the host has no subagents, or a connector cannot be reached from one, search it yourself, one connector after another.

Every class gets a line in 查了哪些來源, whether searched or not. Stopping because classes 1 and 2 answered at the Direct tier and nothing pointed further is a valid line; so is "no matching tool in this session". An investigator that has not returned when you must answer is reported as 未完成, never guessed. An empty search is a result and is reported as one.

If the target looks defensive (null guard, retry, timeout, rate limit, feature flag, size cap), add incident terms to each search: a revert followed by a re-apply, a commit or plan that mentions an outage, a crash, or a user report.

## 4. Weigh the evidence

Read `references/epistemics.md` before writing the answer. It defines the five tiers, which words each tier may use, and the checks to run before presenting. The short form:

- A claim is Direct only when an author wrote the reason down. Code is evidence of what was done, never of why.
- Two sources that disagree are both shown, with citations. Do not pick the one that makes a cleaner story.
- Hypotheses that fit the evidence equally well are all shown, each with what speaks for it and what is missing.
- Spot-check any citation an investigator returned that the answer leans on: open it and confirm it says what was reported.

## 5. Present

Present the answer in this shape; drop a section that would be empty, except 不知道什麼 and 查了哪些來源, which are always present.

```
### 問題
一兩句重述使用者問的事。

### 程式在哪
檔案、行號、關鍵符號，兩三行讓沒看過的人定位。

### 找到什麼
- **[Direct]** 主張。出處：<commit／PR／file:line／計畫路徑>。引文或摘要。
- **[Supported]** 主張。證據：<各項證據與它各自貢獻什麼>。

### 合理推論
- **[Inferred]** 帶保留語氣的主張。推理：<因為 A 和 B，所以可能 C>。

### 競爭假說
- 假說：…　支持：…　反證或缺口：…

### 不知道什麼
具體的缺口：查了哪裡、用什麼關鍵字、找到什麼（沒有，或只有旁支）。誰可能知道。

### 查了哪些來源
每一類一行，含沒查的類別與原因。

### 信心總結
一兩句：哪部分有直接證據、哪部分是推論、哪部分查不到。
```

When the question comes before a change to this code, close with a Preserve / Change / Avoid / Risk list (保留／可改／避開／風險) drawn from the findings; it is the premise list `$baransu:think` takes when deciding the change.

You may tighten the wording for the user, but never strengthen a tier: an Inferred claim stays hedged, and a gap stays a gap.

## Common failure modes

- **Recency bias.** The last commit is rarely the origin; the current shape is usually several decisions layered over each other. Trace back past the latest touch.
- **Rationalizing.** Code that makes sense today may have been written for a reason that no longer holds, or by copy-paste. Do not work backward from "it is good, so it was intended".
- **Absence as evidence.** "Nobody mentioned security" does not mean security was not a concern.
- **Over-reaching for the record.** Searching every transcript for every keyword floods the run with noise; bound the search by the commit dates first.
