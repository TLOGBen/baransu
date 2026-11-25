------------------------------- MODULE Swarm -------------------------------
(* The /swarm protocol: one lead (the queen), several workers (bees), the  *)
(* user. Source: plugins/baransu/skills/swarm/SKILL.md (The board, The   *)
(* loop, What a bee gets and gives back, When something goes wrong) and   *)
(* the design decisions in ../README.md.                                  *)
(*                                                                         *)
(* Interaction mechanism modelled here:                                    *)
(*  - A worker ends its turn with a durable report file (ev / noev /       *)
(*    blockedLead / blockedUser / envFail) or vanishes with none; the host *)
(*    tells the lead a background worker ended (wstate = "ended").         *)
(*  - Only the lead moves board fields. The lead holds nothing in memory:  *)
(*    every step reads the board, the report files and worker liveness,    *)
(*    so a compaction (Compact) loses nothing.                             *)
(*  - A question for the lead is answered and the same worker resumed; a   *)
(*    question for the user is shown to the user, the task waits, the     *)
(*    rest keep running; on the answer the worker is resumed.              *)
(*  - An environment failure is fixed by the lead and written as a lint    *)
(*    check, the worker resumed, no attempt spent; a second one on the     *)
(*    same task counts as a failed attempt.                                *)
(*  - A vanished worker is resumed once to report (reading A3); a second   *)
(*    block in one attempt, or a second vanish, fails the attempt: the     *)
(*    task goes to a fresh worker, at most MaxAttempt attempts, then gap.  *)
EXTENDS SwarmRules

CONSTANT LateTasks   \* tasks the user adds mid-run
CONSTANT Variant     \* "none" for the protocol; any other value breaks one rule on purpose
V(name) == Variant = name

VARIABLES
    answered,   \* task -> the user answered its question
    resumed,    \* task -> the vanished worker was already resumed once (this attempt)
    blocks,     \* task -> blocks raised in this attempt
    envFixed,   \* task -> an environment failure was already fixed (lint check written)
    jobUsed,    \* worker -> started its one background job in this run
    compacted   \* number of lead compactions so far (bounded)

vars == <<board, attempt, awaiting, owner, report, jobsAt, wstate, asked, waitFor, who,
          answered, resumed, blocks, envFixed, jobUsed, compacted>>

Free(w) == /\ wstate[w] \in {"idle", "ended"}
           /\ \A u \in Tasks : owner[u] = w => board[u] # "running"
           /\ V("seatHeld") => \A u \in Tasks : owner[u] = w => board[u] # "blocked"
PathsFree(t) == V("noPathCheck") \/ \A u \in Tasks : Held(u) => PathsOf[t] \cap PathsOf[u] = {}

Init ==
    /\ board = [t \in Tasks |-> IF t \in LateTasks THEN "absent"
                                ELSE IF Deps[t] = {} THEN "ready" ELSE "waiting"]
    /\ attempt = [t \in Tasks |-> 0]
    /\ awaiting = [t \in Tasks |-> "none"]
    /\ owner = [t \in Tasks |-> None]
    /\ report = [t \in Tasks |-> "none"]
    /\ jobsAt = [t \in Tasks |-> FALSE]
    /\ wstate = [w \in Workers |-> "idle"]
    /\ asked = [t \in Tasks |-> FALSE]
    /\ waitFor = [t \in Tasks |-> None]
    /\ who = "none"
    /\ answered = [t \in Tasks |-> FALSE]
    /\ resumed = [t \in Tasks |-> FALSE]
    /\ blocks = [t \in Tasks |-> 0]
    /\ envFixed = [t \in Tasks |-> FALSE]
    /\ jobUsed = [w \in Workers |-> FALSE]
    /\ compacted = 0

\* ---------------------------------------------------------------- lead ---
FailAttempt(t) ==
    /\ board' = [board EXCEPT ![t] = IF attempt[t] < MaxAttempt \/ V("noCap") THEN "ready" ELSE "gap"]
    /\ owner' = [owner EXCEPT ![t] = None]
    /\ awaiting' = [awaiting EXCEPT ![t] = "none"]

ResumeWorker(t) ==
    /\ wstate' = [wstate EXCEPT ![owner[t]] = "working"]
    /\ report' = [report EXCEPT ![t] = "none"]

