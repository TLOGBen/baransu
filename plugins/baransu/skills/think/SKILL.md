---
name: think
description: 'Turn rough intent into a validated five-section approved plan — never produces code, scaffolding, or pseudo-code. Use whenever the user proposes a new feature, architecture decision, library choice, refactor, or data-model change, including 「怎麼設計」「哪種方法」 or "I want to build / refactor / migrate X", even without saying "plan first". 繁體中文輸出。 Not for debugging an existing error/報錯 (use /hunt) nor for writing actual code/scaffolding (/think never does that — hand off to downstream implement or /analyze).'
---

# think — deliberate before you build

Claude's default when a user says "build X" is to start writing code almost immediately — often against a version of X that Claude *assumed* matched the user, rather than one both sides actually agreed on. This skill exists to correct that default.

The deliverable of `/think` is not code. It's an **approved plan** that someone else (usually Claude, in the next turn) can hand off to implementation with zero remaining ambiguity.

If you find yourself thinking "I could just write this quickly" — that's exactly the default the skill is here to push against. Run the process.

---

## Outcome Contract

- **Outcome**: Converge a vague intent into a five-section plan explicitly approved by the user (or, in Evaluation mode, a single-line Kill / Keep / Pivot verdict), producing no code at any point.
- **Done when**: The user approves the final proposal at the Stage G four-option gate (AskUserQuestion), or explicitly abandons this round's plan; a free-text approval must be closed and recorded with 「收到，把這當成批准實作」.
- **Evidence**: The Stage G AskUserQuestion interaction result — one of the four options selected, or the closing sentence of a free-text approval has been emitted.
- **Output**: The 繁中 five-section plan presented in the conversation (or the verdict + three reasons); after approval, persist `.claude/think/<slug>.md` (the plan verbatim) and `.claude/think/<slug>.html` (HTML work journal, containing an 「執行日誌」 section, per the `_shared/output-journal.md` contract), and send them via SendUserFile; then hand off to /analyze or implement directly per _shared/tdd.md.
- **Automation**: ultracode=neutral, loop=not-drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## The iron rule

Until the user has explicitly approved the final proposal through `AskUserQuestion` (Stage G), do **not** produce:

- Production code, even one-liners
- Scaffolding, directory trees, file layouts written out
- Pseudo-code, even "illustrative"
- Config files, YAML snippets, schema definitions
- `TODO: implement` stubs

You *may* reference existing file paths when citing what you found, and you *may* draw ASCII diagrams of component relationships (Stage E). ASCII diagrams must show logical component, service, or data-flow relationships only — no directory names, file paths, or module paths. Everything else is code, and code is forbidden.

Why so strict: the whole point is that a premature code artefact anchors the user — once they see a draft, they argue about its wording rather than its architecture. The value of `/think` is the conversation *before* code, not a head start on code.

---

## User-facing language

All output shown to the user — alignment questions, proposals, the final plan, `AskUserQuestion` labels — must be in **Traditional Chinese (繁體中文)**. The body of this SKILL.md is in English because it is agent-facing.

---

## Step 0 — Pick a mode

Mode selection has two layers. The first picks the **kind** of output (Plan vs Evaluation); the second — only if Plan — picks the **depth** (Lightweight vs Full). These two questions are independent; don't collapse them into a flat three-way choice.

### Design.md soft-read

Before mode selection, check for a DESIGN.md at the project root:
1. Run `git rev-parse --show-toplevel 2>/dev/null`. If empty / fails, skip silently.
2. If `{root}/DESIGN.md` exists, read it into context and output one line in 繁中: 「已載入 DESIGN.md，視覺規格已參考」
3. If absent, skip silently. Non-blocking.

Rationale: /think frequently discusses UI / design choices; loading DESIGN.md into context early avoids being blind to the "existing design language" during Stage A alignment.

### First layer — Plan vs Evaluation (kind divergence)

Decide the kind of output the user wants:

- **Plan** — how to build / fix / refactor something. Produces a five-section plan (Stages A-G). This is the default.
- **Evaluation** — a value judgment about whether something should exist, be kept, or be removed. Produces a single-line verdict (Kill / Keep / Pivot) plus three reasons.

