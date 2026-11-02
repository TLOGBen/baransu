---- MODULE LintMod ----
(* The lint mod's cross-event state (plugins/baransu/hooks/lint.ts), one action
   per hook step. Fix = FALSE is the source as it is; Fix = TRUE is the proposed change.
   Break plants one bug per rule, to show the judge can say no.
   A main-loop Edit/Write/Bash call is two steps, MainBegin and MainEnd, because the
   source awaits between reading lint.ts::languageSlip and clearing it; two calls may overlap. *)
EXTENDS LintRules, Integers, FiniteSets

CONSTANTS Fix, Break, MaxSteps

Calls == {1, 2}
Dirs == {"a", "b"}
ActKinds == {"edit", "bash", "bashwrite", "cd"} \cup Cmds
Outcomes == {"ok", "deny", "error"}

VARIABLES
  n, inTurn,           \* step counter (scope); a main turn is running
  spoke,               \* lint.ts::spokeThisTurn
  slips,               \* lint.ts::languageSlip (source: one block or none; Fix: a set)
  tools,               \* lint.ts::toolsThisTurn > 0
  textLong,            \* lint.ts::textAfterTools reads as a report
  pendingReport,       \* lint.ts::pendingReport
  previewed,           \* lint.ts::previewed (source: command strings; Fix: <<actor, command, directory>>)
  editSeq,             \* lint.ts::editSeq
  reviewedAt,          \* lint.ts::reviewedAt
  cmdSeqs,             \* the editSeq values in lint.ts::commands
  langKnown,           \* lint.ts::userLanguage is set
  trackedCwd,          \* Fix: the shell directory the mod tracks from cd commands
  pc, snap, seen,      \* per main call: "idle"/"mid", restates it took, wrong blocks written before it began
  cwdG,                \* ghost: the main shell's real directory
  userSpokeG,          \* ghost: the user has written (their language is known)
  nextBlock,           \* ghost: id for the next wrong-language block
  workG, reportG       \* ghost: this turn edited or ran something / reported after its last such step

codeVars == <<spoke, slips, tools, textLong, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd>>
vars == <<judgeVars, codeVars, n, inTurn, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

Restate(S) == [b \in Blocks |-> IF b \in S THEN restated[b] + (IF Break = "R2" THEN 2 ELSE 1) ELSE restated[b]]
Idle == \A c \in Calls : pc[c] = "idle"
NoOut == explainNow' = FALSE /\ execCmd' = <<>>
NoClaim == UNCHANGED <<claimNoEdit, claimReviewed, claimCmd>>
NoLast == UNCHANGED <<lastSeen, lastOutcome>>
Step == n < MaxSteps /\ n' = n + 1
Key(actor0, cmd, dir) == IF Fix THEN <<actor0, cmd, dir>> ELSE cmd

Init ==
  /\ ev = "Init" /\ actor = "host" /\ wrongG = {} /\ restated = [b \in Blocks |-> 0]
  /\ reportOwedG = FALSE /\ reportEmits = 0 /\ explainFlags = 0 /\ explainNow = FALSE
  /\ heldTurnG = {} /\ heldEverG = {} /\ execCmd = <<>>
  /\ editedG = FALSE /\ reviewedAfterG = FALSE /\ cmdAfterG = FALSE
  /\ claimNoEdit = FALSE /\ claimReviewed = FALSE /\ claimCmd = FALSE
  /\ spokeTurnG = FALSE /\ actsTurnG = 0 /\ lastSeen = {} /\ lastOutcome = "ok"
  /\ n = 0 /\ inTurn = FALSE
  /\ spoke = TRUE                 \* lint.ts: let spokeThisTurn = true
  /\ slips = {} /\ tools = FALSE /\ textLong = FALSE /\ pendingReport = FALSE
  /\ previewed = {} /\ editSeq = 0 /\ reviewedAt = -1 /\ cmdSeqs = {} /\ langKnown = FALSE /\ trackedCwd = "a"
  /\ pc = [c \in Calls |-> "idle"] /\ snap = [c \in Calls |-> {}] /\ seen = [c \in Calls |-> {}]
  /\ cwdG = "a" /\ userSpokeG = FALSE /\ nextBlock = 1 /\ workG = FALSE /\ reportG = FALSE