AddTask(t) ==
    /\ board[t] = "absent"
    /\ board' = [board EXCEPT ![t] = IF Deps[t] = {} THEN "ready" ELSE "waiting"]
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, attempt, awaiting, owner, report, jobsAt, wstate, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

Promote(t) ==
    /\ board[t] = "waiting"
    /\ \A d \in Deps[t] : board[d] = "verified"
    /\ board' = [board EXCEPT ![t] = "ready"]
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, attempt, awaiting, owner, report, jobsAt, wstate, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

Cascade(t) ==
    /\ ~V("noCascade")
    /\ board[t] = "waiting"
    /\ \E d \in Deps[t] : board[d] = "gap"
    /\ board' = [board EXCEPT ![t] = "gap"]
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, attempt, awaiting, owner, report, jobsAt, wstate, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

Start(t, w) ==
    /\ board[t] = "ready"
    /\ attempt[t] < MaxAttempt \/ V("noCap")
    /\ Free(w)
    \* broken variant: start the next wave only once every seat is free
    /\ V("waves") => \A x \in Workers : Free(x)
    /\ PathsFree(t)
    /\ board' = [board EXCEPT ![t] = "running"]
    /\ attempt' = [attempt EXCEPT ![t] = @ + 1]
    /\ owner' = [owner EXCEPT ![t] = w]
    /\ report' = [report EXCEPT ![t] = "none"]
    /\ jobsAt' = [jobsAt EXCEPT ![t] = FALSE]
    /\ wstate' = [wstate EXCEPT ![w] = "working"]
    /\ jobUsed' = [jobUsed EXCEPT ![w] = FALSE]
    /\ resumed' = [resumed EXCEPT ![t] = FALSE]
    /\ blocks' = [blocks EXCEPT ![t] = 0]
    /\ waitFor' = [waitFor EXCEPT ![t] = None]
    /\ who' = "lead"
    /\ UNCHANGED <<awaiting, asked, answered, envFixed, compacted>>

\* A ready task that cannot start because a held task owns one of its paths
\* is written on the board as waiting for that task.
Holder(t) == CHOOSE u \in Tasks : Held(u) /\ PathsOf[t] \cap PathsOf[u] # {}
MarkPathWait(t) ==
    /\ ~V("noPathWait")
    /\ board[t] = "ready"
    /\ \E u \in Tasks : Held(u) /\ PathsOf[t] \cap PathsOf[u] # {}
    /\ waitFor[t] # Holder(t)
    /\ waitFor' = [waitFor EXCEPT ![t] = Holder(t)]
    /\ who' = "lead"
    /\ UNCHANGED <<board, attempt, awaiting, owner, report, jobsAt, wstate, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

\* The lead takes a worker's end onto the board, from the report file.
Take(t) ==
    /\ board[t] = "running"
    /\ owner[t] # None
    /\ wstate[owner[t]] = "ended"
    /\ who' = "lead"
    /\ CASE report[t] \in {"ev", "noev"} ->
              /\ board' = [board EXCEPT ![t] = "reported"]
              /\ UNCHANGED <<waitFor, attempt, awaiting, owner, report, wstate, resumed, blocks, envFixed>>
         [] report[t] \in {"blockedLead", "blockedUser"} /\ (blocks[t] = 0 \/ V("unboundedBlocks")) ->
              /\ board' = [board EXCEPT ![t] = "blocked"]
              /\ awaiting' = [awaiting EXCEPT ![t] =
                                IF report[t] = "blockedUser" /\ ~V("wrongAwait") THEN "user" ELSE "lead"]
              /\ blocks' = [blocks EXCEPT ![t] = 1]
              /\ owner' = IF V("seatHeld") THEN owner ELSE [owner EXCEPT ![t] = None]
              /\ UNCHANGED <<waitFor, attempt, report, wstate, resumed, envFixed>>
         [] report[t] \in {"blockedLead", "blockedUser"} /\ blocks[t] > 0 /\ ~V("unboundedBlocks") ->
              /\ FailAttempt(t)
              /\ UNCHANGED <<waitFor, attempt, report, wstate, resumed, blocks, envFixed>>
         [] report[t] = "envFail" /\ ~envFixed[t] ->
              /\ board' = [board EXCEPT ![t] = "blocked"]
              /\ awaiting' = [awaiting EXCEPT ![t] = "lead"]
              /\ owner' = [owner EXCEPT ![t] = None]
              /\ UNCHANGED <<waitFor, attempt, report, wstate, resumed, blocks, envFixed>>
         [] report[t] = "envFail" /\ envFixed[t] ->
              /\ FailAttempt(t)
              /\ UNCHANGED <<waitFor, attempt, report, wstate, resumed, blocks, envFixed>>
         [] report[t] = "none" /\ ~resumed[t] ->
              /\ resumed' = [resumed EXCEPT ![t] = TRUE]
              /\ ResumeWorker(t)
              /\ UNCHANGED <<waitFor, board, attempt, awaiting, owner, blocks, envFixed>>
         [] report[t] = "none" /\ resumed[t] ->
              /\ FailAttempt(t)
              /\ UNCHANGED <<waitFor, attempt, report, wstate, resumed, blocks, envFixed>>
    /\ UNCHANGED <<waitFor, jobsAt, asked, answered, jobUsed, compacted>>

