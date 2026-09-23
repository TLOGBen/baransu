---
name: hunt
description: 'Tracks a bug from symptom to root cause before any fix: picks the right
  observability tool (playwright / MCP db / LSP / logs / static analysis), bisects,
  confirms or discards hypotheses before touching code. Trigger On 「排查」「查 bug」「追問題」「為什麼失敗」,
  ''debug'', "what''s wrong", ''not working''. Not For: subjective UI taste (→ $baransu:ui);
  worth-fixing value calls / 值不值得修 (→ $baransu:think 存廢判決 Kill/Keep/Pivot).

  '
metadata:
  version: 1.0.0
  scope: investigation-and-fix
compatibility: Designed for Claude Code; ported to Codex.
---

# Hunt — Diagnose Before You Fix

Output 🥷 as the first line when hunt begins.

A patch applied to a symptom creates a new bug somewhere else.

**Do not touch code until you can state the root cause in one sentence:**
> 「根因是 [X]，因為 [證據]。」
Name a specific file, function, line, or condition. "A state management issue" is not a hypothesis. "Stale cache in `useUser` at `src/hooks/user.ts:42` because the dependency array is missing `userId`" is.

All user-facing output is in **Traditional Chinese (繁體中文)**.

### Plain-language presentation contract

- Make the immediate context explicit: what the user was doing or what event occurred.
- Explain the evidence-backed causal chain in plain Traditional Chinese: what the user was doing → triggering event or condition → concrete root cause → propagation path → visible symptom → practical impact → concrete next step.
- Keep each English technical term, but explain it in plain Traditional Chinese at its first use, in the same sentence or immediately after it.
- Do not add facts that the current evidence has not established. This is presentation-only: it adds no PAUSE and does not replace or rename any output schema below.

---

## Outcome Contract

- **Outcome**: The bug's root cause is stated in one sentence with confirming evidence before any fix, every observed symptom is mapped to that causal chain or separated by an independent evidence citation proving it does not share that chain (with its own incident id and next action), and the hunt is recorded for future reference.
- **Done when**: A Success-format report (根因/修復/確認方式/測試矩陣/迴歸守護) or a Handoff-format report is emitted with status 已解決 / 已解決（附帶條件說明）/ 受阻, and the case file `.codex/hunt-report/HUNT-YYYY-NNN.md` is written.
- **Evidence**: The report's 確認方式 line cites the instrument or test that confirmed the root cause; all 🎯HUNT-id tagged instruments removed after confirmation (`grep -rn "🎯HUNT-{YYYY-NNN}" --exclude-dir=.claude .` over the source/test dirs returns 0 matches).
- **Output**: The 繁中 success or handoff report plus the `.codex/hunt-report/HUNT-YYYY-NNN.md` case file.
- **Automation**: ultracode=assist, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
  In the same non-interactive pass, read `references/loop-pauses.md` for this skill's own PAUSE classification.

## Core constraints

- Do not touch code before stating the root cause in one sentence.
- Locate step (five questions) must complete before adding the first instrument.
- Before You Fix (impact analysis + test matrix) is mandatory before any fix.
- All instruments must carry a HUNT-id tag; remove all after root cause is confirmed.
- Confirm or Discard: one active yes/no probe at a time; contradicted hypotheses are discarded completely, not patched.
- A root cause cannot become `confirmed`, 「已解決」, or 「已解決（附帶條件說明）」 until every observed symptom maps to its causal chain, or an independent evidence citation proves the symptom does not share that chain and the case file records a separate incident id plus next action. A label alone is not separation evidence; otherwise the symptom stays `pending`.
- Before every probe, declare the exact minimal allowed field names for that hypothesis. Runtime observations, reporter results, verbatim RED evidence, and the case file may retain only those fields after redaction; never retain a complete object, payload, credential, token, cookie, PII, or private path. The tested systemd reporter example below uses `timestamp`, `target`, `probe`, `event`, and `result`; other probe types choose their own minimal allowlist.
- Three failed hypotheses triggers Handoff format, not another guess.
- DB-connected investigation tests must use transactions that always rollback.
- File writes and external API calls in investigation tests must use mocks.