\* lint.ts::register prompt.submit, a message the user typed. cmdMsg: a slash command (e.command set; the source skips those).
UserPrompt(cmdMsg) ==
  /\ Step /\ Idle /\ ev' = "UserPrompt" /\ actor' = "user" /\ NoOut /\ NoClaim /\ NoLast
  /\ userSpokeG' = TRUE
  /\ langKnown' = (langKnown \/ ~cmdMsg \/ Fix)   \* the Fix also reads the language from a slash command's arguments
  /\ LET consume == Fix \/ ~cmdMsg IN
     /\ restated' = IF consume THEN Restate(slips) ELSE restated
     /\ slips' = IF consume THEN {} ELSE slips
     /\ pendingReport' = IF consume THEN FALSE ELSE pendingReport
     /\ reportEmits' = IF consume /\ pendingReport THEN reportEmits + 1 ELSE reportEmits
     /\ reportOwedG' = IF consume /\ pendingReport THEN FALSE ELSE reportOwedG
  /\ UNCHANGED <<wrongG, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG, cmdAfterG, spokeTurnG, actsTurnG,
                 spoke, tools, textLong, previewed, editSeq, reviewedAt, cmdSeqs, trackedCwd,
                 inTurn, pc, snap, seen, cwdG, nextBlock, workG, reportG>>

\* lint.ts::register turn.start (main loop). Fix also ends this turn's preview approvals (reading D1-B).
TurnStart ==
  /\ Step /\ ~inTurn /\ ev' = "TurnStart" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast
  /\ inTurn' = TRUE /\ spoke' = FALSE /\ tools' = FALSE /\ textLong' = FALSE
  /\ previewed' = IF Fix THEN {} ELSE previewed
  /\ spokeTurnG' = FALSE /\ actsTurnG' = 0 /\ workG' = FALSE /\ reportG' = FALSE /\ heldTurnG' = {}
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldEverG, editedG, reviewedAfterG, cmdAfterG,
                 slips, pendingReport, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd,
                 pc, snap, seen, cwdG, userSpokeG, nextBlock>>

\* lint.ts::register session.append (main loop, assistant text). wrong: English prose to a Chinese user; long: a report.
\* The source records a wrong block only while lint.ts::userLanguage is set (wantsChinese).
MainText(wrong, long) ==
  /\ Step /\ inTurn /\ ev' = "MainText" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast
  /\ (wrong => (userSpokeG /\ nextBlock \in Blocks))
  /\ spoke' = TRUE /\ spokeTurnG' = TRUE
  /\ textLong' = (textLong \/ long) /\ reportG' = (reportG \/ long)
  /\ wrongG' = IF wrong THEN wrongG \cup {nextBlock} ELSE wrongG
  /\ nextBlock' = IF wrong THEN nextBlock + 1 ELSE nextBlock
  /\ slips' = IF wrong /\ langKnown THEN (IF Fix THEN slips \cup {nextBlock} ELSE {nextBlock}) ELSE slips
  /\ UNCHANGED <<restated, reportOwedG, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG, cmdAfterG,
                 actsTurnG, tools, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs, langKnown, trackedCwd,
                 inTurn, pc, snap, seen, cwdG, userSpokeG, workG>>

\* lint.ts::register session.append with e.agentId: ignored.
SubText ==
  /\ Step /\ ev' = "SubText" /\ actor' = "sub" /\ NoOut /\ NoClaim /\ NoLast
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, codeVars, inTurn, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* lint.ts::register tool.call, main loop, a tool that is not Edit/Write/Bash (Read, a plan update, ...).
\* The source counts it as work and forgets a report written before it; the Fix counts only edits and commands.
MainRead ==
  /\ Step /\ inTurn /\ ev' = "MainRead" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast
  /\ tools' = IF Fix THEN tools ELSE TRUE
  /\ textLong' = IF Fix THEN textLong ELSE FALSE
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, spoke, slips, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs,
                 langKnown, trackedCwd, inTurn, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* lint.ts::register tool.call, main loop, Edit/Write/Bash, first part: count the work; the Fix takes the pending