Verify(t) ==
    /\ board[t] = "reported"
    /\ report[t] = "ev" \/ V("verifyNoEv")
    /\ board' = [board EXCEPT ![t] = "verified"]
    /\ owner' = [owner EXCEPT ![t] = None]
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, attempt, awaiting, report, jobsAt, wstate, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

Retry(t) ==
    /\ board[t] = "reported"
    /\ report[t] = "noev"
    /\ FailAttempt(t)
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, attempt, report, jobsAt, wstate, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

\* A blocked task's worker has ended and holds no seat; resuming it takes a
\* free seat w (the same agent, continued, in a seat that is free now).
ResumeOn(t, w) ==
    /\ Free(w)
    /\ owner' = [owner EXCEPT ![t] = w]
    /\ wstate' = [wstate EXCEPT ![w] = "working"]
    /\ jobUsed' = [jobUsed EXCEPT ![w] = FALSE]
    /\ report' = [report EXCEPT ![t] = "none"]

AnswerLead(t, w) ==
    /\ board[t] = "blocked"
    /\ awaiting[t] = "lead"
    /\ board' = [board EXCEPT ![t] = "running"]
    /\ awaiting' = [awaiting EXCEPT ![t] = "none"]
    /\ envFixed' = [envFixed EXCEPT ![t] = IF report[t] = "envFail" THEN TRUE ELSE @]
    /\ ResumeOn(t, w)
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, attempt, jobsAt, asked, answered, resumed, blocks, compacted>>

Ask(t) ==
    /\ ~V("noAsk")
    /\ board[t] = "blocked"
    /\ awaiting[t] = "user"
    /\ ~asked[t]
    /\ asked' = [asked EXCEPT ![t] = TRUE]
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, board, attempt, awaiting, owner, report, jobsAt, wstate,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

ResumeAfterUser(t, w) ==
    /\ board[t] = "blocked"
    /\ awaiting[t] = "user"
    /\ answered[t]
    /\ board' = [board EXCEPT ![t] = "running"]
    /\ awaiting' = [awaiting EXCEPT ![t] = "none"]
    /\ asked' = [asked EXCEPT ![t] = FALSE]
    /\ answered' = [answered EXCEPT ![t] = FALSE]
    /\ ResumeOn(t, w)
    /\ who' = "lead"
    /\ UNCHANGED <<waitFor, attempt, jobsAt, resumed, blocks, envFixed, compacted>>

\* The lead's context is compacted; it keeps nothing outside the board,
\* the report files and worker liveness, so nothing changes.
Compact ==
    /\ compacted < 1
    /\ compacted' = compacted + 1
    /\ who' = "host"
    \* broken variant: a report that lived only in the lead's context is gone
    /\ report' = IF V("volatileReport")
                 THEN [t \in Tasks |-> IF board[t] = "running" THEN "none" ELSE report[t]]
                 ELSE report
    /\ UNCHANGED <<waitFor, board, attempt, awaiting, owner, jobsAt, wstate, asked,
                   answered, resumed, blocks, envFixed, jobUsed>>

\* -------------------------------------------------------------- workers ---
TaskOf(w) == CHOOSE t \in Tasks : owner[t] = w /\ board[t] = "running"
Busy(w) == \E t \in Tasks : owner[t] = w /\ board[t] = "running"

