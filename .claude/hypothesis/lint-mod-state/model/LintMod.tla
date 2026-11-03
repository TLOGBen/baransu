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
  Mut   \* "none", or one hook step whose core effect is removed, to find the steps no rule can do without

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
  late                 \* ghost: text streamed before a call whose row is appended only later: "none", "pre", "armed"

codeVars == <<spoke, slips, tools, textLong, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd>>
vars == <<judgeVars, codeVars, n, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

Restate(S) == [b \in Blocks |-> IF b \in S THEN restated[b] + (IF Break = "R2" THEN 2 ELSE 1) ELSE restated[b]]
Idle == \A c \in Calls : pc[c] = "idle"
NoOut == explainNow' = FALSE /\ execCmd' = <<>> /\ execStep' = execStep
NoClaim == UNCHANGED <<claimNoEdit, claimReviewed, claimCmd>>
NoLast == UNCHANGED <<lastSeen, lastOutcome>>
NoHold == UNCHANGED <<heldTurnG, heldEverG, heldStepG>>
Step == n < MaxSteps /\ n' = n + 1
Key(actor0, cmd, dir) == IF Fix THEN <<actor0, cmd, dir>> ELSE cmd

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
  /\ UNCHANGED <<wrongG, explainFlags, editedG, reviewedAfterG, cmdAfterG, spokeTurnG, actsTurnG,
                 spoke, tools, textLong, previewed, editSeq, reviewedAt, cmdSeqs, trackedCwd,
                 inTurn, stepC, pc, snap, seen, beginStep, cwdG, nextBlock, workG, reportG, late>>

