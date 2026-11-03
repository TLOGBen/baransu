---- MODULE LintMod ----
(* The lint mod's cross-event state, one action per hook step. Since 8.40 the state is
   the Memory of plugins/baransu/hooks/engine/engine.ts and each hook step is one engine
   method (one to one); up to 8.39 it was S in plugins/baransu/hooks/lint.ts
   (git show 58de798a:plugins/baransu/hooks/lint.ts). Below, "S.x" names a field of that
   state. Three versions of the source:
     Fix = FALSE              the source before the first fix (8.37.0 as first committed),
     Fix = TRUE, Now = FALSE  the source at 0917b911 (the first and second rounds of fixes),
     Fix = TRUE, Now = TRUE   the source now (the fixes from the review of 0917b911).
   Break plants one bug per rule in the newest version, to show the judge can say no.
   A main-loop Edit/Write/Bash call is two steps, MainBegin and MainEnd, because the
   source awaits between taking what is owed and running the tool; two calls may overlap. *)
EXTENDS LintRules, Integers, FiniteSets

CONSTANTS Fix, Now, Break, MaxSteps,
  Mut,  \* "none", or one hook step whose core effect is removed, to find the steps no rule can do without
  Ans   \* how replyAppended takes `answering` (lint-scope sketch): "naive" on any main row; "step" only on a row
        \* of a response later than the one after which the model holds the 重新 (S.steps.main at delivery)

M(x) == Mut = x

N == Fix /\ Now
V2 == Fix /\ ~Now
Calls == {1, 2}
Dirs == {"a", "b"}
Other(d) == IF d = "a" THEN "b" ELSE "a"
\* cd: a foreground cd (the shell moves, even when a later part of the same command fails);
\* subcd: a cd inside ( ... ) (the shell does not move); ro: a read-only command (git status).
ActKinds == {"edit", "bash", "bashwrite", "cd", "subcd", "ro"} \cup Cmds
Outcomes == {"ok", "deny", "error"}
\* plain text; ns: a skill command with a namespace (/baransu:ship); skill: one without (/everything-search);
\* builtin: a command that opens no model turn (/cost).
MsgKinds == {"plain", "ns", "skill", "builtin"}

VARIABLES
  n, inTurn,           \* step counter (scope); a main turn is running
  spoke,               \* S.spoke
  slips,               \* S.slips (first source: one block or none)
  tools,               \* S.tools > 0
  textLong,            \* S.textAfterTools reads as a report
  pendingReport,       \* S.pendingReport
  previewed,           \* S.previewed (first source: commands; 0917b911: <<actor, command, dir>>;
                       \*   now: <<<<actor, command, dir>>, response>> for the main loop)
  editSeq,             \* S.editSeq
  reviewedAt,          \* S.reviewedAt
  cmdSeqs,             \* the editSeq values in S.commands
  langKnown,           \* S.userLanguage is set
  trackedCwd,          \* 0917b911: the shell directory the mod tracked from cd commands (trackCd)
  stepC,               \* the main loop's model responses so far (turn.step; S.steps.main)
  pc, snap, seen,      \* per main call: "idle"/"mid", restates it took, wrong blocks written before it began
  beginStep,           \* per main call: the response it was sent in
  cwdG,                \* ghost: the main shell's real directory ($.session.cwd())
  userSpokeG,          \* ghost: the user has written (their language is known)
  nextBlock,           \* ghost: id for the next wrong-language block
  workG, reportG,      \* ghost: this turn edited or ran something / reported after its last such step
  late,                \* ghost: text streamed before a call whose row is appended only later: "none", "pre", "armed"
  answering,           \* S.answering: the steps (S.steps.main at delivery) of the 重新 not yet answered — a list in
                       \*   engine.ts, a set here (two deliveries at one step are one entry for the checks)
  rowLate, rowStep,    \* ghost: a streamed text's assistant row not yet appended, and the response it belongs to
  \* 8.43, the newest source only (they stay put in the others):
  stopHeld,            \* S.held has `stop|report-before-stop`: the report had its one hold this turn
  stopHolds,           \* S.stopHolds: error holds this turn
  askedG,              \* ghost: this turn was asked for its report at a stop
  stopPassedG,         \* ghost: a stop let this turn end (an answered turn.complete follows one)
  queued,              \* S.queued is not empty (one line stands for the list)
  snapQ                \* per main call: it took the queued line

codeVars == <<spoke, slips, tools, textLong, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd>>
NewVars == <<stopHeld, stopHolds, askedG, stopPassedG, queued, snapQ, askWarrantedG, stopHoldsG, qOwedG, qDeliv>>
vars == <<judgeVars, codeVars, n, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late,
          answering, rowLate, rowStep, stopHeld, stopHolds, askedG, stopPassedG, queued, snapQ>>