## Rationalization Watch

When these thought patterns surface, stop and re-examine:

| Thought pattern | What it actually means | Rule |
|------|---------|------|
| "Let's try this" | No hypothesis — random walk | Stop. Write the hypothesis first, then act. |
| "I'm certain it's X" | Confidence is not evidence | Find one tool that can falsify it before proceeding. |
| "Probably the same as last time" | Mapping a known pattern onto a new symptom | Re-read the execution path from scratch. |
| "It works on my side" | Environment difference IS the bug | List every environment difference, then proceed. |
| "Restarting should fix it" | Avoiding the error message | Read the last error verbatim. Do not restart more than twice without new evidence. |

---

## Progress Signals

When these appear, the diagnosis is moving in the right direction:

| Signal | Meaning | Next step |
|------|------|------|
| "This log entry matches the hypothesis" | Positive evidence found | Find one independent cross-confirmation before fixing. |
| "I can predict what the next error will be" | Mental model is forming | Execute the prediction; if it matches, the model is correct. |
| "Root cause is in A, symptom appears in B" | Propagation path understood | Walk the call chain from A to B one frame at a time. |
| "I can write a test that fails on the old code" | Hypothesis is concrete enough to test | Write the test before touching code. |

Progress claims must map to at least one of the above signals.

Do not stay silent while investigating. Emit a short user-visible progress update after Locate, after each hypothesis is confirmed or discarded, and before a fix or Handoff. Each update says what was checked, what the evidence changed, and what concrete check comes next. Report evidence and decisions only; never expose private chain-of-thought.

---

## Fast Path — Trivial Bugs

Eligibility is measured **at routing time**, by running the Scope Blast grep early — one cheap grep over the pattern signature (Scope Blast Mode step 1). The close-stage blast then reuses/extends this early grep; it is not a second invention.

When BOTH hold: (1) the FIRST instrument, or the error message itself, confirms a one-sentence root cause, AND (2) the routing-time Scope Blast grep returns ≤3 matches still needing a fix/leave verdict (exclude matches inside `tests/` and `.codex/`) — the hunt may compress ceremony. The count that governs is post-exclusion matches requiring a verdict, not raw grep hits (raw hits may be 5 while relevant matches are 1; the Fast Path gates on the 1).

- Locate's five questions answered in one line each.
- Short-form case file: EXACTLY these five named sections — root cause / fix / 確認方式 / 迴歸守護 / blast verdicts. Before You Fix call-chain analysis and the hypothesis log are omitted on the Fast Path; both return the moment the run leaves the Fast Path (the first instrument fails to confirm, or the blast grows past 3).

When the Fast Path is taken, the case file (trace) MUST carry one routing log line — recognition must be auditable, not inferred from a section heading:
「Fast Path：首儀器定根因 ✓；blast 候選 N ≤3 → 壓縮儀式」

The case file, the Scope Blast, and 迴歸守護 are **never** skipped — only their length compresses. Compression does not defer creation either: even on the Fast Path, the case file is created at the Locate stage with `status: scoping` (short form is fine) and finalized at close — a file that first appears at the fix commit is end-of-hunt assembly, not a living record.

Case-memory fast path: before running the Locate-stage case search, check whether any case dirs exist at all (`.codex/hunt-report/` or hunt cases in `.codex/archived/`). If none exist (fresh project), skip the search ritual and log 「首獵：無既往案例」 in the case file instead.

---

## Tool Scan

Before investigating, pick the tool that can **observe the layer where the problem occurs** — not the first available tool:

| Tool | Observable layer | When to use |
|------|---------|---------|
| playwright / browser automation | UI behavior, render output | Visual errors, form flows, frontend logic |
| MCP db query tool | Data state, schema | Data inconsistency, FK errors, abnormal state values |
| LSP findReferences | Call chain structure | Who calls this method, what could be affected |
| bash logging / runtime instrument | Runtime intermediate values | Unexpected branch paths, condition values |
| Static code read | Static structure | When none of the above can observe the problem layer |

If the problem layer is uncertain, use bash logging first to confirm which module the symptom appears in, then choose the precise tool.