\* A plain message a hook or a settings hook beneath refused (prompt.submit's { drop }): it never reached the model.
\* The earlier sources had already taken what was owed; now it goes back.
Dropped ==
  /\ Step /\ Idle /\ ev' = "Dropped" /\ actor' = "user" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ slips' = IF N THEN slips ELSE {}
  /\ pendingReport' = IF N THEN pendingReport ELSE FALSE
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
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldEverG, heldStepG, editedG, reviewedAfterG,
                 cmdAfterG, slips, pendingReport, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd,
                 stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock>>

\* lint.ts turn.step (main loop): a new model response begins.
MainStep ==
  /\ Step /\ inTurn /\ ev' = "MainStep" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ stepC' = stepC + 1
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, codeVars, inTurn, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock,
                 workG, reportG, late>>

\* Text streamed before a call of the same response (turn.step text chunks); its row is appended later (LateAppend).
\* 0917b911 read "spoke" from the stream; the newest source also reads the report from it.
MainPre(long) ==
  /\ Step /\ inTurn /\ Idle /\ late = "none" /\ ev' = "MainPre" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ spoke' = IF Fix /\ ~M("stream-deaf") THEN TRUE ELSE spoke
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
  /\ Step /\ Idle /\ late # "none" /\ ev' = "LateAppend" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ spoke' = TRUE
  /\ textLong' = IF N THEN textLong ELSE TRUE
  /\ late' = "none"
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, slips, tools, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown,
                 trackedCwd, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* Text after the last call, streamed and appended (session.append, main loop). wrong: English prose to a Chinese
\* user; long: a report. A wrong block is recorded only while S.userLanguage is set (wantsChinese).
MainText(wrong, long) ==
  /\ Step /\ inTurn /\ late = "none" /\ ev' = "MainText" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ (wrong => (userSpokeG /\ nextBlock \in Blocks))
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
  /\ Step /\ ev' = "SubText" /\ actor' = "sub" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, codeVars, inTurn, stepC, pc, snap, seen, beginStep, cwdG,
                 userSpokeG, nextBlock, workG, reportG, late>>

\* lint.ts tool.call, main loop, a tool that is not Edit/Write/Bash (Read, a plan update, ...).
\* The first source counted it as work and forgot a report written before it; the fixes count only edits and commands.
MainRead ==
  /\ Step /\ inTurn /\ ev' = "MainRead" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ tools' = IF Fix THEN tools ELSE TRUE
  /\ textLong' = IF Fix THEN textLong ELSE FALSE
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
  /\ tools' = IF N THEN tools ELSE TRUE
  /\ textLong' = IF N THEN textLong ELSE FALSE
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
     /\ restated' = IF Fix THEN (IF out # "error" THEN Restate(taken) ELSE restated)
                           ELSE (IF out = "ok" THEN Restate(taken) ELSE restated)
     /\ slips' = IF Fix THEN (IF out = "error" THEN slips \cup taken ELSE slips) ELSE {}
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
  /\ Step /\ kind \notin {"cd", "subcd"} /\ ev' = "SubAct" /\ actor' = "sub" /\ NoClaim /\ explainNow' = FALSE /\ NoLast
  /\ slips' = IF Fix THEN slips ELSE {}
  /\ explainFlags' = IF Break = "R3" THEN explainFlags + 1 ELSE explainFlags
  /\ LET isDel  == kind \in Cmds
         key    == Key("sub", kind, "a")
         target == <<"sub", kind, "a">>
         held   == isDel /\ ~(key \in previewed)
         ran    == ~held IN
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
  /\ Step /\ inTurn /\ Idle /\ late = "none" /\ ev' = "TurnComplete" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ inTurn' = FALSE
  /\ pendingReport' = IF Break = "R5" THEN TRUE
                      ELSE IF M("no-owe") \/ (N /\ ~answered) THEN pendingReport
                      ELSE IF Fix /\ textLong THEN FALSE
                      ELSE pendingReport \/ (tools /\ ~textLong)
  /\ reportOwedG' = IF ~answered THEN reportOwedG ELSE IF reportG THEN FALSE ELSE (reportOwedG \/ workG)
  /\ UNCHANGED <<wrongG, restated, reportEmits, explainFlags, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, spoke, slips, tools, textLong, previewed, editSeq, reviewedAt, cmdSeqs,
                 langKnown, trackedCwd, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

\* A /review, started and ended (answered) or stopped by the user. The earlier sources counted it when it
\* started (skill.prompt); the newest when its turn ends with an answer (turn.complete).
Review(answered) ==
  /\ Step /\ ev' = "Review" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ reviewedAt' = IF (N /\ ~answered) \/ M("review-ignored") THEN reviewedAt ELSE editSeq
  /\ reviewedAfterG' = (reviewedAfterG \/ answered)
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, cmdAfterG,
                 spokeTurnG, actsTurnG, spoke, slips, tools, textLong, pendingReport, previewed, editSeq, cmdSeqs,
                 langKnown, trackedCwd, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock,
                 workG, reportG, late>>

\* lint.ts sessionRecord, read when skill.prompt for ship runs.
Ship ==
  /\ Step /\ ev' = "Ship" /\ actor' = "main" /\ NoOut /\ NoLast /\ NoHold
  /\ claimNoEdit' = (editSeq = 0)
  /\ claimReviewed' = (editSeq > 0 /\ (reviewedAt >= editSeq \/ (Break = "R8" /\ reviewedAt >= 0)))
  /\ claimCmd' = (editSeq > 0 /\ editSeq \in cmdSeqs)
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, codeVars, inTurn, stepC, pc, snap, seen, beginStep, cwdG,
                 userSpokeG, nextBlock, workG, reportG, late>>

\* The engine reloads the hooks module: the first source's module variables start over; the fixes keep them in $.state.
Reload ==
  /\ Step /\ Idle /\ ev' = "Reload" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast /\ NoHold
  /\ IF Fix /\ ~M("reload-forgets")
       THEN UNCHANGED codeVars
       ELSE /\ spoke' = TRUE /\ slips' = {} /\ tools' = FALSE /\ textLong' = FALSE /\ pendingReport' = FALSE
            /\ previewed' = {} /\ editSeq' = 0 /\ reviewedAt' = -1 /\ cmdSeqs' = {} /\ langKnown' = FALSE
            /\ trackedCwd' = "a"
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG,
                 nextBlock, workG, reportG, late>>

\* /clear: the conversation goes on under a new session id, with no session.start. Nothing is owed to the new one.
\* The newest source starts its state over (session.end, reason clear); the earlier ones kept it.
Clear ==
  /\ Step /\ Idle /\ ~inTurn /\ ev' = "Clear" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast
  /\ wrongG' = {} /\ reportOwedG' = FALSE /\ editedG' = FALSE /\ reviewedAfterG' = FALSE /\ cmdAfterG' = FALSE
  /\ heldTurnG' = {}
  /\ IF N /\ ~M("clear-keeps")
       THEN /\ spoke' = TRUE /\ slips' = {} /\ tools' = FALSE /\ textLong' = FALSE /\ pendingReport' = FALSE
            /\ previewed' = {} /\ editSeq' = 0 /\ reviewedAt' = -1 /\ cmdSeqs' = {}
            /\ UNCHANGED <<langKnown, trackedCwd>>
       ELSE UNCHANGED codeVars
  /\ UNCHANGED <<restated, reportEmits, explainFlags, heldEverG, heldStepG, spokeTurnG, actsTurnG,
                 inTurn, stepC, pc, snap, seen, beginStep, cwdG, userSpokeG, nextBlock, workG, reportG, late>>

Next ==
  \/ \E m \in MsgKinds : UserPrompt(m)
  \/ Dropped
  \/ TurnStart
  \/ MainStep
  \/ \E l \in BOOLEAN : MainPre(l)
  \/ LateAppend
  \/ \E w \in BOOLEAN, l \in BOOLEAN : MainText(w, l)
  \/ SubText
  \/ MainRead
  \/ \E c \in Calls : MainBegin(c)
  \/ \E c \in Calls, k \in ActKinds, o \in Outcomes : MainEnd(c, k, o)
  \/ \E k \in ActKinds : SubAct(k)
  \/ \E a \in BOOLEAN : TurnComplete(a)
  \/ \E a \in BOOLEAN : Review(a)
  \/ Ship
  \/ Reload
  \/ Clear

Spec == Init /\ [][Next]_vars
====