Restate(S) == [b \in Blocks |-> IF b \in S THEN restated[b] + (IF Break = "R2" THEN 2 ELSE 1) ELSE restated[b]]
Idle == \A c \in Calls : pc[c] = "idle"
NoOut == explainNow' = FALSE /\ execCmd' = <<>> /\ execStep' = execStep
NoClaim == UNCHANGED <<claimNoEdit, claimReviewed, claimCmd>>
NoLast == UNCHANGED <<lastSeen, lastOutcome>>
NoHold == UNCHANGED <<heldTurnG, heldEverG, heldStepG>>
Step == n < MaxSteps /\ n' = n + 1
Key(actor0, cmd, dir) == IF Fix THEN <<actor0, cmd, dir>> ELSE cmd

\* ---- the redo checks (lint-scope sketch) ----
\* A step that neither delivers a 重新 nor appends a main reply row.
AnsQuiet == /\ checkNow' = FALSE /\ answerRowG' = FALSE
            /\ UNCHANGED <<answering, rowLate, rowStep, ansOwedG, dupG, checksG>>
\* A delivery (d) after which the model holds the 重新 once response s is done: s added to S.answering.
Deliver(d, s) ==
  /\ answering' = (IF d THEN answering \cup {s} ELSE answering)
  /\ ansOwedG' = (IF d THEN ansOwedG \cup {s} ELSE ansOwedG)
  /\ checkNow' = FALSE /\ answerRowG' = FALSE /\ UNCHANGED <<rowLate, rowStep, dupG, checksG>>