StartJob(w) ==
    /\ wstate[w] = "working"
    /\ ~jobUsed[w]
    /\ wstate' = [wstate EXCEPT ![w] = "jobs"]
    /\ jobUsed' = [jobUsed EXCEPT ![w] = TRUE]
    /\ who' = "worker"
    /\ UNCHANGED <<waitFor, board, attempt, awaiting, owner, report, jobsAt, asked,
                   answered, resumed, blocks, envFixed, compacted>>

JobDone(w) ==
    /\ wstate[w] = "jobs"
    /\ wstate' = [wstate EXCEPT ![w] = "working"]
    /\ who' = "worker"
    /\ UNCHANGED <<waitFor, board, attempt, awaiting, owner, report, jobsAt, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

\* A worker reports only when no job it started is still running.
Report(w, r) ==
    /\ wstate[w] = "working" \/ (V("reportDuringJob") /\ wstate[w] = "jobs")
    /\ Busy(w)
    /\ report' = [report EXCEPT ![TaskOf(w)] = r]
    /\ jobsAt' = [jobsAt EXCEPT ![TaskOf(w)] = (wstate[w] = "jobs")]
    /\ wstate' = [wstate EXCEPT ![w] = "ended"]
    /\ who' = "worker"
    \* broken variant: the worker moves its own task on the board
    /\ board' = IF V("workerWrites") /\ r \in {"ev", "noev"}
                THEN [board EXCEPT ![TaskOf(w)] = "reported"] ELSE board
    /\ UNCHANGED <<waitFor, attempt, awaiting, owner, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

\* A worker's turn ends with no report (stopped early, crashed).
Vanish(w) ==
    /\ wstate[w] \in {"working", "jobs"}
    /\ Busy(w)
    /\ wstate' = [wstate EXCEPT ![w] = "ended"]
    /\ who' = "host"
    /\ UNCHANGED <<waitFor, board, attempt, awaiting, owner, report, jobsAt, asked,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

\* ----------------------------------------------------------------- user ---
Answer(t) ==
    /\ asked[t]
    /\ ~answered[t]
    /\ answered' = [answered EXCEPT ![t] = TRUE]
    /\ who' = "user"
    /\ UNCHANGED <<waitFor, board, attempt, awaiting, owner, report, jobsAt, wstate, asked,
                   resumed, blocks, envFixed, jobUsed, compacted>>

Reports == {"ev", "noev", "blockedLead", "blockedUser", "envFail"}

LeadStep(t) == \/ AddTask(t) \/ Promote(t) \/ Cascade(t) \/ Take(t) \/ Verify(t)
               \/ Retry(t) \/ Ask(t) \/ MarkPathWait(t)
               \/ \E w \in Workers : AnswerLead(t, w) \/ ResumeAfterUser(t, w)
               \/ \E w \in Workers : Start(t, w)
WorkerStep(w) == \/ StartJob(w) \/ JobDone(w) \/ Vanish(w) \/ \E r \in Reports : Report(w, r)

\* The lead and the workers; the user is not part of it, nor is a compaction.
SysNext == (\E t \in Tasks : LeadStep(t)) \/ (\E w \in Workers : WorkerStep(w))

Done == Finished /\ UNCHANGED vars

\* The queen ends her turn and waits for the next event (a bee ending, the
\* user answering). She does so only when she has no step of her own.
QueenWait ==
    /\ ~Finished
    /\ ~(\E t \in Tasks : ENABLED LeadStep(t))
    /\ who' = "wait"
    /\ UNCHANGED <<board, attempt, awaiting, owner, report, jobsAt, wstate, asked, waitFor,
                   answered, resumed, blocks, envFixed, jobUsed, compacted>>

Next == SysNext \/ Compact \/ (\E t \in Tasks : Answer(t)) \/ QueenWait \/ Done

\* AddTask is the user's request reaching the lead; it is fair only once the
\* user made it, which the model treats as some time during the run.
Fair == /\ \A t \in Tasks : WF_vars(LeadStep(t))
        /\ \A w \in Workers : WF_vars(WorkerStep(w))

Spec       == Init /\ [][Next]_vars /\ Fair
SpecAnswer == Spec /\ \A t \in Tasks : WF_vars(Answer(t))

R5 == R5Body(ENABLED SysNext)

\* Liveness over a task's own progress: a working worker eventually ends.
=============================================================================