---

## Locate — Pin Down the Prey

After selecting a tool in Tool Scan, answer these five questions before adding any instrument:

1. **Event sequence**: Which operation or event does the bug appear after? (HTTP request, scheduled job, user action, data sync)
2. **Reproduction data**: Is there data available that triggers the bug? (request payload, DB record, log excerpt)
3. **Dirty data characteristics**: How does the dirty data differ from normal? (which field, which value, which condition)
4. **Environment**: Can the bug be reproduced in a test environment, or only in production?
5. **Observed symptoms**: List every reported or visible symptom verbatim enough to distinguish it, and keep that complete list in the case file. For each item record `pending`, its eventual causal-chain mapping, or `separate incident: <id / independent evidence citation / next action>`. Without the citation it remains `pending`.

These five questions determine where the first instrument goes. Adding a log before answering these questions = setting traps in a forest without knowing where the prey is.

Before instrumenting, run `python3 "./scripts/hunt-search.py" --keyword "<symptom term>"` to check whether a similar case was already solved; the search covers `.codex/hunt-report/` plus `$baransu:ship`-archived cases in `.codex/archived/`. Cite any hit in the report. (If no case dirs exist at all, apply the Fast Path's case-memory rule: skip the search and log 「首獵：無既往案例」.)

**Create the case file now, at the Locate stage — not after completion.** Allocate NNN = max(existing ids found by hunt-search.py across `.codex/hunt-report/` and archived cases) + 1, create `.codex/hunt-report/HUNT-YYYY-NNN.md` (format: `references/hunt-case-template.md`) with a `status: scoping` frontmatter field, and update the status as the hunt progresses: scoping → confirmed → fixed / handoff. On the Fast Path, scoping → fixed is a legal collapse — the `confirmed` hop may fold into the fix transition; off the Fast Path the three-state ladder stands. At creation, the trace entry recording the case file MUST quote the file's `status: scoping` frontmatter line verbatim, so early creation is externally checkable against the trace even in single-commit hunts.

### Reporter probe when local reproduction is unavailable

If the Environment answer is production-only or otherwise unavailable locally, first finish every safe local inventory/context scan. Then run no more local hypothesis probes while waiting: issue exactly this five-line reporter diagnostic block. Its five labels and explicit target/time/work/output bounds are fixed; generate the command and minimal return-field allowlist for the shell/runtime established at Locate. The block below is a tested Linux systemd example, not a universal command. In that example replace only the one known target selector. For a different known runtime, generate an equivalently bounded, quoted, read-only command; for an unknown runtime, use Handoff rather than invent one.

```
診斷目的：{一個 yes/no 假說}
唯讀命令：`bash -c 'target=$1; since=$2; journalctl --no-pager --since "$since" -u "$target" -n 80 -o json --output-fields=__REALTIME_TIMESTAMP,_SYSTEMD_UNIT,HUNT_PROBE,HUNT_EVENT,HUNT_RESULT | jq -c --arg target "$target" "{\"timestamp\": .__REALTIME_TIMESTAMP, \"target\": \$target, \"probe\": .HUNT_PROBE, \"event\": .HUNT_EVENT, \"result\": .HUNT_RESULT}" | head -n 80' -- 'known-service.service' '-15 min'`
執行界限：target=known-service.service；time=15 minutes；work=80 journal records；output=80 lines
請回傳：僅 `timestamp`、`target`、`probe`、`event`、`result` 五個欄位；最多 80 行
回傳前遮蔽：credential/token/cookie/PII/完整 payload/私人路徑
```

The systemd example is one bounded, read-only command: `--no-pager` forbids follow mode, `--since` bounds time, `-n 80` bounds work, and `head -n 80` bounds output. `journalctl -o json --output-fields=__REALTIME_TIMESTAMP,_SYSTEMD_UNIT,HUNT_PROBE,HUNT_EVENT,HUNT_RESULT` forbids a `MESSAGE` dump, and `jq` projects only the five allowed aliases. In this example `HUNT_PROBE`, `HUNT_EVENT`, and `HUNT_RESULT` must be predeclared fixed tokens/enums, never data-derived values. A different known runtime may use different predeclared fields, but it must meet the same minimal-allowlist, redaction, and three-bound contract. If it cannot, do not dump a log line: use the Handoff format instead. Do not replace it with a root/home/all-resource wildcard, unbounded device, global scan followed by truncation, or a follow command.

Treat symptom text, service names, paths, and all reporter values as hostile input. Never interpolate them into shell code: bind validated literal selectors through positional parameters as shown, quote every expansion, and keep the shell program constant. The required hostile-value test set is `'; env; #`, `$(id)`, `` `id` ``, `<newline>`, and `--help`; each must remain data and must neither execute nor rewrite the command.

Before any runtime or reporter probe, declare an exact minimal evidence allowlist for that hypothesis; the tested systemd example uses `timestamp`, `target`, `probe`, `event`, `result`. Redact values before they enter runtime logs, reporter output, a quoted RED evidence line, or the case file. A RED quotation must be one redacted line made only from that probe's allowlist, never a copied raw log/object/payload.

In non-interactive mode, waiting for the reporter result is the reporter-result Input PAUSE in `references/loop-pauses.md`. If no other read-only check remains, emit the existing Handoff format and end with `LOOP_OUTCOME: no progress: reporter probe result required`; do not request authorization.

---

## Instrumentation — 🎯 HUNT-id Tagging

All instruments (log lines, failing assertions, minimal test cases) **must carry a HUNT-id tag**.

- Tag format: see `references/hunt-case-template.md`
- `grep -rn "🎯HUNT-{YYYY-NNN}" --exclude-dir=.claude .` finds all instruments at once (the `--exclude-dir=.claude` scope matters: the case file itself carries the tag and must not count)
- After root cause is confirmed, **remove all tagged instruments in one sweep**, verify the build still passes, and confirm the same scoped grep over the source/test dirs returns 0 matches

One probe answers exactly one written yes/no hypothesis. At most one probe may be active at any time, whether it is an assertion, query, test, log, or static hypothesis check. Only an inventory/context scan that answers no hypothesis may run in parallel.

A probe contains either one assertion/query/test/static check, or 2–3 coordinated log sites. In the log-site form, every site has the same HUNT-id and probe label, all sites test the same yes/no hypothesis, and they close together as one probe — never as parallel hypotheses.

Log bisection therefore uses one log-site probe per round, not 20 instruments or multiple active probes.
```
Probe 1: entry / middle / exit sites answer “does this one path lose the value?” → close the probe
Probe 2: 2–3 sites inside the identified segment answer the next yes/no hypothesis → close the probe
Probe 3: usually locates within 5–10 lines
```

**Side-effect rule**: If adding a log changes the behavior (the bug disappears, the symptom shifts, the order of events differs), treat that as direct evidence of a timing, lifecycle, or concurrency problem — not as a logging side-effect to dismiss. The act of observing already pointed at the root cause class.

---

## Confirm or Discard

Write one yes/no hypothesis, declare its exact evidence allowlist, then open exactly one probe. Close it and record the result before opening another. A partial explanation may stay a hypothesis, but it cannot set `confirmed` until the complete observed-symptom list is mapped to the causal chain, or an independent evidence citation proves a symptom belongs to another incident and the case file records that incident's id plus next action.

After executing:
- Evidence **supports the hypothesis** → close that first probe, then open one second, independent cross-confirmation probe before proceeding to Before You Fix (next section). Independent means a different observable layer than the first probe (per the Tool Scan layers — UI/render, data state, call-chain structure, runtime intermediate values, static structure). Concretely, if a runtime log probe supported it, the second probe must be a DB query, a failing test, or a UI/render observation — not another runtime log. The sole same-layer exception is an observed failing test that encodes the hypothesis; it is still a second, closed-before-opened probe.
- Evidence **contradicts the hypothesis** → **discard the hypothesis completely**. Not patch, not explain. Reorient using what was just learned.

A preserved-but-contradicted hypothesis produces a new bug. Discard completely.

---

## Before You Fix

Both must be complete before any fix. Neither is optional.

### 1. Call chain analysis

- Direct callers (LSP findReferences / graphify / code search)
- Business scenarios affected by this code
- High-risk points (the most likely places to "fix A, break B")

### 2. Test matrix

For the logic being modified, enumerate dimension × boundary value combinations:
- Cover boundary values for every dimension
- **Unchanged scenarios are the most likely to be missed** (version numbers, timestamps, FKs may need synchronization)
- **Multi-X scenarios are the most error-prone** (multi-org, multi-tenant, multi-item)

Build the matrix before entering any fix. A fix without a test matrix is a symptom patch.

---

## Scope Blast Mode

Activate after the root cause is confirmed and before declaring the bug fixed. The same shape of bug often hides in N other places; a local fix that ignores the blast leaves N − 1 bugs in the tree.

1. **Extract the pattern signature**: the specific function name, regex, API call, CSS selector, lock acquisition, validation skip, parser input boundary, or token-handling path that produced the bug.
2. **`grep -rn <pattern>`** across the repo. Exclude generated directories, build output, and vendored dependencies. For class-of-bug patterns (e.g. "any handler missing the lock"), grep for the surrounding shape, not just the literal text.
3. **For each match, record a decision in the case file's `Scope Blast` section** (template line per match: `<file:line> — fix | leave: <reason> | unsure: <question>`). After a user reply resolves an `unsure`, update the same line to `unsure → fix` or `unsure → leave: <reason> after user reply <date>`. Do not silently skip a match.
4. **Do not claim fixed until** (a) every grep match has a recorded decision in the case file's `Scope Blast` section, AND (b) the success report's `迴歸守護` line names the regression test — or a justified 無 with its reason — **and** cites the case file's Scope Blast section by id (例：`[tests/foo.spec.ts:42] + Scope Blast: HUNT-YYYY-NNN §3`).

Common triggers:
- Visual bug fixed on one page → every other page using the same component, layout, or media-query breakpoint.
- One race fixed in one handler → every handler acquiring the same lock or touching the same shared state.
- One validation skip patched at one entry point → every entry point reaching the same downstream sink.
- One regex / parser fix for one input shape → every caller of the same regex / parser.

If the blast surfaces unrelated bugs, list them in the case file but do not fix them in this PR unless the user agrees.

---

## Bisect Mode

Activate when: "It worked before and now it's broken" or "It broke after an update."

**Precondition — git repo**: If the project is not a git repo, skip Bisect Mode entirely and fall back to static analysis + instrumentation (Tool Scan / Instrumentation sections). Never wedge trying to bisect what has no history.

1. Find `last-known-good`: use the most recent tag, not a date or raw SHA. (`git tag --sort=-version:refname | head -5`) If the repo has **zero tags**, ask the user for a known-good ref; when driven non-interactively, pick the oldest commit touching the symptom file and label the choice 「此處採預設」 in the case file.
2. Before starting bisect, define a **pass/fail test command**. The command must be auto-executable and produce a clear exit code. Write it down; reuse the same command at every step.
3. **Pre-bisect clean-tree gate**: Before `git bisect start`, run `git status --porcelain`. If it is empty, start directly. If it is **non-empty** (working tree dirty), stash the in-progress changes with `git stash push -u -m "hunt-{HUNT-id}"` (or commit them), and **record the stash entry's SHA in the case file** (`git stash list --format='%H %gs' | head -1`) so it can be restored in step 6 even if stack positions shift. Then **re-run `git status --porcelain` to verify the tree is now actually clean**. IF it is still non-empty after the stash (stash conflict, or residue the stash left behind) THEN do NOT run `git bisect start` — stop and report, because bisect would otherwise check out arbitrary commits over a tree that was never truly clean and clobber the residue. Only when the post-stash status is empty may you start bisect. Likewise, if the changes cannot be safely stashed or committed in the first place, stop and do not start bisect.
4. Execute: `git bisect start` → `git bisect bad` (current) → `git bisect good <tag>`. Let bisect drive the binary search — do not shortcut it by hand-picking commits. When a commit cannot build or cannot run the test command, `git bisect skip` it; skipping unbuildable commits is the correct use of bisect, not a violation.
5. When bisect identifies a commit: read only that commit's diff. Do not read surrounding history.
6. **Cleanup gate**: After bisect identifies the commit → run `git bisect reset` to exit the bisecting state and restore HEAD before touching code or running any other git operation. If a fix or any other git operation is attempted while still bisecting, stop and run `git bisect reset` first. Never leave the repo in a detached-HEAD bisecting state. **Then restore the step-3 stash**: locate the recorded SHA in `git stash list --format='%H %gr %gs'`, run `git stash apply <sha>` (never pop blindly — apply keeps the entry if conflicts appear), resolve or report any conflicts, and only then drop the entry by re-finding its current `stash@{n}` for that SHA. A hunt must never end with the user's work stranded in a stash.

---

## Repeated Regression Mode

Activate when the user says the same issue is still wrong after a previous fix, OR provides a "good" screenshot / version / file / fixture, OR describes a result as "previously correct" without a usable commit hash.

Treat the reference as **evidence, not decoration**. Five-step flow:

1. **List every reported and visible symptom**, preserving the user's exact words where useful (例：「還是慢」「不清楚」「尖刺」「先顯示上一個內容」). Multiple symptoms must all be explained by the eventual hypothesis.
2. **Identify the reference oracle**: last-good commit / tag, old build, fixture file, screenshot, downloaded artifact, or the user's described expected state. Name the artifact concretely.
3. **Define the pass/fail check before editing**. For visual bugs: a narrow screenshot checklist plus the command that renders the view. For behavioral bugs: an automated regression test or deterministic repro.
4. **Compare current vs. reference and name the exact delta**. Do not generalize an observed defect into "style polish" when the evidence points to a broken render, race, font pipeline, or state path.
5. **If the same symptom remains after one attempted fix**: this triggers the Hard Rule「Same symptom recurs after fix」(see Hard Rules — stop; no further fix attempts until the hypothesis is rebuilt, though 🎯HUNT-tagged instruments for re-diagnosis remain allowed). Then rebuild the hypothesis from the evidence collected in steps 1–4 above; do not stack more patches onto a disproven explanation.

If the issue is purely subjective UI taste, route to `$baransu:ui` instead. Stay in `$baransu:hunt` when the issue is rendering, state, timing, build output, font generation, or a regression from a known-good version.

---

## Hard Rules

| Condition | Action |
|------|------|
| Same symptom recurs after fix | Stop. Hypothesis was incomplete. Re-read the execution path. No further fix attempts until the hypothesis is rebuilt — adding 🎯HUNT-tagged instruments for re-diagnosis remains allowed. |
| "Let's try this" appears | Stop. Write the hypothesis before acting. |
| Three hypothesis failures | Switch to Handoff format (see Output). |
| Before You Fix incomplete when fix is attempted | Stop. Complete call chain analysis and test matrix first. |
| External tool fails | Diagnose the cause first (is the server running? is config correct?) before switching tools. |
| Visual / render bug | Static analysis first (DevTools layers, stacking context); logging is the second step. |
| DB investigation test | Transaction must always rollback. Do not modify real data. |
| Investigation involves file writes / external API calls | Use mocks to prevent real writes; emails and webhooks must not actually send. |
| Working tree dirty (`git status --porcelain` non-empty) when bisect is about to start | Stop — apply Bisect Mode step 3 gate before `git bisect start`. |
| git bisect identified the commit | Run `git bisect reset` per Bisect Mode step 6 before any other git operation. |
| Fix plan or current diff touches 6 or more files (without a Scope Blast pattern justification) | Stop **before adding the 6th file**. Check at two points: (i) when drafting the fix plan, (ii) after each edit. If the scope is genuinely a class-of-bug sweep, route through Scope Blast Mode (which is an explicit exception). If it is symptom-patch creep growing into a refactor, narrow back, or slice it and open a `$baransu:contract` on the first slice. |
| Someone (user or agent) deflects suspicion from a specific area — semantic trigger, not literal string match. Examples: 「那段沒問題」「不是那邊的問題」「先別管那個」「我已經檢查過了」, "that part doesn't matter", "I already checked there" | Treat as a signal. The area being deflected from is often where the bug lives — especially in multi-stage pipelines (CI segments, data pipeline stages, baransu plane handoffs) where one stage is excluded from suspicion. Re-examine that area with one targeted instrument before accepting the deflection. |

> In an ultracode session you may dispatch Workflows only for parallel inventory/context scans that answer no hypothesis. They may inform the next serialized probe, but never explore multiple hypothesis lines in parallel.
> When driven by loop, the loop-mode default is assisted: diagnosis advances automatically, but the fix is reported to the driver before being applied.

---

## Gotchas

| Scenario | Rule |
|------|------|
| Multi-entity comparison (multi-org / multi-tenant) | Compare by business key (SEQ / CODE / NAME), not ID. |
| Synchronizing unchanged items | Version numbers, timestamps, and FKs may need updating even for "unchanged" items. |
| Inheriting IDs after clone | Overwrite PK and FK after cloning; do not inherit source IDs. |
| Stack trace pointing deep into a library | Walk back 3 frames to your own code; the bug is almost always there. |
| One segment shows RUNNING in a parallel pipeline | Test each segment in isolation; each segment being correct does not mean the combination is. |

---

## Output

Before either fixed format below, write one short plain-language event summary that joins the whole incident: what the user was doing → triggering event or condition → concrete root cause (or the exact missing evidence if still unknown) → propagation path → visible symptom → practical impact → concrete next step. This summary is required even when the hunt is blocked; the fixed fields remain unchanged.

### Success format

```
根因：      [問題是什麼，file:line 或 component/query/condition]
修復：      [改了什麼，在哪裡]
確認方式：  [哪個證據或測試確認了修復 + 一行原樣引用的失敗證據]
測試矩陣：  [通過數 / 總數，迴歸測試位置]
迴歸守護：  [test file:line] + Scope Blast: HUNT-YYYY-NNN §N ｜ 或 [無，理由 + Scope Blast citation]
```

狀態：**已解決** / **已解決（附帶條件說明）** / **受阻**

**確認方式 — RED-evidence preservation**: the 確認方式 line MUST include one verbatim line of the observed failing evidence (the test failure line, log line, or query result), captured at the moment it happened. A prose claim that "old code fails" without the quoted artifact does not count.

**迴歸守護 — fidelity**: the named test must observe the **persisted or user-visible truth** of the original symptom end-to-end — drive the real trigger sequence and assert the stored or displayed outcome. Asserting an extracted helper or an internal seam that the fix could bypass does not satisfy 迴歸守護. If end-to-end observation is genuinely impossible, say why in the case file; per Scope Blast step 4(b), a justified 無 with the Scope Blast citation is a legal exit.

For a bug that was previously fixed and then recurred, the conditions for 「已解決」 are: (1) the regression test fails on the old code and passes on the new code; (2) the test lives in the project test suite; (3) the commit message explains the recurrence cause and how it is prevented.

After confirming root cause, route the fix by task scope:
- Single change point, small amount of code → implement directly, building your own red/green task list under the _shared/tdd.md discipline (read `../_shared/tdd.md` §7 before implementing)
- Multiple files, design decision needed, or cross-module impact → slice the fix and run each slice through `$baransu:contract` → implement → `$baransu:seal`

### Handoff format (use after three hypothesis failures)

```
症狀：[原始錯誤，一句話]

已測試的假說：
1. [假說 1] → [測試方式] → [結果：因為...排除]
2. [假說 2] → ...
3. [假說 3] → ...

已蒐集的證據：[Log / stack trace / 觀測到的中間值 / 重現步驟 / 環境]
已排除的根因：[已消除的可能性]
尚不知道的事：[還不清楚的地方]
建議下一步：[下一個調查方向 / 需要的工具或權限]
```

狀態：**受阻**

---

After completing the hunt, finalize the case file at `.codex/hunt-report/HUNT-YYYY-NNN.md` (created at the Locate stage; format: `references/hunt-case-template.md`): set its final `status` (fixed / handoff) and make sure the root cause and fix are recorded for future reference. Past cases are searchable via `scripts/hunt-search.py` — invoked at the Locate stage.
