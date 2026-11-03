---- MODULE LintRules ----
(* The judge: the confirmed rules R1-R10, and R11, as properties over what the
   mod outputs (restate requests, report requests, explain flags, holds, the
   /ship record) and what really happened (the ...G ghost variables).
   Written before the model of the code; it holds no code logic. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Blocks, Cmds

VARIABLES
  ev,             \* the last event: "Init", "UserPrompt", "Builtin", "Dropped", "TurnStart", "MainStep", "MainPre",
                  \*   "LateAppend", "MainText", "SubText", "MainRead", "MainBegin", "MainAct", "SubAct", "TurnComplete",
                  \*   "Review", "Ship", "Reload", "Clear"
  actor,          \* who caused it: "host", "user", "main", "sub"
  wrongG,         \* truth: the main-loop text blocks written in the wrong language
  restated,       \* output: how many times each block was asked to be restated
  reportOwedG,    \* truth: a main turn did work, ended without a report, and no report request followed
  reportEmits,    \* output: report requests given
  explainFlags,   \* output: explain-first flags given
  explainNow,     \* output: this event gave an explain-first flag
  heldTurnG,      \* output, per turn: delete targets (command, directory) held for preview this turn, by this actor
  heldEverG,      \* output: delete targets ever held for preview, by this actor
  heldStepG,      \* output: main-loop delete targets held, with the model response the held call was sent in
  execCmd,        \* output: the delete target <<actor, command, directory>> this event ran, or <<>>
  execStep,       \* the model response the call that ran it was sent in
  editedG,        \* truth: this session edited a file
  reviewedAfterG, \* truth: a review ran to its answer after the last edit
  cmdAfterG,      \* truth: a command ran after the last edit
  claimNoEdit,    \* output at Ship: the record says "no edits this session"
  claimReviewed,  \* output at Ship: the record says "reviewed after the last edit"
  claimCmd,       \* output at Ship: the record says "commands ran after the last edit"
  spokeTurnG,     \* truth: the main loop wrote text to the user this turn
  actsTurnG,      \* truth: main-loop edits and shell commands this turn
  lastSeen,       \* truth: the wrong blocks written before the call that just ended began
  lastOutcome,    \* how that call ended: "ok", "deny" (refused or held), "error" (it ran and failed)
  ansOwedG,       \* truth: the 重新 deliveries owed an answer, each as the model response after which the model
                  \*   holds it (it answers in a later one); several can be owed at once
  dupG,           \* output: a delivery was checked a second time
  answerRowG,     \* truth: this event appended a main-loop row that answers a delivered 重新
  checkNow,       \* output: this event ran the redo checks on a reply
  checksG,        \* output: the deliveries (by response) the redo checks have run for
  askWarrantedG,  \* truth, set at a stop (8.43): this turn did work, has not reported after it, and was not asked yet
  stopHoldsG,     \* output: how many times this turn was held at a stop
  qOwedG,         \* truth: a line for the model was queued and has not reached it
  qDeliv          \* output: how many times the queued line was handed to the model

judgeVars == <<ev, actor, wrongG, restated, reportOwedG, reportEmits, explainFlags, explainNow,
               heldTurnG, heldEverG, heldStepG, execCmd, execStep, editedG, reviewedAfterG, cmdAfterG,
               claimNoEdit, claimReviewed, claimCmd, spokeTurnG, actsTurnG, lastSeen, lastOutcome,
               ansOwedG, dupG, answerRowG, checkNow, checksG, askWarrantedG, stopHoldsG, qOwedG, qDeliv>>

\* R1: by the next user message the model reads at the latest, every wrong block was asked to be restated.
\* (A main call in flight may still be carrying the request, so the user's next message is the point it must be done by.
\* A built-in like /cost and a message refused before it entered are not read by the model.)
R1 == ev = "UserPrompt" => \A b \in wrongG : restated[b] >= 1

\* R2: no block is asked to be restated more than once.
R2 == \A b \in Blocks : restated[b] <= 1

\* R3: a subagent event gives no main-loop redo.
R3 == [][actor' = "sub" => (restated' = restated /\ reportEmits' = reportEmits /\ explainFlags' = explainFlags)]_judgeVars

\* R4: a turn that did work and ended without a report is asked for one. Up to 8.42 the request rode on the
\* user's next message; since 8.43 it comes at the stop, in the same turn (reportOwedG: owed and never asked).
\* Either way, by the user's next message nothing is owed that was never asked for.
R4 == ev = "UserPrompt" => ~reportOwedG

\* R5: a report request is given only when one is owed: from an earlier turn (up to 8.42), or by this turn at its
\* stop (since 8.43, askWarrantedG).
R5 == [][reportEmits' > reportEmits => (reportOwedG \/ askWarrantedG')]_judgeVars

\* R19 (8.43): a turn is held at a stop at most STOP_HOLDS (3) times for an error, plus once for a report or a
\* check, so a check that cannot pass never traps the turn.
R19 == stopHoldsG <= 4

\* R21 (8.43): a line queued for the model (a stop or a subagent's end that passed, a file changed outside, a wait
\* run out) reaches it at most once, and by the user's next message at the latest.
R21 == qDeliv <= 1 /\ (ev = "UserPrompt" => ~qOwedG)

\* R6: a delete runs only if it was held for preview earlier in this same turn (reading D1-B).
R6 == execCmd # <<>> => execCmd \in heldTurnG

\* R7: a delete never previewed is never let through.
R7 == execCmd # <<>> => execCmd \in heldEverG

\* R8: the /ship record never claims a review or a command after the last edit that did not happen.
R8 == ev = "Ship" => ((claimReviewed => reviewedAfterG) /\ (claimCmd => cmdAfterG))

\* R9: the /ship record never says "no edits" in a session that edited.
R9 == ev = "Ship" => (claimNoEdit => ~editedG)

\* R10: the first main-loop edit or command of a turn, with no text before it, is flagged.
R10 == (ev = "MainAct" /\ actsTurnG = 1 /\ ~spokeTurnG) => explainNow

\* R13 (user 2026-11-03): the /ship record says "reviewed after the last edit" whenever a review did answer after it.
R13 == ev = "Ship" => ((editedG /\ reviewedAfterG) => claimReviewed)

\* The redo checks (lint-scope sketch, user 2026-11-03; readings: the answer is the first main row with content
\* written after the model holds the 重新; a turn that ends first drops it; one row answering two kinds is one check).
\* R14 (A): a row that answers a delivered 重新 is checked.
R14 == answerRowG => checkNow
\* R15 (B): one delivery is checked at most once.
R15 == ~dupG
\* R16 (C): only an answer is checked.
R16 == checkNow => answerRowG
\* R17 (D): a subagent's event never runs the redo checks.
R17 == actor = "sub" => ~checkNow

\* R12 (rule A, user 2026-11-03): an act is never flagged "explain first" when the main loop wrote words the
\* person saw earlier this turn.
R12 == (ev = "MainAct" /\ explainNow) => ~spokeTurnG

\* R11: a main-loop delete runs only after the model had the preview in hand: it was held in an earlier response
\* than the one that sends it to run (not by a copy sent in the same response).
R11 == (execCmd # <<>> /\ execCmd[1] = "main") => \E s \in 0..(execStep - 1) : <<execCmd, s>> \in heldStepG
====