Pick **Evaluation** when the user's intent matches one of these triggers and the user is NOT in the middle of debugging an error:
「判断一下」, 「值不值得」, 「有没有必要」, 「我不想做」, 「商业前景」, "should we keep this", "is this worth it".

**Disambiguation — Evaluation vs `/hunt`**: when the trigger is paired with an error / bug context (「判断一下这个报错」, 「判断这个错误」, 「这个报错值不值得修」, etc.), route to `/hunt` instead. Evaluation Mode is strictly for value / existence judgments, not debugging.

If Plan is picked, continue to the second layer. If Evaluation is picked, skip the depth layer and jump to **Evaluation Mode** (below).

### Second layer — Plan depth (Lightweight vs Full)

Applies only inside the Plan branch. Get this wrong and you either bury a small fix in ceremony, or let a design decision slip through without alignment.

**Lightweight mode** applies when **all three** hold:
1. The user wants to fix a known problem, not build a new feature.
2. The scope is already clearly defined (specific bug, specific behaviour, specific file).
3. The only open question is "how to fix it" — not "what should this even do".

Typical phrasings: "fix the bug where…", "this throws when…", "this should return X but returns Y", "the test at line 42 fails because…".

**Full mode** applies when any of these are true:
- New feature, new subsystem, new module, new service.
- Architecture, data-model, library, or vendor decision.
- Refactor that changes more than one file's shape.
- Bug fix that on inspection hides a design decision.

### Escalation from Lightweight to Full (inside the Plan branch only)

If in Step 1 of Lightweight mode you find **3 or more substantively different fixes** (not the-same-fix-at-different-intensities), that's a disguised design decision. Tell the user plainly: "this looks like a bug fix, but there are three fundamentally different ways to fix it with real trade-offs — switching to full `/think`", and jump to Stage A.

This rule is scoped to **Lightweight → Full inside Plan**. There is no automatic escalation between Plan and Evaluation, nor demotion between Full and Lightweight when started from Evaluation. If mid-flow you discover the outer layer was wrong (e.g. realised the user wants a Plan instead of an Evaluation), stop and tell them to restart `/think` — mode switching mid-stream is not supported.

### If Lightweight is rejected

Ask which part was wrong (file? approach? risk analysis?), correct it, and propose once more. If the second proposal is also rejected and the disagreement is *growing* rather than narrowing — escalate to Full mode.

---

## Lightweight mode

Total output: ~10 lines in Traditional Chinese, then wait.

Output template (translated to 繁體中文 in actual output):

```
推薦修法：<2-3 句話：改什麼、在哪個檔案/行數附近、為什麼>

涉及檔案：
- path/to/file1
- path/to/file2
（若超過 5 個檔案，明確說「此修法牽動 N 個檔案，比一般 bug fix 大，請確認是否仍走輕量路徑」）

風險：<一個具體的風險：這個修法可能讓什麼東西壞掉>
驗證方式：<一句話：怎麼知道那個風險沒發生——某個測試、某個手動操作、某個 log>

請回覆「可以」或「不行，因為…」。
```

Then stop. Wait for one round of user confirmation. Don't keep working.

If the user says "可以" (or equivalent): you're done with `/think`. Implementation is the next turn's problem, not this skill's problem.

If the user instead asks to broaden Lightweight into Full ("actually let's plan this properly"), don't extend the current Lightweight in place — tell them to restart `/think` so the Full-mode Stages A-G run with a clean Alignment. Mode switching mid-stream is not supported (see Step 0).

---

## Evaluation Mode

Total output: ~10 lines in Traditional Chinese, then wait. This mode is for value / existence judgment — "should X exist, be kept, or removed". It is not for "how to build X" (that's Plan) and it is not for debugging (that's `/hunt`; see the Step 0 disambiguation rule).

### Output format (Kill / Keep / Pivot)

Line 1 is exactly one of **Kill** / **Keep** / **Pivot** as the verdict. No preamble, no hedging.

Then three reasons, each grounded in the user's **actual constraints** — time budget, motivation, business model, maintenance cost. Not generic trade-offs ("complexity could grow"); the kind of reason that only applies because this is *this* user's situation.

If verdict is **Pivot**: list specific directions, one per line, each actionable. Not "consider alternative approaches" — "switch from X to Y because Z".