\* restates at once (the source reads lint.ts::languageSlip only after awaiting projectRoot and loadChecks).
MainBegin(c) ==
  /\ Step /\ inTurn /\ pc[c] = "idle" /\ ev' = "MainBegin" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast
  /\ pc' = [pc EXCEPT ![c] = "mid"]
  /\ seen' = [seen EXCEPT ![c] = wrongG]
  /\ snap' = [snap EXCEPT ![c] = slips]
  /\ slips' = IF Fix THEN {} ELSE slips
  /\ tools' = TRUE /\ textLong' = FALSE /\ workG' = TRUE /\ reportG' = FALSE
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, spoke, pendingReport, previewed, editSeq, reviewedAt, cmdSeqs,
                 langKnown, trackedCwd, inTurn, cwdG, userSpokeG, nextBlock>>

\* Second part: deliver restates, explain-first, preview, run, record. outcome: "deny" when another check refuses it,
\* "error" when it runs and fails. The source attaches the restate only to a successful result and has already cleared it.
MainEnd(c, kind, outcome) ==
  /\ Step /\ pc[c] = "mid" /\ ev' = "MainAct" /\ actor' = "main" /\ NoClaim
  /\ pc' = [pc EXCEPT ![c] = "idle"] /\ snap' = [snap EXCEPT ![c] = {}]
  /\ actsTurnG' = actsTurnG + 1 /\ lastSeen' = seen[c]
  /\ explainNow' = ~spoke
  /\ explainFlags' = (IF ~spoke THEN explainFlags + 1 ELSE explainFlags)
  /\ spoke' = TRUE
  /\ LET isDel  == kind \in Cmds
         dir    == IF Fix THEN trackedCwd ELSE "a"
         key    == Key("main", kind, dir)
         target == <<"main", kind, cwdG>>
         held   == isDel /\ ~(key \in previewed \/ (Break = "R7" /\ previewed # {}))
         out    == IF held THEN "deny" ELSE outcome
         ran    == out # "deny"
         taken  == snap[c] IN
     /\ lastOutcome' = out
     /\ restated' = IF Fix THEN (IF out # "error" THEN Restate(taken) ELSE restated)
                           ELSE (IF out = "ok" THEN Restate(taken) ELSE restated)
     /\ slips' = IF Fix THEN (IF out = "error" THEN slips \cup taken ELSE slips) ELSE {}
     /\ previewed' = IF held THEN previewed \cup {key} ELSE previewed
     /\ heldTurnG' = IF held THEN heldTurnG \cup {target} ELSE heldTurnG
     /\ heldEverG' = IF held THEN heldEverG \cup {target} ELSE heldEverG
     /\ execCmd' = IF isDel /\ ran THEN target ELSE <<>>
     /\ cwdG' = IF kind = "cd" /\ ran THEN (IF cwdG = "a" THEN "b" ELSE "a") ELSE cwdG
     /\ trackedCwd' = IF Fix /\ kind = "cd" /\ ran THEN (IF cwdG = "a" THEN "b" ELSE "a") ELSE trackedCwd
     /\ editSeq' = IF ran /\ (kind = "edit" \/ (Fix /\ kind = "bashwrite")) THEN editSeq + 1 ELSE editSeq
     /\ editedG' = (editedG \/ (ran /\ kind \in {"edit", "bashwrite"}))
     /\ reviewedAfterG' = IF ran /\ kind \in {"edit", "bashwrite"} THEN FALSE ELSE reviewedAfterG
     /\ cmdSeqs' = IF ran /\ kind # "edit" /\ ~(Fix /\ kind = "bashwrite") THEN cmdSeqs \cup {editSeq} ELSE cmdSeqs
     /\ cmdAfterG' = IF ran /\ kind \in {"edit", "bashwrite"} THEN FALSE ELSE (cmdAfterG \/ ran)
  /\ UNCHANGED <<wrongG, reportOwedG, reportEmits, spokeTurnG, tools, textLong, pendingReport, reviewedAt, langKnown,
                 inTurn, seen, userSpokeG, nextBlock, workG, reportG>>

\* lint.ts::register tool.call with e.agentId, Edit/Write/Bash. The source drops a pending restate here.
\* A subagent's shell is its own; its directory is "a".
SubAct(kind) ==
  /\ Step /\ kind # "cd" /\ ev' = "SubAct" /\ actor' = "sub" /\ NoClaim /\ explainNow' = FALSE /\ NoLast
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
                 reviewedAt, langKnown, trackedCwd, inTurn, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* lint.ts::register turn.complete (main loop). The Fix also clears a report owed from before when this turn reported.
TurnComplete ==
  /\ Step /\ inTurn /\ Idle /\ ev' = "TurnComplete" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast
  /\ inTurn' = FALSE
  /\ pendingReport' = IF Break = "R5" THEN TRUE
                      ELSE IF Fix /\ textLong THEN FALSE
                      ELSE pendingReport \/ (tools /\ ~textLong)
  /\ reportOwedG' = IF reportG THEN FALSE ELSE (reportOwedG \/ workG)
  /\ UNCHANGED <<wrongG, restated, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG, cmdAfterG,
                 spokeTurnG, actsTurnG, spoke, slips, tools, textLong, previewed, editSeq, reviewedAt, cmdSeqs,
                 langKnown, trackedCwd, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* lint.ts::register skill.prompt for review: reviewedAt = editSeq.
Review ==
  /\ Step /\ ev' = "Review" /\ actor' = "main" /\ NoOut /\ NoClaim /\ NoLast
  /\ reviewedAt' = editSeq /\ reviewedAfterG' = TRUE
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, cmdAfterG,
                 spokeTurnG, actsTurnG, spoke, slips, tools, textLong, pendingReport, previewed, editSeq, cmdSeqs,
                 langKnown, trackedCwd, inTurn, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* lint.ts::sessionRecord, read when skill.prompt for ship runs.
Ship ==
  /\ Step /\ ev' = "Ship" /\ actor' = "main" /\ NoOut /\ NoLast
  /\ claimNoEdit' = (editSeq = 0)
  /\ claimReviewed' = (editSeq > 0 /\ (reviewedAt >= editSeq \/ (Break = "R8" /\ reviewedAt >= 0)))
  /\ claimCmd' = (editSeq > 0 /\ editSeq \in cmdSeqs)
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, codeVars, inTurn, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

\* The engine reloads the hooks module: the source's module variables start over; the Fix keeps them in $.state.
Reload ==
  /\ Step /\ Idle /\ ev' = "Reload" /\ actor' = "host" /\ NoOut /\ NoClaim /\ NoLast
  /\ IF Fix
       THEN UNCHANGED codeVars
       ELSE /\ spoke' = TRUE /\ slips' = {} /\ tools' = FALSE /\ textLong' = FALSE /\ pendingReport' = FALSE
            /\ previewed' = {} /\ editSeq' = 0 /\ reviewedAt' = -1 /\ cmdSeqs' = {} /\ langKnown' = FALSE
            /\ trackedCwd' = "a"
  /\ UNCHANGED <<wrongG, restated, reportOwedG, reportEmits, explainFlags, heldTurnG, heldEverG, editedG, reviewedAfterG,
                 cmdAfterG, spokeTurnG, actsTurnG, inTurn, pc, snap, seen, cwdG, userSpokeG, nextBlock, workG, reportG>>

Next ==
  \/ \E m \in BOOLEAN : UserPrompt(m)
  \/ TurnStart
  \/ \E w \in BOOLEAN, l \in BOOLEAN : MainText(w, l)
  \/ SubText
  \/ MainRead
  \/ \E c \in Calls : MainBegin(c)
  \/ \E c \in Calls, k \in ActKinds, o \in Outcomes : MainEnd(c, k, o)
  \/ \E k \in ActKinds : SubAct(k)
  \/ TurnComplete
  \/ Review
  \/ Ship
  \/ Reload

Spec == Init /\ [][Next]_vars
====