\* A main-loop assistant row of response rs appended (session.append → replyAppended), at response stepC.
\* Truth: it answers every owed delivery the model holds by then (delivered in an earlier response than rs).
\* Code: replyAppended takes, synchronously, every S.answering entry with step < S.steps.main ("step"); the naive
\* take takes them all. vis: the row carries content the person sees (text, or a thinking block with text); a row
\* of only a tool_use or an empty thinking does not (second derivation A-2, C-4).
Reply(rs, vis) ==
  LET answered == IF vis THEN {x \in ansOwedG : x < rs} ELSE {}
      taken    == IF Break = "R14" THEN {}
                  ELSE IF Ans = "naive" THEN answering
                  ELSE IF vis \/ Break = "vis" THEN {x \in answering : x < stepC}
                  ELSE {}
  IN /\ checkNow' = (taken # {}) /\ answerRowG' = (answered # {})
     /\ answering' = IF Break = "R15" THEN answering ELSE answering \ taken
     /\ dupG' = (dupG \/ (taken \cap checksG # {}))
     /\ checksG' = checksG \cup taken
     /\ ansOwedG' = ansOwedG \ answered

Init ==
  /\ ev = "Init" /\ actor = "host" /\ wrongG = {} /\ restated = [b \in Blocks |-> 0]
  /\ reportOwedG = FALSE /\ reportEmits = 0 /\ explainFlags = 0 /\ explainNow = FALSE
  /\ heldTurnG = {} /\ heldEverG = {} /\ heldStepG = {} /\ execCmd = <<>> /\ execStep = 0
  /\ editedG = FALSE /\ reviewedAfterG = FALSE /\ cmdAfterG = FALSE
  /\ claimNoEdit = FALSE /\ claimReviewed = FALSE /\ claimCmd = FALSE
  /\ spokeTurnG = FALSE /\ actsTurnG = 0 /\ lastSeen = {} /\ lastOutcome = "ok"
  /\ n = 0 /\ inTurn = FALSE
  /\ spoke = TRUE                 \* lint.ts freshState: spoke: true
  /\ slips = {} /\ tools = FALSE /\ textLong = FALSE /\ pendingReport = FALSE
  /\ previewed = {} /\ editSeq = 0 /\ reviewedAt = -1 /\ cmdSeqs = {} /\ langKnown = FALSE /\ trackedCwd = "a"
  /\ stepC = 0
  /\ pc = [c \in Calls |-> "idle"] /\ snap = [c \in Calls |-> {}] /\ seen = [c \in Calls |-> {}]
  /\ beginStep = [c \in Calls |-> 0]
  /\ cwdG = "a" /\ userSpokeG = FALSE /\ nextBlock = 1 /\ workG = FALSE /\ reportG = FALSE /\ late = "none"
  /\ answering = {} /\ rowLate = FALSE /\ rowStep = 0
  /\ ansOwedG = {} /\ dupG = FALSE /\ answerRowG = FALSE /\ checkNow = FALSE /\ checksG = {}
  /\ stopHeld = FALSE /\ stopHolds = 0 /\ askedG = FALSE /\ stopPassedG = FALSE /\ queued = FALSE
  /\ snapQ = [c \in Calls |-> FALSE]
  /\ askWarrantedG = FALSE /\ stopHoldsG = 0 /\ qOwedG = FALSE /\ qDeliv = 0

\* lint.ts prompt.submit, a message the user typed. The first source skipped slash commands; 0917b911 took what is
\* owed for a namespaced command only; now a slash command's turn delivers what it carried (turn.start).
\* A built-in like /cost opens no turn and takes nothing in any version.
UserPrompt(msg) ==
  /\ Step /\ Idle /\ ev' = (IF msg = "builtin" THEN "Builtin" ELSE "UserPrompt") /\ actor' = "user"
  /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ userSpokeG' = TRUE
  /\ langKnown' = (langKnown \/ msg = "plain" \/ Fix)   \* the fixes also read the language from a command's arguments
  /\ LET consume == ~M("prompt-take") /\ (msg = "plain" \/ (Fix /\ msg = "ns") \/ (N /\ msg = "skill")) IN
     /\ restated' = IF consume THEN Restate(slips) ELSE restated
     /\ slips' = IF consume THEN {} ELSE slips
     /\ pendingReport' = IF consume THEN FALSE ELSE pendingReport
     /\ reportEmits' = IF consume /\ pendingReport THEN reportEmits + 1 ELSE reportEmits
     /\ reportOwedG' = IF consume /\ pendingReport THEN FALSE ELSE reportOwedG
     /\ Deliver(consume /\ (slips # {} \/ pendingReport), stepC)
     /\ queued' = IF N /\ consume /\ Break # "R21" THEN FALSE ELSE queued
     /\ qDeliv' = IF N /\ consume /\ queued THEN qDeliv + 1 ELSE qDeliv
     /\ qOwedG' = IF N /\ consume /\ queued THEN FALSE ELSE qOwedG
  /\ UNCHANGED <<stopHeld, stopHolds, askedG, stopPassedG, snapQ, askWarrantedG, stopHoldsG>>
  /\ UNCHANGED <<wrongG, explainFlags, editedG, reviewedAfterG, cmdAfterG, spokeTurnG, actsTurnG,
                 spoke, tools, textLong, previewed, editSeq, reviewedAt, cmdSeqs, trackedCwd,
                 inTurn, stepC, pc, snap, seen, beginStep, cwdG, nextBlock, workG, reportG, late>>

\* A plain message a hook or a settings hook beneath refused (prompt.submit's { drop }): it never reached the model.
\* The earlier sources had already taken what was owed; now it goes back.
Dropped ==
  /\ UNCHANGED NewVars
  /\ Step /\ Idle /\ ev' = "Dropped" /\ actor' = "user" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ slips' = IF N THEN slips ELSE {}
  /\ pendingReport' = IF N THEN pendingReport ELSE FALSE
  /\ AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, spoke, tools, textLong, previewed, editSeq, reviewedAt, cmdSeqs, langKnown,
                 trackedCwd, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

\* lint.ts turn.start (main loop). The fixes also end this turn's preview approvals (reading D1-B).
TurnStart ==
  /\ Step /\ ~inTurn /\ ev' = "TurnStart" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast
  /\ inTurn' = TRUE
  /\ spoke' = IF M("start-reset") THEN spoke ELSE FALSE
  /\ tools' = IF M("start-reset") THEN tools ELSE FALSE
  /\ textLong' = IF M("start-reset") THEN textLong ELSE FALSE
  /\ previewed' = IF Fix /\ ~M("start-reset") THEN {} ELSE previewed
  /\ spokeTurnG' = FALSE /\ actsTurnG' = 0 /\ workG' = FALSE /\ reportG' = FALSE /\ heldTurnG' = {} /\ late' = "none"
  /\ stopHeld' = FALSE /\ stopHolds' = 0 /\ askedG' = FALSE /\ stopPassedG' = FALSE /\ stopHoldsG' = 0
  /\ UNCHANGED <<queued, snapQ, askWarrantedG, qOwedG, qDeliv>>
  /\ AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldEverG, heldStepG, editedG, reviewedAfterG,
                 cmdAfterG, slips, pendingReport, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd,
                 stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock>>

\* lint.ts turn.step (main loop): a new model response begins.
MainStep ==
  /\ UNCHANGED NewVars
  /\ Step /\ inTurn /\ ~rowLate /\ ev' = "MainStep" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ stepC' = stepC + 1
  /\ AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, codeVars, inTurn, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock,
                 workG, reportG, late>>

\* Text streamed before a call of the same response (turn.step text chunks); its row is appended later (LateAppend).
\* 0917b911 read "spoke" from the stream; the newest source also reads the report from it.
MainPre(long) ==
  /\ UNCHANGED NewVars
  /\ Step /\ inTurn /\ Idle /\ late = "none" /\ ~rowLate /\ ev' = "MainPre" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ spoke' = IF Fix /\ ~M("stream-deaf") THEN TRUE ELSE spoke
  \* its row is appended later (LateAppend for a long one, RowAppend for a short one), before the next response
  /\ rowLate' = TRUE /\ rowStep' = stepC
  /\ checkNow' = FALSE /\ answerRowG' = FALSE /\ UNCHANGED <<answering, ansOwedG, dupG, checksG>>
  /\ spokeTurnG' = TRUE
  /\ reportG' = (reportG \/ long)
  /\ textLong' = IF N /\ ~M("stream-deaf") THEN (textLong \/ long) ELSE textLong
  /\ late' = IF long THEN "pre" ELSE "none"   \* only a long row matters later; a short one changes no report
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 actsTurnG, slips, tools, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd,
                 inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG>>

\* The row of that long streamed text is appended (session.append), after a call when one followed ("armed").
\* The earlier sources counted it as words after the call; the newest reads words from the stream only.
LateAppend ==
  /\ UNCHANGED NewVars
  /\ Step /\ Idle /\ late # "none" /\ ev' = "LateAppend" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ spoke' = TRUE
  /\ textLong' = IF N THEN textLong ELSE TRUE
  /\ late' = "none"
  /\ rowLate' = FALSE /\ UNCHANGED rowStep /\ Reply(rowStep, TRUE)
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, slips, tools, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown,
                 trackedCwd, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* The row of a short streamed text is appended (session.append): it changes no report, but it may answer a 重新.
RowAppend ==
  /\ UNCHANGED NewVars
  /\ Step /\ rowLate /\ late = "none" /\ ev' = "RowAppend" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ rowLate' = FALSE /\ UNCHANGED rowStep /\ Reply(rowStep, TRUE)
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, codeVars, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock,
                 workG, reportG, late>>

\* A main-loop row with nothing the person sees (one block per row: a tool_use, an empty thinking).
EmptyRow ==
  /\ UNCHANGED NewVars
  /\ Step /\ inTurn /\ ev' = "EmptyRow" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ UNCHANGED <<rowLate, rowStep>> /\ Reply(stepC, FALSE)
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, codeVars, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock,
                 workG, reportG, late>>

\* Text after the last call, streamed and appended (session.append, main loop). wrong: English prose to a Chinese
\* user; long: a report. A wrong block is recorded only while S.userLanguage is set (wantsChinese).
MainText(wrong, long) ==
  /\ UNCHANGED NewVars
  /\ Step /\ inTurn /\ late = "none" /\ ~rowLate /\ ev' = "MainText" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ (wrong => (userSpokeG /\ nextBlock \in Blocks))
  /\ UNCHANGED <<rowLate, rowStep>> /\ Reply(stepC, TRUE)
  /\ spoke' = (spoke \/ ~M("text-deaf")) /\ spokeTurnG' = TRUE
  /\ textLong' = (textLong \/ (long /\ ~M("text-deaf"))) /\ reportG' = (reportG \/ long)
  /\ wrongG' = IF wrong THEN wrongG \cup {nextBlock} ELSE wrongG
  /\ nextBlock' = IF wrong THEN nextBlock + 1 ELSE nextBlock
  /\ slips' = IF wrong /\ langKnown THEN (IF Fix THEN slips \cup {nextBlock} ELSE {nextBlock}) ELSE slips
  /\ UNCHANGED <<restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 actsTurnG, tools, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd,
                 inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, workG, late>>

\* lint.ts session.append with e.agentId: ignored.
SubText ==
  /\ UNCHANGED NewVars
  /\ Step /\ ev' = "SubText" /\ actor' = "sub" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ IF Break = "R17"   \* planted: a subagent's row takes the 重新 as if it were the answer
       THEN /\ checkNow' = (answering # {}) /\ answerRowG' = FALSE /\ answering' = {}
            /\ dupG' = (dupG \/ (answering \cap checksG # {})) /\ checksG' = checksG \cup answering
            /\ UNCHANGED <<rowLate, rowStep, ansOwedG>>
       ELSE AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, codeVars, inTurn, stepC, pc, snap, seen, beginStep, cwdG,
                 userSpokeG, nextBlock, workG, reportG, late>>

\* lint.ts tool.call, main loop, a tool that is not Edit/Write/Bash (Read, a plan update, ...).
\* The first source counted it as work and forgot a report written before it; the fixes count only edits and commands.
MainRead ==
  /\ UNCHANGED NewVars
  /\ Step /\ inTurn /\ ev' = "MainRead" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ tools' = IF Fix THEN tools ELSE TRUE
  /\ textLong' = IF Fix THEN textLong ELSE FALSE
  /\ AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, spoke, slips, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs,
                 langKnown, trackedCwd, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock,
                 workG, reportG, late>>

\* lint.ts tool.call, main loop, Edit/Write/Bash, first part. The fixes take the pending restates at once (the first
\* source read them only after awaiting). The earlier sources count the work and forget the report here, for any
\* call; the newest does it after the call ran, and not for a read-only command.
MainBegin(c) ==
  /\ Step /\ inTurn /\ pc[c] = "idle" /\ ev' = "MainBegin" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ pc' = [pc EXCEPT ![c] = "mid"]
  /\ seen' = [seen EXCEPT ![c] = wrongG]
  /\ snap' = [snap EXCEPT ![c] = slips]
  /\ beginStep' = [beginStep EXCEPT ![c] = stepC]
  /\ slips' = IF Fix /\ ~M("call-take") THEN {} ELSE slips
  /\ snapQ' = [snapQ EXCEPT ![c] = N /\ queued]
  /\ queued' = IF N THEN FALSE ELSE queued
  /\ UNCHANGED <<stopHeld, stopHolds, askedG, stopPassedG, askWarrantedG, stopHoldsG, qOwedG, qDeliv>>
  /\ tools' = IF N THEN tools ELSE TRUE
  /\ textLong' = IF N THEN textLong ELSE FALSE
  /\ AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, spoke, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs,
                 langKnown, trackedCwd, inTurn, stepC, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

\* Second part: deliver restates, explain-first, preview, run, record. outcome: "deny" when another check refuses it,
\* "error" when it runs and fails.
\* Where the delete is previewed: the first source used one directory; 0917b911 the directory it tracked from cd
\* commands (moved by a subshell cd, not moved when the command failed); the newest reads the real one.
\* When it passes: the earlier sources on any later call; the newest only in a later response than the held one.
MainEnd(c, kind, outcome) ==
  /\ Step /\ pc[c] = "mid" /\ ev' = "MainAct" /\ actor' = "main" /\ NoClaim
  /\ pc' = [pc EXCEPT ![c] = "idle"] /\ snap' = [snap EXCEPT ![c] = {}]
  /\ actsTurnG' = actsTurnG + 1 /\ lastSeen' = seen[c]
  /\ explainNow' = (~spoke /\ ~M("no-explain"))
  /\ explainFlags' = (IF ~spoke /\ ~M("no-explain") THEN explainFlags + 1 ELSE explainFlags)
  /\ spoke' = TRUE
  /\ LET isDel   == kind \in Cmds
         dir     == IF N THEN cwdG ELSE IF Fix THEN trackedCwd ELSE "a"
         key     == Key("main", kind, dir)
         passes  == IF N /\ Break # "R11"
                      THEN \E s \in 0..(beginStep[c] - 1) : <<key, s>> \in previewed
                      ELSE IF N THEN \E s \in 0..MaxSteps : <<key, s>> \in previewed
                      ELSE key \in previewed
         held    == isDel /\ ~M("no-hold") /\ ~(passes \/ (Break = "R7" /\ previewed # {}))
         rec     == IF N THEN <<key, beginStep[c]>> ELSE key
         target  == <<"main", kind, cwdG>>
         out     == IF held THEN "deny" ELSE outcome
         ran     == out # "deny"
         ranWork == ran /\ kind # "ro"
         taken   == snap[c] IN
     /\ lastOutcome' = out
     \* a 重新 delivered with this call's result: the restates it took, or the explain-first request — both ride on
     \* the result or the refusal, so a call that ran and failed delivers neither (engine.ts callAfterTake: redo[],
     \* deliver on refuse and after a clean run; 8.43.0)
     /\ Deliver((taken # {} \/ (~spoke /\ ~M("no-explain"))) /\ (IF Fix THEN out # "error" ELSE out = "ok"), stepC)
     /\ restated' = IF Fix THEN (IF out # "error" THEN Restate(taken) ELSE restated)
                           ELSE (IF out = "ok" THEN Restate(taken) ELSE restated)
     /\ slips' = IF Fix THEN (IF out = "error" THEN slips \cup taken ELSE slips) ELSE {}
     /\ queued' = IF out = "error" THEN (queued \/ snapQ[c]) ELSE queued
     /\ qDeliv' = IF out # "error" /\ snapQ[c] THEN qDeliv + 1 ELSE qDeliv
     /\ qOwedG' = IF out # "error" /\ snapQ[c] THEN FALSE ELSE qOwedG
     /\ snapQ' = [snapQ EXCEPT ![c] = FALSE]
     /\ UNCHANGED <<stopHeld, stopHolds, askedG, stopPassedG, askWarrantedG, stopHoldsG>>
     /\ previewed' = IF held THEN previewed \cup {rec} ELSE previewed
     /\ heldTurnG' = IF held THEN heldTurnG \cup {target} ELSE heldTurnG
     /\ heldEverG' = IF held THEN heldEverG \cup {target} ELSE heldEverG
     /\ heldStepG' = IF held THEN heldStepG \cup {<<target, beginStep[c]>>} ELSE heldStepG
     /\ execCmd' = IF isDel /\ ran THEN target ELSE <<>>
     /\ execStep' = beginStep[c]
     /\ cwdG' = IF kind = "cd" /\ ran THEN Other(cwdG) ELSE cwdG
     /\ trackedCwd' = IF V2 /\ out = "ok" /\ kind \in {"cd", "subcd"} THEN Other(trackedCwd) ELSE trackedCwd
     /\ tools' = IF N THEN (tools \/ ranWork) ELSE tools
     /\ textLong' = IF N /\ ranWork /\ ~M("work-keeps-report") THEN FALSE ELSE textLong
     /\ workG' = (workG \/ ranWork)
     /\ reportG' = IF ranWork THEN FALSE ELSE reportG
     /\ late' = IF late = "pre" THEN "armed" ELSE late
     /\ editSeq' = IF ran /\ ~M("no-edit-count") /\ (kind = "edit" \/ (Fix /\ kind = "bashwrite")) THEN editSeq + 1 ELSE editSeq
     /\ editedG' = (editedG \/ (ran /\ kind \in {"edit", "bashwrite"}))
     /\ reviewedAfterG' = IF ran /\ kind \in {"edit", "bashwrite"} THEN FALSE ELSE reviewedAfterG
     /\ cmdSeqs' = IF ran /\ kind # "edit" /\ ~(Fix /\ kind = "bashwrite") THEN cmdSeqs \cup {editSeq} ELSE cmdSeqs
     /\ cmdAfterG' = IF ran /\ kind \in {"edit", "bashwrite"} THEN FALSE ELSE (cmdAfterG \/ ran)
  /\ UNCHANGED <<wrongG, reportOwedG, reportEmits, spokeTurnG, pendingReport, reviewedAt, langKnown,
                 inTurn, stepC, seen, beginStep, userSpokeG, nextBlock>>

\* lint.ts tool.call with e.agentId, Edit/Write/Bash. The first source dropped a pending restate here.
\* A subagent's shell is its own; its directory is "a". (The newest source also counts a subagent's responses;
\* the model lets a subagent's repeat through on any later call, which is weaker than the source.)
SubAct(kind) ==
  /\ UNCHANGED NewVars
  /\ Step /\ kind \notin {"cd", "subcd"} /\ ev' = "SubAct" /\ actor' = "sub" /\ NoClaim /\ explainNow' = FALSE /\ NoLast
  /\ slips' = IF Fix THEN slips ELSE {}
  /\ explainFlags' = IF Break = "R3" THEN explainFlags + 1 ELSE explainFlags
  /\ LET isDel  == kind \in Cmds
         key    == Key("sub", kind, "a")
         target == <<"sub", kind, "a">>
         held   == isDel /\ ~(key \in previewed)
         ran    == ~held IN
     /\ AnsQuiet
     /\ previewed' = IF held THEN previewed \cup {key} ELSE previewed
     /\ heldTurnG' = IF held THEN heldTurnG \cup {target} ELSE heldTurnG
     /\ heldEverG' = IF held THEN heldEverG \cup {target} ELSE heldEverG
     /\ execCmd' = IF isDel /\ ran THEN target ELSE <<>>
     /\ editSeq' = IF ran /\ (kind = "edit" \/ (Fix /\ kind = "bashwrite")) THEN editSeq + 1 ELSE editSeq
     /\ editedG' = (editedG \/ (ran /\ kind \in {"edit", "bashwrite"}))
     /\ reviewedAfterG' = IF ran /\ kind \in {"edit", "bashwrite"} THEN FALSE ELSE reviewedAfterG
     /\ cmdSeqs' = IF ran /\ kind # "edit" /\ ~(Fix /\ kind = "bashwrite") THEN cmdSeqs \cup {editSeq} ELSE cmdSeqs
     /\ cmdAfterG' = IF ran /\ kind \in {"edit", "bashwrite"} THEN FALSE ELSE (cmdAfterG \/ ran)
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, spokeTurnG, actsTurnG, spoke, tools, textLong, pendingReport,
                 reviewedAt, langKnown, trackedCwd, heldStepG, execStep, inTurn, stepC, pc, snap, seen, beginStep, cwdG,
                 userSpokeG, nextBlock, workG, reportG, late>>

\* lint.ts turn.complete (main loop). The fixes also clear a report owed from before when this turn reported.
\* Every streamed row is appended before the turn ends.
\* answered: the turn ended with an answer; FALSE when the person interrupted it. Since 8.40.2 the newest source
\* judges the report only for an answered turn (user 2026-11-03: an interrupted turn owes none).
TurnComplete(answered) ==
  /\ Step /\ inTurn /\ Idle /\ late = "none" /\ ~rowLate /\ ev' = "TurnComplete" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  \* since 8.43 an answered turn ends at the stop (Stop); turn.complete here is a turn the person interrupted
  /\ (N => ~answered)
  /\ UNCHANGED NewVars
  /\ inTurn' = FALSE
  \* a 重新 the model read (a later response began) but did not answer before the turn ended is dropped
  \* (reading: a turn that ends first drops it); one delivered with a queued message the model has not read
  \* yet stays for the next turn (second derivation A-3)
  /\ ansOwedG' = {x \in ansOwedG : x >= stepC}
  /\ answering' = IF Ans = "naive" \/ Break = "queued" THEN {} ELSE {x \in answering : x >= stepC}
  /\ checkNow' = FALSE /\ answerRowG' = FALSE
  /\ UNCHANGED <<rowLate, rowStep, dupG, checksG>>
  /\ pendingReport' = IF N THEN pendingReport   \* 8.43 keeps no report for the next turn: the stop asked
                      ELSE IF Break = "R5" THEN TRUE
                      ELSE IF M("no-owe") \/ (N /\ ~answered) THEN pendingReport
                      ELSE IF Fix /\ textLong THEN FALSE
                      ELSE pendingReport \/ (tools /\ ~textLong)
  /\ reportOwedG' = IF ~answered THEN reportOwedG ELSE IF reportG \/ askedG THEN FALSE ELSE (reportOwedG \/ workG)
  /\ UNCHANGED <<wrongG, restated, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, spoke, slips, tools, textLong, previewed, editSeq, reviewedAt, cmdSeqs,
                 langKnown, trackedCwd, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

\* A /review, started and ended (answered) or stopped by the user. The earlier sources counted it when it
\* started (skill.prompt); the newest when its turn ends with an answer (turn.complete).
Review(answered) ==
  /\ UNCHANGED NewVars
  /\ Step /\ ev' = "Review" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ reviewedAt' = IF (N /\ ~answered) \/ M("review-ignored") THEN reviewedAt ELSE editSeq
  /\ reviewedAfterG' = (reviewedAfterG \/ answered)
  /\ AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, cmdAfterG,
                 spokeTurnG, actsTurnG, spoke, slips, tools, textLong, pendingReport, previewed, editSeq, cmdSeqs,
                 langKnown, trackedCwd, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock,
                 workG, reportG, late>>

\* lint.ts sessionRecord, read when skill.prompt for ship runs.
Ship ==
  /\ UNCHANGED NewVars
  /\ Step /\ ev' = "Ship" /\ actor' = "main" /\ NoOut /\ NoLast /\ NoHold
  /\ claimNoEdit' = (editSeq = 0)
  /\ claimReviewed' = (editSeq > 0 /\ (reviewedAt >= editSeq \/ (Break = "R8" /\ reviewedAt >= 0)))
  /\ claimCmd' = (editSeq > 0 /\ editSeq \in cmdSeqs)
  /\ AnsQuiet
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, codeVars, inTurn, stepC, pc, snap, seen, beginStep, cwdG,
                 userSpokeG, nextBlock, workG, reportG, late>>

\* The engine reloads the hooks module: the first source's module variables start over; the fixes keep them in $.state.
Reload ==
  /\ UNCHANGED NewVars
  /\ Step /\ Idle /\ ev' = "Reload" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ IF Fix /\ ~M("reload-forgets")
       THEN UNCHANGED codeVars
       ELSE /\ spoke' = TRUE /\ slips' = {} /\ tools' = FALSE /\ textLong' = FALSE /\ pendingReport' = FALSE
            /\ previewed' = {} /\ editSeq' = 0 /\ reviewedAt' = -1 /\ cmdSeqs' = {} /\ langKnown' = FALSE
            /\ trackedCwd' = "a"
  /\ AnsQuiet   \* S.answering lives in $.state, so a reload keeps it
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG,
                 nextBlock, workG, reportG, late>>

\* /clear: the conversation goes on under a new session id, with no session.start. Nothing is owed to the new one.
\* The newest source starts its state over (session.end, reason clear); the earlier ones kept it.
Clear ==
  /\ Step /\ Idle /\ ~inTurn /\ ev' = "Clear" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast
  /\ wrongG' = {} /\ reportOwedG' = FALSE /\ editedG' = FALSE /\ reviewedAfterG' = FALSE /\ cmdAfterG' = FALSE
  /\ heldTurnG' = {}
  /\ answering' = {} /\ ansOwedG' = {} /\ checkNow' = FALSE /\ answerRowG' = FALSE
  /\ UNCHANGED <<rowLate, rowStep, dupG, checksG>>
  /\ queued' = IF N /\ ~M("clear-keeps") THEN FALSE ELSE queued
  /\ qOwedG' = FALSE
  /\ UNCHANGED <<stopHeld, stopHolds, askedG, stopPassedG, snapQ, askWarrantedG, stopHoldsG, qDeliv>>
  /\ IF N /\ ~M("clear-keeps")
       THEN /\ spoke' = TRUE /\ slips' = {} /\ tools' = FALSE /\ textLong' = FALSE /\ pendingReport' = FALSE
            /\ previewed' = {} /\ editSeq' = 0 /\ reviewedAt' = -1 /\ cmdSeqs' = {}
            /\ UNCHANGED <<langKnown, trackedCwd>>
       ELSE UNCHANGED codeVars
  /\ UNCHANGED <<restated, reportEmits, explainFlags, heldEverG, heldStepG, spokeTurnG, actsTurnG,
                 inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

\* classic.Stop (8.43, engine.ts stopping): the main loop wants to end its turn. err: an error check on its last words
\* fails; line: a warn check has a line for the model. report-before-stop finds work with no report after it
\* (tools, ~textLong). The code holds — the model goes on in the same turn — when an error holds and fewer than
\* STOP_HOLDS (3) error holds came before, or when a hold-once finding (the report) has not had its own hold this turn
\* (S.held `stop|<id>`; not the host's stop_hook_active, which an error's hold would use up — found by R4). Once held,
\* it is shown on the card only: neither asked again with an error's hold nor queued (found by R5). A stop that lets the turn end ends it: the answered turn.complete that
\* follows at once is folded into this step (its effects as TurnComplete(TRUE)), and what the stop still has for the
\* model is queued.
Stop(err, line) ==
  /\ N /\ Step /\ inTurn /\ Idle /\ late = "none" /\ ~rowLate
  /\ ev' = "Stop" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ LET report  == (tools /\ ~textLong /\ ~M("no-owe")) \/ Break = "R5"
         errHold == err /\ (stopHolds < 3 \/ Break = "R19")
         fresh   == report /\ ~stopHeld
         hold    == errHold \/ fresh
         asks    == hold /\ report /\ (~stopHeld \/ Break = "R5")
         left    == ~hold /\ (err \/ line) IN
     /\ askWarrantedG' = (workG /\ ~reportG /\ ~askedG)
     /\ reportEmits' = IF asks THEN reportEmits + 1 ELSE reportEmits
     /\ askedG' = (askedG \/ asks)
     /\ stopHolds' = IF errHold THEN stopHolds + 1 ELSE stopHolds
     /\ stopHoldsG' = IF hold THEN stopHoldsG + 1 ELSE stopHoldsG
     /\ stopHeld' = (stopHeld \/ fresh)
     /\ stopPassedG' = ~hold
     /\ queued' = (queued \/ left)
     /\ qOwedG' = (qOwedG \/ left)
     /\ qDeliv' = IF left /\ ~queued THEN 0 ELSE qDeliv
     /\ IF hold
          THEN /\ Deliver(asks, stepC) /\ UNCHANGED <<inTurn, reportOwedG>>
          ELSE /\ inTurn' = FALSE
               /\ ansOwedG' = {x \in ansOwedG : x >= stepC}
               /\ answering' = IF Ans = "naive" \/ Break = "queued" THEN {} ELSE {x \in answering : x >= stepC}
               /\ checkNow' = FALSE /\ answerRowG' = FALSE
               /\ UNCHANGED <<rowLate, rowStep, dupG, checksG>>
               /\ reportOwedG' = IF reportG \/ askedG THEN FALSE ELSE (reportOwedG \/ workG)
  /\ UNCHANGED <<snapQ, wrongG, restated, explainFlags, editedG, reviewedAfterG, cmdAfterG, spokeTurnG,
                 actsTurnG, codeVars, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

Next ==
  \/ \E m \in MsgKinds : UserPrompt(m)
  \/ Dropped
  \/ TurnStart
  \/ MainStep
  \/ \E l \in BOOLEAN : MainPre(l)
  \/ LateAppend
  \/ RowAppend
  \/ EmptyRow
  \/ \E w \in BOOLEAN, l \in BOOLEAN : MainText(w, l)
  \/ SubText
  \/ MainRead
  \/ \E c \in Calls : MainBegin(c)
  \/ \E c \in Calls, k \in ActKinds, o \in Outcomes : MainEnd(c, k, o)
  \/ \E k \in ActKinds : SubAct(k)
  \/ \E a \in BOOLEAN : TurnComplete(a)
  \/ \E e \in BOOLEAN, l \in BOOLEAN : Stop(e, l)
  \/ \E a \in BOOLEAN : Review(a)
  \/ Ship
  \/ Reload
  \/ Clear

Spec == Init /\ [][Next]_vars
====