If verdict is **Kill** or implies major rework: list impact scope (files touched, dependents, migration cost) before asking for confirmation.

Do not present options for the user to pick between. Do not use Plan's five-section template. Give one verdict, three reasons, and the impact block when applicable.

### Output template (translated to 繁體中文 in actual output)

```
**裁決：Kill / Keep / Pivot 之一**

理由：
- <基於使用者實際限制 1>
- <基於使用者實際限制 2>
- <基於使用者實際限制 3>

（Pivot 時補：可行方向）
- <具體方向 1>
- <具體方向 2>

（Kill 或重大重做時補：影響範圍）
- 涉及檔案：...
- 依賴者：...
- 遷移成本：...

請回覆「同意」或「不同意，因為…」。
```

Then stop. Wait for one round of user confirmation. Do not proceed to Plan's stages (A-G) — Evaluation produces a verdict, not a plan.

---

## Full mode — overview

The stages are ordered the way they are because each depends on the previous one. Don't reorder them.

```
A. Alignment (對焦)      — 3 rounds, no files read, close the gap on 目的/約束/成功
B. Take a stance         — recommended approach + what would falsify it
C. Official-first check  — framework-native / stdlib / well-maintained lib
D. Premise validation    — pwd, existing ADRs, prior art
E. Attack + complexity   — self-refute; file-count & component-count grading; deps list
F. Final plan            — the five-section schema
G. Approval              — AskUserQuestion with four options; downstream is direct implementation per _shared/tdd.md (small) or /analyze (medium-large)
```

Do **not** read any files, run any shell commands, or fetch any URLs before Stage A completes. The whole point of Stage A is to close the gap between Claude's understanding and the user's intent. Touching the codebase first anchors you to what's already there instead of what the user actually wants.

---

## Stage A — Alignment (對焦)

The single most common failure of `/think` is: Claude reads the user's first sentence, decides it understands, produces a beautifully structured plan for the *wrong problem*. Worse — users themselves often don't know exactly what they want until pushed to pick between concrete options.

Round 1: **目的 (purpose)** — what problem is actually being solved; what's in or out of scope-of-problem.
Round 2: **約束 (constraints)** — what can't change; what's the budget of time, files, dependencies, risk tolerance; what boundaries the solution must respect.
Round 3: **成功 (success)** — how we'll know it's done; what observable behaviour or metric marks "finished".

### How to run each round

Open the round by listing **3 specific things that feel ambiguous** in the user's current statement of this dimension. Don't list generic things ("what's the scale?") — list things grounded in what they actually said ("you said 'make it faster' but you haven't said whether latency or throughput matters more — those lead to different designs").

Then call `AskUserQuestion` with 2-3 options that are **fundamentally different in kind**, not "same direction, different intensity". Wrong: [A: cache for 5min, B: cache for 1hr, C: cache for 1day]. Right: [A: read-through cache, B: materialised view refreshed nightly, C: no cache, fix the slow query directly].

Exactly one option must be labelled **【推薦】** and should come first. Explain in the option's description *why* you think it's right given what the user has said. If none of the options fits, the user can pick "Other" and type a free answer — that's fine and often the most useful outcome.

### Don't do these during alignment

- Don't read files (Read tool, Glob, Grep): the point is you-vs-them, not you-vs-the-code.
- Don't search the web, fetch docs, check GitHub.
- Don't write draft plans or pseudo-options.
- Don't collapse multiple rounds into one mega-question — the sequential pressure of the three alignment rounds is part of what surfaces hidden assumptions.

If after Round 3 the user's answers still contradict each other, ask one more narrowing question. If that answer STILL contradicts a prior round, then stop alignment and surface the contradiction as a named Unknown carried into Stage F — do not proceed to Stage B on an unresolved purpose conflict.

---

## Stage B — Take a stance

Claude's default under uncertainty is hedging: "there are several ways to think about this", "it depends on your priorities", "both approaches are valid". This is the single most common failure mode of Claude as a technical advisor. It's polite and it's useless.

After Stage A, you have enough signal to have an opinion. State it.

### What stance-taking looks like

Open with one sentence: **「我的推薦是 X，理由是 Y。」**

Then give 2-3 options — one of which must be a **minimal option** (do the smallest thing that could possibly work; often "don't build this at all, use the existing Z"). One of them is your recommendation, marked **【推薦】**.

