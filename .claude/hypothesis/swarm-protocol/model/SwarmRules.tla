---------------------------- MODULE SwarmRules ----------------------------
(* The judge: the confirmed rules R1-R11 as properties over the swarm's    *)
(* observable state. Written before any protocol design; it shares no     *)
(* protocol code. The protocol module EXTENDS this one and defines Init   *)
(* and Next over the same variables.                                      *)
EXTENDS Naturals, FiniteSets

CONSTANTS Tasks, Workers, Deps, PathsOf, MaxAttempt, None

VARIABLES
    board,      \* task -> state written on the board (lead only)
    attempt,    \* task -> attempts started so far (board field)
    awaiting,   \* task -> "none" | "lead" | "user" (board field, for blocked)
    owner,      \* task -> worker holding it, or None (board field)
    report,     \* task -> durable report of the current attempt
    jobsAt,     \* task -> TRUE when the report was written with a job still running
    wstate,     \* worker -> "idle" | "working" | "jobs" | "ended"
    asked,      \* task -> the user has been shown the question
    waitFor,    \* task -> the held task whose path it needs, or None (board field)
    who         \* actor of the last step: "lead" | "worker" | "user" | "host" | "none";
                \* "wait" when the queen ended her turn to wait for an event

States   == {"absent", "waiting", "ready", "running", "blocked", "reported", "verified", "gap"}
Terminal(t) == board[t] \in {"verified", "gap"}
Present(t)  == board[t] # "absent"
Finished    == \A t \in Tasks : board[t] \in {"absent", "verified", "gap"}
Held(t)     == board[t] \in {"running", "blocked"}

\* A task is waiting on the user when it is blocked on a user decision, or
\* waits (directly or through its dependencies) on such a task.
RECURSIVE UserChain(_, _)
UserChain(t, depth) ==
    \/ board[t] = "blocked" /\ awaiting[t] = "user"
    \/ /\ depth > 0
       /\ board[t] = "waiting"
       /\ \E d \in Deps[t] : UserChain(d, depth - 1)
    \/ /\ depth > 0
       /\ board[t] = "ready"
       /\ waitFor[t] # None
       /\ UserChain(waitFor[t], depth - 1)
AwaitsUser(t) == UserChain(t, Cardinality(Tasks))

\* R1: no task is verified without evidence.
R1 == \A t \in Tasks : board[t] = "verified" => report[t] = "ev"

\* R2: only the lead writes the board (an action property).
BoardVars == <<board, attempt, awaiting, owner, waitFor>>
R2 == [][BoardVars' # BoardVars => who' = "lead"]_<<BoardVars, who>>

\* R3: no path is held by two tasks at once.
R3 == \A t, u \in Tasks :
        (t # u /\ Held(t) /\ Held(u)) => PathsOf[t] \cap PathsOf[u] = {}

\* R4 (safety half): what the board says is backed by a report.
R4 == \A t \in Tasks :
        /\ board[t] = "blocked" => report[t] \in {"blockedLead", "blockedUser", "envFail"}
        /\ (board[t] = "blocked" /\ report[t] = "blockedUser") => awaiting[t] = "user"
        /\ (board[t] = "blocked" /\ report[t] \in {"blockedLead", "envFail"}) => awaiting[t] = "lead"
        /\ board[t] = "reported" => report[t] \in {"ev", "noev", "none"}
\* R4 (liveness half): every report a worker leaves is taken onto the board.
R4live == \A t \in Tasks :
        (board[t] = "running" /\ owner[t] # None /\ wstate[owner[t]] = "ended")
            ~> (board[t] # "running")

\* R5: no silent stall. When nobody but the user can move and the run is not
\* finished, every unfinished task waits on the user and every such question
\* has been shown to the user.
\* The protocol module passes in whether the lead, a worker or the host can
\* take a step (ENABLED of its system actions); the user is not among them.
R5Body(systemCanMove) == (~Finished /\ ~systemCanMove) =>
        \A t \in Tasks :
            (Present(t) /\ ~Terminal(t)) =>
                /\ AwaitsUser(t)
                /\ \A u \in Tasks :
                     (board[u] = "blocked" /\ awaiting[u] = "user") => asked[u]

\* R6: if the user answers every question, every task ends.
R6 == <>Finished

\* R7: a task whose dependency is a gap does not wait forever.
R7 == \A t \in Tasks :
        (board[t] = "waiting" /\ \E d \in Deps[t] : board[d] = "gap") ~> (board[t] = "gap")

\* R8: with the user silent, every task not waiting on the user still ends.
R8 == <>[](\A t \in Tasks : (Present(t) /\ ~Terminal(t)) => AwaitsUser(t))

\* R9: no report is taken while a job its worker started still runs.
R9 == \A t \in Tasks : board[t] \in {"reported", "verified"} => ~jobsAt[t]

\* R10: a compaction of the lead loses nothing a worker left: report files
\* change only by a worker writing or the lead starting a fresh run.
R10 == [][report' # report => who' \in {"worker", "lead"}]_<<report, who>>

\* R12: the queen never ends her turn to wait while a seat is free and a task
\* could start in it (ready, an attempt left, none of its paths held).
SeatFree(w) == /\ wstate[w] \in {"idle", "ended"}
               /\ \A u \in Tasks : owner[u] = w => board[u] # "running"
Startable(t) == /\ board[t] = "ready"
                /\ attempt[t] < MaxAttempt
                /\ \A u \in Tasks : Held(u) => PathsOf[t] \cap PathsOf[u] = {}
R12 == [][who' = "wait" => ~(\E w \in Workers, t \in Tasks : SeatFree(w) /\ Startable(t))]_<<who>>

\* R11: no task runs a third time.
R11 == \A t \in Tasks : attempt[t] <= MaxAttempt

TypeOK ==
    /\ board \in [Tasks -> States]
    /\ attempt \in [Tasks -> 0..(MaxAttempt + 1)]
    /\ awaiting \in [Tasks -> {"none", "lead", "user"}]
    /\ owner \in [Tasks -> Workers \cup {None}]
    /\ report \in [Tasks -> {"none", "ev", "noev", "blockedLead", "blockedUser", "envFail"}]
    /\ jobsAt \in [Tasks -> BOOLEAN]
    /\ wstate \in [Workers -> {"idle", "working", "jobs", "ended"}]
    /\ asked \in [Tasks -> BOOLEAN]
    /\ waitFor \in [Tasks -> Tasks \cup {None}]
    /\ who \in {"lead", "worker", "user", "host", "wait", "none"}
=============================================================================