Then, crucially: **「什麼證據會推翻這個推薦？」** — list 1-3 concrete things. Examples:
- "if you tell me the traffic is actually 100× what I'm assuming, cache-aside breaks and we need X instead"
- "if there's an existing library version ≥ 2.3 in the lockfile, my custom implementation is obsolete"

This is the move that turns a hedge into a falsifiable claim. Without it, "I recommend X" is just an opinion; with it, the user knows exactly what information would change your mind.

### Forbidden phrases

If the words below are in your draft, delete them and rewrite:
- "There are many ways to approach this"
- "It depends on your priorities"
- "Both have trade-offs"
- "This is a design decision for you to make"

These are all ways of refusing to take a position. The user called `/think` because they wanted a technical lead, not a survey.

---

## Stage C — Official-first check

Before proposing any custom implementation, confirm there isn't a built-in or officially-recommended way.

1. **Framework primitives**: does the framework in use already solve this? (Vue `provide/inject`, Spring `@Transactional`, React `Context`, Django middleware, Rails concerns, etc.) Look at which framework the project is actually on (check package.json / pyproject.toml / go.mod etc).
2. **Current best-practice docs**: check the framework's current docs / migration guide for the recommended approach at the project's current version. Patterns that were idiomatic in v2 may be anti-patterns in v3.
3. **Well-maintained libraries**: is there an officially-endorsed or de-facto-standard library for this? Prefer it over hand-rolling.

If an official solution exists, it **must be Option 1** in the proposal.

If you're still recommending a custom solution over the official one, you owe the user a one-line explanation of why the official solution doesn't fit *this* situation (not a generic objection). "The official middleware doesn't let us inject per-request context without monkey-patching" is acceptable; "it's not flexible enough" is not.

Skipping this check and proposing a hand-rolled solution that the framework already offers is one of the most demoralising mistakes a design doc can make — the user spends a day building it, then discovers a stdlib function. Don't do that to them.

---

## Stage D — Premise validation

This stage catches the common failure where the whole plan is built on a wrong assumption about what's already there. Stage D also hosts one cross-Stage rule: when a premise comes from agent memory rather than direct observation, the rule below dispatches the premise to whichever downstream Stage (D / E / F) actually applies it.

1. **Location check**: `pwd` and `git rev-parse --show-toplevel`. Confirm we're in the directory the user thinks we are.
2. **Prior art inside the project**: look for existing ADRs, design docs, `docs/decisions/`, open issues, or the last 10-20 commits touching this area. Often the problem has been discussed — maybe even decided — already. Don't duplicate or contradict without naming what you're overriding.
3. **Prior art outside the project**: a quick search (GitHub, the framework's issue tracker, official docs) for "how do people solve X in Y". You're looking for either a solved pattern to borrow or a known gotcha to avoid.

Record what you found in one short paragraph as part of the proposal — the user should see that this check happened.

**Claim-cite-first**: any non-obvious premise must cite how it was verified — annotate it `(verified: <how>)` (e.g. DB query, changelog, file:line) — or be explicitly marked `(inferred: 未實查)` before anything downstream relies on it.

### Memory type mapping (when a premise comes from memory)

When a premise originates in agent memory (`decision`, `preference`, `principle`, `pattern`, `learning`, `fact`) rather than direct observation, map the memory type to its downstream effect — different types belong to different Stages, even though the mapping rule lives here:

| Memory type | Treated as | Verified in / applied by |
|---|---|---|
| `decision` / `preference` / `principle` | Planning constraint | Stage F (becomes a constraint input to the final plan) |
| `pattern` / `learning` | Design check | Stage E (informs attack-angle and complexity grading) |
| `fact` | Premise to verify | Stage D itself — confirm against current state before relying on it |

**Current state overrides memory.** The live repo, running services, current logs, tests, and remote state always overrule a remembered version. When they conflict, name the conflict in one sentence and go with the current state — never silently follow the memory.

This skill is currently the sole written source for the mapping above; CLAUDE.md does not encode memory-type semantics as of this version. If CLAUDE.md or any global rule ever adds a conflicting type mapping, **CLAUDE.md is authoritative** (global > skill-local).

---

## Stage E — Attack angles + complexity grading

Before writing the final five-section plan, stress-test your own proposal.

### Attack angles

Ask: "in what situation does this proposal break?" List 2-4 concrete failure scenarios. For each:
- If there's a fix, fold the fix into the proposal and say you did so.
- If the failure mode is fundamental, state it plainly in the **Approach** section so the user knows the boundary they're buying.

This is not a theatre of pessimism — it's calibration. A proposal whose author can't name where it breaks has almost certainly not been thought through.

### Complexity grading — be loud about scope

These thresholds force you to surface scope the user might not have realised they were agreeing to:

| Trigger | Required in proposal |
|---|---|
| Touches > 8 files, OR introduces a new service/process | Explicit "scope flag" sentence: "this is medium/large — N files, M new services" |
| > 3 components exchange data | ASCII diagram of the data flow; visually confirm there's no cycle (unless intentional) |
| Needs any API key, OAuth client, third-party account, external service, or new runtime dependency | Full list under **Key decisions**, each with one line on why needed and who'll provision it |

### The no-handwaving rule

The final plan must not contain any of:
- `TBD`, `TODO`, `FIXME`
- "we'll figure out later", "similar to step N", "standard approach"
- "some library that does X" (name the library)
- "the usual auth flow" (say which flow)

If you genuinely don't know something, it goes in **Unknowns** with a reason and an owner — not hidden inside an otherwise-confident plan. Vague phrases are where over-promising and under-delivering both come from.

---

## Stage F — The final plan (five-section schema)

Produce **exactly** this structure, in 繁體中文, with these exact section titles. The schema is fixed because downstream consumers (humans reviewing, or Claude reading the plan back to implement) are calibrated on it.

```
## Building（要做什麼）
<一段話，具體到讀的人能立刻想像出成品長什麼樣。避開抽象詞。>

## Not building（明確不做的事）
- <具體項目 1：為什麼不做>
- <具體項目 2：為什麼不做>
- ...
（至少列 3 項。如果想不到任何不做的事，代表還沒想清楚。）

## Approach（選了哪個方案及理由）
<選了 Stage B/C 的哪一個選項？為什麼選它而不是其他？
 如果是自製方案而非 Option 1（官方），說明為什麼官方方案不適用於這個情境。
 Stage E 的攻擊角度中，哪些 failure mode 是已接受的邊界？>

## Key decisions（關鍵決策）
1. <決策 1>：<為什麼這樣選；有什麼取捨>
2. <決策 2>：...
3. ...
（3-5 條。少於 3 條代表沒有實質決策；多於 5 條代表還可以再收斂。每條必須有「為什麼」，不只是「做什麼」。）

## Unknowns（已知不知道的事）
- <明確被延後的項目>：延後理由；由誰在何時決定
- ...
（如果沒有 unknown，寫「無」並解釋為什麼這個規模的工作不需要延後任何決定。）
```

Claim-cite-first applies to the plan itself: a non-obvious claim in any section carries `(verified: <how>)` or `(inferred: 未實查)` — an unmarked non-obvious claim is a handwave.

### Section-by-section defaults to correct

- **Building**: Claude's default is to describe the mechanism ("we'll add a handler that processes events from the queue"). Push harder: describe the *observable outcome* ("when a user uploads a CSV, within 30 seconds they see a confirmation email with row-count and error-row CSV attached").
- **Not building**: Claude's default is to skip this section or fill it with tautologies ("not building features outside scope"). Force concrete exclusions the user might have silently expected — retry logic? admin UI? migration of historical data? These are the fights that happen after merge if they're not explicitly out-of-scope now.
- **Approach**: Claude's default is to describe the chosen approach in isolation. The value is in the *contrast* — why this over the alternative we considered in Stage B.
- **Key decisions**: Claude's default is to list activities ("set up the database, add the endpoint"). Those aren't decisions, they're tasks. A decision has a "we could have done X, we're doing Y because Z".
- **Unknowns**: Claude's default is to suppress this section to look decisive. It's the opposite — leaving no unknowns listed is usually the sign of a plan that hasn't been stressed.

---

## Stage G — Approval (the four-option gate)

After the plan is presented, call `AskUserQuestion` with these four options. Keep the labels short and stable — same wording every invocation, so they're predictable to the user and cache-friendly.

```
question: "要怎麼處理這份計畫？"
header:   "決定"
options:
  1. label: "送 /review 再決定 【推薦】"
     description: "先用 /baransu:review 對這份計畫做獨立複審，review 完成後再決定是否批准實作。"
  2. label: "批准實作（完全授權）"
     description: "接受這份計畫；接下來我會找出最適合接手實作的 skill，摘要重點並直接交接過去。執行過程中自主判斷，不再過問使用者。"
  3. label: "還有地方要對焦"
     description: "某一節沒收斂；我會先確認新的疑慮是延伸還是另一件事——若是延伸，只重啟受影響的 stage；若是另一件事，從 Stage A 重新對焦。"
  4. label: "放棄"
     description: "整個方向不對或不想做了；結束 /think，不交接。"
```

### Handling each choice

**Option 1 — 送 /review 再決定.** Invoke `/baransu:review` on the five-section plan. Derive the review goal from the user's invocation context (typically: 「確認這份計畫邏輯自洽、沒有設計矛盾、KD 無遺漏 unknown」). After /review presents its findings: if findings point to substantive gaps — missing decisions, logic contradictions, underspecified Unknowns — treat them as Option 3 input and revise the affected section with the finding folded in, then re-present this gate. If findings are advisory or minor, return to this gate and let the user choose Option 2 or 3. The full loop is: `/think → /review → /think (revision) → gate → downstream`.

**Option 2 — 批准實作（完全授權）.** You are done with the deliberation phase. Do two things:

1. Identify the downstream path based on task size:
   - **Small task** (single-file or single-area change that fits one session): implement directly, building a red/green task list under the _shared/tdd.md discipline — the main session implements directly following `plugins/baransu/skills/_shared/tdd.md` §7; no skill handoff.
   - **Medium-to-large task** (spans ≥2 interdependent modules, context-rot risk): invoke `/baransu:analyze`.
   - If no path fits, say so — 「沒有完美接手的 skill，建議直接進入手寫實作」.
2. Produce a one-paragraph **handoff summary** in 繁體中文: what was approved, the key constraints, the first concrete step of implementation. Immediately continue with this summary as input — invoke `/baransu:analyze` for medium-to-large tasks, or begin the direct implementation for small tasks. Execute autonomously; do not ask the user for further confirmation during implementation unless a destructive or irreversible action arises.

**Option 3 — 還有地方要對焦.** Call `AskUserQuestion` to find out what needs re-alignment. Then determine whether the new concern is an **extension** of the current direction or a **different concern**:

- **Extension** (same goal, same problem, deeper constraint or refinement): restart only the affected stage with the user's new constraint folded in. Open the re-proposal with one sentence: 「本次修改了 X 假設/約束，因此 Y 和 Z 有調整」 so the diff is visible. If the extension path is taken three consecutive times without convergence, treat as a different concern and restart from Stage A.
- **Different concern** (goal changes, problem reframed, direction diverges): restart from Stage A. State clearly: 「這是一個不同的問題方向，重新從 Stage A 對焦。」

**Option 4 — 放棄.** End the skill. Don't argue. Don't offer a simplified version. If the user later returns with a different angle, that's a fresh `/think`.

### Work journal (after approval)

Once the plan is approved — Option 2 selected, a free-text approval closed with 「收到，把這當成批准實作」, or the plan sent onward after Option 1's review loop ends in approval — produce the persistent artifacts before handing off:

- [ ] Write the five-section plan verbatim to `.claude/think/<slug>.md` (slug: short kebab-case derived from the plan topic).
- [ ] Render an HTML work journal at `.claude/think/<slug>.html`, based on the book golden-template, per the shared contract in `plugins/baransu/skills/_shared/output-journal.md`. It contains the original skill output (the five-section plan) plus an 「執行日誌」 section, initially seeded with the approval record (who approved, which option, when).
- [ ] Send both files via `SendUserFile` with a one-line 繁中 caption（例：「計畫已落檔；執行日誌將隨實作持續追記」）.

During subsequent implementation, the 「執行日誌」 section MUST be continuously appended with off-spec decisions, forced changes, trade-offs, and anything else the user should know. **The implementing party owns the appending** — `/execute` on the medium-to-large path, or the main session implementing directly per `_shared/tdd.md` §7. /think's responsibility ends at creating the journal and naming this ownership in the handoff summary.

---

## When the user rejects a proposal mid-flow (not via Option 3)

If the user pushes back in free text instead of using Option 3 — same rules apply. Never restart from Stage A.

- Ask: 「哪個部分不符合預期？」 — force them to name a specific section.
- Come back with a narrower proposal. Lead with: 「本次修改了哪個假設或約束」 so they see the delta.
- If you get two rejections in a row and the second reason is *different in kind* from the first (concerns are spreading, not converging), stop and ask for an **anti-example**: 「請給我一個你絕對不要的方案長什麼樣」. Anti-examples often surface a constraint neither side realised was in play.

Do not loop more than 3 re-proposals on the same plan. If the third is also rejected, pause and suggest: 「我們可能在解的是錯的問題；要不要回到 Stage A 重新對焦 目的 / 約束 / 成功？」. This is the one legitimate reason to go back to the top.

---

## Gotchas

One Gotcha keeps its long-form prose because its value is in the multi-layer response. The rest are tabulated for quick scanning — each row pairs an observed mistake with the rule it should obey.

- **User fatigue during Stage A.** Three rounds of questions feels long to users who believe they've already been clear. When that pushback comes, don't skip — but explain why: 「這三輪是為了把我對你的理解縮到最小誤差；跳過的代價是最後的計畫會離你要的差一截」. Then press on. If they insist, you can collapse rounds 2 and 3 into one combined question, but never skip Round 1 (purpose) — purpose confusion is the most expensive kind.

| What happened | Rule |
|---|---|
| User said "just fix the bug quickly"; on inspection it's 4 fixes with real trade-offs | Tell them once it needs Full mode, then run it. No apology — apology signals you might skip next time |
| About to Read / Glob / Grep before Stage A finishes | Stop. If you already did, note it in Stage D's prior-art paragraph and move on; don't pretend it didn't happen |
| Stage B recommendation softened into "X might be good, though Y has merit" | Rewrite with commitment. The falsification bullets are the safety net; you don't also need to hedge the stance itself |
| `Unknowns` filled with bureaucratic placeholders ("scaling strategy: TBD", "monitoring: TODO") | Each unknown needs (a) a specific question, (b) a reason it can be deferred, (c) a person / time to resolve it. Otherwise it belongs back in Key decisions, unresolved |
| User said "looks good, go ahead" in free text instead of via `AskUserQuestion` | Accept it, but say 「收到，把這當成批准實作（完全授權）」 so there's a clear recorded moment. The four-option gate is the audit trail |
| User asks "can we just add X?" after seeing the plan in Stage F | Small fit → fold into Building, note in Key decisions. Real extension (new file, new decision) → treat as Option 3 「還有地方要對焦」 and re-propose |
| Files moved to `~/project`, but the repo actually lives at `~/www/project` | Run `pwd` (and `git rev-parse --show-toplevel`) before the first filesystem operation in Stage D. Never assume which checkout the user has in mind |
| Planned an MCP workflow without checking whether the MCP server was loaded | Verify tool / server availability before handoff, not mid-implementation. Mid-flow "missing server" pauses cost more than the upfront check |
| Slid a second language or runtime into a single-stack project ("just a small Rust helper for the Node app") | Never add a new language or runtime without explicit approval. Surface the stack expansion as a Key decision, not an implementation detail |
| User said 「判断一下这个报错」 and got routed into Evaluation Mode | 「判断一下」 + error / bug context = debugging, route to `/hunt`. Evaluation Mode is strictly for value / existence judgments |

---

## Constraints

- Never produce code, scaffolding, file trees, pseudo-code, or config snippets before Stage G approval.
- Never run file-reading or web-fetching tools during Stage A.
- Never rename, add, or reorder the five final sections (Building / Not building / Approach / Key decisions / Unknowns).
- Never skip the stance-taking step (Stage B). Even if the right answer feels obvious, naming it and naming what would overturn it is the point.
- Never silently propose a custom solution without first doing the Stage C official-first check.
- All output shown to the user is in Traditional Chinese (繁體中文). English appears only inside this SKILL.md and in code identifiers / file paths the user themselves wrote.
